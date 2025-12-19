
-- Batch 10 of 10
-- Migrating 9 connectors

BEGIN;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '6e627e5f-56d6-4e37-b798-09e80191f38c',
    'whatsapp-business',
    'WhatsApp Business',
    'beta',
    'e074b3f9-d982-4bcd-af86-a52933ce5c29',
    '2025-12-19T15:27:14.499970+00:00',
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
    'e074b3f9-d982-4bcd-af86-a52933ce5c29',
    c.id,
    '1.0.0',
    '{"name": "WhatsApp Business", "slug": "whatsapp-business", "version": "1.0.0", "description": "Send WhatsApp messages", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "whatsapp"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/whatsapp", "token_url": "https://api.nango.dev/oauth/whatsapp/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.499970+00:00'
FROM connector c
WHERE c.slug = 'whatsapp-business' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '0afff935-9e84-48e8-8057-43f9c86db72b',
    'when2meet',
    'When2Meet',
    'beta',
    'e5538c49-1b27-4391-a63e-58d7433b8eec',
    '2025-12-19T15:27:14.500333+00:00',
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
    'e5538c49-1b27-4391-a63e-58d7433b8eec',
    c.id,
    '1.0.0',
    '{"name": "When2Meet", "slug": "when2meet", "version": "1.0.0", "description": "Meeting scheduling", "category": "Productivity & Notes", "status": "beta", "nango": {"enabled": true, "provider_key": "when2meet"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/when2meet", "token_url": "https://api.nango.dev/oauth/when2meet/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.500333+00:00'
FROM connector c
WHERE c.slug = 'when2meet' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '7b11154a-e108-4dc5-baa1-a2009ceedc63',
    'woocommerce',
    'WooCommerce',
    'beta',
    'ed1a25c0-ecbb-4cdc-9ac5-41b3dd4070d9',
    '2025-12-19T15:27:14.500690+00:00',
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
    'ed1a25c0-ecbb-4cdc-9ac5-41b3dd4070d9',
    c.id,
    '1.0.0',
    '{"name": "WooCommerce", "slug": "woocommerce", "version": "1.0.0", "description": "WordPress e-commerce plugin", "category": "E-commerce & Payments", "status": "beta", "nango": {"enabled": true, "provider_key": "woocommerce"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/woocommerce", "token_url": "https://api.nango.dev/oauth/woocommerce/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.500690+00:00'
FROM connector c
WHERE c.slug = 'woocommerce' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '03a367d4-8b78-4e9d-b76b-6a27a290e84f',
    'wrike',
    'Wrike',
    'beta',
    '552a90bf-81fa-482c-a06f-f9eada9a2184',
    '2025-12-19T15:27:14.501025+00:00',
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
    '552a90bf-81fa-482c-a06f-f9eada9a2184',
    c.id,
    '1.0.0',
    '{"name": "Wrike", "slug": "wrike", "version": "1.0.0", "description": "Work management and collaboration", "category": "Project Management", "status": "beta", "nango": {"enabled": true, "provider_key": "wrike"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/wrike", "token_url": "https://api.nango.dev/oauth/wrike/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.501025+00:00'
FROM connector c
WHERE c.slug = 'wrike' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '88093f01-7ece-49dd-b51a-f316aa4e3b55',
    'xero',
    'Xero',
    'beta',
    '42949d39-7b23-4df5-ac06-fe5e8919e849',
    '2025-12-19T15:27:14.501357+00:00',
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
    '42949d39-7b23-4df5-ac06-fe5e8919e849',
    c.id,
    '1.0.0',
    '{"name": "Xero", "slug": "xero", "version": "1.0.0", "description": "Cloud accounting platform", "category": "E-commerce & Payments", "status": "beta", "nango": {"enabled": true, "provider_key": "xero"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/xero", "token_url": "https://api.nango.dev/oauth/xero/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.501357+00:00'
FROM connector c
WHERE c.slug = 'xero' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '2b2871c1-4eaf-45be-ba69-52cd3e650150',
    'youtube',
    'YouTube',
    'beta',
    'b067badf-de8c-400f-b9ef-4df1e6908ac3',
    '2025-12-19T15:27:14.501711+00:00',
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
    'b067badf-de8c-400f-b9ef-4df1e6908ac3',
    c.id,
    '1.0.0',
    '{"name": "YouTube", "slug": "youtube", "version": "1.0.0", "description": "Video sharing platform", "category": "Social Media", "status": "beta", "nango": {"enabled": true, "provider_key": "youtube"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/youtube", "token_url": "https://api.nango.dev/oauth/youtube/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.501711+00:00'
FROM connector c
WHERE c.slug = 'youtube' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '4c0875b7-bbcc-4e0e-a159-339bad76e71e',
    'zendesk',
    'Zendesk',
    'beta',
    '6a2dae51-b0f3-4cfa-8af7-436f00f1a002',
    '2025-12-19T15:27:14.502024+00:00',
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
    '6a2dae51-b0f3-4cfa-8af7-436f00f1a002',
    c.id,
    '1.0.0',
    '{"name": "Zendesk", "slug": "zendesk", "version": "1.0.0", "description": "Manage support tickets", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "zendesk"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/zendesk", "token_url": "https://api.nango.dev/oauth/zendesk/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.502024+00:00'
FROM connector c
WHERE c.slug = 'zendesk' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '6f871094-e023-476d-891f-0f99a198769c',
    'zoho-crm',
    'Zoho CRM',
    'beta',
    '0cf6d9f3-15b9-4bc6-8a61-41e4c38284dd',
    '2025-12-19T15:27:14.503090+00:00',
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
    '0cf6d9f3-15b9-4bc6-8a61-41e4c38284dd',
    c.id,
    '1.0.0',
    '{"name": "Zoho CRM", "slug": "zoho-crm", "version": "1.0.0", "description": "Cloud-based CRM platform", "category": "CRM & Sales", "status": "beta", "nango": {"enabled": true, "provider_key": "zoho"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/zoho", "token_url": "https://api.nango.dev/oauth/zoho/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.503090+00:00'
FROM connector c
WHERE c.slug = 'zoho-crm' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '884f51dd-eee5-432d-8441-bfd430803eeb',
    'zoom',
    'Zoom',
    'beta',
    'ca700608-c80b-43fc-9381-bebb2693fb01',
    '2025-12-19T15:27:14.503523+00:00',
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
    'ca700608-c80b-43fc-9381-bebb2693fb01',
    c.id,
    '1.0.0',
    '{"name": "Zoom", "slug": "zoom", "version": "1.0.0", "description": "Create and manage Zoom meetings", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "zoom"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/zoom", "token_url": "https://api.nango.dev/oauth/zoom/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.503523+00:00'
FROM connector c
WHERE c.slug = 'zoom' AND c.is_platform = true
ON CONFLICT DO NOTHING;

COMMIT;

-- Verify this batch
SELECT COUNT(*) as connectors_after_batch FROM connector;
