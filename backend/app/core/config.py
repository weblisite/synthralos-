import secrets
import warnings
from typing import Annotated, Any, Literal
from urllib.parse import urlparse

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use .env file in backend directory and root directory
        env_file=[".env", "../.env"],
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    FRONTEND_HOST: str = "http://localhost:5173"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        """
        Get all allowed CORS origins.

        Includes:
        - BACKEND_CORS_ORIGINS from environment
        - FRONTEND_HOST from environment
        - Production frontend URLs (if in production/staging)
        """
        origins = [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS]

        # Add FRONTEND_HOST if set
        if self.FRONTEND_HOST:
            origins.append(str(self.FRONTEND_HOST).rstrip("/"))

        # Add production frontend URLs for production/staging environments
        if self.ENVIRONMENT in ["staging", "production"]:
            production_origins = [
                "https://app.synthralos.ai",
                "https://synthralos-frontend.onrender.com",
                "https://www.synthralos.ai",
            ]
            for origin in production_origins:
                if origin not in origins:
                    origins.append(origin)

        return origins

    PROJECT_NAME: str
    SENTRY_DSN: HttpUrl | None = None
    # Legacy PostgreSQL Configuration (optional - for backward compatibility)
    # If SUPABASE_DB_URL is set, these will be ignored
    POSTGRES_SERVER: str = ""
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""
    # Clerk Configuration (Authentication)
    CLERK_SECRET_KEY: str = ""
    CLERK_PUBLISHABLE_KEY: str = ""
    CLERK_WEBHOOK_SECRET: str = ""
    CLERK_JWKS_URL: str = ""  # JWKS endpoint for token verification
    # Supabase Configuration (Database & Storage only)
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    # Supabase Database Configuration (preferred)
    # Option 1: Full connection string (recommended)
    # Format examples:
    # - Direct: postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
    # - Session pooler: postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-1-[REGION].pooler.supabase.com:5432/postgres
    # - Transaction pooler: postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
    # For non-serverless platforms with persistent connections, use direct connection (port 5432)
    SUPABASE_DB_URL: str = ""
    # Option 2: Database password (will build connection from SUPABASE_URL)
    # If SUPABASE_DB_URL is not set, will use this to construct connection string
    SUPABASE_DB_PASSWORD: str = ""

    # Workflow Engine Configuration
    WORKFLOW_WORKER_CONCURRENCY: int = 10
    WORKFLOW_MAX_RETRIES: int = 3
    WORKFLOW_RETRY_BACKOFF_MULTIPLIER: float = 2.0
    WORKFLOW_HISTORY_RETENTION_DAYS: int = 30
    WORKFLOW_NODE_TIMEOUT_SECONDS: int = 300  # 5 minutes default timeout per node

    # Infisical Configuration
    INFISICAL_URL: str = "https://app.infisical.com"
    INFISICAL_CLIENT_ID: str = ""
    INFISICAL_CLIENT_SECRET: str = ""

    # Observability Configuration
    # Note: All observability services are optional and fail gracefully if not configured
    # See docs/OBSERVABILITY_SETUP.md for setup instructions

    # Signoz (OpenTelemetry - Distributed Tracing)
    SIGNOZ_ENDPOINT: str = ""  # e.g., "http://localhost:4317" or "http://signoz:4317"

    # PostHog (Product Analytics & Feature Flags)
    POSTHOG_KEY: str = (
        ""  # Get from: https://posthog.com > Project Settings > Project API Key
    )

    # Langfuse (LLM Observability & Tracing)
    LANGFUSE_KEY: str = (
        ""  # Public key - Get from: https://cloud.langfuse.com > Settings > API Keys
    )
    LANGFUSE_SECRET_KEY: str = (
        ""  # Secret key (optional, defaults to LANGFUSE_KEY if not set)
    )
    LANGFUSE_HOST: str = (
        "https://cloud.langfuse.com"  # Optional custom host for self-hosted Langfuse
    )

    # Cache Configuration
    REDIS_URL: str = ""  # e.g., "redis://localhost:6379/0"
    CACHE_TTL_DEFAULT: int = 300  # Default cache TTL in seconds (5 minutes)
    CACHE_ENABLED: bool = True  # Enable/disable caching

    # ChromaDB Configuration (Vector Database for RAG)
    CHROMA_SERVER_HOST: str = ""  # ChromaDB server host (empty = disabled)
    CHROMA_SERVER_HTTP_PORT: int = 8000  # ChromaDB HTTP port
    CHROMA_SERVER_AUTH_TOKEN: str = (
        ""  # Optional ChromaDB auth token (for ChromaDB Cloud)
    )

    # Wazuh Configuration (Security Monitoring & Audit Logging)
    WAZUH_URL: str = ""  # e.g., "http://localhost:55000" or "http://wazuh:55000"
    WAZUH_USER: str = ""  # Optional Wazuh API user
    WAZUH_PASSWORD: str = ""  # Optional Wazuh API password

    # Nango Configuration
    NANGO_BASE_URL: str = "https://api.nango.dev"  # Nango API base URL
    NANGO_SECRET_KEY: str = ""  # Nango secret key (from Nango dashboard)
    NANGO_PUBLIC_KEY: str = ""  # Nango public key (optional, for frontend)
    NANGO_ENABLED: bool = True  # Enable/disable Nango integration

    # LLM Provider Configuration
    OPENAI_API_KEY: str = ""  # OpenAI API key for chat and agents
    ANTHROPIC_API_KEY: str = ""  # Anthropic Claude API key
    GOOGLE_API_KEY: str = ""  # Google Gemini API key
    COHERE_API_KEY: str = ""  # Cohere API key

    # OCR Engine Configuration
    GOOGLE_VISION_API_KEY: str = ""  # Google Cloud Vision API key for OCR
    TESSERACT_CMD: str = (
        "tesseract"  # Path to Tesseract executable (default: system PATH)
    )

    # Browser Automation Configuration
    PLAYWRIGHT_BROWSER_PATH: str = ""  # Optional: Custom Playwright browser path
    PUPPETEER_EXECUTABLE_PATH: str = ""  # Optional: Custom Puppeteer executable path

    # OSINT Configuration
    TWITTER_BEARER_TOKEN: str = ""  # Twitter API Bearer Token for Tweepy
    TWITTER_API_KEY: str = ""  # Twitter API Key
    TWITTER_API_SECRET: str = ""  # Twitter API Secret
    TWITTER_ACCESS_TOKEN: str = ""  # Twitter Access Token
    TWITTER_ACCESS_TOKEN_SECRET: str = ""  # Twitter Access Token Secret

    # Code Execution Configuration
    E2B_API_KEY: str = ""  # E2B API key for sandboxed code execution
    CODE_EXECUTION_TIMEOUT: int = 30  # Default timeout in seconds for code execution

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        """
        Build database URI from Supabase or legacy PostgreSQL config.

        Priority:
        1. SUPABASE_DB_URL (full connection string) - preferred
        2. Build from SUPABASE_URL + SUPABASE_DB_PASSWORD - if Supabase configured
        3. Legacy POSTGRES_* variables - for backward compatibility
        """
        # Option 1: Use Supabase full connection string if provided
        if self.SUPABASE_DB_URL:
            # Use the connection string as-is - no automatic conversion
            # Supports both direct connections (port 5432) and pooler connections (port 5432/6543)
            # Users should set the connection string format they need:
            # - Direct: postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
            # - Session pooler: postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-1-[REGION].pooler.supabase.com:5432/postgres
            # - Transaction pooler: postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
            db_url = str(self.SUPABASE_DB_URL)

            # Convert postgresql:// to postgresql+psycopg:// if not already converted (required for psycopg3)
            if db_url.startswith("postgresql://") and not db_url.startswith(
                "postgresql+psycopg://"
            ):
                db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

            # CRITICAL: Properly URL-encode the password to handle special characters
            # Passwords with special characters like [ ] need to be URL-encoded
            import re
            from urllib.parse import quote, unquote

            # Extract and re-encode the password part
            # Format: postgresql://user:password@host:port/db
            password_match = re.search(r"://([^:]+):([^@]+)@", db_url)
            if password_match:
                password_raw = password_match.group(2)
                # Decode first (in case it's already encoded), then re-encode properly
                password_decoded = unquote(password_raw)
                password_encoded = quote(password_decoded, safe="")
                # Replace the password in the URL
                db_url = db_url.replace(f":{password_raw}@", f":{password_encoded}@")

            try:
                return PostgresDsn(db_url)
            except Exception as e:
                warnings.warn(
                    f"Failed to parse SUPABASE_DB_URL: {e}. Using as-is.", stacklevel=2
                )
                return PostgresDsn(db_url)

        # Option 2: Build from Supabase URL and password
        if self.SUPABASE_URL and self.SUPABASE_DB_PASSWORD:
            # Extract project reference from SUPABASE_URL
            # Format: https://[PROJECT_REF].supabase.co
            try:
                parsed = urlparse(self.SUPABASE_URL)
                project_ref = parsed.netloc.split(".")[0] if parsed.netloc else ""

                if project_ref:
                    # Build direct connection string
                    # Users can use SUPABASE_DB_URL to set any connection type (direct, session pooler, or transaction pooler)
                    host = f"db.{project_ref}.supabase.co"
                    return PostgresDsn.build(
                        scheme="postgresql+psycopg",
                        username="postgres",
                        password=self.SUPABASE_DB_PASSWORD,
                        host=host,
                        port=5432,
                        path="postgres",
                    )
            except Exception as e:
                warnings.warn(
                    f"Failed to build Supabase connection string: {e}. Falling back to legacy config.",
                    stacklevel=2,
                )

        # Option 3: Legacy PostgreSQL configuration (backward compatibility)
        if not self.POSTGRES_SERVER:
            raise ValueError(
                "Database configuration required. Set either SUPABASE_DB_URL, "
                "or SUPABASE_URL + SUPABASE_DB_PASSWORD, or legacy POSTGRES_* variables."
            )

        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: str | None = None

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            # Default to "SynthralOS AI" for better branding
            self.EMAILS_FROM_NAME = "SynthralOS AI"
        return self

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    # Resend Configuration
    RESEND_API_KEY: str | None = None
    USE_RESEND: bool = False  # Set to True to use Resend instead of SMTP

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        if self.USE_RESEND:
            return bool(self.RESEND_API_KEY and self.EMAILS_FROM_EMAIL)
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    EMAIL_TEST_USER: EmailStr = "test@synthralos.ai"
    FIRST_SUPERUSER: EmailStr | None = None
    FIRST_SUPERUSER_PASSWORD: str = ""

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        # Only check POSTGRES_PASSWORD if using legacy config
        if self.POSTGRES_SERVER and not self.SUPABASE_DB_URL:
            self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        # Check SUPABASE_DB_PASSWORD if using Supabase but not full URL
        if self.SUPABASE_URL and self.SUPABASE_DB_PASSWORD and not self.SUPABASE_DB_URL:
            self._check_default_secret(
                "SUPABASE_DB_PASSWORD", self.SUPABASE_DB_PASSWORD
            )
        # Only check FIRST_SUPERUSER_PASSWORD if FIRST_SUPERUSER is set
        if self.FIRST_SUPERUSER:
            self._check_default_secret(
                "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
            )

        return self


settings = Settings()  # type: ignore
