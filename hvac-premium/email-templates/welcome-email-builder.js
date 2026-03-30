// ============================================================
// Syntharra Premium — Welcome Email Builder
// Based on: hvac-standard Build Welcome Email HTML node
// Additions: WhatsApp support block (commented out — enable when number is ready)
//            Premium badge, 1,000 min allocation, integration status section
// ============================================================

const input = $input.first().json;
const companyName    = input.company_name || 'your company';
const agentName      = input.agent_name   || 'your AI receptionist';
const leadEmail      = input.lead_email   || '';
const phone          = input.agent_phone_number || '';
const crmPlatform    = input.crm_platform || '';
const calPlatform    = input.calendar_platform || '';
const hasCRM         = crmPlatform && crmPlatform !== 'None';
const hasCal         = calPlatform && calPlatform !== 'None';

// ── WhatsApp Config (COMMENTED OUT — configure when number is ready) ─────
// const WHATSAPP_NUMBER = 'XXXXXXXXXXX'; // digits only, incl country code e.g. 353851234567
// const WHATSAPP_LINK   = `https://wa.me/${WHATSAPP_NUMBER}`;
// const WHATSAPP_ADD    = `https://wa.me/${WHATSAPP_NUMBER}?text=Hi%2C%20I%27m%20a%20Syntharra%20Premium%20client`;
// ─────────────────────────────────────────────────────────────────────────

const ICON_URL = 'https://raw.githubusercontent.com/Syntharra/syntharra-website/main/logo-icon-2x.png';
const LOGO_ROW = `<tr><td style="padding:0 0 24px;text-align:center"><table cellpadding="0" cellspacing="0" style="margin:0 auto"><tr><td style="vertical-align:middle;padding-right:10px"><img src="${ICON_URL}" alt="" width="36" height="36" style="display:block;border:0"></td><td style="vertical-align:middle;text-align:left"><table cellpadding="0" cellspacing="0" border="0"><tr><td style="text-align:left;padding:0"><div style="font-family:Inter,-apple-system,sans-serif;font-size:16px;font-weight:700;letter-spacing:-0.3px;color:#0f0f1a;line-height:1;text-align:left">Syntharra</div></td></tr><tr><td style="text-align:left;padding:3px 0 0 0"><div style="font-family:Inter,-apple-system,sans-serif;font-size:7.5px;font-weight:600;letter-spacing:1.2px;color:#6C63FF;text-transform:uppercase;line-height:1;text-align:left">Global AI Solutions</div></td></tr></table></td></tr></table></td></tr>`;

function qr(data, size) { return 'https://api.qrserver.com/v1/create-qr-code/?size=' + (size||144) + 'x' + (size||144) + '&data=' + encodeURIComponent(data); }

// ── NO-PHONE PATH ─────────────────────────────────────────────────────────
if (!phone) {
  const html = `<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="color-scheme" content="light only"></head>
<body style="margin:0;padding:0;background-color:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f3f4f6"><tr><td align="center" style="padding:40px 16px">
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:580px">
${LOGO_ROW}
  <tr><td bgcolor="#f59e0b" style="background-color:#f59e0b;height:4px;border-radius:8px 8px 0 0;font-size:4px;line-height:4px">&nbsp;</td></tr>
  <tr><td bgcolor="#ffffff" style="background-color:#ffffff;border-radius:0 0 12px 12px;padding:36px 40px 32px">
    <p style="margin:0 0 6px;font-size:10px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:#d97706;font-family:Helvetica,Arial,sans-serif">Action Required</p>
    <h1 style="margin:0 0 6px;font-size:24px;font-weight:700;color:#111827;line-height:1.2;font-family:Helvetica,Arial,sans-serif">One more step to go live</h1>
    <p style="margin:0;font-size:13px;color:#6b7280;line-height:1.65;font-family:Helvetica,Arial,sans-serif">Your Premium AI receptionist is set up and ready — we just need to connect your dedicated phone number to complete the activation.</p>
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:24px 0"><tr><td align="center">
      <table cellpadding="0" cellspacing="0" border="0"><tr>
        <td bgcolor="#6C63FF" style="background-color:#6C63FF;border-radius:8px;padding:13px 32px">
          <a href="mailto:support@syntharra.com?subject=Ready%20for%20phone%20number%20activation%20-%20${encodeURIComponent(companyName)}&body=Hi%20Syntharra%20team%2C%0A%0AI'm%20ready%20to%20go%20live.%20Please%20assign%20my%20dedicated%20phone%20number.%0A%0AThanks" style="font-size:14px;font-weight:600;color:#ffffff;text-decoration:none;font-family:Helvetica,Arial,sans-serif">Reply — I'm Ready to Go Live</a>
        </td>
      </tr></table>
    </td></tr></table>
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:20px"><tr><td style="text-align:center">
      <p style="margin:0 0 4px;font-size:11px;font-weight:800;letter-spacing:3px;color:#6C63FF;font-family:Helvetica,Arial,sans-serif">SYNTHARRA</p>
      <p style="margin:0;font-size:11px;color:#9ca3af;font-family:Helvetica,Arial,sans-serif">syntharra.com &nbsp;·&nbsp; support@syntharra.com</p>
    </td></tr></table>
  </td></tr>
</table>
</td></tr></table>
</body></html>`;
  return [{ json: { ...input, emailHtml: html, skipEmail: false, lead_email: leadEmail, company_name: companyName } }];
}

