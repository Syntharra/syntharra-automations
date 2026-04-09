#!/usr/bin/env python3
"""Generate browser-viewable HTML preview files for all Syntharra email templates.

Run:
    python tools/preview_emails.py

Opens 5 preview files in your default browser. Files are written to docs/email-previews/.
"""
import os
import sys
import webbrowser
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from shared.email_template import syntharra_email_shell

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "email-previews")
os.makedirs(OUT_DIR, exist_ok=True)


# ── 1. Lead notification ────────────────────────────────────────────────────
def preview_lead():
    urgency_color = "#DC2626"
    urgency_badge = "EMERGENCY"
    caller_name   = "James Tanner"
    caller_phone  = "+1 (615) 882-4401"
    duration      = 47
    summary       = (
        "Customer called about a complete AC failure. Unit is not turning on at all and "
        "the house is 88°F. Has elderly parents at home. Needs emergency same-day service. "
        "Interested in a service agreement if the repair goes well."
    )
    dashboard_url = "https://syntharra.com/dashboard.html?a=agent_example"
    callback_href = "tel:+16158824401"
    company       = "Acme HVAC Services"

    body = (
        f'<div style="margin-bottom:20px"><span style="display:inline-block;background:{urgency_color};color:#ffffff;padding:5px 12px;border-radius:999px;font-size:11px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase">{urgency_badge}</span></div>'
        f'<h1 style="font-size:22px;font-weight:700;color:#0D0D1A;margin:0 0 6px;letter-spacing:-0.02em">{caller_name}</h1>'
        f'<div style="font-size:14px;color:#6B7280;margin-bottom:24px">{caller_phone} &middot; {duration}s call</div>'
        f'<a href="{callback_href}" style="display:inline-block;background:{urgency_color};color:#ffffff;text-decoration:none;padding:13px 24px;border-radius:10px;font-weight:600;font-size:15px">Call back now</a>'
        f'<div style="margin-top:24px;padding:16px 18px;background:#F0EEFF;border-radius:10px;border-left:3px solid #6C63FF">'
        f'<div style="font-size:11px;text-transform:uppercase;letter-spacing:0.06em;color:#6B7280;font-weight:600;margin-bottom:8px">Summary</div>'
        f'<div style="font-size:14px;line-height:1.6;color:#1A1A2E">{summary}</div>'
        f'</div>'
        f'<div style="margin-top:20px"><a href="{dashboard_url}" style="color:#6C63FF;text-decoration:none;font-size:14px;font-weight:500">View transcript in your dashboard &rarr;</a></div>'
    )
    return syntharra_email_shell(
        header_context=f"Lead notification for {company}",
        body_html=body,
    )


