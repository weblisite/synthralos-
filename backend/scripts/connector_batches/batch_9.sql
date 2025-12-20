
-- Batch 9 of 10
-- Migrating 10 connectors

BEGIN;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '06a06cf0-38b9-436d-8cec-3b7fc9ee893c',
    'stripe',
    'Stripe',
    'beta',
    'c9eb18c2-e1eb-4113-a04f-e8ba77a94712',
    '2025-12-19T15:27:14.494753+00:00',
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
    'c9eb18c2-e1eb-4113-a04f-e8ba77a94712',
    c.id,
    '1.0.0',
    '{"name": "Stripe", "slug": "stripe", "version": "1.0.0", "description": "Payment processing platform", "category": "Payments", "status": "beta", "nango": {"enabled": true, "provider_key": "stripe"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/stripe", "token_url": "https://api.nango.dev/oauth/stripe/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.494753+00:00'
FROM connector c
WHERE c.slug = 'stripe' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'e6290848-5da9-422d-be4c-6c58c324a29d',
    'tableau',
    'Tableau',
    'beta',
    '731d97c8-046f-410a-8c6f-d028e5457598',
    '2025-12-19T15:27:14.495740+00:00',
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
    '731d97c8-046f-410a-8c6f-d028e5457598',
    c.id,
    '1.0.0',
    '{"name": "Tableau", "slug": "tableau", "version": "1.0.0", "description": "Data visualization", "category": "Analytics & Data", "status": "beta", "nango": {"enabled": true, "provider_key": "tableau"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/tableau", "token_url": "https://api.nango.dev/oauth/tableau/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.495740+00:00'
FROM connector c
WHERE c.slug = 'tableau' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '1cf4c4ba-8bdc-40be-b7e6-de1fe02c4651',
    'telegram',
    'Telegram',
    'beta',
    '471e1f96-2c4c-4bf6-91e9-1b3180545a26',
    '2025-12-19T15:27:14.496101+00:00',
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
    '471e1f96-2c4c-4bf6-91e9-1b3180545a26',
    c.id,
    '1.0.0',
    '{"name": "Telegram", "slug": "telegram", "version": "1.0.0", "description": "Send Telegram messages", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "telegram"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/telegram", "token_url": "https://api.nango.dev/oauth/telegram/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.496101+00:00'
FROM connector c
WHERE c.slug = 'telegram' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'f32a68ae-a040-4b0d-8a6a-8672db0aec09',
    'terraform-cloud',
    'Terraform Cloud',
    'beta',
    'cb80b607-748f-4b2d-980f-fc067a19f90e',
    '2025-12-19T15:27:14.496417+00:00',
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
    'cb80b607-748f-4b2d-980f-fc067a19f90e',
    c.id,
    '1.0.0',
    '{"name": "Terraform Cloud", "slug": "terraform-cloud", "version": "1.0.0", "description": "Infrastructure as code", "category": "Development & Code", "status": "beta", "nango": {"enabled": true, "provider_key": "terraform"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/terraform", "token_url": "https://api.nango.dev/oauth/terraform/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.496417+00:00'
FROM connector c
WHERE c.slug = 'terraform-cloud' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '17ef4ccf-d767-4b7f-a522-49e453f43019',
    'tiktok',
    'TikTok',
    'beta',
    '8e8c0495-c69b-4b91-a8bf-ddd1df221fd0',
    '2025-12-19T15:27:14.497097+00:00',
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
    '8e8c0495-c69b-4b91-a8bf-ddd1df221fd0',
    c.id,
    '1.0.0',
    '{"name": "TikTok", "slug": "tiktok", "version": "1.0.0", "description": "Short-form video platform", "category": "Social Media", "status": "beta", "nango": {"enabled": true, "provider_key": "tiktok"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/tiktok", "token_url": "https://api.nango.dev/oauth/tiktok/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.497097+00:00'
FROM connector c
WHERE c.slug = 'tiktok' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '8e5447d1-4996-4b26-9525-7a51639d3fb7',
    'todoist',
    'Todoist',
    'beta',
    'fec4ccdc-0023-4623-a4d4-806d4bc0334f',
    '2025-12-19T15:27:14.497456+00:00',
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
    'fec4ccdc-0023-4623-a4d4-806d4bc0334f',
    c.id,
    '1.0.0',
    '{"name": "Todoist", "slug": "todoist", "version": "1.0.0", "description": "Task management and to-do lists", "category": "Project Management", "status": "beta", "nango": {"enabled": true, "provider_key": "todoist"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/todoist", "token_url": "https://api.nango.dev/oauth/todoist/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.497456+00:00'
FROM connector c
WHERE c.slug = 'todoist' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'cf6276a2-359f-49f3-ba9b-5085bb4ae62b',
    'trello',
    'Trello',
    'beta',
    '23217617-3d04-4060-a08c-0962ced2c754',
    '2025-12-19T15:27:14.498355+00:00',
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
    '23217617-3d04-4060-a08c-0962ced2c754',
    c.id,
    '1.0.0',
    '{"name": "Trello", "slug": "trello", "version": "1.0.0", "description": "Kanban board project management", "category": "Project Management", "status": "beta", "nango": {"enabled": true, "provider_key": "trello"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/trello", "token_url": "https://api.nango.dev/oauth/trello/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.498355+00:00'
FROM connector c
WHERE c.slug = 'trello' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'f0e07f95-0713-46bc-91f9-dca212859d83',
    'twilio',
    'Twilio',
    'beta',
    'cb358d15-c395-4edc-b590-11902ac28f90',
    '2025-12-19T15:27:14.498685+00:00',
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
    'cb358d15-c395-4edc-b590-11902ac28f90',
    c.id,
    '1.0.0',
    '{"name": "Twilio", "slug": "twilio", "version": "1.0.0", "description": "Send SMS and make phone calls", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "twilio"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/twilio", "token_url": "https://api.nango.dev/oauth/twilio/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.498685+00:00'
FROM connector c
WHERE c.slug = 'twilio' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'c4faaadd-1b95-4353-a618-c1681ed9980b',
    'twitter',
    'Twitter / X',
    'beta',
    '6f47c115-c1cd-450e-b135-deb3134b26b7',
    '2025-12-19T15:27:14.499077+00:00',
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
    '6f47c115-c1cd-450e-b135-deb3134b26b7',
    c.id,
    '1.0.0',
    '{"name": "Twitter / X", "slug": "twitter", "version": "1.0.0", "description": "Social media platform", "category": "Social Media", "status": "beta", "nango": {"enabled": true, "provider_key": "twitter"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/twitter", "token_url": "https://api.nango.dev/oauth/twitter/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.499077+00:00'
FROM connector c
WHERE c.slug = 'twitter' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'a095a401-066a-4f3e-af89-cbe91808c91b',
    'vercel',
    'Vercel',
    'beta',
    'b487b1e4-0f37-4e0f-81a8-ecb23ca61d13',
    '2025-12-19T15:27:14.499402+00:00',
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
    'b487b1e4-0f37-4e0f-81a8-ecb23ca61d13',
    c.id,
    '1.0.0',
    '{"name": "Vercel", "slug": "vercel", "version": "1.0.0", "description": "Frontend deployment platform", "category": "Development & Code", "status": "beta", "nango": {"enabled": true, "provider_key": "vercel"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/vercel", "token_url": "https://api.nango.dev/oauth/vercel/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.499402+00:00'
FROM connector c
WHERE c.slug = 'vercel' AND c.is_platform = true
ON CONFLICT DO NOTHING;

COMMIT;

-- Verify this batch
SELECT COUNT(*) as connectors_after_batch FROM connector;
