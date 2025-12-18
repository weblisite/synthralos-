# Tesseract OCR Setup Guide

**Date:** December 18, 2025

## Warning Message

```
WARNING:app.ocr.service:Tesseract not available: tesseract is not installed or it's not in your PATH. See README file for more information.
```

## What is Tesseract?

Tesseract is an open-source OCR (Optical Character Recognition) engine that can extract text from images. It's one of several OCR engines supported by SynthralOS.

## Current Status

**Tesseract is optional** - The OCR service will work without it, but Tesseract serves as a fallback engine when other OCR engines are unavailable or fail.

## Impact

- ✅ **OCR service will still work** - Other engines (EasyOCR, Google Vision, PaddleOCR, DocTR) can be used
- ⚠️ **Fallback unavailable** - If other engines fail, Tesseract won't be available as a backup
- ⚠️ **Some OCR jobs may fail** - Jobs that specifically request Tesseract will fail

## Solutions

### Option 1: Install Tesseract in Docker Image (Recommended for Production)

Add Tesseract installation to `backend/Dockerfile`:

```dockerfile
# Install Tesseract OCR
RUN apt-get update && \
    apt-get install -y tesseract-ocr tesseract-ocr-eng && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

**Pros:**
- Tesseract available in all deployments
- No additional configuration needed
- Works on Render, local, and other platforms

**Cons:**
- Increases Docker image size (~50-100MB)
- Slightly longer build time

### Option 2: Disable Tesseract (If Not Needed)

If you don't need Tesseract, you can ignore the warning. The OCR service will:
- Use other available engines (EasyOCR, Google Vision, etc.)
- Skip Tesseract fallback
- Still function normally

### Option 3: Use Only Cloud OCR Engines

If you're using cloud-based OCR engines (Google Vision API, etc.), Tesseract is not needed:
- Google Vision API - Cloud-based, no local installation needed
- EasyOCR - Python library, installs automatically
- PaddleOCR - Python library, installs automatically

## OCR Engine Priority

The OCR service uses this priority order:

1. **DocTR** - For tables and structured documents
2. **EasyOCR** - For handwriting detection
3. **Google Vision API** - For heavy PDFs/images (requires API key)
4. **PaddleOCR** - For EU region or latency requirements
5. **Tesseract** - Fallback (currently unavailable)
6. **Omniparser** - For structured JSON extraction

## Installation Instructions

### Local Development (macOS)

```bash
brew install tesseract
```

### Local Development (Linux/Ubuntu)

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng
```

### Docker (Add to Dockerfile)

```dockerfile
# Install system dependencies including Tesseract
RUN apt-get update && \
    apt-get install -y \
        tesseract-ocr \
        tesseract-ocr-eng \
        tesseract-ocr-fra \
        tesseract-ocr-spa \
        tesseract-ocr-deu \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
```

### Render Deployment

Add to `backend/Dockerfile` before the Python dependencies installation:

```dockerfile
# Install Tesseract OCR
RUN apt-get update && \
    apt-get install -y tesseract-ocr tesseract-ocr-eng && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

## Verification

After installation, the OCR service will automatically detect Tesseract:

```
✅ Tesseract OCR engine initialized
```

## Language Support

To support additional languages, install language packs:

```bash
# Install language packs (example for French, Spanish, German)
sudo apt-get install -y \
    tesseract-ocr-fra \
    tesseract-ocr-spa \
    tesseract-ocr-deu
```

## Related Documentation

- `backend/app/ocr/service.py` - OCR service implementation
- `backend/Dockerfile` - Docker image configuration
- `docs/RENDER_DEPLOYMENT.md` - Render deployment guide

## Recommendation

**For Production:** Install Tesseract in Docker image (Option 1) to ensure reliable fallback OCR capability.

**For Development:** Install locally or ignore the warning if using cloud OCR engines.