# ── 2. Weekly report ────────────────────────────────────────────────────────
def preview_weekly():
    company    = "Acme HVAC Services"
    owner_hi   = "Mike"
    week_label = "Apr 1 – Apr 7, 2026"
    dash_url   = "https://syntharra.com/dashboard.html?a=agent_example"

    stats = {"total": 38, "leads": 7, "emergencies": 2, "total_minutes": 94}
    leads = [
        {"urgency": "emergency", "caller": "James Tanner",    "phone": "+1 (615) 882-4401", "summary": "AC failure, 88°F indoors, elderly parents at home. Needs emergency same-day service."},
        {"urgency": "high",      "caller": "Sarah Kellerman", "phone": "+1 (629) 551-7832", "summary": "Furnace stopped working overnight. Two kids under 5. Asking for next available slot."},
        {"urgency": "normal",    "caller": "Dave Okonkwo",    "phone": "+1 (615) 304-9921", "summary": "Interested in annual maintenance plan. Existing customer, wants to renew."},
    ]

    lead_rows = ""
    for l in leads:
        urg = l["urgency"]
        badge_color = "#DC2626" if urg == "emergency" else "#EA580C" if urg == "high" else "#6C63FF"
        badge_label = urg.upper()
        lead_rows += (
            f'<div style="padding:14px 0;border-bottom:1px solid #E8E6FF">'
            f'<span style="display:inline-block;background:{badge_color};color:#fff;font-size:10px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase;padding:3px 9px;border-radius:999px;margin-bottom:6px">{badge_label}</span>'
            f'<div style="font-size:15px;font-weight:600;color:#0D0D1A;margin-top:2px">{l["caller"]}</div>'
            f'<div style="font-size:13px;color:#6B7280;margin:2px 0 6px">{l["phone"]}</div>'
            f'<div style="font-size:13px;color:#1A1A2E;line-height:1.55">{l["summary"]}</div>'
            f'</div>'
        )

    stats_grid = (
        '<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;margin-bottom:28px"><tr>'
        f'<td width="25%" style="padding:3px 3px 3px 0"><div style="background:#F8F7FF;border:1px solid #E8E6FF;border-radius:10px;padding:18px 8px;text-align:center"><div style="font-size:28px;font-weight:700;color:#0D0D1A">{stats["total"]}</div><div style="font-size:10px;text-transform:uppercase;letter-spacing:0.06em;color:#6B7280;font-weight:600;margin-top:5px">Calls</div></div></td>'
        f'<td width="25%" style="padding:3px"><div style="background:#EEF2FF;border:1px solid #C7D2FE;border-radius:10px;padding:18px 8px;text-align:center"><div style="font-size:28px;font-weight:700;color:#4338CA">{stats["leads"]}</div><div style="font-size:10px;text-transform:uppercase;letter-spacing:0.06em;color:#4338CA;font-weight:600;margin-top:5px">Leads</div></div></td>'
        f'<td width="25%" style="padding:3px"><div style="background:#FFF1F2;border:1px solid #FECDD3;border-radius:10px;padding:18px 8px;text-align:center"><div style="font-size:28px;font-weight:700;color:#BE123C">{stats["emergencies"]}</div><div style="font-size:10px;text-transform:uppercase;letter-spacing:0.06em;color:#BE123C;font-weight:600;margin-top:5px">Emergency</div></div></td>'
        f'<td width="25%" style="padding:3px 0 3px 3px"><div style="background:#F8F7FF;border:1px solid #E8E6FF;border-radius:10px;padding:18px 8px;text-align:center"><div style="font-size:28px;font-weight:700;color:#0D0D1A">{stats["total_minutes"]}</div><div style="font-size:10px;text-transform:uppercase;letter-spacing:0.06em;color:#6B7280;font-weight:600;margin-top:5px">Minutes</div></div></td>'
        '</tr></table>'
    )

    body = (
        f'<div style="font-size:14px;color:#6B7280;margin-bottom:4px">Hi {owner_hi},</div>'
        f'<h1 style="font-size:22px;font-weight:700;color:#0D0D1A;margin:6px 0 24px;letter-spacing:-0.02em">Your week at {company}</h1>'
        + stats_grid
        + '<div style="font-size:11px;text-transform:uppercase;letter-spacing:0.06em;color:#6B7280;font-weight:600;margin-bottom:14px">Top leads this week</div>'
        + lead_rows
        + f'<div style="margin-top:28px;padding-top:24px;border-top:1px solid #E8E6FF"><a href="{dash_url}" style="display:inline-block;background:#6C63FF;color:#ffffff;text-decoration:none;padding:14px 28px;border-radius:10px;font-weight:600;font-size:15px">Open your dashboard</a></div>'
    )
    return syntharra_email_shell(
        header_context=f"Weekly report &nbsp;&middot;&nbsp; {week_label}",
        body_html=body,
        footer_note="Generated every Sunday at 6 pm local time.",
    )


