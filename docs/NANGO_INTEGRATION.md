# Nango Integration Guide

This document describes the Nango integration in SynthralOS for unified OAuth management.

## Overview

**Nango** is a unified OAuth platform that simplifies OAuth flows for SaaS integrations. SynthralOS integrates Nango to:

- Standardize OAuth flows across all connectors
- Automatically handle token refresh
- Centralize token management
- Provide better security and reliability

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Frontend  │─────────▶│   Backend    │─────────▶│   Nango     │
│             │          │              │         │             │
│  OAuth UI   │◀────────│ OAuth Service│◀────────│ OAuth Proxy  │
└─────────────┘         └──────────────┘         └─────────────┘
                              │
                              ▼
                        ┌──────────────┐
                        │   Database   │
                        │  (Tokens)    │
                        └──────────────┘
```

## Configuration

### Environment Variables

```bash
# Nango Configuration
NANGO_URL=https://api.nango.dev          # Nango API URL
NANGO_SECRET_KEY=your_secret_key_here    # Nango secret key
NANGO_ENABLED=true                       # Enable/disable Nango
```

### Service Initialization

Nango service is initialized in `app/services/nango.py`:

```python
from app.services.nango import default_nango_service

# Service is automatically initialized with settings from config
```

## Connector Manifest Format

Connectors using Nango include Nango configuration in their manifest:

```json
{
  "name": "Gmail",
  "slug": "gmail",
  "nango": {
    "enabled": true,
    "provider_key": "gmail"
  },
  "oauth": {
    "authorization_url": "https://api.nango.dev/oauth/gmail",
    "token_url": "https://api.nango.dev/oauth/gmail/token",
    "default_scopes": []
  }
}
```

### Nango Provider Keys

Each connector maps to a Nango provider key:

- `gmail` → `gmail`
- `salesforce` → `salesforce`
- `github` → `github`
- etc.

See `backend/scripts/create_connectors.py` for the complete mapping.

## OAuth Flow

### 1. Authorization Request

When a connector uses Nango, the authorization URL is generated via Nango:

```python
# Backend: app/connectors/oauth.py
if use_nango:
    authorization_url = nango_service.generate_authorization_url(
        provider_key="gmail",
        user_id=user_id,
        redirect_uri=redirect_uri
    )
```

**API Endpoint:**
```bash
POST /api/v1/connectors/{slug}/authorize
{
  "redirect_uri": "https://your-app.com/callback",
  "scopes": ["optional", "scopes"]
}
```

**Response:**
```json
{
  "authorization_url": "https://api.nango.dev/oauth/gmail?state=abc123",
  "state": "abc123",
  "oauth_method": "nango"
}
```

### 2. User Authorization

User is redirected to `authorization_url`:
1. User authenticates with provider (e.g., Google)
2. User grants permissions
3. Provider redirects to Nango callback
4. Nango processes callback and redirects to your `redirect_uri`

### 3. Callback Handling

Nango handles the OAuth callback and stores tokens:

```python
# Backend: app/connectors/oauth.py
if use_nango:
    tokens = nango_service.handle_callback(
        provider_key="gmail",
        code=code,
        state=state
    )
```

**API Endpoint:**
```bash
GET /api/v1/connectors/{slug}/callback?state=abc123&code=xyz789
```

**Response:**
```json
{
  "success": true,
  "connector_slug": "gmail",
  "oauth_method": "nango"
}
```

### 4. Token Refresh

Nango automatically handles token refresh:

```python
# Backend: app/connectors/oauth.py
if use_nango:
    tokens = nango_service.refresh_tokens(
        provider_key="gmail",
        user_id=user_id
    )
```

**API Endpoint:**
```bash
POST /api/v1/connectors/{slug}/refresh
```

**Response:**
```json
{
  "success": true,
  "connector_slug": "gmail",
  "expires_in": 3600,
  "oauth_method": "nango"
}
```

## Fallback to Direct OAuth

If Nango is disabled or unavailable, SynthralOS falls back to direct OAuth:

```python
# Backend: app/connectors/oauth.py
if use_nango and settings.NANGO_ENABLED:
    # Use Nango
    ...
else:
    # Use direct OAuth
    authorization_url = oauth_config["authorization_url"]
    # Direct OAuth flow
    ...
