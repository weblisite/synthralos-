"""
Browser Automation Service

Multi-engine browser automation service with proxy support and behavioral stealth.
Handles routing logic for multiple browser automation engines.
"""

import asyncio
import base64
import logging
import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from app.models import BrowserAction, BrowserSession, ChangeDetection
from app.scraping.proxy_pool import NoAvailableProxyError, default_proxy_pool

logger = logging.getLogger(__name__)


class BrowserServiceError(Exception):
    """Base exception for browser service errors."""

    pass


class SessionNotFoundError(BrowserServiceError):
    """Browser session not found."""

    pass


class EngineNotAvailableError(BrowserServiceError):
    """Browser engine not available."""

    pass


class BrowserService:
    """
    Browser automation service for multi-engine browser automation.

    Routing Logic:
    - js_heavy = true → Playwright
    - headless_chrome = true → Puppeteer
    - lightweight = true → browser-use.com
    - llm_guided = true → AI Browser Agent
    - fleet_scale = true → Browserbase/Stagehand
    - anti_bot = true → Undetected-Chromedriver
    - cloudflare_bypass = true → Cloudscraper
    """

    def __init__(self):
        """Initialize browser service."""
        self._browser_engines: dict[str, Any] = {}
        self._initialize_engines()

    def _initialize_engines(self) -> None:
        """Initialize available browser engines."""
        # Playwright
        try:
            from playwright.async_api import async_playwright

            self._browser_engines["playwright"] = {
                "name": "playwright",
                "is_available": True,
                "async_playwright": async_playwright,
            }
            logger.info("✅ Playwright browser engine initialized")
        except ImportError:
            logger.info(
                "playwright not installed. Install with: pip install playwright && playwright install"
            )
            self._browser_engines["playwright"] = {
                "name": "playwright",
                "is_available": False,
            }

        # Puppeteer (use Playwright as alternative)
        # Note: Puppeteer is Node.js-based, so we'll use Playwright as the primary engine
        # and mark Puppeteer as available if Playwright is available
        if self._browser_engines.get("playwright", {}).get("is_available"):
            self._browser_engines["puppeteer"] = {
                "name": "puppeteer",
                "is_available": True,  # Use Playwright as Puppeteer alternative
                "use_playwright": True,
            }
            logger.info("✅ Puppeteer (via Playwright) browser engine initialized")
        else:
            self._browser_engines["puppeteer"] = {
                "name": "puppeteer",
                "is_available": False,
            }

    def select_engine(
        self,
        automation_requirements: dict[str, Any] | None = None,
    ) -> str:
        """
        Select appropriate browser automation engine.

        Args:
            automation_requirements: Optional automation requirements dictionary

        Returns:
            Browser engine name (e.g., "playwright", "puppeteer", "browserbase")
        """
        if not automation_requirements:
            automation_requirements = {}

        # Extract requirements
        js_heavy = automation_requirements.get("js_heavy", False)
        headless_chrome = automation_requirements.get("headless_chrome", False)
        lightweight = automation_requirements.get("lightweight", False)
        llm_guided = automation_requirements.get("llm_guided", False)
        fleet_scale = automation_requirements.get("fleet_scale", False)
        anti_bot = automation_requirements.get("anti_bot", False)
        cloudflare_bypass = automation_requirements.get("cloudflare_bypass", False)

        # Routing logic (in priority order)

        # Cloudflare bypass → Cloudscraper
        if cloudflare_bypass:
            return "cloudscraper"

        # Anti-bot detection → Undetected-Chromedriver
        if anti_bot:
            return "undetected_chromedriver"

        # Fleet-scale → Browserbase/Stagehand
        if fleet_scale:
            return "browserbase"

        # LLM-guided → AI Browser Agent
        if llm_guided:
            return "ai_browser_agent"

        # Lightweight → browser-use.com
        if lightweight:
            return "browser_use"

        # Headless Chrome → Puppeteer
        if headless_chrome:
            return "puppeteer"

        # JS-heavy → Playwright (default)
        if js_heavy:
            return "playwright"

        # Default to Playwright
        return "playwright"

    def create_session(
        self,
        session: Session,
        browser_tool: str | None = None,
        proxy_id: str | None = None,
        automation_requirements: dict[str, Any] | None = None,
        auto_select_proxy: bool = True,
    ) -> BrowserSession:
        """
        Create a new browser session.

        Args:
            session: Database session
            browser_tool: Optional browser tool name (auto-selected if not provided)
            proxy_id: Optional proxy ID
            automation_requirements: Optional automation requirements
            auto_select_proxy: Whether to auto-select proxy if not provided

        Returns:
            BrowserSession instance
        """
        # Select engine if not provided
        if not browser_tool:
            browser_tool = self.select_engine(
                automation_requirements=automation_requirements,
            )

        # Auto-select proxy if not provided and auto_select_proxy is True
        if not proxy_id and auto_select_proxy:
            try:
                proxy = default_proxy_pool.get_proxy(
                    session=session,
                    country=automation_requirements.get("country")
                    if automation_requirements
                    else None,
                    proxy_type=automation_requirements.get("proxy_type")
                    if automation_requirements
                    else None,
                )
                proxy_id = proxy.proxy_id
                logger.info(f"Auto-selected proxy: {proxy_id} for browser session")
            except NoAvailableProxyError:
                logger.warning("No proxy available, proceeding without proxy")
                proxy_id = None

        # Generate session ID
        session_id = str(uuid.uuid4())

        # Create browser session
        browser_session = BrowserSession(
            session_id=session_id,
            browser_tool=browser_tool,
            proxy_id=proxy_id,
            status="active",
            started_at=datetime.utcnow(),
        )
        session.add(browser_session)
        session.commit()
        session.refresh(browser_session)

        logger.info(
            f"Created browser session: {browser_session.id} (Engine: {browser_tool})"
        )

        return browser_session

    def execute_action(
        self,
        session: Session,
        session_id: uuid.UUID,
        action_type: str,
        action_data: dict[str, Any],
    ) -> BrowserAction:
        """
        Execute a browser action.

        Args:
            session: Database session
            session_id: Browser session ID
            action_type: Action type (navigate, click, fill, screenshot, etc.)
            action_data: Action data dictionary

        Returns:
            BrowserAction instance
        """
        browser_session = session.get(BrowserSession, session_id)
        if not browser_session:
            raise SessionNotFoundError(f"Browser session {session_id} not found")

        if browser_session.status != "active":
            raise BrowserServiceError(f"Browser session {session_id} is not active")

        # Get browser engine client
        engine_client = self._get_engine_client(browser_session.browser_tool)

        # Execute action
        try:
            result_data = self._execute_browser_action(
                client=engine_client,
                browser_session=browser_session,
                action_type=action_type,
                action_data=action_data,
            )

            # Create action record
            action = BrowserAction(
                session_id=browser_session.id,
                action_type=action_type,
                action_data=action_data,
                result=result_data,
                timestamp=datetime.utcnow(),
            )
            session.add(action)
            session.commit()
            session.refresh(action)

            logger.info(
                f"Executed browser action: {action_type} for session {session_id}"
            )

            return action

        except Exception as e:
            logger.error(f"Browser action failed: {e}", exc_info=True)
            raise BrowserServiceError(f"Browser action execution failed: {e}")

    def get_session(
        self,
        session: Session,
        session_id: uuid.UUID,
    ) -> BrowserSession:
        """
        Get browser session by ID.

        Args:
            session: Database session
            session_id: Session ID

        Returns:
            BrowserSession instance
        """
        browser_session = session.get(BrowserSession, session_id)
        if not browser_session:
            raise SessionNotFoundError(f"Browser session {session_id} not found")
        return browser_session

    def list_sessions(
        self,
        session: Session,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[BrowserSession]:
        """
        List browser sessions with optional status filter.

        Args:
            session: Database session
            status: Optional status filter (active, closed, error)
            skip: Skip count
            limit: Limit count

        Returns:
            List of BrowserSession instances
        """
        statement = select(BrowserSession)

        if status:
            statement = statement.where(BrowserSession.status == status)

        statement = (
            statement.order_by(BrowserSession.started_at.desc())
            .offset(skip)
            .limit(limit)
        )

        sessions = session.exec(statement).all()

        return list(sessions)

    def get_session_actions(
        self,
        session: Session,
        session_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[BrowserAction]:
        """
        Get actions for a browser session.

        Args:
            session: Database session
            session_id: Session ID
            skip: Skip count
            limit: Limit count

        Returns:
            List of BrowserAction instances
        """
        browser_session = self.get_session(session, session_id)

        actions = session.exec(
            select(BrowserAction)
            .where(BrowserAction.session_id == browser_session.id)
            .order_by(BrowserAction.timestamp.desc())
            .offset(skip)
            .limit(limit)
        ).all()

        return list(actions)

    def close_session(
        self,
        session: Session,
        session_id: uuid.UUID,
    ) -> BrowserSession:
        """
        Close a browser session.

        Args:
            session: Database session
            session_id: Session ID

        Returns:
            BrowserSession instance
        """
        browser_session = self.get_session(session, session_id)

        browser_session.status = "closed"
        browser_session.closed_at = datetime.utcnow()
        session.add(browser_session)
        session.commit()
        session.refresh(browser_session)

        logger.info(f"Closed browser session: {session_id}")

        return browser_session

    def monitor_page_changes(
        self,
        session: Session,
        url: str,
        check_interval_seconds: int = 60,
        previous_content: str | None = None,
    ) -> ChangeDetection | None:
        """
        Monitor a page for changes.

        Args:
            session: Database session
            url: URL to monitor
            check_interval_seconds: Interval between checks
            previous_content: Previous content for comparison

        Returns:
            ChangeDetection instance if changes detected, None otherwise
        """
        # Placeholder implementation
        # Will be replaced with actual change detection logic

        # For now, create a placeholder change detection
        # In production, this would:
        # 1. Fetch current page content
        # 2. Compare with previous content
        # 3. Detect changes (added, modified, deleted)
        # 4. Store change detection record

        return None

    def _get_engine_client(self, engine: str) -> Any:
        """
        Get client for a specific browser engine.

        Args:
            engine: Browser engine name

        Returns:
            Browser engine client
        """
        if engine not in self._browser_engines:
            # Unknown engine - create placeholder
            self._browser_engines[engine] = {
                "name": engine,
                "is_available": False,
            }

        client = self._browser_engines[engine]

        if not client.get("is_available"):
            logger.warning(
                f"Browser engine '{engine}' not available. Falling back to Playwright or placeholder."
            )
            # Try to fallback to Playwright if available
            if self._browser_engines.get("playwright", {}).get("is_available"):
                return self._browser_engines["playwright"]

        return client

    def _execute_browser_action(
        self,
        client: Any,
        browser_session: BrowserSession,
        action_type: str,
        action_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute a browser action using the specified engine.

        Args:
            client: Browser engine client
            browser_session: Browser session
            action_type: Action type
            action_data: Action data

        Returns:
            Action result dictionary
        """
        if not client.get("is_available"):
            return {
                "action_type": action_type,
                "status": "error",
                "message": f"Browser engine '{client.get('name', 'unknown')}' not available. Please install required dependencies.",
            }

        engine_name = client.get("name", "unknown")

        # Use Playwright for both playwright and puppeteer engines
        if engine_name in ["playwright", "puppeteer"]:
            return self._execute_playwright_action(
                client, browser_session, action_type, action_data
            )
        else:
            # Unknown engine, try Playwright as fallback
            if self._browser_engines.get("playwright", {}).get("is_available"):
                logger.info(
                    f"Unknown engine '{engine_name}', falling back to Playwright"
                )
                return self._execute_playwright_action(
                    self._browser_engines["playwright"],
                    browser_session,
                    action_type,
                    action_data,
                )
            else:
                return {
                    "action_type": action_type,
                    "status": "error",
                    "message": f"Unknown browser engine '{engine_name}' and no fallback available",
                }

    def _execute_playwright_action(
        self,
        client: Any,
        browser_session: BrowserSession,
        action_type: str,
        action_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute browser action using Playwright."""
        try:
            # Run async Playwright code in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    self._async_execute_playwright_action(
                        client, browser_session, action_type, action_data
                    )
                )
            finally:
                loop.close()
            return result
        except Exception as e:
            logger.error(f"Playwright action execution failed: {e}", exc_info=True)
            return {
                "action_type": action_type,
                "status": "error",
                "message": f"Playwright execution failed: {str(e)}",
            }

    async def _async_execute_playwright_action(
        self,
        client: Any,
        browser_session: BrowserSession,
        action_type: str,
        action_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Async Playwright action execution."""
        async_playwright = client["async_playwright"]

        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=action_data.get(
                    "user_agent",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                ),
                viewport={"width": 1920, "height": 1080},
            )
            page = await context.new_page()

            try:
                if action_type == "navigate":
                    url = action_data.get("url", "")
                    await page.goto(url, wait_until="networkidle", timeout=30000)
                    content = await page.content()
                    return {
                        "action_type": action_type,
                        "status": "success",
                        "url": url,
                        "content": content[:1000],  # Limit content size
                        "title": await page.title(),
                    }

                elif action_type == "click":
                    selector = action_data.get("selector", "")
                    await page.click(selector)
                    return {
                        "action_type": action_type,
                        "status": "success",
                        "selector": selector,
                    }

                elif action_type == "fill":
                    selector = action_data.get("selector", "")
                    text = action_data.get("text", "")
                    await page.fill(selector, text)
                    return {
                        "action_type": action_type,
                        "status": "success",
                        "selector": selector,
                    }

                elif action_type == "screenshot":
                    screenshot_bytes = await page.screenshot(
                        full_page=action_data.get("full_page", False)
                    )
                    screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")
                    return {
                        "action_type": action_type,
                        "status": "success",
                        "screenshot": screenshot_b64,
                    }

                elif action_type == "evaluate":
                    script = action_data.get("script", "")
                    result = await page.evaluate(script)
                    return {
                        "action_type": action_type,
                        "status": "success",
                        "result": result,
                    }

                else:
                    return {
                        "action_type": action_type,
                        "status": "error",
                        "message": f"Unknown action type: {action_type}",
                    }
            finally:
                await browser.close()

    def initialize_engine_client(
        self,
        engine: str,
        config: dict[str, Any],
    ) -> None:
        """
        Initialize a browser engine client.

        Args:
            engine: Browser engine name
            config: Client configuration
        """
        # Placeholder - will be implemented per browser engine
        self._browser_engines[engine] = {
            "name": engine,
            "config": config,
            "is_available": True,
        }
        logger.info(f"Initialized browser engine client: {engine}")


# Default browser service instance
default_browser_service = BrowserService()
