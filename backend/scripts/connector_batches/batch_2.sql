
-- Batch 2 of 10
-- Migrating 10 connectors

BEGIN;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '840691a2-54a9-4773-bafc-559c902084ad',
    'bitbucket',
    'Bitbucket',
    'beta',
    'a4ddc553-097e-4d56-bd36-375eb6dc9065',
    '2025-12-19T15:27:14.468276+00:00',
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
    'a4ddc553-097e-4d56-bd36-375eb6dc9065',
    c.id,
    '1.0.0',
    '{"name": "Bitbucket", "slug": "bitbucket", "version": "1.0.0", "description": "Git code hosting", "category": "Development & Code", "status": "beta", "nango": {"enabled": true, "provider_key": "bitbucket"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/bitbucket", "token_url": "https://api.nango.dev/oauth/bitbucket/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.468276+00:00'
FROM connector c
WHERE c.slug = 'bitbucket' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '05380b16-939e-4afc-9a6f-e299997fa9fa',
    'box',
    'Box',
    'beta',
    'e380d734-dd10-43a3-a10f-119799ecdd97',
    '2025-12-19T15:27:14.468639+00:00',
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
    'e380d734-dd10-43a3-a10f-119799ecdd97',
    c.id,
    '1.0.0',
    '{"name": "Box", "slug": "box", "version": "1.0.0", "description": "Cloud content management", "category": "File Storage & Cloud", "status": "beta", "nango": {"enabled": true, "provider_key": "box"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/box", "token_url": "https://api.nango.dev/oauth/box/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.468639+00:00'
FROM connector c
WHERE c.slug = 'box' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'f4bca86b-6ccb-4fd9-a161-83c01263cf78',
    'braintree',
    'Braintree',
    'beta',
    'ab4b6517-b4aa-4f64-8647-8779a259fe25',
    '2025-12-19T15:27:14.469017+00:00',
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
    'ab4b6517-b4aa-4f64-8647-8779a259fe25',
    c.id,
    '1.0.0',
    '{"name": "Braintree", "slug": "braintree", "version": "1.0.0", "description": "Payment gateway", "category": "E-commerce & Payments", "status": "beta", "nango": {"enabled": true, "provider_key": "braintree"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/braintree", "token_url": "https://api.nango.dev/oauth/braintree/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.469017+00:00'
FROM connector c
WHERE c.slug = 'braintree' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '3778b4b6-3bb4-4b53-ac58-42b3a09a60bd',
    'buffer',
    'Buffer',
    'beta',
    '807b8444-4335-4846-be7b-66113b637f11',
    '2025-12-19T15:27:14.469429+00:00',
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
    '807b8444-4335-4846-be7b-66113b637f11',
    c.id,
    '1.0.0',
    '{"name": "Buffer", "slug": "buffer", "version": "1.0.0", "description": "Social media management", "category": "Social Media", "status": "beta", "nango": {"enabled": true, "provider_key": "buffer"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/buffer", "token_url": "https://api.nango.dev/oauth/buffer/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.469429+00:00'
FROM connector c
WHERE c.slug = 'buffer' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'cf4c5617-e6cb-4b5a-b573-f2636bd3af86',
    'calendly',
    'Calendly',
    'beta',
    'c8d003b5-32cd-4151-932f-47caaad96686',
    '2025-12-19T15:27:14.469801+00:00',
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
    'c8d003b5-32cd-4151-932f-47caaad96686',
    c.id,
    '1.0.0',
    '{"name": "Calendly", "slug": "calendly", "version": "1.0.0", "description": "Schedule meetings and appointments", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "calendly"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/calendly", "token_url": "https://api.nango.dev/oauth/calendly/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.469801+00:00'