// ── FULL PREMIUM WELCOME EMAIL ────────────────────────────────────────────
const digits     = phone.replace(/\D/g,'');
const d          = digits.slice(-10);
const displayNum = '+1 (' + d.slice(0,3) + ') ' + d.slice(3,6) + '-' + d.slice(6);
const qrIphone   = qr('App-Prefs:root=Phone&path=CALL_FORWARDING');
const qrAndroid  = qr('tel:**21*' + digits + '#');

const DIV = `<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:24px 0"><tr><td bgcolor="#f3f0ff" style="background-color:#f3f0ff;height:1px;font-size:1px;line-height:1px">&nbsp;</td></tr></table>`;

function sectionHeader(icon, title, sub) {
  return `<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:14px"><tr>
    <td style="width:34px;height:34px;border-radius:8px;background-color:#f3f0ff;text-align:center;vertical-align:middle;font-size:16px;line-height:34px">${icon}</td>
    <td style="padding-left:12px"><p style="margin:0;font-size:15px;font-weight:700;color:#111827;font-family:Helvetica,Arial,sans-serif">${title}</p><p style="margin:2px 0 0;font-size:11px;color:#9ca3af;font-family:Helvetica,Arial,sans-serif">${sub}</p></td>
  </tr></table>`;
}

function steps(arr) {
  return arr.map((s,i) => `<table cellpadding="0" cellspacing="0" border="0" style="margin-bottom:10px"><tr>
    <td style="width:22px;height:22px;border-radius:11px;background-color:#6C63FF;text-align:center;vertical-align:middle;font-size:11px;font-weight:700;color:#ffffff;font-family:Helvetica,Arial,sans-serif">${i+1}</td>
    <td style="padding-left:12px;font-size:13px;color:#374151;line-height:1.6;font-family:Helvetica,Arial,sans-serif">${s}</td>
  </tr></table>`).join('');
}

function qrRow(src, label, sub) {
  return `<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:12px">
    <tr><td bgcolor="#f9f8ff" style="background-color:#f9f8ff;border-radius:8px;padding:14px 16px">
      <table cellpadding="0" cellspacing="0" border="0"><tr>
        <td><img src="${src}" width="72" height="72" style="border-radius:6px;border:1px solid #e5e1ff;display:block" alt="QR Code"></td>
        <td style="padding-left:14px"><p style="margin:0 0 4px;font-size:12px;font-weight:600;color:#6C63FF;font-family:Helvetica,Arial,sans-serif">${label}</p><p style="margin:0;font-size:11px;color:#9ca3af;line-height:1.5;font-family:Helvetica,Arial,sans-serif">${sub}</p></td>
      </tr></table>
    </td></tr>
  </table>`;
}

