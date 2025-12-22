import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.api.middleware.csrf import CSRFMiddleware
from app.api.middleware.guardrails import GuardrailsMiddleware
from app.core.config import settings
from app.observability.langfuse import default_langfuse_client
from app.observability.opentelemetry import setup_opentelemetry
from app.observability.posthog import default_posthog_client
from app.observability.wazuh import default_wazuh_client


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add CSRF protection middleware (after CORS, before guardrails)
# CSRF protection is enabled in production and staging
if settings.ENVIRONMENT in ["staging", "production"]:
    app.add_middleware(
        CSRFMiddleware,
        exempt_paths=[
            "/api/v1/chat/ws",  # WebSocket connections
            "/api/v1/agws",  # WebSocket connections
        ],
    )

# Add guardrails middleware for input validation and abuse detection
# Can be disabled in local environment for development
if settings.ENVIRONMENT != "local":
    app.add_middleware(
        GuardrailsMiddleware,
        enable_validation=True,
        enable_abuse_check=True,
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

# Setup OpenTelemetry instrumentation (can be memory-intensive)
# Only setup if not in low-memory environment
try:
    setup_opentelemetry(app)
    print("✅ OpenTelemetry instrumentation setup complete")
except Exception as e:
    print(f"⚠️  OpenTelemetry setup failed (non-critical): {e}")

# Initialize observability clients (they initialize themselves on import)
# PostHog, Langfuse, and Wazuh clients are already initialized as singletons
# Log initialization status (non-blocking)
try:
    if default_posthog_client.is_available:
        print("✅ PostHog initialized")
    else:
        print("⚠️  PostHog not configured (set POSTHOG_KEY)")
except Exception as e:
    print(f"⚠️  PostHog check failed: {e}")

try:
    if default_langfuse_client.is_available:
        print("✅ Langfuse initialized")
    else:
        print("⚠️  Langfuse not configured (set LANGFUSE_KEY)")
except Exception as e:
    print(f"⚠️  Langfuse check failed: {e}")

try:
    if default_wazuh_client.is_available:
        print("✅ Wazuh initialized")
    else:
        print("⚠️  Wazuh not configured (set WAZUH_URL)")
except Exception as e:
    print(f"⚠️  Wazuh check failed: {e}")

print("✅ FastAPI app initialization complete")
print("🚀 Server ready to accept connections")