# ── 3. Monthly usage (no overage) ───────────────────────────────────────────
def preview_monthly_no_overage():
    billing_month    = "2026-03"
    call_count       = 124
    total_minutes    = 318
    included_minutes = 500
    usage_pct        = round(total_minutes / included_minutes * 100)
    bar_width        = min(usage_pct, 100)
    bar_color        = "#6C63FF"

    overage_block = (
        '<div style="padding:16px 20px;background:#ECFDF5;border-radius:10px;border:1px solid #A7F3D0;margin-bottom:0">'
        '<div style="font-size:14px;font-weight:600;color:#065F46;margin-bottom:4px">No overage this month</div>'
        '<div style="font-size:13px;color:#047857">You stayed within your included minutes.</div>'
        '</div>'
    )

    body = (
        '<div style="font-size:14px;color:#6B7280;margin-bottom:4px">Hi Acme HVAC Services,</div>'
        '<h1 style="font-size:22px;font-weight:700;color:#0D0D1A;margin:6px 0 6px;letter-spacing:-0.02em">Monthly Usage Report</h1>'
        f'<div style="font-size:14px;color:#6B7280;margin-bottom:24px">{billing_month}</div>'
        '<div style="padding:20px 24px;background:#F8F7FF;border-radius:12px;border:1px solid #E8E6FF;margin-bottom:20px">'
        '<table width="100%" cellpadding="0" cellspacing="0">'
        f'<tr><td style="padding:10px 0;border-bottom:1px solid #E8E6FF;font-size:14px;color:#6B7280">Total calls</td><td style="padding:10px 0;border-bottom:1px solid #E8E6FF;text-align:right;font-size:14px;font-weight:600;color:#0D0D1A">{call_count}</td></tr>'
        f'<tr><td style="padding:10px 0;border-bottom:1px solid #E8E6FF;font-size:14px;color:#6B7280">Total minutes</td><td style="padding:10px 0;border-bottom:1px solid #E8E6FF;text-align:right;font-size:14px;font-weight:600;color:#0D0D1A">{total_minutes}</td></tr>'
        f'<tr><td style="padding:10px 0;border-bottom:1px solid #E8E6FF;font-size:14px;color:#6B7280">Included minutes</td><td style="padding:10px 0;border-bottom:1px solid #E8E6FF;text-align:right;font-size:14px;color:#0D0D1A">{included_minutes}</td></tr>'
        f'<tr><td style="padding:12px 0 0;font-size:14px;color:#6B7280">Usage</td><td style="padding:12px 0 0;text-align:right;font-size:20px;font-weight:700;color:#6C63FF">{usage_pct}%</td></tr>'
        '</table>'
        f'<div style="margin-top:16px;height:8px;background:#E8E6FF;border-radius:4px;overflow:hidden"><div style="height:8px;width:{bar_width}%;background:{bar_color};border-radius:4px"></div></div>'
        f'<div style="font-size:11px;color:#6B7280;margin-top:6px;text-align:right">{total_minutes} / {included_minutes} min</div>'
        '</div>'
        + overage_block
    )
    return syntharra_email_shell(
        header_context=f"Monthly usage report &nbsp;&middot;&nbsp; {billing_month}",
        body_html=body,
    )


