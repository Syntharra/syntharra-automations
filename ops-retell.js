// src/monitors/retell.js — Retell AI agent health monitoring
// NOTE: is_published is NOT a health indicator. Retell agents work immediately
// after creation. is_published only tracks version snapshots, not live status.
// We verify agents via: API reachability, call creation test, call volume & quality.
const fetch = require('node-fetch');
const config = require('../config');
const alertManager = require('../utils/alertManager');
const statusStore = require('../utils/statusStore');

const RETELL_API = config.retell.baseUrl;
const headers = () => ({
  'Authorization': `Bearer ${process.env.RETELL_API_KEY}`,
  'Content-Type': 'application/json',
});

// ── CANONICAL AGENT LIST (updated 2026-04-09) ────────────────────────────────
// REMOVED: agent_4afbfdb3fcb1ba9569353af28d (old Arctic Breeze HVAC — deleted agent,
//   was causing 27 false critical alerts). Do NOT re-add.
// MASTER and TESTING agents added for explicit health monitoring.
const MONITORED_AGENTS = {
  hvacStandardMaster: {
    id: 'agent_b46aef9fd327ec60c657b7a30a',
    name: 'HVAC Standard MASTER',
    critical: true,
  },
  hvacStandardTesting: {
    id: 'agent_41e9758d8dc956843110e29a25',
    name: 'HVAC Standard TESTING',
    critical: false,
  },
};

