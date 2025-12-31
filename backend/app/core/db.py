import logging
import time
from datetime import datetime, timedelta

from sqlalchemy import event
from sqlalchemy.exc import OperationalError
from sqlalchemy.pool import Pool
from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models import User, UserCreate

logger = logging.getLogger(__name__)

# Circuit breaker state tracking
_circuit_breaker_open_until: datetime | None = None
_circuit_breaker_wait_time = 300  # Wait 5 minutes when circuit breaker is detected

# Create engine with optimized connection pool settings
# These settings minimize connection attempts to avoid triggering Supabase circuit breaker
# REDUCED pool size to minimize authentication attempts
engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    pool_pre_ping=True,  # Verify connections before using them (prevents stale connections)
    pool_recycle=1800,  # Recycle connections after 30 minutes (shorter than default to avoid timeouts)
    pool_size=5,  # REDUCED: Maintain only 5 connections in the pool (minimizes auth attempts)
    max_overflow=2,  # REDUCED: Allow only 2 additional connections beyond pool_size (total: 7)
    pool_timeout=30,  # REDUCED: Wait up to 30 seconds for a connection from the pool
    connect_args={
        "connect_timeout": 10,  # REDUCED: 10 second connection timeout (fail fast)
        "options": "-c statement_timeout=30000",  # 30 second statement timeout (in milliseconds)
        "keepalives": 1,  # Enable TCP keepalives
        "keepalives_idle": 30,  # Start keepalives after 30 seconds of inactivity
        "keepalives_interval": 10,  # Send keepalives every 10 seconds
        "keepalives_count": 5,  # Send up to 5 keepalives before considering connection dead
    },
    echo=False,  # Set to True for SQL query logging
)


# Add event listener to log connection pool events and detect circuit breaker
@event.listens_for(Pool, "connect")
def receive_connect(dbapi_conn, connection_record):
    global _circuit_breaker_open_until
    logger.debug("Database connection established")
    # Reset circuit breaker state on successful connection
    if _circuit_breaker_open_until:
        logger.info("Circuit breaker appears to be closed - connection successful")
        _circuit_breaker_open_until = None


@event.listens_for(Pool, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    global _circuit_breaker_open_until
    # Check if circuit breaker is still open
    if _circuit_breaker_open_until and datetime.now() < _circuit_breaker_open_until:
        remaining = (_circuit_breaker_open_until - datetime.now()).total_seconds()
        raise OperationalError(
            f"Circuit breaker is open. Wait {int(remaining)}s before retrying.",
            None,
            None,
        )
    logger.debug("Connection checked out from pool")


@event.listens_for(Pool, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    logger.debug("Connection returned to pool")


def _handle_circuit_breaker_error(error: Exception) -> None:
    """Handle circuit breaker errors by setting a wait period."""
    global _circuit_breaker_open_until
    error_str = str(error).lower()
    if "circuit breaker" in error_str:
        _circuit_breaker_open_until = datetime.now() + timedelta(
            seconds=_circuit_breaker_wait_time
        )
        logger.warning(
            f"Circuit breaker detected. Will wait {_circuit_breaker_wait_time}s before retrying. "
            f"Resets at {_circuit_breaker_open_until.strftime('%H:%M:%S')}"
        )


def check_db_connectivity() -> bool:
    """
    Check if database is accessible.
    Returns True if connection successful, False otherwise.

    Uses retry logic with exponential backoff to avoid triggering circuit breakers.
    Respects circuit breaker wait periods.
    """
    global _circuit_breaker_open_until

    # Check if circuit breaker is still open
    if _circuit_breaker_open_until and datetime.now() < _circuit_breaker_open_until:
        remaining = (_circuit_breaker_open_until - datetime.now()).total_seconds()
        logger.warning(
            f"Circuit breaker is still open. Wait {int(remaining)}s before retrying. "
            f"Resets at {_circuit_breaker_open_until.strftime('%H:%M:%S')}"
        )
        return False

    max_retries = 2  # REDUCED: Only 2 retries to minimize auth attempts
    base_delay = 5  # INCREASED: Start with 5 second delay

    for attempt in range(max_retries):
        try:
            with Session(engine) as session:
                session.exec(select(1))
            # Success - reset circuit breaker state
            if _circuit_breaker_open_until:
                logger.info(
                    "Database connection successful - circuit breaker appears closed"
                )
                _circuit_breaker_open_until = None
            return True
        except Exception as e:
            error_str = str(e)
            _handle_circuit_breaker_error(e)

            # If circuit breaker is open, don't retry immediately
            if "circuit breaker" in error_str.lower():
                if _circuit_breaker_open_until:
                    remaining = (
                        _circuit_breaker_open_until - datetime.now()
                    ).total_seconds()
                    logger.warning(
                        f"Circuit breaker detected. Will wait {int(remaining)}s before retrying. "
                        f"Resets at {_circuit_breaker_open_until.strftime('%H:%M:%S')}"
                    )
                return False

            # For other errors, use exponential backoff
            if attempt < max_retries - 1:
                delay = base_delay * (2**attempt)  # Exponential backoff: 5s, 10s
                logger.warning(
                    f"Database connectivity check failed (attempt {attempt + 1}/{max_retries}): {error_str}. "
                    f"Waiting {delay}s before retry..."
                )
                time.sleep(delay)
                continue

            logger.error(
                f"Database connectivity check failed after {max_retries} attempts: {error_str}"
            )
            # Only create system alert on final failure
            try:
                from app.services.system_alerts import handle_database_error

                # Use a new session to avoid nested transaction issues
                try:
                    with Session(engine) as alert_session:
                        handle_database_error(alert_session, e)
                except Exception:
                    # If we can't create alert due to DB issues, just log it
                    logger.warning(
                        "Could not create system alert due to database error"
                    )
            except Exception as alert_error:
                logger.warning(f"Failed to create system alert: {alert_error}")
            return False

    return False


def get_circuit_breaker_status() -> dict:
    """
    Get current circuit breaker status.

    Returns:
        dict with 'is_open', 'resets_at', 'remaining_seconds' keys
    """
    global _circuit_breaker_open_until

    if _circuit_breaker_open_until and datetime.now() < _circuit_breaker_open_until:
        remaining = int((_circuit_breaker_open_until - datetime.now()).total_seconds())
        return {
            "is_open": True,
            "resets_at": _circuit_breaker_open_until.isoformat(),
            "remaining_seconds": remaining,
            "message": f"Circuit breaker is open. Wait {remaining}s before retrying.",
        }

    return {
        "is_open": False,
        "resets_at": None,
        "remaining_seconds": 0,
        "message": "Circuit breaker is closed. Database connections are available.",
    }


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    # Only create first superuser if FIRST_SUPERUSER is configured
    # This is optional - admins can be created via promotion script or admin panel
    if settings.FIRST_SUPERUSER and settings.FIRST_SUPERUSER_PASSWORD:
        user = session.exec(
            select(User).where(User.email == settings.FIRST_SUPERUSER)
        ).first()
        if not user:
            user_in = UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True,
            )
            user = crud.create_user(session=session, user_create=user_in)
