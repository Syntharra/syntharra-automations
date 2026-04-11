// src/monitors/pipeline.js — End-to-end pipeline integrity checks
// All clients in hvac_standard_agent; all calls in hvac_call_log
const { createClient } = require('@supabase/supabase-js');
const fetch = require('node-fetch');
const config = require('../config');
const alertManager = require('../utils/alertManager');
const statusStore = require('../utils/statusStore');

async function checkPipeline() {
  const checks = [];
  let healthy = true;
  const data = {};

  try {
    const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY);

    // 1. Stripe payment → Jotform sent
    try {
      const { data: payments } = await supabase
        .from(config.supabase.tables.stripePaymentData)
        .select('*')
        .eq('jotform_sent', false);

      const stuckPayments = (payments || []).filter(p => {
        const age = (Date.now() - new Date(p.created_at).getTime()) / 1000 / 3600;
        return age > 1;
      });

      data.stuckPayments = stuckPayments.length;
      checks.push({
        name: 'Payment → Jotform sent',
        ok: stuckPayments.length === 0,
        detail: stuckPayments.length === 0
          ? 'All payments have Jotform sent'
          : `${stuckPayments.length} payment(s) without Jotform sent (>1h old)`,
      });

      if (stuckPayments.length > 0) {
        healthy = false;
        await alertManager.alert({
          system: 'Pipeline', check: 'payment-no-jotform', tier: 'critical',
          title: `Pipeline Break: ${stuckPayments.length} Payments Without Jotform`,
          message: `${stuckPayments.length} Stripe payments received but Jotform not sent. Customers: ${stuckPayments.map(p => p.customer_email).join(', ')}`,
        });
      }
    } catch (err) {
      checks.push({ name: 'Payment → Jotform', ok: false, detail: err.message });
    }

    // 2. Agent → Reachable (via retell monitor statusStore)
    try {
      const retellStatus = statusStore.get('retell');
      if (retellStatus) {
        const agentChecks = (retellStatus.checks || []).filter(c => c.name && c.name.startsWith('Agent:'));
        const failedAgents = agentChecks.filter(c => !c.ok);
        data.unreachableAgents = failedAgents.length;
        checks.push({
          name: 'Agent → Reachable',
          ok: failedAgents.length === 0,
          detail: failedAgents.length === 0
            ? `All ${agentChecks.length} agents reachable (via retell monitor)`
            : `${failedAgents.length} unreachable: ${failedAgents.map(c => c.name.replace('Agent: ','')).join(', ')}`,
        });
        if (failedAgents.length > 0) {
          healthy = false;
          await alertManager.alert({
            system: 'Pipeline', check: 'agent-not-reachable', tier: 'critical',
            title: `${failedAgents.length} Agent(s) Not Reachable`,
            message: `Agents unreachable in Retell: ${failedAgents.map(c => c.name).join(', ')}. Calls will fail.`,
          });
        }
      } else {
        checks.push({ name: 'Agent → Reachable', ok: true, detail: 'Retell monitor not yet run — skipping' });
      }
    } catch (err) {
      checks.push({ name: 'Agent publish check', ok: false, detail: err.message });
    }

    // 3. Calls flowing → Call processed (check hvac_call_log for unprocessed calls)
    try {
      const retellRes = await fetch(`${config.retell.baseUrl}/v2/list-calls`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${process.env.RETELL_API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ sort_order: 'descending', limit: 50 }),
      });

      if (retellRes.ok) {
        const rawCalls = await retellRes.json();
        const cutoff6h = Date.now() - 6 * 3600 * 1000;
        const retellCalls = (Array.isArray(rawCalls) ? rawCalls : []).filter(c => c.start_timestamp > cutoff6h);
        const completedCalls = retellCalls.filter(c => c.call_status === 'ended' && c.call_analysis);

        let unprocessedCalls = 0;
        for (const call of completedCalls) {
          const { data: logEntry } = await supabase
            .from(config.supabase.tables.hvacCallLog)
            .select('id')
            .eq('call_id', call.call_id)
            .limit(1);

          if (!logEntry || logEntry.length === 0) {
            const callAge = (Date.now() - call.start_timestamp) / 1000 / 60;
            if (callAge > 30) unprocessedCalls++;
          }
        }

        data.unprocessedCalls = unprocessedCalls;
        checks.push({
          name: 'Call → Processed',
          ok: unprocessedCalls === 0,
          detail: unprocessedCalls === 0
            ? `All ${completedCalls.length} recent calls processed`
            : `${unprocessedCalls} calls completed but not processed (>30 min old)`,
        });

        if (unprocessedCalls >= 3) {
          healthy = false;
          await alertManager.alert({
            system: 'Pipeline', check: 'calls-not-processed', tier: 'critical',
            title: `${unprocessedCalls} Calls Not Processed`,
            message: `${unprocessedCalls} completed calls have no matching call_log entry. Call processor workflow may be down.`,
          });
        }
      }
    } catch (err) {
      checks.push({ name: 'Call processing', ok: false, detail: err.message });
    }

    // 4. Lead notification check
    try {
      const sixHoursAgo = new Date(Date.now() - 6 * 3600 * 1000).toISOString();
      const { data: recentLeads } = await supabase
        .from(config.supabase.tables.hvacCallLog)
        .select('id, call_id, company_name, is_lead, lead_score')
        .gte('call_timestamp', sixHoursAgo)
        .eq('is_lead', true);

      data.recentLeads = (recentLeads || []).length;
      checks.push({
        name: 'Lead notifications',
        ok: true,
        detail: `${(recentLeads || []).length} leads in last 6h`,
      });
    } catch (err) {
      checks.push({ name: 'Lead notifications', ok: false, detail: err.message });
    }

    // 5. Booking pipeline check REMOVED — relied on hvac_call_log (DROPPED 2026-04-09)
    //    and booking_attempted/booking_success columns from the Premium pipeline.
    //    Standard plan has no booking pipeline. Remove until Standard booking is built.

  } catch (err) {
    healthy = false;
    checks.push({ name: 'Pipeline', ok: false, detail: err.message });
  }

  statusStore.update('pipeline', { healthy, checks, data });
  console.log(`[Pipeline] Check complete — ${healthy ? '✅ healthy' : '❌ issues found'}`);
}

module.exports = { checkPipeline };
