// src/monitors/n8n.js — n8n workflow health monitoring
const fetch = require('node-fetch');
const config = require('../config');
const alertManager = require('../utils/alertManager');
const statusStore = require('../utils/statusStore');

const headers = () => ({
  'X-N8N-API-KEY': process.env.N8N_API_KEY,
  'Content-Type': 'application/json',
});

// ── CANONICAL WORKFLOW LIST (updated 2026-04-09) ──────────────────────────────
// Premium workflows RETIRED 2026-04-09. Monthly billing replaced by tools/monthly_minutes.py.
// Usage Alert Monitor is BROKEN — queries dropped hvac_call_log table (2026-04-09).
const EXPECTED_WORKFLOWS = {
  hvacCallProcessorLean: {
    id: 'Kg576YtPM9yEacKn',
    name: 'HVAC Call Processor (Lean Fan-out)',
    critical: true,
  },
  // NOTE: Monthly Minutes Calculator & Overage was n8n workflow z1DNTjvTDAkExsX8
  // ARCHIVED 2026-04-09 → renamed [ARCHIVED-2026-04-09]. Replaced by tools/monthly_minutes.py.

  // NOTE: Usage Alert Monitor (80% & 100%) workflow Wa3pHRMwSjbZHqMC is BROKEN —
  // it queries the dropped hvac_call_log table. Status: WARNING (not monitored as critical).
  // Do NOT add it back here until the workflow is fixed to use a live table.

  // REMOVED: HVAC Premium Onboarding (Premium RETIRED 2026-04-09)
  // REMOVED: HVAC Premium Call Processor (Premium RETIRED 2026-04-09)
  // REMOVED: Premium Integration Dispatcher (Premium RETIRED 2026-04-09)
};

async function checkN8n() {
  const checks = [];
  let healthy = true;
  const workflowStatuses = [];

  // Use inline workflow list (overrides config.n8n.workflows) so retired Premium
  // workflows are not checked and the lean call processor is monitored.
  const expectedWorkflows = EXPECTED_WORKFLOWS;

  try {
    // 1. Get all workflows and check active status
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

    // Check each expected workflow
    for (const [key, expected] of Object.entries(expectedWorkflows)) {
      const found = workflows.find(w => w.id === expected.id);
      if (!found) {
        checks.push({ name: expected.name, ok: false, detail: 'NOT FOUND in n8n' });
        if (expected.critical) healthy = false;
        continue;
      }

      const isActive = found.active === true;
      workflowStatuses.push({ id: found.id, name: expected.name, active: isActive, critical: expected.critical });

      if (!isActive && expected.critical) {
        healthy = false;
        checks.push({ name: expected.name, ok: false, detail: 'INACTIVE (should be active)' });
        await alertManager.alert({
          system: 'n8n', check: `workflow-inactive-${key}`, tier: 'critical',
          title: `Critical Workflow Inactive: ${expected.name}`,
          message: `Workflow "${expected.name}" (${expected.id}) is inactive. This is a critical workflow.`,
        });
      } else if (!isActive) {
        checks.push({ name: expected.name, ok: false, detail: 'Inactive' });
      } else {
        checks.push({ name: expected.name, ok: true, detail: 'Active' });
      }
    }

    // 2. Check recent executions for errors (last 2 hours)
    try {
      const execRes = await fetch(
        `${config.n8n.baseUrl}/api/v1/executions?limit=50&status=error`,
        { headers: headers() }
      );

      if (execRes.ok) {
        const execData = await execRes.json();
        const executions = execData.data || [];
        const twoHoursAgo = new Date(Date.now() - 2 * 3600 * 1000).toISOString();
        const recentErrors = executions.filter(e =>
          e.startedAt && e.startedAt > twoHoursAgo
        );

        // Group errors by workflow
        const errorsByWorkflow = {};
        for (const exec of recentErrors) {
          const wfId = exec.workflowId;
          if (!errorsByWorkflow[wfId]) errorsByWorkflow[wfId] = [];
          errorsByWorkflow[wfId].push(exec);
        }

        const totalRecentErrors = recentErrors.length;
        checks.push({
          name: 'Recent errors (2h)',
          ok: totalRecentErrors < 5,
          detail: `${totalRecentErrors} errors across ${Object.keys(errorsByWorkflow).length} workflows`,
        });

        // Alert on critical workflow errors
        for (const [wfId, errors] of Object.entries(errorsByWorkflow)) {
          const wfConfig = Object.values(expectedWorkflows).find(w => w.id === wfId);
          if (wfConfig && wfConfig.critical && errors.length >= 3) {
            healthy = false;
            await alertManager.alert({
              system: 'n8n', check: `execution-errors-${wfId}`, tier: 'warning',
              title: `Execution Errors: ${wfConfig.name}`,
              message: `${errors.length} errors in the last 2 hours for "${wfConfig.name}".`,
            });
          }
        }

        // Calculate error rate across all recent executions
        const allExecRes = await fetch(
          `${config.n8n.baseUrl}/api/v1/executions?limit=100`,
          { headers: headers() }
        );
        if (allExecRes.ok) {
          const allData = await allExecRes.json();
          const allExecs = (allData.data || []).filter(e => e.startedAt && e.startedAt > twoHoursAgo);
          const errorRate = allExecs.length > 0
            ? ((recentErrors.length / allExecs.length) * 100).toFixed(1)
            : '0';
          checks.push({
            name: 'Error rate (2h)',
            ok: parseFloat(errorRate) < 15,
            detail: `${errorRate}% (${recentErrors.length}/${allExecs.length})`,
          });

          if (parseFloat(errorRate) > 25 && allExecs.length > 10) {
            healthy = false;
            await alertManager.alert({
              system: 'n8n', check: 'high-error-rate', tier: 'critical',
              title: `High Error Rate: ${errorRate}%`,
              message: `n8n execution error rate is ${errorRate}% in the last 2 hours (${recentErrors.length} errors out of ${allExecs.length} executions).`,
            });
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
