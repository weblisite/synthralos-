
-- Batch 8 of 10
-- Migrating 10 connectors

BEGIN;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '7c02d30b-5aad-4823-b9e8-58e78e678fca',
    'reddit',
    'Reddit',
    'beta',
    'f83be2ac-d3e5-47bc-8108-1a02f307dda6',
    '2025-12-19T15:27:14.491322+00:00',
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
    'f83be2ac-d3e5-47bc-8108-1a02f307dda6',
    c.id,
    '1.0.0',
    '{"name": "Reddit", "slug": "reddit", "version": "1.0.0", "description": "Social news and discussion", "category": "Social Media", "status": "beta", "nango": {"enabled": true, "provider_key": "reddit"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/reddit", "token_url": "https://api.nango.dev/oauth/reddit/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.491322+00:00'
FROM connector c
WHERE c.slug = 'reddit' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '5ed966d3-50fe-4985-a453-1c622a75f34e',
    'replicate',
    'Replicate',
    'beta',
    '8f421620-f73c-42ed-a0ec-91aeb88cc67b',
    '2025-12-19T15:27:14.491688+00:00',
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
    '8f421620-f73c-42ed-a0ec-91aeb88cc67b',
    c.id,
    '1.0.0',
    '{"name": "Replicate", "slug": "replicate", "version": "1.0.0", "description": "ML model hosting", "category": "AI & Machine Learning", "status": "beta", "nango": {"enabled": true, "provider_key": "replicate"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/replicate", "token_url": "https://api.nango.dev/oauth/replicate/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.491688+00:00'
FROM connector c
WHERE c.slug = 'replicate' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'd1ed536d-2fad-414f-8207-ce23844c1a79',
    's3-compatible-storage',
    'S3 Compatible Storage',
    'beta',
    '0cbf99bf-f524-4df3-9614-7acdc4bb5563',
    '2025-12-19T15:27:14.492044+00:00',
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
    '0cbf99bf-f524-4df3-9614-7acdc4bb5563',
    c.id,
    '1.0.0',
    '{"name": "S3 Compatible Storage", "slug": "s3-compatible-storage", "version": "1.0.0", "description": "S3-compatible object storage", "category": "File Storage & Cloud", "status": "beta", "nango": {"enabled": true, "provider_key": "s3-compatible"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/s3-compatible", "token_url": "https://api.nango.dev/oauth/s3-compatible/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.492044+00:00'
FROM connector c
WHERE c.slug = 's3-compatible-storage' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '0e2639ac-1065-4609-ae0f-495650a89ebe',
    'salesforce',
    'Salesforce',
    'beta',
    'c096ad80-e5fc-493e-8d83-51f73a1a818a',
    '2025-12-19T15:27:14.492424+00:00',
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
    'c096ad80-e5fc-493e-8d83-51f73a1a818a',
    c.id,
    '1.0.0',
    '{"name": "Salesforce", "slug": "salesforce", "version": "1.0.0", "description": "CRM platform for sales and customer management", "category": "CRM & Sales", "status": "beta", "nango": {"enabled": true, "provider_key": "salesforce"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/salesforce", "token_url": "https://api.nango.dev/oauth/salesforce/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.492424+00:00'
FROM connector c
WHERE c.slug = 'salesforce' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'dcb9a8bd-1aaa-45b9-b25b-d15f4e446abb',
    'segment',
    'Segment',
    'beta',
    '47527ee3-9829-414d-b9ad-3780a962a521',
    '2025-12-19T15:27:14.492733+00:00',
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
    '47527ee3-9829-414d-b9ad-3780a962a521',
    c.id,
    '1.0.0',
    '{"name": "Segment", "slug": "segment", "version": "1.0.0", "description": "Customer data platform", "category": "Analytics & Data", "status": "beta", "nango": {"enabled": true, "provider_key": "segment"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/segment", "token_url": "https://api.nango.dev/oauth/segment/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.492733+00:00'
