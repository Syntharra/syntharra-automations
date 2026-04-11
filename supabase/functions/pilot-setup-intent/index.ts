// pilot-setup-intent
// Phase 0 pilot Stripe Setup Intent endpoint. Called by the pilot dashboard
// "Add Card" CTA. Looks up the pilot's client_subscriptions row, creates (or
// reuses) a Stripe customer, creates a Setup Intent, and returns the
// client_secret for the frontend Stripe Elements form.
//
// Public endpoint: verify_jwt=false. The agent_id is the access token — only
// someone who knows the agent_id (= the pilot owner who got the welcome email
// link) can create a Setup Intent against that pilot's row. The agent_id is a
// long random string from Retell, hard to guess.
//
// Stripe key fetched from syntharra_vault (service_name='Stripe',
// key_type='secret_key_test' for test mode; will switch to secret_key_live
// when Dan vaults the live key + we deploy a new version of this function).
//
// Spec: docs/superpowers/specs/2026-04-10-phase-0-vsl-funnel-design.md § 6.4
// + Day 3 Task 21

import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? "";
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";

const CORS_HEADERS: Record<string, string> = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "content-type, x-synth-asset",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json", ...CORS_HEADERS },
  });
}

async function fetchVault(serviceName: string, keyType: string): Promise<string | null> {
  const url =
    `${SUPABASE_URL}/rest/v1/syntharra_vault?service_name=eq.${encodeURIComponent(serviceName)}&key_type=eq.${encodeURIComponent(keyType)}&select=key_value`;
  const resp = await fetch(url, {
    headers: {
      apikey: SUPABASE_SERVICE_ROLE_KEY,
      authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
    },
  });
  if (!resp.ok) return null;
  const rows = await resp.json();
  return Array.isArray(rows) && rows.length > 0 ? rows[0].key_value : null;
}

async function findPilot(agentId: string): Promise<Record<string, unknown> | null> {
  const url =
    `${SUPABASE_URL}/rest/v1/client_subscriptions?agent_id=eq.${encodeURIComponent(agentId)}&pilot_mode=eq.true&status=eq.pilot&select=id,agent_id,company_name,client_email,stripe_customer_id&limit=1`;
  const resp = await fetch(url, {
    headers: {
      apikey: SUPABASE_SERVICE_ROLE_KEY,
      authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
    },
  });
  if (!resp.ok) return null;
  const rows = await resp.json();
  return Array.isArray(rows) && rows.length > 0 ? rows[0] : null;
}

async function stripeCall(
  stripeKey: string,
  method: string,
  path: string,
  formBody?: Record<string, string>,
): Promise<Record<string, unknown>> {
  const url = `https://api.stripe.com${path}`;
  const init: RequestInit = {
    method,
    headers: {
      authorization: `Bearer ${stripeKey}`,
    },
  };
  if (formBody) {
    (init.headers as Record<string, string>)["content-type"] =
      "application/x-www-form-urlencoded";
    init.body = new URLSearchParams(formBody).toString();
  }
  const resp = await fetch(url, init);
  const data = await resp.json();
  if (!resp.ok) {
    throw new Error(`stripe ${method} ${path} -> ${resp.status} ${JSON.stringify(data).slice(0, 300)}`);
  }
  return data;
}

async function persistCustomerId(rowId: string, customerId: string): Promise<void> {
  const url = `${SUPABASE_URL}/rest/v1/client_subscriptions?id=eq.${encodeURIComponent(rowId)}`;
  await fetch(url, {
    method: "PATCH",
    headers: {
      apikey: SUPABASE_SERVICE_ROLE_KEY,
      authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
      "content-type": "application/json",
      prefer: "return=minimal",
    },
    body: JSON.stringify({ stripe_customer_id: customerId }),
  });
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: CORS_HEADERS });
  }
  if (req.method !== "POST") {
    return jsonResponse({ error: "method_not_allowed" }, 405);
  }

  let body: Record<string, unknown>;
  try {
    body = await req.json();
  } catch {
    return jsonResponse({ error: "invalid_json" }, 400);
  }

  const agentId = String(body.agent_id ?? "");
  if (!agentId) {
    return jsonResponse({ error: "missing_agent_id" }, 400);
  }

  const pilot = await findPilot(agentId);
  if (!pilot) {
    return jsonResponse({ error: "pilot_not_found" }, 404);
  }

  // Use test key by default. Switch to secret_key_live once Dan vaults it.
  const stripeKey =
    (await fetchVault("Stripe", "secret_key_live")) ??
    (await fetchVault("Stripe", "secret_key_test"));
  if (!stripeKey) {
    return jsonResponse({ error: "stripe_key_unavailable" }, 500);
  }

  let customerId = String(pilot.stripe_customer_id ?? "");
  if (!customerId) {
    const customer = await stripeCall(stripeKey, "POST", "/v1/customers", {
      email: String(pilot.client_email ?? ""),
      name: String(pilot.company_name ?? ""),
      "metadata[syntharra_agent_id]": agentId,
      "metadata[syntharra_source]": "phase0_pilot",
    });
    customerId = String(customer.id ?? "");
    if (customerId) {
      await persistCustomerId(String(pilot.id), customerId);
    }
  }

  const setupIntent = await stripeCall(stripeKey, "POST", "/v1/setup_intents", {
    customer: customerId,
    usage: "off_session",
    "payment_method_types[]": "card",
    "metadata[source]": "syntharra_pilot",
    "metadata[agent_id]": agentId,
  });

  return jsonResponse({
    client_secret: setupIntent.client_secret,
    customer_id: customerId,
    setup_intent_id: setupIntent.id,
  });
});