# ── 4. Usage alert — 80% ────────────────────────────────────────────────────
def preview_usage_alert_80():
    total_minutes    = 412
    included_minutes = 500
    usage_pct        = round(total_minutes / included_minutes * 100)
    bar_color        = "#D97706"

    body_extra = (
        "You still have time left in the month, but we wanted to give you a heads-up "
        "so there are no surprises at billing time. If you go over your included minutes, "
        "overage is charged per minute at your plan rate.<br><br>"
        "No action needed — your AI receptionist keeps running. This is just a friendly alert."
    )

    body = (
        '<span style="display:inline-block;background:#D97706;color:#fff;padding:5px 12px;border-radius:999px;font-size:11px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:20px">Usage Alert</span>'
        '<h1 style="font-size:22px;font-weight:700;color:#0D0D1A;margin:0 0 6px;letter-spacing:-0.02em">You\'re at 80% of your included minutes</h1>'
        '<div style="font-size:14px;color:#6B7280;margin-bottom:24px">Hi Acme HVAC Services — here\'s your current usage.</div>'
        f'<div style="margin-bottom:24px"><div style="height:8px;background:#E8E6FF;border-radius:4px;overflow:hidden"><div style="height:8px;width:{usage_pct}%;background:{bar_color};border-radius:4px"></div></div><div style="font-size:11px;color:#6B7280;margin-top:6px;text-align:right">{total_minutes} / {included_minutes} min used</div></div>'
        '<div style="padding:20px 24px;background:#F8F7FF;border-radius:12px;border:1px solid #E8E6FF;margin-bottom:24px">'
        '<table width="100%" cellpadding="0" cellspacing="0">'
        f'<tr><td style="padding:8px 0;border-bottom:1px solid #E8E6FF;font-size:14px;color:#6B7280">Minutes used so far</td><td style="padding:8px 0;border-bottom:1px solid #E8E6FF;text-align:right;font-size:14px;font-weight:700;color:#0D0D1A">{total_minutes}</td></tr>'
        f'<tr><td style="padding:8px 0;border-bottom:1px solid #E8E6FF;font-size:14px;color:#6B7280">Included minutes</td><td style="padding:8px 0;border-bottom:1px solid #E8E6FF;text-align:right;font-size:14px;color:#0D0D1A">{included_minutes}</td></tr>'
        f'<tr><td style="padding:10px 0 0;font-size:14px;color:#6B7280">Usage</td><td style="padding:10px 0 0;text-align:right;font-size:20px;font-weight:700;color:{bar_color}">{usage_pct}%</td></tr>'
        '</table></div>'
        f'<div style="font-size:14px;color:#1A1A2E;line-height:1.7">{body_extra}</div>'
        '<div style="margin-top:20px;font-size:13px;color:#6B7280">Questions? Email us at <a href="mailto:support@syntharra.com" style="color:#6C63FF;text-decoration:none;font-weight:500">support@syntharra.com</a></div>'
    )
    return syntharra_email_shell(
        header_context="Usage alert &nbsp;&middot;&nbsp; 80% of included minutes",
        body_html=body,
    )


