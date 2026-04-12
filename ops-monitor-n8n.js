// src/monitors/n8n.js — n8n workflow health monitoring
const fetch = require('node-fetch');
const config = require('../config');
const alertManager = require('../utils/alertManager');
const statusStore = require('../utils/statusStore');

const headers = () => ({
  'X-N8N-API-KEY': process.env.N8N_API_KEY,
  'Content-Type': 'application/json',
});

// ── CANONICAL WORKFLOW LIST (updated 2026-04-11) ──────────────────────────────
// IDs sourced from docs/REFERENCE.md — the single source of truth.
// config.js workflow IDs are stale — do NOT use them here.
//
// checkExecutionRecency (ms): for scheduled workflows, alert if last success is older than this.
// Omit or set to null for event-driven workflows (onboarding, call processor) — recency isn't meaningful.
const EXPECTED_WORKFLOWS = {
  hvacCallProcessorLean: {
    id: 'Kg576YtPM9yEacKn',
    name: 'HVAC Call Processor (Lean Fan-out)',
    critical: true,
    checkExecutionRecency: null, // event-driven — fires per-call
  },
  hvacStdOnboarding: {
    id: '4Hx7aRdzMl5N0uJP',
    name: 'HVAC Standard Onboarding',
    critical: true,
    checkExecutionRecency: null, // event-driven — fires on Jotform submission
  },
  nightlyBackup: {
    id: 'EAHgqAfQoCDumvPU',
    name: 'Nightly GitHub Backup',
    critical: true,
    checkExecutionRecency: 25 * 3600 * 1000, // scheduled — must run within 25h
  },
};

