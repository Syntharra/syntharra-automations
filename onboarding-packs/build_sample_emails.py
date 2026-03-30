import re, urllib.parse

ICON_URL = 'https://raw.githubusercontent.com/Syntharra/syntharra-website/main/logo-icon-2x.png'

# ── FIXED LOGO ROW: icon 40px, text vertically centred, total height balanced ──
LOGO_ROW = f'''<tr><td style="padding:0 0 28px;text-align:center">
  <table cellpadding="0" cellspacing="0" border="0" style="margin:0 auto">
    <tr>
      <td style="vertical-align:middle;padding-right:12px;line-height:0">
        <img src="{ICON_URL}" alt="Syntharra" width="44" height="44" style="display:block;border:0">
      </td>
      <td style="vertical-align:middle">
        <div style="font-family:Inter,-apple-system,BlinkMacSystemFont,sans-serif;font-size:22px;font-weight:700;letter-spacing:-0.5px;color:#0f0f1a;line-height:1">Syntharra</div>
        <div style="font-family:Inter,-apple-system,BlinkMacSystemFont,sans-serif;font-size:8.5px;font-weight:600;letter-spacing:1.5px;color:#6C63FF;text-transform:uppercase;line-height:1;margin-top:4px">Global AI Solutions</div>
      </td>
    </tr>
  </table>
</td></tr>'''

def qr(val, size=144):
    return f'https://api.qrserver.com/v1/create-qr-code/?size={size}x{size}&data={urllib.parse.quote(val)}'

DIV = '<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:24px 0"><tr><td bgcolor="#f3f0ff" style="background-color:#f3f0ff;height:1px;font-size:1px;line-height:1px">&nbsp;</td></tr></table>'

def section_header(icon, title, sub):
    return f'''<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:14px"><tr>
    <td style="width:34px;height:34px;border-radius:8px;background-color:#f3f0ff;text-align:center;vertical-align:middle;font-size:16px;line-height:34px;flex-shrink:0">{icon}</td>
    <td style="padding-left:12px"><p style="margin:0;font-size:15px;font-weight:700;color:#111827;font-family:Helvetica,Arial,sans-serif">{title}</p><p style="margin:2px 0 0;font-size:11px;color:#9ca3af;font-family:Helvetica,Arial,sans-serif">{sub}</p></td>
  </tr></table>'''

def steps(arr):
    # FIXED: all badges same size, no italic — consistent 22x22px circle
    result = ''
    for i, s in enumerate(arr):
        result += f'''<table cellpadding="0" cellspacing="0" border="0" style="margin-bottom:10px;width:100%"><tr>
    <td style="width:22px;min-width:22px;height:22px;border-radius:11px;background-color:#6C63FF;text-align:center;vertical-align:middle;font-size:11px;font-weight:700;color:#ffffff;font-family:Helvetica,Arial,sans-serif;line-height:22px;padding:0">{i+1}</td>
    <td style="padding-left:12px;font-size:13px;color:#374151;line-height:1.6;font-family:Helvetica,Arial,sans-serif;vertical-align:middle">{s}</td>
  </tr></table>'''
    return result

def qr_row(src, label, sub):
    return f'''<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:12px">
    <tr><td bgcolor="#f9f8ff" style="background-color:#f9f8ff;border-radius:8px;padding:14px 16px">
      <table cellpadding="0" cellspacing="0" border="0"><tr>
        <td style="width:72px"><img src="{src}" width="72" height="72" style="border-radius:6px;border:1px solid #e5e1ff;display:block" alt="QR Code"></td>
        <td style="padding-left:14px"><p style="margin:0 0 4px;font-size:12px;font-weight:600;color:#6C63FF;font-family:Helvetica,Arial,sans-serif">{label}</p><p style="margin:0;font-size:11px;color:#9ca3af;line-height:1.5;font-family:Helvetica,Arial,sans-serif">{sub}</p></td>
      </tr></table>
    </td></tr>
  </table>'''

