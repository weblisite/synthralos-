
-- Batch 7 of 10
-- Migrating 10 connectors

BEGIN;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '09d6a694-7129-4c64-aeb8-53d3c6eedb71',
    'notion',
    'Notion',
    'beta',
    '2dceab18-87ee-4764-892d-b4771bb62973',
    '2025-12-19T15:27:14.487734+00:00',
    NULL,
    true,
    NULL
)
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    status = EXCLUDED.status,
    latest_version_id = EXCLUDED.latest_version_id,
    is_platform = true,
    owner_id = NULL,
    created_by = NULL;

INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
SELECT 
    '2dceab18-87ee-4764-892d-b4771bb62973',
    c.id,
    '1.0.0',
    '{"name": "Notion", "slug": "notion", "version": "1.0.0", "description": "All-in-one workspace", "category": "Productivity & Notes", "status": "beta", "nango": {"enabled": true, "provider_key": "notion"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/notion", "token_url": "https://api.nango.dev/oauth/notion/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.487734+00:00'
FROM connector c
WHERE c.slug = 'notion' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '6e6d57f7-0c3a-4ad4-bfdb-ff4e9b23e7ea',
    'onedrive',
    'OneDrive',
    'beta',
    '0329feb4-3db8-4115-afa3-6f8c5f045f86',
    '2025-12-19T15:27:14.488082+00:00',
    NULL,
    true,
    NULL
)
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    status = EXCLUDED.status,
    latest_version_id = EXCLUDED.latest_version_id,
    is_platform = true,
    owner_id = NULL,
    created_by = NULL;

INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
SELECT 
    '0329feb4-3db8-4115-afa3-6f8c5f045f86',
    c.id,
    '1.0.0',
    '{"name": "OneDrive", "slug": "onedrive", "version": "1.0.0", "description": "Microsoft cloud storage", "category": "File Storage & Cloud", "status": "beta", "nango": {"enabled": true, "provider_key": "onedrive"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/onedrive", "token_url": "https://api.nango.dev/oauth/onedrive/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.488082+00:00'
FROM connector c
WHERE c.slug = 'onedrive' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'b54a0419-2c71-4b88-bc51-8105853463d2',
    'openai',
    'OpenAI',
    'beta',
    'fea7b87e-6a3d-4cc7-87e7-5d64c175accb',
    '2025-12-19T15:27:14.488465+00:00',
    NULL,
    true,
    NULL
)
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    status = EXCLUDED.status,
    latest_version_id = EXCLUDED.latest_version_id,
    is_platform = true,
    owner_id = NULL,
    created_by = NULL;

INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
SELECT 
    'fea7b87e-6a3d-4cc7-87e7-5d64c175accb',
    c.id,
    '1.0.0',
    '{"name": "OpenAI", "slug": "openai", "version": "1.0.0", "description": "AI models and APIs", "category": "AI & Machine Learning", "status": "beta", "nango": {"enabled": true, "provider_key": "openai"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/openai", "token_url": "https://api.nango.dev/oauth/openai/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.488465+00:00'
FROM connector c
WHERE c.slug = 'openai' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '0f8f46f8-7d67-41ce-b2f7-e2bd01add009',
    'outlook-calendar',
    'Outlook Calendar',
    'beta',
    '4e810c04-7587-4239-b8e7-9601f204ad9f',
    '2025-12-19T15:27:14.488775+00:00',
    NULL,
    true,
    NULL
)
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    status = EXCLUDED.status,
    latest_version_id = EXCLUDED.latest_version_id,
    is_platform = true,
    owner_id = NULL,
    created_by = NULL;

INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
SELECT 
    '4e810c04-7587-4239-b8e7-9601f204ad9f',
    c.id,
    '1.0.0',
    '{"name": "Outlook Calendar", "slug": "outlook-calendar", "version": "1.0.0", "description": "Microsoft calendar", "category": "Calendar & Scheduling", "status": "beta", "nango": {"enabled": true, "provider_key": "microsoft-calendar"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/microsoft-calendar", "token_url": "https://api.nango.dev/oauth/microsoft-calendar/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.488775+00:00'
FROM connector c
WHERE c.slug = 'outlook-calendar' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '316f55ca-655f-4c76-bb84-b8faf5ed6d3c',
    'paypal',
    'PayPal',
    'beta',
    'd27becb4-e7d7-46ed-927a-56962de6fd2b',
    '2025-12-19T15:27:14.489126+00:00',
    NULL,
    true,
    NULL
)
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    status = EXCLUDED.status,
    latest_version_id = EXCLUDED.latest_version_id,
    is_platform = true,
    owner_id = NULL,
    created_by = NULL;

INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
SELECT 
    'd27becb4-e7d7-46ed-927a-56962de6fd2b',
    c.id,
    '1.0.0',
    '{"name": "PayPal", "slug": "paypal", "version": "1.0.0", "description": "Online payment processing", "category": "E-commerce & Payments", "status": "beta", "nango": {"enabled": true, "provider_key": "paypal"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/paypal", "token_url": "https://api.nango.dev/oauth/paypal/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.489126+00:00'