async function checkN8n() {
  const checks = [];
  let healthy = true;
  const workflowStatuses = [];

  try {
    // 1. n8n API reachable
    const wfRes = await fetch(`${config.n8n.baseUrl}/api/v1/workflows?limit=50`, { headers: headers() });
    if (!wfRes.ok) {
      checks.push({ name: 'n8n API', ok: false, detail: `HTTP ${wfRes.status}` });
      healthy = false;
      await alertManager.alert({
        system: 'n8n', check: 'api-unreachable', tier: 'critical',
        title: 'n8n API Unreachable',
        message: `n8n API returned HTTP ${wfRes.status}. All automations may be down.`,
      });
      statusStore.update('n8n', { healthy: false, checks });
      return;
    }

    const wfData = await wfRes.json();
    const workflows = wfData.data || [];

    // 2. Check each expected workflow exists and is active
    for (const [key, expected] of Object.entries(EXPECTED_WORKFLOWS)) {
      const found = workflows.find(w => w.id === expected.id);
      if (!found) {
        checks.push({ name: expected.name, ok: false, detail: 'NOT FOUND in n8n — wrong ID or deleted?' });
        if (expected.critical) {
          healthy = false;
          await alertManager.alert({
            system: 'n8n', check: `workflow-missing-${key}`, tier: 'critical',
            title: `Workflow Not Found: ${expected.name}`,
            message: `Workflow "${expected.name}" (${expected.id}) not found in n8n. Check docs/REFERENCE.md for correct ID.`,
          });
        }
        continue;
      }

      const isActive = found.active === true;
      workflowStatuses.push({ id: found.id, name: expected.name, active: isActive, critical: expected.critical });

      if (!isActive && expected.critical) {
        healthy = false;
        checks.push({ name: expected.name, ok: false, detail: 'INACTIVE — should be active' });
        await alertManager.alert({
          system: 'n8n', check: `workflow-inactive-${key}`, tier: 'critical',
          title: `Critical Workflow Inactive: ${expected.name}`,
          message: `Workflow "${expected.name}" (${expected.id}) is inactive. Reactivate immediately.`,
        });
      } else if (!isActive) {
        checks.push({ name: expected.name, ok: false, detail: 'Inactive' });
      } else {
        checks.push({ name: expected.name, ok: true, detail: 'Active' });
      }
    }

    // 3. Execution recency — scheduled workflows must have run recently
    for (const [key, wf] of Object.entries(EXPECTED_WORKFLOWS)) {
      if (!wf.checkExecutionRecency) continue;
      try {
        const execRes = await fetch(
          `${config.n8n.baseUrl}/api/v1/executions?workflowId=${wf.id}&limit=1`,
          { headers: headers() }
        );
        if (execRes.ok) {
          const execData = await execRes.json();
          const lastExec = (execData.data || [])[0];
          if (!lastExec) {
            checks.push({ name: `${wf.name}: last run`, ok: false, detail: 'No executions found — never ran?' });
            if (wf.critical) {
              healthy = false;
              await alertManager.alert({
                system: 'n8n', check: `${key}-never-ran`, tier: 'critical',
                title: `Never Ran: ${wf.name}`,
                message: `Scheduled workflow "${wf.name}" has no execution history. It may not be triggering.`,
              });
            }
          } else {
            const lastRunAt = new Date(lastExec.startedAt || lastExec.createdAt).getTime();
            const ageMs = Date.now() - lastRunAt;
            const ageHours = Math.round(ageMs / 3600000);
            const isRecent = ageMs < wf.checkExecutionRecency;
            const status = lastExec.status || lastExec.finished ? 'success' : 'running';

            checks.push({
              name: `${wf.name}: last run`,
              ok: isRecent,
              detail: isRecent
                ? `${ageHours}h ago (${status})`
                : `OVERDUE — last ran ${ageHours}h ago (${status})`,
            });

            if (!isRecent && wf.critical) {
              healthy = false;
              const expectedHours = Math.round(wf.checkExecutionRecency / 3600000);
              await alertManager.alert({
                system: 'n8n', check: `${key}-overdue`, tier: 'critical',
                title: `Overdue: ${wf.name}`,
                message: `Last run was ${ageHours}h ago — expected every ${expectedHours}h. The scheduled trigger may have stopped.`,
              });
            }
          }
        }
      } catch (err) {
        checks.push({ name: `${wf.name}: last run`, ok: false, detail: err.message });
      }
    }

    // 4. Recent execution error rate (last 2h across all workflows)
    try {
      const execRes = await fetch(
        `${config.n8n.baseUrl}/api/v1/executions?limit=50&status=error`,
        { headers: headers() }
      );

      if (execRes.ok) {
        const execData = await execRes.json();
        const twoHoursAgo = new Date(Date.now() - 2 * 3600 * 1000).toISOString();
        const recentErrors = (execData.data || []).filter(e => e.startedAt && e.startedAt > twoHoursAgo);

        // Group by workflow
        const errorsByWf = {};
        for (const exec of recentErrors) {
          errorsByWf[exec.workflowId] = (errorsByWf[exec.workflowId] || 0) + 1;
        }

        checks.push({
          name: 'Errors (2h)',
          ok: recentErrors.length < 5,
          detail: recentErrors.length === 0
            ? 'None'
            : `${recentErrors.length} errors across ${Object.keys(errorsByWf).length} workflows`,
        });

        // Alert on critical workflow errors
        for (const [wfId, count] of Object.entries(errorsByWf)) {
          const wfConfig = Object.values(EXPECTED_WORKFLOWS).find(w => w.id === wfId);
          if (wfConfig && wfConfig.critical && count >= 3) {
            healthy = false;
            await alertManager.alert({
              system: 'n8n', check: `execution-errors-${wfId}`, tier: 'warning',
              title: `Execution Errors: ${wfConfig.name}`,
              message: `${count} errors in the last 2 hours for "${wfConfig.name}". Investigate immediately.`,
            });
          }
        }

        // Overall error rate
        const allExecRes = await fetch(
          `${config.n8n.baseUrl}/api/v1/executions?limit=100`,
          { headers: headers() }
        );
        if (allExecRes.ok) {
          const allData = await allExecRes.json();
          const allRecent = (allData.data || []).filter(e => e.startedAt && e.startedAt > twoHoursAgo);
          if (allRecent.length > 0) {
            const errorRate = ((recentErrors.length / allRecent.length) * 100).toFixed(1);
            checks.push({
              name: 'Error rate (2h)',
              ok: parseFloat(errorRate) < 15,
              detail: `${errorRate}% (${recentErrors.length}/${allRecent.length})`,
            });
            if (parseFloat(errorRate) > 25 && allRecent.length > 10) {
              healthy = false;
              await alertManager.alert({
                system: 'n8n', check: 'high-error-rate', tier: 'critical',
                title: `High n8n Error Rate: ${errorRate}%`,
                message: `${recentErrors.length}/${allRecent.length} executions failed in the last 2h. Platform may be degraded.`,
              });
            }
          }
        }
      }
    } catch (err) {
      checks.push({ name: 'Execution check', ok: false, detail: err.message });
    }

  } catch (err) {
    healthy = false;
    checks.push({ name: 'n8n connectivity', ok: false, detail: err.message });
  }

  statusStore.update('n8n', { healthy, checks, data: { workflowStatuses } });
  console.log(`[n8n] Check complete — ${healthy ? '✅ healthy' : '❌ issues found'}`);
}

module.exports = { checkN8n };