def code_box(label, val, qr_src):
    return f'''<td style="width:50%;padding:4px"><table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f7f5ff" style="background-color:#f7f5ff;border-radius:8px"><tr><td style="padding:10px 8px;text-align:center">
    <p style="margin:0 0 5px;font-size:9px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:#9ca3af;font-family:Helvetica,Arial,sans-serif">{label}</p>
    <p style="margin:0 0 7px;font-size:12px;font-weight:700;color:#6C63FF;font-family:monospace">{val}</p>
    <img src="{qr_src}" width="56" height="56" style="border-radius:4px;border:1px solid #e5e1ff" alt="QR">
  </td></tr></table></td>'''

def carrier_card(name, sub, codes):
    rows = ''
    for i in range(0, len(codes), 2):
        c1 = code_box(codes[i][0], codes[i][1], qr(codes[i][2], 80))
        c2 = code_box(codes[i+1][0], codes[i+1][1], qr(codes[i+1][2], 80)) if i+1 < len(codes) else '<td></td>'
        rows += f'<tr>{c1}{c2}</tr>'
    return f'''<table width="100%" cellpadding="0" cellspacing="0" border="0" style="border:1px solid #f3f0ff;border-radius:10px;margin-bottom:10px">
    <tr><td style="padding:16px 16px 12px">
      <p style="margin:0 0 3px;font-size:13px;font-weight:600;color:#111827;font-family:Helvetica,Arial,sans-serif">{name}</p>
      <p style="margin:0 0 12px;font-size:11px;color:#9ca3af;font-family:Helvetica,Arial,sans-serif">{sub}</p>
      <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:-4px">{rows}</table>
    </td></tr>
  </table>'''

def voip_card(icon, title, body):
    return f'''<table width="100%" cellpadding="0" cellspacing="0" border="0" style="border:1px solid #f3f0ff;border-radius:10px;margin-bottom:10px">
    <tr><td style="padding:14px 16px">
      <p style="margin:0 0 6px;font-size:13px;font-weight:700;color:#111827;font-family:Helvetica,Arial,sans-serif">{icon} {title}</p>
      <p style="margin:0;font-size:13px;color:#6b7280;line-height:1.6;font-family:Helvetica,Arial,sans-serif">{body}</p>
    </td></tr>
  </table>'''

