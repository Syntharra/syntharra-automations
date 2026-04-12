// src/monitors/revenue.js — Revenue & business metrics monitoring
// Tracks: MRR, churn signals, website leads, pilot funnel health
// NOTE: hvac_call_log was dropped 2026-04-09 — call-to-lead rate no longer tracked here.
//       Use Retell monitor for call volume data.
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
        return sum + (interval === 'year' ? Math.round(amount / 12) : amount);
      }, 0);
      // mrr from Stripe is in cents. Divide by 100 to get dollars.
      const mrrDollars = Math.round(mrr / 100);
      data.activeSubscriptions = activeSubs.data.length;
      data.mrr = mrrDollars;
      checks.push({
        name: 'MRR',
        ok: true,
        detail: `$${mrrDollars.toLocaleString()}/mo from ${activeSubs.data.length} subscriptions (TEST MODE)`,
      });
    } catch (err) {
      checks.push({ name: 'MRR', ok: false, detail: err.message });
    }

    // 2. Website lead funnel
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

      data.leads7d = leads7d || 0;
      data.leads30d = leads30d || 0;

      checks.push({
        name: 'Website leads',
        ok: true,
        detail: `${leads7d || 0} (7d), ${leads30d || 0} (30d)`,
      });

      // Alert if zero leads in 7 days — funnel may be broken
      if ((leads7d || 0) === 0 && (leads30d || 0) > 0) {
        await alertManager.alert({
          system: 'Revenue', check: 'zero-leads-7d', tier: 'warning',
          title: 'No New Website Leads in 7 Days',
          message: 'Zero new website leads captured in the last 7 days. Check lead form and website traffic.',
        });
      }
    } catch (err) {
      checks.push({ name: 'Website leads', ok: false, detail: err.message });
    }

    // 3. Recent signups (last 30 days from Stripe payments)
    try {
      const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 3600 * 1000).toISOString();
      const { count } = await supabase
        .from(config.supabase.tables.stripePaymentData)
        .select('*', { count: 'exact', head: true })
        .gte('created_at', thirtyDaysAgo);

      data.signups30d = count || 0;
      checks.push({ name: 'Signups (30d)', ok: true, detail: `${count || 0} new clients` });
    } catch (err) {
      checks.push({ name: 'Signups (30d)', ok: false, detail: err.message });
    }

    // 4. Pilot funnel health (Phase 0)
    // Tracks pilots from client_subscriptions table — set by pilot_lifecycle.py
    try {
      const { data: allSubs, error: subsError } = await supabase
        .from(config.supabase.tables.clientSubscriptions)
        .select('status, pilot_expires_at, minutes_used, minutes_limit, created_at');

      if (!subsError && allSubs) {
        const now = new Date();
        const pilotRows = allSubs.filter(s => s.status === 'pilot');
        const activePilots = pilotRows.length;

        // Pilots expiring in < 3 days
        const soonExpiring = pilotRows.filter(s => {
          if (!s.pilot_expires_at) return false;
          const expiresAt = new Date(s.pilot_expires_at);
          const daysLeft = (expiresAt - now) / (1000 * 3600 * 24);
          return daysLeft >= 0 && daysLeft < 3;
        });

        // Pilots that converted (status = 'active' or 'paid')
        const convertedThisMonth = allSubs.filter(s => {
          const monthAgo = new Date(Date.now() - 30 * 24 * 3600 * 1000);
          return (s.status === 'active' || s.status === 'paid') && new Date(s.created_at) > monthAgo;
        }).length;

        // Expired pilots (status = 'expired')
        const expiredThisMonth = allSubs.filter(s => {
          const monthAgo = new Date(Date.now() - 30 * 24 * 3600 * 1000);
          return s.status === 'expired' && new Date(s.created_at) > monthAgo;
        }).length;

        data.activePilots = activePilots;
        data.convertedThisMonth = convertedThisMonth;

        checks.push({
          name: 'Pilot funnel',
          ok: true,
          detail: `${activePilots} active pilots, ${convertedThisMonth} converted (30d), ${expiredThisMonth} expired (30d)`,
        });

        if (soonExpiring.length > 0) {
          checks.push({
            name: 'Pilots expiring soon',
            ok: false, // surface as warning to prompt follow-up
            detail: `${soonExpiring.length} pilot(s) expiring within 3 days`,
          });
          await alertManager.alert({
            system: 'Revenue', check: 'pilots-expiring-soon', tier: 'warning',
            title: `${soonExpiring.length} Pilot(s) Expiring in < 3 Days`,
            message: `${soonExpiring.length} pilots expire within 3 days. Send conversion push or extend via pilot_lifecycle.py.`,
          });
        }

        // Pilots at 80%+ of minute allowance
        const nearLimit = pilotRows.filter(s =>
          s.minutes_used && s.minutes_limit && (s.minutes_used / s.minutes_limit) >= 0.8
        );
        if (nearLimit.length > 0) {
          checks.push({
            name: 'Pilots near limit',
            ok: false,
            detail: `${nearLimit.length} pilot(s) at 80%+ of minute allowance`,
          });
          await alertManager.alert({
            system: 'Revenue', check: 'pilots-near-minute-limit', tier: 'warning',
            title: `${nearLimit.length} Pilot(s) Near Minute Limit`,
            message: `${nearLimit.length} pilot(s) have used 80%+ of their included minutes. Review and upsell.`,
          });
        }
      } else {
        // client_subscriptions table may not exist yet (pre-first pilot)
        checks.push({ name: 'Pilot funnel', ok: true, detail: 'No pilot data yet (pre-launch)' });
      }
    } catch (err) {
      // Table may not exist — don't mark unhealthy
      checks.push({ name: 'Pilot funnel', ok: true, detail: `Unavailable: ${err.message.slice(0, 60)}` });
    }

    // 5. Churn signals — past_due, recent cancellations
    try {
      const pastDueSubs = await stripe.subscriptions.list({ status: 'past_due', limit: 100 });
      const cancelledRecent = await stripe.subscriptions.list({ status: 'canceled', limit: 10 });
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

    // 6. Affiliate applications (non-critical, informational)
    try {
      const { count: pendingAffiliates } = await supabase
        .from(config.supabase.tables.affiliateApps)
        .select('*', { count: 'exact', head: true })
        .eq('status', 'pending');

      if ((pendingAffiliates || 0) > 0) {
        checks.push({ name: 'Affiliate apps', ok: true, detail: `${pendingAffiliates} pending review` });
      }
    } catch (_) {
      // Non-critical — skip silently
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