# ── 5. You're Live ──────────────────────────────────────────────────────────
def preview_youre_live():
    company     = "Acme HVAC Services"
    agent_name  = "Live — Acme HVAC Services"
    display_num = "+1 (812) 994-4371"
    QR_IPHONE   = "https://api.qrserver.com/v1/create-qr-code/?size=120x120&color=6C63FF&bgcolor=F0EEFF&data=App-Prefs%3Aroot%3DPhone%26path%3DCALL_FORWARDING"
    QR_ANDROID  = "https://api.qrserver.com/v1/create-qr-code/?size=120x120&color=6C63FF&bgcolor=F0EEFF&data=tel%3A**21*18129944371%23"

    body = (
        '<div style="margin-bottom:20px"><span style="display:inline-block;background:#6C63FF;color:#ffffff;padding:5px 14px;border-radius:999px;font-size:11px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase">You\'re Live</span></div>'
        f'<h1 style="font-size:22px;font-weight:700;color:#0D0D1A;margin:0 0 8px;letter-spacing:-0.02em">Your AI Receptionist is answering calls</h1>'
        f'<p style="font-size:14px;color:#6B7280;line-height:1.7;margin:0 0 24px">{agent_name} is configured and ready to answer calls 24/7 for {company}. Forward your business number to activate it.</p>'
        f'<div style="padding:16px 20px;background:#ECFDF5;border-radius:10px;border:1px solid #A7F3D0;margin-bottom:20px"><div style="font-size:13px;color:#047857;margin-bottom:4px"><strong style="color:#065F46">Agent:</strong> {agent_name}</div><div style="font-size:13px;color:#047857"><strong style="color:#065F46">Status:</strong> &#x2705; Active &mdash; answering calls 24/7</div></div>'
        f'<div style="padding:22px;background:#F0EEFF;border-radius:12px;border:1px solid #D0CAFF;text-align:center;margin-bottom:28px"><div style="font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:#6C63FF;margin-bottom:8px">Your AI Receptionist Number</div><div style="font-size:28px;font-weight:700;color:#0D0D1A;letter-spacing:0.5px">{display_num}</div><div style="font-size:12px;color:#6B7280;margin-top:8px">Forward your existing business number to this number</div></div>'
        '<h2 style="font-size:17px;font-weight:700;color:#0D0D1A;margin:0 0 4px">Quick Setup &mdash; Scan to Activate</h2>'
        '<p style="font-size:13px;color:#6B7280;line-height:1.6;margin:0 0 18px">Open your phone camera and scan the QR code for your device type.</p>'
        '<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:10px"><tr>'
        f'<td width="48%" style="background:#F8F7FF;border:1px solid #E8E6FF;border-radius:12px;padding:20px;text-align:center;vertical-align:top"><div style="font-size:13px;font-weight:700;color:#0D0D1A;margin-bottom:12px">&#x1F4F1; iPhone</div><img src="{QR_IPHONE}" width="120" height="120" style="display:block;margin:0 auto 12px;border-radius:8px" alt="iPhone QR"><p style="font-size:11px;color:#6B7280;line-height:1.5;margin:0">Opens Call Forwarding settings directly</p></td>'
        '<td width="4%"></td>'
        f'<td width="48%" style="background:#F8F7FF;border:1px solid #E8E6FF;border-radius:12px;padding:20px;text-align:center;vertical-align:top"><div style="font-size:13px;font-weight:700;color:#0D0D1A;margin-bottom:12px">&#x1F4F1; Android</div><img src="{QR_ANDROID}" width="120" height="120" style="display:block;margin:0 auto 12px;border-radius:8px" alt="Android QR"><p style="font-size:11px;color:#6B7280;line-height:1.5;margin:0">Dials the forwarding code automatically</p></td>'
        '</tr></table>'
        '<div style="padding:18px 20px;background:#F0EEFF;border-radius:10px;border:1px solid #D0CAFF;margin-bottom:20px"><div style="font-size:14px;font-weight:700;color:#0D0D1A;margin-bottom:10px">Once forwarding is active</div><div style="font-size:13px;color:#4A4A6A;line-height:1.6;margin-bottom:4px">&#x2022; Every call answered instantly by your AI receptionist</div><div style="font-size:13px;color:#4A4A6A;line-height:1.6;margin-bottom:4px">&#x2022; Lead alerts emailed to you within 30 seconds</div><div style="font-size:13px;color:#4A4A6A;line-height:1.6">&#x2022; Weekly activity report every Sunday at 6 pm</div></div>'
        '<div style="padding:18px 20px;background:#6C63FF;border-radius:10px;margin-bottom:20px"><div style="font-size:14px;font-weight:700;color:#ffffff;margin-bottom:6px">&#x1F4CE; Full Setup Guide Attached</div><div style="font-size:13px;color:rgba(255,255,255,0.88);line-height:1.6">We\'ve attached a PDF with step-by-step instructions for every carrier, VoIP provider, and business phone system.</div></div>'
        '<div style="margin-top:28px;padding-top:24px;border-top:1px solid #E8E6FF"><a href="https://syntharra.com/dashboard.html?a=agent_example" style="display:inline-block;background:#6C63FF;color:#ffffff;text-decoration:none;padding:14px 28px;border-radius:10px;font-weight:600;font-size:15px">Open your dashboard</a></div>'
        '<p style="font-size:13px;color:#6B7280;line-height:1.6;margin:16px 0 0">Need help? Email us at <a href="mailto:support@syntharra.com" style="color:#6C63FF;font-weight:600;text-decoration:none">support@syntharra.com</a></p>'
    )
    return syntharra_email_shell(
        header_context="Your AI Receptionist is live",
        body_html=body,
    )


# ── Write + open ────────────────────────────────────────────────────────────
PREVIEWS = [
    ("1-lead-notification.html",  "Lead Notification",   preview_lead),
    ("2-weekly-report.html",      "Weekly Report",       preview_weekly),
    ("3-monthly-usage.html",      "Monthly Usage",       preview_monthly_no_overage),
    ("4-usage-alert-80pct.html",  "Usage Alert (80%)",   preview_usage_alert_80),
    ("5-youre-live.html",         "You're Live",         preview_youre_live),
]

for filename, label, fn in PREVIEWS:
    path = os.path.join(OUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(fn())
    print(f"  OK {label:25s}  ->  docs/email-previews/{filename}")
    webbrowser.open(f"file:///{path.replace(os.sep, '/')}")

print(f"\nAll previews opened in your browser.")
print(f"Files saved to: docs/email-previews/")
