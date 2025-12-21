# How to Verify Optional Services Are Working

**Date:** December 21, 2025

## Quick Status Check

Based on your backend logs, here's how to verify each service:

---

## 1. EasyOCR Verification

### Check Logs For:
```
✅ EasyOCR engine initialized
```

### If You See:
```
INFO:app.ocr.service:easyocr not installed. Install with: pip install easyocr
```

**Status:** ❌ Not working
**Reason:** EasyOCR failed to install during Docker build
**Fix:**
- System dependencies are now in Dockerfile (committed)
- Will install automatically on next deployment
- No manual configuration needed

### Test EasyOCR:
1. Go to OCR page in frontend
2. Upload an image with handwriting
3. EasyOCR should be automatically selected for handwriting detection

---

## 2. Tweepy Verification

### Check Logs For:
```
✅ Tweepy engine initialized (Bearer Token)
```
or
```
✅ Tweepy engine initialized (OAuth)
```

### If You See:
```
INFO:app.osint.service:Tweepy not configured (missing API credentials)
```

**Status:** ❌ Not configured
**Reason:** `TWITTER_BEARER_TOKEN` environment variable not set
**Fix:**
1. Get Bearer Token from https://developer.twitter.com/
2. Go to Render Dashboard → Backend Service → Environment
3. Add: `TWITTER_BEARER_TOKEN=your_token_here`
4. Restart backend service

### Test Tweepy:
1. Go to Social Monitoring page
2. Create a new stream for Twitter/X
3. Should use Tweepy engine automatically

---

## 3. ChromaDB Verification

### Check Logs For:
```
✅ ChromaDB client initialized ([HOST]:[PORT])
```

### If You See:
```
INFO:app.rag.service:ChromaDB not configured (CHROMA_SERVER_HOST not set). Using placeholder client.
```

**Status:** ❌ Not configured
**Reason:** `CHROMA_SERVER_HOST` environment variable not set
**Fix:**
1. Deploy ChromaDB server (Cloud or self-hosted)
2. Go to Render Dashboard → Backend Service → Environment
3. Add:
   - `CHROMA_SERVER_HOST=your-chromadb-host.com`
   - `CHROMA_SERVER_HTTP_PORT=8000` (or 443 for Cloud)
   - `CHROMA_SERVER_AUTH_TOKEN=your_token` (if using Cloud)
4. Restart backend service

### Test ChromaDB:
1. Go to RAG page
2. Create a new RAG index
3. Upload documents
4. Vector embeddings should be stored in ChromaDB

---

## Current Status Summary

Based on your backend logs from the deployment:

| Service | Status | Action Needed |
|---------|--------|---------------|
| **EasyOCR** | ❌ Not installed | Wait for next deployment (auto-fix) |
| **Tweepy** | ❌ Not configured | Add `TWITTER_BEARER_TOKEN` to Render |
| **ChromaDB** | ❌ Not configured | Deploy ChromaDB & add `CHROMA_SERVER_HOST` |

---

## Verification Checklist

After configuring, verify in backend logs:

- [ ] `✅ EasyOCR engine initialized`
- [ ] `✅ Tweepy engine initialized (Bearer Token)` or `(OAuth)`
- [ ] `✅ ChromaDB client initialized ([HOST]:[PORT])`

---

## Next Steps

1. **EasyOCR:** No action needed - will work after next deployment
2. **Tweepy:** Add Twitter Bearer Token to Render environment variables
3. **ChromaDB:** Deploy ChromaDB server and add host to Render environment variables

See `docs/OPTIONAL_SERVICES_SETUP.md` for detailed setup instructions.