function codeBox(label, val, qrSrc) {
  return `<td style="width:50%;padding:4px"><table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f7f5ff" style="background-color:#f7f5ff;border-radius:8px"><tr><td style="padding:10px 8px;text-align:center">
    <p style="margin:0 0 5px;font-size:9px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:#9ca3af;font-family:Helvetica,Arial,sans-serif">${label}</p>
    <p style="margin:0 0 7px;font-size:12px;font-weight:700;color:#6C63FF;font-family:monospace">${val}</p>
    <img src="${qrSrc}" width="56" height="56" style="border-radius:4px;border:1px solid #e5e1ff" alt="QR">
  </td></tr></table></td>`;
}

function carrierCard(name, sub, codes) {
  let rows = '';
  for (let i = 0; i < codes.length; i += 2) {
    rows += `<tr>${codeBox(codes[i][0], codes[i][1], qr(codes[i][2], 80))}${codes[i+1] ? codeBox(codes[i+1][0], codes[i+1][1], qr(codes[i+1][2], 80)) : '<td></td>'}</tr>`;
  }
  return `<table width="100%" cellpadding="0" cellspacing="0" border="0" style="border:1px solid #f3f0ff;border-radius:10px;margin-bottom:10px">
    <tr><td style="padding:16px 16px 12px">
      <p style="margin:0 0 3px;font-size:13px;font-weight:600;color:#111827;font-family:Helvetica,Arial,sans-serif">${name}</p>
      <p style="margin:0 0 12px;font-size:11px;color:#9ca3af;font-family:Helvetica,Arial,sans-serif">${sub}</p>
      <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:-4px">${rows}</table>
    </td></tr>
  </table>`;
}

function voipCard(icon, title, body) {
  return `<table width="100%" cellpadding="0" cellspacing="0" border="0" style="border:1px solid #f3f0ff;border-radius:10px;margin-bottom:10px">
    <tr><td style="padding:14px 16px">
      <p style="margin:0 0 6px;font-size:13px;font-weight:700;color:#111827;font-family:Helvetica,Arial,sans-serif">${icon} ${title}</p>
      <p style="margin:0;font-size:13px;color:#6b7280;line-height:1.6;font-family:Helvetica,Arial,sans-serif">${body}</p>
    </td></tr>
  </table>`;
}

const qrTableRows = [
  ['I have an iPhone',               'Use the Settings App method above'],
  ['I have an Android',              'Use Phone Settings or scan the Android QR'],
  ['I\'m on AT&T or T-Mobile',       'Dial <strong style="color:#fff">**21*' + digits + '#</strong>'],
  ['I\'m on Verizon',                'Dial <strong style="color:#fff">*72' + digits + '</strong>'],
  ['I use VoIP (RingCentral etc.)',   'Log in to your portal → Settings → Call Forwarding'],
  ['I have a landline',              'Dial <strong style="color:#fff">*72 then your AI number</strong> from the handset'],
  ['Forward when unanswered only',   'Use the "When Unanswered" code for your carrier above'],
].map(([s,a],i,arr) => {
  const border = i < arr.length-1 ? 'border-bottom:1px solid rgba(255,255,255,0.12);' : '';
  return `<tr><td style="padding:9px 6px;font-size:12px;color:#c4c0ff;font-weight:600;width:44%;font-family:Helvetica,Arial,sans-serif;${border}">${s}</td><td style="padding:9px 6px;font-size:12px;color:#ffffff;font-family:Helvetica,Arial,sans-serif;${border}">${a}</td></tr>`;
}).join('');

