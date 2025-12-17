"""
Script to create all 100 connector manifests and register them.

Generates connector manifest JSON files for all supported SaaS integrations.
"""

import json
from pathlib import Path

# Base directory for manifests
MANIFESTS_DIR = Path(__file__).parent.parent / "app" / "connectors" / "manifests"
MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)

# Nango provider key mapping (maps connector slug to Nango provider key)
NANGO_PROVIDER_KEYS = {
    # Communication & Collaboration
    "gmail": "gmail",
    "microsoft-teams": "microsoft-teams",
    "discord": "discord",
    "zoom": "zoom",
    "twilio": "twilio",
    "sendgrid": "sendgrid",
    "mailchimp": "mailchimp",
    "whatsapp-business": "whatsapp",
    "telegram": "telegram",
    "intercom": "intercom",
    "zendesk": "zendesk",
    "freshdesk": "freshdesk",
    "help-scout": "helpscout",
    "front": "front",
    "calendly": "calendly",
    # CRM & Sales
    "salesforce": "salesforce",
    "hubspot": "hubspot",
    "pipedrive": "pipedrive",
    "close": "close",
    "copper": "copper",
    "insightly": "insightly",
    "activecampaign": "activecampaign",
    "monday-com": "monday",
    "airtable": "airtable",
    "zoho-crm": "zoho",
    # Project Management
    "asana": "asana",
    "trello": "trello",
    "jira": "jira",
    "linear": "linear",
    "clickup": "clickup",
    "basecamp": "basecamp",
    "wrike": "wrike",
    "smartsheet": "smartsheet",
    "todoist": "todoist",
    "microsoft-to-do": "microsoft-todo",
    # File Storage & Cloud
    "google-drive": "google-drive",
    "dropbox": "dropbox",
    "box": "box",
    "onedrive": "onedrive",
    "amazon-s3": "aws-s3",
    "azure-blob-storage": "azure",
    "google-cloud-storage": "gcs",
    "cloudinary": "cloudinary",
    "imgur": "imgur",
    "s3-compatible-storage": "s3-compatible",
    # E-commerce & Payments
    "shopify": "shopify",
    "woocommerce": "woocommerce",
    "paypal": "paypal",
    "square": "square",
    "quickbooks": "quickbooks",
    "xero": "xero",
    "recurly": "recurly",
    "chargebee": "chargebee",
    "braintree": "braintree",
    "razorpay": "razorpay",
    # Social Media
    "twitter": "twitter",
    "facebook": "facebook",
    "instagram": "instagram",
    "linkedin": "linkedin",
    "youtube": "youtube",
    "tiktok": "tiktok",
    "pinterest": "pinterest",
    "reddit": "reddit",
    "medium": "medium",
    "buffer": "buffer",
    # Analytics & Data
    "google-analytics": "google-analytics",
    "mixpanel": "mixpanel",
    "amplitude": "amplitude",
    "segment": "segment",
    "snowflake": "snowflake",
    "google-bigquery": "bigquery",
    "tableau": "tableau",
    "looker": "looker",
    "databricks": "databricks",
    "metabase": "metabase",
    # Development & Code
    "github": "github",
    "gitlab": "gitlab",
    "bitbucket": "bitbucket",
    "circleci": "circleci",
    "jenkins": "jenkins",
    "vercel": "vercel",
    "netlify": "netlify",
    "docker-hub": "docker",
    "kubernetes": "kubernetes",
    "terraform-cloud": "terraform",
    "aws": "aws",
    # AI & Machine Learning
    "openai": "openai",
    "anthropic-claude": "anthropic",
    "google-ai": "google-ai",
    "cohere": "cohere",
    "hugging-face": "huggingface",
    "replicate": "replicate",
    # Productivity & Notes
    "notion": "notion",
    "when2meet": "when2meet",
    # Calendar & Scheduling
    "google-calendar": "google-calendar",
    "outlook-calendar": "microsoft-calendar",
    "apple-calendar": "apple-calendar",
    "doodle": "doodle",
    # Payments
    "stripe": "stripe",
}

