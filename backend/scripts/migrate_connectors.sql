
-- Migrate all connectors to Supabase
-- Generated: 2025-12-19T15:18:46.492746
-- Total connectors: 99

BEGIN;


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '731167b1-7ed6-4d38-9e13-5a26d220104f',
    'activecampaign',
    'ActiveCampaign',
    'beta',
    '0fe9423a-82d6-4af8-9978-7046b28c300e',
    '2025-12-19T15:18:46.448519',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'd4612083-0f88-4869-b9d9-b5cd8ab0959d',
    'airtable',
    'Airtable',
    'beta',
    '800b1cd2-5356-45fd-8c81-872be89fd116',
    '2025-12-19T15:18:46.449395',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'cff19a4e-a16c-47ea-b544-7dfe581945f6',
    'amazon-s3',
    'Amazon S3',
    'beta',
    '22180232-f637-48c3-93d0-5c5e57266cb2',
    '2025-12-19T15:18:46.449867',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'b0905cd7-7676-42c5-bfda-e6c1675cc6d2',
    'amplitude',
    'Amplitude',
    'beta',
    'ad527526-ecbb-4007-93c0-bc64c5fca61c',
    '2025-12-19T15:18:46.450549',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '6a2f95d8-28e8-4811-8804-6d528a0324c7',
    'anthropic-claude',
    'Anthropic Claude',
    'beta',
    '2314c0d6-4307-44fb-b07e-cc2856699ecb',
    '2025-12-19T15:18:46.451865',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'aa3b63d7-e5d6-4942-9363-87366b58e65d',
    'apple-calendar',
    'Apple Calendar',
    'beta',
    'caec2fb1-1ffd-4f9a-afed-6b0ca869853b',
    '2025-12-19T15:18:46.452694',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '47d2520c-5e7a-4322-9449-a5b5df0b0d27',
    'asana',
    'Asana',
    'beta',
    'a8b57867-10e5-415b-a973-938bc2c07174',
    '2025-12-19T15:18:46.453120',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '8de9176d-856b-4a20-9c52-dc24f184964a',
    'aws',
    'AWS',
    'beta',
    'bc99fa01-862c-4e68-8aa9-b27a1cad3091',
    '2025-12-19T15:18:46.453902',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '49a7ce38-321f-4b4e-a15f-60435fb56e56',
    'azure-blob-storage',
    'Azure Blob Storage',
    'beta',
    'b733b012-9dea-4daa-a11b-39ead739793c',
    '2025-12-19T15:18:46.454358',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'f7c56773-a32b-450a-baa0-210517770dcb',
    'basecamp',
    'Basecamp',
    'beta',
    '63ddbf73-2c9a-4bb6-b93c-b282c2b470bd',
    '2025-12-19T15:18:46.455230',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '500f645d-7de0-4837-b51f-781c8fe062c9',
    'bitbucket',
    'Bitbucket',
    'beta',
    '1edd729e-682c-4f61-8315-127379b303d5',
    '2025-12-19T15:18:46.455669',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '3f63ab01-8427-45c3-bcaa-a344943492b4',
    'box',
    'Box',
    'beta',
    '4571fe8e-08fd-4eff-ac3d-4c66d4aa9089',
    '2025-12-19T15:18:46.456271',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '6a428f0c-36d8-4d48-8d9c-e3ae7abddc0f',
    'braintree',
    'Braintree',
    'beta',
    'e636b029-c0f7-455e-9124-cbb6ef5af1b2',
    '2025-12-19T15:18:46.456648',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'e3abe8a6-4485-4a09-bf25-03cb7f2e110d',
    'buffer',
    'Buffer',
    'beta',
    '9969a533-06a5-4025-8dd4-5b9cb278eed3',
    '2025-12-19T15:18:46.457302',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'c5674b59-28fe-42c9-b434-cfecd06068e4',
    'calendly',
    'Calendly',
    'beta',
    'edc4b156-015f-47a0-8025-09db6e42eb9c',
    '2025-12-19T15:18:46.457655',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'eac9d497-7b47-468f-964b-4b3510b4283a',
    'chargebee',
    'Chargebee',
    'beta',
    '6d6e09ed-03ed-43e4-9871-1e4d668c38e4',
    '2025-12-19T15:18:46.458307',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '3f4db045-b402-4bb2-a778-d7532ed9c554',
    'circleci',
    'CircleCI',
    'beta',
    '8d5f2028-65fe-485a-ac01-87300bf22a26',
    '2025-12-19T15:18:46.458678',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'e7b0f029-acd2-4a43-9aff-a23592081877',
    'clickup',
    'ClickUp',
    'beta',
    '3b4b5dd5-4cea-46d7-b994-771f5a1af7ce',
    '2025-12-19T15:18:46.459410',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '13f84fbd-26e7-4ca6-9ccf-90cceb27d0b0',
    'close',
    'Close',
    'beta',
    'c542135b-fc75-4948-ab3a-d84e0c545f60',
    '2025-12-19T15:18:46.459776',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'c803bcc1-ef21-4202-89c5-d663de599252',
    'cloudinary',
    'Cloudinary',
    'beta',
    '8be275dc-179e-45d2-93dc-5c3b00e1c954',
    '2025-12-19T15:18:46.460568',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'bc16be88-2d2d-4a7c-8c9c-632f78ae96a7',
    'cohere',
    'Cohere',
    'beta',
    '6476bc17-cacf-4953-953c-2cc5376d717a',
    '2025-12-19T15:18:46.461180',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'a3f672d2-9ac2-46cd-859a-d62ecbea5b02',
    'copper',
    'Copper',
    'beta',
    '50c94f04-ae95-4ec7-876c-ae02298926df',
    '2025-12-19T15:18:46.461891',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '0fda879e-b345-4879-87c8-55c48a90ec6c',
    'databricks',
    'Databricks',
    'beta',
    '8ca8cf12-9a1b-46c2-9dc6-bf119e176f7a',
    '2025-12-19T15:18:46.462326',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'f05a6fea-cdc9-4f49-af86-cf79687a4578',
    'discord',
    'Discord',
    'beta',
    'dc0f3536-9f2b-48d2-80a7-f47abf5e95b9',
    '2025-12-19T15:18:46.463261',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '11f29555-856a-4c46-a70a-341d94c732dd',
    'docker-hub',
    'Docker Hub',
    'beta',
    '21365890-73cd-454d-a135-8232d5e6da6a',
    '2025-12-19T15:18:46.463758',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'db7b70f7-a826-44d8-8c97-c53d47f646d7',
    'doodle',
    'Doodle',
    'beta',
    'c0c485f6-551b-4b2e-9d5a-d62ccf191e2e',
    '2025-12-19T15:18:46.464158',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'fe31cbfe-9548-47b1-ad45-4ea9c00f62ec',
    'dropbox',
    'Dropbox',
    'beta',
    '50218e06-1e9a-4fff-bf07-137fd90f6b31',
    '2025-12-19T15:18:46.464601',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'a93dc4b0-c431-45f0-8d5e-520125645de5',
    'facebook',
    'Facebook',
    'beta',
    '75abe127-926c-4b58-9b8d-bdb54418c585',
    '2025-12-19T15:18:46.465381',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'aa91e0c0-baed-4ef8-9c0c-9dcb9ed5b465',
    'freshdesk',
    'Freshdesk',
    'beta',
    'cb89dde6-20b9-40ba-8697-48441775ba86',
    '2025-12-19T15:18:46.465840',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'fd4bdd1f-7716-4d70-8207-d9c18c683646',
    'front',
    'Front',
    'beta',
    '5eeeec2f-aa08-46e1-ae1d-9c8b6efebc51',
    '2025-12-19T15:18:46.466337',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'a8f825fb-0587-4088-8084-832e147b7717',
    'github',
    'GitHub',
    'beta',
    'c87180a7-4174-433c-9260-d2369a93d974',
    '2025-12-19T15:18:46.467051',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'a63acdc0-23fc-4cd6-9a69-52f5df6176c5',
    'gitlab',
    'GitLab',
    'beta',
    '7cd720ac-a592-4863-8a1a-ab6ab862a70b',
    '2025-12-19T15:18:46.467403',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '3b80cbe3-44cf-4f5b-bdc9-7cd7db4cd875',
    'gmail',
    'Gmail',
    'beta',
    '3eabe463-8670-4164-b5b3-682a46a411da',
    '2025-12-19T15:18:46.467856',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '2a40eabe-5f7e-4bf1-9508-318721e23806',
    'google-ai',
    'Google AI',
    'beta',
    '2e10ea8d-d658-4f1c-9193-d52d760bb083',
    '2025-12-19T15:18:46.468221',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '7e4e3e8f-1a12-494c-8938-5f5d8509a06f',
    'google-analytics',
    'Google Analytics',
    'beta',
    'b78cb827-f298-4c39-81cf-0cc93e68c799',
    '2025-12-19T15:18:46.468570',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '5db0fef4-d35f-4bad-8f86-a9bc3acca575',
    'google-bigquery',
    'Google BigQuery',
    'beta',
    '90b21c47-86cf-4c36-b294-e4359659ee9a',
    '2025-12-19T15:18:46.468960',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '16172528-b227-4ee7-bc55-81eda35d1d01',
    'google-calendar',
    'Google Calendar',
    'beta',
    '559f9b67-c701-485a-8dc8-59d3dbbc1210',
    '2025-12-19T15:18:46.469362',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '03450f37-04f8-4f59-bff8-7a74704d4e09',
    'google-cloud-storage',
    'Google Cloud Storage',
    'beta',
    '12892e5e-ce86-4db9-b913-eca838f782e9',
    '2025-12-19T15:18:46.469794',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '64be0963-f83d-4520-b3f0-0beba9d1d0f6',
    'google-drive',
    'Google Drive',
    'beta',
    '6d6ee581-4662-4f84-8f3a-629885e170cf',
    '2025-12-19T15:18:46.470218',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '1e3ac982-379f-4d67-bacf-576f653ff756',
    'help-scout',
    'Help Scout',
    'beta',
    'e6f97e03-0592-4a4c-be5a-9da90337759e',
    '2025-12-19T15:18:46.470602',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'c6c6dc58-ac82-4941-b570-ca65ce756abc',
    'hubspot',
    'HubSpot',
    'beta',
    '3ea60d49-18ce-4743-b3dc-ce2c6f2b5e6d',
    '2025-12-19T15:18:46.471034',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '48d9a5bc-65e1-45a3-a02e-a2f41bf06fea',
    'hugging-face',
    'Hugging Face',
    'beta',
    'f7c912a0-d8f6-4c51-adc1-7128375261af',
    '2025-12-19T15:18:46.471429',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '9c783954-de36-4828-a6be-faf1e2703fa5',
    'imgur',
    'Imgur',
    'beta',
    'cf1c7c4a-7244-4942-a9b1-33d9ee15d88c',
    '2025-12-19T15:18:46.471792',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '340c47a8-3e8b-4304-a58b-b6e9cf9973fe',
    'insightly',
    'Insightly',
    'beta',
    'dab5677e-8c4d-4ed8-acca-0c295593a924',
    '2025-12-19T15:18:46.472138',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '039a6970-0052-40dd-a257-9d4d1fa30488',
    'instagram',
    'Instagram',
    'beta',
    '3421afc0-72b6-46a7-b8bb-48dd30038a43',
    '2025-12-19T15:18:46.472492',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '6a48f45c-860e-4965-b3bb-4cd7b2cd2648',
    'intercom',
    'Intercom',
    'beta',
    'd8d58f4a-a4d2-4d3d-8acb-eb5c92579f01',
    '2025-12-19T15:18:46.472842',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '956bd446-492e-4c2d-8004-e55a4ae56c4f',
    'jenkins',
    'Jenkins',
    'beta',
    '7791bbf6-5f9f-442f-b65b-44813ac16968',
    '2025-12-19T15:18:46.473180',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '72265992-ea36-4b7d-9e57-548396708b2d',
    'jira',
    'Jira',
    'beta',
    'd7f0c8b2-049d-4819-8103-f75746d54b5e',
    '2025-12-19T15:18:46.473537',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'ac9fa87d-599d-4e49-9385-46444e8b365f',
    'kubernetes',
    'Kubernetes',
    'beta',
    '05da1321-fe02-44fb-a685-3f65db156c49',
    '2025-12-19T15:18:46.473870',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '9a641c6d-de26-4612-bcfa-bc01742b0e34',
    'linear',
    'Linear',
    'beta',
    '375226c1-8a8b-4d93-b582-089673cb3218',
    '2025-12-19T15:18:46.474188',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'cab0c8cf-6c85-421d-8921-6b79d212a149',
    'linkedin',
    'LinkedIn',
    'beta',
    'fc79070a-1dce-403b-ae22-c8c257214038',
    '2025-12-19T15:18:46.474597',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'b07898f0-3c6c-45ae-9b20-626a5347e742',
    'looker',
    'Looker',
    'beta',
    'f4ea8724-9500-4354-bf69-5d5036525c33',
    '2025-12-19T15:18:46.474915',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '924c5d19-2bee-4846-b6dd-d320d1600be5',
    'mailchimp',
    'Mailchimp',
    'beta',
    'bccd518f-0ace-4e87-8883-b62bac64f63a',
    '2025-12-19T15:18:46.475276',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '671564bd-990d-49c1-ab31-4cb86b99a008',
    'medium',
    'Medium',
    'beta',
    'b6d47602-656c-42ec-84e8-5ae3ffc11a50',
    '2025-12-19T15:18:46.475616',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'a8e4ab6f-70e4-4f85-838f-481b7842fcb2',
    'metabase',
    'Metabase',
    'beta',
    '7d7d57e9-920d-47dc-88ee-ae69324ac84a',
    '2025-12-19T15:18:46.475964',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'b075f357-b32c-4f7e-9675-720baaa00071',
    'microsoft-teams',
    'Microsoft Teams',
    'beta',
    'e6450245-6b4d-4fd7-8534-0a5f2fe57b74',
    '2025-12-19T15:18:46.476330',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '992f03e4-ee14-4716-9882-2d473f20beb6',
    'microsoft-to-do',
    'Microsoft To Do',
    'beta',
    'd65e4710-e8a4-4925-a879-6f7586073260',
    '2025-12-19T15:18:46.476801',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'fe8f198c-9b6e-4b9f-8137-5cabdf6ce0ea',
    'mixpanel',
    'Mixpanel',
    'beta',
    'ab6697f8-f1fc-4dcd-811c-23eee24a46fd',
    '2025-12-19T15:18:46.477173',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '186770e7-62d6-44eb-9bbf-b6d04d2c709b',
    'monday-com',
    'Monday.com',
    'beta',
    '09456384-30d0-452a-913b-72d9a88d5e7d',
    '2025-12-19T15:18:46.477604',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '0969c038-53bf-4c34-9c73-4edf31eb7ced',
    'netlify',
    'Netlify',
    'beta',
    'c92aecea-0c6a-41f4-8140-c0021e8dd179',
    '2025-12-19T15:18:46.478168',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'ba5665b6-a7ad-4b2f-a17c-ca7648677efd',
    'notion',
    'Notion',
    'beta',
    'b1880d06-4bd1-40b2-8042-c831583c0a93',
    '2025-12-19T15:18:46.478612',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'e1d659c6-d70a-403d-9204-e6b49f562938',
    'onedrive',
    'OneDrive',
    'beta',
    'd3045a2e-bab1-4733-b4ab-f7749074672c',
    '2025-12-19T15:18:46.479047',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '8f8f4c18-2a33-4456-92fd-0aaa6d56e31b',
    'openai',
    'OpenAI',
    'beta',
    '0280edf6-1071-48e1-9e4b-1b82736fb4c2',
    '2025-12-19T15:18:46.479499',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'a8ebe45b-5e00-4a51-9a91-33c41a402a06',
    'outlook-calendar',
    'Outlook Calendar',
    'beta',
    '671b764b-95bf-4c2d-bafd-f52e62435531',
    '2025-12-19T15:18:46.479963',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'a8f28764-6e2f-4c22-b21b-e12df083fd48',
    'paypal',
    'PayPal',
    'beta',
    '1cc2f4e6-5db8-4bd9-9da1-be79835c6cd5',
    '2025-12-19T15:18:46.480379',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '0c082976-aadf-4be1-a59c-4f5991d11363',
    'pinterest',
    'Pinterest',
    'beta',
    '320ae121-a2d3-41da-ad35-b43e4ee35947',
    '2025-12-19T15:18:46.480771',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '6a462435-9e8e-4969-a962-d452949cc2b8',
    'pipedrive',
    'Pipedrive',
    'beta',
    '6ff6500d-7b57-4bc1-89fa-4a24ab1a2459',
    '2025-12-19T15:18:46.481125',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'aca6ca3f-351c-434a-ab57-5153ffd1a7ff',
    'quickbooks',
    'QuickBooks',
    'beta',
    '1ec3909a-0b2a-46af-ab5e-db3ee309b427',
    '2025-12-19T15:18:46.481499',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '81b246c9-ba4f-462f-8520-a4b0ea1699c4',
    'razorpay',
    'Razorpay',
    'beta',
    '4b0b8ee7-fdef-4d77-9d85-8785030e21bf',
    '2025-12-19T15:18:46.481841',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '7e56c65b-61ab-425a-958c-6760cae9986c',
    'recurly',
    'Recurly',
    'beta',
    '7ccfcfe9-e5f8-4cfc-af51-dfaaab9a6bc5',
    '2025-12-19T15:18:46.482179',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'a76a4ac4-4978-4307-88be-f5dce3d0fcac',
    'reddit',
    'Reddit',
    'beta',
    '6368360e-c677-4735-b8f0-16f5d948a7cd',
    '2025-12-19T15:18:46.482554',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '46fb2f4e-8cd9-41b9-a6dd-c7672bdad244',
    'replicate',
    'Replicate',
    'beta',
    '7309dec4-6e18-4b7a-9f00-a6a91315c5e6',
    '2025-12-19T15:18:46.482982',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '24f96687-ef66-4164-82e6-35f748ef812d',
    's3-compatible-storage',
    'S3 Compatible Storage',
    'beta',
    'd22951ad-cd61-41d2-a8d7-3648e4349410',
    '2025-12-19T15:18:46.483402',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '171da5b6-6bc8-48e8-9eb8-2a9ef7e2dd95',
    'salesforce',
    'Salesforce',
    'beta',
    'fbe365ce-363a-4c1b-b3f0-3a14b15cd7c0',
    '2025-12-19T15:18:46.483740',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '2f4e14f1-9329-4ac6-a3fd-299a2498fcef',
    'segment',
    'Segment',
    'beta',
    '465d0cff-46ec-48be-adcc-b666daa5b73a',
    '2025-12-19T15:18:46.484097',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'dff6fb13-91b9-4744-85b4-3e3c510d1cc2',
    'sendgrid',
    'SendGrid',
    'beta',
    '6e1f0be6-8cd2-46cf-9f97-f473a9f0cc36',
    '2025-12-19T15:18:46.484476',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '7d118285-c2d1-4529-a6d7-185b0a993e6e',
    'shopify',
    'Shopify',
    'beta',
    'bbc4fad0-9848-4477-a839-40c1bec6e47d',
    '2025-12-19T15:18:46.484827',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '1936e2a3-ff81-4f00-8e1a-c922cc100283',
    'smartsheet',
    'Smartsheet',
    'beta',
    '5f72950e-bb6b-46dc-90bd-fb717629ce06',
    '2025-12-19T15:18:46.485202',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'e1fd0f95-0c2a-49f5-b773-f9686725044b',
    'snowflake',
    'Snowflake',
    'beta',
    '2e7c4933-8fd6-430f-8892-58e3d1250020',
    '2025-12-19T15:18:46.485551',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'f80d48ad-8074-4a18-b0c1-a564d5cd63a1',
    'square',
    'Square',
    'beta',
    '95f8d4b1-d1b1-4649-b364-da3e057e9a23',
    '2025-12-19T15:18:46.485931',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '748f8c66-1c8e-44ce-942b-b01744e2ff42',
    'stripe',
    'Stripe',
    'beta',
    'b08ab1a8-746b-43b3-a519-03941b8da2f2',
    '2025-12-19T15:18:46.486322',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '36bbc8c1-ba95-466a-bd0b-a732717768dd',
    'tableau',
    'Tableau',
    'beta',
    'eb5cb400-cbce-4fb0-a82c-45888f683f3e',
    '2025-12-19T15:18:46.486691',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '31ffd670-4a0b-4d18-a1fe-c8ba7ecbd709',
    'telegram',
    'Telegram',
    'beta',
    '4c7527cf-f209-4c74-8000-928f4b32aa12',
    '2025-12-19T15:18:46.487055',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'a2ca27dc-7cbe-46b1-9e86-0d50e923b96d',
    'terraform-cloud',
    'Terraform Cloud',
    'beta',
    '12ce8a0c-98b5-4869-bd3f-fc9c67953e06',
    '2025-12-19T15:18:46.487425',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '846d014f-e672-4c06-9e19-a879902c546a',
    'tiktok',
    'TikTok',
    'beta',
    '65a3fa3a-9c9c-4735-a5d9-f12fece379c1',
    '2025-12-19T15:18:46.487810',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '3c55279c-a0f2-4d2c-a4f2-082306fc6398',
    'todoist',
    'Todoist',
    'beta',
    '2bc66517-3b3c-426b-a3ed-8fecd3f7e56a',
    '2025-12-19T15:18:46.488158',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '305a7e96-514d-4fa3-b793-d4c41826d88a',
    'trello',
    'Trello',
    'beta',
    'ab7a407a-316f-4cc3-9b4e-55ac1acfc8fb',
    '2025-12-19T15:18:46.488510',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '197b3182-a5eb-4fdf-ac87-cc83edb21961',
    'twilio',
    'Twilio',
    'beta',
    '6cf8b148-3528-419e-8134-dc45ed474d84',
    '2025-12-19T15:18:46.488849',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'e64b620f-3fdf-4228-bff3-5e908ea271e6',
    'twitter',
    'Twitter / X',
    'beta',
    '59c5652e-4167-4449-ac6d-c835660a91a9',
    '2025-12-19T15:18:46.489199',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '612251b3-e8ad-42cf-86d0-7f28ed70c286',
    'vercel',
    'Vercel',
    'beta',
    '40a5f0c0-9b1a-48e1-a581-9ef5bd7e0fe5',
    '2025-12-19T15:18:46.489520',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '4f6bb34a-b5dd-4f68-bdf5-1b3b2c85b5f4',
    'whatsapp-business',
    'WhatsApp Business',
    'beta',
    '201f0a52-edad-4f85-8393-10ee2c4ea036',
    '2025-12-19T15:18:46.489857',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '3a795d0e-ffc0-479e-b523-bb629308748a',
    'when2meet',
    'When2Meet',
    'beta',
    'd17e6492-01c0-49e5-9a03-83ce9a7fdaf7',
    '2025-12-19T15:18:46.490195',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'fc564cfc-32c1-4447-a127-0a4338e8248d',
    'woocommerce',
    'WooCommerce',
    'beta',
    'bc9cacb2-bce5-4dbb-b150-ccf43d0a1847',
    '2025-12-19T15:18:46.490560',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '0e4fe189-5cbc-4a24-aa6f-2e5301e0e87c',
    'wrike',
    'Wrike',
    'beta',
    '976937e9-f7ca-4fca-9bb8-a87b7ae20777',
    '2025-12-19T15:18:46.490903',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'd53bdb86-369c-43fd-8dc8-bc1c8f234f14',
    'xero',
    'Xero',
    'beta',
    '59a69e37-ea7a-458d-96fb-5eb24e693c14',
    '2025-12-19T15:18:46.491280',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '139d545f-de74-4b5a-9976-aec4a00798fc',
    'youtube',
    'YouTube',
    'beta',
    'bffc6cdd-245b-4eef-9709-04f49d57b2ff',
    '2025-12-19T15:18:46.491641',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    'c43e7620-7551-44eb-990f-0524d938af3a',
    'zendesk',
    'Zendesk',
    'beta',
    '7a50f97b-a33f-407c-b561-d1a1a41ce9be',
    '2025-12-19T15:18:46.491962',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '8fdc4fdb-99fe-4eb8-8950-14f522ebd72e',
    'zoho-crm',
    'Zoho CRM',
    'beta',
    '5496a447-d0ea-490e-95a0-d875b17c03f7',
    '2025-12-19T15:18:46.492314',
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


INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '9f50696f-394c-4bbc-995d-012dac03c6c6',
    'zoom',
    'Zoom',
    'beta',
    '364aef36-e19e-4176-91bc-e0d696dde41a',
    '2025-12-19T15:18:46.492676',
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
VALUES (
    '0fe9423a-82d6-4af8-9978-7046b28c300e',
    '731167b1-7ed6-4d38-9e13-5a26d220104f',
    '1.0.0',
    '{"name": "ActiveCampaign", "slug": "activecampaign", "version": "1.0.0", "description": "Marketing automation and CRM", "category": "CRM & Sales", "status": "beta", "nango": {"enabled": true, "provider_key": "activecampaign"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/activecampaign", "token_url": "https://api.nango.dev/oauth/activecampaign/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.448519'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '800b1cd2-5356-45fd-8c81-872be89fd116',
    'd4612083-0f88-4869-b9d9-b5cd8ab0959d',
    '1.0.0',
    '{"name": "Airtable", "slug": "airtable", "version": "1.0.0", "description": "Database and collaboration platform", "category": "CRM & Sales", "status": "beta", "nango": {"enabled": true, "provider_key": "airtable"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/airtable", "token_url": "https://api.nango.dev/oauth/airtable/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.449395'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '22180232-f637-48c3-93d0-5c5e57266cb2',
    'cff19a4e-a16c-47ea-b544-7dfe581945f6',
    '1.0.0',
    '{"name": "Amazon S3", "slug": "amazon-s3", "version": "1.0.0", "description": "Object storage service", "category": "File Storage & Cloud", "status": "beta", "nango": {"enabled": true, "provider_key": "aws-s3"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/aws-s3", "token_url": "https://api.nango.dev/oauth/aws-s3/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.449867'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'ad527526-ecbb-4007-93c0-bc64c5fca61c',
    'b0905cd7-7676-42c5-bfda-e6c1675cc6d2',
    '1.0.0',
    '{"name": "Amplitude", "slug": "amplitude", "version": "1.0.0", "description": "Product analytics", "category": "Analytics & Data", "status": "beta", "nango": {"enabled": true, "provider_key": "amplitude"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/amplitude", "token_url": "https://api.nango.dev/oauth/amplitude/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.450549'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '2314c0d6-4307-44fb-b07e-cc2856699ecb',
    '6a2f95d8-28e8-4811-8804-6d528a0324c7',
    '1.0.0',
    '{"name": "Anthropic Claude", "slug": "anthropic-claude", "version": "1.0.0", "description": "AI assistant API", "category": "AI & Machine Learning", "status": "beta", "nango": {"enabled": true, "provider_key": "anthropic"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/anthropic", "token_url": "https://api.nango.dev/oauth/anthropic/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.451865'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'caec2fb1-1ffd-4f9a-afed-6b0ca869853b',
    'aa3b63d7-e5d6-4942-9363-87366b58e65d',
    '1.0.0',
    '{"name": "Apple Calendar", "slug": "apple-calendar", "version": "1.0.0", "description": "Apple calendar", "category": "Calendar & Scheduling", "status": "beta", "nango": {"enabled": true, "provider_key": "apple-calendar"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/apple-calendar", "token_url": "https://api.nango.dev/oauth/apple-calendar/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.452694'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'a8b57867-10e5-415b-a973-938bc2c07174',
    '47d2520c-5e7a-4322-9449-a5b5df0b0d27',
    '1.0.0',
    '{"name": "Asana", "slug": "asana", "version": "1.0.0", "description": "Project and task management", "category": "Project Management", "status": "beta", "nango": {"enabled": true, "provider_key": "asana"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/asana", "token_url": "https://api.nango.dev/oauth/asana/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.453120'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'bc99fa01-862c-4e68-8aa9-b27a1cad3091',
    '8de9176d-856b-4a20-9c52-dc24f184964a',
    '1.0.0',
    '{"name": "AWS", "slug": "aws", "version": "1.0.0", "description": "Amazon Web Services cloud platform", "category": "Development & Code", "status": "beta", "nango": {"enabled": true, "provider_key": "aws"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/aws", "token_url": "https://api.nango.dev/oauth/aws/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.453902'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'b733b012-9dea-4daa-a11b-39ead739793c',
    '49a7ce38-321f-4b4e-a15f-60435fb56e56',
    '1.0.0',
    '{"name": "Azure Blob Storage", "slug": "azure-blob-storage", "version": "1.0.0", "description": "Microsoft Azure object storage", "category": "File Storage & Cloud", "status": "beta", "nango": {"enabled": true, "provider_key": "azure"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/azure", "token_url": "https://api.nango.dev/oauth/azure/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.454358'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '63ddbf73-2c9a-4bb6-b93c-b282c2b470bd',
    'f7c56773-a32b-450a-baa0-210517770dcb',
    '1.0.0',
    '{"name": "Basecamp", "slug": "basecamp", "version": "1.0.0", "description": "Project management and team communication", "category": "Project Management", "status": "beta", "nango": {"enabled": true, "provider_key": "basecamp"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/basecamp", "token_url": "https://api.nango.dev/oauth/basecamp/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.455230'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '1edd729e-682c-4f61-8315-127379b303d5',
    '500f645d-7de0-4837-b51f-781c8fe062c9',
    '1.0.0',
    '{"name": "Bitbucket", "slug": "bitbucket", "version": "1.0.0", "description": "Git code hosting", "category": "Development & Code", "status": "beta", "nango": {"enabled": true, "provider_key": "bitbucket"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/bitbucket", "token_url": "https://api.nango.dev/oauth/bitbucket/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.455669'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '4571fe8e-08fd-4eff-ac3d-4c66d4aa9089',
    '3f63ab01-8427-45c3-bcaa-a344943492b4',
    '1.0.0',
    '{"name": "Box", "slug": "box", "version": "1.0.0", "description": "Cloud content management", "category": "File Storage & Cloud", "status": "beta", "nango": {"enabled": true, "provider_key": "box"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/box", "token_url": "https://api.nango.dev/oauth/box/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.456271'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'e636b029-c0f7-455e-9124-cbb6ef5af1b2',
    '6a428f0c-36d8-4d48-8d9c-e3ae7abddc0f',
    '1.0.0',
    '{"name": "Braintree", "slug": "braintree", "version": "1.0.0", "description": "Payment gateway", "category": "E-commerce & Payments", "status": "beta", "nango": {"enabled": true, "provider_key": "braintree"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/braintree", "token_url": "https://api.nango.dev/oauth/braintree/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.456648'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '9969a533-06a5-4025-8dd4-5b9cb278eed3',
    'e3abe8a6-4485-4a09-bf25-03cb7f2e110d',
    '1.0.0',
    '{"name": "Buffer", "slug": "buffer", "version": "1.0.0", "description": "Social media management", "category": "Social Media", "status": "beta", "nango": {"enabled": true, "provider_key": "buffer"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/buffer", "token_url": "https://api.nango.dev/oauth/buffer/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.457302'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'edc4b156-015f-47a0-8025-09db6e42eb9c',
    'c5674b59-28fe-42c9-b434-cfecd06068e4',
    '1.0.0',
    '{"name": "Calendly", "slug": "calendly", "version": "1.0.0", "description": "Schedule meetings and appointments", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "calendly"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/calendly", "token_url": "https://api.nango.dev/oauth/calendly/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.457655'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '6d6e09ed-03ed-43e4-9871-1e4d668c38e4',
    'eac9d497-7b47-468f-964b-4b3510b4283a',
    '1.0.0',
    '{"name": "Chargebee", "slug": "chargebee", "version": "1.0.0", "description": "Subscription management", "category": "E-commerce & Payments", "status": "beta", "nango": {"enabled": true, "provider_key": "chargebee"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/chargebee", "token_url": "https://api.nango.dev/oauth/chargebee/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.458307'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '8d5f2028-65fe-485a-ac01-87300bf22a26',
    '3f4db045-b402-4bb2-a778-d7532ed9c554',
    '1.0.0',
    '{"name": "CircleCI", "slug": "circleci", "version": "1.0.0", "description": "CI/CD platform", "category": "Development & Code", "status": "beta", "nango": {"enabled": true, "provider_key": "circleci"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/circleci", "token_url": "https://api.nango.dev/oauth/circleci/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.458678'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '3b4b5dd5-4cea-46d7-b994-771f5a1af7ce',
    'e7b0f029-acd2-4a43-9aff-a23592081877',
    '1.0.0',
    '{"name": "ClickUp", "slug": "clickup", "version": "1.0.0", "description": "All-in-one productivity platform", "category": "Project Management", "status": "beta", "nango": {"enabled": true, "provider_key": "clickup"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/clickup", "token_url": "https://api.nango.dev/oauth/clickup/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.459410'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'c542135b-fc75-4948-ab3a-d84e0c545f60',
    '13f84fbd-26e7-4ca6-9ccf-90cceb27d0b0',
    '1.0.0',
    '{"name": "Close", "slug": "close", "version": "1.0.0", "description": "Inside sales CRM", "category": "CRM & Sales", "status": "beta", "nango": {"enabled": true, "provider_key": "close"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/close", "token_url": "https://api.nango.dev/oauth/close/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.459776'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '8be275dc-179e-45d2-93dc-5c3b00e1c954',
    'c803bcc1-ef21-4202-89c5-d663de599252',
    '1.0.0',
    '{"name": "Cloudinary", "slug": "cloudinary", "version": "1.0.0", "description": "Image and video management", "category": "File Storage & Cloud", "status": "beta", "nango": {"enabled": true, "provider_key": "cloudinary"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/cloudinary", "token_url": "https://api.nango.dev/oauth/cloudinary/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.460568'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '6476bc17-cacf-4953-953c-2cc5376d717a',
    'bc16be88-2d2d-4a7c-8c9c-632f78ae96a7',
    '1.0.0',
    '{"name": "Cohere", "slug": "cohere", "version": "1.0.0", "description": "NLP and language models", "category": "AI & Machine Learning", "status": "beta", "nango": {"enabled": true, "provider_key": "cohere"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/cohere", "token_url": "https://api.nango.dev/oauth/cohere/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.461180'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '50c94f04-ae95-4ec7-876c-ae02298926df',
    'a3f672d2-9ac2-46cd-859a-d62ecbea5b02',
    '1.0.0',
    '{"name": "Copper", "slug": "copper", "version": "1.0.0", "description": "CRM built for Google Workspace", "category": "CRM & Sales", "status": "beta", "nango": {"enabled": true, "provider_key": "copper"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/copper", "token_url": "https://api.nango.dev/oauth/copper/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.461891'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '8ca8cf12-9a1b-46c2-9dc6-bf119e176f7a',
    '0fda879e-b345-4879-87c8-55c48a90ec6c',
    '1.0.0',
    '{"name": "Databricks", "slug": "databricks", "version": "1.0.0", "description": "Data analytics platform", "category": "Analytics & Data", "status": "beta", "nango": {"enabled": true, "provider_key": "databricks"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/databricks", "token_url": "https://api.nango.dev/oauth/databricks/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.462326'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'dc0f3536-9f2b-48d2-80a7-f47abf5e95b9',
    'f05a6fea-cdc9-4f49-af86-cf79687a4578',
    '1.0.0',
    '{"name": "Discord", "slug": "discord", "version": "1.0.0", "description": "Send messages and manage Discord servers", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "discord"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/discord", "token_url": "https://api.nango.dev/oauth/discord/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.463261'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '21365890-73cd-454d-a135-8232d5e6da6a',
    '11f29555-856a-4c46-a70a-341d94c732dd',
    '1.0.0',
    '{"name": "Docker Hub", "slug": "docker-hub", "version": "1.0.0", "description": "Container registry", "category": "Development & Code", "status": "beta", "nango": {"enabled": true, "provider_key": "docker"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/docker", "token_url": "https://api.nango.dev/oauth/docker/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.463758'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'c0c485f6-551b-4b2e-9d5a-d62ccf191e2e',
    'db7b70f7-a826-44d8-8c97-c53d47f646d7',
    '1.0.0',
    '{"name": "Doodle", "slug": "doodle", "version": "1.0.0", "description": "Meeting scheduling", "category": "Calendar & Scheduling", "status": "beta", "nango": {"enabled": true, "provider_key": "doodle"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/doodle", "token_url": "https://api.nango.dev/oauth/doodle/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.464158'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '50218e06-1e9a-4fff-bf07-137fd90f6b31',
    'fe31cbfe-9548-47b1-ad45-4ea9c00f62ec',
    '1.0.0',
    '{"name": "Dropbox", "slug": "dropbox", "version": "1.0.0", "description": "Cloud file storage", "category": "File Storage & Cloud", "status": "beta", "nango": {"enabled": true, "provider_key": "dropbox"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/dropbox", "token_url": "https://api.nango.dev/oauth/dropbox/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.464601'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '75abe127-926c-4b58-9b8d-bdb54418c585',
    'a93dc4b0-c431-45f0-8d5e-520125645de5',
    '1.0.0',
    '{"name": "Facebook", "slug": "facebook", "version": "1.0.0", "description": "Social media platform", "category": "Social Media", "status": "beta", "nango": {"enabled": true, "provider_key": "facebook"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/facebook", "token_url": "https://api.nango.dev/oauth/facebook/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.465381'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'cb89dde6-20b9-40ba-8697-48441775ba86',
    'aa91e0c0-baed-4ef8-9c0c-9dcb9ed5b465',
    '1.0.0',
    '{"name": "Freshdesk", "slug": "freshdesk", "version": "1.0.0", "description": "Customer support platform", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "freshdesk"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/freshdesk", "token_url": "https://api.nango.dev/oauth/freshdesk/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.465840'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '5eeeec2f-aa08-46e1-ae1d-9c8b6efebc51',
    'fd4bdd1f-7716-4d70-8207-d9c18c683646',
    '1.0.0',
    '{"name": "Front", "slug": "front", "version": "1.0.0", "description": "Shared inbox and customer communication", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "front"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/front", "token_url": "https://api.nango.dev/oauth/front/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.466337'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'c87180a7-4174-433c-9260-d2369a93d974',
    'a8f825fb-0587-4088-8084-832e147b7717',
    '1.0.0',
    '{"name": "GitHub", "slug": "github", "version": "1.0.0", "description": "Code hosting and version control", "category": "Development & Code", "status": "beta", "nango": {"enabled": true, "provider_key": "github"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/github", "token_url": "https://api.nango.dev/oauth/github/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.467051'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '7cd720ac-a592-4863-8a1a-ab6ab862a70b',
    'a63acdc0-23fc-4cd6-9a69-52f5df6176c5',
    '1.0.0',
    '{"name": "GitLab", "slug": "gitlab", "version": "1.0.0", "description": "DevOps platform", "category": "Development & Code", "status": "beta", "nango": {"enabled": true, "provider_key": "gitlab"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/gitlab", "token_url": "https://api.nango.dev/oauth/gitlab/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.467403'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '3eabe463-8670-4164-b5b3-682a46a411da',
    '3b80cbe3-44cf-4f5b-bdc9-7cd7db4cd875',
    '1.0.0',
    '{"name": "Gmail", "slug": "gmail", "version": "1.0.0", "description": "Send and receive emails via Gmail API", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "gmail"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/gmail", "token_url": "https://api.nango.dev/oauth/gmail/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.467856'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '2e10ea8d-d658-4f1c-9193-d52d760bb083',
    '2a40eabe-5f7e-4bf1-9508-318721e23806',
    '1.0.0',
    '{"name": "Google AI", "slug": "google-ai", "version": "1.0.0", "description": "Google AI services", "category": "AI & Machine Learning", "status": "beta", "nango": {"enabled": true, "provider_key": "google-ai"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/google-ai", "token_url": "https://api.nango.dev/oauth/google-ai/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.468221'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'b78cb827-f298-4c39-81cf-0cc93e68c799',
    '7e4e3e8f-1a12-494c-8938-5f5d8509a06f',
    '1.0.0',
    '{"name": "Google Analytics", "slug": "google-analytics", "version": "1.0.0", "description": "Web analytics platform", "category": "Analytics & Data", "status": "beta", "nango": {"enabled": true, "provider_key": "google-analytics"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/google-analytics", "token_url": "https://api.nango.dev/oauth/google-analytics/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.468570'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '90b21c47-86cf-4c36-b294-e4359659ee9a',
    '5db0fef4-d35f-4bad-8f86-a9bc3acca575',
    '1.0.0',
    '{"name": "Google BigQuery", "slug": "google-bigquery", "version": "1.0.0", "description": "Cloud data warehouse", "category": "Analytics & Data", "status": "beta", "nango": {"enabled": true, "provider_key": "bigquery"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/bigquery", "token_url": "https://api.nango.dev/oauth/bigquery/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.468960'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '559f9b67-c701-485a-8dc8-59d3dbbc1210',
    '16172528-b227-4ee7-bc55-81eda35d1d01',
    '1.0.0',
    '{"name": "Google Calendar", "slug": "google-calendar", "version": "1.0.0", "description": "Calendar and scheduling", "category": "Calendar & Scheduling", "status": "beta", "nango": {"enabled": true, "provider_key": "google-calendar"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/google-calendar", "token_url": "https://api.nango.dev/oauth/google-calendar/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.469362'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '12892e5e-ce86-4db9-b913-eca838f782e9',
    '03450f37-04f8-4f59-bff8-7a74704d4e09',
    '1.0.0',
    '{"name": "Google Cloud Storage", "slug": "google-cloud-storage", "version": "1.0.0", "description": "Google Cloud object storage", "category": "File Storage & Cloud", "status": "beta", "nango": {"enabled": true, "provider_key": "gcs"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/gcs", "token_url": "https://api.nango.dev/oauth/gcs/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.469794'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '6d6ee581-4662-4f84-8f3a-629885e170cf',
    '64be0963-f83d-4520-b3f0-0beba9d1d0f6',
    '1.0.0',
    '{"name": "Google Drive", "slug": "google-drive", "version": "1.0.0", "description": "Cloud file storage and sharing", "category": "File Storage & Cloud", "status": "beta", "nango": {"enabled": true, "provider_key": "google-drive"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/google-drive", "token_url": "https://api.nango.dev/oauth/google-drive/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.470218'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'e6f97e03-0592-4a4c-be5a-9da90337759e',
    '1e3ac982-379f-4d67-bacf-576f653ff756',
    '1.0.0',
    '{"name": "Help Scout", "slug": "help-scout", "version": "1.0.0", "description": "Customer support and help desk", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "helpscout"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/helpscout", "token_url": "https://api.nango.dev/oauth/helpscout/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.470602'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '3ea60d49-18ce-4743-b3dc-ce2c6f2b5e6d',
    'c6c6dc58-ac82-4941-b570-ca65ce756abc',
    '1.0.0',
    '{"name": "HubSpot", "slug": "hubspot", "version": "1.0.0", "description": "Marketing, sales, and service platform", "category": "CRM & Sales", "status": "beta", "nango": {"enabled": true, "provider_key": "hubspot"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/hubspot", "token_url": "https://api.nango.dev/oauth/hubspot/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.471034'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'f7c912a0-d8f6-4c51-adc1-7128375261af',
    '48d9a5bc-65e1-45a3-a02e-a2f41bf06fea',
    '1.0.0',
    '{"name": "Hugging Face", "slug": "hugging-face", "version": "1.0.0", "description": "ML model hosting", "category": "AI & Machine Learning", "status": "beta", "nango": {"enabled": true, "provider_key": "huggingface"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/huggingface", "token_url": "https://api.nango.dev/oauth/huggingface/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.471429'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'cf1c7c4a-7244-4942-a9b1-33d9ee15d88c',
    '9c783954-de36-4828-a6be-faf1e2703fa5',
    '1.0.0',
    '{"name": "Imgur", "slug": "imgur", "version": "1.0.0", "description": "Image hosting and sharing", "category": "File Storage & Cloud", "status": "beta", "nango": {"enabled": true, "provider_key": "imgur"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/imgur", "token_url": "https://api.nango.dev/oauth/imgur/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.471792'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'dab5677e-8c4d-4ed8-acca-0c295593a924',
    '340c47a8-3e8b-4304-a58b-b6e9cf9973fe',
    '1.0.0',
    '{"name": "Insightly", "slug": "insightly", "version": "1.0.0", "description": "CRM and project management", "category": "CRM & Sales", "status": "beta", "nango": {"enabled": true, "provider_key": "insightly"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/insightly", "token_url": "https://api.nango.dev/oauth/insightly/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.472138'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '3421afc0-72b6-46a7-b8bb-48dd30038a43',
    '039a6970-0052-40dd-a257-9d4d1fa30488',
    '1.0.0',
    '{"name": "Instagram", "slug": "instagram", "version": "1.0.0", "description": "Photo and video sharing", "category": "Social Media", "status": "beta", "nango": {"enabled": true, "provider_key": "instagram"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/instagram", "token_url": "https://api.nango.dev/oauth/instagram/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.472492'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'd8d58f4a-a4d2-4d3d-8acb-eb5c92579f01',
    '6a48f45c-860e-4965-b3bb-4cd7b2cd2648',
    '1.0.0',
    '{"name": "Intercom", "slug": "intercom", "version": "1.0.0", "description": "Manage customer conversations", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "intercom"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/intercom", "token_url": "https://api.nango.dev/oauth/intercom/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.472842'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '7791bbf6-5f9f-442f-b65b-44813ac16968',
    '956bd446-492e-4c2d-8004-e55a4ae56c4f',
    '1.0.0',
    '{"name": "Jenkins", "slug": "jenkins", "version": "1.0.0", "description": "CI/CD automation server", "category": "Development & Code", "status": "beta", "nango": {"enabled": true, "provider_key": "jenkins"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/jenkins", "token_url": "https://api.nango.dev/oauth/jenkins/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.473180'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'd7f0c8b2-049d-4819-8103-f75746d54b5e',
    '72265992-ea36-4b7d-9e57-548396708b2d',
    '1.0.0',
    '{"name": "Jira", "slug": "jira", "version": "1.0.0", "description": "Issue tracking and project management", "category": "Project Management", "status": "beta", "nango": {"enabled": true, "provider_key": "jira"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/jira", "token_url": "https://api.nango.dev/oauth/jira/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.473537'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '05da1321-fe02-44fb-a685-3f65db156c49',
    'ac9fa87d-599d-4e49-9385-46444e8b365f',
    '1.0.0',
    '{"name": "Kubernetes", "slug": "kubernetes", "version": "1.0.0", "description": "Container orchestration", "category": "Development & Code", "status": "beta", "nango": {"enabled": true, "provider_key": "kubernetes"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/kubernetes", "token_url": "https://api.nango.dev/oauth/kubernetes/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.473870'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '375226c1-8a8b-4d93-b582-089673cb3218',
    '9a641c6d-de26-4612-bcfa-bc01742b0e34',
    '1.0.0',
    '{"name": "Linear", "slug": "linear", "version": "1.0.0", "description": "Issue tracking for software teams", "category": "Project Management", "status": "beta", "nango": {"enabled": true, "provider_key": "linear"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/linear", "token_url": "https://api.nango.dev/oauth/linear/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.474188'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'fc79070a-1dce-403b-ae22-c8c257214038',
    'cab0c8cf-6c85-421d-8921-6b79d212a149',
    '1.0.0',
    '{"name": "LinkedIn", "slug": "linkedin", "version": "1.0.0", "description": "Professional networking", "category": "Social Media", "status": "beta", "nango": {"enabled": true, "provider_key": "linkedin"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/linkedin", "token_url": "https://api.nango.dev/oauth/linkedin/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.474597'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'f4ea8724-9500-4354-bf69-5d5036525c33',
    'b07898f0-3c6c-45ae-9b20-626a5347e742',
    '1.0.0',
    '{"name": "Looker", "slug": "looker", "version": "1.0.0", "description": "Business intelligence", "category": "Analytics & Data", "status": "beta", "nango": {"enabled": true, "provider_key": "looker"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/looker", "token_url": "https://api.nango.dev/oauth/looker/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.474915'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'bccd518f-0ace-4e87-8883-b62bac64f63a',
    '924c5d19-2bee-4846-b6dd-d320d1600be5',
    '1.0.0',
    '{"name": "Mailchimp", "slug": "mailchimp", "version": "1.0.0", "description": "Manage email campaigns and subscribers", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "mailchimp"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/mailchimp", "token_url": "https://api.nango.dev/oauth/mailchimp/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.475276'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'b6d47602-656c-42ec-84e8-5ae3ffc11a50',
    '671564bd-990d-49c1-ab31-4cb86b99a008',
    '1.0.0',
    '{"name": "Medium", "slug": "medium", "version": "1.0.0", "description": "Online publishing platform", "category": "Social Media", "status": "beta", "nango": {"enabled": true, "provider_key": "medium"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/medium", "token_url": "https://api.nango.dev/oauth/medium/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.475616'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '7d7d57e9-920d-47dc-88ee-ae69324ac84a',
    'a8e4ab6f-70e4-4f85-838f-481b7842fcb2',
    '1.0.0',
    '{"name": "Metabase", "slug": "metabase", "version": "1.0.0", "description": "Business intelligence tool", "category": "Analytics & Data", "status": "beta", "nango": {"enabled": true, "provider_key": "metabase"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/metabase", "token_url": "https://api.nango.dev/oauth/metabase/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.475964'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'e6450245-6b4d-4fd7-8534-0a5f2fe57b74',
    'b075f357-b32c-4f7e-9675-720baaa00071',
    '1.0.0',
    '{"name": "Microsoft Teams", "slug": "microsoft-teams", "version": "1.0.0", "description": "Send messages and manage Teams channels", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "microsoft-teams"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/microsoft-teams", "token_url": "https://api.nango.dev/oauth/microsoft-teams/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.476330'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'd65e4710-e8a4-4925-a879-6f7586073260',
    '992f03e4-ee14-4716-9882-2d473f20beb6',
    '1.0.0',
    '{"name": "Microsoft To Do", "slug": "microsoft-to-do", "version": "1.0.0", "description": "Task management app", "category": "Project Management", "status": "beta", "nango": {"enabled": true, "provider_key": "microsoft-todo"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/microsoft-todo", "token_url": "https://api.nango.dev/oauth/microsoft-todo/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.476801'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'ab6697f8-f1fc-4dcd-811c-23eee24a46fd',
    'fe8f198c-9b6e-4b9f-8137-5cabdf6ce0ea',
    '1.0.0',
    '{"name": "Mixpanel", "slug": "mixpanel", "version": "1.0.0", "description": "Product analytics", "category": "Analytics & Data", "status": "beta", "nango": {"enabled": true, "provider_key": "mixpanel"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/mixpanel", "token_url": "https://api.nango.dev/oauth/mixpanel/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.477173'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '09456384-30d0-452a-913b-72d9a88d5e7d',
    '186770e7-62d6-44eb-9bbf-b6d04d2c709b',
    '1.0.0',
    '{"name": "Monday.com", "slug": "monday-com", "version": "1.0.0", "description": "Work management platform", "category": "CRM & Sales", "status": "beta", "nango": {"enabled": true, "provider_key": "monday"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/monday", "token_url": "https://api.nango.dev/oauth/monday/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.477604'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'c92aecea-0c6a-41f4-8140-c0021e8dd179',
    '0969c038-53bf-4c34-9c73-4edf31eb7ced',
    '1.0.0',
    '{"name": "Netlify", "slug": "netlify", "version": "1.0.0", "description": "Web development platform", "category": "Development & Code", "status": "beta", "nango": {"enabled": true, "provider_key": "netlify"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/netlify", "token_url": "https://api.nango.dev/oauth/netlify/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.478168'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'b1880d06-4bd1-40b2-8042-c831583c0a93',
    'ba5665b6-a7ad-4b2f-a17c-ca7648677efd',
    '1.0.0',
    '{"name": "Notion", "slug": "notion", "version": "1.0.0", "description": "All-in-one workspace", "category": "Productivity & Notes", "status": "beta", "nango": {"enabled": true, "provider_key": "notion"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/notion", "token_url": "https://api.nango.dev/oauth/notion/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.478612'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'd3045a2e-bab1-4733-b4ab-f7749074672c',
    'e1d659c6-d70a-403d-9204-e6b49f562938',
    '1.0.0',
    '{"name": "OneDrive", "slug": "onedrive", "version": "1.0.0", "description": "Microsoft cloud storage", "category": "File Storage & Cloud", "status": "beta", "nango": {"enabled": true, "provider_key": "onedrive"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/onedrive", "token_url": "https://api.nango.dev/oauth/onedrive/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.479047'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '0280edf6-1071-48e1-9e4b-1b82736fb4c2',
    '8f8f4c18-2a33-4456-92fd-0aaa6d56e31b',
    '1.0.0',
    '{"name": "OpenAI", "slug": "openai", "version": "1.0.0", "description": "AI models and APIs", "category": "AI & Machine Learning", "status": "beta", "nango": {"enabled": true, "provider_key": "openai"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/openai", "token_url": "https://api.nango.dev/oauth/openai/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.479499'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '671b764b-95bf-4c2d-bafd-f52e62435531',
    'a8ebe45b-5e00-4a51-9a91-33c41a402a06',
    '1.0.0',
    '{"name": "Outlook Calendar", "slug": "outlook-calendar", "version": "1.0.0", "description": "Microsoft calendar", "category": "Calendar & Scheduling", "status": "beta", "nango": {"enabled": true, "provider_key": "microsoft-calendar"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/microsoft-calendar", "token_url": "https://api.nango.dev/oauth/microsoft-calendar/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.479963'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '1cc2f4e6-5db8-4bd9-9da1-be79835c6cd5',
    'a8f28764-6e2f-4c22-b21b-e12df083fd48',
    '1.0.0',
    '{"name": "PayPal", "slug": "paypal", "version": "1.0.0", "description": "Online payment processing", "category": "E-commerce & Payments", "status": "beta", "nango": {"enabled": true, "provider_key": "paypal"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/paypal", "token_url": "https://api.nango.dev/oauth/paypal/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.480379'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '320ae121-a2d3-41da-ad35-b43e4ee35947',
    '0c082976-aadf-4be1-a59c-4f5991d11363',
    '1.0.0',
    '{"name": "Pinterest", "slug": "pinterest", "version": "1.0.0", "description": "Image sharing and discovery", "category": "Social Media", "status": "beta", "nango": {"enabled": true, "provider_key": "pinterest"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/pinterest", "token_url": "https://api.nango.dev/oauth/pinterest/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.480771'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '6ff6500d-7b57-4bc1-89fa-4a24ab1a2459',
    '6a462435-9e8e-4969-a962-d452949cc2b8',
    '1.0.0',
    '{"name": "Pipedrive", "slug": "pipedrive", "version": "1.0.0", "description": "Sales CRM and pipeline management", "category": "CRM & Sales", "status": "beta", "nango": {"enabled": true, "provider_key": "pipedrive"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/pipedrive", "token_url": "https://api.nango.dev/oauth/pipedrive/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.481125'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '1ec3909a-0b2a-46af-ab5e-db3ee309b427',
    'aca6ca3f-351c-434a-ab57-5153ffd1a7ff',
    '1.0.0',
    '{"name": "QuickBooks", "slug": "quickbooks", "version": "1.0.0", "description": "Accounting software", "category": "E-commerce & Payments", "status": "beta", "nango": {"enabled": true, "provider_key": "quickbooks"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/quickbooks", "token_url": "https://api.nango.dev/oauth/quickbooks/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.481499'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '4b0b8ee7-fdef-4d77-9d85-8785030e21bf',
    '81b246c9-ba4f-462f-8520-a4b0ea1699c4',
    '1.0.0',
    '{"name": "Razorpay", "slug": "razorpay", "version": "1.0.0", "description": "Payment gateway for India", "category": "E-commerce & Payments", "status": "beta", "nango": {"enabled": true, "provider_key": "razorpay"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/razorpay", "token_url": "https://api.nango.dev/oauth/razorpay/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.481841'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '7ccfcfe9-e5f8-4cfc-af51-dfaaab9a6bc5',
    '7e56c65b-61ab-425a-958c-6760cae9986c',
    '1.0.0',
    '{"name": "Recurly", "slug": "recurly", "version": "1.0.0", "description": "Subscription billing platform", "category": "E-commerce & Payments", "status": "beta", "nango": {"enabled": true, "provider_key": "recurly"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/recurly", "token_url": "https://api.nango.dev/oauth/recurly/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.482179'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '6368360e-c677-4735-b8f0-16f5d948a7cd',
    'a76a4ac4-4978-4307-88be-f5dce3d0fcac',
    '1.0.0',
    '{"name": "Reddit", "slug": "reddit", "version": "1.0.0", "description": "Social news and discussion", "category": "Social Media", "status": "beta", "nango": {"enabled": true, "provider_key": "reddit"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/reddit", "token_url": "https://api.nango.dev/oauth/reddit/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.482554'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '7309dec4-6e18-4b7a-9f00-a6a91315c5e6',
    '46fb2f4e-8cd9-41b9-a6dd-c7672bdad244',
    '1.0.0',
    '{"name": "Replicate", "slug": "replicate", "version": "1.0.0", "description": "ML model hosting", "category": "AI & Machine Learning", "status": "beta", "nango": {"enabled": true, "provider_key": "replicate"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/replicate", "token_url": "https://api.nango.dev/oauth/replicate/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.482982'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'd22951ad-cd61-41d2-a8d7-3648e4349410',
    '24f96687-ef66-4164-82e6-35f748ef812d',
    '1.0.0',
    '{"name": "S3 Compatible Storage", "slug": "s3-compatible-storage", "version": "1.0.0", "description": "S3-compatible object storage", "category": "File Storage & Cloud", "status": "beta", "nango": {"enabled": true, "provider_key": "s3-compatible"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/s3-compatible", "token_url": "https://api.nango.dev/oauth/s3-compatible/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.483402'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'fbe365ce-363a-4c1b-b3f0-3a14b15cd7c0',
    '171da5b6-6bc8-48e8-9eb8-2a9ef7e2dd95',
    '1.0.0',
    '{"name": "Salesforce", "slug": "salesforce", "version": "1.0.0", "description": "CRM platform for sales and customer management", "category": "CRM & Sales", "status": "beta", "nango": {"enabled": true, "provider_key": "salesforce"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/salesforce", "token_url": "https://api.nango.dev/oauth/salesforce/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.483740'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '465d0cff-46ec-48be-adcc-b666daa5b73a',
    '2f4e14f1-9329-4ac6-a3fd-299a2498fcef',
    '1.0.0',
    '{"name": "Segment", "slug": "segment", "version": "1.0.0", "description": "Customer data platform", "category": "Analytics & Data", "status": "beta", "nango": {"enabled": true, "provider_key": "segment"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/segment", "token_url": "https://api.nango.dev/oauth/segment/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.484097'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '6e1f0be6-8cd2-46cf-9f97-f473a9f0cc36',
    'dff6fb13-91b9-4744-85b4-3e3c510d1cc2',
    '1.0.0',
    '{"name": "SendGrid", "slug": "sendgrid", "version": "1.0.0", "description": "Send transactional emails", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "sendgrid"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/sendgrid", "token_url": "https://api.nango.dev/oauth/sendgrid/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.484476'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'bbc4fad0-9848-4477-a839-40c1bec6e47d',
    '7d118285-c2d1-4529-a6d7-185b0a993e6e',
    '1.0.0',
    '{"name": "Shopify", "slug": "shopify", "version": "1.0.0", "description": "E-commerce platform", "category": "E-commerce & Payments", "status": "beta", "nango": {"enabled": true, "provider_key": "shopify"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/shopify", "token_url": "https://api.nango.dev/oauth/shopify/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.484827'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '5f72950e-bb6b-46dc-90bd-fb717629ce06',
    '1936e2a3-ff81-4f00-8e1a-c922cc100283',
    '1.0.0',
    '{"name": "Smartsheet", "slug": "smartsheet", "version": "1.0.0", "description": "Work execution platform", "category": "Project Management", "status": "beta", "nango": {"enabled": true, "provider_key": "smartsheet"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/smartsheet", "token_url": "https://api.nango.dev/oauth/smartsheet/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.485202'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '2e7c4933-8fd6-430f-8892-58e3d1250020',
    'e1fd0f95-0c2a-49f5-b773-f9686725044b',
    '1.0.0',
    '{"name": "Snowflake", "slug": "snowflake", "version": "1.0.0", "description": "Cloud data warehouse", "category": "Analytics & Data", "status": "beta", "nango": {"enabled": true, "provider_key": "snowflake"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/snowflake", "token_url": "https://api.nango.dev/oauth/snowflake/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.485551'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '95f8d4b1-d1b1-4649-b364-da3e057e9a23',
    'f80d48ad-8074-4a18-b0c1-a564d5cd63a1',
    '1.0.0',
    '{"name": "Square", "slug": "square", "version": "1.0.0", "description": "Payment processing and POS", "category": "E-commerce & Payments", "status": "beta", "nango": {"enabled": true, "provider_key": "square"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/square", "token_url": "https://api.nango.dev/oauth/square/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.485931'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'b08ab1a8-746b-43b3-a519-03941b8da2f2',
    '748f8c66-1c8e-44ce-942b-b01744e2ff42',
    '1.0.0',
    '{"name": "Stripe", "slug": "stripe", "version": "1.0.0", "description": "Payment processing platform", "category": "Payments", "status": "beta", "nango": {"enabled": true, "provider_key": "stripe"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/stripe", "token_url": "https://api.nango.dev/oauth/stripe/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.486322'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'eb5cb400-cbce-4fb0-a82c-45888f683f3e',
    '36bbc8c1-ba95-466a-bd0b-a732717768dd',
    '1.0.0',
    '{"name": "Tableau", "slug": "tableau", "version": "1.0.0", "description": "Data visualization", "category": "Analytics & Data", "status": "beta", "nango": {"enabled": true, "provider_key": "tableau"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/tableau", "token_url": "https://api.nango.dev/oauth/tableau/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.486691'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '4c7527cf-f209-4c74-8000-928f4b32aa12',
    '31ffd670-4a0b-4d18-a1fe-c8ba7ecbd709',
    '1.0.0',
    '{"name": "Telegram", "slug": "telegram", "version": "1.0.0", "description": "Send Telegram messages", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "telegram"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/telegram", "token_url": "https://api.nango.dev/oauth/telegram/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.487055'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '12ce8a0c-98b5-4869-bd3f-fc9c67953e06',
    'a2ca27dc-7cbe-46b1-9e86-0d50e923b96d',
    '1.0.0',
    '{"name": "Terraform Cloud", "slug": "terraform-cloud", "version": "1.0.0", "description": "Infrastructure as code", "category": "Development & Code", "status": "beta", "nango": {"enabled": true, "provider_key": "terraform"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/terraform", "token_url": "https://api.nango.dev/oauth/terraform/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.487425'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '65a3fa3a-9c9c-4735-a5d9-f12fece379c1',
    '846d014f-e672-4c06-9e19-a879902c546a',
    '1.0.0',
    '{"name": "TikTok", "slug": "tiktok", "version": "1.0.0", "description": "Short-form video platform", "category": "Social Media", "status": "beta", "nango": {"enabled": true, "provider_key": "tiktok"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/tiktok", "token_url": "https://api.nango.dev/oauth/tiktok/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.487810'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '2bc66517-3b3c-426b-a3ed-8fecd3f7e56a',
    '3c55279c-a0f2-4d2c-a4f2-082306fc6398',
    '1.0.0',
    '{"name": "Todoist", "slug": "todoist", "version": "1.0.0", "description": "Task management and to-do lists", "category": "Project Management", "status": "beta", "nango": {"enabled": true, "provider_key": "todoist"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/todoist", "token_url": "https://api.nango.dev/oauth/todoist/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.488158'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'ab7a407a-316f-4cc3-9b4e-55ac1acfc8fb',
    '305a7e96-514d-4fa3-b793-d4c41826d88a',
    '1.0.0',
    '{"name": "Trello", "slug": "trello", "version": "1.0.0", "description": "Kanban board project management", "category": "Project Management", "status": "beta", "nango": {"enabled": true, "provider_key": "trello"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/trello", "token_url": "https://api.nango.dev/oauth/trello/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.488510'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '6cf8b148-3528-419e-8134-dc45ed474d84',
    '197b3182-a5eb-4fdf-ac87-cc83edb21961',
    '1.0.0',
    '{"name": "Twilio", "slug": "twilio", "version": "1.0.0", "description": "Send SMS and make phone calls", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "twilio"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/twilio", "token_url": "https://api.nango.dev/oauth/twilio/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.488849'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '59c5652e-4167-4449-ac6d-c835660a91a9',
    'e64b620f-3fdf-4228-bff3-5e908ea271e6',
    '1.0.0',
    '{"name": "Twitter / X", "slug": "twitter", "version": "1.0.0", "description": "Social media platform", "category": "Social Media", "status": "beta", "nango": {"enabled": true, "provider_key": "twitter"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/twitter", "token_url": "https://api.nango.dev/oauth/twitter/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.489199'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '40a5f0c0-9b1a-48e1-a581-9ef5bd7e0fe5',
    '612251b3-e8ad-42cf-86d0-7f28ed70c286',
    '1.0.0',
    '{"name": "Vercel", "slug": "vercel", "version": "1.0.0", "description": "Frontend deployment platform", "category": "Development & Code", "status": "beta", "nango": {"enabled": true, "provider_key": "vercel"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/vercel", "token_url": "https://api.nango.dev/oauth/vercel/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.489520'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '201f0a52-edad-4f85-8393-10ee2c4ea036',
    '4f6bb34a-b5dd-4f68-bdf5-1b3b2c85b5f4',
    '1.0.0',
    '{"name": "WhatsApp Business", "slug": "whatsapp-business", "version": "1.0.0", "description": "Send WhatsApp messages", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "whatsapp"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/whatsapp", "token_url": "https://api.nango.dev/oauth/whatsapp/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.489857'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'd17e6492-01c0-49e5-9a03-83ce9a7fdaf7',
    '3a795d0e-ffc0-479e-b523-bb629308748a',
    '1.0.0',
    '{"name": "When2Meet", "slug": "when2meet", "version": "1.0.0", "description": "Meeting scheduling", "category": "Productivity & Notes", "status": "beta", "nango": {"enabled": true, "provider_key": "when2meet"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/when2meet", "token_url": "https://api.nango.dev/oauth/when2meet/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.490195'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'bc9cacb2-bce5-4dbb-b150-ccf43d0a1847',
    'fc564cfc-32c1-4447-a127-0a4338e8248d',
    '1.0.0',
    '{"name": "WooCommerce", "slug": "woocommerce", "version": "1.0.0", "description": "WordPress e-commerce plugin", "category": "E-commerce & Payments", "status": "beta", "nango": {"enabled": true, "provider_key": "woocommerce"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/woocommerce", "token_url": "https://api.nango.dev/oauth/woocommerce/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.490560'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '976937e9-f7ca-4fca-9bb8-a87b7ae20777',
    '0e4fe189-5cbc-4a24-aa6f-2e5301e0e87c',
    '1.0.0',
    '{"name": "Wrike", "slug": "wrike", "version": "1.0.0", "description": "Work management and collaboration", "category": "Project Management", "status": "beta", "nango": {"enabled": true, "provider_key": "wrike"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/wrike", "token_url": "https://api.nango.dev/oauth/wrike/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.490903'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '59a69e37-ea7a-458d-96fb-5eb24e693c14',
    'd53bdb86-369c-43fd-8dc8-bc1c8f234f14',
    '1.0.0',
    '{"name": "Xero", "slug": "xero", "version": "1.0.0", "description": "Cloud accounting platform", "category": "E-commerce & Payments", "status": "beta", "nango": {"enabled": true, "provider_key": "xero"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/xero", "token_url": "https://api.nango.dev/oauth/xero/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.491280'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    'bffc6cdd-245b-4eef-9709-04f49d57b2ff',
    '139d545f-de74-4b5a-9976-aec4a00798fc',
    '1.0.0',
    '{"name": "YouTube", "slug": "youtube", "version": "1.0.0", "description": "Video sharing platform", "category": "Social Media", "status": "beta", "nango": {"enabled": true, "provider_key": "youtube"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/youtube", "token_url": "https://api.nango.dev/oauth/youtube/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.491641'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '7a50f97b-a33f-407c-b561-d1a1a41ce9be',
    'c43e7620-7551-44eb-990f-0524d938af3a',
    '1.0.0',
    '{"name": "Zendesk", "slug": "zendesk", "version": "1.0.0", "description": "Manage support tickets", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "zendesk"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/zendesk", "token_url": "https://api.nango.dev/oauth/zendesk/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.491962'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '5496a447-d0ea-490e-95a0-d875b17c03f7',
    '8fdc4fdb-99fe-4eb8-8950-14f522ebd72e',
    '1.0.0',
    '{"name": "Zoho CRM", "slug": "zoho-crm", "version": "1.0.0", "description": "Cloud-based CRM platform", "category": "CRM & Sales", "status": "beta", "nango": {"enabled": true, "provider_key": "zoho"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/zoho", "token_url": "https://api.nango.dev/oauth/zoho/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.492314'
)
ON CONFLICT DO NOTHING;


INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '364aef36-e19e-4176-91bc-e0d696dde41a',
    '9f50696f-394c-4bbc-995d-012dac03c6c6',
    '1.0.0',
    '{"name": "Zoom", "slug": "zoom", "version": "1.0.0", "description": "Create and manage Zoom meetings", "category": "Communication & Collaboration", "status": "beta", "nango": {"enabled": true, "provider_key": "zoom"}, "oauth": {"authorization_url": "https://api.nango.dev/oauth/zoom", "token_url": "https://api.nango.dev/oauth/zoom/token", "default_scopes": [], "authorization_params": {}}, "actions": {"test_connection": {"name": "Test Connection", "description": "Test the connection to the service", "method": "GET", "endpoint": "/test"}}, "triggers": {}}'::jsonb,
    NULL,
    '2025-12-19T15:18:46.492676'
)
ON CONFLICT DO NOTHING;


COMMIT;

-- Verify migration
SELECT COUNT(*) as total_connectors FROM connector;
SELECT COUNT(*) as total_versions FROM connectorversion;
