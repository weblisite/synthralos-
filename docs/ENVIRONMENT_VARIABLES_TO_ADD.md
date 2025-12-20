# Environment Variables to Add to Render

This document lists all environment variables that should be **uncommented and configured** in `render.yaml` for full platform functionality.

## 🔴 CRITICAL - Required for Core Features

### OpenAI API Key (REQUIRED for Chat & Agents)
```yaml
- key: OPENAI_API_KEY
  sync: false  # REQUIRED: Set manually in Render dashboard
  # Get from: https://platform.openai.com/api-keys
  # Used by: Chat processor, Agent frameworks (AgentGPT, AutoGen, Archon, etc.)
```

**Why:** Your chat processor and agent frameworks require this to function. Without it, users will see errors when trying to use chat or agent features.

---

## 🟡 RECOMMENDED - For Production Observability

### Langfuse (LLM Observability) - Already Integrated ✅
```yaml
- key: LANGFUSE_KEY
  sync: false  # REQUIRED: Get from https://cloud.langfuse.com > Settings > API Keys
- key: LANGFUSE_SECRET_KEY
  sync: false  # Optional - defaults to LANGFUSE_KEY if not set
- key: LANGFUSE_HOST
  value: https://cloud.langfuse.com  # Optional - custom host for self-hosted
```

**Why:** We just integrated Langfuse tracing. Add these keys to start tracking LLM calls.

### PostHog (Product Analytics) - Already Integrated ✅
```yaml
- key: POSTHOG_KEY
  sync: false  # REQUIRED: Get from https://posthog.com > Project Settings > Project API Key
- key: POSTHOG_HOST
  value: https://app.posthog.com  # Optional - defaults to https://app.posthog.com
```

**Why:** We just integrated PostHog event tracking. Add these keys to start tracking user events.

### Wazuh (Security Monitoring) - Already Integrated ✅
```yaml
- key: WAZUH_URL
  sync: false  # e.g., http://wazuh:55000 or https://wazuh.example.com
- key: WAZUH_USER
  sync: false  # Optional - Wazuh API username
- key: WAZUH_PASSWORD
  sync: false  # Optional - Wazuh API password
```

**Why:** We just integrated Wazuh security logging. Add these keys to start logging security events.

---

## 🟢 OPTIONAL - Additional Features

### Sentry (Error Tracking)
```yaml
- key: SENTRY_DSN
  sync: false  # Error tracking - Get from https://sentry.io
```

**Why:** Track and debug production errors automatically.

### Redis (Caching)
```yaml
- key: REDIS_URL
  sync: false  # e.g., redis://redis:6379/0 or redis://your-redis-host:6379/0
```

**Why:** Enable caching for better performance. Platform works without it, but slower.

### Anthropic Claude API (Alternative LLM)
```yaml
- key: ANTHROPIC_API_KEY
  sync: false  # Get from: https://console.anthropic.com/settings/keys
```

**Why:** Alternative LLM provider for agent frameworks. Optional if you're using OpenAI.

### Signoz (Distributed Tracing)
```yaml
- key: SIGNOZ_ENDPOINT
  sync: false  # e.g., http://signoz:4317 or https://signoz.example.com:4317
```

**Why:** Distributed tracing for API requests. Already auto-instruments FastAPI.

### ChromaDB (Vector Database for RAG)
```yaml
- key: CHROMA_SERVER_HOST
  sync: false  # e.g., chromadb.example.com or localhost
- key: CHROMA_SERVER_HTTP_PORT
  value: "8000"  # ChromaDB HTTP port (default: 8000)
- key: CHROMA_SERVER_AUTH_TOKEN
  sync: false  # Optional - Auth token for ChromaDB Cloud
```

**Why:** Vector database for RAG (Retrieval Augmented Generation) features.

### Twitter/X API (OSINT Features)
```yaml
- key: TWITTER_API_KEY
  sync: false  # Get from https://developer.twitter.com > Your App > Keys and Tokens
- key: TWITTER_API_SECRET
  sync: false  # Get from https://developer.twitter.com > Your App > Keys and Tokens
- key: TWITTER_BEARER_TOKEN
  sync: false  # Get from https://developer.twitter.com > Your App > Keys and Tokens
```

**Why:** Enable OSINT (Open Source Intelligence) features for social media monitoring.

---

## 📋 Quick Checklist

### Must Add (Critical):
- [ ] `OPENAI_API_KEY` - Required for chat and agents

### Should Add (Recommended):
- [ ] `LANGFUSE_KEY` - LLM observability (already integrated)
- [ ] `LANGFUSE_SECRET_KEY` - LLM observability (already integrated)
- [ ] `POSTHOG_KEY` - Product analytics (already integrated)
- [ ] `WAZUH_URL` - Security monitoring (already integrated)

### Nice to Have (Optional):
- [ ] `SENTRY_DSN` - Error tracking
- [ ] `REDIS_URL` - Caching
- [ ] `ANTHROPIC_API_KEY` - Alternative LLM
- [ ] `SIGNOZ_ENDPOINT` - Distributed tracing
- [ ] `CHROMA_SERVER_HOST` - Vector database
- [ ] `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_BEARER_TOKEN` - OSINT

---

## 🚀 How to Add These

1. **Uncomment** the relevant sections in `render.yaml`
2. **Deploy** the updated blueprint (or manually add in Render dashboard)
3. **Set values** in Render dashboard > Your Service > Environment > Environment Variables
4. **Restart** the service to pick up new environment variables

---

## 📝 Notes

- All variables marked `sync: false` must be set manually in Render dashboard
- Never commit actual API keys to git
- Test each service after adding its keys
- Check service logs if integrations aren't working
