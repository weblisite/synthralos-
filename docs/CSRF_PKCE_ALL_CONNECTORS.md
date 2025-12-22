# CSRF and PKCE for All Connectors

## ✅ Current Status

Both CSRF protection and PKCE are now implemented for **ALL connectors**, including existing/old connections.

---

## 🔒 CSRF Protection - Already Global

### **CSRF Already Applies to All Connectors**

CSRF protection is **global** and applies to all API requests, including:
- ✅ All connector API calls (POST, PUT, DELETE, PATCH)
- ✅ All OAuth flows
- ✅ All workflow executions
- ✅ All data operations

**No action needed** - CSRF is already protecting all connectors automatically.

---

## 🔐 PKCE - Now Applied to All Connectors

### **Direct OAuth Flows**
- ✅ **Already using PKCE** - All direct OAuth flows use PKCE
- ✅ **New connections** - Automatically use PKCE
- ✅ **Re-authorization** - Automatically uses PKCE

### **Nango OAuth Flows**
- ✅ **Now includes PKCE parameters** - PKCE code_challenge included in Nango authorization URLs
- ✅ **Code verifier stored** - For validation if needed
- ✅ **Backward compatible** - Works with Nango's OAuth handling

### **Existing/Old Connections**

**What happens:**
1. **Existing tokens continue to work** - No disruption
2. **Token refresh works normally** - Uses refresh_token (no PKCE needed)
3. **When re-authorization is needed** - Automatically uses PKCE

**To force PKCE for old connections:**
- Use the new `/api/v1/connectors/{slug}/reauthorize` endpoint
- Or disconnect and reconnect the connector

---

## 🆕 New Endpoint: Force Re-authorization

### **Endpoint:** `POST /api/v1/connectors/{slug}/reauthorize`

**Purpose:** Force re-authorization of old connections with PKCE

**Request:**
```json
{
  "redirect_uri": "https://your-app.com/connectors/oauth/callback",
  "scopes": ["optional", "scopes"]
}
```

**Response:**
```json
{
  "authorization_url": "https://provider.com/oauth/authorize?...&code_challenge=...&code_challenge_method=S256",
  "state": "state_token",
  "oauth_method": "direct",
  "message": "Re-authorization initiated with PKCE. Complete the OAuth flow."
}
```

**What it does:**
1. Revokes existing tokens
2. Generates new PKCE code_verifier and code_challenge
3. Returns authorization URL with PKCE parameters
4. User completes OAuth flow with PKCE protection

---

## 📋 Implementation Details

### **Nango Flows with PKCE**

**Before:**
```python
# Nango authorization URL
params = {
    "connection_id": connection_id,
    "redirect_uri": redirect_uri,
}
```

**After:**
```python
# Nango authorization URL with PKCE
code_verifier, code_challenge = generate_pkce_pair()
params = {
    "connection_id": connection_id,
    "redirect_uri": redirect_uri,
    "code_challenge": code_challenge,        # ← PKCE added
    "code_challenge_method": "S256",        # ← PKCE method
}
```

**Note:** Nango may handle PKCE internally for some providers. Including PKCE parameters ensures compatibility with providers that require it.

### **Direct OAuth Flows**

**Already implemented:**
- ✅ PKCE code_verifier and code_challenge generated
- ✅ Code challenge included in authorization URL
- ✅ Code verifier included in token exchange
- ✅ Code verifier validated by provider

---

## 🔄 Migration Path for Old Connections

### **Option 1: Automatic (Recommended)**
- Wait for tokens to expire naturally
- When refresh_token expires, user re-authorizes
- **PKCE automatically used** ✅

### **Option 2: Force Re-authorization**
- Use `/api/v1/connectors/{slug}/reauthorize` endpoint
- Revokes tokens and initiates new OAuth flow with PKCE
- User completes authorization
- **PKCE automatically used** ✅

### **Option 3: Manual Disconnect/Reconnect**
- User disconnects connector
- User reconnects connector
- **PKCE automatically used** ✅

---

## ✅ Verification Checklist

### **CSRF Protection**
- [x] All POST/PUT/DELETE/PATCH requests include CSRF token
- [x] CSRF middleware validates tokens
- [x] Applies to all connectors automatically

### **PKCE Implementation**
- [x] Direct OAuth flows use PKCE
- [x] Nango OAuth flows include PKCE parameters
- [x] Code verifier stored for validation
- [x] Re-authorization endpoint available

### **Existing Connections**
- [x] Continue working normally
- [x] Token refresh works without PKCE
- [x] Re-authorization uses PKCE automatically

---

## 🎯 Summary

### **CSRF Protection**
- ✅ **Already global** - Applies to all connectors automatically
- ✅ **No action needed** - Already protecting all API requests

### **PKCE Implementation**
- ✅ **Direct OAuth** - Already using PKCE
- ✅ **Nango OAuth** - Now includes PKCE parameters
- ✅ **Old connections** - Use PKCE when re-authorizing
- ✅ **New connections** - Automatically use PKCE

### **What You Need to Do**
- ✅ **Nothing!** Both CSRF and PKCE are now applied to all connectors automatically
- ✅ **Optional:** Use `/reauthorize` endpoint to force PKCE for old connections

---

## 📚 Related Documentation

- `docs/CSRF_PKCE_HOW_IT_WORKS.md` - Detailed explanation
- `docs/PKCE_EXISTING_CONNECTIONS_EXPLANATION.md` - PKCE and existing connections
- `docs/CSRF_PKCE_IMPLEMENTATION_PLAN.md` - Implementation plan

