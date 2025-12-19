
-- Batch 4 of 10
-- Migrating 10 connectors

BEGIN;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'a37b0a46-e0f5-462d-92fd-1234e488bab6',
    'github',
    'GitHub',
    'beta',
    '699ca343-e382-49fd-a2c6-d74ad85d8fdf',
    '2025-12-19T15:27:14.476717+00:00',
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
    '699ca343-e382-49fd-a2c6-d74ad85d8fdf',
    c.id,
    '1.0.0',
    '{"name": "GitHub", "slug": "github", "version": "1.0.0", "description": "Code hosting and version control", "category": "Development & Code", "status": "beta", "nango": {"enabled": true, "provider_key": "github"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/github", "token_url": "https://api.nango.dev/oauth/github/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.476717+00:00'
FROM connector c
WHERE c.slug = 'github' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '00f8fb75-3b7c-4fe5-8baf-e4561d82f051',
    'gitlab',
    'GitLab',
    'beta',
    'd53d3f0e-9eb5-4920-b7c0-5bbef2c4c241',
    '2025-12-19T15:27:14.477030+00:00',
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
    'd53d3f0e-9eb5-4920-b7c0-5bbef2c4c241',
    c.id,
    '1.0.0',
    '{"name": "GitLab", "slug": "gitlab", "version": "1.0.0", "description": "DevOps platform", "category": "Development & Code", "status": "beta", "nango": {"enabled": true, "provider_key": "gitlab"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/gitlab", "token_url": "https://api.nango.dev/oauth/gitlab/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.477030+00:00'
FROM connector c
WHERE c.slug = 'gitlab' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'a5086011-cc50-4c13-81df-01f90fb45a84',
    'gmail',
    'Gmail',
    'beta',
    'a3772e0f-8fa5-454d-b537-e93c95570fe3',
    '2025-12-19T15:27:14.477336+00:00',
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
    'a3772e0f-8fa5-454d-b537-e93c95570fe3',
    c.id,
    '1.0.0',
    '{"name": "Gmail", "slug": "gmail", "version": "1.0.0", "description": "Send and receive emails via Gmail API", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "gmail"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/gmail", "token_url": "https://api.nango.dev/oauth/gmail/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.477336+00:00'
FROM connector c
WHERE c.slug = 'gmail' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '16924cca-09cb-45b3-a9e6-679d9bacdf80',
    'google-ai',
    'Google AI',
    'beta',
    'a3ab3af7-5183-496f-b90b-28a7ef65cca5',
    '2025-12-19T15:27:14.477724+00:00',
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
    'a3ab3af7-5183-496f-b90b-28a7ef65cca5',
    c.id,
    '1.0.0',
    '{"name": "Google AI", "slug": "google-ai", "version": "1.0.0", "description": "Google AI services", "category": "AI & Machine Learning", "status": "beta", "nango": {"enabled": true, "provider_key": "google-ai"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/google-ai", "token_url": "https://api.nango.dev/oauth/google-ai/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.477724+00:00'
FROM connector c
WHERE c.slug = 'google-ai' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '32d73dae-90c3-4047-8e1c-72108d6ad406',
    'google-analytics',
    'Google Analytics',
    'beta',
    'e418ecdc-7d4c-4f2a-883d-2ccdf574d64f',
    '2025-12-19T15:27:14.478178+00:00',
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
    'e418ecdc-7d4c-4f2a-883d-2ccdf574d64f',
    c.id,
    '1.0.0',
    '{"name": "Google Analytics", "slug": "google-analytics", "version": "1.0.0", "description": "Web analytics platform", "category": "Analytics & Data", "status": "beta", "nango": {"enabled": true, "provider_key": "google-analytics"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/google-analytics", "token_url": "https://api.nango.dev/oauth/google-analytics/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.478178+00:00'
