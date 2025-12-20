"""
Scraping Service

Multi-engine web scraping service with proxy support and behavioral stealth.
Handles routing logic for multiple scraping engines.
"""

import hashlib
import logging
import re
import time
import uuid
from datetime import datetime
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from sqlmodel import Session, select

from app.models import ContentChecksum, DomainProfile, ScrapeJob, ScrapeResult
from app.scraping.proxy_pool import NoAvailableProxyError, default_proxy_pool
from app.scraping.stealth import StealthConfig, default_stealth_service

logger = logging.getLogger(__name__)


class ScrapingServiceError(Exception):
    """Base exception for scraping service errors."""

    pass


class JobNotFoundError(ScrapingServiceError):
    """Scraping job not found."""

    pass


class EngineNotAvailableError(ScrapingServiceError):
    """Scraping engine not available."""

    pass


class ScrapingService:
    """
    Scraping service for multi-engine web scraping.

    Routing Logic:
    - simple_html = true → BeautifulSoup
    - multi_page_crawl = true → Crawl4AI
    - js_rendering_required = true → Playwright
    - spider_framework = true → Scrapy
    - visual_crawl = true → ScrapeGraph AI
    - job_board = true → Jobspy
    - agent_driven = true → WaterCrawl
    """

    def __init__(self):
        """Initialize scraping service."""
        self._scraping_engines: dict[str, Any] = {}

    def select_engine(
        self,
        url: str,
        scrape_requirements: dict[str, Any] | None = None,
    ) -> str:
        """
        Select appropriate scraping engine for a URL.

        Args:
            url: URL to scrape
            scrape_requirements: Optional scraping requirements dictionary

        Returns:
            Scraping engine name (e.g., "beautifulsoup", "playwright", "scrapy")
        """
        if not scrape_requirements:
            scrape_requirements = {}

        # Extract requirements
        simple_html = scrape_requirements.get("simple_html", False)
        multi_page_crawl = scrape_requirements.get("multi_page_crawl", False)
        js_rendering_required = scrape_requirements.get("js_rendering_required", False)
        spider_framework = scrape_requirements.get("spider_framework", False)
        visual_crawl = scrape_requirements.get("visual_crawl", False)
        job_board = scrape_requirements.get("job_board", False)
        agent_driven = scrape_requirements.get("agent_driven", False)

        # Routing logic (in priority order)

        # Agent-driven crawling → WaterCrawl
        if agent_driven:
            return "watercrawl"

        # Job board specialized → Jobspy
        if job_board:
            return "jobspy"

        # Visual crawl → ScrapeGraph AI
        if visual_crawl:
            return "scrapegraph_ai"

        # Spider framework → Scrapy
        if spider_framework:
            return "scrapy"

        # Multi-page crawling → Crawl4AI
        if multi_page_crawl:
            return "crawl4ai"

        # JS rendering required → Playwright
        if js_rendering_required:
            return "playwright"

        # Simple HTML → BeautifulSoup (default)
        return "beautifulsoup"

    def create_job(
        self,
        session: Session,
        url: str,
        engine: str | None = None,
        proxy_id: str | None = None,
        scrape_requirements: dict[str, Any] | None = None,
        auto_select_proxy: bool = True,
    ) -> ScrapeJob:
        """
        Create a new scraping job.

        Args:
            session: Database session
            url: URL to scrape
            engine: Optional engine name (auto-selected if not provided)
            proxy_id: Optional proxy ID
            scrape_requirements: Optional scraping requirements

        Returns:
            ScrapeJob instance
        """
        # Select engine if not provided
        if not engine:
            engine = self.select_engine(
                url=url,
                scrape_requirements=scrape_requirements,
            )

        # Auto-select proxy if not provided and auto_select_proxy is True
        if not proxy_id and auto_select_proxy:
            try:
                domain = self._extract_domain(url)
                country_filter = (
                    scrape_requirements.get("country") if scrape_requirements else None
                )
                proxy_type_filter = (
                    scrape_requirements.get("proxy_type")
                    if scrape_requirements
                    else None
                )

                proxy = default_proxy_pool.get_proxy(
                    session=session,
                    domain=domain,
                    country=country_filter,
                    proxy_type=proxy_type_filter,
                )
                proxy_id = proxy.proxy_id
                logger.info(f"Auto-selected proxy: {proxy_id} for domain: {domain}")
            except NoAvailableProxyError:
                logger.warning(
                    f"No proxy available for {url}, proceeding without proxy"
                )
                proxy_id = None

        # Check for duplicate content (content checksum)
        content_hash = self._calculate_content_hash(url)
        existing_checksum = session.exec(
            select(ContentChecksum).where(ContentChecksum.content_hash == content_hash)
        ).first()

        # Create job
        job = ScrapeJob(
            url=url,
            engine=engine,
            proxy_id=proxy_id,
            status="running",
            started_at=datetime.utcnow(),
        )
        session.add(job)
        session.commit()
        session.refresh(job)

        # Update or create content checksum
        if existing_checksum:
            existing_checksum.last_scraped_at = datetime.utcnow()
            session.add(existing_checksum)
        else:
            checksum = ContentChecksum(
                url=url,
                content_hash=content_hash,
                last_scraped_at=datetime.utcnow(),
            )
            session.add(checksum)

        session.commit()

        logger.info(f"Created scraping job: {job.id} (Engine: {engine}, URL: {url})")

        return job

    def process_job(
        self,
        session: Session,
        job_id: uuid.UUID,
    ) -> ScrapeResult:
        """
        Process a scraping job.

        Args:
            session: Database session
            job_id: Scraping job ID

        Returns:
            ScrapeResult instance
        """
        job = session.get(ScrapeJob, job_id)
        if not job:
            raise JobNotFoundError(f"Scraping job {job_id} not found")

        if job.status != "running":
            raise ScrapingServiceError(
                f"Scraping job {job_id} is not in running status"
            )

        # Get scraping engine client
        engine_client = self._get_engine_client(job.engine)

        # Get domain profile for behavioral settings
        domain = self._extract_domain(job.url)
        domain_profile = self._get_or_create_domain_profile(session, domain)

        # Create stealth config based on domain profile
        stealth_config = None
        if domain_profile:
            stealth_config = StealthConfig(
                enable_ua_rotation=True,
                enable_timing_randomness=True,
                enable_fingerprint_spoofing=domain_profile.captcha_likelihood
                in ["medium", "high"],
                enable_ghost_cursor=domain_profile.scroll_needed
                or domain_profile.captcha_likelihood in ["medium", "high"],
                min_delay_seconds=domain_profile.idle_before_click,
                max_delay_seconds=domain_profile.idle_before_click * 2,
            )

        # Execute scraping
        try:
            result_data = self._execute_scraping(
                client=engine_client,
                url=job.url,
                engine=job.engine,
                proxy_id=job.proxy_id,
                domain_profile=domain_profile,
                stealth_config=stealth_config,
            )

            # Create result record
            result = ScrapeResult(
                job_id=job.id,
                content=result_data.get("content", ""),
                html=result_data.get("html"),
                result_metadata={
                    "engine": job.engine,
                    "proxy_id": job.proxy_id,
                    "content_length": len(result_data.get("content", "")),
                    "has_html": result_data.get("html") is not None,
                },
            )
            session.add(result)

            # Record proxy usage for scoring
            if job.proxy_id:
                domain = self._extract_domain(job.url)
                status_code = result_data.get("status_code", 200)
                latency_ms = result_data.get("latency_ms", 0)
                block_reason = result_data.get("block_reason")

                default_proxy_pool.record_proxy_usage(
                    session=session,
                    proxy_id=job.proxy_id,
                    domain=domain,
                    status_code=status_code,
                    latency_ms=latency_ms,
                    block_reason=block_reason,
                )

            # Update job status
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            job.result = {
                "engine": job.engine,
                "content_length": len(result.content),
                "result_id": str(result.id),
            }
            session.add(job)
            session.commit()
            session.refresh(result)

            logger.info(
                f"Scraping job {job_id} completed successfully (Engine: {job.engine})"
            )

            return result

        except Exception as e:
            # Update job status to failed
            job.status = "failed"
            job.completed_at = datetime.utcnow()
            job.error_message = str(e)
            session.add(job)
            session.commit()

            logger.error(f"Scraping job {job_id} failed: {e}", exc_info=True)
            raise ScrapingServiceError(f"Scraping processing failed: {e}")

    def get_job(
        self,
        session: Session,
        job_id: uuid.UUID,
    ) -> ScrapeJob:
        """
        Get scraping job by ID.

        Args:
            session: Database session
            job_id: Job ID

        Returns:
            ScrapeJob instance
        """
        job = session.get(ScrapeJob, job_id)
        if not job:
            raise JobNotFoundError(f"Scraping job {job_id} not found")
        return job

    def get_job_result(
        self,
        session: Session,
        job_id: uuid.UUID,
    ) -> ScrapeResult | None:
        """
        Get scraping result for a job.

        Args:
            session: Database session
            job_id: Job ID

        Returns:
            ScrapeResult instance or None if not found
        """
        result = session.exec(
            select(ScrapeResult).where(ScrapeResult.job_id == job_id)
        ).first()
        return result

    def list_jobs(
        self,
        session: Session,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ScrapeJob]:
        """
        List scraping jobs.

        Args:
            session: Database session
            status: Optional status filter
            skip: Skip count
            limit: Limit count

        Returns:
            List of ScrapeJob instances
        """
        statement = select(ScrapeJob)

        if status:
            statement = statement.where(ScrapeJob.status == status)

        statement = (
            statement.order_by(ScrapeJob.started_at.desc()).offset(skip).limit(limit)
        )

        jobs = session.exec(statement).all()
        return list(jobs)

    def _get_engine_client(self, engine: str) -> Any:
        """
        Get client for a specific scraping engine.

        Args:
            engine: Scraping engine name

        Returns:
            Scraping engine client (placeholder for now)
        """
        if engine not in self._scraping_engines:
            # Placeholder client - will be implemented per scraping engine
            self._scraping_engines[engine] = {
                "name": engine,
                "is_available": False,  # Will be True when actual client is initialized
            }

        client = self._scraping_engines[engine]

        if not client.get("is_available"):
            logger.warning(
                f"Scraping engine '{engine}' not available. Using placeholder."
            )

        return client

    def _execute_scraping(
        self,
        client: Any,
        url: str,
        engine: str,
        proxy_id: str | None = None,
        domain_profile: DomainProfile | None = None,
        stealth_config: StealthConfig | None = None,
    ) -> dict[str, Any]:
        """
        Execute scraping on a URL using the specified engine.

        Args:
            client: Scraping engine client
            url: URL to scrape
            engine: Engine name
            proxy_id: Optional proxy ID
            domain_profile: Optional domain profile for behavioral settings
            stealth_config: Optional stealth configuration

        Returns:
            Scraping result dictionary
        """
        # Apply stealth configuration if domain profile requires it
        if domain_profile and domain_profile.captcha_likelihood in ["medium", "high"]:
            if stealth_config is None:
                stealth_config = StealthConfig(
                    enable_ua_rotation=True,
                    enable_timing_randomness=True,
                    enable_fingerprint_spoofing=True,
                    enable_ghost_cursor=True,
                    min_delay_seconds=domain_profile.idle_before_click,
                    max_delay_seconds=domain_profile.idle_before_click * 2,
                )

        # Get stealth headers
        stealth_service = default_stealth_service
        if stealth_config:
            from app.scraping.stealth import StealthService

            stealth_service = StealthService(stealth_config)

        headers = stealth_service.get_stealth_headers()

        # Apply timing delay before scraping
        if stealth_config and stealth_config.enable_timing_randomness:
            stealth_service.apply_timing_delay()

        # Execute HTTP request to fetch the page
        start_time = time.time()
        try:
            # Create request with stealth headers
            req = Request(url, headers=headers)

            # Note: Proxy support would require additional configuration
            # For now, direct requests are made
            # In production, proxy_id would be used to configure proxy settings

            response = urlopen(req, timeout=30)
            status_code = response.getcode()
            html_content = response.read().decode("utf-8", errors="ignore")

            # Extract text content from HTML using simple parser
            text_content = self._extract_text_from_html(html_content)

            latency_ms = int((time.time() - start_time) * 1000)

            logger.info(
                f"Successfully scraped {url} using {engine} (Status: {status_code}, Latency: {latency_ms}ms)"
            )

            return {
                "content": text_content,
                "html": html_content,
                "headers": headers,
                "status_code": status_code,
                "latency_ms": latency_ms,
            }
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error(f"Failed to scrape {url}: {e}")

            # Return error result
            return {
                "content": "",
                "html": "",
                "headers": headers,
                "status_code": 500,
                "latency_ms": latency_ms,
                "block_reason": str(e),
            }

    def _extract_text_from_html(self, html: str) -> str:
        """
        Extract text content from HTML using a simple parser.

        Args:
            html: HTML content string

        Returns:
            Extracted text content
        """

        class TextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text = []
                self.skip_tags = {"script", "style", "meta", "link", "head"}
                self.in_skip_tag = False

            def handle_starttag(self, tag, attrs):
                if tag.lower() in self.skip_tags:
                    self.in_skip_tag = True

            def handle_endtag(self, tag):
                if tag.lower() in self.skip_tags:
                    self.in_skip_tag = False
                elif tag.lower() in {"p", "br", "div", "li"}:
                    self.text.append("\n")

            def handle_data(self, data):
                if not self.in_skip_tag:
                    self.text.append(data.strip())

        try:
            parser = TextExtractor()
            parser.feed(html)
            # Join text and clean up whitespace
            text = " ".join(parser.text)
            # Remove excessive whitespace
            text = re.sub(r"\s+", " ", text)
            return text.strip()
        except Exception as e:
            logger.warning(f"Failed to extract text from HTML: {e}")
            return ""

    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL.

        Args:
            url: URL string

        Returns:
            Domain name
        """
        try:
            parsed = urlparse(url)
            return parsed.netloc or parsed.path.split("/")[0]
        except Exception:
            return "unknown"

    def _get_or_create_domain_profile(
        self,
        session: Session,
        domain: str,
    ) -> DomainProfile:
        """
        Get or create domain profile for behavioral settings.

        Args:
            session: Database session
            domain: Domain name

        Returns:
            DomainProfile instance
        """
        profile = session.exec(
            select(DomainProfile).where(DomainProfile.domain == domain)
        ).first()

        if not profile:
            profile = DomainProfile(
                domain=domain,
                max_requests_per_hour=60,
                requires_login=False,
                captcha_likelihood="low",
                scroll_needed=False,
                idle_before_click=2.0,
            )
            session.add(profile)
            session.commit()
            session.refresh(profile)

        return profile

    def _calculate_content_hash(self, url: str) -> str:
        """
        Calculate content hash for deduplication.

        Args:
            url: URL string

        Returns:
            SHA256 hash string
        """
        # For now, hash the URL itself
        # In production, this would hash the actual content
        return hashlib.sha256(url.encode()).hexdigest()

    def initialize_engine_client(
        self,
        engine: str,
        config: dict[str, Any],
    ) -> None:
        """
        Initialize a scraping engine client.

        Args:
            engine: Scraping engine name
            config: Client configuration
        """
        # Placeholder - will be implemented per scraping engine
        self._scraping_engines[engine] = {
            "name": engine,
            "config": config,
            "is_available": True,
        }
        logger.info(f"Initialized scraping engine client: {engine}")

    def crawl_multiple_pages(
        self,
        session: Session,
        urls: list[str],
        engine: str | None = None,
        proxy_id: str | None = None,
        scrape_requirements: dict[str, Any] | None = None,
    ) -> list[ScrapeJob]:
        """
        Create multiple scraping jobs for multi-page crawling.

        Args:
            session: Database session
            urls: List of URLs to scrape
            engine: Optional engine name (auto-selected if not provided)
            proxy_id: Optional proxy ID
            scrape_requirements: Optional scraping requirements

        Returns:
            List of ScrapeJob instances
        """
        jobs = []

        for url in urls:
            job = self.create_job(
                session=session,
                url=url,
                engine=engine,
                proxy_id=proxy_id,
                scrape_requirements=scrape_requirements,
            )
            jobs.append(job)

        logger.info(f"Created {len(jobs)} scraping jobs for multi-page crawling")

        return jobs


# Default scraping service instance
default_scraping_service = ScrapingService()
