# Deployment Warnings Guide

**Date:** December 18, 2025

## Overview

This document explains the warnings you may see in deployment logs and whether they need to be addressed.

## Backend Warnings

### ✅ Non-Critical Warnings (Can Be Ignored)

#### 1. Agent Framework Warnings

```
AgentGPT requires OPENAI_API_KEY to be configured
AutoGPT requires OPENAI_API_KEY to be configured
MetaGPT requires OPENAI_API_KEY to be configured
...
```

**What it means:** Agent frameworks are optional features that require OpenAI API keys.

**Impact:** Agent features won't work until API keys are configured.

**Action:**
- **Optional:** Add `OPENAI_API_KEY` environment variable if you want to use agent frameworks
- **Can ignore:** If you don't need agent features

#### 2. EasyOCR Warning

```
INFO:app.ocr.service:easyocr not installed. Install with: pip install easyocr
```

**What it means:** EasyOCR is an optional OCR engine for handwriting detection.

**Impact:** OCR will use other available engines (Tesseract, Google Vision, etc.).

**Action:**
- **Optional:** Add `easyocr` to `pyproject.toml` if you need handwriting OCR
- **Can ignore:** Other OCR engines are available

#### 3. ChromaDB Warning

```
WARNING:app.rag.service:Failed to initialize ChromaDB client: Could not connect to a Chroma server. Are you sure it is running?. Using placeholder.
```

**What it means:** ChromaDB vector database is not configured.

**Impact:** RAG (Retrieval-Augmented Generation) features may be limited.

**Action:**
- **Optional:** Set up ChromaDB if you need vector search for RAG
- **Can ignore:** RAG can use other vector databases (Supabase pgvector, etc.)

#### 4. Observability Warnings

```
WARNING:app.observability.langfuse:Langfuse not configured. LLM observability will be disabled.
WARNING:app.observability.posthog:PostHog not configured. Analytics will be disabled.
WARNING:app.observability.wazuh:Wazuh not configured. Security monitoring will be disabled.
WARNING:app.observability.opentelemetry:Signoz endpoint not configured. Skipping OpenTelemetry setup.
```

**What it means:** Optional observability services are not configured.

**Impact:**
- No LLM observability (Langfuse)
- No user analytics (PostHog)
- No security monitoring (Wazuh)
- No distributed tracing (Signoz)

**Action:**
- **Optional:** Configure these services if you need observability features
- **Can ignore:** Core functionality works without them

### ⚠️ Issues to Address

#### 1. Health Check 307 Redirects

```
INFO: 10.219.18.72:43786 - "GET /api/v1/utils/health-check HTTP/1.1" 307 Temporary Redirect
```

**What it means:** Health check endpoint has a trailing slash issue.

**Impact:** Render health checks may fail or be slower.

**Status:** ✅ **FIXED** - Removed trailing slash from endpoint

#### 2. Double `/api/v1` in API Calls

```
INFO: 10.20.199.224:41902 - "GET /api/v1/api/v1/users/me HTTP/1.1" 404 Not Found
```

**What it means:** Frontend is calling `/api/v1/api/v1/...` (double prefix).

**Impact:** API calls fail with 404 errors.

**Solution:** Ensure `VITE_API_URL` is set to base URL only (without `/api/v1`):
```bash
# ✅ Correct
VITE_API_URL=https://synthralos-backend.onrender.com

# ❌ Wrong
VITE_API_URL=https://synthralos-backend.onrender.com/api/v1
```

**Status:** ⚠️ **NEEDS FIX** - Update `VITE_API_URL` in Render dashboard

## Frontend Warnings

### ✅ Normal Messages (Not Warnings)

```
==> Setting WEB_CONCURRENCY=1 by default, based on available CPUs in the instance
```

**What it means:** Render automatically sets worker concurrency.

**Action:** None needed - this is informational.

## Summary

### Must Fix

1. **Double `/api/v1` in API calls** - Update `VITE_API_URL` environment variable

### Already Fixed

1. ✅ Health check 307 redirects - Fixed in code
2. ✅ Tesseract OCR warning - Added to Dockerfile
3. ✅ FastAPI dependency injection errors - Fixed

### Can Ignore (Optional Features)

1. Agent framework warnings (require API keys)
2. EasyOCR warning (optional OCR engine)
3. ChromaDB warning (optional vector DB)
4. Observability warnings (optional services)

## Verification

After fixing `VITE_API_URL`, verify:

1. **Backend health check:**
   ```bash
   curl https://synthralos-backend.onrender.com/api/v1/utils/health-check
   # Should return: true (no redirect)
   ```

2. **Frontend API calls:**
   - Open browser DevTools → Network tab
   - Check API calls - should be `/api/v1/users/me` (not `/api/v1/api/v1/users/me`)
   - Should return 200 OK (not 404)

## Related Documentation

- `docs/FRONTEND_BACKEND_INTERACTION.md` - How frontend and backend communicate
- `docs/RENDER_DEPLOYMENT.md` - Deployment guide
- `render.yaml` - Blueprint configuration
