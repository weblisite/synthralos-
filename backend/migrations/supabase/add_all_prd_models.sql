-- Migration: add_all_prd_models
-- Generated from Alembic migration

-- Running upgrade 1a31ce608336 -> c4cd6f5a4f64

CREATE TABLE agentcontextcache (
    id UUID NOT NULL,
    agent_id VARCHAR(255) NOT NULL,
    context_key VARCHAR(255) NOT NULL,
    context_data JSONB,
    expires_at TIMESTAMP WITHOUT TIME ZONE,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id)
);

CREATE INDEX ix_agentcontextcache_agent_id ON agentcontextcache (agent_id);

CREATE INDEX ix_agentcontextcache_context_key ON agentcontextcache (context_key);

CREATE TABLE agentframeworkconfig (
    id UUID NOT NULL,
    framework VARCHAR(100) NOT NULL,
    config JSONB,
    is_enabled BOOLEAN NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (framework)
);

CREATE TABLE agenttask (
    id UUID NOT NULL,
    agent_framework VARCHAR(100) NOT NULL,
    task_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    started_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITHOUT TIME ZONE,
    error_message VARCHAR,
    PRIMARY KEY (id)
);

CREATE TABLE browsersession (
    id UUID NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    browser_tool VARCHAR(100) NOT NULL,
    proxy_id VARCHAR(255),
    status VARCHAR(50) NOT NULL,
    started_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    closed_at TIMESTAMP WITHOUT TIME ZONE,
    PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_browsersession_session_id ON browsersession (session_id);

CREATE TABLE changedetection (
    id UUID NOT NULL,
    url VARCHAR(2000) NOT NULL,
    diff_hash VARCHAR(64) NOT NULL,
    previous_content VARCHAR(1000000),
    current_content VARCHAR(1000000),
    detected_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id)
);

CREATE INDEX ix_changedetection_diff_hash ON changedetection (diff_hash);

CREATE INDEX ix_changedetection_url ON changedetection (url);

CREATE TABLE codeexecution (
    id UUID NOT NULL,
    runtime VARCHAR(100) NOT NULL,
    language VARCHAR(50) NOT NULL,
    code VARCHAR(100000) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    status VARCHAR(50) NOT NULL,
    exit_code INTEGER,
    duration_ms INTEGER NOT NULL,
    memory_mb INTEGER,
    started_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITHOUT TIME ZONE,
    error_message VARCHAR,
    PRIMARY KEY (id)
);

CREATE TABLE connector (
    id UUID NOT NULL,
    slug VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    latest_version_id UUID,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_connector_slug ON connector (slug);

CREATE TABLE contentchecksum (
    id UUID NOT NULL,
    url VARCHAR(2000) NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    last_scraped_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id)
);

CREATE INDEX ix_contentchecksum_content_hash ON contentchecksum (content_hash);

CREATE INDEX ix_contentchecksum_url ON contentchecksum (url);

CREATE TABLE domainprofile (
    id UUID NOT NULL,
    domain VARCHAR(255) NOT NULL,
    max_requests_per_hour INTEGER NOT NULL,
    requires_login BOOLEAN NOT NULL,
    captcha_likelihood VARCHAR(50) NOT NULL,
    scroll_needed BOOLEAN NOT NULL,
    idle_before_click FLOAT NOT NULL,
    config JSONB,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_domainprofile_domain ON domainprofile (domain);

CREATE TABLE eventlog (
    id UUID NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    context JSONB,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id)
);

CREATE INDEX ix_eventlog_created_at ON eventlog (created_at);

CREATE INDEX ix_eventlog_event_type ON eventlog (event_type);

CREATE TABLE modelcostlog (
    id UUID NOT NULL,
    agent_id UUID,
    model VARCHAR(100) NOT NULL,
    tokens_input INTEGER NOT NULL,
    tokens_output INTEGER NOT NULL,
    usd_cost FLOAT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id)
);

CREATE INDEX ix_modelcostlog_agent_id ON modelcostlog (agent_id);

CREATE INDEX ix_modelcostlog_created_at ON modelcostlog (created_at);

CREATE INDEX ix_modelcostlog_model ON modelcostlog (model);

CREATE TABLE ocrjob (
    id UUID NOT NULL,
    document_url VARCHAR(1000) NOT NULL,
    engine VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    result JSONB,
    started_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITHOUT TIME ZONE,
    error_message VARCHAR,
    PRIMARY KEY (id)
);

CREATE TABLE osintstream (
    id UUID NOT NULL,
    platform VARCHAR(100) NOT NULL,
    keywords JSONB,
    engine VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE proxylog (
    id UUID NOT NULL,
    ip_id VARCHAR(255) NOT NULL,
    agent_id VARCHAR(255),
    domain_scraped VARCHAR(255) NOT NULL,
    status_code INTEGER,
    retry_count INTEGER NOT NULL,
    block_reason VARCHAR(500),
    latency_ms INTEGER NOT NULL,
    timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id)
);

