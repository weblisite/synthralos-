# Quick Setup Checklist - All Warnings

## ✅ Status Summary

| # | Service | Status | Action Required | Time |
|---|---------|--------|-----------------|------|
| 1 | EasyOCR | ✅ Auto | None - Already configured | 0 min |
| 2 | Langfuse | ⚠️ Recommended | Add API key to Render | 5 min |
| 3 | PostHog | ⚠️ Recommended | Add API key to Render | 5 min |
| 4 | ChromaDB | Optional | Set up server + add config | 15-30 min |
| 5 | Twitter API | Optional | Get API keys + add to Render | 10 min |
| 6 | Wazuh | Optional | Set up server + add config | 30+ min |
| 7 | Signoz | Optional | Set up server + add config | 30+ min |

---

## 🚀 Quick Start (Recommended)

### Step 1: Set Up Langfuse (5 minutes)

1. Go to https://cloud.langfuse.com → Sign up
2. Settings → API Keys → Copy Public Key (`pk_...`)
3. Render Dashboard → Backend Service → Environment → Add:
   ```
   LANGFUSE_KEY=pk_lf_xxxxxxxxxxxxxxxxxxxxx
   LANGFUSE_SECRET_KEY=sk_lf_xxxxxxxxxxxxxxxxxxxxx  # Optional
   ```

### Step 2: Set Up PostHog (5 minutes)

1. Go to https://posthog.com → Sign up
2. Project Settings → Project API Key → Copy (`phc_...`)
3. Render Dashboard → Backend Service → Environment → Add:
   ```
   POSTHOG_KEY=phc_xxxxxxxxxxxxxxxxxxxxx
   ```

### Step 3: Verify

- Render will auto-redeploy
- Check logs - warnings should disappear
- ✅ Done!

---

## 📋 Complete Checklist

### ✅ Already Configured:
- [x] **EasyOCR** - In pyproject.toml, will install automatically

### ⚠️ Recommended (Do These):
- [ ] **Langfuse** - Add `LANGFUSE_KEY` to Render
- [ ] **PostHog** - Add `POSTHOG_KEY` to Render

### 🔧 Optional (Only If Needed):
- [ ] **ChromaDB** - Only if using RAG features
- [ ] **Twitter API** - Only if using Twitter OSINT
- [ ] **Wazuh** - Only for enterprise security
- [ ] **Signoz** - Only for distributed tracing

---

## 📝 Environment Variables Reference

Copy-paste ready for Render Dashboard:

### Langfuse (Recommended):
```
LANGFUSE_KEY=pk_lf_xxxxxxxxxxxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk_lf_xxxxxxxxxxxxxxxxxxxxx
LANGFUSE_HOST=https://cloud.langfuse.com
```

### PostHog (Recommended):
```
POSTHOG_KEY=phc_xxxxxxxxxxxxxxxxxxxxx
POSTHOG_HOST=https://app.posthog.com
```

### ChromaDB (Optional):
```
CHROMA_SERVER_HOST=your-chromadb-host.com
CHROMA_SERVER_HTTP_PORT=8000
CHROMA_SERVER_AUTH_TOKEN=your-token
```

### Twitter API (Optional):
```
TWITTER_API_KEY=your-api-key
TWITTER_API_SECRET=your-api-secret
TWITTER_BEARER_TOKEN=your-bearer-token
```

### Wazuh (Optional):
```
WAZUH_URL=http://your-wazuh-server:55000
WAZUH_USER=wazuh-wui
WAZUH_PASSWORD=your-password
```

### Signoz (Optional):
```
SIGNOZ_ENDPOINT=http://your-signoz-host:4317
```

---

## 📚 Detailed Guides

- **Complete Setup:** `docs/COMPLETE_SETUP_GUIDE.md`
- **Warnings Explanation:** `docs/WARNINGS_RESOLUTION.md`
- **Observability Setup:** `docs/OBSERVABILITY_SETUP.md`

---

## ⏱️ Estimated Time

- **Minimum (Recommended):** 10 minutes (Langfuse + PostHog)
- **Complete (All Services):** 2-3 hours (if setting up self-hosted services)

**Recommendation:** Start with Langfuse + PostHog, add others as needed.
