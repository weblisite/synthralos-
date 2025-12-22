# Webhook Security Implementation

## Overview

Webhooks in SynthralOS use **signature-based authentication** (HMAC) rather than CSRF tokens or PKCE. This is the correct approach because:

1. **Webhooks are called by external services** (GitHub, Stripe, etc.), not browsers
2. **CSRF protection is for browser-based requests** - webhooks don't have browser sessions
3. **PKCE is for OAuth flows** - webhooks use signature validation instead

---

## Security Mechanisms

### ✅ Signature Validation (HMAC)

**Location:** `backend/app/connectors/webhook.py`

**How it works:**
- Each webhook subscription has a secret (`endpoint_secret`)
- External service signs payload with secret using HMAC-SHA256 or HMAC-SHA1
- SynthralOS validates signature before processing webhook

**Supported Algorithms:**
- `sha256` (default)
- `sha1`

**Signature Headers:**
- `X-Hub-Signature-256` (GitHub-style)
- `X-Signature` (Generic)

**Example:**
```python
# External service signs payload
signature = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
headers = {"X-Signature": signature}

# SynthralOS validates
is_valid = validate_webhook_signature(
    payload=payload,
    signature=signature,
    secret=subscription.endpoint_secret,
    algorithm="sha256"
)
```

---

## CSRF Protection

### ✅ Webhooks are Exempted from CSRF

**Why:**
- Webhooks are called by external services, not browsers
- CSRF protection is for browser-based requests with sessions
- Webhooks use signature validation instead

**Implementation:**
- Webhook endpoints are exempted in CSRF middleware
- Path: `/api/v1/connectors/{slug}/webhook`
- Exempted in `backend/app/main.py` CSRF middleware configuration

**Code:**
```python
# backend/app/main.py
app.add_middleware(
    CSRFMiddleware,
    exempt_paths=[
        "/api/v1/connectors/",  # Webhook endpoints exempted
        # ... other exempt paths
    ],
)
```

---

## PKCE (Not Applicable)

### ❌ PKCE is NOT Used for Webhooks

**Why:**
- PKCE is specifically for OAuth 2.0 authorization code flows
- Webhooks don't use OAuth flows
- Webhooks use signature-based authentication (HMAC)

**PKCE is used for:**
- ✅ OAuth connector authorization flows
- ✅ Direct OAuth flows
- ✅ Nango OAuth flows

**PKCE is NOT used for:**
- ❌ Webhook endpoints (use signature validation)
- ❌ API endpoints (use JWT tokens)
- ❌ WebSocket connections (use JWT tokens)

---

## Webhook Endpoint Security

### Endpoint: `POST /api/v1/connectors/{slug}/webhook`

**Security Measures:**
1. ✅ **Signature Validation** - HMAC signature required
2. ✅ **CSRF Exempt** - Not subject to CSRF protection (external service calls)
3. ✅ **Secret-based** - Each subscription has unique secret
4. ✅ **Constant-time comparison** - Prevents timing attacks

**Request Flow:**
```
1. External service sends webhook with signature
2. SynthralOS receives webhook at /api/v1/connectors/{slug}/webhook
3. CSRF middleware skips check (webhook is exempted)
4. Webhook service validates signature
5. If valid, process webhook and emit workflow signal
6. If invalid, return 401 Unauthorized
```

---

## Comparison: Webhooks vs OAuth Flows

| Feature | Webhooks | OAuth Flows |
|---------|----------|-------------|
| **Authentication** | HMAC Signature | OAuth 2.0 |
| **CSRF Protection** | Exempted | Protected |
| **PKCE** | Not applicable | Used |
| **Called By** | External services | Browsers/users |
| **Security Method** | Signature validation | CSRF + PKCE |

---

## Security Best Practices

### ✅ Implemented

1. **Signature Validation**
   - All webhooks require valid HMAC signature
   - Constant-time comparison prevents timing attacks
   - Supports multiple signature algorithms

2. **Secret Management**
   - Each webhook subscription has unique secret
   - Secrets stored securely in database
   - Secrets can be rotated

3. **CSRF Exemption**
   - Webhooks correctly exempted from CSRF
   - Prevents false positives from external services

### 🔒 Recommendations

1. **Rate Limiting**
   - Consider adding rate limiting for webhook endpoints
   - Prevent abuse from malicious actors

2. **IP Whitelisting** (Optional)
   - For high-security connectors, consider IP whitelisting
   - Validate webhook source IP addresses

3. **Secret Rotation**
   - Implement secret rotation mechanism
   - Allow users to regenerate webhook secrets

---

## Code References

### Webhook Service
- **File:** `backend/app/connectors/webhook.py`
- **Class:** `ConnectorWebhookService`
- **Method:** `validate_webhook_signature()`

### Webhook Endpoint
- **File:** `backend/app/api/routes/connectors.py`
- **Route:** `POST /api/v1/connectors/{slug}/webhook`
- **Function:** `webhook_ingress()`

### CSRF Middleware
- **File:** `backend/app/api/middleware/csrf.py`
- **Exemption:** Configured in `backend/app/main.py`

---

## Summary

✅ **Webhooks are secure** - They use signature validation (HMAC)  
✅ **CSRF exempted** - Correctly exempted (external service calls)  
❌ **PKCE not applicable** - PKCE is for OAuth flows, not webhooks  

**Webhook security is properly implemented** using industry-standard HMAC signature validation, which is the correct approach for webhook endpoints.