// ── Integration status section (Premium only) ─────────────────────────────
const integrationSection = (hasCRM || hasCal) ? `
${DIV}
<tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:0 40px">
  ${sectionHeader('⚡', 'Your Premium Integrations', 'Google Calendar and CRM connections — setup instructions sent separately')}
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="border:1px solid #e5e1ff;border-radius:10px;overflow:hidden">
    ${hasCal ? `<tr>
      <td bgcolor="#1a1440" style="background-color:#1a1440;padding:12px 16px;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
          <td style="font-size:13px;font-weight:600;color:#ffffff;font-family:Helvetica,Arial,sans-serif">📅 ${calPlatform}</td>
          <td align="right"><span style="background:rgba(0,212,255,0.15);border:1px solid rgba(0,212,255,0.3);border-radius:20px;padding:3px 10px;font-size:10px;font-weight:700;color:#00D4FF;font-family:Helvetica,Arial,sans-serif">Setup email sent</span></td>
        </tr></table>
      </td>
    </tr>` : ''}
    ${hasCRM ? `<tr>
      <td bgcolor="#1a1440" style="background-color:#1a1440;padding:12px 16px;border-top:1px solid rgba(255,255,255,0.08)">
        <table width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
          <td style="font-size:13px;font-weight:600;color:#ffffff;font-family:Helvetica,Arial,sans-serif">🔧 ${crmPlatform}</td>
          <td align="right"><span style="background:rgba(0,212,255,0.15);border:1px solid rgba(0,212,255,0.3);border-radius:20px;padding:3px 10px;font-size:10px;font-weight:700;color:#00D4FF;font-family:Helvetica,Arial,sans-serif">Setup email sent</span></td>
        </tr></table>
      </td>
    </tr>` : ''}
    <tr>
      <td style="padding:10px 16px;background-color:#f9f8ff;">
        <p style="margin:0;font-size:12px;color:#9ca3af;font-family:Helvetica,Arial,sans-serif">Until authorised, your AI captures all caller details and notifies you for manual follow-up. Check your inbox for the integration setup email.</p>
      </td>
    </tr>
  </table>
</td></tr>` : '';

// ── WhatsApp support block (COMMENTED OUT — enable when number is ready) ──
/*
const whatsappSection = `
${DIV}
<tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:0 40px">
  ${sectionHeader('💬', 'WhatsApp Priority Support', 'Premium exclusive — direct access to our team')}
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f0fdf4;border:1px solid #a3e6bc;border-radius:10px;margin-bottom:10px">
    <tr><td style="padding:16px 18px">
      <p style="margin:0 0 12px;font-size:13px;color:#374151;line-height:1.6;font-family:Helvetica,Arial,sans-serif">
        As a Premium client, you have direct WhatsApp access to the Syntharra support team for priority assistance. 
        Save the number below or tap a button to connect instantly.
      </p>
      <table width="100%" cellpadding="0" cellspacing="0" border="0">
        <tr>
          <td width="50%" style="padding-right:6px">
            <a href="${WHATSAPP_LINK}" style="display:block;background:#25D366;color:#ffffff;font-weight:700;font-size:13px;padding:12px 16px;border-radius:8px;text-decoration:none;text-align:center;font-family:Helvetica,Arial,sans-serif">💬 Message on WhatsApp</a>
          </td>
          <td width="50%" style="padding-left:6px">
            <a href="${WHATSAPP_ADD}" style="display:block;background:#ffffff;color:#25D366;font-weight:700;font-size:13px;padding:12px 16px;border-radius:8px;text-decoration:none;text-align:center;border:2px solid #25D366;font-family:Helvetica,Arial,sans-serif">➕ Add to Contacts</a>
          </td>
        </tr>
      </table>
      <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:12px">
        <tr>
          <td align="center">
            <img src="https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=${encodeURIComponent(WHATSAPP_LINK)}" 
                 width="80" height="80" style="border-radius:6px;border:1px solid #a3e6bc;display:block;margin:0 auto 6px" alt="WhatsApp QR">
            <p style="margin:0;font-size:10px;color:#6b7280;font-family:Helvetica,Arial,sans-serif">Scan to open WhatsApp chat</p>
          </td>
        </tr>
      </table>
      <p style="margin:10px 0 0;font-size:11px;color:#9ca3af;text-align:center;font-family:Helvetica,Arial,sans-serif">
        Support number: +${WHATSAPP_NUMBER} &nbsp;·&nbsp; Typically responds within 2 hours
      </p>
    </td></tr>
  </table>
</td></tr>`;
*/
// To activate: uncomment the block above, ensure WHATSAPP_NUMBER is set at the top,
// and add ${whatsappSection} into the html template below where indicated.
// ──────────────────────────────────────────────────────────────────────────

