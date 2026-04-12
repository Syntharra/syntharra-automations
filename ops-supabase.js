// src/monitors/supabase.js — Supabase database health monitoring
const { createClient } = require('@supabase/supabase-js');
const config = require('../config');
const alertManager = require('../utils/alertManager');
const statusStore = require('../utils/statusStore');

function getClient() {
  return createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY);
}

async function checkSupabase() {
  const checks = [];
  let healthy = true;
  const data = {};

  try {
    const supabase = getClient();

    // 1. DB connectivity — simple query
    try {
      const { data: pingData, error } = await supabase
        .from(config.supabase.tables.hvacStandardAgent)
        .select('id')
        .limit(1);
      if (error) throw error;
      checks.push({ name: 'DB connectivity', ok: true, detail: 'Connected' });
    } catch (err) {
      healthy = false;
      checks.push({ name: 'DB connectivity', ok: false, detail: err.message });
      await alertManager.alert({
        system: 'Supabase', check: 'db-connectivity', tier: 'critical',
        title: 'Database Unreachable',
        message: `Cannot connect to Supabase: ${err.message}`,
      });
      statusStore.update('supabase', { healthy: false, checks });
      return;
    }

    // 2. Client data integrity — missing agent_ids (all tiers in one table)
    try {
      const { data: missingAgents, error } = await supabase
        .from(config.supabase.tables.hvacStandardAgent)
        .select('id, company_name, agent_id, client_email, plan_type')
        .is('agent_id', null);
      if (error) throw error;

      const missingAgentIds = missingAgents || [];
      data.missingAgentIds = missingAgentIds.length;

      checks.push({
        name: 'Client integrity',
        ok: missingAgentIds.length === 0,
        detail: missingAgentIds.length === 0
          ? 'All clients have agent_ids'
          : `${missingAgentIds.length} clients missing agent_id: ${missingAgentIds.map(a => a.company_name).join(', ')}`,
      });

      if (missingAgentIds.length > 0) {
        await alertManager.alert({
          system: 'Supabase', check: 'missing-agent-ids', tier: 'warning',
          title: `${missingAgentIds.length} Clients Missing agent_id`,
          message: `Clients without agent_id (incomplete onboarding): ${missingAgentIds.map(a => a.company_name || a.client_email).join(', ')}`,
        });
      }
    } catch (err) {
      checks.push({ name: 'Client integrity', ok: false, detail: err.message });
    }

    // 3. DLQ check REMOVED — call_processor_dlq table was DROPPED 2026-04-09.
    //    Do not re-add until/unless the table is recreated.

    // 4. Lead flow — calls in last 24h (all tiers in one call log)
    try {
      const yesterday = new Date(Date.now() - 24 * 3600 * 1000).toISOString();

      const { count: callCount } = await supabase
        .from(config.supabase.tables.hvacCallLog)
        .select('*', { count: 'exact', head: true })
        .gte('call_timestamp', yesterday);

      const { count: leadCount } = await supabase
        .from(config.supabase.tables.hvacCallLog)
        .select('*', { count: 'exact', head: true })
        .gte('call_timestamp', yesterday)
        .eq('is_lead', true);

      data.calls24h = callCount || 0;
      data.leads24h = leadCount || 0;

      checks.push({
        name: 'Lead flow (24h)',
        ok: true,
        detail: `${callCount || 0} calls, ${leadCount || 0} leads`,
      });
    } catch (err) {
      checks.push({ name: 'Lead flow', ok: false, detail: err.message });
    }

    // 5. Subscription health — check for past_due
    try {
      const { data: pastDue } = await supabase
        .from(config.supabase.tables.clientSubscriptions)
        .select('agent_id, company_name, status')
        .eq('status', 'past_due');

      data.pastDueSubscriptions = (pastDue || []).length;

      checks.push({
        name: 'Past-due subscriptions',
        ok: (pastDue || []).length === 0,
        detail: (pastDue || []).length === 0 ? 'None' : `${(pastDue || []).length} past due`,
      });
    } catch (err) {
      checks.push({ name: 'Subscription health', ok: false, detail: err.message });
    }

    // 6. Premium integrations check REMOVED — Premium plan RETIRED 2026-04-09.
    //    Single product: HVAC Standard at $697/mo. No CRM/Calendar integrations.

    // 7. Booking success (7d) check REMOVED — relies on hvac_call_log (DROPPED 2026-04-09)
    //    and was a Premium-only feature. Remove until table/pipeline is re-established.

  } catch (err) {
    healthy = false;
    checks.push({ name: 'Supabase', ok: false, detail: err.message });
  }

  const hasFailedChecks = checks.some(c => !c.ok);
  healthy = !hasFailedChecks;

  statusStore.update('supabase', { healthy, checks, data });
  console.log(`[Supabase] Check complete — ${healthy ? '✅ healthy' : '❌ issues found'} (${checks.filter(c=>c.ok).length}/${checks.length} passing)`);
}

module.exports = { checkSupabase };
