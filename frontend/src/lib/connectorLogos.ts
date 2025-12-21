/**
 * Connector Logo Utility
 *
 * Provides logo URLs for connectors using multiple logo libraries with fallback chain.
 *
 * Logo Library Priority:
 * 1. Simple Icons (2000+ brand icons) - https://cdn.simpleicons.org/
 * 2. Clearbit Logo API (auto-detects from domain) - https://logo.clearbit.com/
 * 3. Favicon.io (favicon-based logos) - https://favicon.io/
 * 4. Local connector logos directory
 */

/**
 * Mapping of connector slugs to domain names for Clearbit Logo API
 * Clearbit uses domain names to fetch logos automatically
 */
const SLUG_TO_DOMAIN_MAP: Record<string, string> = {
  // Google services
  gmail: "gmail.com",
  "google-gmail": "gmail.com",
  "google-drive": "drive.google.com",
  "google-sheets": "sheets.google.com",
  "google-calendar": "calendar.google.com",
  "google-analytics": "analytics.google.com",
  "google-ads": "ads.google.com",
  "google-bigquery": "bigquery.cloud.google.com",
  "google-cloud-storage": "cloud.google.com",
  "google-ai": "ai.google.com",

  // Microsoft services
  "microsoft-outlook": "outlook.com",
  "outlook-calendar": "outlook.com",
  "microsoft-teams": "teams.microsoft.com",
  "microsoft-excel": "office.com",
  "microsoft-word": "office.com",
  "microsoft-powerpoint": "office.com",
  "microsoft-to-do": "todo.microsoft.com",
  onedrive: "onedrive.live.com",
  "azure-blob-storage": "azure.microsoft.com",

  // AWS services
  aws: "aws.amazon.com",
  "amazon-s3": "s3.amazonaws.com",
  "s3-compatible-storage": "s3.amazonaws.com",

  // Cloud platforms
  gcp: "cloud.google.com",
  azure: "azure.microsoft.com",
  heroku: "heroku.com",
  vercel: "vercel.com",
  netlify: "netlify.com",

  // Development tools
  github: "github.com",
  gitlab: "gitlab.com",
  bitbucket: "bitbucket.org",
  "docker-hub": "hub.docker.com",
  kubernetes: "kubernetes.io",
  jenkins: "jenkins.io",
  circleci: "circleci.com",
  "terraform-cloud": "terraform.io",

  // Communication & Collaboration
  slack: "slack.com",
  discord: "discord.com",
  zoom: "zoom.us",
  telegram: "telegram.org",
  "whatsapp-business": "whatsapp.com",
  "monday-com": "monday.com",

  // CRM & Sales
  salesforce: "salesforce.com",
  hubspot: "hubspot.com",
  pipedrive: "pipedrive.com",
  copper: "copper.com",
  close: "close.com",
  insightly: "insightly.com",
  "zoho-crm": "zoho.com",

  // Support & Helpdesk
  zendesk: "zendesk.com",
  intercom: "intercom.com",
  freshdesk: "freshdesk.com",
  "help-scout": "helpscout.com",
  front: "front.com",

  // Payment & E-commerce
  stripe: "stripe.com",
  paypal: "paypal.com",
  shopify: "shopify.com",
  woocommerce: "woocommerce.com",
  square: "squareup.com",
  razorpay: "razorpay.com",
  braintree: "braintree.com",
  recurly: "recurly.com",
  chargebee: "chargebee.com",

  // Social Media
  twitter: "twitter.com",
  linkedin: "linkedin.com",
  facebook: "facebook.com",
  instagram: "instagram.com",
  youtube: "youtube.com",
  tiktok: "tiktok.com",
  reddit: "reddit.com",
  pinterest: "pinterest.com",
  medium: "medium.com",
  buffer: "buffer.com",

  // Productivity & Project Management
  airtable: "airtable.com",
  notion: "notion.so",
  trello: "trello.com",
  asana: "asana.com",
  clickup: "clickup.com",
  todoist: "todoist.com",
  basecamp: "basecamp.com",
  wrike: "wrike.com",
  linear: "linear.app",
  smartsheet: "smartsheet.com",

  // Atlassian
  jira: "atlassian.com",
  confluence: "atlassian.com",

  // Storage & File Sharing
  dropbox: "dropbox.com",
  box: "box.com",
  cloudinary: "cloudinary.com",
  imgur: "imgur.com",

  // Analytics & Data
  segment: "segment.com",
  mixpanel: "mixpanel.com",
  amplitude: "amplitude.com",
  snowflake: "snowflake.com",
  databricks: "databricks.com",
  tableau: "tableau.com",
  looker: "looker.com",
  metabase: "metabase.com",

  // Email & Marketing
  mailchimp: "mailchimp.com",
  sendgrid: "sendgrid.com",
  activecampaign: "activecampaign.com",

  // AI & ML
  openai: "openai.com",
  "anthropic-claude": "anthropic.com",
  cohere: "cohere.com",
  "hugging-face": "huggingface.co",
  replicate: "replicate.com",

  // Other services
  twilio: "twilio.com",
  calendly: "calendly.com",
  doodle: "doodle.com",
  when2meet: "when2meet.com",
  "apple-calendar": "apple.com",
  quickbooks: "quickbooks.intuit.com",
  xero: "xero.com",
}