const html = `<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="color-scheme" content="light only"></head>
<body style="margin:0;padding:0;background-color:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f3f4f6"><tr><td align="center" style="padding:40px 16px">
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:540px">

<tr><td bgcolor="#6C63FF" style="background-color:#6C63FF;height:4px;border-radius:8px 8px 0 0;font-size:4px;line-height:4px">&nbsp;</td></tr>

<tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:36px 40px 28px">
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:8px"><tr>
    <td><p style="margin:0 0 6px;font-size:10px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:#6C63FF;font-family:Helvetica,Arial,sans-serif">Syntharra Premium AI Receptionist</p>
    <h1 style="margin:0 0 6px;font-size:24px;font-weight:700;color:#111827;line-height:1.2;font-family:Helvetica,Arial,sans-serif">You're all set, ${companyName} 🎉</h1>
    <p style="margin:0;font-size:13px;color:#6b7280;line-height:1.65;font-family:Helvetica,Arial,sans-serif">Your Premium AI receptionist is live and answering calls 24/7. Follow the steps below to forward your business number — pick whichever method suits your setup.</p></td>
    <td align="right" valign="top" style="padding-left:12px">
      <div style="display:inline-block;background:#1a1440;border-radius:20px;padding:5px 12px;white-space:nowrap">
        <span style="font-size:10px;font-weight:700;color:#00D4FF;letter-spacing:1px;text-transform:uppercase;font-family:Helvetica,Arial,sans-serif">⭐ PREMIUM</span>
      </div>
    </td>
  </tr></table>

  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:22px">
    <tr><td bgcolor="#f7f5ff" style="background-color:#f7f5ff;border-radius:12px;padding:22px;text-align:center">
      <table cellpadding="0" cellspacing="0" border="0" style="margin:0 auto">
        <tr><td bgcolor="#6C63FF" style="background-color:#6C63FF;border-radius:10px;padding:12px 28px;text-align:center">
          <p style="margin:0 0 4px;font-size:9px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:#c4c0ff;font-family:Helvetica,Arial,sans-serif">Your AI Receptionist Number</p>
          <p style="margin:0;font-size:22px;font-weight:800;color:#ffffff;letter-spacing:1px;font-family:Helvetica,Arial,sans-serif">${displayNum}</p>
        </td></tr>
      </table>
      <p style="margin:12px 0 0;font-size:12px;color:#9ca3af;font-family:Helvetica,Arial,sans-serif">Forward your existing business number to this number using any of the methods below.</p>
    </td></tr>
  </table>
</td></tr>

${DIV.replace('<table ', '<tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:0 40px"><table ')}

<tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:0 40px">
  ${sectionHeader('📱','iPhone — Settings App','Works on all iPhones running iOS 13 and above')}
  ${steps([
    'Open <strong style="color:#111827">Settings → Phone → Call Forwarding</strong>',
    'Toggle <strong style="color:#111827">Call Forwarding</strong> on',
    'Enter your number: <strong style="color:#111827">' + displayNum + '</strong>',
    'To stop forwarding, return here and toggle it <strong style="color:#111827">off</strong>'
  ])}
  ${qrRow(qrIphone, 'Scan to open Call Forwarding settings', 'Scan with your iPhone camera — takes you directly to the Call Forwarding screen.')}
</td></tr>

${DIV.replace('<table ', '<tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:0 40px"><table ')}

<tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:0 40px">
  ${sectionHeader('🤖','Android — Phone Settings','Samsung, Google Pixel, OnePlus and all Android devices')}
  ${steps([
    'Open the <strong style="color:#111827">Phone app</strong> → tap <strong style="color:#111827">⋮ → Settings → Calls</strong>',
    'Tap <strong style="color:#111827">Call Forwarding → Always Forward</strong>',
    'Enter <strong style="color:#111827">' + displayNum + '</strong> and confirm',
    '<em style="color:#9ca3af;font-size:12px">Samsung: Phone → ⋮ → Settings → Supplementary services → Call forwarding</em>'
  ])}
  ${qrRow(qrAndroid, 'Scan to activate forwarding instantly', 'Dials the GSM forwarding code automatically. Works on AT&T, T-Mobile and most carriers.')}
</td></tr>

${DIV.replace('<table ', '<tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:0 40px"><table ')}

<tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:0 40px">
  ${sectionHeader('📡','Carrier Dial Codes','Dial directly from any phone — no menus needed.')}
  ${carrierCard(
    'AT&amp;T &nbsp;·&nbsp; T-Mobile &nbsp;·&nbsp; Cricket &nbsp;·&nbsp; Mint Mobile &nbsp;·&nbsp; Google Fi &nbsp;·&nbsp; Metro',
    'GSM Carriers',
    [
      ['Forward All Calls',       '**21*'+digits+'#', 'tel:**21*'+digits+'#'],
      ['Forward When Unanswered', '**61*'+digits+'#', 'tel:**61*'+digits+'#'],
      ['Cancel All Forwarding',   '##21#',             'tel:##21#'],
      ['Cancel Unanswered',       '##61#',             'tel:##61#'],
    ]
  )}
  ${carrierCard(
    'Verizon &nbsp;·&nbsp; Visible &nbsp;·&nbsp; Xfinity Mobile &nbsp;·&nbsp; Spectrum Mobile',
    'Verizon Network Carriers',
    [
      ['Forward All Calls',       '*72'+digits, 'tel:*72'+digits],
      ['Forward When Unanswered', '*71'+digits, 'tel:*71'+digits],
      ['Cancel All Forwarding',   '*73',         'tel:*73'],
    ]
  )}
</td></tr>

${DIV.replace('<table ', '<tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:0 40px"><table ')}

<tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:0 40px">
  ${sectionHeader('🏢','Business Lines, Landlines &amp; VoIP','Office phones, PBX systems and internet-based services')}
  ${voipCard('🌐','VoIP — RingCentral, Grasshopper, Google Voice, Dialpad, 8x8', `Log in to your provider's web portal or app. Go to <strong>Settings → Calls → Call Forwarding</strong> and enter <strong>${displayNum}</strong>.`)}
  ${voipCard('☎️','Traditional Landline', `Dial <strong>*72 followed by ${digits}</strong> from your handset and press Call. To cancel, dial <strong>*73</strong>.`)}
  ${voipCard('🖥️','PBX / Enterprise System', `Contact your IT administrator to set call forwarding to <strong>${displayNum}</strong>.`)}
