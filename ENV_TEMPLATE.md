# Environment Variables Template

This document lists all environment variables required for SynthralOS. Copy these to your `.env` file and fill in the values.

## Quick Start

```bash
# Copy this template to .env
cp ENV_TEMPLATE.md .env
# Then edit .env with your actual values
```

## Required Environment Variables

### Project Configuration
```bash
PROJECT_NAME=SynthralOS
ENVIRONMENT=local  # Options: local, staging, production
DOMAIN=localhost
STACK_NAME=synthralos
```

### Docker Configuration
```bash
DOCKER_IMAGE_BACKEND=synthralos-backend
DOCKER_IMAGE_FRONTEND=synthralos-frontend
TAG=latest
```

### Frontend Configuration
```bash
FRONTEND_HOST=http://localhost:5173
BACKEND_CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Security & Authentication
```bash
SECRET_KEY=changethis  # Generate a secure random key for production
ACCESS_TOKEN_EXPIRE_MINUTES=11520  # 8 days
```

### Supabase Configuration (Database, Auth, Storage)
```bash
# Supabase Project URL (for Auth API)
SUPABASE_URL=https://your-project-ref.supabase.co
# Supabase Anon Key (for Auth API)
SUPABASE_ANON_KEY=your-supabase-anon-key

# Supabase Database Connection (choose one option)
# Option 1: Full connection string (recommended for production)
# Get from: Supabase Dashboard > Settings > Database > Connection string
# Use the "Connection pooling" option for serverless environments (port 6543)
SUPABASE_DB_URL=postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres

# Option 2: Database password only (will build connection from SUPABASE_URL)
# Get from: Supabase Dashboard > Settings > Database > Database password
# SUPABASE_DB_PASSWORD=your-database-password

# Legacy PostgreSQL Configuration (optional - only if not using Supabase)
# These are ignored if SUPABASE_DB_URL or SUPABASE_DB_PASSWORD is set
# POSTGRES_SERVER=db
# POSTGRES_PORT=5432
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=changethis
# POSTGRES_DB=app
```

### Redis Configuration
```bash
REDIS_URL=redis://redis:6379/0
```

### ChromaDB Configuration
```bash
CHROMA_SERVER_HOST=chromadb
CHROMA_SERVER_HTTP_PORT=8000
CHROMA_SERVER_AUTH_TOKEN=  # Optional: Leave empty for no auth
CHROMA_SERVER_AUTHN_PROVIDER=chromadb.auth.token_authn.TokenAuthenticationServerProvider
CHROMA_SERVER_AUTHN_CREDENTIALS=
CHROMA_SERVER_AUTHN_TOKEN_TRANSPORT_HEADER=X-Chroma-Token
```

### Workflow Engine Configuration
```bash
WORKFLOW_WORKER_CONCURRENCY=10
WORKFLOW_MAX_RETRIES=3
WORKFLOW_RETRY_BACKOFF_MULTIPLIER=2.0
WORKFLOW_HISTORY_RETENTION_DAYS=30
WORKFLOW_NODE_TIMEOUT_SECONDS=300
```

### Cache Configuration
```bash
CACHE_TTL_DEFAULT=300  # 5 minutes
CACHE_ENABLED=true
```

### Infisical Configuration (Secrets Management)
```bash
INFISICAL_URL=https://app.infisical.com
INFISICAL_CLIENT_ID=
INFISICAL_CLIENT_SECRET=
```

### Nango Configuration (OAuth Integration)
```bash
NANGO_URL=https://api.nango.dev
NANGO_SECRET_KEY=  # Your Nango API secret key
NANGO_ENABLED=true  # Enable/disable Nango integration
```

### Observability & Monitoring
```bash
# Signoz (OpenTelemetry - Distributed Tracing)
# Get from: Signoz dashboard or self-hosted instance
SIGNOZ_ENDPOINT=  # e.g., http://localhost:4317 (OTLP gRPC endpoint)

# PostHog (Product Analytics & Feature Flags)
# Get from: https://posthog.com > Project Settings > Project API Key
POSTHOG_KEY=  # e.g., phc_xxxxxxxxxxxxxxxxxxxxx

# Langfuse (LLM Observability & Tracing)
# Get from: https://cloud.langfuse.com > Settings > API Keys
LANGFUSE_KEY=  # Public key (starts with pk_lf_)
LANGFUSE_SECRET_KEY=  # Secret key (optional, defaults to LANGFUSE_KEY)
LANGFUSE_HOST=https://cloud.langfuse.com  # Optional, defaults to cloud.langfuse.com

# Wazuh (Security Monitoring & Audit Logging)
# Get from: Self-hosted Wazuh instance or managed service
WAZUH_URL=  # e.g., http://localhost:55000
WAZUH_USER=  # Optional: Wazuh API username
WAZUH_PASSWORD=  # Optional: Wazuh API password

# ChromaDB (Vector Database for RAG)
# Get from: Self-hosted ChromaDB or ChromaDB Cloud
CHROMA_SERVER_HOST=localhost  # ChromaDB server hostname
CHROMA_SERVER_HTTP_PORT=8000  # ChromaDB HTTP port (usually 8000)
CHROMA_SERVER_AUTH_TOKEN=  # Optional: Auth token for ChromaDB Cloud

# Sentry (Error Tracking)
# Get from: https://sentry.io > Project Settings > DSN
SENTRY_DSN=  # e.g., https://xxx@xxx.ingest.sentry.io/xxx
```

### Email Configuration (SMTP)
```bash
SMTP_TLS=true
SMTP_SSL=false
SMTP_PORT=587
SMTP_HOST=
SMTP_USER=
SMTP_PASSWORD=
EMAILS_FROM_EMAIL=
EMAILS_FROM_NAME=SynthralOS
EMAIL_RESET_TOKEN_EXPIRE_HOURS=48
```

### Initial User Configuration (Optional)
```bash
# Optional: Create first superuser on database initialization
# If not set, you can create admins via the promotion script or admin panel
# FIRST_SUPERUSER=admin@synthralos.ai
# FIRST_SUPERUSER_PASSWORD=changethis  # Change this in production
```

### WebSocket Configuration
```bash
VITE_WS_URL=ws://localhost:8000
```

## Optional: LLM Provider API Keys

These are used by agent frameworks and RAG services:

```bash
# OPENAI_API_KEY=
# ANTHROPIC_API_KEY=
# GOOGLE_API_KEY=
# COHERE_API_KEY=
```

## Notes

- **Security**: Never commit your `.env` file to version control. It contains sensitive credentials.
- **Production**: Change all `changethis` values and generate secure random keys before deploying.
- **Docker**: When running in Docker Compose, most variables are automatically set from the `.env` file.
- **Frontend**: Frontend-specific variables (like `VITE_WS_URL`) should be prefixed with `VITE_` for Vite to expose them.

