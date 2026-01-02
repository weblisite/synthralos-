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
    # Format: postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
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
            # Parse the connection string and convert to PostgresDsn
            # Supabase connection strings are typically:
            # postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres (pooler - recommended)
            # or: postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres (direct)
            # We need to ensure it uses postgresql+psycopg:// for psycopg3
            # IMPORTANT: For Render/serverless, prefer the pooler connection (port 6543) over direct (port 5432)
            # The pooler avoids IPv6 resolution issues and is optimized for serverless environments
            db_url = str(self.SUPABASE_DB_URL)

            # Convert postgresql:// to postgresql+psycopg:// if not already converted
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
                username = password_match.group(1)
                password_raw = password_match.group(2)
                # Decode first (in case it's already encoded), then re-encode properly
                password_decoded = unquote(password_raw)
                password_encoded = quote(password_decoded, safe="")
                # Replace the password in the URL
                db_url = db_url.replace(f":{password_raw}@", f":{password_encoded}@")

            # CIRCUIT BREAKER MITIGATION: Only convert DIRECT connections to pooler
            # Supabase has two pooler types:
            # 1. Session pooler: port 5432, IPv4 proxied (aws-1-us-west-1.pooler.supabase.com:5432)
            # 2. Transaction pooler: port 6543 (aws-0-us-west-1.pooler.supabase.com:6543)
            # Both pooler types work fine - we only need to convert DIRECT connections (db.*.supabase.co:5432)
            
            # Check if this is already a pooler connection (session or transaction)
            is_pooler = ".pooler.supabase.com" in db_url
            is_direct = "db." in db_url and ".supabase.co" in db_url
            
            # If using direct connection (port 5432 with db.*.supabase.co hostname), convert to pooler
            # This helps avoid IPv6 resolution issues on Render and circuit breaker problems
            if self.SUPABASE_URL and is_direct and ":5432/" in db_url:
                try:
                    parsed = urlparse(self.SUPABASE_URL)
                    # Extract project_ref from SUPABASE_URL
                    # Format: https://[PROJECT_REF].supabase.co
                    # Example: https://lorefpaifkembnzmlodm.supabase.co -> project_ref = "lorefpaifkembnzmlodm"
                    project_ref = parsed.netloc.split(".")[0] if parsed.netloc else ""
                    if not project_ref:
                        # Fallback: try to extract from hostname if netloc parsing fails
                        hostname = parsed.hostname or ""
                        if hostname:
                            project_ref = hostname.split(".")[0]
                    
                    if project_ref:
                        import re
                        from urllib.parse import urlparse as parse_url

                        # Parse the connection string properly using urlparse
                        # Note: urlparse handles PostgreSQL connection strings correctly
                        db_parsed = parse_url(db_url)

                        # Extract region from the direct connection hostname
                        # Format options:
                        # 1. aws-0-[REGION].compute.amazonaws.com:5432
                        # 2. aws-1-[REGION].pooler.supabase.com:5432 (wrong port)
                        # 3. db.[PROJECT_REF].supabase.co:5432 (need to infer region)
                        # 4. IP address (54.241.103.102) - need to infer region
                        hostname = db_parsed.hostname or ""
                        region_match = re.search(r"aws-[01]-([^.]+)\.", hostname)
                        if region_match:
                            region = region_match.group(1)
                        else:
                            # If using db.[PROJECT_REF].supabase.co format or IP address, infer region
                            # Most Supabase projects default to us-west-1
                            # Check if it's an IP address
                            ip_match = re.match(r"^\d+\.\d+\.\d+\.\d+$", hostname)
                            if ip_match:
                                # IP address detected - default to us-west-1 (most common)
                                region = "us-west-1"
                            else:
                                # Default to us-west-1
                                region = "us-west-1"

                        # Extract username - always construct as "postgres.[PROJECT_REF]" for pooler connections
                        # The project_ref from SUPABASE_URL is the source of truth
                        raw_username = db_parsed.username or "postgres"
                        
                        # Extract base username (should be "postgres")
                        # Handle cases where username might already be "postgres.[something]"
                        if raw_username.startswith("postgres."):
                            # If it's already "postgres.[something]", extract just "postgres"
                            # Split on first dot to get base username
                            base_username = raw_username.split(".", 1)[0]
                        else:
                            # Use as-is (should be "postgres")
                            base_username = raw_username
                        
                        # Always construct username as "postgres.[PROJECT_REF]" using project_ref from SUPABASE_URL
                        # This ensures consistency and correctness
                        # Format must be exactly: postgres.[PROJECT_REF] (e.g., postgres.lorefpaifkembnzmlodm)
                        username = f"{base_username}.{project_ref}"
                        
                        # Validate username format
                        if not username.startswith("postgres.") or username.count(".") != 1:
                            raise ValueError(
                                f"Invalid username format constructed: {username}. "
                                f"Expected format: postgres.[PROJECT_REF], project_ref={project_ref}"
                            )

                        # Extract password (should already be URL-encoded in connection string)
                        password = db_parsed.password or ""
                        # Password should already be URL-encoded, keep as-is

                        # Extract database name (usually "postgres")
                        database = (db_parsed.path or "/postgres").lstrip("/").split(
                            "?"
                        )[0] or "postgres"

                        # Build pooler connection string manually to ensure correct format
                        # Format: postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
                        # Username can contain dots (like postgres.lorefpaifkembnzmlodm), don't URL-encode it
                        if password:
                            # Build netloc: username:password@hostname:port
                            netloc = f"{username}:{password}@aws-0-{region}.pooler.supabase.com:6543"
                        else:
                            netloc = (
                                f"{username}@aws-0-{region}.pooler.supabase.com:6543"
                            )

                        # Construct the full URL
                        db_url = (
                            f"{db_parsed.scheme or 'postgresql'}://{netloc}/{database}"
                        )

                        # Validate the constructed URL by parsing it back
                        # This ensures the format is correct
                        test_parsed = parse_url(db_url)
                        if not test_parsed.hostname or test_parsed.hostname == username:
                            # If hostname is wrong, fall back to manual construction
                            raise ValueError(
                                f"Invalid connection string format after conversion: hostname={test_parsed.hostname}"
                            )

                        warnings.warn(
                            "Automatically converted direct connection (port 5432) to pooler connection "
                            "(port 6543) for better serverless compatibility. This helps avoid connection "
                            "issues and circuit breaker problems.",
                            stacklevel=2,
                        )
                except Exception as e:
                    # If conversion fails, warn but continue with original connection string
                    warnings.warn(
                        f"Failed to convert direct connection to pooler: {e}. "
                        f"Consider manually setting SUPABASE_DB_URL to use pooler connection (port 6543).",
                        stacklevel=2,
                    )

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
                    # Use Supabase connection pooler (recommended for serverless/Render)
                    # Port 6543 is the pooler (better for serverless, avoids IPv6 issues)
                    # Port 5432 is direct connection (may resolve to IPv6 which Render can't reach)
                    #
                    # NOTE: The pooler connection string format requires the exact hostname from Supabase dashboard:
                    # Format: postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
                    #
                    # For now, we'll use direct connection but warn the user
                    # Users should get the pooler connection string from Supabase dashboard for production
                    host = f"db.{project_ref}.supabase.co"
                    warnings.warn(
                        "Using direct Supabase connection (port 5432). For Render/serverless deployments, "
                        "use the connection pooler (port 6543) from Supabase dashboard to avoid IPv6 issues. "
                        "Get it from: Settings > Database > Connection string > Connection pooling",
                        stacklevel=2,
                    )
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
