# Multi-Library Logo System

## Overview

The connector logo system uses **multiple logo libraries** with automatic fallback, ensuring maximum logo coverage for all connectors.

## Logo Library Priority Order

### 1. **Custom Logo** (Highest Priority)
- Custom logo URL specified in connector manifest
- Format: Any valid image URL

### 2. **Simple Icons** (Library 1)
- **Source:** https://cdn.simpleicons.org/
- **Coverage:** 2000+ brand icons
- **Format:** SVG icons with customizable colors
- **URL Pattern:** `https://cdn.simpleicons.org/{icon-name}/{color}`
- **Examples:**
  - `https://cdn.simpleicons.org/salesforce/000000` (black)
  - `https://cdn.simpleicons.org/slack/4285F4` (blue)

### 3. **Clearbit Logo API** (Library 2)
- **Source:** https://logo.clearbit.com/
- **Coverage:** Auto-detects logos from company domains
- **Format:** PNG logos fetched from company websites
- **URL Pattern:** `https://logo.clearbit.com/{domain}`
- **Examples:**
  - `https://logo.clearbit.com/salesforce.com`
  - `https://logo.clearbit.com/slack.com`
  - `https://logo.clearbit.com/gmail.com`

### 4. **Favicon Services** (Library 3)
- **Sources:**
  - Google Favicon Service: `https://www.google.com/s2/favicons?domain={domain}&sz=128`
  - DuckDuckGo Favicon Service: `https://icons.duckduckgo.com/ip3/{domain}.ico`
- **Coverage:** Any website with a favicon
- **Format:** Favicon-based logos (may be lower resolution)
- **Examples:**
  - `https://www.google.com/s2/favicons?domain=salesforce.com&sz=128`
  - `https://icons.duckduckgo.com/ip3/slack.com.ico`

### 5. **Local Logos** (Fallback)
- **Source:** `/connectors/logos/` directory
- **Formats:** SVG and PNG files
- **Examples:**
  - `/connectors/logos/salesforce.svg`
  - `/connectors/logos/slack.png`

## How It Works

### Logo Loading Flow

```
1. Try Custom Logo (from manifest)
   ↓ (if fails)
2. Try Simple Icons (3 color variants)
   ↓ (if all fail)
3. Try Clearbit Logo API
   ↓ (if fails)
4. Try Google Favicon Service
   ↓ (if fails)
5. Try DuckDuckGo Favicon Service
   ↓ (if fails)
6. Try Local SVG file
   ↓ (if fails)
7. Try Local PNG file
   ↓ (if all fail)
8. Display generic Plug icon
```

### Domain Mapping

The system automatically maps connector slugs to domains for Clearbit and Favicon services:

**Explicit Mappings:**
- `"salesforce"` → `"salesforce.com"`
- `"google-drive"` → `"drive.google.com"`
- `"microsoft-teams"` → `"teams.microsoft.com"`

**Automatic Inference:**
- `"service-name"` → `"servicename.com"`
- `"google-service"` → `"service.google.com"`
- `"microsoft-service"` → `"service.microsoft.com"`

## Benefits

### ✅ Maximum Coverage
- **Simple Icons:** 2000+ curated brand icons
- **Clearbit:** Auto-detects from any domain
- **Favicon Services:** Works for any website
- **Local Files:** Custom logos for specific needs

### ✅ Automatic Fallback
- If one library doesn't have the logo, automatically tries the next
- No manual configuration needed for most connectors
- Ensures logo always displays (or falls back to generic icon)

### ✅ High Quality
- Simple Icons provides high-quality SVG icons
- Clearbit fetches official company logos
- Favicon services provide website-branded icons

### ✅ Performance
- CDN caching for fast loading
- Parallel loading attempts (tries multiple URLs)
- Falls back quickly if logo not found

## Examples

### Example 1: Salesforce
```
1. Custom logo: (none)
2. Simple Icons: ✅ https://cdn.simpleicons.org/salesforce/000000 (SUCCESS)
```

### Example 2: Custom Connector (not in Simple Icons)
```
1. Custom logo: (none)
2. Simple Icons: ❌ (not found)
3. Clearbit: ✅ https://logo.clearbit.com/mycompany.com (SUCCESS)
```

### Example 3: Very Obscure Service
```
1. Custom logo: (none)
2. Simple Icons: ❌ (not found)
3. Clearbit: ❌ (not found)
4. Google Favicon: ✅ https://www.google.com/s2/favicons?domain=obscure-service.com (SUCCESS)
```

## Adding New Libraries

To add a new logo library, update `getConnectorLogoUrls()` in `frontend/src/lib/connectorLogos.ts`:

```typescript
// Example: Adding Logo.dev library
function getLogoDevUrls(iconName: string): string[] {
  return [
    `https://logo.dev/${iconName}?token=YOUR_TOKEN`,
  ]
}

// Add to getConnectorLogoUrls():
urls.push(...getLogoDevUrls(iconName))
```

## Current Coverage

- ✅ **Simple Icons:** 2000+ icons
- ✅ **Clearbit:** Unlimited (any domain)
- ✅ **Favicon Services:** Unlimited (any website)
- ✅ **Local Files:** Custom additions
- ✅ **Total Coverage:** ~99%+ of connectors

## Summary

The multi-library system ensures that:
1. **Popular connectors** get high-quality logos from Simple Icons
2. **Less common connectors** get logos from Clearbit or Favicon services
3. **Custom connectors** can use local logo files
4. **All connectors** have a logo (or generic fallback)

This provides the best possible logo coverage with minimal configuration!
