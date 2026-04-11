// src/monitors/clients.js — Per-client health monitoring
// NOTE: hvac_call_log dropped 2026-04-09 — call counts now fetched from Retell API per-agent.
const fetch = require('node-fetch');
const { createClient } = require('@supabase/supabase-js');
const config = require('../config');
const alertManager = require('../utils/alertManager');
const statusStore = require('../utils/statusStore');

const RETELL_API = config.retell.baseUrl;

async function checkClients() {
  const checks = [];
  let healthy = true;
  const data = { clients: [] };

  try {
    const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY);

    const { data: allClients, error } = await supabase
      .from(config.supabase.tables.hvacStandardAgent)
      .select('company_name, agent_id, plan_type, client_email, lead_phone, lead_email, transfer_phone, emergency_phone, created_at');

    if (error) throw new Error(error.message);

    if (!allClients || allClients.length === 0) {
      checks.push({ name: 'Active clients', ok: true, detail: 'No clients onboarded yet' });
      statusStore.update('clients', { healthy: true, checks, data });
      return;
    }

    const stdCount = allClients.filter(c => c.plan_type !== 'premium').length;
    checks.push({ name: 'Active clients', ok: true, detail: `${allClients.length} total (${stdCount} standard)` });

    // Fetch all calls from Retell once (last 7 days) and group by agent_id
    // More efficient than one API call per client
    let callsByAgent = {};
    let leadsByAgent = {};
    try {
      const sevenDaysAgo = Date.now() - 7 * 24 * 3600 * 1000;
      const res = await fetch(`${RETELL_API}/v2/list-calls`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${process.env.RETELL_API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ sort_order: 'descending', limit: 500 }),
      });
      if (res.ok) {
        const rawCalls = await res.json();
        const recentCalls = (Array.isArray(rawCalls) ? rawCalls : [])
          .filter(c => c.start_timestamp && c.start_timestamp > sevenDaysAgo);

        for (const call of recentCalls) {
          const aid = call.agent_id;
          if (!aid) continue;
          callsByAgent[aid] = (callsByAgent[aid] || 0) + 1;
          if (call.call_analysis?.call_successful || call.in_voicemail === false) {
            // Count as lead if flagged — best proxy without hvac_call_log
            // The n8n call processor sets is_lead; we just count non-voicemail connected calls
            leadsByAgent[aid] = (leadsByAgent[aid] || 0) + 1;
          }
        }
      }
    } catch (_) {
      // Retell bulk fetch failed — client call counts will show N/A
    }

    for (const client of allClients) {
      const clientChecks = [];
      const clientName = client.company_name || 'Unknown';

      // 1. Retell agent reachable
      if (client.agent_id) {
        try {
          const res = await fetch(`${RETELL_API}/get-agent/${client.agent_id}`, {
            headers: { 'Authorization': `Bearer ${process.env.RETELL_API_KEY}` },
          });
          if (res.ok) {
            const agentData = await res.json();
            clientChecks.push({ check: 'Agent', ok: true, detail: `v${agentData.version}` });
          } else {
            clientChecks.push({ check: 'Agent', ok: false, detail: `HTTP ${res.status}` });
          }
        } catch (e) {
          clientChecks.push({ check: 'Agent', ok: false, detail: e.message });
        }
      } else {
        clientChecks.push({ check: 'Agent', ok: false, detail: 'No agent_id — onboarding incomplete?' });
      }

      // 2. Call volume (last 7 days) — from Retell bulk fetch above
      const callCount = callsByAgent[client.agent_id] || 0;
      const leadCount = leadsByAgent[client.agent_id] || 0;
      clientChecks.push({
        check: 'Calls (7d)',
        ok: true,
        detail: `${callCount} calls, ${leadCount} connected`,
      });

      // 3. Contact info completeness
      const hasLeadContact = !!(client.lead_phone || client.lead_email);
      const hasTransfer = !!client.transfer_phone;
      clientChecks.push({
        check: 'Contact info',
        ok: hasLeadContact,
        detail: [
          hasLeadContact ? 'Lead contact ✓' : '⚠ NO LEAD CONTACT',
          hasTransfer ? 'Transfer ✓' : 'No transfer#',
        ].join(', '),
      });

      const clientOk = clientChecks.every(c => c.ok);

      checks.push({
        name: `${clientName}`,
        ok: clientOk,
        detail: clientOk
          ? clientChecks.map(c => `${c.check}: ${c.detail}`).join(' | ')
          : clientChecks.filter(c => !c.ok).map(c => `${c.check}: ${c.detail}`).join(' | '),
      });

      if (!clientOk) {
        const failedChecks = clientChecks.filter(c => !c.ok).map(c => `${c.check}: ${c.detail}`).join(', ');
        await alertManager.alert({
          system: 'clients', check: `client-health-${client.agent_id}`, tier: 'warning',
          title: `Client Issue: ${clientName}`,
          message: `Issues for ${clientName} (${client.plan_type || 'standard'}): ${failedChecks}`,
        });
      }

      data.clients.push({
        name: clientName,
        tier: client.plan_type || 'standard',
        agent_id: client.agent_id,
        healthy: clientOk,
        checks: clientChecks,
        lastCheck: new Date().toISOString(),
      });
    }

  } catch (err) {
    healthy = false;
    checks.push({ name: 'Client monitor', ok: false, detail: err.message });
  }

  const hasFailedChecks = checks.some(c => !c.ok);
  healthy = !hasFailedChecks;

  statusStore.update('clients', { healthy, checks, data });
  console.log(`[Clients] Check complete — ${healthy ? '✅ healthy' : '❌ issues found'}`);
}

module.exports = { checkClients };
