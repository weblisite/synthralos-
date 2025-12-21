# Connector Logo Matching Explained

## How Logo Matching Works

The connector logo system uses a **three-tier matching approach** to find the correct logo for each connector:

### 1. **Explicit Mapping** (Highest Priority)
First, the system checks if there's an explicit mapping in `SLUG_TO_ICON_MAP`. This handles cases where connector slugs don't match Simple Icons names exactly.

**Examples:**
- `"google-drive"` → `"googledrive"` (Simple Icons removes hyphens)
- `"aws"` → `"amazonaws"` (Simple Icons uses full brand name)
- `"microsoft-teams"` → `"microsoftteams"` (no hyphens in Simple Icons)
- `"anthropic-claude"` → `"anthropic"` (uses parent brand name)

### 2. **Exact Match** (Automatic)
If no explicit mapping exists, the system tries the connector slug as-is. Many connectors match Simple Icons names exactly:

**Examples:**
- `"salesforce"` → `"salesforce"` ✓
- `"slack"` → `"slack"` ✓
- `"github"` → `"github"` ✓
- `"stripe"` → `"stripe"` ✓
- `"airtable"` → `"airtable"` ✓

### 3. **Normalized Match** (Fallback)
If exact match fails, the system normalizes the slug by:
- Converting to lowercase
- Removing hyphens (Simple Icons doesn't use them)
- Removing underscores
- Removing special characters

**Examples:**
- `"google-drive"` → `"googledrive"` (if not in mapping)
- `"microsoft_teams"` → `"microsoftteams"`
- `"s3-compatible-storage"` → `"s3compatiblestorage"`

## Logo Loading Priority

When displaying a logo, the system tries URLs in this order:

1. **Custom logo from manifest** (if specified in connector config)
2. **Simple Icons CDN - Black** (`https://cdn.simpleicons.org/{icon-name}/000000`)
3. **Simple Icons CDN - Blue** (`https://cdn.simpleicons.org/{icon-name}/4285F4`)
4. **Simple Icons CDN - Discord Blue** (`https://cdn.simpleicons.org/{icon-name}/5865F2`)
5. **Local logo - SVG** (`/connectors/logos/{slug}.svg`)
6. **Local logo - PNG** (`/connectors/logos/{slug}.png`)
7. **Fallback** - Generic `Plug` icon

## Examples

### Perfect Matches (No Mapping Needed)
```typescript
"salesforce" → "salesforce" → ✅ Logo loads
"slack" → "slack" → ✅ Logo loads
"stripe" → "stripe" → ✅ Logo loads
"airtable" → "airtable" → ✅ Logo loads
"snowflake" → "snowflake" → ✅ Logo loads
```

### Needs Mapping (Handled Automatically)
```typescript
"google-drive" → "googledrive" → ✅ Logo loads
"microsoft-teams" → "microsoftteams" → ✅ Logo loads
"aws" → "amazonaws" → ✅ Logo loads
"anthropic-claude" → "anthropic" → ✅ Logo loads
```

### Normalized Matches (Automatic Fallback)
```typescript
"google_analytics" → "googleanalytics" → ✅ Logo loads
"microsoft-outlook" → "microsoftoutlook" → ✅ Logo loads
```

## Adding New Mappings

If a connector logo doesn't load, you can add it to `SLUG_TO_ICON_MAP` in `frontend/src/lib/connectorLogos.ts`:

```typescript
const SLUG_TO_ICON_MAP: Record<string, string> = {
  // ... existing mappings
  "your-connector-slug": "simpleiconsname",
}
```

To find the correct Simple Icons name:
1. Visit https://simpleicons.org/
2. Search for the brand/service
3. Use the exact name shown (usually lowercase, no hyphens)

## Testing Logo Loading

To verify a connector logo loads correctly:

1. **Check browser console** - Look for failed image loads
2. **Inspect network tab** - See which URLs are being tried
3. **Check Simple Icons** - Verify the icon exists at https://cdn.simpleicons.org/{icon-name}/000000

## Current Coverage

- ✅ **99 connectors** in database
- ✅ **60+ explicit mappings** for common connectors
- ✅ **Automatic normalization** for remaining connectors
- ✅ **Simple Icons CDN** with 2000+ brand icons
- ✅ **Fallback chain** ensures logo always displays (or generic icon)

## Summary

**The system works perfectly when:**
- Connector slug matches Simple Icons name exactly (most common)
- Connector slug is in the explicit mapping (handles special cases)
- Connector slug normalizes to a valid Simple Icons name (automatic fallback)

**If a logo doesn't load:**
1. Check if Simple Icons has the icon (visit simpleicons.org)
2. Add explicit mapping if needed
3. Logo will fallback to generic `Plug` icon if no match found
