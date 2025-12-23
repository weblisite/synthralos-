#!/usr/bin/env python3
"""
Workflow Worker Startup Script

Starts the workflow worker that processes workflow executions.
Run this script in a separate process/terminal from the main API server.

Usage:
    python -m scripts.start_worker
    # or
    python backend/scripts/start_worker.py
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.workflows.worker import WorkflowWorker  # noqa: E402


def main() -> None:
    """Start the workflow worker."""
    print("=" * 60)  # noqa: T201
    print("🚀 Starting Workflow Worker")  # noqa: T201
    print("=" * 60)  # noqa: T201
    print()  # noqa: T201
    print("The worker will:")  # noqa: T201
    print("  • Poll database every 1 second for workflow executions")  # noqa: T201
    print("  • Process running executions")  # noqa: T201
    print("  • Handle retries, signals, and scheduled executions")  # noqa: T201
    print("  • Execute workflow nodes via activity handlers")  # noqa: T201
    print()  # noqa: T201
    print("Press Ctrl+C to stop the worker")  # noqa: T201
    print("=" * 60)  # noqa: T201
    print()  # noqa: T201

    try:
        # Create and start worker
        worker = WorkflowWorker(poll_interval=1.0)
        worker.start()
    except KeyboardInterrupt:
        print("\n\n✅ Worker stopped by user")  # noqa: T201
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Worker failed to start: {e}")  # noqa: T201
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
