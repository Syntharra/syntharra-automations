// src/monitors/crm.js — CRM & Calendar integration health
// RETIRED 2026-04-09: Premium plan discontinued. Single product is HVAC Standard ($697/mo).
// CRM/Calendar integrations were Premium-only features. This monitor is now a static no-op.
// Do NOT restore Premium checks without a product decision and new table schema.
const statusStore = require('../utils/statusStore');

async function checkCRM() {
  const checks = [
    {
      name: 'CRM/Calendar',
      ok: true,
      detail: 'Standard plan — no CRM integrations (Premium feature, retired 2026-04-09)',
    },
  ];
  const healthy = true;
  const data = { clients: [] };

  statusStore.update('crm', { healthy, checks, data });
  console.log('[CRM] Check complete — static (Premium retired, no CRM integrations on Standard)');
}

module.exports = { checkCRM };