</td></tr>

${DIV.replace('<table ', '<tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:0 40px"><table ')}

<tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:0 40px">
  ${sectionHeader('⚡','Quick Reference','Not sure which method to use? Find your situation below.')}
  <table width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr><td bgcolor="#6C63FF" style="background-color:#6C63FF;border-radius:10px;padding:18px">
      <p style="margin:0 0 12px;font-size:10px;font-weight:700;color:#c4c0ff;letter-spacing:2px;text-transform:uppercase;font-family:Helvetica,Arial,sans-serif">Which method should I use?</p>
      <table width="100%" cellpadding="0" cellspacing="0" border="0">${qrTableRows}</table>
    </td></tr>
  </table>
</td></tr>

${integrationSection}

<!-- WHATSAPP SECTION: uncomment ${whatsappSection} here when number is ready -->

<tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:22px 40px 28px">
  <table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td bgcolor="#f3f0ff" style="background-color:#f3f0ff;height:1px;font-size:1px;line-height:1px">&nbsp;</td></tr></table>
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:20px">
    <tr>
      <td width="3" bgcolor="#6C63FF" style="background-color:#6C63FF;border-radius:2px;vertical-align:top">&nbsp;</td>
      <td style="padding-left:14px;font-size:13px;color:#6b7280;line-height:1.7;font-family:Helvetica,Arial,sans-serif">Need help? Reply to this email or reach us at <strong style="color:#111827">support@syntharra.com</strong> — we'll get your forwarding set up in minutes.</td>
    </tr>
  </table>
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:22px"><tr><td bgcolor="#f3f0ff" style="background-color:#f3f0ff;height:1px;font-size:1px;line-height:1px">&nbsp;</td></tr></table>
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:20px"><tr><td style="text-align:center">
    <p style="margin:0 0 4px;font-size:11px;font-weight:800;letter-spacing:3px;color:#6C63FF;font-family:Helvetica,Arial,sans-serif">SYNTHARRA</p>
    <p style="margin:0;font-size:11px;color:#9ca3af;font-family:Helvetica,Arial,sans-serif">syntharra.com &nbsp;·&nbsp; support@syntharra.com</p>
  </td></tr></table>
</td></tr>

</table></td></tr></table>
</body></html>`;

return [{ json: { ...input, emailHtml: html, skipEmail: false, lead_email: leadEmail, company_name: companyName, agent_name: agentName } }];