/**
 * Mapping of connector slugs to Simple Icons names
 * Some connectors have different names in Simple Icons than their slugs
 */
/**
 * Mapping of connector slugs to Simple Icons names
 *
 * Simple Icons uses specific naming conventions:
 * - No hyphens (e.g., "googledrive" not "google-drive")
 * - Lowercase only
 * - Some brands have specific names (e.g., "amazonaws" not "aws")
 *
 * This map handles cases where connector slugs don't match Simple Icons names exactly.
 */
const SLUG_TO_ICON_MAP: Record<string, string> = {
  // Google services
  gmail: "gmail",
  "google-gmail": "gmail",
  "google-drive": "googledrive",
  "google-sheets": "googlesheets",
  "google-calendar": "googlecalendar",
  "google-analytics": "googleanalytics",
  "google-ads": "googleads",
  "google-bigquery": "googlebigquery",
  "google-cloud-storage": "googlecloud",
  "google-ai": "google",

  // Microsoft services
  "microsoft-outlook": "microsoftoutlook",
  "outlook-calendar": "microsoftoutlook",
  "microsoft-teams": "microsoftteams",
  "microsoft-excel": "microsoftexcel",
  "microsoft-word": "microsoftword",
  "microsoft-powerpoint": "microsoftpowerpoint",
  "microsoft-to-do": "microsofttodo",
  onedrive: "onedrive",
  "azure-blob-storage": "microsoftazure",

  // AWS services
  aws: "amazonaws",
  "amazon-s3": "amazons3",
  "s3-compatible-storage": "amazons3",

  // Cloud platforms
  gcp: "googlecloud",
  azure: "microsoftazure",
  heroku: "heroku",
  vercel: "vercel",
  netlify: "netlify",

  // Development tools
  github: "github",
  gitlab: "gitlab",
  bitbucket: "bitbucket",
  "docker-hub": "docker",
  kubernetes: "kubernetes",
  jenkins: "jenkins",
  circleci: "circleci",
  "terraform-cloud": "terraform",

  // Communication & Collaboration
  slack: "slack",
  discord: "discord",
  zoom: "zoom",
  telegram: "telegram",
  "whatsapp-business": "whatsapp",
  "monday-com": "monday",

  // CRM & Sales
  salesforce: "salesforce",
  hubspot: "hubspot",
  pipedrive: "pipedrive",
  copper: "copper",
  close: "close",
  insightly: "insightly",
  "zoho-crm": "zoho",

  // Support & Helpdesk
  zendesk: "zendesk",
  intercom: "intercom",
  freshdesk: "freshdesk",
  "help-scout": "helpscout",
  front: "front",

  // Payment & E-commerce
  stripe: "stripe",
  paypal: "paypal",
  shopify: "shopify",
  woocommerce: "woocommerce",
  square: "square",
  razorpay: "razorpay",
  braintree: "braintree",
  recurly: "recurly",
  chargebee: "chargebee",

  // Social Media
  twitter: "twitter",
  linkedin: "linkedin",
  facebook: "facebook",
  instagram: "instagram",
  youtube: "youtube",
  tiktok: "tiktok",
  reddit: "reddit",
  pinterest: "pinterest",
  medium: "medium",
  buffer: "buffer",

  // Productivity & Project Management
  airtable: "airtable",
  notion: "notion",
  trello: "trello",
  asana: "asana",
  clickup: "clickup",
  todoist: "todoist",
  basecamp: "basecamp",
  wrike: "wrike",
  linear: "linear",
  smartsheet: "smartsheet",

  // Atlassian
  jira: "jira",
  confluence: "confluence",

  // Storage & File Sharing
  dropbox: "dropbox",
  box: "box",
  cloudinary: "cloudinary",
  imgur: "imgur",

  // Analytics & Data
  segment: "segment",
  mixpanel: "mixpanel",
  amplitude: "amplitude",
  snowflake: "snowflake",
  databricks: "databricks",
  tableau: "tableau",
  looker: "looker",
  metabase: "metabase",

  // Email & Marketing
  mailchimp: "mailchimp",
  sendgrid: "sendgrid",
  activecampaign: "activecampaign",

  // AI & ML
  openai: "openai",
  "anthropic-claude": "anthropic",
  cohere: "cohere",
  "hugging-face": "huggingface",
  replicate: "replicate",

  // Other services
  twilio: "twilio",
  calendly: "calendly",
  doodle: "doodle",
  when2meet: "when2meet",
  "apple-calendar": "apple",
  quickbooks: "quickbooks",
  xero: "xero",
}