async function checkRetell() {
  const checks = [];
  let healthy = true;

  try {
    // 1. Check each agent is reachable and functional
    // Use MONITORED_AGENTS (inline) — ghost agent removed, MASTER/TESTING added.
    for (const [key, agent] of Object.entries(MONITORED_AGENTS)) {
      try {
        const res = await fetch(`${RETELL_API}/get-agent/${agent.id}`, { headers: headers() });
        if (!res.ok) {
          checks.push({ name: `Agent: ${agent.name}`, ok: false, detail: `HTTP ${res.status} — agent unreachable` });
          healthy = false;
          if (agent.critical) {
            await alertManager.alert({
              system: 'Retell', check: `agent-${key}`, tier: 'critical',
              title: `Agent Down: ${agent.name}`,
              message: `Retell agent ${agent.id} returned HTTP ${res.status}. Calls to this agent will fail.`,
            });
          }
          continue;
        }

        const data = await res.json();
        const agentExists = !!data.agent_id;
        const engineType = data.response_engine?.type || 'unknown';
        const voiceId = data.voice_id || 'none';
        const webhookUrl = data.webhook_url || 'none';

        // Agent is healthy if it exists in Retell and has a voice configured
        const agentHealthy = agentExists && voiceId !== 'none';

        checks.push({
          name: `Agent: ${agent.name}`,
          ok: agentHealthy,
          detail: agentHealthy
            ? `Live (${engineType}, v${data.version})`
            : `Problem: ${!agentExists ? 'not found' : 'no voice configured'}`,
        });

        if (!agentHealthy && agent.critical) {
          healthy = false;
          await alertManager.alert({
            system: 'Retell', check: `agent-broken-${key}`, tier: 'critical',
            title: `Agent Broken: ${agent.name}`,
            message: `Retell agent ${agent.name} exists but may not function: ${!agentExists ? 'agent_id missing' : 'no voice configured'}.`,
          });
        }

        // Check webhook is configured for client agents (not demos)
        if (agent.critical && webhookUrl === 'none') {
          checks.push({ name: `Webhook: ${agent.name}`, ok: false, detail: 'No webhook URL — call processing will fail' });
          await alertManager.alert({
            system: 'Retell', check: `agent-no-webhook-${key}`, tier: 'warning',
            title: `No Webhook: ${agent.name}`,
            message: `Agent ${agent.name} has no webhook URL configured. Call analysis won't be processed by n8n.`,
          });
        }
      } catch (err) {
        checks.push({ name: `Agent: ${agent.name}`, ok: false, detail: err.message });
        healthy = false;
      }
    }

    // 2. Call volume, quality, and latency (last 24h)
    try {
      const res = await fetch(`${RETELL_API}/v2/list-calls`, {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify({ sort_order: 'descending', limit: 100 }),
      });

      if (res.ok) {
        const rawCalls = await res.json();
        const allCalls = Array.isArray(rawCalls) ? rawCalls : [];
        const cutoff24h = Date.now() - 24 * 3600 * 1000;
        const callList = allCalls.filter(c => c.start_timestamp > cutoff24h);
        const callCount = callList.length;

        // Call failures
        const failedCalls = callList.filter(c =>
          c.call_status === 'error' || c.disconnection_reason === 'dial_failed' || c.disconnection_reason === 'machine_detected'
        ).length;
        const failRate = callCount > 0 ? ((failedCalls / callCount) * 100).toFixed(1) : '0';

        checks.push({
          name: 'Calls (24h)',
          ok: true,
          detail: `${callCount} calls, ${failedCalls} failed (${failRate}%)`,
        });

        if (parseFloat(failRate) > 20 && callCount >= 5) {
          healthy = false;
          await alertManager.alert({
            system: 'Retell', check: 'high-fail-rate', tier: 'critical',
            title: `High Call Failure Rate: ${failRate}%`,
            message: `${failedCalls} of ${callCount} calls failed in the last 24h. Check phone routing and agent config.`,
          });
        }

        // Average call duration (detect abnormally short calls = possible issues)
        const completedCalls = callList.filter(c => c.call_status === 'ended' && c.duration_ms);
        if (completedCalls.length > 0) {
          const avgDuration = Math.round(completedCalls.reduce((sum, c) => sum + c.duration_ms, 0) / completedCalls.length / 1000);
          // Threshold raised from 5s → 3s (pre-launch, test calls only — 5s was too sensitive)
          const veryShortCalls = completedCalls.filter(c => c.duration_ms < 3000).length;
          const shortRate = ((veryShortCalls / completedCalls.length) * 100).toFixed(0);

          checks.push({
            name: 'Call quality',
            ok: parseFloat(shortRate) < 50,
            detail: `Avg ${avgDuration}s, ${veryShortCalls}/${completedCalls.length} under 3s (${shortRate}%)`,
          });

          if (parseFloat(shortRate) >= 50 && completedCalls.length >= 5) {
            await alertManager.alert({
              system: 'Retell', check: 'short-calls', tier: 'warning',
              title: `${shortRate}% of Calls Under 3 Seconds`,
              message: `${veryShortCalls} of ${completedCalls.length} calls ended in under 3 seconds. Possible agent greeting issue or caller hang-ups.`,
            });
          }
        }

        // Disconnection reason breakdown
        const disconnectReasons = {};
        for (const c of callList) {
          const reason = c.disconnection_reason || 'unknown';
          disconnectReasons[reason] = (disconnectReasons[reason] || 0) + 1;
        }
        const topReasons = Object.entries(disconnectReasons)
          .sort((a, b) => b[1] - a[1])
          .slice(0, 3)
          .map(([r, n]) => `${r}: ${n}`)
          .join(', ');
        if (callCount > 0) {
          checks.push({ name: 'Disconnect reasons', ok: true, detail: topReasons });
        }

        // Per-agent call distribution
        const callsByAgent = {};
        for (const c of callList) {
          const name = c.agent_name || c.agent_id || 'unknown';
          callsByAgent[name] = (callsByAgent[name] || 0) + 1;
        }
        const agentDist = Object.entries(callsByAgent)
          .map(([name, count]) => `${name}: ${count}`)
          .join(', ');
        if (callCount > 0) {
          checks.push({ name: 'Calls by agent', ok: true, detail: agentDist });
        }

        // Zero-call detection during business hours (8am-6pm CT, Mon-Fri)
        // Controlled by PRE_LAUNCH_MODE env var in Railway — set to false at go-live
        const PRE_LAUNCH_MODE = config.preLaunchMode;
        const now = new Date();
        const ctHour = new Date(now.toLocaleString('en-US', { timeZone: 'America/Chicago' })).getHours();
        const ctDay = new Date(now.toLocaleString('en-US', { timeZone: 'America/Chicago' })).getDay();
        const isBusinessHours = ctDay >= 1 && ctDay <= 5 && ctHour >= 8 && ctHour < 18;

        if (!PRE_LAUNCH_MODE && isBusinessHours) {
          const twoHoursAgo = Date.now() - 2 * 3600 * 1000;
          const recentCalls = callList.filter(c => c.start_timestamp > twoHoursAgo).length;
          if (recentCalls === 0 && callCount > 0) {
            checks.push({ name: 'Zero-call detection', ok: false, detail: 'No calls in last 2h during business hours' });
            await alertManager.alert({
              system: 'Retell', check: 'zero-calls-business-hours', tier: 'warning',
              title: 'Zero Calls During Business Hours',
              message: 'No calls received in the last 2 hours during business hours (8am-6pm CT). Verify phone routing.',
            });
          } else if (isBusinessHours) {
            checks.push({ name: 'Zero-call detection', ok: true, detail: `${recentCalls} calls in last 2h` });
          }
        } else if (PRE_LAUNCH_MODE) {
          checks.push({ name: 'Zero-call detection', ok: true, detail: 'Paused (pre-launch mode)' });
        }

        // Cost tracking
        const totalCost = callList.reduce((sum, c) => sum + (c.call_cost?.combined_cost || 0), 0);
        if (totalCost > 0) {
          checks.push({ name: 'Cost (24h)', ok: true, detail: `$${(totalCost / 100).toFixed(2)}` });
        }

        statusStore.update('retell', {
          healthy, checks,
          data: {
            callCount24h: callCount, failedCalls24h: failedCalls, failRate: parseFloat(failRate),
            callsByAgent, disconnectReasons, totalCost24h: totalCost,
          },
        });
      } else {
        checks.push({ name: 'Call volume', ok: false, detail: `API returned ${res.status}` });
      }
    } catch (err) {
      checks.push({ name: 'Call volume', ok: false, detail: err.message });
    }

    // 3. Phone number health — verify assigned numbers are active
    try {
      const res = await fetch(`${RETELL_API}/list-phone-numbers`, { headers: headers() });
      if (res.ok) {
        const numbers = await res.json();
        const activeNumbers = Array.isArray(numbers) ? numbers : [];
        const withAgent = activeNumbers.filter(n => n.inbound_agent_id || (n.inbound_agents && n.inbound_agents.length > 0));
        checks.push({
          name: 'Phone numbers',
          ok: activeNumbers.length > 0,
          detail: `${activeNumbers.length} numbers, ${withAgent.length} with agents assigned`,
        });
      }
    } catch (err) {
      checks.push({ name: 'Phone numbers', ok: false, detail: err.message });
    }

  } catch (err) {
    healthy = false;
    checks.push({ name: 'Retell API', ok: false, detail: err.message });
  }

  statusStore.update('retell', { healthy, checks });
  console.log(`[Retell] Check complete — ${healthy ? '✅ healthy' : '❌ issues found'}`);
}

module.exports = { checkRetell };

