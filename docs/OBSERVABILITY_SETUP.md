# Observability Services Setup Guide

**Date:** December 18, 2025

## Overview

SynthralOS supports multiple observability and monitoring services. This guide explains how to set up each service.

## Services

1. **Langfuse** - LLM observability and tracing
2. **PostHog** - Product analytics and feature flags
3. **Wazuh** - Security monitoring and audit logging
4. **Signoz** - Distributed tracing (OpenTelemetry)
5. **ChromaDB** - Vector database for RAG

## 1. Langfuse (LLM Observability)

### What It Does

- Tracks LLM calls (prompts, responses, tokens)
- Traces agent execution
- Monitors LLM costs
- Provides debugging tools for AI workflows

### Setup Steps

1. **Sign up for Langfuse:**
   - Go to https://cloud.langfuse.com (or self-host)
   - Create an account and project

2. **Get API Keys:**
   - Go to Settings → API Keys
   - Copy your **Public Key** (starts with `pk_`)

3. **Configure Environment Variables:**

**For Local Development (.env):**
```bash
LANGFUSE_KEY=pk_lf_xxxxxxxxxxxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk_lf_xxxxxxxxxxxxxxxxxxxxx  # Optional, defaults to LANGFUSE_KEY
LANGFUSE_HOST=https://cloud.langfuse.com  # Optional, defaults to cloud.langfuse.com
```

**For Render (Dashboard → Environment):**
- `LANGFUSE_KEY` = Your public key
- `LANGFUSE_SECRET_KEY` = Your secret key (optional)
- `LANGFUSE_HOST` = `https://cloud.langfuse.com` (or your self-hosted URL)

### Self-Hosting Langfuse

If you prefer to self-host:

```bash
# Docker Compose example
docker-compose -f langfuse-docker-compose.yml up -d
```

Then set:
```bash
LANGFUSE_HOST=http://localhost:3000
```

### Verification

After setting up, check logs:
```
✅ Langfuse client initialized
```

## 2. PostHog (Product Analytics)

### What It Does

- User behavior tracking
- Feature flags
- A/B testing
- Product analytics dashboard

### Setup Steps

1. **Sign up for PostHog:**
   - Go to https://posthog.com
   - Create an account and project

2. **Get API Key:**
   - Go to Project Settings → Project API Key
   - Copy your **Project API Key**

3. **Configure Environment Variables:**

**For Local Development (.env):**
```bash
POSTHOG_KEY=phc_xxxxxxxxxxxxxxxxxxxxx
```

**For Render (Dashboard → Environment):**
- `POSTHOG_KEY` = Your project API key

### Verification

After setting up, check logs:
```
✅ PostHog client initialized
```

## 3. Wazuh (Security Monitoring)

### What It Does

- Security event logging
- Audit trail
- Intrusion detection
- Compliance monitoring

### Setup Steps

1. **Install Wazuh (Self-Hosted):**

**Option A: Docker Compose**
```yaml
# docker-compose.wazuh.yml
version: '3'
services:
  wazuh-manager:
    image: wazuh/wazuh-manager:latest
    ports:
      - "55000:55000"
    environment:
      - WAZUH_API_USERNAME=wazuh
      - WAZUH_API_PASSWORD=wazuh
```

**Option B: Cloud Service**
- Use a managed Wazuh service
- Get API endpoint URL

2. **Configure Environment Variables:**

**For Local Development (.env):**
```bash
WAZUH_URL=http://localhost:55000
WAZUH_USER=wazuh  # Optional
WAZUH_PASSWORD=wazuh  # Optional
```

**For Render (Dashboard → Environment):**
- `WAZUH_URL` = Your Wazuh API endpoint
- `WAZUH_USER` = API username (if required)
- `WAZUH_PASSWORD` = API password (if required)

### Verification

After setting up, check logs:
```
✅ Wazuh client initialized (URL: http://localhost:55000)
```

## 4. Signoz (Distributed Tracing)

### What It Does

- Distributed tracing
- Performance monitoring
- Service dependency mapping
- Error tracking

### Setup Steps

1. **Install Signoz:**

**Option A: Docker Compose**
```yaml
# docker-compose.signoz.yml
version: '3'
services:
  signoz:
    image: signoz/signoz:latest
    ports:
      - "3301:3301"  # Query service
      - "4317:4317"  # OTLP gRPC receiver
      - "4318:4318"  # OTLP HTTP receiver
```

**Option B: Cloud Service**
- Use Signoz Cloud or self-hosted instance

2. **Configure Environment Variables:**

**For Local Development (.env):**
```bash
SIGNOZ_ENDPOINT=http://localhost:4317
```

**For Render (Dashboard → Environment):**
- `SIGNOZ_ENDPOINT` = Your Signoz OTLP endpoint (gRPC port, usually 4317)

### Verification

After setting up, check logs:
```
✅ OpenTelemetry configured (Signoz endpoint: http://localhost:4317)
✅ FastAPI instrumented with OpenTelemetry
```

## 5. ChromaDB (Vector Database for RAG)

### What It Does

- Vector storage for RAG documents
- Semantic search
- Document embeddings

### Setup Steps

1. **Install ChromaDB:**

