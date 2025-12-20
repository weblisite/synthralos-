"""
OSINT Service

Multi-engine OSINT service with routing logic for:
- Twint (Twitter scraping)
- Tweepy (Twitter API)
- Social-Listener (multi-platform)
- NewsCatcher (news aggregation)
- Huginn (automation/scraping)
"""

import logging
from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from app.core.config import settings
from app.models import OSINTAlert, OSINTSignal, OSINTStream

logger = logging.getLogger(__name__)


class OSINTServiceError(Exception):
    """Base exception for OSINT service errors."""

    pass


class EngineNotAvailableError(OSINTServiceError):
    """OSINT engine not available."""

    pass


class OSINTService:
    """
    OSINT service for multi-engine OSINT operations.

    Routes queries to appropriate engines based on:
    - Platform (Twitter, Reddit, News, etc.)
    - Query type (streaming, batch, alerts)
    - Engine availability
    - Rate limits
    """

    def __init__(self):
        """Initialize OSINT service."""
        self._engines: dict[str, Any] = {}
        self._initialize_engines()

    def _initialize_engines(self) -> None:
        """Initialize OSINT engines."""
        # Tweepy (Twitter API)
        try:
            import tweepy

            if settings.TWITTER_BEARER_TOKEN:
                # Use Bearer Token authentication (v2 API)
                client = tweepy.Client(bearer_token=settings.TWITTER_BEARER_TOKEN)
                self._engines["tweepy"] = {
                    "name": "tweepy",
                    "is_available": True,
                    "client": client,
                    "auth_type": "bearer",
                }
                logger.info("✅ Tweepy engine initialized (Bearer Token)")
            elif settings.TWITTER_API_KEY and settings.TWITTER_API_SECRET:
                # Use API Key/Secret authentication (v1.1 API)
                auth = tweepy.OAuthHandler(
                    settings.TWITTER_API_KEY,
                    settings.TWITTER_API_SECRET,
                )
                if (
                    settings.TWITTER_ACCESS_TOKEN
                    and settings.TWITTER_ACCESS_TOKEN_SECRET
                ):
                    auth.set_access_token(
                        settings.TWITTER_ACCESS_TOKEN,
                        settings.TWITTER_ACCESS_TOKEN_SECRET,
                    )
                api = tweepy.API(auth)
                self._engines["tweepy"] = {
                    "name": "tweepy",
                    "is_available": True,
                    "client": api,
                    "auth_type": "oauth",
                }
                logger.info("✅ Tweepy engine initialized (OAuth)")
            else:
                self._engines["tweepy"] = {
                    "name": "tweepy",
                    "is_available": False,
                }
                logger.info("Tweepy not configured (missing API credentials)")
        except ImportError:
            logger.info("tweepy not installed. Install with: pip install tweepy")
            self._engines["tweepy"] = {
                "name": "tweepy",
                "is_available": False,
            }
        except Exception as e:
            logger.warning(f"Tweepy initialization failed: {e}")
            self._engines["tweepy"] = {
                "name": "tweepy",
                "is_available": False,
            }

        # Initialize other engines as unavailable (to be implemented)
        self._engines.setdefault("twint", {"name": "twint", "is_available": False})
        self._engines.setdefault(
            "social_listener", {"name": "social_listener", "is_available": False}
        )
        self._engines.setdefault(
            "newscatcher", {"name": "newscatcher", "is_available": False}
        )
        self._engines.setdefault("huginn", {"name": "huginn", "is_available": False})

    def select_engine(
        self,
        platform: str,
        query_type: str,
        requirements: dict[str, Any] | None = None,
    ) -> str:
        """
        Select appropriate OSINT engine for a query.

        Routing Logic:
        - platform = twitter → Twint (scraping) or Tweepy (API)
        - query_type = stream → Twint/Social-Listener
        - query_type = batch → Tweepy/NewsCatcher
        - platform = news → NewsCatcher
        - multi_platform = true → Social-Listener/Huginn

        Args:
            platform: Target platform (twitter, reddit, news, etc.)
            query_type: Query type (stream, batch, alert)
            requirements: Optional requirements dictionary

        Returns:
            Engine name (e.g., "twint", "tweepy", "newscatcher")
        """
        if not requirements:
            requirements = {}

        # Check for explicit engine preference
        preferred_engine = requirements.get("engine")
        if preferred_engine and preferred_engine in self._engines:
            return preferred_engine

        # Routing logic based on platform and query type
        platform_lower = platform.lower()

        # Twitter platform
        if platform_lower == "twitter":
            if query_type == "stream":
                # Streaming → Twint (scraping)
                return "twint"
            elif query_type == "batch":
                # Batch → Tweepy (API)
                return "tweepy"
            else:
                # Default to Twint
                return "twint"

        # News platform
        elif platform_lower == "news":
            return "newscatcher"

        # Multi-platform
        elif requirements.get("multi_platform", False):
            return "social_listener"

        # Default to Social-Listener for unknown platforms
        return "social_listener"

    def create_stream(
        self,
        session: Session,
        platform: str,
        keywords: list[str],
        engine: str | None = None,
        requirements: dict[str, Any] | None = None,
    ) -> OSINTStream:
        """
        Create a new OSINT stream.

        Args:
            session: Database session
            platform: Target platform
            keywords: List of keywords to monitor
            engine: Optional engine name (auto-selected if not provided)
            requirements: Optional requirements dictionary

        Returns:
            OSINTStream instance
        """
        # Select engine if not provided
        if not engine:
            engine = self.select_engine(platform, "stream", requirements)

        # Create stream record
        osint_stream = OSINTStream(
            platform=platform,
            keywords=keywords,
            engine=engine,
            is_active=True,
        )
        session.add(osint_stream)
        session.commit()
        session.refresh(osint_stream)

        logger.info(
            f"Created OSINT stream: {osint_stream.id} (Platform: {platform}, Engine: {engine})"
        )

        return osint_stream

    def execute_stream(
        self,
        session: Session,
        stream_id: str,
    ) -> list[OSINTSignal]:
        """
        Execute an OSINT stream and collect signals.

        Args:
            session: Database session
            stream_id: Stream ID

        Returns:
            List of OSINTSignal instances

        Raises:
            OSINTServiceError: If execution fails
        """
        # Get stream
        stream = session.get(OSINTStream, stream_id)
        if not stream:
            raise OSINTServiceError(f"OSINT stream {stream_id} not found")

        if not stream.is_active:
            raise OSINTServiceError(f"OSINT stream {stream_id} is not active")

        try:
            # Get engine handler
            engine_handler = self._get_engine_handler(stream.engine)

            # Execute stream using engine
            result_data = self._execute_with_engine(
                engine_handler,
                stream.platform,
                " ".join(stream.keywords),
                "stream",
            )

            # Create signal records
            signals = []
            for item in result_data.get("items", []):
                signal = OSINTSignal(
                    stream_id=stream.id,
                    source=item.get("source", stream.platform),
                    author=item.get("author"),
                    text=item.get("text", ""),
                    media=item.get("media", []),
                    link=item.get("link"),
                    sentiment_score=item.get("sentiment_score"),
                )
                session.add(signal)
                signals.append(signal)

            session.commit()

            # Refresh signals
            for signal in signals:
                session.refresh(signal)

            logger.info(f"Executed OSINT stream: {stream_id} (Signals: {len(signals)})")

            return signals

        except Exception as e:
            logger.error(f"OSINT stream execution failed: {stream_id}", exc_info=True)
            raise OSINTServiceError(f"Stream execution failed: {e}")

    def stream_signals(
        self,
        session: Session,
        stream_id: str,
    ) -> Any:
        """
        Stream OSINT signals in real-time.

        Args:
            session: Database session
            stream_id: Stream ID

        Yields:
            Signal chunks
        """
        # Get stream
        stream = session.get(OSINTStream, stream_id)
        if not stream:
            raise OSINTServiceError(f"OSINT stream {stream_id} not found")

        if not stream.is_active:
            raise OSINTServiceError(f"OSINT stream {stream_id} is not active")

        # Get engine handler
        engine_handler = self._get_engine_handler(stream.engine)

        # Stream results
        # TODO: Implement streaming logic per engine
        # For now, return placeholder
        yield {
            "type": "signal",
            "stream_id": str(stream.id),
            "data": {},
            "timestamp": datetime.utcnow().isoformat(),
        }

    def create_alert(
        self,
        session: Session,
        stream_id: str | None,
        alert_type: str,
        message: str,
        severity: str = "medium",
    ) -> OSINTAlert:
        """
        Create an OSINT alert.

        Args:
            session: Database session
            stream_id: Optional stream ID (if alert is related to a stream)
            alert_type: Alert type
            message: Alert message
            severity: Alert severity (low, medium, high, critical)

        Returns:
            OSINTAlert instance
        """
        # Create alert record
        alert = OSINTAlert(
            stream_id=stream_id,
            alert_type=alert_type,
            message=message,
            severity=severity,
            is_read=False,
        )
        session.add(alert)
        session.commit()
        session.refresh(alert)

        logger.info(
            f"Created OSINT alert: {alert.id} (Type: {alert_type}, Severity: {severity})"
        )

        return alert

    def check_stream_alerts(
        self,
        session: Session,
        stream_id: str,
        alert_conditions: dict[str, Any],
    ) -> OSINTAlert | None:
        """
        Check stream signals against alert conditions and create alert if conditions met.

        Args:
            session: Database session
            stream_id: Stream ID
            alert_conditions: Alert conditions dictionary

        Returns:
            OSINTAlert instance if conditions met, None otherwise
        """
        # Get stream
        stream = session.get(OSINTStream, stream_id)
        if not stream:
            raise OSINTServiceError(f"OSINT stream {stream_id} not found")

        # Get recent signals
        recent_signals = session.exec(
            select(OSINTSignal)
            .where(OSINTSignal.stream_id == stream.id)
            .order_by(OSINTSignal.created_at.desc())
            .limit(100)
        ).all()

        # Check alert conditions
        if self._check_alert_conditions(recent_signals, alert_conditions):
            # Create alert
            alert = self.create_alert(
                session,
                stream_id=stream.id,
                alert_type=alert_conditions.get("alert_type", "threshold_exceeded"),
                message=alert_conditions.get("message", "Alert conditions met"),
                severity=alert_conditions.get("severity", "medium"),
            )
            return alert

        return None

    def _get_engine_handler(self, engine: str) -> Any:
        """
        Get handler for a specific engine.

        Args:
            engine: Engine name

        Returns:
            Engine handler instance

        Raises:
            EngineNotAvailableError: If engine not found
        """
        if engine not in self._engines:
            raise EngineNotAvailableError(f"Engine '{engine}' not found")

        handler = self._engines[engine]
        if handler is None:
            raise EngineNotAvailableError(f"Engine '{engine}' not available")

        return handler

    def _execute_with_engine(
        self,
        handler: Any,
        platform: str,
        query_text: str,
        query_type: str,
    ) -> dict[str, Any]:
        """
        Execute query using engine handler.

        Args:
            handler: Engine handler instance
            platform: Target platform
            query_text: Query text
            query_type: Query type

        Returns:
            Result data dictionary
        """
        engine_name = handler.get("name", "unknown")

        if engine_name == "tweepy" and handler.get("is_available"):
            return self._execute_tweepy(handler, platform, query_text, query_type)
        else:
            # Unknown or unavailable engine
            return {
                "items": [],
                "total_count": 0,
                "platform": platform,
                "query_text": query_text,
                "query_type": query_type,
                "timestamp": datetime.utcnow().isoformat(),
                "error": f"Engine '{engine_name}' not available",
            }

    def _execute_tweepy(
        self,
        handler: dict[str, Any],
        platform: str,
        query_text: str,
        query_type: str,
    ) -> dict[str, Any]:
        """Execute query using Tweepy."""
        try:
            client = handler["client"]
            auth_type = handler.get("auth_type", "bearer")

            items = []

            if auth_type == "bearer":
                # Twitter API v2 (Bearer Token)

                if query_type == "search":
                    # Search tweets
                    tweets = client.search_recent_tweets(
                        query=query_text,
                        max_results=10,
                        tweet_fields=["created_at", "author_id", "public_metrics"],
                    )

                    if tweets.data:
                        for tweet in tweets.data:
                            items.append(
                                {
                                    "id": tweet.id,
                                    "text": tweet.text,
                                    "created_at": tweet.created_at.isoformat()
                                    if tweet.created_at
                                    else None,
                                    "author_id": tweet.author_id,
                                    "metrics": tweet.public_metrics
                                    if hasattr(tweet, "public_metrics")
                                    else {},
                                }
                            )

                elif query_type == "user":
                    # Get user tweets
                    user = client.get_user(username=query_text)
                    if user.data:
                        tweets = client.get_users_tweets(
                            user.data.id,
                            max_results=10,
                            tweet_fields=["created_at", "public_metrics"],
                        )
                        if tweets.data:
                            for tweet in tweets.data:
                                items.append(
                                    {
                                        "id": tweet.id,
                                        "text": tweet.text,
                                        "created_at": tweet.created_at.isoformat()
                                        if tweet.created_at
                                        else None,
                                        "metrics": tweet.public_metrics
                                        if hasattr(tweet, "public_metrics")
                                        else {},
                                    }
                                )

            elif auth_type == "oauth":
                # Twitter API v1.1 (OAuth)
                if query_type == "search":
                    tweets = client.search_tweets(
                        q=query_text, count=10, tweet_mode="extended"
                    )
                    for tweet in tweets:
                        items.append(
                            {
                                "id": tweet.id,
                                "text": tweet.full_text
                                if hasattr(tweet, "full_text")
                                else tweet.text,
                                "created_at": tweet.created_at.isoformat()
                                if tweet.created_at
                                else None,
                                "user": {
                                    "id": tweet.user.id,
                                    "name": tweet.user.name,
                                    "screen_name": tweet.user.screen_name,
                                },
                                "retweet_count": tweet.retweet_count,
                                "favorite_count": tweet.favorite_count,
                            }
                        )

                elif query_type == "user":
                    user = client.get_user(screen_name=query_text)
                    tweets = client.user_timeline(
                        screen_name=query_text, count=10, tweet_mode="extended"
                    )
                    for tweet in tweets:
                        items.append(
                            {
                                "id": tweet.id,
                                "text": tweet.full_text
                                if hasattr(tweet, "full_text")
                                else tweet.text,
                                "created_at": tweet.created_at.isoformat()
                                if tweet.created_at
                                else None,
                                "retweet_count": tweet.retweet_count,
                                "favorite_count": tweet.favorite_count,
                            }
                        )

            return {
                "items": items,
                "total_count": len(items),
                "platform": platform,
                "query_text": query_text,
                "query_type": query_type,
                "timestamp": datetime.utcnow().isoformat(),
                "engine": "tweepy",
            }
        except Exception as e:
            logger.error(f"Tweepy execution failed: {e}", exc_info=True)
            return {
                "items": [],
                "total_count": 0,
                "platform": platform,
                "query_text": query_text,
                "query_type": query_type,
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
            }

    def _check_alert_conditions(
        self,
        signals: list[OSINTSignal],
        conditions: dict[str, Any],
    ) -> bool:
        """
        Check if alert conditions are met.

        Args:
            signals: List of OSINT signals
            conditions: Alert conditions dictionary

        Returns:
            True if conditions are met
        """
        # Check signal count threshold
        min_count = conditions.get("min_signal_count", 0)
        if len(signals) >= min_count:
            return True

        # Check for keywords in signals
        keywords = conditions.get("keywords", [])
        if keywords:
            for signal in signals:
                text_lower = signal.text.lower()
                if any(keyword.lower() in text_lower for keyword in keywords):
                    return True

        # Check sentiment threshold
        sentiment_threshold = conditions.get("sentiment_threshold")
        if sentiment_threshold:
            for signal in signals:
                if signal.sentiment_score is not None:
                    if signal.sentiment_score <= sentiment_threshold:
                        return True

        return False


# Default OSINT service instance
default_osint_service = OSINTService()