# Connector definitions
CONNECTORS = [
    # Communication & Collaboration (15)
    {"slug": "gmail", "name": "Gmail", "category": "Communication & Collaboration", "description": "Send and receive emails via Gmail API"},
    {"slug": "microsoft-teams", "name": "Microsoft Teams", "category": "Communication & Collaboration", "description": "Send messages and manage Teams channels"},
    {"slug": "discord", "name": "Discord", "category": "Communication & Collaboration", "description": "Send messages and manage Discord servers"},
    {"slug": "zoom", "name": "Zoom", "category": "Communication & Collaboration", "description": "Create and manage Zoom meetings"},
    {"slug": "twilio", "name": "Twilio", "category": "Communication & Collaboration", "description": "Send SMS and make phone calls"},
    {"slug": "sendgrid", "name": "SendGrid", "category": "Communication & Collaboration", "description": "Send transactional emails"},
    {"slug": "mailchimp", "name": "Mailchimp", "category": "Communication & Collaboration", "description": "Manage email campaigns and subscribers"},
    {"slug": "whatsapp-business", "name": "WhatsApp Business", "category": "Communication & Collaboration", "description": "Send WhatsApp messages"},
    {"slug": "telegram", "name": "Telegram", "category": "Communication & Collaboration", "description": "Send Telegram messages"},
    {"slug": "intercom", "name": "Intercom", "category": "Communication & Collaboration", "description": "Manage customer conversations"},
    {"slug": "zendesk", "name": "Zendesk", "category": "Communication & Collaboration", "description": "Manage support tickets"},
    {"slug": "freshdesk", "name": "Freshdesk", "category": "Communication & Collaboration", "description": "Customer support platform"},
    {"slug": "help-scout", "name": "Help Scout", "category": "Communication & Collaboration", "description": "Customer support and help desk"},
    {"slug": "front", "name": "Front", "category": "Communication & Collaboration", "description": "Shared inbox and customer communication"},
    {"slug": "calendly", "name": "Calendly", "category": "Communication & Collaboration", "description": "Schedule meetings and appointments"},
    
    # CRM & Sales (10)
    {"slug": "salesforce", "name": "Salesforce", "category": "CRM & Sales", "description": "CRM platform for sales and customer management"},
    {"slug": "hubspot", "name": "HubSpot", "category": "CRM & Sales", "description": "Marketing, sales, and service platform"},
    {"slug": "pipedrive", "name": "Pipedrive", "category": "CRM & Sales", "description": "Sales CRM and pipeline management"},
    {"slug": "close", "name": "Close", "category": "CRM & Sales", "description": "Inside sales CRM"},
    {"slug": "copper", "name": "Copper", "category": "CRM & Sales", "description": "CRM built for Google Workspace"},
    {"slug": "insightly", "name": "Insightly", "category": "CRM & Sales", "description": "CRM and project management"},
    {"slug": "activecampaign", "name": "ActiveCampaign", "category": "CRM & Sales", "description": "Marketing automation and CRM"},
    {"slug": "monday-com", "name": "Monday.com", "category": "CRM & Sales", "description": "Work management platform"},
    {"slug": "airtable", "name": "Airtable", "category": "CRM & Sales", "description": "Database and collaboration platform"},
    {"slug": "zoho-crm", "name": "Zoho CRM", "category": "CRM & Sales", "description": "Cloud-based CRM platform"},
    
    # Project Management (10)
    {"slug": "asana", "name": "Asana", "category": "Project Management", "description": "Project and task management"},
    {"slug": "trello", "name": "Trello", "category": "Project Management", "description": "Kanban board project management"},
    {"slug": "jira", "name": "Jira", "category": "Project Management", "description": "Issue tracking and project management"},
    {"slug": "linear", "name": "Linear", "category": "Project Management", "description": "Issue tracking for software teams"},
    {"slug": "clickup", "name": "ClickUp", "category": "Project Management", "description": "All-in-one productivity platform"},
    {"slug": "basecamp", "name": "Basecamp", "category": "Project Management", "description": "Project management and team communication"},
    {"slug": "wrike", "name": "Wrike", "category": "Project Management", "description": "Work management and collaboration"},
    {"slug": "smartsheet", "name": "Smartsheet", "category": "Project Management", "description": "Work execution platform"},
    {"slug": "todoist", "name": "Todoist", "category": "Project Management", "description": "Task management and to-do lists"},
    {"slug": "microsoft-to-do", "name": "Microsoft To Do", "category": "Project Management", "description": "Task management app"},
    
    # File Storage & Cloud (10)
    {"slug": "google-drive", "name": "Google Drive", "category": "File Storage & Cloud", "description": "Cloud file storage and sharing"},
    {"slug": "dropbox", "name": "Dropbox", "category": "File Storage & Cloud", "description": "Cloud file storage"},
    {"slug": "box", "name": "Box", "category": "File Storage & Cloud", "description": "Cloud content management"},
    {"slug": "onedrive", "name": "OneDrive", "category": "File Storage & Cloud", "description": "Microsoft cloud storage"},
    {"slug": "amazon-s3", "name": "Amazon S3", "category": "File Storage & Cloud", "description": "Object storage service"},
    {"slug": "azure-blob-storage", "name": "Azure Blob Storage", "category": "File Storage & Cloud", "description": "Microsoft Azure object storage"},
    {"slug": "google-cloud-storage", "name": "Google Cloud Storage", "category": "File Storage & Cloud", "description": "Google Cloud object storage"},
    {"slug": "cloudinary", "name": "Cloudinary", "category": "File Storage & Cloud", "description": "Image and video management"},
    {"slug": "imgur", "name": "Imgur", "category": "File Storage & Cloud", "description": "Image hosting and sharing"},
    {"slug": "s3-compatible-storage", "name": "S3 Compatible Storage", "category": "File Storage & Cloud", "description": "S3-compatible object storage"},
    
    # E-commerce & Payments (10)
    {"slug": "shopify", "name": "Shopify", "category": "E-commerce & Payments", "description": "E-commerce platform"},
    {"slug": "woocommerce", "name": "WooCommerce", "category": "E-commerce & Payments", "description": "WordPress e-commerce plugin"},
    {"slug": "paypal", "name": "PayPal", "category": "E-commerce & Payments", "description": "Online payment processing"},
    {"slug": "square", "name": "Square", "category": "E-commerce & Payments", "description": "Payment processing and POS"},
    {"slug": "quickbooks", "name": "QuickBooks", "category": "E-commerce & Payments", "description": "Accounting software"},
    {"slug": "xero", "name": "Xero", "category": "E-commerce & Payments", "description": "Cloud accounting platform"},
    {"slug": "recurly", "name": "Recurly", "category": "E-commerce & Payments", "description": "Subscription billing platform"},
    {"slug": "chargebee", "name": "Chargebee", "category": "E-commerce & Payments", "description": "Subscription management"},
    {"slug": "braintree", "name": "Braintree", "category": "E-commerce & Payments", "description": "Payment gateway"},
    {"slug": "razorpay", "name": "Razorpay", "category": "E-commerce & Payments", "description": "Payment gateway for India"},
    
    # Social Media (10)
    {"slug": "twitter", "name": "Twitter / X", "category": "Social Media", "description": "Social media platform"},
    {"slug": "facebook", "name": "Facebook", "category": "Social Media", "description": "Social media platform"},
    {"slug": "instagram", "name": "Instagram", "category": "Social Media", "description": "Photo and video sharing"},
    {"slug": "linkedin", "name": "LinkedIn", "category": "Social Media", "description": "Professional networking"},
    {"slug": "youtube", "name": "YouTube", "category": "Social Media", "description": "Video sharing platform"},
    {"slug": "tiktok", "name": "TikTok", "category": "Social Media", "description": "Short-form video platform"},
    {"slug": "pinterest", "name": "Pinterest", "category": "Social Media", "description": "Image sharing and discovery"},
    {"slug": "reddit", "name": "Reddit", "category": "Social Media", "description": "Social news and discussion"},
    {"slug": "medium", "name": "Medium", "category": "Social Media", "description": "Online publishing platform"},
    {"slug": "buffer", "name": "Buffer", "category": "Social Media", "description": "Social media management"},
    
    # Analytics & Data (10)
    {"slug": "google-analytics", "name": "Google Analytics", "category": "Analytics & Data", "description": "Web analytics platform"},
    {"slug": "mixpanel", "name": "Mixpanel", "category": "Analytics & Data", "description": "Product analytics"},
    {"slug": "amplitude", "name": "Amplitude", "category": "Analytics & Data", "description": "Product analytics"},
    {"slug": "segment", "name": "Segment", "category": "Analytics & Data", "description": "Customer data platform"},
    {"slug": "snowflake", "name": "Snowflake", "category": "Analytics & Data", "description": "Cloud data warehouse"},
    {"slug": "google-bigquery", "name": "Google BigQuery", "category": "Analytics & Data", "description": "Cloud data warehouse"},
    {"slug": "tableau", "name": "Tableau", "category": "Analytics & Data", "description": "Data visualization"},
    {"slug": "looker", "name": "Looker", "category": "Analytics & Data", "description": "Business intelligence"},
    {"slug": "databricks", "name": "Databricks", "category": "Analytics & Data", "description": "Data analytics platform"},
    {"slug": "metabase", "name": "Metabase", "category": "Analytics & Data", "description": "Business intelligence tool"},
    
    # Development & Code (11)
    {"slug": "github", "name": "GitHub", "category": "Development & Code", "description": "Code hosting and version control"},
    {"slug": "gitlab", "name": "GitLab", "category": "Development & Code", "description": "DevOps platform"},
    {"slug": "bitbucket", "name": "Bitbucket", "category": "Development & Code", "description": "Git code hosting"},
    {"slug": "circleci", "name": "CircleCI", "category": "Development & Code", "description": "CI/CD platform"},
    {"slug": "jenkins", "name": "Jenkins", "category": "Development & Code", "description": "CI/CD automation server"},
    {"slug": "vercel", "name": "Vercel", "category": "Development & Code", "description": "Frontend deployment platform"},
    {"slug": "netlify", "name": "Netlify", "category": "Development & Code", "description": "Web development platform"},
    {"slug": "docker-hub", "name": "Docker Hub", "category": "Development & Code", "description": "Container registry"},
    {"slug": "kubernetes", "name": "Kubernetes", "category": "Development & Code", "description": "Container orchestration"},
    {"slug": "terraform-cloud", "name": "Terraform Cloud", "category": "Development & Code", "description": "Infrastructure as code"},
    {"slug": "aws", "name": "AWS", "category": "Development & Code", "description": "Amazon Web Services cloud platform"},
    
    # AI & Machine Learning (6)
    {"slug": "openai", "name": "OpenAI", "category": "AI & Machine Learning", "description": "AI models and APIs"},
    {"slug": "anthropic-claude", "name": "Anthropic Claude", "category": "AI & Machine Learning", "description": "AI assistant API"},
    {"slug": "google-ai", "name": "Google AI", "category": "AI & Machine Learning", "description": "Google AI services"},
    {"slug": "cohere", "name": "Cohere", "category": "AI & Machine Learning", "description": "NLP and language models"},
    {"slug": "hugging-face", "name": "Hugging Face", "category": "AI & Machine Learning", "description": "ML model hosting"},
    {"slug": "replicate", "name": "Replicate", "category": "AI & Machine Learning", "description": "ML model hosting"},
    
    # Productivity & Notes (2)
    {"slug": "notion", "name": "Notion", "category": "Productivity & Notes", "description": "All-in-one workspace"},
    {"slug": "when2meet", "name": "When2Meet", "category": "Productivity & Notes", "description": "Meeting scheduling"},
    
    # Calendar & Scheduling (4)
    {"slug": "google-calendar", "name": "Google Calendar", "category": "Calendar & Scheduling", "description": "Calendar and scheduling"},
    {"slug": "outlook-calendar", "name": "Outlook Calendar", "category": "Calendar & Scheduling", "description": "Microsoft calendar"},
    {"slug": "apple-calendar", "name": "Apple Calendar", "category": "Calendar & Scheduling", "description": "Apple calendar"},
    {"slug": "doodle", "name": "Doodle", "category": "Calendar & Scheduling", "description": "Meeting scheduling"},
    
    # Payments (1)
    {"slug": "stripe", "name": "Stripe", "category": "Payments", "description": "Payment processing platform"},
]


