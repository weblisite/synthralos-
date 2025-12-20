
-- Batch 5 of 10
-- Migrating 10 connectors

BEGIN;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'de0f4244-17dc-461d-b1ec-4d53dfd6ae47',
    'hubspot',
    'HubSpot',
    'beta',
    '3edc63ef-48b6-4e0b-8574-fa615fb505cf',
    '2025-12-19T15:27:14.480561+00:00',
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
    '3edc63ef-48b6-4e0b-8574-fa615fb505cf',
    c.id,
    '1.0.0',
    '{"name": "HubSpot", "slug": "hubspot", "version": "1.0.0", "description": "Marketing, sales, and service platform", "category": "CRM & Sales", "status": "beta", "nango": {"enabled": true, "provider_key": "hubspot"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/hubspot", "token_url": "https://api.nango.dev/oauth/hubspot/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.480561+00:00'
FROM connector c
WHERE c.slug = 'hubspot' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'be91c976-3682-4a9a-a92f-3a155e3f81b1',
    'hugging-face',
    'Hugging Face',
    'beta',
    'e7a9e6ce-dffe-43b5-9a1b-3d4ea5254c2d',
    '2025-12-19T15:27:14.480912+00:00',
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
    'e7a9e6ce-dffe-43b5-9a1b-3d4ea5254c2d',
    c.id,
    '1.0.0',
    '{"name": "Hugging Face", "slug": "hugging-face", "version": "1.0.0", "description": "ML model hosting", "category": "AI & Machine Learning", "status": "beta", "nango": {"enabled": true, "provider_key": "huggingface"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/huggingface", "token_url": "https://api.nango.dev/oauth/huggingface/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.480912+00:00'
FROM connector c
WHERE c.slug = 'hugging-face' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '510426c4-92f2-4132-9657-f3836fbe7236',
    'imgur',
    'Imgur',
    'beta',
    '00bb1ff6-6d09-41ef-9674-0db37225a2f6',
    '2025-12-19T15:27:14.481285+00:00',
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
    '00bb1ff6-6d09-41ef-9674-0db37225a2f6',
    c.id,
    '1.0.0',
    '{"name": "Imgur", "slug": "imgur", "version": "1.0.0", "description": "Image hosting and sharing", "category": "File Storage & Cloud", "status": "beta", "nango": {"enabled": true, "provider_key": "imgur"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/imgur", "token_url": "https://api.nango.dev/oauth/imgur/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.481285+00:00'
FROM connector c
WHERE c.slug = 'imgur' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'adffbd6e-b53c-4af6-a76d-4350cb13c711',
    'insightly',
    'Insightly',
    'beta',
    '41885794-1a01-4eb7-9297-6ab35ef21406',
    '2025-12-19T15:27:14.481669+00:00',
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
    '41885794-1a01-4eb7-9297-6ab35ef21406',
    c.id,
    '1.0.0',
    '{"name": "Insightly", "slug": "insightly", "version": "1.0.0", "description": "CRM and project management", "category": "CRM & Sales", "status": "beta", "nango": {"enabled": true, "provider_key": "insightly"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/insightly", "token_url": "https://api.nango.dev/oauth/insightly/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.481669+00:00'
FROM connector c
WHERE c.slug = 'insightly' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '775cc94c-2852-45ee-8dda-42bcec59c01c',
    'instagram',
    'Instagram',
    'beta',
    '3ab5b9fb-1cac-45de-8808-e87166d4b51b',
    '2025-12-19T15:27:14.482051+00:00',
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
    '3ab5b9fb-1cac-45de-8808-e87166d4b51b',
    c.id,
    '1.0.0',
    '{"name": "Instagram", "slug": "instagram", "version": "1.0.0", "description": "Photo and video sharing", "category": "Social Media", "status": "beta", "nango": {"enabled": true, "provider_key": "instagram"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/instagram", "token_url": "https://api.nango.dev/oauth/instagram/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.482051+00:00'
