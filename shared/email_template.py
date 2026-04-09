"""
shared/email_template.py — Syntharra transactional email shell.

All outbound client emails must use this shell so every touchpoint looks
identical. Design system mirrors https://n8n.syntharra.com/form/client-update.

Usage:
    from shared.email_template import syntharra_email_shell

    html = syntharra_email_shell(
        header_context="Lead notification for Acme HVAC",
        body_html="<p>...</p>",
    )

    # Or with a custom footer note:
    html = syntharra_email_shell(
        header_context="Weekly report · Apr 1 – Apr 7, 2026",
        body_html="...",
        footer_note="Generated every Sunday at 6 pm local time.",
    )

Design tokens (match client-update form exactly):
    Background:    #F2F1FF
    Card border:   1px solid #E8E6FF
    Card radius:   18px
    Accent bar:    4px linear-gradient(90deg, #6C63FF, #8B7FFF, #A78BFA)
    Primary:       #6C63FF
    Text primary:  #0D0D1A
    Text muted:    #6B7280
    Font:          -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif
    CTA button:    background #6C63FF, border-radius 10px, padding 14px 28px, weight 600
"""


# Reusable inline elements — import these when building body_html
BADGE_STYLES = {
    "purple":    "display:inline-block;background:#6C63FF;color:#fff;padding:5px 12px;border-radius:999px;font-size:11px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase",
    "emergency": "display:inline-block;background:#DC2626;color:#fff;padding:5px 12px;border-radius:999px;font-size:11px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase",
    "high":      "display:inline-block;background:#EA580C;color:#fff;padding:5px 12px;border-radius:999px;font-size:11px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase",
    "warning":   "display:inline-block;background:#D97706;color:#fff;padding:5px 12px;border-radius:999px;font-size:11px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase",
}

CTA_BUTTON = (
    "display:inline-block;background:#6C63FF;color:#ffffff;text-decoration:none;"
    "padding:14px 28px;border-radius:10px;font-weight:600;font-size:15px;letter-spacing:-0.01em"
)

STAT_BOX = (
    "background:#F8F7FF;border:1px solid #E8E6FF;border-radius:10px;"
    "padding:18px 10px;text-align:center"
)

INFO_BOX = (
    "padding:18px 20px;background:#F8F7FF;border-radius:12px;border:1px solid #E8E6FF"
)

SUCCESS_BOX = (
    "padding:16px 20px;background:#ECFDF5;border-radius:10px;border:1px solid #A7F3D0"
)

ERROR_BOX = (
    "padding:16px 20px;background:#FEF2F2;border-radius:10px;border:1px solid #FECACA"
)

HIGHLIGHT_BOX = (
    "padding:16px 18px;background:#F0EEFF;border-radius:10px;border-left:3px solid #6C63FF"
)


_LOGO_BARS = (
    '<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse">'
    "<tr>"
    '<td style="vertical-align:bottom;padding-right:3px"><div style="width:5px;height:13px;background:#6C63FF;font-size:1px;line-height:1px">&nbsp;</div></td>'
    '<td style="vertical-align:bottom;padding-right:3px"><div style="width:5px;height:19px;background:#6C63FF;font-size:1px;line-height:1px">&nbsp;</div></td>'
    '<td style="vertical-align:bottom;padding-right:3px"><div style="width:5px;height:26px;background:#6C63FF;font-size:1px;line-height:1px">&nbsp;</div></td>'
    '<td style="vertical-align:bottom"><div style="width:5px;height:33px;background:#6C63FF;font-size:1px;line-height:1px">&nbsp;</div></td>'
    "</tr>"
    "</table>"
)


def syntharra_email_shell(
    header_context: str,
    body_html: str,
    footer_note: str = "",
) -> str:
    """Return a complete HTML email document using the Syntharra design system.

    Args:
        header_context: Short descriptor shown below the wordmark in the header.
                        E.g. "Lead notification for Acme HVAC" or
                             "Weekly report · Apr 1 – Apr 7, 2026"
        body_html:      The email-specific content (inside the card body).
        footer_note:    Optional second line in the footer (e.g. cadence note).
    """
    footer_extra = (
        f'<br><span style="color:#9CA3AF">{footer_note}</span>'
        if footer_note else ""
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background:#F2F1FF;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;color:#0D0D1A">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#F2F1FF;padding:40px 20px">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;background:#ffffff;border-radius:18px;overflow:hidden;border:1px solid #E8E6FF;box-shadow:0 8px 40px rgba(108,99,255,.10),0 1px 3px rgba(0,0,0,.04)">

<!-- Accent bar -->
<tr><td style="height:4px;background:linear-gradient(90deg,#6C63FF,#8B7FFF,#A78BFA);font-size:0;line-height:0">&nbsp;</td></tr>

<!-- Header -->
<tr><td style="padding:24px 40px;border-bottom:1px solid #E8E6FF;background:#ffffff">
<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>
<td style="padding-right:11px;vertical-align:middle">{_LOGO_BARS}</td>
<td style="vertical-align:middle">
<div style="font-size:16px;font-weight:700;color:#0D0D1A;letter-spacing:-0.02em;line-height:1">Syntharra</div>
<div style="font-size:12px;color:#6B7280;margin-top:5px;line-height:1">{header_context}</div>
</td>
</tr></table>
</td></tr>

<!-- Body -->
<tr><td style="padding:32px 40px;background:#ffffff">
{body_html}
</td></tr>

<!-- Footer -->
<tr><td style="padding:18px 40px;border-top:1px solid #E8E6FF;background:#ffffff">
<div style="font-size:12px;color:#6B7280;text-align:center;line-height:1.7">
Syntharra AI Receptionist &nbsp;&middot;&nbsp; <a href="https://syntharra.com" style="color:#6C63FF;text-decoration:none">syntharra.com</a>{footer_extra}
</div>
</td></tr>

</table>
</td></tr>
</table>
</body>
</html>"""