def build_email(data, is_premium=False):
    phone        = data.get('agent_phone_number', '')
    company_name = data.get('company_name', '')
    agent_name   = data.get('agent_name', '')
    lead_email   = data.get('lead_email', '')
    crm_platform = data.get('crm_platform', '')
    cal_platform = data.get('calendar_platform', '')
    has_crm      = bool(crm_platform and crm_platform not in ('', 'None'))
    has_cal      = bool(cal_platform and cal_platform not in ('', 'None'))

    digits     = re.sub(r'\D', '', phone)
    d          = digits[-10:]
    display_num = f'+1 ({d[0:3]}) {d[3:6]}-{d[6:]}'

    qr_iphone  = qr('App-Prefs:root=Phone&path=CALL_FORWARDING')
    qr_android = qr(f'tel:**21*{digits}#')

    qr_table_rows = ''
    quick_ref = [
        ('I have an iPhone',             'Use the Settings App method above'),
        ('I have an Android',            'Use Phone Settings or scan the Android QR'),
        ("I'm on AT&T or T-Mobile",      f'Dial <strong style="color:#fff">**21*{digits}#</strong>'),
        ("I'm on Verizon",               f'Dial <strong style="color:#fff">*72{digits}</strong>'),
        ('I use VoIP (RingCentral etc.)', 'Log in to your portal → Settings → Call Forwarding'),
        ('I have a landline',            f'Dial <strong style="color:#fff">*72{display_num}</strong>'),
        ('Forward unanswered only',      'Use the "When Unanswered" code for your carrier'),
    ]
    for i, (s, a) in enumerate(quick_ref):
        border = 'border-bottom:1px solid rgba(255,255,255,0.12);' if i < len(quick_ref)-1 else ''
        qr_table_rows += f'<tr><td style="padding:9px 6px;font-size:12px;color:#c4c0ff;font-weight:600;width:44%;font-family:Helvetica,Arial,sans-serif;{border}">{s}</td><td style="padding:9px 6px;font-size:12px;color:#ffffff;font-family:Helvetica,Arial,sans-serif;{border}">{a}</td></tr>'

    # ── Premium badge ──
    premium_badge = ''
    if is_premium:
        premium_badge = '''<td align="right" valign="top" style="padding-left:12px;white-space:nowrap">
      <span style="display:inline-block;background:#f3f0ff;border:1px solid #d4d0ff;border-radius:20px;padding:5px 12px;font-size:10px;font-weight:700;color:#6C63FF;letter-spacing:1px;text-transform:uppercase;font-family:Helvetica,Arial,sans-serif">⭐ PREMIUM</span>
    </td>'''

    plan_label = 'Syntharra Premium AI Receptionist' if is_premium else 'Syntharra AI Receptionist'

    # ── Premium integration section — LIGHT THEME, generic language ──
    # NOTE: This email only sends AFTER integrations are connected (workflow gated)
    integration_section = ''
    if is_premium:
        int_items = ''
        if has_cal:
            int_items += f'''<tr>
          <td style="padding:11px 16px;border-bottom:1px solid #f3f0ff">
            <table width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
              <td style="font-size:13px;font-weight:600;color:#111827;font-family:Helvetica,Arial,sans-serif">📅 {cal_platform}</td>
              <td align="right"><span style="background:#ecfdf5;border:1px solid #a7f3d0;border-radius:20px;padding:3px 10px;font-size:10px;font-weight:700;color:#065f46;font-family:Helvetica,Arial,sans-serif">✓ Connected</span></td>
            </tr></table>
          </td>
        </tr>'''
        if has_crm:
            int_items += f'''<tr>
          <td style="padding:11px 16px">
            <table width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
              <td style="font-size:13px;font-weight:600;color:#111827;font-family:Helvetica,Arial,sans-serif">🔧 {crm_platform}</td>
              <td align="right"><span style="background:#ecfdf5;border:1px solid #a7f3d0;border-radius:20px;padding:3px 10px;font-size:10px;font-weight:700;color:#065f46;font-family:Helvetica,Arial,sans-serif">✓ Connected</span></td>
            </tr></table>
          </td>
        </tr>'''
        
        integration_section = f'''
{DIV.replace('<table ', '<tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:0 40px"><table ')}
<tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:0 40px">
  {section_header('⚡', 'Your Premium Integrations', 'Calendar &amp; CRM are connected and active')}
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="border:1px solid #e5e7eb;border-radius:10px;overflow:hidden">
    {int_items}
  </table>
  <p style="margin:10px 0 0;font-size:12px;color:#9ca3af;font-family:Helvetica,Arial,sans-serif;">Your AI will now check real availability and log jobs automatically.</p>
</td></tr>'''

    html = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="color-scheme" content="light only"></head>
<body style="margin:0;padding:0;background-color:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f3f4f6"><tr><td align="center" style="padding:40px 16px">
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:540px">

{LOGO_ROW}
<tr><td bgcolor="#6C63FF" style="background-color:#6C63FF;height:4px;border-radius:8px 8px 0 0;font-size:4px;line-height:4px">&nbsp;</td></tr>

<tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:36px 40px 28px">
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:8px"><tr>
    <td>
      <p style="margin:0 0 6px;font-size:10px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:#6C63FF;font-family:Helvetica,Arial,sans-serif">{plan_label}</p>
      <h1 style="margin:0 0 6px;font-size:24px;font-weight:700;color:#111827;line-height:1.2;font-family:Helvetica,Arial,sans-serif">You're all set, {company_name} 🎉</h1>
      <p style="margin:0;font-size:13px;color:#6b7280;line-height:1.65;font-family:Helvetica,Arial,sans-serif">Your AI receptionist is live and answering calls 24/7. Forward your business number using any method below — it takes under 2 minutes.</p>
    </td>
    {premium_badge}
  </tr></table>
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:22px">
    <tr><td bgcolor="#f7f5ff" style="background-color:#f7f5ff;border-radius:12px;padding:22px;text-align:center">
      <table cellpadding="0" cellspacing="0" border="0" style="margin:0 auto">
        <tr><td bgcolor="#6C63FF" style="background-color:#6C63FF;border-radius:10px;padding:12px 28px;text-align:center">
          <p style="margin:0 0 4px;font-size:9px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:#c4c0ff;font-family:Helvetica,Arial,sans-serif">Your AI Receptionist Number</p>
          <p style="margin:0;font-size:22px;font-weight:800;color:#ffffff;letter-spacing:1px;font-family:Helvetica,Arial,sans-serif">{display_num}</p>
        </td></tr>
      </table>
      <p style="margin:12px 0 0;font-size:12px;color:#9ca3af;font-family:Helvetica,Arial,sans-serif">Forward your existing business number to this number using any of the methods below.</p>
    </td></tr>
  </table>
</td></tr>

{DIV.replace('<table ', '<tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:0 40px"><table ')}

<tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:0 40px">
  {section_header('📱','iPhone — Settings App','Works on all iPhones running iOS 13 and above')}
  {steps([
    'Open <strong style="color:#111827">Settings → Phone → Call Forwarding</strong>',
    'Toggle <strong style="color:#111827">Call Forwarding</strong> on',
    f'Enter your number: <strong style="color:#111827">{display_num}</strong>',
    'Done — to stop forwarding, come back here and toggle it off'
  ])}
  {qr_row(qr_iphone, 'Scan to open Call Forwarding settings', 'Takes you directly to the Call Forwarding screen on iPhone.')}
</td></tr>

{DIV.replace('<table ', '<tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:0 40px"><table ')}

<tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:0 40px">
  {section_header('🤖','Android — Phone Settings','Samsung, Google Pixel, OnePlus and all Android devices')}
  {steps([
    'Open the <strong style="color:#111827">Phone app</strong> → tap <strong style="color:#111827">⋮ → Settings → Calls</strong>',
    'Tap <strong style="color:#111827">Call Forwarding → Always Forward</strong>',
    f'Enter <strong style="color:#111827">{display_num}</strong> and confirm',
    'Samsung path: Phone → ⋮ → Settings → Supplementary services → Call forwarding'
  ])}
  {qr_row(qr_android, 'Scan to activate forwarding instantly', 'Dials the GSM forwarding code automatically.')}
</td></tr>

{DIV.replace('<table ', '<tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:0 40px"><table ')}

<tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:0 40px">
  {section_header('📡','Carrier Dial Codes','Dial directly from any phone — no menus needed.')}
  {carrier_card(
    'AT&amp;T &nbsp;·&nbsp; T-Mobile &nbsp;·&nbsp; Cricket &nbsp;·&nbsp; Mint Mobile &nbsp;·&nbsp; Google Fi &nbsp;·&nbsp; Metro',
    'GSM Carriers',
    [
      ['Forward All', f'**21*{digits}#', f'tel:**21*{digits}#'],
      ['Forward Unanswered', f'**61*{digits}#', f'tel:**61*{digits}#'],
      ['Cancel All', '##21#', 'tel:##21#'],
      ['Cancel Unanswered', '##61#', 'tel:##61#'],
    ]
  )}
  {carrier_card(
    'Verizon &nbsp;·&nbsp; Visible &nbsp;·&nbsp; Xfinity Mobile &nbsp;·&nbsp; Spectrum Mobile',
    'Verizon Network Carriers',
    [
      ['Forward All', f'*72{digits}', f'tel:*72{digits}'],
      ['Forward Unanswered', f'*71{digits}', f'tel:*71{digits}'],
      ['Cancel All', '*73', 'tel:*73'],
    ]
  )}
