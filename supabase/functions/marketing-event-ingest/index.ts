// marketing-event-ingest
// Phase 0 measurement spine ingestion endpoint. Receives marketing events from
// the browser-side tracker (`marketing-tracker.js`) on syntharra.com/start and
// other marketing surfaces. Applies a basic bot filter, then INSERTs into the
// `marketing_events` Supabase table for later analysis by Phase 3 Optimizer.
//
// Public endpoint: verify_jwt=false. The bot filter is the only access control.
// (No PII / no destructive actions accessible via this endpoint.)
//
// Spec: docs/superpowers/specs/2026-04-10-phase-0-vsl-funnel-design.md § 7.3

import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? "";
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";

const BOT_UA_PATTERNS = [
  /bot/i, /crawl/i, /spider/i, /scraper/i, /headless/i, /phantom/i, /selenium/i,
  /python-requests/i, /curl\//i, /wget/i, /go-http-client/i, /preview/i,
];

const ALLOWED_EVENT_TYPES = new Set([
  "page_view",
  "vsl_play_started",
  "vsl_play_completed",
  "vsl_25_pct",
  "vsl_50_pct",
  "vsl_75_pct",
  "vsl_100_pct",
  "form_view",
  "form_field_focus",
  "form_submit_attempt",
  "form_submit_success",
  "outbound_click",
  "scroll_depth",
  "session_start",
  "cta_click",
]);

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

function isBot(ua: string | null): boolean {
  if (!ua) return true;
  return BOT_UA_PATTERNS.some((re) => re.test(ua));
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: CORS_HEADERS });
  }
  if (req.method !== "POST") {
    return jsonResponse({ error: "method_not_allowed" }, 405);
  }
  if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
    return jsonResponse({ error: "server_misconfigured" }, 500);
  }

  const ua = req.headers.get("user-agent");
  if (isBot(ua)) {
    // Drop silently with 204 — not an error, just not stored
    return new Response(null, { status: 204, headers: CORS_HEADERS });
  }

  let payload: Record<string, unknown>;
  try {
    payload = await req.json();
  } catch {
    return jsonResponse({ error: "invalid_json" }, 400);
  }

  const eventType = String(payload.event_type ?? "");
  if (!ALLOWED_EVENT_TYPES.has(eventType)) {
    return jsonResponse({ error: "unknown_event_type", event_type: eventType }, 400);
  }

  // Schema (verified 2026-04-11 against live marketing_events table):
  //   session_id text NOT NULL, visitor_id, client_agent_id, event_type NOT NULL,
  //   asset_id, utm_*, referrer, user_agent, ip_country, ip_region, metadata jsonb,
  //   created_at (auto). The browser tracker keeps session_id in localStorage and
  //   sends it on every event so all events for one visit join cleanly.
  const props = (payload.props ?? {}) as Record<string, unknown>;
  const sessionId =
    String(payload.session_id ?? "") || `srv-${crypto.randomUUID()}`; // session_id is NOT NULL
  const visitorId = String(payload.visitor_id ?? "") || null;
  const clientAgentId = String(payload.client_agent_id ?? "") || null;
  const assetId =
    String(payload.asset_id ?? req.headers.get("x-synth-asset") ?? "") || null;
  const referrer = String(payload.referrer ?? "") || null;

  const row = {
    session_id: sessionId,
    visitor_id: visitorId,
    client_agent_id: clientAgentId,
    event_type: eventType,
    asset_id: assetId,
    utm_source:   String(payload.utm_source   ?? "") || null,
    utm_medium:   String(payload.utm_medium   ?? "") || null,
    utm_campaign: String(payload.utm_campaign ?? "") || null,
    utm_content:  String(payload.utm_content  ?? "") || null,
    utm_term:     String(payload.utm_term     ?? "") || null,
    referrer,
    user_agent: ua,
    metadata: props,
  };

  // INSERT via PostgREST. Use the service role key — this Edge Function is the
  // only thing writing to marketing_events.
  const insertResp = await fetch(`${SUPABASE_URL}/rest/v1/marketing_events`, {
    method: "POST",
    headers: {
      apikey: SUPABASE_SERVICE_ROLE_KEY,
      authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
      "content-type": "application/json",
      prefer: "return=minimal",
    },
    body: JSON.stringify(row),
  });

  if (!insertResp.ok) {
    const text = await insertResp.text();
    return jsonResponse(
      { error: "insert_failed", status: insertResp.status, detail: text.slice(0, 300) },
      500,
    );
  }

  return jsonResponse({ ok: true, event_type: eventType });
});