```

The API response includes `oauth_method` to indicate which method was used:

```json
{
  "authorization_url": "...",
  "state": "...",
  "oauth_method": "direct"  // or "nango"
}
```

## Token Storage

### Nango-Managed Tokens

When using Nango, tokens are stored by Nango:
- Access tokens
- Refresh tokens
- Expiration times
- Token metadata

### Direct OAuth Tokens

When using direct OAuth, tokens are stored in SynthralOS database:
- `ConnectorOAuthToken` model
- Encrypted storage
- User-specific tokens

## Service Implementation

### NangoService

Located in `app/services/nango.py`:

```python
class NangoService:
    def generate_authorization_url(
        self,
        provider_key: str,
        user_id: UUID,
        redirect_uri: str,
        scopes: list[str] | None = None
    ) -> dict[str, Any]:
        """Generate Nango OAuth authorization URL."""
        ...

    def handle_callback(
        self,
        provider_key: str,
        code: str,
        state: str
    ) -> dict[str, Any]:
        """Handle Nango OAuth callback."""
        ...

    def get_tokens(
        self,
        provider_key: str,
        user_id: UUID
    ) -> dict[str, Any]:
        """Get stored tokens from Nango."""
        ...

    def refresh_tokens(
        self,
        provider_key: str,
        user_id: UUID
    ) -> dict[str, Any]:
        """Refresh tokens via Nango."""
        ...
```

### Integration with OAuth Service

The `ConnectorOAuthService` (`app/connectors/oauth.py`) integrates Nango:

```python
class ConnectorOAuthService:
    def __init__(self):
        self.nango_service = default_nango_service

    def generate_authorization_url(self, ...):
        # Check if connector uses Nango
        if use_nango:
            return self.nango_service.generate_authorization_url(...)
        else:
            # Direct OAuth
            ...
```

## API Endpoints

All connector OAuth endpoints support Nango:

### List Connectors

```bash
GET /api/v1/connectors/list
```

Returns `nango_enabled` and `nango_provider_key` for each connector.

### Authorize Connector

```bash
POST /api/v1/connectors/{slug}/authorize
```

Returns `oauth_method: "nango"` if Nango is used.

### OAuth Callback

```bash
GET /api/v1/connectors/{slug}/callback
```

Handles both Nango and direct OAuth callbacks.

### Refresh Tokens

```bash
POST /api/v1/connectors/{slug}/refresh
```

Refreshes tokens via Nango or direct OAuth.

## Testing

### Test Nango Integration

1. **Enable Nango:**
   ```bash
   export NANGO_ENABLED=true
   export NANGO_SECRET_KEY=your_key
   ```

2. **List connectors:**
   ```bash
   curl -H "Authorization: Bearer TOKEN" \
     http://localhost:8000/api/v1/connectors/list
   ```

3. **Check Nango status:**
   ```bash
   # Look for nango_enabled: true in response
   ```

4. **Authorize connector:**
   ```bash
   curl -X POST \
     -H "Authorization: Bearer TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"redirect_uri": "http://localhost:3000/callback"}' \
     http://localhost:8000/api/v1/connectors/gmail/authorize
   ```

5. **Verify oauth_method:**
   ```bash
   # Response should include "oauth_method": "nango"
   ```

### Test Fallback to Direct OAuth

1. **Disable Nango:**
   ```bash
   export NANGO_ENABLED=false
   ```

2. **Authorize connector:**
   ```bash
   # Should use direct OAuth
   # Response should include "oauth_method": "direct"
   ```

## Troubleshooting

### Nango Not Working

**Problem:** Connector uses direct OAuth even though Nango is enabled

**Solutions:**
1. Check `NANGO_ENABLED=true` in environment
2. Verify `NANGO_SECRET_KEY` is set correctly
3. Check connector manifest has `nango.enabled: true`
4. Verify Nango service is accessible (`NANGO_URL`)
5. Check Nango service logs

### Token Refresh Fails

**Problem:** Token refresh returns error

**Solutions:**
1. Verify tokens exist in Nango
2. Check refresh token is valid
3. Re-authorize connector if refresh token expired
4. Check Nango service status

### Authorization URL Invalid

**Problem:** Authorization URL returns 404

**Solutions:**
1. Verify Nango provider key matches connector slug
2. Check Nango provider is configured correctly
3. Ensure `NANGO_URL` is correct
4. Verify provider key exists in Nango

## Best Practices

1. **Always check `oauth_method`** in API responses
2. **Use Nango when available** for better token management
3. **Handle fallback gracefully** when Nango is unavailable
4. **Monitor Nango service health** for production deployments
5. **Store Nango credentials securely** (use secrets management)
6. **Test both Nango and direct OAuth** flows during development

## Additional Resources

- [Nango Documentation](https://docs.nango.dev)
- [Nango API Reference](https://docs.nango.dev/api-reference)
- [OAuth 2.0 Specification](https://oauth.net/2/)
- [Connector Guide](./CONNECTORS_GUIDE.md)
