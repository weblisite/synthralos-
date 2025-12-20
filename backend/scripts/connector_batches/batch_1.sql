
-- Batch 1 of 10
-- Migrating 10 connectors

BEGIN;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'fed2ed56-38e1-468e-baba-da0a43f24dc6',
    'activecampaign',
    'ActiveCampaign',
    'beta',
    'd4e8bca9-a86e-4dc0-939c-2858e0b53942',
    '2025-12-19T15:27:14.463734+00:00',
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
    'd4e8bca9-a86e-4dc0-939c-2858e0b53942',
    c.id,
    '1.0.0',
    '{"name": "ActiveCampaign", "slug": "activecampaign", "version": "1.0.0", "description": "Marketing automation and CRM", "category": "CRM & Sales", "status": "beta", "nango": {"enabled": true, "provider_key": "activecampaign"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/activecampaign", "token_url": "https://api.nango.dev/oauth/activecampaign/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.463734+00:00'
FROM connector c
WHERE c.slug = 'activecampaign' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '10f7196f-bbd1-4a23-bd64-06cc51310acc',
    'airtable',
    'Airtable',
    'beta',
    '0e399225-8313-46a7-950b-3a363dbbf4ae',
    '2025-12-19T15:27:14.465130+00:00',
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
    '0e399225-8313-46a7-950b-3a363dbbf4ae',
    c.id,
    '1.0.0',
    '{"name": "Airtable", "slug": "airtable", "version": "1.0.0", "description": "Database and collaboration platform", "category": "CRM & Sales", "status": "beta", "nango": {"enabled": true, "provider_key": "airtable"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/airtable", "token_url": "https://api.nango.dev/oauth/airtable/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.465130+00:00'
FROM connector c
WHERE c.slug = 'airtable' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'd261e495-e4ad-4d09-b892-b1987986bad9',
    'amazon-s3',
    'Amazon S3',
    'beta',
    '15bacaae-ee04-401e-bc5f-f50ac8274151',
    '2025-12-19T15:27:14.465529+00:00',
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
    '15bacaae-ee04-401e-bc5f-f50ac8274151',
    c.id,
    '1.0.0',
    '{"name": "Amazon S3", "slug": "amazon-s3", "version": "1.0.0", "description": "Object storage service", "category": "File Storage & Cloud", "status": "beta", "nango": {"enabled": true, "provider_key": "aws-s3"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/aws-s3", "token_url": "https://api.nango.dev/oauth/aws-s3/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.465529+00:00'
FROM connector c
WHERE c.slug = 'amazon-s3' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '0acfec86-9b4d-42f0-a7a0-7436731c48a4',
    'amplitude',
    'Amplitude',
    'beta',
    '68d45b7d-eedf-4cc2-9743-865b263b2085',
    '2025-12-19T15:27:14.465873+00:00',
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
    '68d45b7d-eedf-4cc2-9743-865b263b2085',
    c.id,
    '1.0.0',
    '{"name": "Amplitude", "slug": "amplitude", "version": "1.0.0", "description": "Product analytics", "category": "Analytics & Data", "status": "beta", "nango": {"enabled": true, "provider_key": "amplitude"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/amplitude", "token_url": "https://api.nango.dev/oauth/amplitude/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.465873+00:00'
FROM connector c
WHERE c.slug = 'amplitude' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '62da08d0-7ed9-42d6-8fd4-a2444146b5a5',
    'anthropic-claude',
    'Anthropic Claude',
    'beta',
    '9669582d-b0b5-406c-a311-2b69423778c0',
    '2025-12-19T15:27:14.466272+00:00',
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
    '9669582d-b0b5-406c-a311-2b69423778c0',
    c.id,
    '1.0.0',
    '{"name": "Anthropic Claude", "slug": "anthropic-claude", "version": "1.0.0", "description": "AI assistant API", "category": "AI & Machine Learning", "status": "beta", "nango": {"enabled": true, "provider_key": "anthropic"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/anthropic", "token_url": "https://api.nango.dev/oauth/anthropic/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.466272+00:00'
