
-- Batch 3 of 10
-- Migrating 10 connectors

BEGIN;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '9c00c07c-6f75-4bbd-b3b7-0d771225c12a',
    'cohere',
    'Cohere',
    'beta',
    'e81e9fb3-2b31-4ff7-8889-b6cf16e7bd3f',
    '2025-12-19T15:27:14.472769+00:00',
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
    'e81e9fb3-2b31-4ff7-8889-b6cf16e7bd3f',
    c.id,
    '1.0.0',
    '{"name": "Cohere", "slug": "cohere", "version": "1.0.0", "description": "NLP and language models", "category": "AI & Machine Learning", "status": "beta", "nango": {"enabled": true, "provider_key": "cohere"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/cohere", "token_url": "https://api.nango.dev/oauth/cohere/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.472769+00:00'
FROM connector c
WHERE c.slug = 'cohere' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'e53d7217-ce94-4f39-aff5-10ad2e4bebb9',
    'copper',
    'Copper',
    'beta',
    'bca28141-a65d-46b3-acf4-78590cc1588e',
    '2025-12-19T15:27:14.473333+00:00',
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
    'bca28141-a65d-46b3-acf4-78590cc1588e',
    c.id,
    '1.0.0',
    '{"name": "Copper", "slug": "copper", "version": "1.0.0", "description": "CRM built for Google Workspace", "category": "CRM & Sales", "status": "beta", "nango": {"enabled": true, "provider_key": "copper"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/copper", "token_url": "https://api.nango.dev/oauth/copper/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.473333+00:00'
FROM connector c
WHERE c.slug = 'copper' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '95db4919-2dd4-4cf0-bd0e-0a15f361bebc',
    'databricks',
    'Databricks',
    'beta',
    'f619e470-ed8c-415f-aefb-57fdab3aad36',
    '2025-12-19T15:27:14.473801+00:00',
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
    'f619e470-ed8c-415f-aefb-57fdab3aad36',
    c.id,
    '1.0.0',
    '{"name": "Databricks", "slug": "databricks", "version": "1.0.0", "description": "Data analytics platform", "category": "Analytics & Data", "status": "beta", "nango": {"enabled": true, "provider_key": "databricks"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/databricks", "token_url": "https://api.nango.dev/oauth/databricks/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.473801+00:00'
FROM connector c
WHERE c.slug = 'databricks' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '917a7eab-ce96-4740-9296-ac31b074ad69',
    'discord',
    'Discord',
    'beta',
    '47515d7f-6e33-4bfb-928b-a74e3bf9ab40',
    '2025-12-19T15:27:14.474232+00:00',
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
    '47515d7f-6e33-4bfb-928b-a74e3bf9ab40',
    c.id,
    '1.0.0',
    '{"name": "Discord", "slug": "discord", "version": "1.0.0", "description": "Send messages and manage Discord servers", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "discord"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/discord", "token_url": "https://api.nango.dev/oauth/discord/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.474232+00:00'
FROM connector c
WHERE c.slug = 'discord' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '49d50fe8-4852-485b-8a0b-cfbe9b64cf24',
    'docker-hub',
    'Docker Hub',
    'beta',
    '2fd9979b-3d96-4f37-a11f-dcf2e0e4520a',
    '2025-12-19T15:27:14.474636+00:00',
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
    '2fd9979b-3d96-4f37-a11f-dcf2e0e4520a',
    c.id,
    '1.0.0',
    '{"name": "Docker Hub", "slug": "docker-hub", "version": "1.0.0", "description": "Container registry", "category": "Development & Code", "status": "beta", "nango": {"enabled": true, "provider_key": "docker"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/docker", "token_url": "https://api.nango.dev/oauth/docker/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.474636+00:00'
FROM connector c
WHERE c.slug = 'docker-hub' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '69ad1458-962b-4ca3-8e0d-83b49f2b40e2',
    'doodle',
    'Doodle',
    'beta',
    '6689e3f2-feb6-4d2f-84d0-41c79adc0a0f',
    '2025-12-19T15:27:14.475028+00:00',
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
    '6689e3f2-feb6-4d2f-84d0-41c79adc0a0f',
    c.id,
    '1.0.0',
    '{"name": "Doodle", "slug": "doodle", "version": "1.0.0", "description": "Meeting scheduling", "category": "Calendar & Scheduling", "status": "beta", "nango": {"enabled": true, "provider_key": "doodle"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/doodle", "token_url": "https://api.nango.dev/oauth/doodle/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.475028+00:00'
FROM connector c
WHERE c.slug = 'doodle' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '5a7c46aa-259a-4ac5-ace2-e1619e0884c7',
    'dropbox',
    'Dropbox',
    'beta',
    'cde2e50f-efdb-4cf2-b906-fb5c676f730b',
    '2025-12-19T15:27:14.475371+00:00',
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
    'cde2e50f-efdb-4cf2-b906-fb5c676f730b',
    c.id,
    '1.0.0',
    '{"name": "Dropbox", "slug": "dropbox", "version": "1.0.0", "description": "Cloud file storage", "category": "File Storage & Cloud", "status": "beta", "nango": {"enabled": true, "provider_key": "dropbox"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/dropbox", "token_url": "https://api.nango.dev/oauth/dropbox/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.475371+00:00'
FROM connector c
WHERE c.slug = 'dropbox' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '9fa401cc-ac69-4a49-a4e0-da0ac8024e55',
    'facebook',
    'Facebook',
    'beta',
    'a0ffd2b0-de72-4487-95da-9afcb081e9a3',
    '2025-12-19T15:27:14.475710+00:00',
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
    'a0ffd2b0-de72-4487-95da-9afcb081e9a3',
    c.id,
    '1.0.0',
    '{"name": "Facebook", "slug": "facebook", "version": "1.0.0", "description": "Social media platform", "category": "Social Media", "status": "beta", "nango": {"enabled": true, "provider_key": "facebook"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/facebook", "token_url": "https://api.nango.dev/oauth/facebook/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.475710+00:00'
FROM connector c
WHERE c.slug = 'facebook' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'a3877321-d661-4b6c-940c-cfdbf73620f9',
    'freshdesk',
    'Freshdesk',
    'beta',
    'bda619f2-7668-4066-8a6e-d128974b6ca9',
    '2025-12-19T15:27:14.476065+00:00',
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
    'bda619f2-7668-4066-8a6e-d128974b6ca9',
    c.id,
    '1.0.0',
    '{"name": "Freshdesk", "slug": "freshdesk", "version": "1.0.0", "description": "Customer support platform", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "freshdesk"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/freshdesk", "token_url": "https://api.nango.dev/oauth/freshdesk/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.476065+00:00'
FROM connector c
WHERE c.slug = 'freshdesk' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '5d601b30-738a-45b1-b325-74da4d7337b2',
    'front',
    'Front',
    'beta',
    '9cd6c00a-0e00-4845-8123-2e326f7c983e',
    '2025-12-19T15:27:14.476396+00:00',
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
    '9cd6c00a-0e00-4845-8123-2e326f7c983e',
    c.id,
    '1.0.0',
    '{"name": "Front", "slug": "front", "version": "1.0.0", "description": "Shared inbox and customer communication", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "front"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/front", "token_url": "https://api.nango.dev/oauth/front/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.476396+00:00'
FROM connector c
WHERE c.slug = 'front' AND c.is_platform = true
ON CONFLICT DO NOTHING;

COMMIT;

-- Verify this batch
SELECT COUNT(*) as connectors_after_batch FROM connector;
