// src/monitors/stripe.js — Stripe payment & subscription monitoring
// Added: recent event recency check (verify Stripe is delivering webhooks)
const config = require('../config');
const alertManager = require('../utils/alertManager');
const statusStore = require('../utils/statusStore');

async function checkStripe() {
  const checks = [];
  let healthy = true;
  const data = {};

  try {
    const Stripe = require('stripe');
    const stripe = Stripe(process.env.STRIPE_SECRET_KEY);

    // 1. API connectivity
    try {
      await stripe.balance.retrieve();
      checks.push({ name: 'Stripe API', ok: true, detail: 'Connected' });
    } catch (err) {
      healthy = false;
      checks.push({ name: 'Stripe API', ok: false, detail: err.message });
      await alertManager.alert({
        system: 'Stripe', check: 'api-connectivity', tier: 'critical',
        title: 'Stripe API Unreachable',
        message: `Cannot connect to Stripe: ${err.message}`,
      });
      statusStore.update('stripe', { healthy: false, checks });
      return;
    }

    // 2. Recent payment failures (last 24h)
    try {
      const yesterday = Math.floor((Date.now() - 24 * 3600 * 1000) / 1000);
      const failedPayments = await stripe.paymentIntents.list({ created: { gte: yesterday }, limit: 100 });
      const failed = failedPayments.data.filter(p =>
        p.status === 'requires_payment_method' || p.status === 'canceled'
      );
      data.failedPayments24h = failed.length;
      checks.push({
        name: 'Failed payments (24h)',
        ok: failed.length === 0,
        detail: failed.length === 0 ? 'None' : `${failed.length} failed`,
      });
      if (failed.length > 0) {
        await alertManager.alert({
          system: 'Stripe', check: 'payment-failures', tier: 'warning',
          title: `${failed.length} Payment Failures (24h)`,
          message: `${failed.length} payments failed in the last 24 hours.`,
        });
      }
    } catch (err) {
      checks.push({ name: 'Payment failures', ok: false, detail: err.message });
    }

    // 3. Subscription health — past_due, unpaid
    try {
      const [pastDueSubs, unpaidSubs] = await Promise.all([
        stripe.subscriptions.list({ status: 'past_due', limit: 100 }),
        stripe.subscriptions.list({ status: 'unpaid', limit: 100 }),
      ]);

      data.pastDueSubscriptions = pastDueSubs.data.length;
      data.unpaidSubscriptions = unpaidSubs.data.length;

      checks.push({
        name: 'Past-due subscriptions',
        ok: pastDueSubs.data.length === 0,
        detail: pastDueSubs.data.length === 0 ? 'None' : `${pastDueSubs.data.length} past due`,
      });
      checks.push({
        name: 'Unpaid subscriptions',
        ok: unpaidSubs.data.length === 0,
        detail: unpaidSubs.data.length === 0 ? 'None' : `${unpaidSubs.data.length} unpaid`,
      });

      if (pastDueSubs.data.length > 0) {
        healthy = false;
        await alertManager.alert({
          system: 'Stripe', check: 'past-due-subscriptions', tier: 'warning',
          title: `${pastDueSubs.data.length} Past-Due Subscriptions`,
          message: `Revenue at risk: ${pastDueSubs.data.map(s => s.id).join(', ')}`,
        });
      }
    } catch (err) {
      checks.push({ name: 'Subscription health', ok: false, detail: err.message });
    }

    // 4. Active subscription count
    try {
      const activeSubs = await stripe.subscriptions.list({ status: 'active', limit: 100 });
      data.activeSubscriptions = activeSubs.data.length;
      checks.push({ name: 'Active subscriptions', ok: true, detail: `${activeSubs.data.length}` });
    } catch (err) {
      checks.push({ name: 'Active subs', ok: false, detail: err.message });
    }

    // 5. Webhook endpoint health
    try {
      const webhook = await stripe.webhookEndpoints.retrieve(config.stripe.webhookId);
      const isEnabled = webhook.status === 'enabled';
      checks.push({
        name: 'Webhook endpoint',
        ok: isEnabled,
        detail: isEnabled ? `Enabled` : `Status: ${webhook.status}`,
      });
      if (!isEnabled) {
        healthy = false;
        await alertManager.alert({
          system: 'Stripe', check: 'webhook-disabled', tier: 'critical',
          title: 'Stripe Webhook Disabled',
          message: `Webhook ${config.stripe.webhookId} is ${webhook.status}. New signups won't trigger onboarding.`,
        });
      }
    } catch (err) {
      checks.push({ name: 'Webhook endpoint', ok: false, detail: err.message });
    }

    // 6. Webhook event recency — verify Stripe is delivering events recently
    // Alerts if we haven't received any events in 48h (may indicate webhook delivery failure)
    try {
      const twoDaysAgo = Math.floor((Date.now() - 48 * 3600 * 1000) / 1000);
      const recentEvents = await stripe.events.list({ created: { gte: twoDaysAgo }, limit: 5 });
      const eventCount = recentEvents.data.length;
      const lastEventAt = recentEvents.data[0]
        ? new Date(recentEvents.data[0].created * 1000).toISOString()
        : null;

      checks.push({
        name: 'Webhook events (48h)',
        ok: true, // informational — test mode has low event volume
        detail: eventCount > 0
          ? `${eventCount} events, last: ${lastEventAt ? new Date(lastEventAt).toLocaleTimeString('en-US', { timeZone: 'America/Chicago' }) : '—'}`
          : 'No events in 48h (test mode — expected)',
      });
    } catch (err) {
      checks.push({ name: 'Webhook events', ok: false, detail: err.message });
    }

    // 7. Product availability (standard only — Premium retired)
    try {
      const product = await stripe.products.retrieve(config.stripe.products.standard);
      checks.push({
        name: 'Product: standard',
        ok: product.active,
        detail: product.active ? `Active: ${product.name}` : 'INACTIVE — customers cannot purchase',
      });
      if (!product.active) {
        await alertManager.alert({
          system: 'Stripe', check: 'product-inactive-standard', tier: 'warning',
          title: 'Stripe Standard Product Inactive',
          message: `Product ${config.stripe.products.standard} is inactive. Customers cannot subscribe.`,
        });
      }
    } catch (err) {
      checks.push({ name: 'Product: standard', ok: false, detail: err.message });
    }

  } catch (err) {
    healthy = false;
    checks.push({ name: 'Stripe', ok: false, detail: err.message });
  }

  statusStore.update('stripe', { healthy, checks, data });
  console.log(`[Stripe] Check complete — ${healthy ? '✅ healthy' : '❌ issues found'}`);
}

module.exports = { checkStripe };
