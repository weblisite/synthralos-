"""
OpenTelemetry Setup

Configures OpenTelemetry SDK for distributed tracing.
Exports traces to Signoz.
"""

import logging
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)

# OpenTelemetry imports (optional - will fail gracefully if not installed)
try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    logger.warning(
        "OpenTelemetry packages not installed. Observability features will be limited."
    )


def setup_opentelemetry(app: Any | None = None) -> None:
    """
    Set up OpenTelemetry instrumentation.

    Args:
        app: Optional FastAPI app instance to instrument
    """
    if not OPENTELEMETRY_AVAILABLE:
        logger.warning("OpenTelemetry not available. Skipping setup.")
        return

    if not settings.SIGNOZ_ENDPOINT:
        logger.warning(
            "Signoz endpoint not configured (SIGNOZ_ENDPOINT not set). Skipping OpenTelemetry setup."
        )
        logger.info(
            "To enable Signoz: Set SIGNOZ_ENDPOINT environment variable. See docs/OBSERVABILITY_SETUP.md"
        )
        return

    try:
        # Create resource with service name
        resource = Resource.create(
            {
                "service.name": "synthralos-backend",
                "service.version": "0.1.0",
            }
        )

        # Create tracer provider
        tracer_provider = TracerProvider(resource=resource)

        # Create OTLP exporter for Signoz
        otlp_exporter = OTLPSpanExporter(
            endpoint=settings.SIGNOZ_ENDPOINT,
            insecure=True,  # Set to False if using TLS
        )

        # Add span processor
        span_processor = BatchSpanProcessor(otlp_exporter)
        tracer_provider.add_span_processor(span_processor)

        # Set global tracer provider
        trace.set_tracer_provider(tracer_provider)

        # Instrument FastAPI if app provided
        if app:
            FastAPIInstrumentor.instrument_app(app)
            logger.info("✅ FastAPI instrumented with OpenTelemetry")

        # Instrument requests library
        RequestsInstrumentor().instrument()
        logger.info("✅ Requests library instrumented with OpenTelemetry")

        logger.info(
            f"✅ OpenTelemetry configured (Signoz endpoint: {settings.SIGNOZ_ENDPOINT})"
        )

    except Exception as e:
        logger.error(f"Failed to setup OpenTelemetry: {e}", exc_info=True)


def get_tracer(name: str) -> Any:
    """
    Get a tracer instance.

    Args:
        name: Tracer name (usually module name)

    Returns:
        Tracer instance or None if not available
    """
    if not OPENTELEMETRY_AVAILABLE:
        return None

    try:
        return trace.get_tracer(name)
    except Exception:
        return None
