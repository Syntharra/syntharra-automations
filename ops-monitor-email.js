// src/monitors/email.js — Brevo email delivery health monitoring
// Strategy: verify Brevo API credentials, account health, delivery stats, service status
const fetch = require('node-fetch');
const alertManager = require('../utils/alertManager');
const statusStore = require('../utils/statusStore');

async function checkEmail() {
  const checks = [];
  let healthy = true;

  try {
    const apiKey = process.env.BREVO_API_KEY;

    // 1. Brevo credentials present (renamed from "SMTP credentials" 2026-04-11)
    if (!apiKey) {
      healthy = false;
      checks.push({ name: 'Brevo credentials', ok: false, detail: 'BREVO_API_KEY not set — no emails will send' });
      await alertManager.alert({
        system: 'Email', check: 'brevo-credentials-missing', tier: 'critical',
        title: 'Brevo API Key Missing',
        message: 'BREVO_API_KEY environment variable is not set. All transactional email is down.',
      });
      statusStore.update('email', { healthy, checks });
      return;
    }

    checks.push({ name: 'Brevo credentials', ok: true, detail: 'Configured' });

    // 2. Brevo API connectivity — test account endpoint (no email sent)
    try {
      const res = await fetch('https://api.brevo.com/v3/account', {
        headers: { 'api-key': apiKey, 'accept': 'application/json' },
        timeout: 8000,
      });
      if (res.ok) {
        const data = await res.json();
        const plan = data.plan?.[0]?.type || 'unknown';
        checks.push({ name: 'Brevo API', ok: true, detail: `Connected (${data.email}, plan: ${plan})` });
      } else {
        healthy = false;
        checks.push({ name: 'Brevo API', ok: false, detail: `HTTP ${res.status} — check API key` });
        await alertManager.alert({
          system: 'Email', check: 'brevo-api-error', tier: 'critical',
          title: 'Brevo API Error',
          message: `Brevo API returned HTTP ${res.status}. Transactional email may be down.`,
        });
      }
    } catch (err) {
      checks.push({ name: 'Brevo API', ok: false, detail: err.message });
      healthy = false;
    }

    // 3. Brevo transactional delivery stats — last 7 days
    try {
      const toDate = new Date().toISOString().slice(0, 10);
      const fromDate = new Date(Date.now() - 7 * 24 * 3600 * 1000).toISOString().slice(0, 10);
      const res = await fetch(
        `https://api.brevo.com/v3/smtp/statistics/aggregatedReport?startDate=${fromDate}&endDate=${toDate}`,
        { headers: { 'api-key': apiKey, 'accept': 'application/json' }, timeout: 8000 }
      );
      if (res.ok) {
        const stats = await res.json();
        const sent = stats.requests || 0;
        const delivered = stats.delivered || 0;
        const hardBounces = stats.hardBounces || 0;
        const softBounces = stats.softBounces || 0;
        const bounced = hardBounces + softBounces;
        const deliveryRate = sent > 0 ? ((delivered / sent) * 100).toFixed(1) : null;
        const bounceRate = sent > 0 ? ((bounced / sent) * 100).toFixed(1) : '0';

        const deliveryOk = sent === 0 || parseFloat(deliveryRate) > 85;
        checks.push({
          name: 'Delivery rate (7d)',
          ok: deliveryOk,
          detail: sent === 0
            ? 'No emails sent in 7 days'
            : `${deliveryRate}% delivered (${delivered}/${sent}), ${bounceRate}% bounced`,
        });

        if (sent > 0 && !deliveryOk) {
          await alertManager.alert({
            system: 'Email', check: 'low-delivery-rate', tier: 'warning',
            title: `Low Email Delivery Rate: ${deliveryRate}%`,
            message: `Only ${delivered}/${sent} emails delivered in the last 7 days. Bounce rate: ${bounceRate}%. Check Brevo sender reputation.`,
          });
        }
      } else {
        checks.push({ name: 'Delivery stats', ok: false, detail: `Stats API HTTP ${res.status}` });
      }
    } catch (err) {
      checks.push({ name: 'Delivery stats', ok: false, detail: err.message });
    }

    // 4. Brevo service status — public statuspage (no auth)
    try {
      const res = await fetch('https://status.brevo.com/api/v2/status.json', { timeout: 8000 });
      if (res.ok) {
        const data = await res.json();
        const indicator = data?.status?.indicator || 'unknown';
        const description = data?.status?.description || 'Unknown';
        const serviceOk = indicator === 'none';
        checks.push({
          name: 'Brevo service',
          ok: serviceOk,
          detail: serviceOk ? 'Operational' : `${indicator.toUpperCase()}: ${description}`,
        });
        if (!serviceOk) {
          healthy = false;
          await alertManager.alert({
            system: 'Email', check: 'brevo-service-degraded',
            tier: indicator === 'critical' ? 'critical' : 'warning',
            title: `Brevo Service Degraded: ${indicator}`,
            message: `Brevo status: ${description}. Email delivery may be affected.`,
          });
        }
      } else {
        checks.push({ name: 'Brevo service', ok: true, detail: `Status page HTTP ${res.status} — assuming operational` });
      }
    } catch (err) {
      checks.push({ name: 'Brevo service', ok: true, detail: 'Status page unreachable — assuming operational' });
    }

    // 5. Telnyx SMS readiness
    const telnyxKey = process.env.TELNYX_API_KEY;
    const telnyxReady = !!(telnyxKey && telnyxKey.startsWith('KEY'));
    checks.push({
      name: 'Telnyx SMS',
      ok: true, // informational only — not critical until Telnyx approval lands
      detail: telnyxReady ? 'Configured & ready' : 'Awaiting Telnyx approval — SMS alerts paused',
    });

  } catch (err) {
    healthy = false;
    checks.push({ name: 'Email monitor', ok: false, detail: err.message });
  }

  statusStore.update('email', { healthy, checks });
  console.log(`[Email] Check complete — ${healthy ? '✅ healthy' : '❌ issues found'}`);
}

module.exports = { checkEmail };
