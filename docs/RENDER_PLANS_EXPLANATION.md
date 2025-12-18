# Render Plans Explanation

**Date:** December 18, 2025

## Two Different Plans

Render has **two separate plans** that control different aspects of your deployment:

### 1. Build Pipeline Plan (What You're Currently Viewing)

**Purpose:** Controls resources during **Docker image building** (compile time)

**Plans:**
- **Starter:** 2 CPU, 8 GB RAM - $5/1,000 min
- **Performance:** 16 CPU, 64 GB RAM - $25/1,000 min

**What it affects:**
- Speed of Docker image builds
- Time to install dependencies (`pip install`, `npm install`)
- Compilation time for your code

**Does NOT affect:**
- Runtime memory limits
- How much memory your running service can use
- Server startup or runtime performance

### 2. Web Service Runtime Plan (The One Causing Your Issue)

**Purpose:** Controls resources during **service runtime** (when your app is running)

**Plans:**
- **Starter:** 512MB RAM - Free tier (limited)
- **Standard:** 2GB RAM - $25/month
- **Pro:** 4GB RAM - $85/month
- **Pro Plus:** 8GB RAM - $170/month

**What it affects:**
- Memory available to your running application
- CPU resources during runtime
- Server performance and stability

**This is what's causing your memory issue!**

## Your Current Issue

The error `Out of memory (used over 512Mi)` is caused by the **Web Service Runtime Plan** being set to **Starter (512MB)**.

The **Build Pipeline Plan** being on Starter is fine - it only affects build speed, not runtime memory.

## Solution

You need to upgrade the **Web Service Runtime Plan**, not the Build Pipeline Plan:

### Steps to Upgrade Runtime Plan:

1. Go to **Render Dashboard**
2. Click on **`synthralos-backend`** service (not the build pipeline settings)
3. Click **Settings** tab
4. Scroll to **Plan** section
5. Change from **Starter** to **Standard** (2GB RAM - $25/month)
6. Click **Save Changes**
7. Render will automatically redeploy with the new plan

### Alternative: Update render.yaml

You can also update `render.yaml` to specify the plan:

```yaml
services:
  - type: web
    name: synthralos-backend
    plan: standard  # Change from "starter" to "standard"
    # ... rest of config
```

Then commit and push - Render will use the new plan on next deployment.

## Summary

| Plan Type | Current Setting | Issue? | Action Needed |
|-----------|----------------|--------|---------------|
| **Build Pipeline** | Starter | ✅ No | Keep as is (only affects build speed) |
| **Runtime Plan** | Starter (512MB) | ❌ **YES** | **Upgrade to Standard (2GB)** |

## Cost Impact

- **Build Pipeline:** Starter is fine (only pay for build minutes used)
- **Runtime Plan:** Upgrade to Standard = **+$25/month** (but fixes memory issue)

## Verification

After upgrading the runtime plan:
1. Check Render logs - should see "Standard plan" in service details
2. Memory errors should disappear
3. Server should start successfully and bind to port

## Related Documentation

- `docs/RENDER_MEMORY_OPTIMIZATION.md` - Memory optimization strategies
- `docs/RENDER_DEPLOYMENT.md` - Full deployment guide
- `render.yaml` - Blueprint configuration file

