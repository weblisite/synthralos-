-- Migration: c4cd6f5a4f64 - Add all PRD models
-- This migration creates all the tables for the PRD models

-- First, create tables without foreign keys
CREATE TABLE IF NOT EXISTS agentcontextcache (
    id UUID PRIMARY KEY,
    agent_id VARCHAR(255) NOT NULL,
    context_key VARCHAR(255) NOT NULL,
    context_data JSONB,
    expires_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_agentcontextcache_agent_id ON agentcontextcache (agent_id);
CREATE INDEX IF NOT EXISTS ix_agentcontextcache_context_key ON agentcontextcache (context_key);

CREATE TABLE IF NOT EXISTS agentframeworkconfig (
    id UUID PRIMARY KEY,
    framework VARCHAR(100) NOT NULL UNIQUE,
    config JSONB,
    is_enabled BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS agenttask (
    id UUID PRIMARY KEY,
    agent_framework VARCHAR(100) NOT NULL,
    task_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS browsersession (
    id UUID PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL UNIQUE,
    browser_tool VARCHAR(100) NOT NULL,
    proxy_id VARCHAR(255),
    status VARCHAR(50) NOT NULL,
    started_at TIMESTAMP NOT NULL,
    closed_at TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_browsersession_session_id ON browsersession (session_id);

CREATE TABLE IF NOT EXISTS changedetection (
    id UUID PRIMARY KEY,
    url VARCHAR(2000) NOT NULL,
    diff_hash VARCHAR(64) NOT NULL,
    previous_content TEXT,
    current_content TEXT,
    detected_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_changedetection_diff_hash ON changedetection (diff_hash);
CREATE INDEX IF NOT EXISTS ix_changedetection_url ON changedetection (url);

CREATE TABLE IF NOT EXISTS codeexecution (
    id UUID PRIMARY KEY,
    runtime VARCHAR(100) NOT NULL,
    language VARCHAR(50) NOT NULL,
    code TEXT NOT NULL,
    input_data JSONB,
    output_data JSONB,
    status VARCHAR(50) NOT NULL,
    exit_code INTEGER,
    duration_ms INTEGER NOT NULL,
    memory_mb INTEGER,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS connector (
    id UUID PRIMARY KEY,
    slug VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    latest_version_id UUID,
    created_at TIMESTAMP NOT NULL,
    owner_id UUID REFERENCES "user"(id) ON DELETE CASCADE,
    is_platform BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES "user"(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS ix_connector_slug ON connector (slug);

CREATE TABLE IF NOT EXISTS contentchecksum (
    id UUID PRIMARY KEY,
    url VARCHAR(2000) NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    last_scraped_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_contentchecksum_content_hash ON contentchecksum (content_hash);
CREATE INDEX IF NOT EXISTS ix_contentchecksum_url ON contentchecksum (url);

CREATE TABLE IF NOT EXISTS domainprofile (
    id UUID PRIMARY KEY,
    domain VARCHAR(255) NOT NULL UNIQUE,
    max_requests_per_hour INTEGER NOT NULL,
    requires_login BOOLEAN NOT NULL,
    captcha_likelihood VARCHAR(50) NOT NULL,
    scroll_needed BOOLEAN NOT NULL,
    idle_before_click DOUBLE PRECISION NOT NULL,
    config JSONB,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_domainprofile_domain ON domainprofile (domain);

CREATE TABLE IF NOT EXISTS eventlog (
    id UUID PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    context JSONB,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_eventlog_created_at ON eventlog (created_at);
CREATE INDEX IF NOT EXISTS ix_eventlog_event_type ON eventlog (event_type);

CREATE TABLE IF NOT EXISTS modelcostlog (
    id UUID PRIMARY KEY,
    agent_id UUID,
    model VARCHAR(100) NOT NULL,
    tokens_input INTEGER NOT NULL,
    tokens_output INTEGER NOT NULL,
    usd_cost DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_modelcostlog_agent_id ON modelcostlog (agent_id);
CREATE INDEX IF NOT EXISTS ix_modelcostlog_created_at ON modelcostlog (created_at);
CREATE INDEX IF NOT EXISTS ix_modelcostlog_model ON modelcostlog (model);

CREATE TABLE IF NOT EXISTS ocrjob (
    id UUID PRIMARY KEY,
    document_url VARCHAR(1000) NOT NULL,
    engine VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    result JSONB,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS osintstream (
    id UUID PRIMARY KEY,
    platform VARCHAR(100) NOT NULL,
    keywords JSONB,
    engine VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS proxylog (
    id UUID PRIMARY KEY,
    ip_id VARCHAR(255) NOT NULL,
    agent_id VARCHAR(255),
    domain_scraped VARCHAR(255) NOT NULL,
    status_code INTEGER,
    retry_count INTEGER NOT NULL,
    block_reason VARCHAR(500),
    latency_ms INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_proxylog_domain_scraped ON proxylog (domain_scraped);
CREATE INDEX IF NOT EXISTS ix_proxylog_ip_id ON proxylog (ip_id);

CREATE TABLE IF NOT EXISTS scrapejob (
    id UUID PRIMARY KEY,
    url VARCHAR(2000) NOT NULL,
    engine VARCHAR(100) NOT NULL,
    proxy_id VARCHAR(255),
    status VARCHAR(50) NOT NULL,
    result JSONB,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS toolusagelog (
    id UUID PRIMARY KEY,
    tool_id VARCHAR(255) NOT NULL,
    tool_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    latency_ms INTEGER NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_toolusagelog_created_at ON toolusagelog (created_at);
CREATE INDEX IF NOT EXISTS ix_toolusagelog_tool_id ON toolusagelog (tool_id);
CREATE INDEX IF NOT EXISTS ix_toolusagelog_tool_type ON toolusagelog (tool_type);

-- Tables with foreign keys
CREATE TABLE IF NOT EXISTS agenttasklog (
    id UUID PRIMARY KEY,
    task_id UUID NOT NULL REFERENCES agenttask(id) ON DELETE CASCADE,
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_agenttasklog_task_id ON agenttasklog (task_id);

CREATE TABLE IF NOT EXISTS browseraction (
    id UUID PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES browsersession(id) ON DELETE CASCADE,
    action_type VARCHAR(100) NOT NULL,
    action_data JSONB,
    result JSONB,
    timestamp TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS codesandbox (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    runtime VARCHAR(100) NOT NULL,
    config JSONB,
    owner_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS codetoolregistry (
    id UUID PRIMARY KEY,
    tool_id VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    description TEXT,
    code TEXT NOT NULL,
    input_schema JSONB,
    output_schema JSONB,
    runtime VARCHAR(100) NOT NULL,
    owner_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    usage_count INTEGER NOT NULL DEFAULT 0,
    is_deprecated BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_codetoolregistry_tool_id ON codetoolregistry (tool_id);

CREATE TABLE IF NOT EXISTS connectorversion (
    id UUID PRIMARY KEY,
    connector_id UUID NOT NULL REFERENCES connector(id) ON DELETE CASCADE,
    version VARCHAR(50) NOT NULL,
    manifest JSONB,
    wheel_url VARCHAR(1000),
    created_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_connectorversion_connector_id ON connectorversion (connector_id);

CREATE TABLE IF NOT EXISTS ocrdocument (
    id UUID PRIMARY KEY,
    job_id UUID NOT NULL REFERENCES ocrjob(id) ON DELETE CASCADE,
    file_url VARCHAR(1000) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    document_metadata JSONB,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS ocrresult (
    id UUID PRIMARY KEY,
    job_id UUID NOT NULL REFERENCES ocrjob(id) ON DELETE CASCADE,
    extracted_text TEXT NOT NULL,
    structured_data JSONB,
    confidence_score DOUBLE PRECISION,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS osintalert (
    id UUID PRIMARY KEY,
    stream_id UUID REFERENCES osintstream(id) ON DELETE SET NULL,
    alert_type VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    severity VARCHAR(50) NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS osintsignal (
    id UUID PRIMARY KEY,
    stream_id UUID NOT NULL REFERENCES osintstream(id) ON DELETE CASCADE,
    source VARCHAR(100) NOT NULL,
    author VARCHAR(255),
    text TEXT NOT NULL,
    media JSONB,
    link VARCHAR(2000),
    sentiment_score DOUBLE PRECISION,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS ragindex (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    vector_db_type VARCHAR(50) NOT NULL,
    owner_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS scraperesult (
    id UUID PRIMARY KEY,
    job_id UUID NOT NULL REFERENCES scrapejob(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    html TEXT,
    result_metadata JSONB,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS workflow (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    version INTEGER NOT NULL DEFAULT 1,
    trigger_config JSONB,
    graph_config JSONB,
    owner_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS ragdocument (
    id UUID PRIMARY KEY,
    index_id UUID NOT NULL REFERENCES ragindex(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    document_metadata JSONB,
    embedding JSONB,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS ragfinetunejob (
    id UUID PRIMARY KEY,
    index_id UUID NOT NULL REFERENCES ragindex(id),
    status VARCHAR(50) NOT NULL,
    config JSONB,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS ragquery (
    id UUID PRIMARY KEY,
    index_id UUID NOT NULL REFERENCES ragindex(id) ON DELETE CASCADE,
    query_text TEXT NOT NULL,
    results JSONB,
    latency_ms INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_ragquery_index_id ON ragquery (index_id);
CREATE INDEX IF NOT EXISTS ix_ragquery_created_at ON ragquery (created_at);

CREATE TABLE IF NOT EXISTS webhooksubscription (
    id UUID PRIMARY KEY,
    connector_version_id UUID NOT NULL REFERENCES connectorversion(id) ON DELETE CASCADE,
    trigger_id VARCHAR(255) NOT NULL,
    tenant_id UUID NOT NULL,
    endpoint_secret VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS workflowexecution (
    id UUID PRIMARY KEY,
    workflow_id UUID NOT NULL REFERENCES workflow(id) ON DELETE CASCADE,
    workflow_version INTEGER NOT NULL,
    execution_id VARCHAR(255) NOT NULL UNIQUE,
    status VARCHAR(50) NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    error_message TEXT,
    current_node_id VARCHAR(255),
    execution_state JSONB,
    retry_count INTEGER NOT NULL DEFAULT 0,
    next_retry_at TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_workflowexecution_execution_id ON workflowexecution (execution_id);
CREATE INDEX IF NOT EXISTS ix_workflowexecution_workflow_id ON workflowexecution (workflow_id);
CREATE INDEX IF NOT EXISTS ix_workflowexecution_status ON workflowexecution (status);
CREATE INDEX IF NOT EXISTS ix_workflowexecution_started_at ON workflowexecution (started_at);

CREATE TABLE IF NOT EXISTS workflownode (
    id UUID PRIMARY KEY,
    workflow_id UUID NOT NULL REFERENCES workflow(id) ON DELETE CASCADE,
    node_type VARCHAR(100) NOT NULL,
    node_id VARCHAR(255) NOT NULL,
    position_x DOUBLE PRECISION NOT NULL,
    position_y DOUBLE PRECISION NOT NULL,
    config JSONB
);

CREATE TABLE IF NOT EXISTS workflowschedule (
    id UUID PRIMARY KEY,
    workflow_id UUID NOT NULL REFERENCES workflow(id) ON DELETE CASCADE,
    cron_expression VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    next_run_at TIMESTAMP,
    last_run_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS executionlog (
    id UUID PRIMARY KEY,
    execution_id UUID NOT NULL REFERENCES workflowexecution(id) ON DELETE CASCADE,
    node_id VARCHAR(255) NOT NULL,
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_executionlog_execution_id ON executionlog (execution_id);
CREATE INDEX IF NOT EXISTS ix_executionlog_timestamp ON executionlog (timestamp);

CREATE TABLE IF NOT EXISTS ragfinetunedataset (
    id UUID PRIMARY KEY,
    job_id UUID NOT NULL REFERENCES ragfinetunejob(id) ON DELETE CASCADE,
    dataset_url VARCHAR(1000) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS ragswitchlog (
    id UUID PRIMARY KEY,
    query_id UUID REFERENCES ragquery(id) ON DELETE SET NULL,
    routing_decision VARCHAR(100) NOT NULL,
    routing_reason VARCHAR(500) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS workflowsignal (
    id UUID PRIMARY KEY,
    execution_id UUID NOT NULL REFERENCES workflowexecution(id) ON DELETE CASCADE,
    signal_type VARCHAR(100) NOT NULL,
    signal_data JSONB,
    received_at TIMESTAMP NOT NULL,
    processed BOOLEAN NOT NULL DEFAULT FALSE
);

-- Update user email index to be unique
DROP INDEX IF EXISTS ix_user_email;
CREATE UNIQUE INDEX ix_user_email ON "user" (email);

-- Update Alembic version
UPDATE alembic_version SET version_num = 'c4cd6f5a4f64';

