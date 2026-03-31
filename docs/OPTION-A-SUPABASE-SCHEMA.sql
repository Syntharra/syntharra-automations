-- Syntharra Option A: Supabase Schema
-- ====================================
-- Tables for diagnosis, testing, deployment, and rollback tracking

-- ============================================================================
-- TABLE: option_a_issues
-- ============================================================================
-- Stores detected issues from diagnosis scans
CREATE TABLE IF NOT EXISTS option_a_issues (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  scan_id VARCHAR(255) NOT NULL,
  agent_id VARCHAR(255) NOT NULL,
  issue_type VARCHAR(100) NOT NULL,
  severity VARCHAR(20) NOT NULL,
  frequency INTEGER NOT NULL,
  description TEXT NOT NULL,
  affected_call_ids TEXT[] DEFAULT '{}',
  sample_call_id VARCHAR(255),
  proposed_fix TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  INDEX (agent_id),
  INDEX (severity),
  INDEX (created_at)
);

-- ============================================================================
-- TABLE: option_a_scans
-- ============================================================================
-- Stores scan metadata and results
CREATE TABLE IF NOT EXISTS option_a_scans (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  scan_id VARCHAR(255) NOT NULL UNIQUE,
  agent_id VARCHAR(255) NOT NULL,
  scan_type VARCHAR(50) DEFAULT 'manual',  -- 'manual', 'scheduled', 'webhook'
  total_calls_analyzed INTEGER DEFAULT 0,
  total_issues_found INTEGER DEFAULT 0,
  critical_count INTEGER DEFAULT 0,
  high_count INTEGER DEFAULT 0,
  medium_count INTEGER DEFAULT 0,
  low_count INTEGER DEFAULT 0,
  duration_seconds FLOAT DEFAULT 0,
  cost_usd NUMERIC(10,4) DEFAULT 0,
  status VARCHAR(50) DEFAULT 'completed',  -- 'running', 'completed', 'failed'
  error_message TEXT,
  triggered_by VARCHAR(255),  -- 'system', 'user', 'webhook'
  created_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP,
  INDEX (agent_id),
  INDEX (created_at)
);

-- ============================================================================
-- TABLE: option_a_fixes
-- ============================================================================
-- Stores proposed fixes and their deployment status
CREATE TABLE IF NOT EXISTS option_a_fixes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  issue_id UUID REFERENCES option_a_issues(id) ON DELETE CASCADE,
  fix_proposal TEXT NOT NULL,
  fix_summary TEXT,
  status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'approved', 'testing', 'deployed', 'failed', 'rolled_back', 'skipped'
  approval_timestamp TIMESTAMP,
  approved_by VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  INDEX (status),
  INDEX (created_at)
);

-- ============================================================================
-- TABLE: option_a_test_runs
-- ============================================================================
-- Stores test results for fixes
CREATE TABLE IF NOT EXISTS option_a_test_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  fix_id UUID REFERENCES option_a_fixes(id) ON DELETE CASCADE,
  test_agent_id VARCHAR(255) NOT NULL,
  test_type VARCHAR(50) NOT NULL,  -- 'auto', 'manual'
  scenario_count INTEGER DEFAULT 1,
  pass_count INTEGER DEFAULT 0,
  fail_count INTEGER DEFAULT 0,
  total_tests INTEGER DEFAULT 0,
  pass_rate NUMERIC(5,2) DEFAULT 0,  -- Percentage
  status VARCHAR(50) DEFAULT 'running',  -- 'running', 'completed', 'error'
  test_result_details JSONB,
  error_message TEXT,
  duration_seconds FLOAT DEFAULT 0,
  cost_usd NUMERIC(10,4) DEFAULT 0,
  test_started_at TIMESTAMP DEFAULT NOW(),
  test_completed_at TIMESTAMP,
  tested_by VARCHAR(255),  -- 'system' or username
  INDEX (fix_id),
  INDEX (status),
  INDEX (test_started_at)
);

-- ============================================================================
-- TABLE: option_a_deployments
-- ============================================================================
-- Stores deployment execution and results
CREATE TABLE IF NOT EXISTS option_a_deployments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  deployment_id VARCHAR(255) NOT NULL UNIQUE,
  fix_id UUID REFERENCES option_a_fixes(id) ON DELETE CASCADE,
  target_agents VARCHAR(50) NOT NULL,  -- 'standard', 'premium', 'all', or agent_list
  target_agent_ids VARCHAR[] DEFAULT '{}',  -- Specific agent IDs if applicable
  total_agents INTEGER DEFAULT 0,
  batch_size INTEGER DEFAULT 10,
  batches_completed INTEGER DEFAULT 0,
  agents_succeeded INTEGER DEFAULT 0,
  agents_failed INTEGER DEFAULT 0,
  status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'in_progress', 'completed', 'failed', 'rolled_back'
  
  -- Layer validation
  layer1_passed BOOLEAN DEFAULT NULL,
  layer1_message TEXT,
  layer2_passed BOOLEAN DEFAULT NULL,
  layer2_message TEXT,
  layer2_canary_error_rate NUMERIC(5,2),
  layer3_passed BOOLEAN DEFAULT NULL,
  layer3_message TEXT,
  layer4_passed BOOLEAN DEFAULT NULL,
  layer4_message TEXT,
  layer4_error_rate NUMERIC(5,2),
  
  deployment_started_at TIMESTAMP DEFAULT NOW(),
  deployment_completed_at TIMESTAMP,
  approved_by VARCHAR(255),
  approval_timestamp TIMESTAMP,
  
  cost_usd NUMERIC(10,4) DEFAULT 0,
  INDEX (deployment_id),
  INDEX (status),
  INDEX (fix_id),
  INDEX (deployment_started_at)
);