</td></tr>

{DIV.replace('<table ', '<tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:0 40px"><table ')}

<tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:0 40px">
  {section_header('🏢','Business Lines, Landlines &amp; VoIP','')}
  {voip_card('🌐','VoIP — RingCentral, Grasshopper, Google Voice, Dialpad, 8x8', f'Log in to your provider portal → <strong>Settings → Call Forwarding</strong> → enter <strong>{display_num}</strong>.')}
  {voip_card('☎️','Traditional Landline', f'From your handset, dial <strong>*72{digits}</strong> and press Call. Wait for the confirmation tone. To cancel, dial <strong>*73</strong>.')}
  {voip_card('🖥️','PBX / Enterprise System', f'Contact your IT team and ask them to set unconditional call forwarding to <strong>{display_num}</strong>.')}
</td></tr>

{DIV.replace('<table ', '<tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:0 40px"><table ')}

<tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:0 40px">
  {section_header('⚡','Quick Reference','')}
  <table width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr><td bgcolor="#6C63FF" style="background-color:#6C63FF;border-radius:10px;padding:18px">
      <p style="margin:0 0 12px;font-size:10px;font-weight:700;color:#c4c0ff;letter-spacing:2px;text-transform:uppercase;font-family:Helvetica,Arial,sans-serif">Which method should I use?</p>
      <table width="100%" cellpadding="0" cellspacing="0" border="0">{qr_table_rows}</table>
    </td></tr>
  </table>
</td></tr>

{integration_section}

<tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:22px 40px 28px">
  <table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td bgcolor="#f3f0ff" style="background-color:#f3f0ff;height:1px;font-size:1px;line-height:1px">&nbsp;</td></tr></table>
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:20px">
    <tr>
      <td width="3" bgcolor="#6C63FF" style="background-color:#6C63FF;border-radius:2px;vertical-align:top">&nbsp;</td>
      <td style="padding-left:14px;font-size:13px;color:#6b7280;line-height:1.7;font-family:Helvetica,Arial,sans-serif">Need help? Reply to this email or contact us at <strong style="color:#111827">support@syntharra.com</strong> — we'll get your forwarding set up in minutes.</td>
    </tr>
  </table>
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:22px"><tr><td bgcolor="#f3f0ff" style="background-color:#f3f0ff;height:1px;font-size:1px;line-height:1px">&nbsp;</td></tr></table>
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:20px"><tr><td style="text-align:center">
    <p style="margin:0 0 4px;font-size:11px;font-weight:800;letter-spacing:3px;color:#6C63FF;font-family:Helvetica,Arial,sans-serif">SYNTHARRA</p>
    <p style="margin:0;font-size:11px;color:#9ca3af;font-family:Helvetica,Arial,sans-serif">syntharra.com &nbsp;·&nbsp; support@syntharra.com</p>
  </td></tr></table>
</td></tr>

</table></td></tr></table>
</body></html>'''
    return html

# Sample data
std = {
    'company_name': 'Arctic Breeze HVAC',
    'agent_name': 'Alex',
    'lead_email': 'mike@arcticbreezehvac.com',
    'agent_phone_number': '+18129944371',
}
prem = {
    'company_name': 'Summit Climate Solutions',
    'agent_name': 'Sophie',
    'lead_email': 'james@summitclimate.com',
    'agent_phone_number': '+18005551234',
    'crm_platform': 'Jobber',
    'calendar_platform': 'Google Calendar',
}

with open('/mnt/user-data/outputs/sample-email-standard.html', 'w') as f:
    f.write(build_email(std, is_premium=False))
with open('/mnt/user-data/outputs/sample-email-premium.html', 'w') as f:
    f.write(build_email(prem, is_premium=True))

print('✅ Done')