**Option A: Docker Compose**
```yaml
# docker-compose.chromadb.yml
version: '3'
services:
  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8000:8000"
    environment:
      - IS_PERSISTENT=TRUE
      - PERSIST_DIRECTORY=/chroma/chroma
    volumes:
      - chroma_data:/chroma/chroma
```

**Option B: ChromaDB Cloud**
- Sign up at https://www.trychroma.com
- Get server host and auth token

2. **Configure Environment Variables:**

**For Local Development (.env):**
```bash
CHROMA_SERVER_HOST=localhost
CHROMA_SERVER_HTTP_PORT=8000
CHROMA_SERVER_AUTH_TOKEN=  # Optional, only if using ChromaDB Cloud
```

**For Render (Dashboard → Environment):**
- `CHROMA_SERVER_HOST` = ChromaDB server hostname
- `CHROMA_SERVER_HTTP_PORT` = Port (usually 8000)
- `CHROMA_SERVER_AUTH_TOKEN` = Auth token (if using ChromaDB Cloud)

### Verification

After setting up, check logs:
```
✅ ChromaDB client initialized (localhost:8000)
```

## Quick Setup Script

Create a `setup-observability.sh` script:

```bash
#!/bin/bash

echo "Setting up Observability Services..."

# Langfuse
read -p "Enter Langfuse Public Key (or press Enter to skip): " LANGFUSE_KEY
if [ ! -z "$LANGFUSE_KEY" ]; then
    echo "LANGFUSE_KEY=$LANGFUSE_KEY" >> .env
    echo "✅ Langfuse configured"
fi

# PostHog
read -p "Enter PostHog API Key (or press Enter to skip): " POSTHOG_KEY
if [ ! -z "$POSTHOG_KEY" ]; then
    echo "POSTHOG_KEY=$POSTHOG_KEY" >> .env
    echo "✅ PostHog configured"
fi

# Wazuh
read -p "Enter Wazuh URL (or press Enter to skip): " WAZUH_URL
if [ ! -z "$WAZUH_URL" ]; then
    echo "WAZUH_URL=$WAZUH_URL" >> .env
    echo "✅ Wazuh configured"
fi

# Signoz
read -p "Enter Signoz Endpoint (or press Enter to skip): " SIGNOZ_ENDPOINT
if [ ! -z "$SIGNOZ_ENDPOINT" ]; then
    echo "SIGNOZ_ENDPOINT=$SIGNOZ_ENDPOINT" >> .env
    echo "✅ Signoz configured"
fi

# ChromaDB
read -p "Enter ChromaDB Host (or press Enter to skip): " CHROMA_SERVER_HOST
if [ ! -z "$CHROMA_SERVER_HOST" ]; then
    echo "CHROMA_SERVER_HOST=$CHROMA_SERVER_HOST" >> .env
    echo "CHROMA_SERVER_HTTP_PORT=8000" >> .env
    echo "✅ ChromaDB configured"
fi

echo ""
echo "Setup complete! Restart your backend to apply changes."
```

## Render Deployment

### Environment Variables in Render

Add these to Render Dashboard → `synthralos-backend` → Environment:

```bash
# Langfuse
LANGFUSE_KEY=pk_lf_xxxxxxxxxxxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk_lf_xxxxxxxxxxxxxxxxxxxxx  # Optional
LANGFUSE_HOST=https://cloud.langfuse.com  # Optional

# PostHog
POSTHOG_KEY=phc_xxxxxxxxxxxxxxxxxxxxx

# Wazuh
WAZUH_URL=https://wazuh.example.com
WAZUH_USER=wazuh  # Optional
WAZUH_PASSWORD=password  # Optional

# Signoz
SIGNOZ_ENDPOINT=http://signoz:4317  # Or your Signoz instance URL

# ChromaDB
CHROMA_SERVER_HOST=chromadb.example.com
CHROMA_SERVER_HTTP_PORT=8000
CHROMA_SERVER_AUTH_TOKEN=token  # Optional
```

## Optional vs Required

### Required for Core Functionality

- **None** - All observability services are optional

### Recommended for Production

- **PostHog** - User analytics and feature flags
- **Signoz** - Performance monitoring and debugging

### Recommended for AI Features

- **Langfuse** - LLM observability (if using AI agents/chat)
- **ChromaDB** - Vector database (if using RAG)

### Recommended for Security

- **Wazuh** - Security monitoring and audit logging

## Troubleshooting

### Service Not Initializing

1. Check environment variables are set correctly
2. Verify service is running and accessible
3. Check network connectivity (firewall, VPN)
4. Review backend logs for specific error messages

### Connection Errors

- **Langfuse:** Verify API key is correct and has proper permissions
- **PostHog:** Check API key is valid and project exists
- **Wazuh:** Ensure Wazuh server is running and URL is correct
- **Signoz:** Verify OTLP endpoint is accessible (port 4317)
- **ChromaDB:** Check server is running and host/port are correct

### Performance Impact

All services are designed to be non-blocking:
- Failures are logged but don't crash the application
- Services can be disabled by not setting environment variables
- No performance impact if services are unavailable

## Related Documentation

- `docs/FRONTEND_BACKEND_INTERACTION.md` - How services communicate
- `docs/RENDER_DEPLOYMENT.md` - Render deployment guide
- `ENV_TEMPLATE.md` - Environment variable template

