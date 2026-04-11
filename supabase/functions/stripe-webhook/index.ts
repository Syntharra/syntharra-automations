// stripe-webhook
// Phase 0 Stripe webhook handler. Receives events from Stripe and reconciles
// them with client_subscriptions. Currently handles:
//   - setup_intent.succeeded → set payment_method_added_at, send pilot-card-added
//   - customer.subscription.created → no-op (logged)
//   - customer.subscription.updated → no-op (logged)
//
// Public endpoint: verify_jwt=false. Authentication is via Stripe webhook
// signature (HMAC-SHA256 of `t.{timestamp}.{payload}` against the webhook
// secret). The signing secret lives in syntharra_vault as service_name=Stripe,
// key_type='webhook_signing_secret'. If absent, signature verification is
// SKIPPED with a warning — this is INSECURE and only acceptable in dark-launch
// (no real Stripe events arriving yet). Add the secret as soon as the webhook
// is registered in the Stripe dashboard.
//
// Spec: docs/superpowers/specs/2026-04-10-phase-0-vsl-funnel-design.md § 6.4
// + Day 3 Task 21

import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? "";
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";

const CORS_HEADERS: Record<string, string> = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "content-type, stripe-signature",
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

async function verifyStripeSignature(
  rawPayload: string,
  signatureHeader: string | null,
  secret: string,
): Promise<boolean> {
  if (!signatureHeader) return false;
  // Stripe-Signature: t=1234567890,v1=hexhmac,...
  const parts = Object.fromEntries(
    signatureHeader.split(",").map((p) => {
      const [k, v] = p.split("=", 2);
      return [k.trim(), (v ?? "").trim()];
    }),
  );
  const t = parts["t"];
  const v1 = parts["v1"];
  if (!t || !v1) return false;

  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    enc.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const msg = enc.encode(`${t}.${rawPayload}`);
  const sig = await crypto.subtle.sign("HMAC", key, msg);
  const expected = Array.from(new Uint8Array(sig))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");

  // Constant-time-ish compare (length check then char-by-char)
  if (expected.length !== v1.length) return false;
  let mismatch = 0;
  for (let i = 0; i < expected.length; i++) {
    mismatch |= expected.charCodeAt(i) ^ v1.charCodeAt(i);
  }
  return mismatch === 0;
}

async function findPilotByCustomer(customerId: string): Promise<Record<string, unknown> | null> {
  const url =
    `${SUPABASE_URL}/rest/v1/client_subscriptions?stripe_customer_id=eq.${encodeURIComponent(customerId)}&select=id,agent_id,client_email,company_name,pilot_mode,status&limit=1`;
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

async function markCardAdded(rowId: string): Promise<void> {
  await fetch(
    `${SUPABASE_URL}/rest/v1/client_subscriptions?id=eq.${encodeURIComponent(rowId)}`,
    {
      method: "PATCH",
      headers: {
        apikey: SUPABASE_SERVICE_ROLE_KEY,
        authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
        "content-type": "application/json",
        prefer: "return=minimal",
      },
      body: JSON.stringify({ payment_method_added_at: new Date().toISOString() }),
    },
  );
}

async function emitMarketingEvent(
  eventType: string,
  agentId: string,
  props: Record<string, unknown>,
): Promise<void> {
  // Schema match against live marketing_events: session_id NOT NULL, jsonb metadata.
  await fetch(`${SUPABASE_URL}/rest/v1/marketing_events`, {
    method: "POST",
    headers: {
      apikey: SUPABASE_SERVICE_ROLE_KEY,
      authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
      "content-type": "application/json",
      prefer: "return=minimal",
    },
    body: JSON.stringify({
      session_id: `webhook-${agentId}`,
      visitor_id: null,
      client_agent_id: agentId,
      event_type: eventType,
      asset_id: null,
      user_agent: "stripe-webhook",
      metadata: { agent_id: agentId, ...props },
    }),
  });
}

async function sendCardAddedEmail(email: string, companyName: string): Promise<void> {
  const brevoKey = await fetchVault("Brevo", "api_key");
  if (!brevoKey) return;
  await fetch("https://api.brevo.com/v3/smtp/email", {
    method: "POST",
    headers: {
      "api-key": brevoKey,
      "content-type": "application/json",
      accept: "application/json",
    },
    body: JSON.stringify({
      sender: { name: "Syntharra", email: "daniel@syntharra.com" },
      to: [{ email, name: companyName }],
      templateId: 1, // pilot-card-added (uploaded 2026-04-11)
      params: {
        first_name: "there",
        company_name: companyName,
      },
    }),
  });
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: CORS_HEADERS });
  }
  if (req.method !== "POST") {
    return jsonResponse({ error: "method_not_allowed" }, 405);
  }

  const rawPayload = await req.text();
  const signatureHeader = req.headers.get("stripe-signature");

  // Webhook secret is optional in dark-launch mode. If present, enforce. If
  // absent, log a warning and proceed (events from a malicious source can
  // poison rows — only acceptable until the webhook is registered in Stripe).
  const webhookSecret = await fetchVault("Stripe", "webhook_signing_secret");
  if (webhookSecret) {
    const ok = await verifyStripeSignature(rawPayload, signatureHeader, webhookSecret);
    if (!ok) {
      return jsonResponse({ error: "signature_verification_failed" }, 400);
    }
  } else {
    console.warn(
      "[stripe-webhook] webhook_signing_secret not in vault — signature verification SKIPPED (dark-launch only)",
    );
  }

  let event: Record<string, unknown>;
  try {
    event = JSON.parse(rawPayload);
  } catch {
    return jsonResponse({ error: "invalid_json" }, 400);
  }

  const eventType = String(event.type ?? "");
  const data = (event.data as Record<string, unknown>) ?? {};
  const obj = (data.object as Record<string, unknown>) ?? {};

  if (eventType === "setup_intent.succeeded") {
    const customerId = String(obj.customer ?? "");
    if (!customerId) {
      return jsonResponse({ ok: true, action: "ignored_no_customer" });
    }
    const pilot = await findPilotByCustomer(customerId);
    if (!pilot) {
      return jsonResponse({ ok: true, action: "no_matching_pilot" });
    }
    await markCardAdded(String(pilot.id));
    await emitMarketingEvent("pilot_card_added", String(pilot.agent_id), {
      stripe_customer_id: customerId,
      stripe_setup_intent_id: String(obj.id ?? ""),
    });
    if (pilot.client_email) {
      await sendCardAddedEmail(
        String(pilot.client_email),
        String(pilot.company_name ?? ""),
      );
    }
    return jsonResponse({ ok: true, action: "card_added", agent_id: pilot.agent_id });
  }

  // Other event types — log + 200 OK so Stripe doesn't retry
  console.log(`[stripe-webhook] received ${eventType} (no handler)`);
  return jsonResponse({ ok: true, action: "ignored", type: eventType });
});