FROM connector c
WHERE c.slug = 'segment' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '455be262-2f5b-4c06-b2f5-2700aa9ca2ed',
    'sendgrid',
    'SendGrid',
    'beta',
    '38733287-cd00-4f43-9fe1-54c460386a89',
    '2025-12-19T15:27:14.493061+00:00',
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
    '38733287-cd00-4f43-9fe1-54c460386a89',
    c.id,
    '1.0.0',
    '{"name": "SendGrid", "slug": "sendgrid", "version": "1.0.0", "description": "Send transactional emails", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "sendgrid"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/sendgrid", "token_url": "https://api.nango.dev/oauth/sendgrid/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.493061+00:00'
FROM connector c
WHERE c.slug = 'sendgrid' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '63ae665c-b7e9-4664-9b03-3dddd6243159',
    'shopify',
    'Shopify',
    'beta',
    '699a6021-9d6b-474f-bbc9-04bd140126a6',
    '2025-12-19T15:27:14.493396+00:00',
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
    '699a6021-9d6b-474f-bbc9-04bd140126a6',
    c.id,
    '1.0.0',
    '{"name": "Shopify", "slug": "shopify", "version": "1.0.0", "description": "E-commerce platform", "category": "E-commerce & Payments", "status": "beta", "nango": {"enabled": true, "provider_key": "shopify"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/shopify", "token_url": "https://api.nango.dev/oauth/shopify/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.493396+00:00'
FROM connector c
WHERE c.slug = 'shopify' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '4ce49c99-c464-4046-9240-379fb9e6d5ca',
    'smartsheet',
    'Smartsheet',
    'beta',
    '9089db16-a272-486a-8d18-da6f36bf7691',
    '2025-12-19T15:27:14.493730+00:00',
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
    '9089db16-a272-486a-8d18-da6f36bf7691',
    c.id,
    '1.0.0',
    '{"name": "Smartsheet", "slug": "smartsheet", "version": "1.0.0", "description": "Work execution platform", "category": "Project Management", "status": "beta", "nango": {"enabled": true, "provider_key": "smartsheet"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/smartsheet", "token_url": "https://api.nango.dev/oauth/smartsheet/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.493730+00:00'
FROM connector c
WHERE c.slug = 'smartsheet' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '7ce49289-8063-4b05-9a9b-6e289d7844c4',
    'snowflake',
    'Snowflake',
    'beta',
    '7a5aa5da-2659-4438-8bd8-7c22c69bff4a',
    '2025-12-19T15:27:14.494065+00:00',
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
    '7a5aa5da-2659-4438-8bd8-7c22c69bff4a',
    c.id,
    '1.0.0',
    '{"name": "Snowflake", "slug": "snowflake", "version": "1.0.0", "description": "Cloud data warehouse", "category": "Analytics & Data", "status": "beta", "nango": {"enabled": true, "provider_key": "snowflake"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/snowflake", "token_url": "https://api.nango.dev/oauth/snowflake/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.494065+00:00'
FROM connector c
WHERE c.slug = 'snowflake' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '565fe1b7-c3ce-4555-8d15-5ad69fbd0b9d',
    'square',
    'Square',
    'beta',
    'd4c0f974-2337-4eb4-938d-e495dea36502',
    '2025-12-19T15:27:14.494388+00:00',
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
    'd4c0f974-2337-4eb4-938d-e495dea36502',
    c.id,
    '1.0.0',
    '{"name": "Square", "slug": "square", "version": "1.0.0", "description": "Payment processing and POS", "category": "E-commerce & Payments", "status": "beta", "nango": {"enabled": true, "provider_key": "square"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/square", "token_url": "https://api.nango.dev/oauth/square/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.494388+00:00'
FROM connector c
WHERE c.slug = 'square' AND c.is_platform = true
ON CONFLICT DO NOTHING;

COMMIT;

-- Verify this batch
SELECT COUNT(*) as connectors_after_batch FROM connector;