FROM connector c
WHERE c.slug = 'instagram' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'd6ff3fd1-5dca-4aa2-af83-e49a865ce42e',
    'intercom',
    'Intercom',
    'beta',
    '0d4bc1b6-c67a-41ce-87ed-9462249bb7c3',
    '2025-12-19T15:27:14.482460+00:00',
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
    '0d4bc1b6-c67a-41ce-87ed-9462249bb7c3',
    c.id,
    '1.0.0',
    '{"name": "Intercom", "slug": "intercom", "version": "1.0.0", "description": "Manage customer conversations", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "intercom"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/intercom", "token_url": "https://api.nango.dev/oauth/intercom/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.482460+00:00'
FROM connector c
WHERE c.slug = 'intercom' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'd5f3c4b5-e3ca-4116-a69f-e53110e47e51',
    'jenkins',
    'Jenkins',
    'beta',
    '63217e2f-4a8f-4b44-8d17-047ccf6f5e60',
    '2025-12-19T15:27:14.482775+00:00',
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
    '63217e2f-4a8f-4b44-8d17-047ccf6f5e60',
    c.id,
    '1.0.0',
    '{"name": "Jenkins", "slug": "jenkins", "version": "1.0.0", "description": "CI/CD automation server", "category": "Development & Code", "status": "beta", "nango": {"enabled": true, "provider_key": "jenkins"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/jenkins", "token_url": "https://api.nango.dev/oauth/jenkins/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.482775+00:00'
FROM connector c
WHERE c.slug = 'jenkins' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '567b444f-e8cb-49b9-ac1c-729fec695ef1',
    'jira',
    'Jira',
    'beta',
    'd6ade571-50aa-43c4-a90c-b8c5ff3dbdd7',
    '2025-12-19T15:27:14.483105+00:00',
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
    'd6ade571-50aa-43c4-a90c-b8c5ff3dbdd7',
    c.id,
    '1.0.0',
    '{"name": "Jira", "slug": "jira", "version": "1.0.0", "description": "Issue tracking and project management", "category": "Project Management", "status": "beta", "nango": {"enabled": true, "provider_key": "jira"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/jira", "token_url": "https://api.nango.dev/oauth/jira/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.483105+00:00'
FROM connector c
WHERE c.slug = 'jira' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '8e598cf4-3f38-4de9-9351-11e6eaa02e17',
    'kubernetes',
    'Kubernetes',
    'beta',
    '022da258-48c3-4be7-9c91-c636c169b2ac',
    '2025-12-19T15:27:14.483441+00:00',
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
    '022da258-48c3-4be7-9c91-c636c169b2ac',
    c.id,
    '1.0.0',
    '{"name": "Kubernetes", "slug": "kubernetes", "version": "1.0.0", "description": "Container orchestration", "category": "Development & Code", "status": "beta", "nango": {"enabled": true, "provider_key": "kubernetes"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/kubernetes", "token_url": "https://api.nango.dev/oauth/kubernetes/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.483441+00:00'
FROM connector c
WHERE c.slug = 'kubernetes' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '33d43e76-3e25-409b-89f9-8247342a9db5',
    'linear',
    'Linear',
    'beta',
    '89fa1c4a-0fa5-404c-80c5-00e8ce5a43db',
    '2025-12-19T15:27:14.483772+00:00',
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
    '89fa1c4a-0fa5-404c-80c5-00e8ce5a43db',
    c.id,
    '1.0.0',
    '{"name": "Linear", "slug": "linear", "version": "1.0.0", "description": "Issue tracking for software teams", "category": "Project Management", "status": "beta", "nango": {"enabled": true, "provider_key": "linear"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/linear", "token_url": "https://api.nango.dev/oauth/linear/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.483772+00:00'
FROM connector c
WHERE c.slug = 'linear' AND c.is_platform = true
ON CONFLICT DO NOTHING;

COMMIT;

-- Verify this batch
SELECT COUNT(*) as connectors_after_batch FROM connector;
