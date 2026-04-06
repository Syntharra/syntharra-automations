-- 2026-04-07 — Track B1 — client_agents registry
-- Applied via Supabase MCP apply_migration name=create_client_agents_registry
CREATE TABLE IF NOT EXISTS public.client_agents (
  id BIGSERIAL PRIMARY KEY,
  client_id TEXT NOT NULL,
  agent_id TEXT NOT NULL,
  flow_id TEXT,
  tier TEXT NOT NULL CHECK (tier IN ('std','prem')),
  prompt_version TEXT,
  base_tag TEXT,
  deployed_at TIMESTAMPTZ DEFAULT now(),
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','canary','paused','retired')),
  canary BOOLEAN NOT NULL DEFAULT false,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS client_agents_client_tier_uniq ON public.client_agents(client_id, tier);
CREATE INDEX IF NOT EXISTS client_agents_agent_id_idx ON public.client_agents(agent_id);
CREATE INDEX IF NOT EXISTS client_agents_status_idx ON public.client_agents(status);
ALTER TABLE public.client_agents ENABLE ROW LEVEL SECURITY;
CREATE POLICY client_agents_service_role_all ON public.client_agents
  FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE TABLE IF NOT EXISTS public.client_agents_rollout_log (
  id BIGSERIAL PRIMARY KEY,
  rollout_tag TEXT NOT NULL,
  client_id TEXT NOT NULL,
  agent_id TEXT NOT NULL,
  tier TEXT NOT NULL,
  prev_prompt_version TEXT,
  new_prompt_version TEXT,
  status TEXT NOT NULL,
  error TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);
ALTER TABLE public.client_agents_rollout_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY client_agents_rollout_log_service_role_all ON public.client_agents_rollout_log
  FOR ALL TO service_role USING (true) WITH CHECK (true);
