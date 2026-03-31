-- ============================================================================
-- SYNTHARRA PRODUCTION SELF-HEALING LOOP
-- Supabase Schema Definition
-- ============================================================================

-- ============================================================================
-- TABLE: deployment_cycles
-- Track each nightly deployment cycle
-- ============================================================================
CREATE TABLE IF NOT EXISTS deployment_cycles (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    cycle_date DATE NOT NULL,
    cycle_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(50) NOT NULL,
    -- ENUM: 'healthy', 'issues_detected', 'validation_failed', 'deployment_success', 'deployment_failed', 'monitoring_passed', 'monitoring_failed', 'auto_rollback'
    
    -- Diagnosis results
    issues_detected INT DEFAULT 0,
    top_issue_id VARCHAR(100),
    top_issue_severity VARCHAR(50),
    
    -- Deployment results
    agents_targeted INT DEFAULT 0,
    agents_successful INT DEFAULT 0,
    agents_failed INT DEFAULT 0,
    agents_rolled_back INT DEFAULT 0,
    
    -- Cost tracking
    diagnosis_cost DECIMAL(10, 4) DEFAULT 0,
    validation_cost DECIMAL(10, 4) DEFAULT 0,
    deployment_cost DECIMAL(10, 4) DEFAULT 0,
    monitoring_cost DECIMAL(10, 4) DEFAULT 0,
    total_cost DECIMAL(10, 4) DEFAULT 0,
    
    -- Timing
    duration_mins FLOAT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Version
    deployed_version VARCHAR(20),
    
    -- Error tracking
    error_message TEXT,
    error_details JSONB,
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_deployment_cycles_date ON deployment_cycles(cycle_date DESC);
CREATE INDEX idx_deployment_cycles_status ON deployment_cycles(status);
CREATE INDEX idx_deployment_cycles_version ON deployment_cycles(deployed_version);

-- ============================================================================
-- TABLE: deployment_backups
-- Save agent state before each deployment
-- ============================================================================
CREATE TABLE IF NOT EXISTS deployment_backups (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    cycle_id BIGINT REFERENCES deployment_cycles(id),
    version_tag VARCHAR(20) NOT NULL,
    backup_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Backup data
    agent_configs JSONB NOT NULL,
    agent_count INT,
    
    -- Status
    backup_status VARCHAR(50) DEFAULT 'completed',
    restored BOOLEAN DEFAULT FALSE,
    restored_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_deployment_backups_version ON deployment_backups(version_tag);
CREATE INDEX idx_deployment_backups_cycle ON deployment_backups(cycle_id);

-- ============================================================================
-- TABLE: deployment_agents
-- Track deployment status per agent
-- ============================================================================
CREATE TABLE IF NOT EXISTS deployment_agents (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    cycle_id BIGINT REFERENCES deployment_cycles(id),
    
    -- Agent info
    agent_id VARCHAR(100) NOT NULL,
    client_id VARCHAR(100),
    company_name VARCHAR(255),
    
    -- Deployment tracking
    deployment_status VARCHAR(50),
    -- ENUM: 'pending', 'validating', 'backing_up', 'deploying', 'deployed', 'verifying', 'verified', 'failed', 'rolled_back'
    
    -- Deployment details
    version_deployed VARCHAR(20),
    deployment_attempt INT DEFAULT 1,
    deployment_error TEXT,
    
    -- Variables injected
    variables_injected JSONB,
    variables_valid BOOLEAN,
    
    -- Monitoring
    call_count_post_deploy INT DEFAULT 0,
    success_rate_post_deploy FLOAT,
    errors_detected INT DEFAULT 0,
    
    -- Timing
    deploy_started_at TIMESTAMP WITH TIME ZONE,
    deploy_completed_at TIMESTAMP WITH TIME ZONE,
    deploy_duration_ms INT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_deployment_agents_cycle ON deployment_agents(cycle_id);
CREATE INDEX idx_deployment_agents_agent_id ON deployment_agents(agent_id);
CREATE INDEX idx_deployment_agents_status ON deployment_agents(deployment_status);

-- ============================================================================
-- TABLE: validation_checks
-- Track validation results for each cycle
-- ============================================================================
CREATE TABLE IF NOT EXISTS validation_checks (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    cycle_id BIGINT REFERENCES deployment_cycles(id),
    
    -- Check type
    check_type VARCHAR(100) NOT NULL,
    -- ENUM: 'variable_injection', 'master_fix', 'flow_syntax', 'say_prefix', 'emergency_routing', 'config', 'emergency_stop'
    
    -- Results
    passed BOOLEAN NOT NULL,
    error_message TEXT,
    error_details JSONB,
    
    -- Details
    agents_tested INT,
    agents_failed INT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_validation_checks_cycle ON validation_checks(cycle_id);
CREATE INDEX idx_validation_checks_type ON validation_checks(check_type);

-- ============================================================================
-- TABLE: monitoring_events
-- Real-time monitoring events during post-deployment window
-- ============================================================================
CREATE TABLE IF NOT EXISTS monitoring_events (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    cycle_id BIGINT REFERENCES deployment_cycles(id),
    
    -- Event info
    event_type VARCHAR(50) NOT NULL,
    -- ENUM: 'check_performed', 'call_monitored', 'error_detected', 'spike_detected', 'agent_healthy', 'rollback_triggered'
    
    event_severity VARCHAR(50),
    -- ENUM: 'info', 'warning', 'error', 'critical'
    
    -- Details
    agent_id VARCHAR(100),
    check_number INT,
    
    call_success_rate FLOAT,
    call_count INT,
    error_count INT,
    
    details JSONB,
    action_taken VARCHAR(255),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_monitoring_events_cycle ON monitoring_events(cycle_id);
CREATE INDEX idx_monitoring_events_type ON monitoring_events(event_type);
CREATE INDEX idx_monitoring_events_agent ON monitoring_events(agent_id);

-- ============================================================================
-- TABLE: issue_detections
-- Track detected issues from each diagnosis run
-- ============================================================================
CREATE TABLE IF NOT EXISTS issue_detections (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    cycle_id BIGINT REFERENCES deployment_cycles(id),
    
    -- Issue info
    issue_id VARCHAR(100) NOT NULL,
    issue_type VARCHAR(100),
    severity VARCHAR(50),
    
    -- Statistics
    frequency INT,
    total_instances INT,
    affected_agents INT,
    
    -- Description
    description TEXT,
    affected_node VARCHAR(100),
    affected_field VARCHAR(100),
    
    -- Example
    example_call_id VARCHAR(255),
    
    -- Fix tracking
    fix_generated BOOLEAN DEFAULT FALSE,
    fix_validated BOOLEAN DEFAULT FALSE,
    fix_deployed BOOLEAN DEFAULT FALSE,
    fix_version VARCHAR(20),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_issue_detections_cycle ON issue_detections(cycle_id);
CREATE INDEX idx_issue_detections_type ON issue_detections(issue_type);
CREATE INDEX idx_issue_detections_severity ON issue_detections(severity);

-- ============================================================================
-- TABLE: cost_tracking
-- Monthly cost tracking and analysis
-- ============================================================================
CREATE TABLE IF NOT EXISTS cost_tracking (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    
    -- Period
    month_year DATE NOT NULL,
    
    -- Costs
    total_diagnosis_cost DECIMAL(10, 4) DEFAULT 0,
    total_validation_cost DECIMAL(10, 4) DEFAULT 0,
    total_deployment_cost DECIMAL(10, 4) DEFAULT 0,
    total_monitoring_cost DECIMAL(10, 4) DEFAULT 0,
    total_cost DECIMAL(10, 4) DEFAULT 0,
    
    -- Metrics
    cycles_run INT DEFAULT 0,
    issues_fixed INT DEFAULT 0,
    agents_improved INT DEFAULT 0,
    
    -- Average cost
    average_cost_per_cycle DECIMAL(10, 4),
    cost_per_agent_per_month DECIMAL(10, 4),
    
    notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_cost_tracking_month ON cost_tracking(month_year);

-- ============================================================================
-- TABLE: alerts_sent
-- Log all alerts sent to admin
-- ============================================================================
CREATE TABLE IF NOT EXISTS alerts_sent (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    cycle_id BIGINT REFERENCES deployment_cycles(id),
    
    -- Alert details
    event_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50),
    
    -- Recipients
    sent_to_email VARCHAR(255),
    sent_to_slack BOOLEAN DEFAULT FALSE,
    sent_to_dashboard BOOLEAN DEFAULT FALSE,
    
    -- Content
    subject TEXT,
    message TEXT,
    details JSONB,
    
    -- Delivery
    delivery_status VARCHAR(50),
    delivery_error TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_alerts_sent_cycle ON alerts_sent(cycle_id);
CREATE INDEX idx_alerts_sent_event ON alerts_sent(event_type);
CREATE INDEX idx_alerts_sent_severity ON alerts_sent(severity);

-- ============================================================================
-- TABLE: rollback_events
-- Track all automatic rollback events
-- ============================================================================
CREATE TABLE IF NOT EXISTS rollback_events (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    cycle_id BIGINT REFERENCES deployment_cycles(id),
    backup_id BIGINT REFERENCES deployment_backups(id),
    
    -- Rollback trigger
    trigger_reason VARCHAR(255),
    trigger_severity VARCHAR(50),
    
    -- Rollback details
    agents_targeted INT,
    agents_rolled_back_successful INT,
    agents_rolled_back_failed INT,
    
    -- Timing
    triggered_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_ms INT,
    
    -- Details
    error_details JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_rollback_events_cycle ON rollback_events(cycle_id);
CREATE INDEX idx_rollback_events_reason ON rollback_events(trigger_reason);

-- ============================================================================
-- TABLE: version_log
-- Track all deployed versions
-- ============================================================================
CREATE TABLE IF NOT EXISTS version_log (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    
    -- Version info
    version_number VARCHAR(20) NOT NULL UNIQUE,
    deployed_at TIMESTAMP WITH TIME ZONE,
    
    -- Status
    deployment_status VARCHAR(50),
    agents_deployed INT,
    
    -- Quality
    pass_rate_before FLOAT,
    pass_rate_after FLOAT,
    
    -- Issues fixed
    issues_fixed TEXT[],
    
    -- Rollback
    rolled_back BOOLEAN DEFAULT FALSE,
    rollback_reason TEXT,
    rollback_timestamp TIMESTAMP WITH TIME ZONE,
    
    notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_version_log_number ON version_log(version_number);
CREATE INDEX idx_version_log_deployed ON version_log(deployed_at);

-- ============================================================================
-- TABLE: client_master_version
-- Track which master version each client is on
-- ============================================================================
CREATE TABLE IF NOT EXISTS client_master_version (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    
    client_id VARCHAR(100) NOT NULL UNIQUE,
    agent_id VARCHAR(100) NOT NULL,
    company_name VARCHAR(255),
    
    -- Current version
    current_master_version VARCHAR(20),
    deployed_at TIMESTAMP WITH TIME ZONE,
    
    -- Previous version
    previous_master_version VARCHAR(20),
    previous_deployed_at TIMESTAMP WITH TIME ZONE,
    
    -- Status
    deployment_status VARCHAR(50),
    is_live BOOLEAN DEFAULT FALSE,
    
    -- Last checked
    last_verified_at TIMESTAMP WITH TIME ZONE,
    verification_passed BOOLEAN,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_client_master_version_client ON client_master_version(client_id);
CREATE INDEX idx_client_master_version_agent ON client_master_version(agent_id);
CREATE INDEX idx_client_master_version_current ON client_master_version(current_master_version);

-- ============================================================================
-- FUNCTION: update_deployment_cycles_timestamp
-- Auto-update updated_at on deployment_cycles
-- ============================================================================
CREATE OR REPLACE FUNCTION update_deployment_cycles_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER deployment_cycles_timestamp
    BEFORE UPDATE ON deployment_cycles
    FOR EACH ROW
    EXECUTE FUNCTION update_deployment_cycles_timestamp();

-- ============================================================================
-- FUNCTION: log_deployment_cost
-- Auto-sum costs in deployment_cycles
-- ============================================================================
CREATE OR REPLACE FUNCTION log_deployment_cost()
RETURNS TRIGGER AS $$
BEGIN
    NEW.total_cost = NEW.diagnosis_cost + NEW.validation_cost + NEW.deployment_cost + NEW.monitoring_cost;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER deployment_cost_sum
    BEFORE INSERT OR UPDATE ON deployment_cycles
    FOR EACH ROW
    EXECUTE FUNCTION log_deployment_cost();

-- ============================================================================
-- PERMISSIONS
-- ============================================================================
-- Grant appropriate permissions to n8n service account
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO n8n_user;
-- GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO n8n_user;

-- ============================================================================
-- INITIAL DATA
-- ============================================================================
-- Insert initial cost tracking entry for current month
INSERT INTO cost_tracking (month_year)
VALUES (DATE_TRUNC('month', NOW())::DATE)
ON CONFLICT DO NOTHING;