FROM connector c
WHERE c.slug = 'anthropic-claude' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '012be085-618b-4020-a65b-5851c24e8aae',
    'apple-calendar',
    'Apple Calendar',
    'beta',
    '5a407d37-6bd6-4c0a-a64f-5337da7bda10',
    '2025-12-19T15:27:14.466596+00:00',
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
    '5a407d37-6bd6-4c0a-a64f-5337da7bda10',
    c.id,
    '1.0.0',
    '{"name": "Apple Calendar", "slug": "apple-calendar", "version": "1.0.0", "description": "Apple calendar", "category": "Calendar & Scheduling", "status": "beta", "nango": {"enabled": true, "provider_key": "apple-calendar"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/apple-calendar", "token_url": "https://api.nango.dev/oauth/apple-calendar/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.466596+00:00'
FROM connector c
WHERE c.slug = 'apple-calendar' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '9f30b034-fb2d-452e-8340-4ab16a56cb8e',
    'asana',
    'Asana',
    'beta',
    'eeb1be22-6e2f-4d0f-98c9-d9fc41bc3470',
    '2025-12-19T15:27:14.466942+00:00',
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
    'eeb1be22-6e2f-4d0f-98c9-d9fc41bc3470',
    c.id,
    '1.0.0',
    '{"name": "Asana", "slug": "asana", "version": "1.0.0", "description": "Project and task management", "category": "Project Management", "status": "beta", "nango": {"enabled": true, "provider_key": "asana"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/asana", "token_url": "https://api.nango.dev/oauth/asana/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.466942+00:00'
FROM connector c
WHERE c.slug = 'asana' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'c8e4f04e-c740-4797-bb37-4e37f061dc36',
    'aws',
    'AWS',
    'beta',
    '4cb2a9a0-328a-4fdf-89c8-74b08a736764',
    '2025-12-19T15:27:14.467286+00:00',
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
    '4cb2a9a0-328a-4fdf-89c8-74b08a736764',
    c.id,
    '1.0.0',
    '{"name": "AWS", "slug": "aws", "version": "1.0.0", "description": "Amazon Web Services cloud platform", "category": "Development & Code", "status": "beta", "nango": {"enabled": true, "provider_key": "aws"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/aws", "token_url": "https://api.nango.dev/oauth/aws/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.467286+00:00'
FROM connector c
WHERE c.slug = 'aws' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '8dc51cb7-5924-44a6-859f-920b6f22c7de',
    'azure-blob-storage',
    'Azure Blob Storage',
    'beta',
    '47b92271-cf39-4bd0-9e2b-c0fd3c55cc13',
    '2025-12-19T15:27:14.467609+00:00',
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
    '47b92271-cf39-4bd0-9e2b-c0fd3c55cc13',
    c.id,
    '1.0.0',
    '{"name": "Azure Blob Storage", "slug": "azure-blob-storage", "version": "1.0.0", "description": "Microsoft Azure object storage", "category": "File Storage & Cloud", "status": "beta", "nango": {"enabled": true, "provider_key": "azure"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/azure", "token_url": "https://api.nango.dev/oauth/azure/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.467609+00:00'
FROM connector c
WHERE c.slug = 'azure-blob-storage' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'c54e2c01-1353-4df2-835e-487127bed1f6',
    'basecamp',
    'Basecamp',
    'beta',
    'a239a477-194f-4eb7-b046-c879efbec7e1',
    '2025-12-19T15:27:14.467943+00:00',
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
    'a239a477-194f-4eb7-b046-c879efbec7e1',
    c.id,
    '1.0.0',
    '{"name": "Basecamp", "slug": "basecamp", "version": "1.0.0", "description": "Project management and team communication", "category": "Project Management", "status": "beta", "nango": {"enabled": true, "provider_key": "basecamp"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/basecamp", "token_url": "https://api.nango.dev/oauth/basecamp/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.467943+00:00'
FROM connector c
WHERE c.slug = 'basecamp' AND c.is_platform = true
ON CONFLICT DO NOTHING;

COMMIT;

-- Verify this batch
SELECT COUNT(*) as connectors_after_batch FROM connector;