CREATE INDEX ix_proxylog_domain_scraped ON proxylog (domain_scraped);

CREATE INDEX ix_proxylog_ip_id ON proxylog (ip_id);

CREATE TABLE scrapejob (
    id UUID NOT NULL,
    url VARCHAR(2000) NOT NULL,
    engine VARCHAR(100) NOT NULL,
    proxy_id VARCHAR(255),
    status VARCHAR(50) NOT NULL,
    result JSONB,
    started_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITHOUT TIME ZONE,
    error_message VARCHAR,
    PRIMARY KEY (id)
);

CREATE TABLE toolusagelog (
    id UUID NOT NULL,
    tool_id VARCHAR(255) NOT NULL,
    tool_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    latency_ms INTEGER NOT NULL,
    error_message VARCHAR,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id)
);

CREATE INDEX ix_toolusagelog_created_at ON toolusagelog (created_at);

CREATE INDEX ix_toolusagelog_tool_id ON toolusagelog (tool_id);

CREATE INDEX ix_toolusagelog_tool_type ON toolusagelog (tool_type);

CREATE TABLE agenttasklog (
    id UUID NOT NULL,
    task_id UUID NOT NULL,
    level VARCHAR(20) NOT NULL,
    message VARCHAR(5000) NOT NULL,
    timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(task_id) REFERENCES agenttask (id) ON DELETE CASCADE
);

CREATE INDEX ix_agenttasklog_task_id ON agenttasklog (task_id);

CREATE TABLE browseraction (
    id UUID NOT NULL,
    session_id UUID NOT NULL,
    action_type VARCHAR(100) NOT NULL,
    action_data JSONB,
    result JSONB,
    timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(session_id) REFERENCES browsersession (id) ON DELETE CASCADE
);

CREATE TABLE codesandbox (
    id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    runtime VARCHAR(100) NOT NULL,
    config JSONB,
    owner_id UUID NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(owner_id) REFERENCES "user" (id) ON DELETE CASCADE
);

