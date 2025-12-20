# Complete Setup Guide - All Optional Services

**Date:** December 20, 2025

This guide provides step-by-step instructions for configuring all optional services to eliminate backend warnings.

## Quick Reference

| Service | Status | Setup Time | Cost |
|---------|--------|------------|------|
| EasyOCR | ✅ Auto-installed | 0 min | Free |
| Langfuse | ⚠️ Recommended | 5 min | Free tier available |
| PostHog | ⚠️ Recommended | 5 min | Free tier available |
| ChromaDB | Optional | 15-30 min | Free (self-hosted) or paid (cloud) |
| Tweepy/Twitter | Optional | 10 min | Free tier available |
| Wazuh | Optional | 30+ min | Free (self-hosted) |
| Signoz | Optional | 30+ min | Free (self-hosted) |

---

## 1. EasyOCR ✅ (Already Configured)

**Status:** ✅ **No action needed** - Already in `pyproject.toml` and `uv.lock`

EasyOCR will be automatically installed on the next deployment. No configuration required.

**Verification:**
- Check backend logs after deployment - should see: `✅ EasyOCR engine initialized`

---

## 2. Langfuse ⚠️ (Recommended for Production)

**Why:** Tracks LLM API calls, tokens, costs, and helps debug AI workflows

### Setup Steps:

1. **Sign up for Langfuse:**
   - Go to https://cloud.langfuse.com
   - Click "Sign Up" and create an account
   - Create a new project

2. **Get API Keys:**
   - Go to Settings → API Keys
   - Copy your **Public Key** (starts with `pk_`)
   - Copy your **Secret Key** (starts with `sk_`) - Optional but recommended

3. **Add to Render:**
   - Go to Render Dashboard → Your Backend Service → Environment
   - Add these environment variables:
     ```
     LANGFUSE_KEY=pk_lf_xxxxxxxxxxxxxxxxxxxxx
     LANGFUSE_SECRET_KEY=sk_lf_xxxxxxxxxxxxxxxxxxxxx
     LANGFUSE_HOST=https://cloud.langfuse.com
     ```

4. **Redeploy:**
   - Render will automatically redeploy when you save environment variables
   - Check logs - warning should disappear

**Cost:** Free tier includes 1M events/month

---

## 3. PostHog ⚠️ (Recommended for Production)

**Why:** User behavior analytics, feature flags, and product insights

### Setup Steps:

1. **Sign up for PostHog:**
   - Go to https://posthog.com
   - Click "Get Started" and create an account
   - Create a new project

2. **Get Project API Key:**
   - Go to Project Settings → Project API Key
   - Copy your **Project API Key** (starts with `phc_`)

3. **Add to Render:**
   - Go to Render Dashboard → Your Backend Service → Environment
   - Add these environment variables:
     ```
     POSTHOG_KEY=phc_xxxxxxxxxxxxxxxxxxxxx
     POSTHOG_HOST=https://app.posthog.com
     ```

4. **Redeploy:**
   - Render will automatically redeploy
   - Check logs - warning should disappear

**Cost:** Free tier includes 1M events/month

---

## 4. ChromaDB (Optional - Only if Using RAG)

**Why:** Vector database for RAG (Retrieval-Augmented Generation) features

### Option A: ChromaDB Cloud (Easiest)

1. **Sign up:**
   - Go to https://www.trychroma.com/
   - Create an account and project

2. **Get Connection Details:**
   - Copy your ChromaDB host URL
   - Copy your auth token (if provided)

3. **Add to Render:**
   ```
   CHROMA_SERVER_HOST=your-project.chromadb.com
   CHROMA_SERVER_HTTP_PORT=8000
   CHROMA_SERVER_AUTH_TOKEN=your-auth-token
   ```

### Option B: Self-Hosted ChromaDB

1. **Deploy ChromaDB:**
   - Use Docker: `docker run -p 8000:8000 chromadb/chroma`
   - Or deploy on Render as a separate service

2. **Add to Render:**
   ```
   CHROMA_SERVER_HOST=your-chromadb-host.onrender.com
   CHROMA_SERVER_HTTP_PORT=8000
   CHROMA_SERVER_AUTH_TOKEN=  # Leave empty if no auth
   ```

**Note:** If you're not using RAG features, you can safely ignore this warning.

---

## 5. Twitter/X API (Optional - Only if Using Twitter OSINT)

**Why:** Enables Twitter/X social media monitoring and OSINT features

### Setup Steps:

1. **Create Twitter Developer Account:**
   - Go to https://developer.twitter.com
   - Sign in with your Twitter/X account
   - Apply for a developer account (usually approved quickly)

2. **Create an App:**
   - Go to Developer Portal → Projects & Apps
   - Create a new App
   - Note your App name

3. **Get API Keys:**
   - Go to your App → Keys and Tokens
   - Generate:
     - **API Key** (Consumer Key)
     - **API Secret** (Consumer Secret)
     - **Bearer Token** (if available)

4. **Add to Render:**
   ```
   TWITTER_API_KEY=your-api-key
   TWITTER_API_SECRET=your-api-secret
   TWITTER_BEARER_TOKEN=your-bearer-token
   ```