FROM connector c
WHERE c.slug = 'google-analytics' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '1995319a-ffaf-4e7a-8bc4-2b22b6c947a0',
    'google-bigquery',
    'Google BigQuery',
    'beta',
    '5bb0170b-1539-4192-a9aa-7f94a0ccd10d',
    '2025-12-19T15:27:14.478596+00:00',
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
    '5bb0170b-1539-4192-a9aa-7f94a0ccd10d',
    c.id,
    '1.0.0',
    '{"name": "Google BigQuery", "slug": "google-bigquery", "version": "1.0.0", "description": "Cloud data warehouse", "category": "Analytics & Data", "status": "beta", "nango": {"enabled": true, "provider_key": "bigquery"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/bigquery", "token_url": "https://api.nango.dev/oauth/bigquery/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.478596+00:00'
FROM connector c
WHERE c.slug = 'google-bigquery' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '0f1aab40-b076-46bb-9570-9b2810c61c1e',
    'google-calendar',
    'Google Calendar',
    'beta',
    '3d640eaa-9bc9-48a6-909a-6085a13e710e',
    '2025-12-19T15:27:14.478962+00:00',
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
    '3d640eaa-9bc9-48a6-909a-6085a13e710e',
    c.id,
    '1.0.0',
    '{"name": "Google Calendar", "slug": "google-calendar", "version": "1.0.0", "description": "Calendar and scheduling", "category": "Calendar & Scheduling", "status": "beta", "nango": {"enabled": true, "provider_key": "google-calendar"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/google-calendar", "token_url": "https://api.nango.dev/oauth/google-calendar/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.478962+00:00'
FROM connector c
WHERE c.slug = 'google-calendar' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '51b96845-cd85-460a-9ff7-fc8f10a19973',
    'google-cloud-storage',
    'Google Cloud Storage',
    'beta',
    '9ce94f30-a90c-416f-9a56-a5460593998a',
    '2025-12-19T15:27:14.479365+00:00',
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
    '9ce94f30-a90c-416f-9a56-a5460593998a',
    c.id,
    '1.0.0',
    '{"name": "Google Cloud Storage", "slug": "google-cloud-storage", "version": "1.0.0", "description": "Google Cloud object storage", "category": "File Storage & Cloud", "status": "beta", "nango": {"enabled": true, "provider_key": "gcs"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/gcs", "token_url": "https://api.nango.dev/oauth/gcs/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.479365+00:00'
FROM connector c
WHERE c.slug = 'google-cloud-storage' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '6a28bb44-4276-4b2a-bf9e-443219a0b5e0',
    'google-drive',
    'Google Drive',
    'beta',
    '8f6c764e-23a6-453c-9d7b-fbf3620106b0',
    '2025-12-19T15:27:14.479771+00:00',
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
    '8f6c764e-23a6-453c-9d7b-fbf3620106b0',
    c.id,
    '1.0.0',
    '{"name": "Google Drive", "slug": "google-drive", "version": "1.0.0", "description": "Cloud file storage and sharing", "category": "File Storage & Cloud", "status": "beta", "nango": {"enabled": true, "provider_key": "google-drive"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/google-drive", "token_url": "https://api.nango.dev/oauth/google-drive/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.479771+00:00'
FROM connector c
WHERE c.slug = 'google-drive' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '205dcab4-4894-42fb-ba93-12fd09066149',
    'help-scout',
    'Help Scout',
    'beta',
    '4637b22d-e327-4582-92ed-519a7e7fb25f',
    '2025-12-19T15:27:14.480182+00:00',
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
    '4637b22d-e327-4582-92ed-519a7e7fb25f',
    c.id,
    '1.0.0',
    '{"name": "Help Scout", "slug": "help-scout", "version": "1.0.0", "description": "Customer support and help desk", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "helpscout"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/helpscout", "token_url": "https://api.nango.dev/oauth/helpscout/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.480182+00:00'
FROM connector c
WHERE c.slug = 'help-scout' AND c.is_platform = true
ON CONFLICT DO NOTHING;

COMMIT;

-- Verify this batch
SELECT COUNT(*) as connectors_after_batch FROM connector;
