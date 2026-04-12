// src/monitors/infrastructure.js — External endpoint & infrastructure health
// Monitors: website, checkout, OAuth server, all webhook endpoints, Railway services, DNS/SSL
const fetch = require('node-fetch');
const config = require('../config');
const alertManager = require('../utils/alertManager');
const statusStore = require('../utils/statusStore');

const ENDPOINTS = {
  // Public-facing websites
  website:        { url: 'https://syntharra.com', method: 'GET', name: 'Website (syntharra.com)', critical: true },
  checkoutPage:   { url: 'https://checkout.syntharra.com', method: 'GET', name: 'Checkout Page', critical: true },
  oauthServer:    { url: 'https://auth.syntharra.com', method: 'GET', name: 'OAuth Server', critical: false },
  dashboard:      { url: 'https://syntharra.com/dashboard.html', method: 'GET', name: 'Client Dashboard', critical: false },
  demo:           { url: 'https://syntharra.com/demo.html', method: 'GET', name: 'Demo Page', critical: true },
  n8nCloud:       { url: 'https://n8n.syntharra.com', method: 'GET', name: 'n8n (Railway)', critical: true },
  opsMonitor:     { url: 'https://syntharra-ops-monitor-production.up.railway.app/api/health', method: 'GET', name: 'Ops Monitor API', critical: false },

  // Webhook endpoints — use HEAD to verify endpoint exists without triggering workflow
  // NEVER use POST here — it triggers real workflow processing and creates ghost data
  retellWebhook:        { url: 'https://n8n.syntharra.com/webhook/retell-hvac-webhook', method: 'HEAD', name: 'Retell Call Webhook', critical: true, expectStatus: [200, 404] },
  stripeWebhook:        { url: 'https://n8n.syntharra.com/webhook/syntharra-stripe-webhook', method: 'HEAD', name: 'Stripe Webhook', critical: true, expectStatus: [200, 404] },
  jotformStdWebhook:    { url: 'https://n8n.syntharra.com/webhook/jotform-hvac-onboarding', method: 'HEAD', name: 'Jotform Std Webhook', critical: true, expectStatus: [200, 404] },
  // jotformPremWebhook REMOVED — Premium plan RETIRED 2026-04-09.
};