FROM connector c
WHERE c.slug = 'paypal' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '770f7a8c-324a-4ac6-b599-1625fec6d3e8',
    'pinterest',
    'Pinterest',
    'beta',
    '9281e648-d551-4a99-8129-f9446d8e9225',
    '2025-12-19T15:27:14.489464+00:00',
    NULL,
    true,
    NULL
)
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    status = EXCLUDED.status,
    latest_version_id = EXCLUDED.latest_version_id,
    is_platform = true,
    owner_id = NULL,
    created_by = NULL;

INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
SELECT 
    '9281e648-d551-4a99-8129-f9446d8e9225',
    c.id,
    '1.0.0',
    '{"name": "Pinterest", "slug": "pinterest", "version": "1.0.0", "description": "Image sharing and discovery", "category": "Social Media", "status": "beta", "nango": {"enabled": true, "provider_key": "pinterest"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/pinterest", "token_url": "https://api.nango.dev/oauth/pinterest/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.489464+00:00'
FROM connector c
WHERE c.slug = 'pinterest' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'c19b1ca3-6fe8-4d85-b2dd-b7efc67c7868',
    'pipedrive',
    'Pipedrive',
    'beta',
    '5eea36b0-948c-4e42-8278-3e1fbcf7ad39',
    '2025-12-19T15:27:14.489814+00:00',
    NULL,
    true,
    NULL
)
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    status = EXCLUDED.status,
    latest_version_id = EXCLUDED.latest_version_id,
    is_platform = true,
    owner_id = NULL,
    created_by = NULL;

INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
SELECT 
    '5eea36b0-948c-4e42-8278-3e1fbcf7ad39',
    c.id,
    '1.0.0',
    '{"name": "Pipedrive", "slug": "pipedrive", "version": "1.0.0", "description": "Sales CRM and pipeline management", "category": "CRM & Sales", "status": "beta", "nango": {"enabled": true, "provider_key": "pipedrive"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/pipedrive", "token_url": "https://api.nango.dev/oauth/pipedrive/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.489814+00:00'
FROM connector c
WHERE c.slug = 'pipedrive' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '1357cfe8-00f5-418e-a1a5-c6262faf63de',
    'quickbooks',
    'QuickBooks',
    'beta',
    '0b83c87c-c98b-490e-aac9-2a9338d8ae63',
    '2025-12-19T15:27:14.490164+00:00',
    NULL,
    true,
    NULL
)
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    status = EXCLUDED.status,
    latest_version_id = EXCLUDED.latest_version_id,
    is_platform = true,
    owner_id = NULL,
    created_by = NULL;

INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
SELECT 
    '0b83c87c-c98b-490e-aac9-2a9338d8ae63',
    c.id,
    '1.0.0',
    '{"name": "QuickBooks", "slug": "quickbooks", "version": "1.0.0", "description": "Accounting software", "category": "E-commerce & Payments", "status": "beta", "nango": {"enabled": true, "provider_key": "quickbooks"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/quickbooks", "token_url": "https://api.nango.dev/oauth/quickbooks/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.490164+00:00'
FROM connector c
WHERE c.slug = 'quickbooks' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '5511ebe4-97cc-498a-b6f3-6c0d175855fa',
    'razorpay',
    'Razorpay',
    'beta',
    '524fc97f-4498-4d16-99a1-d45e98c1bcc1',
    '2025-12-19T15:27:14.490548+00:00',
    NULL,
    true,
    NULL
)
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    status = EXCLUDED.status,
    latest_version_id = EXCLUDED.latest_version_id,
    is_platform = true,
    owner_id = NULL,
    created_by = NULL;

INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
SELECT 
    '524fc97f-4498-4d16-99a1-d45e98c1bcc1',
    c.id,
    '1.0.0',
    '{"name": "Razorpay", "slug": "razorpay", "version": "1.0.0", "description": "Payment gateway for India", "category": "E-commerce & Payments", "status": "beta", "nango": {"enabled": true, "provider_key": "razorpay"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/razorpay", "token_url": "https://api.nango.dev/oauth/razorpay/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.490548+00:00'
FROM connector c
WHERE c.slug = 'razorpay' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '0816f354-580d-4157-8f23-7ab75c1609a9',
    'recurly',
    'Recurly',
    'beta',
    '79ad812e-b45c-4983-92d9-3f30167b95c9',
    '2025-12-19T15:27:14.490891+00:00',
    NULL,
    true,
    NULL
)
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    status = EXCLUDED.status,
    latest_version_id = EXCLUDED.latest_version_id,
    is_platform = true,
    owner_id = NULL,
    created_by = NULL;

INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
SELECT 
    '79ad812e-b45c-4983-92d9-3f30167b95c9',
    c.id,
    '1.0.0',
    '{"name": "Recurly", "slug": "recurly", "version": "1.0.0", "description": "Subscription billing platform", "category": "E-commerce & Payments", "status": "beta", "nango": {"enabled": true, "provider_key": "recurly"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/recurly", "token_url": "https://api.nango.dev/oauth/recurly/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.490891+00:00'
FROM connector c
WHERE c.slug = 'recurly' AND c.is_platform = true
ON CONFLICT DO NOTHING;

COMMIT;

-- Verify this batch
SELECT COUNT(*) as connectors_after_batch FROM connector;
