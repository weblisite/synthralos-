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

### Database Configuration (PostgreSQL)
```bash
POSTGRES_SERVER=db
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changethis  # Change this in production
POSTGRES_DB=app
```

### Supabase Configuration
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
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
# Signoz (OpenTelemetry)
SIGNOZ_ENDPOINT=  # e.g., http://localhost:4317

# PostHog (Product Analytics)
POSTHOG_KEY=

# Langfuse (LLM Observability)
LANGFUSE_KEY=

# Sentry (Error Tracking)
SENTRY_DSN=
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

### Initial User Configuration
```bash
FIRST_SUPERUSER=admin@synthralos.ai
FIRST_SUPERUSER_PASSWORD=changethis  # Change this in production
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

