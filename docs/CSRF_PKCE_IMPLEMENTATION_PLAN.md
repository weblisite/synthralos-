# CSRF and PKCE Implementation Plan

## Overview

This document outlines the implementation of two critical security features:
1. **CSRF Protection** for general API endpoints
2. **PKCE (Proof Key for Code Exchange)** for OAuth flows

## 1. CSRF Protection Implementation

### Current State
- ✅ OAuth flows already use state tokens for CSRF protection
- ❌ General API endpoints lack CSRF protection
- ✅ JWT tokens in Authorization headers (reduces CSRF risk)
- ✅ CORS middleware restricts origins

### Implementation Strategy

#### Backend Changes

1. **CSRF Middleware** (`backend/app/api/middleware/csrf.py`)
   - Generate CSRF tokens using `secrets.token_urlsafe(32)`
   - Store tokens in Redis or in-memory cache (with expiration)
   - Validate tokens on state-changing requests (POST, PUT, DELETE, PATCH)
   - Exempt certain endpoints (health checks, public endpoints)

2. **CSRF Token Endpoint** (`backend/app/api/routes/utils.py`)
   - `GET /api/v1/utils/csrf-token` - Returns CSRF token
   - Token stored server-side with expiration (15 minutes)
   - Returns token in response header `X-CSRF-Token`

3. **Middleware Integration** (`backend/app/main.py`)
   - Add CSRF middleware after CORS middleware
   - Configure exempt paths (health, public endpoints)

#### Frontend Changes

1. **CSRF Token Management** (`frontend/src/lib/csrf.ts`)
   - Fetch CSRF token on app initialization
   - Store token in memory (not localStorage for security)
   - Refresh token periodically (before expiration)
   - Include token in `X-CSRF-Token` header for all requests

2. **API Client Update** (`frontend/src/lib/api.ts`)
   - Automatically include CSRF token in headers
   - Handle CSRF token refresh on 403 errors

### Security Considerations

- **Token Storage**: Server-side only (not in cookies to avoid CSRF)
- **Token Expiration**: 15 minutes (configurable)
- **Token Validation**: Required for POST, PUT, DELETE, PATCH
- **Exempt Endpoints**: Health checks, public endpoints, WebSocket connections

---

## 2. PKCE Implementation

### Current State
- ❌ OAuth flows use standard authorization code flow without PKCE
- ✅ State tokens provide CSRF protection
- ❌ No code_verifier/code_challenge parameters

### Implementation Strategy

#### Backend Changes

1. **PKCE Helper Functions** (`backend/app/connectors/pkce.py`)
   - `generate_code_verifier()` - Generate random 43-128 character string
   - `generate_code_challenge(verifier)` - SHA256 hash of verifier
   - `verify_code_verifier(verifier, challenge)` - Validate verifier matches challenge

2. **OAuth Service Updates** (`backend/app/connectors/oauth.py`)
   - Generate `code_verifier` and `code_challenge` in `generate_authorization_url()`
   - Store `code_verifier` with state data
   - Include `code_challenge` and `code_challenge_method=S256` in authorization URL
   - Validate `code_verifier` in `handle_callback()` before token exchange

3. **Nango Service Updates** (`backend/app/services/nango.py`)
   - Add PKCE support for Nango flows
   - Pass PKCE parameters to Nango if supported

#### Frontend Changes

1. **OAuth Modal Updates** (`frontend/src/components/Connectors/OAuthModal.tsx`)
   - Generate `code_verifier` client-side (if needed for direct OAuth)
   - Store `code_verifier` in sessionStorage (temporary, cleared after callback)
   - Include `code_verifier` in callback handling

### PKCE Flow

```
1. Client generates code_verifier (random string)
2. Client generates code_challenge = SHA256(code_verifier)
3. Authorization request includes:
   - code_challenge
   - code_challenge_method=S256
4. Provider redirects with authorization code
5. Token exchange includes:
   - authorization_code
   - code_verifier (validated against stored code_challenge)
```

### Security Benefits

- **Prevents Authorization Code Interception**: Even if code is intercepted, attacker needs code_verifier
- **Public Client Security**: Essential for SPAs and mobile apps
- **OAuth 2.1 Compliance**: PKCE is required in OAuth 2.1

---

## Implementation Steps

### Phase 1: CSRF Protection (Priority: High)

1. ✅ Create CSRF middleware
2. ✅ Add CSRF token endpoint
3. ✅ Integrate middleware in FastAPI app
4. ✅ Update frontend API client
5. ✅ Add CSRF token management
6. ✅ Test CSRF protection

### Phase 2: PKCE Implementation (Priority: High)

1. ✅ Create PKCE helper functions
2. ✅ Update OAuth service to generate PKCE parameters
3. ✅ Update OAuth callback to validate code_verifier
4. ✅ Update Nango service (if applicable)
5. ✅ Test PKCE flow end-to-end

### Phase 3: Testing & Documentation

1. ✅ Write unit tests for CSRF middleware
2. ✅ Write unit tests for PKCE functions
3. ✅ Integration tests for OAuth flows
4. ✅ Update API documentation
5. ✅ Security audit

---

## Configuration

### Environment Variables

```bash
# CSRF Configuration
CSRF_TOKEN_EXPIRY_SECONDS=900  # 15 minutes
CSRF_EXEMPT_PATHS=/health,/api/v1/utils/csrf-token

# PKCE Configuration
PKCE_CODE_VERIFIER_LENGTH=64  # 43-128 characters
PKCE_CODE_CHALLENGE_METHOD=S256  # SHA256
```

---

## Testing Checklist

### CSRF Protection
- [ ] CSRF token generation works
- [ ] CSRF token validation works
- [ ] Requests without CSRF token are rejected
- [ ] Requests with invalid CSRF token are rejected
- [ ] CSRF token expiration works
- [ ] Exempt endpoints bypass CSRF check
- [ ] Frontend automatically includes CSRF token

### PKCE
- [ ] Code verifier generation works
- [ ] Code challenge generation works
- [ ] Authorization URL includes PKCE parameters
- [ ] Code verifier validation works
- [ ] Invalid code verifier is rejected
- [ ] OAuth flow completes successfully with PKCE
- [ ] Nango flows support PKCE (if applicable)

---

## Rollout Plan

1. **Development**: Implement and test locally
2. **Staging**: Deploy to staging environment
3. **Testing**: Comprehensive security testing
4. **Production**: Deploy with monitoring
5. **Monitoring**: Watch for CSRF/PKCE errors

---

## References

- [OWASP CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [OAuth 2.0 PKCE RFC 7636](https://datatracker.ietf.org/doc/html/rfc7636)
- [OAuth 2.1 Specification](https://oauth.net/2.1/)