/**
 * Get Simple Icons name for a connector slug
 *
 * Matching logic:
 * 1. Check explicit mapping first (handles special cases)
 * 2. Try exact slug match (many connectors match exactly)
 * 3. Normalize slug (remove hyphens, lowercase) for Simple Icons format
 *
 * Simple Icons naming conventions:
 * - Lowercase only
 * - No hyphens (e.g., "googledrive" not "google-drive")
 * - Brand-specific names (e.g., "amazonaws" not "aws")
 */
function getSimpleIconName(slug: string): string {
  const lowerSlug = slug.toLowerCase()

  // 1. Check explicit mapping first (handles special cases)
  if (SLUG_TO_ICON_MAP[lowerSlug]) {
    return SLUG_TO_ICON_MAP[lowerSlug]
  }

  // 2. Try exact match (many connectors match Simple Icons names exactly)
  // Simple Icons uses lowercase, no hyphens
  // So "salesforce" → "salesforce" ✓, "slack" → "slack" ✓

  // 3. Normalize slug for Simple Icons format:
  // - Remove hyphens (Simple Icons doesn't use them)
  // - Remove underscores
  // - Remove special characters
  const normalized = lowerSlug
    .replace(/-/g, "") // Remove hyphens
    .replace(/_/g, "") // Remove underscores
    .replace(/[^a-z0-9]/g, "") // Remove any remaining special chars

  return normalized
}

/**
 * Generate logo URLs from Simple Icons library
 */
function getSimpleIconsUrls(iconName: string): string[] {
  return [
    `https://cdn.simpleicons.org/${iconName}/000000`, // Black
    `https://cdn.simpleicons.org/${iconName}/4285F4`, // Blue
    `https://cdn.simpleicons.org/${iconName}/5865F2`, // Discord blue
  ]
}

/**
 * Generate logo URLs from Clearbit Logo API
 * Clearbit automatically fetches logos from company domains
 */
function getClearbitUrls(domain: string): string[] {
  return [
    `https://logo.clearbit.com/${domain}`, // Standard Clearbit logo
  ]
}

/**
 * Generate logo URLs from Favicon.io (favicon-based logos)
 * Uses Google's favicon service as fallback
 */
function getFaviconUrls(domain: string): string[] {
  return [
    `https://www.google.com/s2/favicons?domain=${domain}&sz=128`, // Google favicon service
    `https://icons.duckduckgo.com/ip3/${domain}.ico`, // DuckDuckGo favicon service
  ]
}

/**
 * Get domain name for a connector slug (for Clearbit/Favicon APIs)
 */
function getConnectorDomain(slug: string): string | null {
  const lowerSlug = slug.toLowerCase()

  // Check explicit domain mapping
  if (SLUG_TO_DOMAIN_MAP[lowerSlug]) {
    return SLUG_TO_DOMAIN_MAP[lowerSlug]
  }

  // Try to infer domain from slug
  // Common patterns:
  // - "service-name" → "service-name.com"
  // - "google-service" → "service.google.com"
  // - "microsoft-service" → "service.microsoft.com"

  // Handle common prefixes
  if (lowerSlug.startsWith("google-")) {
    const service = lowerSlug.replace("google-", "")
    return `${service}.google.com`
  }

  if (lowerSlug.startsWith("microsoft-")) {
    const service = lowerSlug.replace("microsoft-", "")
    return `${service}.microsoft.com`
  }

  // Default: try slug as domain
  if (lowerSlug.includes(".")) {
    return lowerSlug // Already looks like a domain
  }

  return `${lowerSlug.replace(/-/g, "")}.com`
}

/**
 * Get logo URL for a connector from multiple libraries
 *
 * @param slug - Connector slug
 * @param customLogo - Optional custom logo URL from manifest
 * @returns Array of logo URLs to try in order (from multiple libraries)
 */
export function getConnectorLogoUrls(
  slug: string,
  customLogo?: string | null,
): string[] {
  const iconName = getSimpleIconName(slug)
  const domain = getConnectorDomain(slug)

  const urls: string[] = []

  // 1. Custom logo from manifest (highest priority)
  if (customLogo) {
    urls.push(customLogo)
  }

  // 2. Simple Icons CDN (Library 1: 2000+ brand icons)
  urls.push(...getSimpleIconsUrls(iconName))

  // 3. Clearbit Logo API (Library 2: Auto-detects from domain)
  if (domain) {
    urls.push(...getClearbitUrls(domain))
  }

  // 4. Favicon.io / Google Favicon Service (Library 3: Favicon-based logos)
  if (domain) {
    urls.push(...getFaviconUrls(domain))
  }

  // 5. Local connector logos directory (fallback)
  urls.push(`/connectors/logos/${slug}.svg`)
  urls.push(`/connectors/logos/${slug}.png`)

  return urls
}

/**
 * Get the primary logo URL for a connector (first in the list)
 */
export function getConnectorLogoUrl(
  slug: string,
  customLogo?: string | null,
): string | null {
  const urls = getConnectorLogoUrls(slug, customLogo)
  return urls[0] || null
}
