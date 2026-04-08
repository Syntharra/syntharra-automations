-- Syntharra Agent Testing Tables
-- Run in Supabase SQL editor

-- Table 1: Test run results (one row per scenario per run)
CREATE TABLE IF NOT EXISTS agent_test_results (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  run_id TEXT NOT NULL,
  agent_type TEXT NOT NULL CHECK (agent_type IN ('standard', 'premium')),
  run_label TEXT,
  scenario_id INTEGER NOT NULL,
  scenario_name TEXT NOT NULL,
  scenario_group TEXT NOT NULL,
  pass BOOLEAN NOT NULL,
  score INTEGER,
  severity TEXT CHECK (severity IN ('PASS','LOW','MEDIUM','HIGH','CRITICAL')),
  issues JSONB DEFAULT '[]',
  fix_needed TEXT DEFAULT '',
  root_cause TEXT DEFAULT '',
  caller_turn1 TEXT,
  agent_turn1 TEXT,
  caller_turn2 TEXT,
  agent_turn2 TEXT,
  tested_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_test_results_run_id ON agent_test_results(run_id);
CREATE INDEX IF NOT EXISTS idx_test_results_agent_type ON agent_test_results(agent_type);
CREATE INDEX IF NOT EXISTS idx_test_results_pass ON agent_test_results(pass);
CREATE INDEX IF NOT EXISTS idx_test_results_tested_at ON agent_test_results(tested_at DESC);

-- Table 2: Pending fixes awaiting approval
CREATE TABLE IF NOT EXISTS agent_pending_fixes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  run_id TEXT NOT NULL,
  agent_type TEXT NOT NULL,
  agent_id TEXT NOT NULL,
  scenario_id INTEGER NOT NULL,
  scenario_name TEXT NOT NULL,
  scenario_group TEXT NOT NULL,
  severity TEXT NOT NULL,
  root_cause TEXT NOT NULL,
  fix_description TEXT NOT NULL,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending','approved','rejected','applied')),
  approved_by TEXT,
  applied_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pending_fixes_status ON agent_pending_fixes(status);
CREATE INDEX IF NOT EXISTS idx_pending_fixes_run_id ON agent_pending_fixes(run_id);
CREATE INDEX IF NOT EXISTS idx_pending_fixes_agent_type ON agent_pending_fixes(agent_type);

-- View: Run summary (one row per run)
CREATE OR REPLACE VIEW agent_test_run_summary AS
SELECT
  run_id,
  agent_type,
  run_label,
  MIN(tested_at) AS started_at,
  MAX(tested_at) AS completed_at,
  COUNT(*) AS total_scenarios,
  SUM(CASE WHEN pass THEN 1 ELSE 0 END) AS passed,
  SUM(CASE WHEN NOT pass THEN 1 ELSE 0 END) AS failed,
  ROUND(100.0 * SUM(CASE WHEN pass THEN 1 ELSE 0 END) / COUNT(*), 1) AS pass_rate,
  SUM(CASE WHEN severity = 'CRITICAL' THEN 1 ELSE 0 END) AS critical_count,
  SUM(CASE WHEN severity = 'HIGH' THEN 1 ELSE 0 END) AS high_count,
  SUM(CASE WHEN severity = 'MEDIUM' THEN 1 ELSE 0 END) AS medium_count,
  SUM(CASE WHEN severity = 'LOW' THEN 1 ELSE 0 END) AS low_count
FROM agent_test_results
GROUP BY run_id, agent_type, run_label
ORDER BY MIN(tested_at) DESC;

-- View: Pending fixes with run context
CREATE OR REPLACE VIEW agent_pending_fixes_view AS
SELECT
  f.*,
  r.pass_rate AS run_pass_rate,
  r.total_scenarios AS run_total
FROM agent_pending_fixes f
LEFT JOIN agent_test_run_summary r ON f.run_id = r.run_id AND f.agent_type = r.agent_type
WHERE f.status = 'pending'
ORDER BY
  CASE f.severity WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 WHEN 'MEDIUM' THEN 3 ELSE 4 END,
  f.created_at DESC;
