// src/monitors/revenue.js — Revenue & business metrics monitoring
// Tracks: MRR, lead conversion, website leads, churn signals, usage trends
const { createClient } = require('@supabase/supabase-js');
const config = require('../config');
const alertManager = require('../utils/alertManager');
const statusStore = require('../utils/statusStore');

async function checkRevenue() {
  const checks = [];
  let healthy = true;
  const data = {};

  try {
    const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY);
    const Stripe = require('stripe');
    const stripe = Stripe(process.env.STRIPE_SECRET_KEY);

    // 1. Active subscriptions & MRR
    try {
      const activeSubs = await stripe.subscriptions.list({ status: 'active', limit: 100 });
      const mrr = activeSubs.data.reduce((sum, sub) => {
        const amount = sub.items?.data?.[0]?.price?.unit_amount || 0;
        const interval = sub.items?.data?.[0]?.price?.recurring?.interval;
        // Normalize to monthly
        return sum + (interval === 'year' ? Math.round(amount / 12) : amount);
      }, 0);

      // mrr from Stripe is in cents (unit_amount). Divide by 100 to store dollars.
      // Bug fix 2026-04-09: was storing raw cents → displayed $2,175,417 instead of $21,754.
      const mrrDollars = Math.round(mrr / 100);

      data.activeSubscriptions = activeSubs.data.length;
      data.mrr = mrrDollars;  // stored in DOLLARS, not cents

      checks.push({
        name: 'MRR',
        ok: true,
        detail: `$${mrrDollars.toLocaleString()}/mo from ${activeSubs.data.length} subscriptions (TEST MODE)`,
      });
    } catch (err) {
      checks.push({ name: 'MRR', ok: false, detail: err.message });
    }

    // 2. Recent signups (last 30 days)
    try {
      const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 3600 * 1000).toISOString();
      const { data: recentPayments, count } = await supabase
        .from(config.supabase.tables.stripePaymentData)
        .select('*', { count: 'exact' })
        .gte('created_at', thirtyDaysAgo);

      data.signups30d = count || 0;
      checks.push({ name: 'Signups (30d)', ok: true, detail: `${count || 0} new clients` });
    } catch (err) {
      checks.push({ name: 'Signups', ok: false, detail: err.message });
    }

    // 3. Website lead funnel
    try {
      const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 3600 * 1000).toISOString();
      const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 3600 * 1000).toISOString();

      const { count: leads7d } = await supabase
        .from(config.supabase.tables.websiteLeads)
        .select('*', { count: 'exact', head: true })
        .gte('created_at', sevenDaysAgo);

      const { count: leads30d } = await supabase
        .from(config.supabase.tables.websiteLeads)
        .select('*', { count: 'exact', head: true })
        .gte('created_at', thirtyDaysAgo);

      const { count: unsubscribed } = await supabase
        .from(config.supabase.tables.websiteLeads)
        .select('*', { count: 'exact', head: true })
        .eq('unsubscribed', true);

      data.leads7d = leads7d || 0;
      data.leads30d = leads30d || 0;
      data.unsubscribed = unsubscribed || 0;

      checks.push({
        name: 'Website leads',
        ok: true,
        detail: `${leads7d || 0} (7d), ${leads30d || 0} (30d), ${unsubscribed || 0} unsubscribed`,
      });
    } catch (err) {
      checks.push({ name: 'Website leads', ok: false, detail: err.message });
    }

    // 4. Call-to-lead conversion (last 7 days)
    try {
      const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 3600 * 1000).toISOString();

      const { count: totalCalls } = await supabase
        .from(config.supabase.tables.hvacCallLog)
        .select('*', { count: 'exact', head: true })
        .gte('call_timestamp', sevenDaysAgo);

      const { count: totalLeads } = await supabase
        .from(config.supabase.tables.hvacCallLog)
        .select('*', { count: 'exact', head: true })
        .gte('call_timestamp', sevenDaysAgo)
        .eq('is_lead', true);

      const conversionRate = (totalCalls || 0) > 0
        ? ((totalLeads || 0) / (totalCalls || 1) * 100).toFixed(0)
        : 'N/A';

      data.callToLeadRate7d = conversionRate;
      checks.push({
        name: 'Call→Lead rate (7d)',
        ok: true,
        detail: `${conversionRate}% (${totalLeads || 0} leads from ${totalCalls || 0} calls)`,
      });
    } catch (err) {
      checks.push({ name: 'Conversion rate', ok: false, detail: err.message });
    }

    // 5. Churn signals — past_due, cancelled, usage drop-off
    try {
      const pastDueSubs = await stripe.subscriptions.list({ status: 'past_due', limit: 100 });
      const cancelledRecent = await stripe.subscriptions.list({
        status: 'canceled',
        limit: 10,
      });
      // Filter cancelled in last 30 days
      const thirtyDaysAgoUnix = Math.floor((Date.now() - 30 * 24 * 3600 * 1000) / 1000);
      const recentCancels = cancelledRecent.data.filter(s => s.canceled_at && s.canceled_at > thirtyDaysAgoUnix);

      data.pastDue = pastDueSubs.data.length;
      data.cancelledRecent = recentCancels.length;

      const churnOk = pastDueSubs.data.length === 0 && recentCancels.length === 0;
      checks.push({
        name: 'Churn signals',
        ok: churnOk,
        detail: churnOk
          ? 'No churn signals'
          : `${pastDueSubs.data.length} past-due, ${recentCancels.length} cancelled (30d)`,
      });

      if (pastDueSubs.data.length > 0) {
        await alertManager.alert({
          system: 'Revenue', check: 'past-due', tier: 'warning',
          title: `${pastDueSubs.data.length} Past-Due Subscription(s)`,
          message: `Revenue at risk: ${pastDueSubs.data.map(s => s.id).join(', ')}`,
        });
      }
    } catch (err) {
      checks.push({ name: 'Churn signals', ok: false, detail: err.message });
    }

    // 6. Affiliate applications
    try {
      const { count: pendingAffiliates } = await supabase
        .from(config.supabase.tables.affiliateApps)
        .select('*', { count: 'exact', head: true })
        .eq('status', 'pending');

      if ((pendingAffiliates || 0) > 0) {
        checks.push({
          name: 'Affiliate apps',
          ok: true,
          detail: `${pendingAffiliates} pending review`,
        });
      }
    } catch (err) {
      // Not critical, skip silently
    }

  } catch (err) {
    healthy = false;
    checks.push({ name: 'Revenue monitor', ok: false, detail: err.message });
  }

  const hasFailedChecks = checks.some(c => !c.ok);
  healthy = !hasFailedChecks;

  statusStore.update('revenue', { healthy, checks, data });
  console.log(`[Revenue] Check complete — ${healthy ? '✅ healthy' : '❌ issues found'}`);
}

module.exports = { checkRevenue };