FROM connector c
WHERE c.slug = 'calendly' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '10fa96b6-e895-4e8e-b2a6-df2d1c6819a3',
    'chargebee',
    'Chargebee',
    'beta',
    'fafba460-5b6d-4b0c-9a90-a613656b9a3b',
    '2025-12-19T15:27:14.470149+00:00',
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
    'fafba460-5b6d-4b0c-9a90-a613656b9a3b',
    c.id,
    '1.0.0',
    '{"name": "Chargebee", "slug": "chargebee", "version": "1.0.0", "description": "Subscription management", "category": "E-commerce & Payments", "status": "beta", "nango": {"enabled": true, "provider_key": "chargebee"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/chargebee", "token_url": "https://api.nango.dev/oauth/chargebee/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.470149+00:00'
FROM connector c
WHERE c.slug = 'chargebee' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'cb89e9a6-a506-49d4-8740-a0e2ab6c53e5',
    'circleci',
    'CircleCI',
    'beta',
    'abc16836-3c42-45b3-b560-f6651a735e23',
    '2025-12-19T15:27:14.470584+00:00',
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
    'abc16836-3c42-45b3-b560-f6651a735e23',
    c.id,
    '1.0.0',
    '{"name": "CircleCI", "slug": "circleci", "version": "1.0.0", "description": "CI/CD platform", "category": "Development & Code", "status": "beta", "nango": {"enabled": true, "provider_key": "circleci"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/circleci", "token_url": "https://api.nango.dev/oauth/circleci/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.470584+00:00'
FROM connector c
WHERE c.slug = 'circleci' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'a19c1c6e-dc15-4007-be6e-0f77d707007a',
    'clickup',
    'ClickUp',
    'beta',
    'ecd953c5-41f2-4a35-a6c0-3b2316988770',
    '2025-12-19T15:27:14.471026+00:00',
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
    'ecd953c5-41f2-4a35-a6c0-3b2316988770',
    c.id,
    '1.0.0',
    '{"name": "ClickUp", "slug": "clickup", "version": "1.0.0", "description": "All-in-one productivity platform", "category": "Project Management", "status": "beta", "nango": {"enabled": true, "provider_key": "clickup"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/clickup", "token_url": "https://api.nango.dev/oauth/clickup/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.471026+00:00'
FROM connector c
WHERE c.slug = 'clickup' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'f779e8e2-ca29-408c-b58a-771991381e13',
    'close',
    'Close',
    'beta',
    'ffa37e6c-0b81-4a83-acb8-bcc8d01c9854',
    '2025-12-19T15:27:14.471470+00:00',
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
    'ffa37e6c-0b81-4a83-acb8-bcc8d01c9854',
    c.id,
    '1.0.0',
    '{"name": "Close", "slug": "close", "version": "1.0.0", "description": "Inside sales CRM", "category": "CRM & Sales", "status": "beta", "nango": {"enabled": true, "provider_key": "close"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/close", "token_url": "https://api.nango.dev/oauth/close/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.471470+00:00'
FROM connector c
WHERE c.slug = 'close' AND c.is_platform = true
ON CONFLICT DO NOTHING;

INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '48b95dc9-37f6-4a43-86bd-e478f928e1b6',
    'cloudinary',
    'Cloudinary',
    'beta',
    '2f2a8802-a1e6-4c98-91ed-274a1aa1fb56',
    '2025-12-19T15:27:14.472125+00:00',
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
    '2f2a8802-a1e6-4c98-91ed-274a1aa1fb56',
    c.id,
    '1.0.0',
    '{"name": "Cloudinary", "slug": "cloudinary", "version": "1.0.0", "description": "Image and video management", "category": "File Storage & Cloud", "status": "beta", "nango": {"enabled": true, "provider_key": "cloudinary"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/cloudinary", "token_url": "https://api.nango.dev/oauth/cloudinary/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:27:14.472125+00:00'
FROM connector c
WHERE c.slug = 'cloudinary' AND c.is_platform = true
ON CONFLICT DO NOTHING;

COMMIT;

-- Verify this batch
SELECT COUNT(*) as connectors_after_batch FROM connector;