-- ============================================================================
-- TABLE: option_a_rollbacks
-- ============================================================================
-- Audit trail for rollback events
CREATE TABLE IF NOT EXISTS option_a_rollbacks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  deployment_id VARCHAR(255) NOT NULL,
  rollback_trigger VARCHAR(100) NOT NULL,  -- 'manual', 'auto_layer1', 'auto_layer2', 'auto_layer3', 'auto_layer4'
  rollback_reason TEXT NOT NULL,
  agents_rolled_back INTEGER DEFAULT 0,
  agents_failed_rollback INTEGER DEFAULT 0,
  rollback_initiated_at TIMESTAMP DEFAULT NOW(),
  rollback_completed_at TIMESTAMP,
  initiated_by VARCHAR(255),
  status VARCHAR(50) DEFAULT 'completed',  -- 'in_progress', 'completed', 'partial_failure'
  INDEX (deployment_id),
  INDEX (rollback_initiated_at)
);

-- ============================================================================
-- TABLE: option_a_deployment_history
-- ============================================================================
-- Per-agent deployment history and monitoring
CREATE TABLE IF NOT EXISTS option_a_deployment_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  deployment_id VARCHAR(255) NOT NULL,
  agent_id VARCHAR(255) NOT NULL,
  agent_plan VARCHAR(50),  -- 'standard', 'premium'
  fix_id UUID,
  deployment_status VARCHAR(50),  -- 'pending', 'deployed', 'failed', 'rolled_back'
  deployment_timestamp TIMESTAMP DEFAULT NOW(),
  
  -- Monitoring (30 min post-deployment)
  calls_received_post_deploy INTEGER DEFAULT 0,
  call_errors_post_deploy INTEGER DEFAULT 0,
  error_rate_post_deploy NUMERIC(5,2),
  avg_call_duration_post_deploy FLOAT,
  monitoring_completed_at TIMESTAMP,
  
  -- Result
  deployment_successful BOOLEAN,
  
  INDEX (deployment_id),
  INDEX (agent_id),
  INDEX (deployment_timestamp)
);

-- ============================================================================
-- TABLE: option_a_approvals
-- ============================================================================
-- Manual approval workflow
CREATE TABLE IF NOT EXISTS option_a_approvals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  fix_id UUID REFERENCES option_a_fixes(id) ON DELETE CASCADE,
  issue_id UUID REFERENCES option_a_issues(id) ON DELETE CASCADE,
  approval_action VARCHAR(50) NOT NULL,  -- 'approved', 'skipped', 'investigate'
  approval_reason TEXT,
  approved_by VARCHAR(255) NOT NULL,
  approved_at TIMESTAMP DEFAULT NOW(),
  
  INDEX (fix_id),
  INDEX (approved_at)
);

-- ============================================================================
-- TABLE: option_a_cost_tracker
-- ============================================================================
-- Track costs per operation (diagnosis, test, deployment)
CREATE TABLE IF NOT EXISTS option_a_cost_tracker (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  operation_type VARCHAR(50) NOT NULL,  -- 'diagnosis', 'test', 'deployment'
  operation_id VARCHAR(255) NOT NULL,
  fix_id UUID,
  cost_usd NUMERIC(10,4) NOT NULL,
  operation_details JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  
  INDEX (operation_type),
  INDEX (created_at)
);

-- ============================================================================
-- VIEW: option_a_pending_approvals
-- ============================================================================
-- Quick view of issues pending your approval
CREATE OR REPLACE VIEW option_a_pending_approvals AS
SELECT
  i.id,
  i.agent_id,
  i.issue_type,
  i.severity,
  i.frequency,
  i.description,
  i.proposed_fix,
  f.status,
  f.created_at,
  s.scan_id
FROM option_a_issues i
LEFT JOIN option_a_fixes f ON f.issue_id = i.id
LEFT JOIN option_a_scans s ON s.scan_id = i.scan_id
WHERE f.status = 'pending' OR f.status IS NULL
ORDER BY i.severity DESC, i.frequency DESC;

-- ============================================================================
-- VIEW: option_a_deployment_status
-- ============================================================================
-- Current deployment status overview
CREATE OR REPLACE VIEW option_a_deployment_status AS
SELECT
  d.deployment_id,
  d.status,
  d.total_agents,
  d.agents_succeeded,
  d.agents_failed,
  ROUND(100.0 * d.agents_succeeded / NULLIF(d.total_agents, 0), 2) as success_rate,
  d.layer1_passed,
  d.layer2_passed,
  d.layer3_passed,
  d.layer4_passed,
  d.deployment_started_at,
  d.deployment_completed_at,
  EXTRACT(MINUTE FROM (d.deployment_completed_at - d.deployment_started_at)) as duration_minutes,
  d.cost_usd