CREATE TABLE codetoolregistry (
    id UUID NOT NULL,
    tool_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    description VARCHAR(1000),
    code VARCHAR(100000) NOT NULL,
    input_schema JSONB,
    output_schema JSONB,
    runtime VARCHAR(100) NOT NULL,
    owner_id UUID NOT NULL,
    usage_count INTEGER NOT NULL,
    is_deprecated BOOLEAN NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(owner_id) REFERENCES "user" (id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX ix_codetoolregistry_tool_id ON codetoolregistry (tool_id);

CREATE TABLE connectorversion (
    id UUID NOT NULL,
    connector_id UUID NOT NULL,
    version VARCHAR(50) NOT NULL,
    manifest JSONB,
    wheel_url VARCHAR(1000),
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(connector_id) REFERENCES connector (id) ON DELETE CASCADE
);

CREATE INDEX ix_connectorversion_connector_id ON connectorversion (connector_id);

CREATE TABLE ocrdocument (
    id UUID NOT NULL,
    job_id UUID NOT NULL,
    file_url VARCHAR(1000) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    document_metadata JSONB,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(job_id) REFERENCES ocrjob (id) ON DELETE CASCADE
);

CREATE TABLE ocrresult (
    id UUID NOT NULL,
    job_id UUID NOT NULL,
    extracted_text VARCHAR(100000) NOT NULL,
    structured_data JSONB,
    confidence_score FLOAT,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(job_id) REFERENCES ocrjob (id) ON DELETE CASCADE
);

CREATE TABLE osintalert (
    id UUID NOT NULL,
    stream_id UUID,
    alert_type VARCHAR(100) NOT NULL,
    message VARCHAR(5000) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    is_read BOOLEAN NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(stream_id) REFERENCES osintstream (id) ON DELETE SET NULL
);

CREATE TABLE osintsignal (
    id UUID NOT NULL,
    stream_id UUID NOT NULL,
    source VARCHAR(100) NOT NULL,
    author VARCHAR(255),
    text VARCHAR(10000) NOT NULL,
    media JSONB,
    link VARCHAR(2000),
    sentiment_score FLOAT,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(stream_id) REFERENCES osintstream (id) ON DELETE CASCADE
);

CREATE TABLE ragindex (
    id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    vector_db_type VARCHAR(50) NOT NULL,
    owner_id UUID NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(owner_id) REFERENCES "user" (id) ON DELETE CASCADE
);

CREATE TABLE scraperesult (
    id UUID NOT NULL,
    job_id UUID NOT NULL,
    content VARCHAR(1000000) NOT NULL,
    html VARCHAR(10000000),
    result_metadata JSONB,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(job_id) REFERENCES scrapejob (id) ON DELETE CASCADE
);

CREATE TABLE workflow (
    name VARCHAR(255) NOT NULL,
    description VARCHAR(1000),
    is_active BOOLEAN NOT NULL,
    version INTEGER NOT NULL,
    trigger_config JSONB,
    graph_config JSONB,
    id UUID NOT NULL,
    owner_id UUID NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(owner_id) REFERENCES "user" (id) ON DELETE CASCADE
);

CREATE TABLE ragdocument (
    id UUID NOT NULL,
    index_id UUID NOT NULL,
    content VARCHAR(100000) NOT NULL,
    document_metadata JSONB,
    embedding JSONB,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(index_id) REFERENCES ragindex (id) ON DELETE CASCADE
);

CREATE TABLE ragfinetunejob (
    id UUID NOT NULL,
    index_id UUID NOT NULL,
    status VARCHAR(50) NOT NULL,
    config JSONB,
    started_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITHOUT TIME ZONE,
    error_message VARCHAR,
    PRIMARY KEY (id),
    FOREIGN KEY(index_id) REFERENCES ragindex (id)
);

CREATE TABLE ragquery (
    id UUID NOT NULL,
    index_id UUID NOT NULL,
    query_text VARCHAR(5000) NOT NULL,
    results JSONB,
    latency_ms INTEGER NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(index_id) REFERENCES ragindex (id) ON DELETE CASCADE
);

CREATE INDEX ix_ragquery_index_id ON ragquery (index_id);

CREATE INDEX ix_ragquery_created_at ON ragquery (created_at);

CREATE TABLE webhooksubscription (
    id UUID NOT NULL,
    connector_version_id UUID NOT NULL,
    trigger_id VARCHAR(255) NOT NULL,
    tenant_id UUID NOT NULL,
    endpoint_secret VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(connector_version_id) REFERENCES connectorversion (id) ON DELETE CASCADE
);

CREATE TABLE workflowexecution (
    id UUID NOT NULL,
    workflow_id UUID NOT NULL,
    workflow_version INTEGER NOT NULL,
    execution_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    started_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITHOUT TIME ZONE,
    error_message VARCHAR,
    current_node_id VARCHAR(255),
    execution_state JSONB,
    retry_count INTEGER NOT NULL,
    next_retry_at TIMESTAMP WITHOUT TIME ZONE,
    PRIMARY KEY (id),
    FOREIGN KEY(workflow_id) REFERENCES workflow (id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX ix_workflowexecution_execution_id ON workflowexecution (execution_id);

CREATE INDEX ix_workflowexecution_workflow_id ON workflowexecution (workflow_id);

CREATE INDEX ix_workflowexecution_status ON workflowexecution (status);

CREATE INDEX ix_workflowexecution_started_at ON workflowexecution (started_at);

CREATE TABLE workflownode (
    id UUID NOT NULL,
    workflow_id UUID NOT NULL,
    node_type VARCHAR(100) NOT NULL,
    node_id VARCHAR(255) NOT NULL,
    position_x FLOAT NOT NULL,
    position_y FLOAT NOT NULL,
    config JSONB,
    PRIMARY KEY (id),
    FOREIGN KEY(workflow_id) REFERENCES workflow (id) ON DELETE CASCADE
);

CREATE TABLE workflowschedule (
    id UUID NOT NULL,
    workflow_id UUID NOT NULL,
    cron_expression VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL,
    next_run_at TIMESTAMP WITHOUT TIME ZONE,
    last_run_at TIMESTAMP WITHOUT TIME ZONE,
    PRIMARY KEY (id),
    FOREIGN KEY(workflow_id) REFERENCES workflow (id) ON DELETE CASCADE
);

CREATE TABLE executionlog (
    id UUID NOT NULL,
    execution_id UUID NOT NULL,
    node_id VARCHAR(255) NOT NULL,
    level VARCHAR(20) NOT NULL,
    message VARCHAR(5000) NOT NULL,
    timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(execution_id) REFERENCES workflowexecution (id) ON DELETE CASCADE
);

CREATE INDEX ix_executionlog_execution_id ON executionlog (execution_id);

CREATE INDEX ix_executionlog_timestamp ON executionlog (timestamp);

CREATE TABLE ragfinetunedataset (
    id UUID NOT NULL,
    job_id UUID NOT NULL,
    dataset_url VARCHAR(1000) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(job_id) REFERENCES ragfinetunejob (id) ON DELETE CASCADE
);

CREATE TABLE ragswitchlog (
    id UUID NOT NULL,
    query_id UUID,
    routing_decision VARCHAR(100) NOT NULL,
    routing_reason VARCHAR(500) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(query_id) REFERENCES ragquery (id) ON DELETE SET NULL
);

CREATE TABLE workflowsignal (
    id UUID NOT NULL,
    execution_id UUID NOT NULL,
    signal_type VARCHAR(100) NOT NULL,
    signal_data JSONB,
    received_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    processed BOOLEAN NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(execution_id) REFERENCES workflowexecution (id) ON DELETE CASCADE
);

ALTER TABLE "user" DROP CONSTRAINT user_email_key;

DROP INDEX ix_user_email;

CREATE UNIQUE INDEX ix_user_email ON "user" (email);

UPDATE alembic_version SET version_num='c4cd6f5a4f64' WHERE alembic_version.version_num = '1a31ce608336';
