
-- Batch 6 of 10
-- Migrating 10 connectors

BEGIN;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '7d8df5a9-87c2-42bc-a002-f775a4699764',
    'linkedin',
    'LinkedIn',
    'beta',
    'e1d093ae-4572-4a4c-b2ab-1be2fd76ba6b',
    '2025-12-19T15:27:14.484112+00:00',
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
    'e1d093ae-4572-4a4c-b2ab-1be2fd76ba6b',
    c.id,
    '1.0.0',
    '{"name": "LinkedIn", "slug": "linkedin", "version": "1.0.0", "description": "Professional networking", "category": "Social Media", "status": "beta", "nango": {"enabled": true, "provider_key": "linkedin"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/linkedin", "token_url": "https://api.nango.dev/oauth/linkedin/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.484112+00:00'
FROM connector c
WHERE c.slug = 'linkedin' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '7cc6dbb6-b7d0-499a-a0e8-4d7220e985d8',
    'looker',
    'Looker',
    'beta',
    '30a43840-35d4-4aec-b686-ad4da16468d4',
    '2025-12-19T15:27:14.484422+00:00',
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
    '30a43840-35d4-4aec-b686-ad4da16468d4',
    c.id,
    '1.0.0',
    '{"name": "Looker", "slug": "looker", "version": "1.0.0", "description": "Business intelligence", "category": "Analytics & Data", "status": "beta", "nango": {"enabled": true, "provider_key": "looker"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/looker", "token_url": "https://api.nango.dev/oauth/looker/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.484422+00:00'
FROM connector c
WHERE c.slug = 'looker' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '18cba009-83ce-4c5b-ace3-abcd040f4e9b',
    'mailchimp',
    'Mailchimp',
    'beta',
    'dc41937e-0ae4-4e1f-8a2c-07c0e6b4635c',
    '2025-12-19T15:27:14.484724+00:00',
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
    'dc41937e-0ae4-4e1f-8a2c-07c0e6b4635c',
    c.id,
    '1.0.0',
    '{"name": "Mailchimp", "slug": "mailchimp", "version": "1.0.0", "description": "Manage email campaigns and subscribers", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "mailchimp"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/mailchimp", "token_url": "https://api.nango.dev/oauth/mailchimp/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.484724+00:00'
FROM connector c
WHERE c.slug = 'mailchimp' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '1a13a405-0b7f-40ad-af34-a1c12183a5b8',
    'medium',
    'Medium',
    'beta',
    '5c995a16-d10b-4305-9132-329b22aa3045',
    '2025-12-19T15:27:14.485041+00:00',
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
    '5c995a16-d10b-4305-9132-329b22aa3045',
    c.id,
    '1.0.0',
    '{"name": "Medium", "slug": "medium", "version": "1.0.0", "description": "Online publishing platform", "category": "Social Media", "status": "beta", "nango": {"enabled": true, "provider_key": "medium"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/medium", "token_url": "https://api.nango.dev/oauth/medium/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.485041+00:00'
FROM connector c
WHERE c.slug = 'medium' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '4bdf8770-eb85-4807-a884-c0c34d94f890',
    'metabase',
    'Metabase',
    'beta',
    'a1ab826b-861a-4ce3-a5ba-8871c5044be2',
    '2025-12-19T15:27:14.485368+00:00',
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
    'a1ab826b-861a-4ce3-a5ba-8871c5044be2',
    c.id,
    '1.0.0',
    '{"name": "Metabase", "slug": "metabase", "version": "1.0.0", "description": "Business intelligence tool", "category": "Analytics & Data", "status": "beta", "nango": {"enabled": true, "provider_key": "metabase"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/metabase", "token_url": "https://api.nango.dev/oauth/metabase/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.485368+00:00'