FROM option_a_deployments d
ORDER BY d.deployment_started_at DESC;

-- ============================================================================
-- RLS POLICIES (Row-Level Security)
-- ============================================================================

ALTER TABLE option_a_issues ENABLE ROW LEVEL SECURITY;
ALTER TABLE option_a_fixes ENABLE ROW LEVEL SECURITY;
ALTER TABLE option_a_test_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE option_a_deployments ENABLE ROW LEVEL SECURITY;
ALTER TABLE option_a_rollbacks ENABLE ROW LEVEL SECURITY;
ALTER TABLE option_a_cost_tracker ENABLE ROW LEVEL SECURITY;

-- Only authenticated users can read/write
CREATE POLICY "Allow authenticated users to read issues" ON option_a_issues
  FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated users to write issues" ON option_a_issues
  FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated users to read fixes" ON option_a_fixes
  FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated users to write fixes" ON option_a_fixes
  FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated users to update fixes" ON option_a_fixes
  FOR UPDATE USING (auth.role() = 'authenticated');

-- Similar policies for other tables...

-- ============================================================================
-- INDEXES (Additional)
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_option_a_issues_scan_id ON option_a_issues(scan_id);
CREATE INDEX IF NOT EXISTS idx_option_a_issues_agent_severity ON option_a_issues(agent_id, severity);
CREATE INDEX IF NOT EXISTS idx_option_a_fixes_status_created ON option_a_fixes(status, created_at);
CREATE INDEX IF NOT EXISTS idx_option_a_test_runs_fix_status ON option_a_test_runs(fix_id, status);
CREATE INDEX IF NOT EXISTS idx_option_a_deployments_status_created ON option_a_deployments(status, deployment_started_at);
CREATE INDEX IF NOT EXISTS idx_option_a_cost_tracker_operation ON option_a_cost_tracker(operation_type, created_at);

-- ============================================================================
-- FUNCTION: option_a_get_next_issue_to_fix
-- ============================================================================
-- Fetch the next pending issue (highest severity, most frequent)
CREATE OR REPLACE FUNCTION option_a_get_next_issue_to_fix()
RETURNS TABLE (
  issue_id UUID,
  agent_id VARCHAR,
  issue_type VARCHAR,
  severity VARCHAR,
  frequency INTEGER,
  description TEXT,
  proposed_fix TEXT
) AS $$
  SELECT
    i.id,
    i.agent_id,
    i.issue_type,
    i.severity,
    i.frequency,
    i.description,
    i.proposed_fix
  FROM option_a_issues i
  LEFT JOIN option_a_fixes f ON f.issue_id = i.id
  WHERE f.id IS NULL OR f.status = 'pending'
  ORDER BY
    CASE i.severity
      WHEN 'CRITICAL' THEN 1
      WHEN 'HIGH' THEN 2
      WHEN 'MEDIUM' THEN 3
      WHEN 'LOW' THEN 4
    END,
    i.frequency DESC
  LIMIT 1;
$$ LANGUAGE SQL;

-- ============================================================================
-- FUNCTION: option_a_log_cost
-- ============================================================================
-- Log operation cost
CREATE OR REPLACE FUNCTION option_a_log_cost(
  p_operation_type VARCHAR,
  p_operation_id VARCHAR,
  p_cost NUMERIC,
  p_details JSONB DEFAULT NULL
)
RETURNS UUID AS $$
  INSERT INTO option_a_cost_tracker (operation_type, operation_id, cost_usd, operation_details)
  VALUES (p_operation_type, p_operation_id, p_cost, p_details)
  RETURNING id;
$$ LANGUAGE SQL;

-- ============================================================================
-- FUNCTION: option_a_get_total_session_cost
-- ============================================================================
-- Get total cost for current session
CREATE OR REPLACE FUNCTION option_a_get_total_session_cost()
RETURNS NUMERIC AS $$
  SELECT COALESCE(SUM(cost_usd), 0)
  FROM option_a_cost_tracker
  WHERE DATE(created_at) = CURRENT_DATE;
$$ LANGUAGE SQL;

-- ============================================================================
-- GRANTS
-- ============================================================================

GRANT SELECT, INSERT, UPDATE, DELETE ON option_a_issues TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON option_a_fixes TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON option_a_test_runs TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON option_a_deployments TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON option_a_rollbacks TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON option_a_cost_tracker TO authenticated;
GRANT SELECT ON option_a_pending_approvals TO authenticated;
GRANT SELECT ON option_a_deployment_status TO authenticated;
GRANT EXECUTE ON FUNCTION option_a_get_next_issue_to_fix TO authenticated;
GRANT EXECUTE ON FUNCTION option_a_log_cost TO authenticated;
GRANT EXECUTE ON FUNCTION option_a_get_total_session_cost TO authenticated;
