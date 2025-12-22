# PKCE and Existing Connections - Detailed Explanation

## What "Existing Connections" Means

When I said **"Existing connections: Not affected (only new connections use PKCE)"**, here's what that means:

---

## 🔄 OAuth Connection Lifecycle

### 1. **Initial Connection (Uses PKCE)**
```
User clicks "Connect Gmail"
  ↓
Backend generates PKCE code_verifier and code_challenge
  ↓
User authorizes on Google
  ↓
Backend exchanges authorization_code + code_verifier for tokens
  ↓
Tokens stored: access_token, refresh_token
```

**PKCE is used here** ✅

### 2. **Using Existing Tokens (No PKCE)**
```
User runs a workflow that uses Gmail connector
  ↓
Backend retrieves stored access_token from Infisical/Nango
  ↓
Uses access_token to make API calls to Gmail
```

**PKCE is NOT used here** - tokens are already obtained ✅

### 3. **Token Refresh (No PKCE)**
```
access_token expires (usually after 1 hour)
  ↓
Backend uses refresh_token to get new access_token
  ↓
Uses refresh_token grant type (no authorization_code needed)
```

**PKCE is NOT used here** - refresh_token flow doesn't use PKCE ✅

### 4. **Re-authorization (Uses PKCE)**
```
refresh_token expires or is revoked
  ↓
User needs to reconnect connector
  ↓
Backend generates NEW PKCE code_verifier and code_challenge
  ↓
User authorizes again
```

**PKCE is used here** ✅

---

## What "Existing Connections" Means

### **Scenario 1: Connector Connected Before PKCE Implementation**

If a user connected Gmail **before** PKCE was implemented:

1. **Their stored tokens still work:**
   - `access_token` - Used for API calls ✅
   - `refresh_token` - Used for token refresh ✅

2. **Token refresh works normally:**
   - Uses `refresh_token` grant type
   - No PKCE involved
   - Works exactly as before ✅

3. **Only when re-authorization is needed:**
   - If `refresh_token` expires (rare, usually lasts months/years)
   - If user disconnects and reconnects
   - **Then** PKCE will be used (because it's a new authorization flow)

### **Scenario 2: Connector Connected After PKCE Implementation**

If a user connects Gmail **after** PKCE was implemented:

1. **PKCE is used during connection:**
   - Authorization URL includes `code_challenge`
   - Token exchange includes `code_verifier`
   - Tokens stored normally ✅

2. **After connection:**
   - Using tokens: No PKCE (just uses stored tokens)
   - Refreshing tokens: No PKCE (uses refresh_token)
   - Re-authorizing: PKCE used again ✅

---

## Code Evidence

### Token Refresh (No PKCE)
```python
# backend/app/connectors/oauth.py - refresh_tokens()
data = {
    "grant_type": "refresh_token",  # ← Uses refresh_token, not authorization_code
    "refresh_token": tokens["refresh_token"],
    "client_id": client_id,
}
# No code_verifier needed - refresh_token flow doesn't use PKCE
```

### Using Stored Tokens (No PKCE)
```python
# backend/app/api/routes/connectors.py - invoke_connector_action()
tokens = oauth_service.get_tokens(
    connector_slug=slug,
    user_id=current_user.id,
)
# Just retrieves stored tokens - no PKCE involved
credentials = {
    "access_token": tokens.get("access_token"),
    "refresh_token": tokens.get("refresh_token"),
}
# Uses stored tokens directly - no PKCE
```

### New Authorization (Uses PKCE)
```python
# backend/app/connectors/oauth.py - generate_authorization_url()
code_verifier, code_challenge = generate_pkce_pair()  # ← PKCE generated
params = {
    "code_challenge": code_challenge,  # ← PKCE included
    "code_challenge_method": "S256",
}
```

---

## Summary

### **"Existing Connections" = Connectors Already Connected**

**What works without PKCE:**
- ✅ Using stored `access_token` for API calls
- ✅ Refreshing tokens using `refresh_token`
- ✅ All normal connector operations

**What requires PKCE:**
- ✅ Initial connection (new connector)
- ✅ Re-authorization (if tokens expire/revoked)
- ✅ Reconnection (user disconnects and reconnects)

### **Key Point:**

**PKCE only affects the authorization flow** (getting tokens initially or re-authorizing).

**PKCE does NOT affect:**
- Using existing tokens
- Refreshing tokens
- Normal connector operations

---

## Real-World Example

### User Connected Gmail 6 Months Ago

**Current State:**
- Tokens stored: `access_token` (expires in 1 hour), `refresh_token` (expires in 6 months)
- Connection status: ✅ Connected

**What Happens:**

1. **User runs workflow using Gmail:**
   - Backend uses stored `access_token`
   - **No PKCE involved** ✅

2. **access_token expires:**
   - Backend uses `refresh_token` to get new `access_token`
   - **No PKCE involved** ✅

3. **6 months later, refresh_token expires:**
   - User needs to reconnect
   - Backend generates PKCE `code_verifier` and `code_challenge`
   - **PKCE used here** ✅

---

## Bottom Line

**"Existing connections" means connectors that are already connected and have tokens stored.**

**These connections:**
- ✅ Continue working normally
- ✅ Don't need PKCE for normal operations
- ✅ Only use PKCE if re-authorization is needed

**PKCE is transparent** - it only affects the authorization step, not the use of tokens.
