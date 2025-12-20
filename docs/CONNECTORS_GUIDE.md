# Connector Guide

This guide explains how to use connectors in SynthralOS, including OAuth authorization, Nango integration, and connector actions.

## Table of Contents

1. [Overview](#overview)
2. [Connector Categories](#connector-categories)
3. [OAuth Authorization](#oauth-authorization)
4. [Nango Integration](#nango-integration)
5. [Using Connectors](#using-connectors)
6. [Connector Actions](#connector-actions)
7. [Troubleshooting](#troubleshooting)

## Overview

Connectors enable SynthralOS to integrate with external services and APIs. Each connector provides:

- **OAuth Authentication**: Secure token-based authentication
- **Actions**: Pre-defined operations you can perform
- **Triggers**: Webhooks and events from external services
- **Metadata**: Category, description, and status information

### Available Connectors

SynthralOS includes **99 pre-configured connectors** across 9 categories:

- **Communication & Collaboration** (15): Gmail, Teams, Discord, Zoom, etc.
- **CRM & Sales** (10): Salesforce, HubSpot, Pipedrive, etc.
- **Project Management** (10): Asana, Trello, Jira, Linear, etc.
- **File Storage & Cloud** (10): Google Drive, Dropbox, S3, etc.
- **E-commerce & Payments** (10): Shopify, PayPal, Stripe, etc.
- **Social Media** (10): Twitter, Facebook, LinkedIn, etc.
- **Analytics & Data** (10): Google Analytics, Mixpanel, Snowflake, etc.
- **Development & Code** (10): GitHub, GitLab, CircleCI, etc.
- **AI & Machine Learning** (6): OpenAI, Anthropic, Google AI, etc.
- **Productivity & Notes** (2): Notion, When2Meet
- **Calendar & Scheduling** (4): Google Calendar, Outlook, etc.
- **Payments** (1): Stripe

## Connector Categories

Connectors are organized by category for easy discovery:

```bash
# List connectors by category
GET /api/v1/connectors/list?category=Communication%20%26%20Collaboration
```

Categories include:
- `Communication & Collaboration`
- `CRM & Sales`
- `Project Management`
- `File Storage & Cloud`
- `E-commerce & Payments`
- `Social Media`
- `Analytics & Data`
- `Development & Code`
- `AI & Machine Learning`
- `Productivity & Notes`
- `Calendar & Scheduling`
- `Payments`

## OAuth Authorization

Most connectors require OAuth authorization to access external services. SynthralOS supports two OAuth methods:

### 1. Nango (Recommended)

**Nango** provides unified OAuth management for all connectors. It handles:
- Token storage and refresh
- OAuth flow standardization
- Automatic token rotation
- Multi-provider support

**Benefits:**
- Simplified OAuth flows
- Automatic token refresh
- Centralized token management
- Better security

### 2. Direct OAuth

For connectors without Nango support, SynthralOS uses direct OAuth flows with the provider's native OAuth endpoints.

## Nango Integration

### Enabling Nango

Nango is enabled by default. Configure it in your environment:

```bash
NANGO_URL=https://api.nango.dev
NANGO_SECRET_KEY=your_secret_key_here
NANGO_ENABLED=true
```

### Checking Nango Status

When listing connectors, check the `nango_enabled` field:

```json
{
  "connectors": [
    {
      "slug": "gmail",
      "name": "Gmail",
      "nango_enabled": true,
      "nango_provider_key": "gmail",
      "category": "Communication & Collaboration"
    }
  ]
}
```

### Nango vs Direct OAuth

The API automatically detects which method to use:

```json
{
  "authorization_url": "https://api.nango.dev/oauth/gmail",
  "state": "abc123",
  "oauth_method": "nango"  // or "direct"
}
```

## Using Connectors

### Step 1: List Available Connectors

```bash
# List all connectors
GET /api/v1/connectors/list

# Filter by category
GET /api/v1/connectors/list?category=Social%20Media

# Filter by status
GET /api/v1/connectors/list?status_filter=beta
```

**Response:**
```json
{
  "connectors": [
    {
      "id": "uuid",
      "slug": "gmail",
      "name": "Gmail",
      "status": "beta",
      "category": "Communication & Collaboration",
      "description": "Send and receive emails via Gmail API",
      "latest_version": "1.0.0",
      "nango_enabled": true,
      "nango_provider_key": "gmail",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total_count": 99
}
```

### Step 2: Get Connector Details

```bash
GET /api/v1/connectors/{slug}
```

**Response:**
```json
{
  "id": "uuid",
  "slug": "gmail",
  "name": "Gmail",
  "status": "beta",
  "version": "1.0.0",
  "manifest": {
    "name": "Gmail",
    "slug": "gmail",
    "description": "Send and receive emails via Gmail API",
    "category": "Communication & Collaboration",
    "nango": {
      "enabled": true,
      "provider_key": "gmail"
    },
    "oauth": {
      "authorization_url": "https://api.nango.dev/oauth/gmail",
      "token_url": "https://api.nango.dev/oauth/gmail/token",
      "default_scopes": []
    },
    "actions": {
      "test_connection": {
        "name": "Test Connection",
        "description": "Test the connection to the service",
        "method": "GET",
        "endpoint": "/test"
      }
    }
  }
}
```

### Step 3: Authorize Connector

```bash
POST /api/v1/connectors/{slug}/authorize
Content-Type: application/json

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

**Next Steps:**
1. Redirect user to `authorization_url`
2. User authorizes the application
3. User is redirected to your `redirect_uri` with `code` and `state`
4. Handle callback (see Step 4)

### Step 4: Handle OAuth Callback

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

### Step 5: Refresh Tokens (if needed)

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

## Connector Actions

Once authorized, you can invoke connector actions:

### List Available Actions

```bash
GET /api/v1/connectors/{slug}/actions
```

**Response:**
```json
{
  "actions": {
    "test_connection": {
      "name": "Test Connection",
      "description": "Test the connection to the service",
      "method": "GET",
      "endpoint": "/test"
    },
    "send_email": {
      "name": "Send Email",
      "description": "Send an email via Gmail",
      "method": "POST",
      "endpoint": "/messages/send"
    }
  }
}
```

### Invoke an Action

```bash
POST /api/v1/connectors/{slug}/{action}
Content-Type: application/json

{
  "to": "recipient@synthralos.ai",
  "subject": "Hello",
  "body": "This is a test email"
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "message_id": "msg123",
    "status": "sent"
  }
}
```

## Troubleshooting

### OAuth Authorization Fails

**Problem:** Authorization URL returns error

**Solutions:**
1. Check Nango configuration (`NANGO_URL`, `NANGO_SECRET_KEY`)
2. Verify connector manifest includes Nango configuration
3. Ensure redirect URI matches registered callback URL
4. Check connector status (should be `beta` or `stable`)

### Token Refresh Fails

**Problem:** Token refresh returns error

**Solutions:**
1. Verify tokens exist for the connector
2. Check if refresh token is still valid
3. Re-authorize the connector if refresh token expired
4. Check Nango service status (if using Nango)

### Connector Action Fails

**Problem:** Action invocation returns 401 Unauthorized

**Solutions:**
1. Ensure connector is authorized (`POST /connectors/{slug}/authorize`)
2. Check if tokens are expired (refresh if needed)
3. Verify action exists in connector manifest
4. Check required scopes are granted

### Nango Not Working

**Problem:** Nango-enabled connector uses direct OAuth

**Solutions:**
1. Verify `NANGO_ENABLED=true` in environment
2. Check `NANGO_SECRET_KEY` is set correctly
3. Verify connector manifest has `nango.enabled: true`
4. Check Nango service is accessible

## Best Practices

1. **Always check connector status** before authorization
2. **Use Nango when available** for better token management
3. **Handle token refresh** proactively before expiration
4. **Store state tokens securely** during OAuth flow
5. **Validate callback state** to prevent CSRF attacks
6. **Monitor connector health** via test_connection action
7. **Use appropriate scopes** - request only what you need

## Examples

### Complete OAuth Flow (Gmail)

```python
import requests

# 1. List connectors
response = requests.get(
    "http://localhost:8000/api/v1/connectors/list",
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)
connectors = response.json()["connectors"]
gmail = next(c for c in connectors if c["slug"] == "gmail")

# 2. Authorize
auth_response = requests.post(
    f"http://localhost:8000/api/v1/connectors/gmail/authorize",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json={"redirect_uri": "https://your-app.com/callback"}
)
auth_data = auth_response.json()

# 3. Redirect user to authorization_url
print(f"Visit: {auth_data['authorization_url']}")

# 4. After callback, invoke action
action_response = requests.post(
    "http://localhost:8000/api/v1/connectors/gmail/send_email",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json={
        "to": "recipient@synthralos.ai",
        "subject": "Hello",
        "body": "Test email"
    }
)
print(action_response.json())
```

### Filter Connectors by Category

```python
# Get all social media connectors
response = requests.get(
    "http://localhost:8000/api/v1/connectors/list",
    params={"category": "Social Media"},
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)
social_media_connectors = response.json()["connectors"]
```

### Check Nango Status

```python
# List connectors and check Nango status
response = requests.get(
    "http://localhost:8000/api/v1/connectors/list",
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

for connector in response.json()["connectors"]:
    if connector["nango_enabled"]:
        print(f"{connector['name']} uses Nango (provider: {connector['nango_provider_key']})")
    else:
        print(f"{connector['name']} uses direct OAuth")
```

## Additional Resources

- [API Documentation](../backend/app/api/routes/connectors.py)
- [Nango Documentation](https://docs.nango.dev)
- [OAuth 2.0 Specification](https://oauth.net/2/)
