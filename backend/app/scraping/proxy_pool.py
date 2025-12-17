"""
Proxy Pool Manager

Manages proxy rotation, scoring, geolocation filtering, and fallback logic.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from sqlmodel import Session, select

from app.models import ProxyLog

logger = logging.getLogger(__name__)


class ProxyPoolError(Exception):
    """Base exception for proxy pool errors."""
    pass


class NoAvailableProxyError(ProxyPoolError):
    """No available proxy found."""
    pass


class Proxy:
    """
    Proxy representation.
    
    This is a data class for proxy information.
    In production, proxies would be stored in a database or external service.
    """
    
    def __init__(
        self,
        proxy_id: str,
        proxy_type: str,  # residential, isp, mobile, datacenter, vps
        ip_address: str,
        port: int,
        country: str | None = None,
        city: str | None = None,
        username: str | None = None,
        password: str | None = None,
        score: float = 100.0,
        success_count: int = 0,
        failure_count: int = 0,
        last_used_at: datetime | None = None,
        is_active: bool = True,
    ):
        self.proxy_id = proxy_id
        self.proxy_type = proxy_type
        self.ip_address = ip_address
        self.port = port
        self.country = country
        self.city = city
        self.username = username
        self.password = password
        self.score = score
        self.success_count = success_count
        self.failure_count = failure_count
        self.last_used_at = last_used_at
        self.is_active = is_active
    
    def to_dict(self) -> dict[str, Any]:
        """Convert proxy to dictionary."""
        return {
            "proxy_id": self.proxy_id,
            "proxy_type": self.proxy_type,
            "ip_address": self.ip_address,
            "port": self.port,
            "country": self.country,
            "city": self.city,
            "score": self.score,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "is_active": self.is_active,
        }
    
    def get_proxy_url(self) -> str:
        """Get proxy URL for use in requests."""
        if self.username and self.password:
            return f"http://{self.username}:{self.password}@{self.ip_address}:{self.port}"
        return f"http://{self.ip_address}:{self.port}"


class ProxyPoolManager:
    """
    Proxy pool manager with rotation, scoring, and filtering.
    
    Features:
    - Proxy rotation logic
    - Scoring system (success rate, latency, block rate)
    - Geolocation filtering
    - Fallback mechanisms
    - Proxy health tracking
    """
    
    def __init__(self):
        """Initialize proxy pool manager."""
        self._proxies: dict[str, Proxy] = {}
        self._proxy_logs_cache: dict[str, list[ProxyLog]] = {}
    
    def add_proxy(
        self,
        proxy_id: str,
        proxy_type: str,
        ip_address: str,
        port: int,
        country: str | None = None,
        city: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> Proxy:
        """
        Add a proxy to the pool.
        
        Args:
            proxy_id: Unique proxy identifier
            proxy_type: Type of proxy (residential, isp, mobile, datacenter, vps)
            ip_address: Proxy IP address
            port: Proxy port
            country: Optional country code
            city: Optional city name
            username: Optional username for authentication
            password: Optional password for authentication
            
        Returns:
            Proxy instance
        """
        proxy = Proxy(
            proxy_id=proxy_id,
            proxy_type=proxy_type,
            ip_address=ip_address,
            port=port,
            country=country,
            city=city,
            username=username,
            password=password,
        )
        self._proxies[proxy_id] = proxy
        logger.info(f"Added proxy to pool: {proxy_id} ({proxy_type}, {country or 'unknown'})")
        return proxy
    
    def get_proxy(
        self,
        session: Session,
        domain: str | None = None,
        country: str | None = None,
        proxy_type: str | None = None,
        exclude_proxy_ids: list[str] | None = None,
    ) -> Proxy:
        """
        Get the best available proxy based on scoring and filters.
        
        Args:
            session: Database session for proxy logs
            domain: Optional domain to scrape (for domain-specific proxy selection)
            country: Optional country filter
            proxy_type: Optional proxy type filter
            exclude_proxy_ids: Optional list of proxy IDs to exclude
            
        Returns:
            Best available Proxy instance
            
        Raises:
            NoAvailableProxyError: If no proxy is available
        """
        # Filter proxies
        available_proxies = [
            proxy
            for proxy in self._proxies.values()
            if proxy.is_active
            and (country is None or proxy.country == country)
            and (proxy_type is None or proxy.proxy_type == proxy_type)
            and (exclude_proxy_ids is None or proxy.proxy_id not in exclude_proxy_ids)
        ]
        
        if not available_proxies:
            raise NoAvailableProxyError("No available proxy found matching criteria")
        
        # Update scores based on recent performance
        for proxy in available_proxies:
            self._update_proxy_score(session, proxy, domain)
        
        # Sort by score (highest first), then by last_used_at (least recently used)
        available_proxies.sort(
            key=lambda p: (
                -p.score,  # Higher score first
                p.last_used_at if p.last_used_at else datetime.min,  # Least recently used first
            )
        )
        
        selected_proxy = available_proxies[0]
        selected_proxy.last_used_at = datetime.utcnow()
        
        logger.info(
            f"Selected proxy: {selected_proxy.proxy_id} "
            f"(Score: {selected_proxy.score:.2f}, Type: {selected_proxy.proxy_type}, "
            f"Country: {selected_proxy.country or 'unknown'})"
        )
        
        return selected_proxy
    
    def record_proxy_usage(
        self,
        session: Session,
        proxy_id: str,
        domain: str,
        status_code: int | None = None,
        latency_ms: int = 0,
        block_reason: str | None = None,
        agent_id: str | None = None,
    ) -> None:
        """
        Record proxy usage for scoring.
        
        Args:
            session: Database session
            proxy_id: Proxy ID
            domain: Domain that was scraped
            status_code: HTTP status code
            latency_ms: Request latency in milliseconds
            block_reason: Optional block reason if proxy was blocked
            agent_id: Optional agent ID
        """
        proxy = self._proxies.get(proxy_id)
        if not proxy:
            logger.warning(f"Proxy {proxy_id} not found in pool")
            return
        
        # Create proxy log
        proxy_log = ProxyLog(
            ip_id=proxy_id,
            agent_id=agent_id,
            domain_scraped=domain,
            status_code=status_code,
            latency_ms=latency_ms,
            block_reason=block_reason,
            timestamp=datetime.utcnow(),
        )
        session.add(proxy_log)
        session.commit()
        session.refresh(proxy_log)
        
        # Update proxy statistics
        if status_code and 200 <= status_code < 300:
            proxy.success_count += 1
        elif status_code and status_code >= 400:
            proxy.failure_count += 1
        
        # Update score based on result
        self._update_proxy_score(session, proxy, domain)
        
        logger.debug(
            f"Recorded proxy usage: {proxy_id} for {domain} "
            f"(Status: {status_code}, Latency: {latency_ms}ms, Block: {block_reason})"
        )
    
    def _update_proxy_score(
        self,
        session: Session,
        proxy: Proxy,
        domain: str | None = None,
    ) -> None:
        """
        Update proxy score based on recent performance.
        
        Scoring factors:
        - Success rate (weight: 0.4)
        - Average latency (weight: 0.3)
        - Block rate (weight: 0.3)
        
        Args:
            session: Database session
            proxy: Proxy instance
            domain: Optional domain for domain-specific scoring
        """
        # Get recent proxy logs (last 24 hours)
        since = datetime.utcnow() - timedelta(hours=24)
        
        query = select(ProxyLog).where(
            ProxyLog.ip_id == proxy.proxy_id,
            ProxyLog.timestamp >= since,
        )
        
        if domain:
            query = query.where(ProxyLog.domain_scraped == domain)
        
        logs = session.exec(query).all()
        
        if not logs:
            # No recent logs, keep current score
            return
        
        # Calculate metrics
        total_requests = len(logs)
        successful_requests = sum(1 for log in logs if log.status_code and 200 <= log.status_code < 300)
        failed_requests = sum(1 for log in logs if log.status_code and log.status_code >= 400)
        blocked_requests = sum(1 for log in logs if log.block_reason is not None)
        
        avg_latency = sum(log.latency_ms for log in logs) / total_requests if total_requests > 0 else 0
        
        # Calculate scores (0-100 scale)
        success_rate_score = (successful_requests / total_requests * 100) if total_requests > 0 else 50
        latency_score = max(0, 100 - (avg_latency / 10))  # Lower latency = higher score
        block_rate_score = max(0, 100 - (blocked_requests / total_requests * 100)) if total_requests > 0 else 50
        
        # Weighted score
        proxy.score = (
            success_rate_score * 0.4
            + latency_score * 0.3
            + block_rate_score * 0.3
        )
        
        # Penalize proxies with high failure rates
        if failed_requests > successful_requests:
            proxy.score *= 0.5  # Reduce score by 50%
        
        # Deactivate proxies with very low scores
        if proxy.score < 20:
            proxy.is_active = False
            logger.warning(f"Deactivated proxy {proxy.proxy_id} due to low score: {proxy.score:.2f}")
    
    def rotate_proxy(
        self,
        session: Session,
        current_proxy_id: str | None = None,
        domain: str | None = None,
        country: str | None = None,
        proxy_type: str | None = None,
    ) -> Proxy:
        """
        Rotate to the next available proxy.
        
        Args:
            session: Database session
            current_proxy_id: Current proxy ID to rotate away from
            domain: Optional domain for domain-specific selection
            country: Optional country filter
            proxy_type: Optional proxy type filter
            
        Returns:
            New Proxy instance
            
        Raises:
            NoAvailableProxyError: If no proxy is available
        """
        exclude_proxy_ids = [current_proxy_id] if current_proxy_id else None
        return self.get_proxy(
            session=session,
            domain=domain,
            country=country,
            proxy_type=proxy_type,
            exclude_proxy_ids=exclude_proxy_ids,
        )
    
    def get_proxy_by_id(self, proxy_id: str) -> Proxy | None:
        """
        Get proxy by ID.
        
        Args:
            proxy_id: Proxy ID
            
        Returns:
            Proxy instance or None if not found
        """
        return self._proxies.get(proxy_id)
    
    def list_proxies(
        self,
        country: str | None = None,
        proxy_type: str | None = None,
        active_only: bool = True,
    ) -> list[Proxy]:
        """
        List proxies with optional filters.
        
        Args:
            country: Optional country filter
            proxy_type: Optional proxy type filter
            active_only: Only return active proxies
            
        Returns:
            List of Proxy instances
        """
        proxies = list(self._proxies.values())
        
        if active_only:
            proxies = [p for p in proxies if p.is_active]
        
        if country:
            proxies = [p for p in proxies if p.country == country]
        
        if proxy_type:
            proxies = [p for p in proxies if p.proxy_type == proxy_type]
        
        return sorted(proxies, key=lambda p: -p.score)  # Sort by score descending
    
    def deactivate_proxy(self, proxy_id: str, reason: str | None = None) -> None:
        """
        Deactivate a proxy.
        
        Args:
            proxy_id: Proxy ID
            reason: Optional reason for deactivation
        """
        proxy = self._proxies.get(proxy_id)
        if proxy:
            proxy.is_active = False
            logger.info(f"Deactivated proxy {proxy_id}: {reason or 'Manual deactivation'}")
    
    def activate_proxy(self, proxy_id: str) -> None:
        """
        Activate a proxy.
        
        Args:
            proxy_id: Proxy ID
        """
        proxy = self._proxies.get(proxy_id)
        if proxy:
            proxy.is_active = True
            proxy.score = 100.0  # Reset score when reactivating
            logger.info(f"Activated proxy {proxy_id}")
    
    def get_proxy_statistics(
        self,
        session: Session,
        proxy_id: str,
        domain: str | None = None,
        hours: int = 24,
    ) -> dict[str, Any]:
        """
        Get statistics for a proxy.
        
        Args:
            session: Database session
            proxy_id: Proxy ID
            domain: Optional domain filter
            hours: Number of hours to look back
            
        Returns:
            Statistics dictionary
        """
        proxy = self._proxies.get(proxy_id)
        if not proxy:
            return {"error": "Proxy not found"}
        
        since = datetime.utcnow() - timedelta(hours=hours)
        
        query = select(ProxyLog).where(
            ProxyLog.ip_id == proxy_id,
            ProxyLog.timestamp >= since,
        )
        
        if domain:
            query = query.where(ProxyLog.domain_scraped == domain)
        
        logs = session.exec(query).all()
        
        total_requests = len(logs)
        successful_requests = sum(1 for log in logs if log.status_code and 200 <= log.status_code < 300)
        failed_requests = sum(1 for log in logs if log.status_code and log.status_code >= 400)
        blocked_requests = sum(1 for log in logs if log.block_reason is not None)
        avg_latency = sum(log.latency_ms for log in logs) / total_requests if total_requests > 0 else 0
        
        return {
            "proxy_id": proxy_id,
            "proxy_type": proxy.proxy_type,
            "country": proxy.country,
            "score": proxy.score,
            "is_active": proxy.is_active,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "blocked_requests": blocked_requests,
            "success_rate": (successful_requests / total_requests * 100) if total_requests > 0 else 0,
            "block_rate": (blocked_requests / total_requests * 100) if total_requests > 0 else 0,
            "avg_latency_ms": round(avg_latency, 2),
            "last_used_at": proxy.last_used_at.isoformat() if proxy.last_used_at else None,
        }


# Default proxy pool manager instance
default_proxy_pool = ProxyPoolManager()

