# Optional Services Setup Guide

**Date:** December 21, 2025

## Overview

This guide explains how to configure the optional service dependencies that appear as INFO messages in the backend logs:
- EasyOCR (OCR engine)
- Tweepy (Twitter API client)
- ChromaDB (Vector database for RAG)

These services are **optional** - the platform works without them, but enabling them unlocks additional features.

---

## 1. EasyOCR (OCR Engine)

### Current Status
- ✅ Already in dependencies (`easyocr>=1.7.0` in `pyproject.toml`)
- ✅ System dependencies added to Dockerfile
- ⚠️ May need additional setup for optimal performance

### What is EasyOCR?
EasyOCR is an OCR engine optimized for handwriting recognition. It's automatically selected when handwriting is detected in documents.

### Installation
EasyOCR is automatically installed via `uv sync` during Docker build. The Dockerfile now includes required system dependencies:
- `libgl1-mesa-glx` - OpenGL libraries
- `libglib2.0-0` - GLib library
- `libsm6`, `libxext6`, `libxrender-dev` - X11 libraries
- `libgomp1` - OpenMP library

### Verification
After deployment, check logs for:
```
✅ EasyOCR engine initialized
```

If you see:
```
INFO:app.ocr.service:easyocr not installed. Install with: pip install easyocr
```

This means EasyOCR failed to install. Check Docker build logs for errors.

### Troubleshooting
If EasyOCR fails to initialize:
1. Check Docker build logs for installation errors
2. Verify system dependencies are installed (check Dockerfile)
3. EasyOCR downloads models on first use - ensure sufficient disk space
4. For GPU support, additional CUDA libraries may be needed

### Impact if Not Available
- OCR service will use other engines (Tesseract, PaddleOCR, Google Vision)
- Handwriting detection may be less accurate
- No critical functionality lost

---

## 2. Tweepy (Twitter/X API Client)

### Current Status
- ✅ Already in dependencies (`tweepy>=4.14.0` in `pyproject.toml`)
- ⚠️ Requires Twitter API credentials to function

### What is Tweepy?
Tweepy is the Python client for Twitter/X API. It's used for social media monitoring and OSINT operations.

### Setup Instructions

#### Step 1: Create Twitter Developer Account
1. Go to https://developer.twitter.com/
2. Sign up for a developer account
3. Create a new app/project

#### Step 2: Generate API Credentials
1. Navigate to your app's "Keys and Tokens" section
2. Generate or copy:
   - **Bearer Token** (recommended - simplest authentication)
   - **API Key** (optional - for OAuth)
   - **API Secret** (optional - for OAuth)
   - **Access Token** (optional - for OAuth)
   - **Access Token Secret** (optional - for OAuth)

#### Step 3: Configure in Render
Add environment variables in Render dashboard:

**Minimum (Bearer Token only):**
```
TWITTER_BEARER_TOKEN=your_bearer_token_here
```

**Full OAuth (if needed):**
```
TWITTER_BEARER_TOKEN=your_bearer_token_here
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
```

#### Step 4: Restart Backend Service
After adding environment variables, restart the backend service in Render.

### Verification
After configuration, check logs for:
```
✅ Tweepy engine initialized (Bearer Token)
```
or
```
✅ Tweepy engine initialized (OAuth)
```

### Impact if Not Configured
- Twitter/X social monitoring features won't work
- OSINT batch queries for Twitter will fail
- Other OSINT sources (Reddit, News, etc.) work independently

---

## 3. ChromaDB (Vector Database for RAG)

### Current Status
- ✅ Already in dependencies (`chromadb>=0.4.0` in `pyproject.toml`)
- ⚠️ Requires ChromaDB server to be deployed

### What is ChromaDB?
ChromaDB is a vector database used for storing and querying document embeddings in RAG (Retrieval-Augmented Generation) operations. It enables fast semantic search.

### Setup Options

#### Option 1: ChromaDB Cloud (Recommended for Production)

1. **Sign up for ChromaDB Cloud**
   - Go to https://www.trychroma.com/
   - Create an account and project

2. **Get Connection Details**
   - From ChromaDB Cloud dashboard, get:
     - Server host (format: `[PROJECT_ID].chromadb.cloud`)
     - Auth token (if enabled)

3. **Configure in Render**
   Add environment variables:
   ```
   CHROMA_SERVER_HOST=[PROJECT_ID].chromadb.cloud
   CHROMA_SERVER_HTTP_PORT=443
   CHROMA_SERVER_AUTH_TOKEN=your_auth_token_here
   ```

#### Option 2: Self-Hosted ChromaDB

1. **Deploy ChromaDB Server**
   ```bash
   # Using Docker
   docker run -p 8000:8000 chromadb/chroma
   ```

2. **Configure in Render**
   Add environment variables:
   ```
   CHROMA_SERVER_HOST=your-chromadb-host.com
   CHROMA_SERVER_HTTP_PORT=8000
   CHROMA_SERVER_AUTH_TOKEN=  # Leave empty for self-hosted
   ```

#### Option 3: Local Development (Persistent Client)

For local development, you can use ChromaDB's PersistentClient instead of HttpClient. This doesn't require a server.

### Verification
After configuration, check logs for:
```
✅ ChromaDB client initialized ([HOST]:[PORT])
```

### Impact if Not Configured
- RAG will use database-based search (slower but functional)
- Vector similarity search won't be available
- Document embeddings won't be stored in vector database
- RAG queries will still work but may be slower

---

## Quick Setup Checklist

### EasyOCR
- [x] Already in dependencies
- [x] System dependencies added to Dockerfile
- [ ] Verify installation after deployment

### Tweepy
- [x] Already in dependencies
- [ ] Create Twitter Developer account
- [ ] Generate Bearer Token
- [ ] Add `TWITTER_BEARER_TOKEN` to Render environment variables
- [ ] Restart backend service

### ChromaDB
- [x] Already in dependencies
- [ ] Choose deployment option (Cloud or Self-hosted)
- [ ] Deploy ChromaDB server (if self-hosting)
- [ ] Add `CHROMA_SERVER_HOST` to Render environment variables
- [ ] Add `CHROMA_SERVER_HTTP_PORT` (default: 8000, Cloud: 443)
- [ ] Add `CHROMA_SERVER_AUTH_TOKEN` (if using Cloud)
- [ ] Restart backend service

---

## Environment Variables Reference

Add these to Render dashboard → Environment Variables:

```yaml
# Twitter/X API (OSINT)
TWITTER_BEARER_TOKEN=your_bearer_token_here
# Optional OAuth credentials:
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here

# ChromaDB (Vector Database)
CHROMA_SERVER_HOST=your-chromadb-host.com
CHROMA_SERVER_HTTP_PORT=8000  # or 443 for Cloud
CHROMA_SERVER_AUTH_TOKEN=your_auth_token_here  # Optional
```

---

## Related Documentation

- `backend/pyproject.toml` - Python dependencies
- `backend/Dockerfile` - Docker image configuration
- `backend/app/core/config.py` - Configuration settings
- `render.yaml` - Render deployment configuration
- `docs/OBSERVABILITY_SETUP.md` - Other optional services setup

---

## Support

If you encounter issues:
1. Check backend logs for specific error messages
2. Verify environment variables are set correctly
3. Ensure services are restarted after configuration changes
4. Review service-specific documentation (Twitter API docs, ChromaDB docs)
