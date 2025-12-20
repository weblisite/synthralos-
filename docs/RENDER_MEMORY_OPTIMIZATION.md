# Render Memory Optimization Guide

**Issue:** Backend running out of memory on Render starter plan (512MB limit)
**Date:** December 18, 2025

## Problem

The Render logs show:
- `Out of memory (used over 512Mi)` during startup
- Server starts but crashes before binding to port
- Heavy imports (agent frameworks, OCR libraries, etc.) consume too much memory

## Solutions

### Option 1: Upgrade Render Plan (Recommended)

**Starter Plan:** 512MB RAM (current)
**Standard Plan:** 2GB RAM ($25/month)
**Pro Plan:** 4GB RAM ($85/month)

**Steps:**
1. Go to Render Dashboard → `synthralos-backend` service
2. Click **Settings** → **Plan**
3. Upgrade to **Standard** or **Pro** plan
4. Redeploy the service

### Option 2: Optimize Memory Usage

**Lazy Loading:**
- Most heavy imports are already lazy-loaded (agent frameworks, OCR engines)
- Consider moving more imports to function-level instead of module-level

**Disable Optional Services:**
- Set environment variables to disable unused services:
  - `DISABLE_OCR=true` (if not using OCR)
  - `DISABLE_RAG=true` (if not using RAG)
  - `DISABLE_AGENTS=true` (if not using agents)

**Reduce Worker Processes:**
- If using multiple workers, reduce to 1 worker on starter plan
- Already configured: `WEB_CONCURRENCY=1` (set by Render automatically)

### Option 3: Optimize Docker Image

**Multi-stage Build:**
- Use multi-stage Docker builds to reduce image size
- Remove build dependencies in final image

**Python Optimizations:**
- Use `PYTHONUNBUFFERED=1` (already set)
- Consider `PYTHONDONTWRITEBYTECODE=1` to skip .pyc files
- Use `python -O` for optimized bytecode

### Option 4: Split Services

**Separate Heavy Services:**
- Move OCR processing to a separate worker service
- Move agent execution to a separate worker service
- Keep main API lightweight

## Current Memory Usage

**Heavy Imports:**
- Agent frameworks (AgentGPT, AutoGPT, MetaGPT, etc.)
- OCR libraries (Tesseract, EasyOCR, PaddleOCR)
- Browser automation (Playwright, Selenium)
- Vector databases (ChromaDB)
- ML libraries (LangChain, LangGraph)

**Memory-Efficient Imports:**
- FastAPI, SQLModel, Supabase (already loaded)
- Most services lazy-load heavy dependencies

## Monitoring

**Check Memory Usage:**
1. Go to Render Dashboard → `synthralos-backend` → **Metrics**
2. Monitor **Memory Usage** graph
3. Check **Logs** for memory-related errors

**Signs of Memory Issues:**
- `Out of memory` errors in logs
- Server crashes during startup
- Slow response times
- OOM (Out of Memory) kills

## Recommended Action

**For Production:**
- Upgrade to **Standard Plan** (2GB RAM) - $25/month
- Provides sufficient memory for all services
- Better performance and reliability

**For Development/Testing:**
- Use **Starter Plan** but disable unused services
- Set environment variables to disable heavy features
- Monitor memory usage closely

## Environment Variables for Memory Optimization

Add these to Render environment variables to reduce memory usage:

```bash
# Disable unused services
DISABLE_OCR=false  # Set to true if not using OCR
DISABLE_RAG=false  # Set to true if not using RAG
DISABLE_AGENTS=false  # Set to true if not using agents

# Reduce worker concurrency
WEB_CONCURRENCY=1  # Already set by Render

# Python optimizations
PYTHONUNBUFFERED=1  # Already set
PYTHONDONTWRITEBYTECODE=1  # Skip .pyc files
```

## Related Documentation

- `docs/RENDER_DEPLOYMENT.md` - Full deployment guide
- `docs/RENDER_DATABASE_CONNECTION_FIX.md` - Database connection setup
- `backend/render-start.sh` - Startup script