async function checkInfrastructure() {
  const checks = [];
  let healthy = true;
  const data = { endpoints: {} };

  // 1. Check all endpoints
  for (const [key, endpoint] of Object.entries(ENDPOINTS)) {
    try {
      const start = Date.now();
      const opts = {
        method: endpoint.method,
        headers: { 'Content-Type': 'application/json' },
        redirect: 'follow',
        timeout: 10000,
      };
      if (endpoint.method === 'POST') opts.body = '{}';

      const res = await fetch(endpoint.url, opts);
      const latency = Date.now() - start;
      // Webhooks checked with HEAD return 404 (endpoint exists but only accepts POST) — that's OK
      const expectedStatuses = endpoint.expectStatus || null;
      const ok = expectedStatuses
        ? expectedStatuses.includes(res.status)
        : (res.status >= 200 && res.status < 400);

      data.endpoints[key] = { status: res.status, latency, ok };

      checks.push({
        name: endpoint.name,
        ok,
        detail: ok
          ? `${res.status} (${latency}ms)`
          : `HTTP ${res.status} (${latency}ms)`,
      });

      // Alert on slow responses (>5s)
      if (ok && latency > 5000) {
        await alertManager.alert({
          system: 'Infrastructure', check: `slow-${key}`, tier: 'warning',
          title: `Slow Response: ${endpoint.name}`,
          message: `${endpoint.name} responded in ${latency}ms (>5s threshold).`,
        });
      }

      if (!ok && endpoint.critical) {
        healthy = false;
        await alertManager.alert({
          system: 'Infrastructure', check: `down-${key}`, tier: 'critical',
          title: `Endpoint Down: ${endpoint.name}`,
          message: `${endpoint.name} returned HTTP ${res.status}. URL: ${endpoint.url}`,
        });
      }
    } catch (err) {
      checks.push({ name: endpoint.name, ok: false, detail: `Timeout/Error: ${err.message.slice(0, 80)}` });
      data.endpoints[key] = { status: 0, latency: 0, ok: false };
      if (endpoint.critical) {
        healthy = false;
        await alertManager.alert({
          system: 'Infrastructure', check: `unreachable-${key}`, tier: 'critical',
          title: `Unreachable: ${endpoint.name}`,
          message: `Cannot reach ${endpoint.name}: ${err.message.slice(0, 100)}`,
        });
      }
    }
  }

  // 2. SSL — inferred from ENDPOINTS check results above (HTTPS success = SSL valid)
  // Separate SSL HEAD requests removed — they duplicated the endpoint checks and doubled requests
  const sslDomains = {
    'syntharra.com':          'website',
    'checkout.syntharra.com': 'checkoutPage',
    'auth.syntharra.com':     'oauthServer',
  };
  for (const [domain, endpointKey] of Object.entries(sslDomains)) {
    const endpointResult = data.endpoints[endpointKey];
    if (endpointResult) {
      // If endpoint responded (even with 4xx), HTTPS/SSL is working
      const sslOk = endpointResult.status > 0;
      checks.push({
        name: `SSL: ${domain}`,
        ok: sslOk,
        detail: sslOk ? 'Valid (inferred from HTTPS endpoint check)' : 'Unreachable — may indicate SSL issue',
      });
    }
  }

  // 3. Railway services health via API
  // input: syntax is correct per live schema introspection (2026-04-03)
  // Status filter excludes REMOVED/REMOVING/SKIPPED so first:1 = most recent active deployment
  // TRANSIENT states (DEPLOYING, BUILDING, etc.) are healthy — only alert on FAILED/CRASHED
  if (process.env.RAILWAY_TOKEN) {
    try {
      const serviceId = config.railway?.checkoutServiceId || 'e3df3e6d-6824-498f-bb4a-fdb6598f7638';
      const envId = config.railway?.envId || '5303bcf8-43a4-4a95-8e0c-75909094e02e';
      const gqlRes = await fetch('https://backboard.railway.com/graphql/v2', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${process.env.RAILWAY_TOKEN}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: `{
            deployments(
              first: 1,
              input: {
                serviceId: "${serviceId}",
                environmentId: "${envId}",
                status: { notIn: [REMOVED, REMOVING, SKIPPED] }
              }
            ) {
              edges { node { status createdAt } }
            }
          }`,
        }),
      });
      if (gqlRes.ok) {
        const gqlData = await gqlRes.json();
        if (gqlData.errors) {
          checks.push({ name: 'Railway API', ok: false, detail: gqlData.errors[0]?.message?.slice(0, 80) });
        } else {
          const deploy = gqlData?.data?.deployments?.edges?.[0]?.node;
          const TRANSIENT = ['DEPLOYING', 'INITIALIZING', 'BUILDING', 'QUEUED', 'WAITING', 'NEEDS_APPROVAL'];
          const deployOk = deploy?.status === 'SUCCESS' || TRANSIENT.includes(deploy?.status);
          const statusLabel = deploy?.status || 'no-deployments';
          checks.push({ name: 'Railway: Checkout', ok: deployOk, detail: statusLabel });
          if (!deployOk) {
            await alertManager.alert({
              system: 'Infrastructure', check: 'railway-checkout', tier: 'warning',
              title: 'Railway Checkout Deploy Issue',
              message: `Checkout service deployment status: ${statusLabel}`,
            });
          }
        }
      } else {
        const errBody = await gqlRes.text();
        checks.push({ name: 'Railway API', ok: false, detail: `HTTP ${gqlRes.status}: ${errBody.slice(0, 80)}` });
      }
    } catch (err) {
      checks.push({ name: 'Railway API', ok: false, detail: err.message });
    }
  }

  statusStore.update('infrastructure', { healthy, checks, data });
  console.log(`[Infrastructure] Check complete — ${healthy ? '✅ healthy' : '❌ issues found'}`);
}

module.exports = { checkInfrastructure };