**Note:** Twitter API has rate limits on free tier. Only enable if you need Twitter OSINT features.

---

## 6. Wazuh (Optional - Enterprise Security)

**Why:** Enterprise-grade security monitoring and audit logging

### Setup Steps:

1. **Deploy Wazuh Server:**
   - Self-hosted: Follow https://documentation.wazuh.com/current/installation-guide/
   - Or use Wazuh Cloud: https://wazuh.com/cloud/

2. **Get API Credentials:**
   - Default API user: `wazuh-wui`
   - Or create custom API user in Wazuh dashboard

3. **Add to Render:**
   ```
   WAZUH_URL=https://your-wazuh-server.com:55000
   WAZUH_USER=wazuh-wui
   WAZUH_PASSWORD=your-password
   ```

**Note:** Only needed for enterprise security requirements. Most deployments don't need this.

---

## 7. Signoz (Optional - Distributed Tracing)

**Why:** Advanced distributed tracing for microservices architectures

### Setup Steps:

1. **Deploy Signoz:**
   - Self-hosted: Follow https://signoz.io/docs/install/docker/
   - Or use Signoz Cloud: https://signoz.io/cloud/

2. **Get Endpoint:**
   - Self-hosted: `http://your-signoz-host:4317`
   - Cloud: Provided endpoint from Signoz dashboard

3. **Add to Render:**
   ```
   SIGNOZ_ENDPOINT=http://your-signoz-host:4317
   ```

**Note:** Only needed for complex microservices architectures. Most deployments don't need this.

---

## Complete Configuration Checklist

### ✅ Quick Setup (Recommended for Production):
- [ ] **Langfuse:** Sign up → Get API key → Add `LANGFUSE_KEY` to Render
- [ ] **PostHog:** Sign up → Get API key → Add `POSTHOG_KEY` to Render

### ✅ Optional (As Needed):
- [ ] **ChromaDB:** Only if using RAG features
- [ ] **Twitter API:** Only if using Twitter OSINT
- [ ] **Wazuh:** Only for enterprise security
- [ ] **Signoz:** Only for distributed tracing

### ✅ Already Done:
- [x] **EasyOCR:** Already in dependencies, will install automatically

---

## Adding Environment Variables in Render

1. **Go to Render Dashboard:**
   - Navigate to https://dashboard.render.com
   - Select your backend service (`synthralos-backend`)

2. **Open Environment Tab:**
   - Click on "Environment" in the left sidebar
   - Scroll to "Environment Variables" section

3. **Add Variables:**
   - Click "Add Environment Variable"
   - Enter the key and value
   - Click "Save Changes"

4. **Redeploy:**
   - Render automatically redeploys when you save environment variables
   - Or manually trigger: "Manual Deploy" → "Deploy latest commit"

5. **Verify:**
   - Check logs after deployment
   - Warnings should disappear for configured services

---

## Verification

After configuring services, check backend logs for:

✅ **Success indicators:**
- `✅ Langfuse client initialized`
- `✅ PostHog client initialized`
- `✅ ChromaDB client initialized`
- `✅ EasyOCR engine initialized`

❌ **Warnings should disappear:**
- No more `Langfuse not configured` warnings
- No more `PostHog not configured` warnings
- No more `ChromaDB not configured` warnings
- No more `easyocr not installed` messages

---

## Troubleshooting

### Service not working after configuration?

1. **Check environment variables:**
   - Verify they're set correctly in Render dashboard
   - Check for typos in variable names
   - Ensure values don't have extra spaces

2. **Check logs:**
   - Look for specific error messages
   - Verify API keys are correct format

3. **Redeploy:**
   - Sometimes a manual redeploy is needed
   - Go to "Manual Deploy" → "Deploy latest commit"

4. **Verify API keys:**
   - Test API keys directly with the service's API
   - Ensure accounts are active and not expired

---

## Cost Summary

| Service | Free Tier | Paid Plans |
|---------|-----------|------------|
| Langfuse | 1M events/month | Starts at $29/month |
| PostHog | 1M events/month | Starts at $0 (usage-based) |
| ChromaDB | Self-hosted free | Cloud starts at $99/month |
| Twitter API | Limited free tier | Paid plans available |
| Wazuh | Self-hosted free | Cloud plans available |
| Signoz | Self-hosted free | Cloud plans available |

**Recommendation:** Start with free tiers for Langfuse and PostHog. Add others only as needed.

---

## Related Documentation

- `docs/WARNINGS_RESOLUTION.md` - Detailed explanation of each warning
- `docs/OBSERVABILITY_SETUP.md` - Advanced observability setup
- `render.yaml` - Environment variable template

---

## Next Steps

1. **Start with recommended services:**
   - Set up Langfuse (5 minutes)
   - Set up PostHog (5 minutes)

2. **Add optional services as needed:**
   - Only configure services you actually use
   - Don't feel pressured to configure everything

3. **Monitor and optimize:**
   - Use Langfuse to track LLM costs
   - Use PostHog to understand user behavior
   - Adjust configurations based on usage

**Remember:** All warnings are safe to ignore. Configure services based on your actual needs, not just to eliminate warnings.
