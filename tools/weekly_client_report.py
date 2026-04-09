#!/usr/bin/env python3
"""Weekly Client Report — Syntharra branded.

Generates a weekly activity report for every client in the given timezone and
sends it via email (Brevo) + optional Slack (if the client set a webhook URL
during onboarding). Sunday 6pm local delivery.

Source of truth for call data: Retell `list-calls` API (not Supabase).
Client config: Supabase `hvac_standard_agent`.

Usage:
    python tools/weekly_client_report.py --tz America/New_York [--dry-run]

Cron setup (run once per TZ bucket, launched from Claude Code `CronCreate` or
any cron runner that supports tz-aware scheduling):

    # Sunday 18:00 local time, America/New_York clients
    0 18 * * 0  TZ=America/New_York  python tools/weekly_client_report.py --tz America/New_York

    # Replicate with other IANA zones as clients expand:
    #   America/Chicago, America/Denver, America/Los_Angeles,
    #   America/Phoenix (no DST), America/Anchorage, Pacific/Honolulu

Required env vars:
    SUPABASE_URL              # https://hgheyqwnrcvwtgngqdnq.supabase.co
    SUPABASE_SERVICE_KEY      # service_role JWT (syntharra_vault: Supabase/service_role_key)
    RETELL_API_KEY            # syntharra_vault: Retell/api_key
    BREVO_API_KEY             # syntharra_vault: Brevo/api_key

Dry-run: logs what would be sent without calling Brevo or Slack.
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone

# --------------- config ---------------
BRAND_FROM_NAME = "Syntharra"
BRAND_FROM_EMAIL = "reports@syntharra.com"
DASHBOARD_BASE = "https://syntharra.com/dashboard.html"
BRAND_LINK = "https://syntharra.com"


def env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        sys.exit(f"missing env var: {name}")
    return v


def http_json(method: str, url: str, headers: dict, body=None, timeout: int = 60):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, headers=headers, data=data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode("utf-8")[:500]}


# --------------- data fetchers ---------------
def fetch_clients(tz: str):
    """Return active clients in the given timezone."""
    sb = env("SUPABASE_URL")
    key = env("SUPABASE_SERVICE_KEY")
    url = (
        f"{sb}/rest/v1/hvac_standard_agent"
        "?select=agent_id,company_name,owner_name,client_email,"
        "notification_email_2,notification_email_3,slack_webhook_url,timezone"
        f"&timezone=eq.{urllib.parse.quote(tz)}"
        "&agent_status=eq.active"
    )
    status, data = http_json(
        "GET",
        url,
        {"apikey": key, "Authorization": f"Bearer {key}"},
    )
    if status != 200:
        sys.exit(f"supabase fetch failed: {status} {data}")
    return data


def fetch_calls(agent_id: str, since: datetime, until: datetime):
    """Pull all calls in window from Retell `list-calls`."""
    key = env("RETELL_API_KEY")
    body = {
        "filter_criteria": {
            "agent_id": [agent_id],
            "start_timestamp": {
                "lower_threshold": int(since.timestamp() * 1000),
                "upper_threshold": int(until.timestamp() * 1000),
            },
        },
        "limit": 500,
        "sort_order": "descending",
    }
    status, data = http_json(
        "POST",
        "https://api.retellai.com/v2/list-calls",
        {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        body,
    )
    if status != 200:
        return []
    return data if isinstance(data, list) else data.get("calls", [])


# --------------- aggregation ---------------
def aggregate(calls: list) -> dict:
    total = len(calls)
    leads = 0
    emergencies = 0
    spam = 0
    top_leads = []
    total_duration_s = 0

    for c in calls:
        dur_ms = c.get("duration_ms") or 0
        total_duration_s += int(dur_ms / 1000)
        analysis = c.get("call_analysis") or {}
        custom = analysis.get("custom_analysis_data") or {}
        if custom.get("is_lead"):
            leads += 1
            summary = analysis.get("call_summary") or ""
            top_leads.append(
                {
                    "caller": (c.get("collected_dynamic_variables") or {}).get(
                        "caller_name"
                    )
                    or c.get("from_number")
                    or "Unknown",
                    "phone": c.get("from_number") or "",
                    "urgency": (custom.get("urgency") or "normal").lower(),
                    "summary": summary[:220],
                    "at": c.get("start_timestamp"),
                }
            )
        if (custom.get("urgency") or "").lower() == "emergency":
            emergencies += 1
        if custom.get("is_spam"):
            spam += 1

    # Top 5 leads, emergency-first
    top_leads.sort(key=lambda l: (l["urgency"] != "emergency", -(l["at"] or 0)))
    return {
        "total": total,
        "leads": leads,
        "emergencies": emergencies,
        "spam": spam,
        "total_minutes": round(total_duration_s / 60),
        "top_leads": top_leads[:5],
    }


# --------------- email render ---------------
def render_email_html(client: dict, stats: dict, since: datetime, until: datetime) -> tuple:
    company = client["company_name"]
    owner_hi = (client.get("owner_name") or "").strip().split(" ")[0] or "there"
    dash_url = f"{DASHBOARD_BASE}?a={urllib.parse.quote(client['agent_id'])}"
    week_label = f"{since.strftime('%b %d')} – {until.strftime('%b %d, %Y')}"

    subject = f"Your Syntharra weekly report — {stats['leads']} lead{'s' if stats['leads'] != 1 else ''} this week"

    # Lead row HTML
    lead_rows = ""
    for l in stats["top_leads"]:
        urg = l["urgency"]
        badge_color = "#dc2626" if urg == "emergency" else "#ea580c" if urg == "high" else "#2563eb"
        badge_label = "EMERGENCY" if urg == "emergency" else urg.upper()
        lead_rows += (
            f'<tr><td style="padding:14px 0;border-bottom:1px solid #e2e8f0">'
            f'<div style="display:inline-block;background:{badge_color};color:#fff;font-size:10px;font-weight:600;letter-spacing:0.04em;padding:3px 8px;border-radius:4px;margin-bottom:4px">{badge_label}</div>'
            f'<div style="font-size:15px;font-weight:600;color:#0f172a">{l["caller"]}</div>'
            f'<div style="font-size:13px;color:#64748b;margin:2px 0 6px">{l["phone"]}</div>'
            f'<div style="font-size:13px;color:#334155;line-height:1.5">{l["summary"]}</div>'
            f"</td></tr>"
        )
    if not lead_rows:
        lead_rows = (
            '<tr><td style="padding:24px 0;text-align:center;color:#94a3b8;font-size:14px">'
            "No leads this week. Check the dashboard for all activity."
            "</td></tr>"
        )

    html = f"""<!DOCTYPE html>