FROM connector c
WHERE c.slug = 'metabase' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'ef924275-c9d6-4614-a367-a804d04e425d',
    'microsoft-teams',
    'Microsoft Teams',
    'beta',
    '1697c656-e2ac-4e5b-8a99-e5513e96c596',
    '2025-12-19T15:27:14.485699+00:00',
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
    '1697c656-e2ac-4e5b-8a99-e5513e96c596',
    c.id,
    '1.0.0',
    '{"name": "Microsoft Teams", "slug": "microsoft-teams", "version": "1.0.0", "description": "Send messages and manage Teams channels", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "microsoft-teams"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/microsoft-teams", "token_url": "https://api.nango.dev/oauth/microsoft-teams/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.485699+00:00'
FROM connector c
WHERE c.slug = 'microsoft-teams' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'd02e3c96-e5c4-46f1-b825-982710388bf1',
    'microsoft-to-do',
    'Microsoft To Do',
    'beta',
    '393f3331-1e35-4fd8-82d0-2cfd61b10241',
    '2025-12-19T15:27:14.486041+00:00',
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
    '393f3331-1e35-4fd8-82d0-2cfd61b10241',
    c.id,
    '1.0.0',
    '{"name": "Microsoft To Do", "slug": "microsoft-to-do", "version": "1.0.0", "description": "Task management app", "category": "Project Management", "status": "beta", "nango": {"enabled": true, "provider_key": "microsoft-todo"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/microsoft-todo", "token_url": "https://api.nango.dev/oauth/microsoft-todo/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.486041+00:00'
FROM connector c
WHERE c.slug = 'microsoft-to-do' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '63f0c4a2-4878-41b6-84df-ec3bb1aaa6a5',
    'mixpanel',
    'Mixpanel',
    'beta',
    '6cfeee31-bcd1-4f97-859a-df2bc54e655a',
    '2025-12-19T15:27:14.486353+00:00',
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
    '6cfeee31-bcd1-4f97-859a-df2bc54e655a',
    c.id,
    '1.0.0',
    '{"name": "Mixpanel", "slug": "mixpanel", "version": "1.0.0", "description": "Product analytics", "category": "Analytics & Data", "status": "beta", "nango": {"enabled": true, "provider_key": "mixpanel"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/mixpanel", "token_url": "https://api.nango.dev/oauth/mixpanel/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.486353+00:00'
FROM connector c
WHERE c.slug = 'mixpanel' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'd3955615-564e-4cb8-8998-bd02e082d8ce',
    'monday-com',
    'Monday.com',
    'beta',
    'a2452866-0882-4206-8f84-b56588851cd7',
    '2025-12-19T15:27:14.486874+00:00',
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
    'a2452866-0882-4206-8f84-b56588851cd7',
    c.id,
    '1.0.0',
    '{"name": "Monday.com", "slug": "monday-com", "version": "1.0.0", "description": "Work management platform", "category": "CRM & Sales", "status": "beta", "nango": {"enabled": true, "provider_key": "monday"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/monday", "token_url": "https://api.nango.dev/oauth/monday/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.486874+00:00'
FROM connector c
WHERE c.slug = 'monday-com' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '72749917-53f8-4188-9ee4-36cac5aabe95',
    'netlify',
    'Netlify',
    'beta',
    'd0538828-c646-44bc-a5de-d757e8da295e',
    '2025-12-19T15:27:14.487284+00:00',
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
    'd0538828-c646-44bc-a5de-d757e8da295e',
    c.id,
    '1.0.0',
    '{"name": "Netlify", "slug": "netlify", "version": "1.0.0", "description": "Web development platform", "category": "Development & Code", "status": "beta", "nango": {"enabled": true, "provider_key": "netlify"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/netlify", "token_url": "https://api.nango.dev/oauth/netlify/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.487284+00:00'
FROM connector c
WHERE c.slug = 'netlify' AND c.is_platform = true
ON CONFLICT DO NOTHING;

COMMIT;

-- Verify this batch
SELECT COUNT(*) as connectors_after_batch FROM connector;
