#!/usr/bin/env python3
"""
Wait for circuit breaker to reset and then run migrations.

This script:
1. Checks circuit breaker status periodically
2. Waits for it to close
3. Tests database connection
4. Runs Alembic migrations once connection is successful
"""

import subprocess
import sys
import time
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import logging

from app.core.db import check_db_connectivity, get_circuit_breaker_status

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_connection() -> bool:
    """Check if database connection is successful."""
    try:
        return check_db_connectivity()
    except Exception as e:
        logger.debug(f"Connection check failed: {e}")
        return False


def run_migration() -> bool:
    """Run Alembic migrations."""
    try:
        logger.info("Running Alembic migrations...")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=backend_dir,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        if result.returncode == 0:
            logger.info("✅ Migrations completed successfully!")
            if result.stdout:
                logger.info(f"Migration output:\n{result.stdout}")
            return True
        else:
            logger.error(f"❌ Migration failed with exit code {result.returncode}")
            if result.stderr:
                logger.error(f"Error output:\n{result.stderr}")
            if result.stdout:
                logger.error(f"Standard output:\n{result.stdout}")
            return False
    except subprocess.TimeoutExpired:
        logger.error("❌ Migration timed out after 5 minutes")
        return False
    except Exception as e:
        logger.error(f"❌ Error running migration: {e}")
        return False


def main():
    """Main function to wait for circuit breaker and run migration."""
    logger.info("=" * 60)
    logger.info("Circuit Breaker Monitor & Migration Runner")
    logger.info("=" * 60)
    logger.info("")

    max_wait_time = 900  # 15 minutes maximum wait
    check_interval = 30  # Check every 30 seconds
    start_time = time.time()

    logger.info(
        f"Waiting for circuit breaker to reset (max {max_wait_time // 60} minutes)..."
    )
    logger.info(f"Checking every {check_interval} seconds...")
    logger.info("")

    while True:
        elapsed = time.time() - start_time

        # Check circuit breaker status
        cb_status = get_circuit_breaker_status()

        if cb_status["is_open"]:
            remaining_cb = cb_status["remaining_seconds"]
            logger.info(
                f"[{int(elapsed)}s] Circuit breaker is OPEN. "
                f"Wait {remaining_cb}s before retrying. "
                f"Resets at: {cb_status.get('resets_at', 'N/A')}"
            )
        else:
            logger.info(
                f"[{int(elapsed)}s] Circuit breaker appears CLOSED. Testing connection..."
            )

            # Test connection
            if check_connection():
                logger.info("✅ Database connection successful!")
                logger.info("")

                # Run migration
                if run_migration():
                    logger.info("")
                    logger.info("=" * 60)
                    logger.info("✅ All done! Migration completed successfully.")
                    logger.info("=" * 60)
                    return True
                else:
                    logger.error("Migration failed. Please check the errors above.")
                    return False
            else:
                logger.warning(
                    "⚠️  Connection test failed. Circuit breaker may still be open."
                )
                logger.info("Continuing to wait...")

        # Check if we've exceeded max wait time
        if elapsed >= max_wait_time:
            logger.error("")
            logger.error("=" * 60)
            logger.error("❌ Timeout: Circuit breaker did not reset within 15 minutes")
            logger.error("=" * 60)
            logger.error("")
            logger.error("Possible issues:")
            logger.error("  1. Database password may still be incorrect")
            logger.error("  2. Database server may be down")
            logger.error("  3. Network connectivity issues")
            logger.error("")
            logger.error("Please verify:")
            logger.error("  - SUPABASE_DB_URL in .env file")
            logger.error("  - Database password is correct")
            logger.error("  - Database server is accessible")
            return False

        # Wait before next check
        time.sleep(check_interval)


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("")
        logger.info("Interrupted by user. Exiting...")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