<html><body style="margin:0;padding:0;background:#f8fafc;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#0f172a">
<div style="max-width:600px;margin:0 auto;background:#ffffff">
  <div style="background:#0f172a;padding:28px 32px">
    <div style="color:#ffffff;font-size:20px;font-weight:600;letter-spacing:-0.01em">Syntharra</div>
    <div style="color:#94a3b8;font-size:13px;margin-top:4px">Weekly report · {week_label}</div>
  </div>
  <div style="padding:32px">
    <div style="font-size:15px;color:#475569;margin-bottom:4px">Hi {owner_hi},</div>
    <h1 style="font-size:24px;margin:6px 0 24px;font-weight:600;letter-spacing:-0.02em">Your week at {company}</h1>

    <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;margin-bottom:32px">
      <tr>
        <td width="25%" style="text-align:center;padding:20px 10px;background:#f1f5f9;border-radius:8px 0 0 8px">
          <div style="font-size:28px;font-weight:700;color:#0f172a">{stats['total']}</div>
          <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.05em;color:#64748b;margin-top:4px">Calls</div>
        </td>
        <td width="25%" style="text-align:center;padding:20px 10px;background:#dbeafe">
          <div style="font-size:28px;font-weight:700;color:#1e40af">{stats['leads']}</div>
          <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.05em;color:#1e40af;margin-top:4px">Leads</div>
        </td>
        <td width="25%" style="text-align:center;padding:20px 10px;background:#fee2e2">
          <div style="font-size:28px;font-weight:700;color:#991b1b">{stats['emergencies']}</div>
          <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.05em;color:#991b1b;margin-top:4px">Emergency</div>
        </td>
        <td width="25%" style="text-align:center;padding:20px 10px;background:#f1f5f9;border-radius:0 8px 8px 0">
          <div style="font-size:28px;font-weight:700;color:#0f172a">{stats['total_minutes']}</div>
          <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.05em;color:#64748b;margin-top:4px">Minutes</div>
        </td>
      </tr>
    </table>

    <h2 style="font-size:13px;text-transform:uppercase;letter-spacing:0.06em;color:#64748b;font-weight:600;margin:0 0 8px">Top leads this week</h2>
    <table width="100%" cellpadding="0" cellspacing="0">{lead_rows}</table>

    <div style="margin-top:32px;padding:20px 0;border-top:1px solid #e2e8f0">
      <a href="{dash_url}" style="display:inline-block;background:#0f172a;color:#ffffff;text-decoration:none;padding:14px 28px;border-radius:8px;font-weight:600;font-size:15px">Open your dashboard</a>
    </div>
  </div>
  <div style="padding:20px 32px;border-top:1px solid #e2e8f0;color:#94a3b8;font-size:12px;text-align:center">
    Syntharra AI Receptionist · <a href="{BRAND_LINK}" style="color:#94a3b8;text-decoration:underline">syntharra.com</a><br>
    This report was generated automatically every Sunday at 6pm local time.
  </div>