def create_manifest(connector: dict) -> dict:
    """Create a connector manifest."""
    slug = connector["slug"]
    nango_provider_key = NANGO_PROVIDER_KEYS.get(slug, slug)
    
    manifest = {
        "name": connector["name"],
        "slug": slug,
        "version": "1.0.0",
        "description": connector["description"],
        "category": connector["category"],
        "status": "beta",
        "nango": {
            "enabled": True,
            "provider_key": nango_provider_key,
        },
        "oauth": {
            "authorization_url": f"https://api.nango.dev/oauth/{nango_provider_key}",
            "token_url": f"https://api.nango.dev/oauth/{nango_provider_key}/token",
            "default_scopes": [],
            "authorization_params": {},
        },
        "actions": {
            "test_connection": {
                "name": "Test Connection",
                "description": "Test the connection to the service",
                "method": "GET",
                "endpoint": "/test",
            },
        },
        "triggers": {},
    }
    
    return manifest


def main():
    """Create all connector manifests."""
    print(f"Creating connector manifests in {MANIFESTS_DIR}")
    print(f"Total connectors: {len(CONNECTORS)}\n")
    
    created_count = 0
    skipped_count = 0
    
    for connector in CONNECTORS:
        manifest = create_manifest(connector)
        manifest_file = MANIFESTS_DIR / f"{connector['slug']}.json"
        
        # Check if file already exists
        if manifest_file.exists():
            print(f"⏭️  Skipped {connector['name']} ({connector['slug']}) - already exists")
            skipped_count += 1
            continue
        
        with open(manifest_file, "w") as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✅ Created manifest for {connector['name']} ({connector['slug']})")
        created_count += 1
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Created: {created_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Total: {len(CONNECTORS)}")
    print(f"{'='*60}")
    print(f"\nManifests saved to: {MANIFESTS_DIR}")
    print(f"\nTo register these connectors, use the /api/v1/connectors/register endpoint")
    print(f"or run: python backend/scripts/register_connectors.py")


if __name__ == "__main__":
    main()

