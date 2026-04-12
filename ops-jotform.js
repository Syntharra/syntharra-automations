// src/monitors/jotform.js — Jotform submission & pipeline monitoring
const fetch = require('node-fetch');
const { createClient } = require('@supabase/supabase-js');
const config = require('../config');
const alertManager = require('../utils/alertManager');
const statusStore = require('../utils/statusStore');

const JF_API = config.jotform.baseUrl;

// ── CANONICAL FORM LIST (updated 2026-04-09) ─────────────────────────────────
// premiumOnboarding REMOVED — Premium plan RETIRED 2026-04-09.
// pilotOnboarding ADDED — 200-min free trial funnel (form ID 261002359315044).
const MONITORED_FORMS = {
  pilotOnboarding: '261002359315044',  // Pilot Onboarding (200-min trial)
  // hvacStandardOnboarding: from config (existing Standard form, if any)
};

async function checkJotform() {
  const checks = [];
  let healthy = true;
  const data = {};

  try {
    const apiKey = process.env.JOTFORM_API_KEY;
    const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY);

    // Fetch all form submissions ONCE per run — used for both staleness + orphan detection
    // NOTE: No separate /user connectivity ping — that wastes a rate-limit slot.
    // If the first form fetch succeeds we know the API is reachable. If it 429s, we bail.
    const formSubmissions = {};
    let apiReachable = true;

    // Use MONITORED_FORMS (inline) instead of config.jotform.forms — Premium form removed, pilot added.
    for (const [formKey, formId] of Object.entries(MONITORED_FORMS)) {
      try {
        const res = await fetch(
          `${JF_API}/form/${formId}/submissions?apiKey=${apiKey}&limit=20&orderby=created_at`
        );

        // 429 = rate limited — bail immediately, single alert, do not continue checking
        if (res.status === 429) {
          apiReachable = false;
          healthy = false;
          checks.push({ name: 'Jotform API', ok: false, detail: 'HTTP 429 — rate limited' });
          await alertManager.alert({
            system: 'Jotform', check: 'api-connectivity', tier: 'warning',
            title: 'Jotform Rate Limited',
            message: 'Jotform API returned HTTP 429. Monitor will retry next cycle. No action needed unless this persists >1 hour.',
          });
          statusStore.update('jotform', { healthy: false, checks });
          return;
        }

        if (!res.ok) {
          checks.push({ name: `Form: ${formKey}`, ok: false, detail: `HTTP ${res.status}` });
          formSubmissions[formKey] = [];
          continue;
        }

        // First successful fetch = API is reachable
        if (apiReachable && !checks.find(c => c.name === 'Jotform API')) {
          checks.push({ name: 'Jotform API', ok: true, detail: 'Connected' });
        }

        const formData = await res.json();
        formSubmissions[formKey] = formData.content || [];
        const submissions = formSubmissions[formKey];
        data[formKey] = { totalSubmissions: submissions.length };

        if (submissions.length > 0) {
          const latestDate = new Date(submissions[0].created_at);
          const daysSince = (Date.now() - latestDate.getTime()) / 1000 / 3600 / 24;
          if (daysSince > 30) {
            checks.push({ name: `Form: ${formKey}`, ok: false, detail: `Stale — no submissions in ${Math.round(daysSince)} days` });
          } else {
            checks.push({ name: `Form: ${formKey}`, ok: true, detail: `${submissions.length} recent, last ${Math.round(daysSince)}d ago` });
          }
        } else {
          checks.push({ name: `Form: ${formKey}`, ok: true, detail: 'No submissions yet' });
        }
      } catch (err) {
        checks.push({ name: `Form: ${formKey}`, ok: false, detail: err.message });
        formSubmissions[formKey] = [];
      }
    }

    // Orphan detection — bulk Supabase fetch, compare in memory. Zero extra Jotform calls.
    try {
      const { data: stdRows } = await supabase.from(config.supabase.tables.hvacStandardAgent).select('company_name, client_email');
      const { data: premRows } = await supabase.from(config.supabase.tables.hvacStandardAgent).select('company_name, client_email').eq('plan_type', 'premium');

      const knownCompanies = new Set([
        ...(stdRows || []).map(r => (r.company_name || '').toLowerCase().trim()),
        ...(premRows || []).map(r => (r.company_name || '').toLowerCase().trim()),
      ].filter(Boolean));
      const knownEmails = new Set([
        ...(stdRows || []).map(r => (r.client_email || '').toLowerCase().trim()),
        ...(premRows || []).map(r => (r.client_email || '').toLowerCase().trim()),
      ].filter(Boolean));

      let orphanCount = 0;
      for (const [, submissions] of Object.entries(formSubmissions)) {
        for (const sub of submissions) {
          if (sub.status !== 'ACTIVE') continue;
          const subAge = (Date.now() - new Date(sub.created_at).getTime()) / 1000 / 3600;
          if (subAge < 1) continue;
          const answers = Object.values(sub.answers || {});
          const company = (answers.find(a => a.name?.toLowerCase().includes('company'))?.answer || '').toLowerCase().trim();
          const email = (answers.find(a => a.name?.toLowerCase().includes('email'))?.answer || '').toLowerCase().trim();
          if (!company && !email) continue;
          if (!((company && knownCompanies.has(company)) || (email && knownEmails.has(email)))) orphanCount++;
        }
      }

      data.orphanedSubmissions = orphanCount;
      checks.push({
        name: 'Orphaned submissions',
        ok: orphanCount === 0,
        detail: orphanCount === 0 ? 'None detected' : `${orphanCount} orphaned`,
      });

      if (orphanCount > 0) {
        await alertManager.alert({
          system: 'Jotform', check: 'orphaned-submissions', tier: 'warning',
          title: `${orphanCount} Orphaned Jotform Submissions`,
          message: `${orphanCount} Jotform submissions have no matching Supabase row.`,
        });
      }
    } catch (err) {
      checks.push({ name: 'Orphaned submissions', ok: false, detail: err.message });
    }

  } catch (err) {
    healthy = false;
    checks.push({ name: 'Jotform', ok: false, detail: err.message });
  }

  statusStore.update('jotform', { healthy, checks, data });
  console.log(`[Jotform] Check complete — ${healthy ? '✅ healthy' : '❌ issues found'}`);
}

module.exports = { checkJotform };