</div></body></html>"""
    return subject, html


def render_slack_blocks(client: dict, stats: dict, since: datetime, until: datetime) -> dict:
    company = client["company_name"]
    dash_url = f"{DASHBOARD_BASE}?a={urllib.parse.quote(client['agent_id'])}"
    week_label = f"{since.strftime('%b %d')} – {until.strftime('%b %d')}"
    return {
        "text": f"Syntharra weekly report for {company}: {stats['leads']} leads, {stats['total']} calls",
        "blocks": [
            {"type": "header", "text": {"type": "plain_text", "text": f"📊  Weekly report — {company}", "emoji": True}},
            {"type": "context", "elements": [{"type": "mrkdwn", "text": f"Syntharra AI Receptionist  ·  {week_label}"}]},
            {"type": "divider"},
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Calls*\n{stats['total']}"},
                    {"type": "mrkdwn", "text": f"*Leads*\n{stats['leads']}"},
                    {"type": "mrkdwn", "text": f"*Emergencies*\n{stats['emergencies']}"},
                    {"type": "mrkdwn", "text": f"*Total minutes*\n{stats['total_minutes']}"},
                ],
            },
            *(
                [
                    {"type": "divider"},
                    {"type": "section", "text": {"type": "mrkdwn", "text": "*Top leads*"}},
                    *[
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*{'🔥 ' if l['urgency'] == 'emergency' else ''}{l['caller']}*  ·  {l['phone']}\n{l['summary']}",
                            },
                        }
                        for l in stats["top_leads"]
                    ],
                ]
                if stats["top_leads"]
                else []
            ),
            {
                "type": "actions",
                "elements": [
                    {"type": "button", "text": {"type": "plain_text", "text": "Open dashboard"}, "url": dash_url, "style": "primary"}
                ],
            },
        ],
    }


# --------------- senders ---------------
def send_email(recipients: list, subject: str, html: str, dry_run: bool) -> tuple:
    if dry_run:
        return 200, {"dry_run": True, "to": recipients}
    if not recipients:
        return 204, {"skipped": "no recipients"}
    body = {
        "sender": {"name": BRAND_FROM_NAME, "email": BRAND_FROM_EMAIL},
        "to": [{"email": e} for e in recipients],
        "subject": subject,
        "htmlContent": html,
    }
    return http_json(
        "POST",
        "https://api.brevo.com/v3/smtp/email",
        {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": env("BREVO_API_KEY"),
        },
        body,
    )


def send_slack(webhook_url: str, payload: dict, dry_run: bool) -> tuple:
    if dry_run:
        return 200, {"dry_run": True, "url": webhook_url[:40] + "…"}
    return http_json("POST", webhook_url, {"Content-Type": "application/json"}, payload)


# --------------- main ---------------
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--tz", required=True, help="IANA timezone, e.g. America/New_York")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    until = datetime.now(timezone.utc)
    since = until - timedelta(days=7)

    clients = fetch_clients(args.tz)
    print(f"[{args.tz}] {len(clients)} active client(s)")

    for client in clients:
        company = client["company_name"]
        calls = fetch_calls(client["agent_id"], since, until)
        stats = aggregate(calls)
        emails = [
            e
            for e in [
                client.get("client_email"),
                client.get("notification_email_2"),
                client.get("notification_email_3"),
            ]
            if e and e.strip()
        ]
        emails = list(dict.fromkeys(emails))  # dedupe preserve order

        subject, html = render_email_html(client, stats, since, until)
        es, _ = send_email(emails, subject, html, args.dry_run)

        slack_url = client.get("slack_webhook_url")
        if slack_url:
            payload = render_slack_blocks(client, stats, since, until)
            ss, _ = send_slack(slack_url, payload, args.dry_run)
        else:
            ss = None

        print(
            f"  {company}: calls={stats['total']} leads={stats['leads']} "
            f"emergencies={stats['emergencies']} | email={es} slack={ss or '-'}"
        )


if __name__ == "__main__":
    import urllib.parse  # used by render_email_html

    main()
