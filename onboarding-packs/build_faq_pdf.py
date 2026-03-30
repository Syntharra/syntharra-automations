"""
Syntharra — Client Onboarding FAQ & How-To Guide PDF  v2
Fixes: page-split text, real logo in cover, KeepTogether throughout
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, KeepTogether, PageBreak, Image
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus.flowables import Flowable
import os

W, H = A4

# ── Colours ──────────────────────────────────────────────────────────
PURPLE   = colors.HexColor('#6C63FF')
CYAN     = colors.HexColor('#00D4FF')
DARK     = colors.HexColor('#1A1A2E')
GREY_BG  = colors.HexColor('#F7F7FB')
MUTED    = colors.HexColor('#6B7280')
BORDER   = colors.HexColor('#E5E7EB')
LIGHT_P  = colors.HexColor('#F3F0FF')
WHITE    = colors.white
CARD_BG  = colors.white

COL_W = 170 * mm   # usable width with 20mm margins each side


# ── Style factory ────────────────────────────────────────────────────
def S(name, font='Helvetica', size=10, color=DARK, leading=None,
      align=TA_LEFT, sb=0, sa=0):
    return ParagraphStyle(name, fontName=font, fontSize=size,
                          textColor=color,
                          leading=leading or size * 1.45,
                          alignment=align,
                          spaceBefore=sb, spaceAfter=sa,
                          wordWrap='CJK')

S_BODY  = S('body',  size=10, color=DARK,   sa=3)
S_MUTED = S('muted', size=9,  color=MUTED,  sa=2)
S_CODE  = S('code',  font='Courier', size=10, color=PURPLE, sa=2)
S_H1    = S('h1',    font='Helvetica-Bold', size=15, color=DARK,  sb=4, sa=4)
S_H2    = S('h2',    font='Helvetica-Bold', size=11, color=PURPLE, sb=4, sa=2)
S_SECBADGE = S('sb', font='Helvetica-Bold', size=8, color=PURPLE, sa=1)
S_WHITE = S('wh',   size=9, color=WHITE, sa=2)
S_WHITE_B = S('whb', font='Helvetica-Bold', size=11, color=WHITE, sa=2)
S_FAQ_Q = S('fq', font='Helvetica-Bold', size=10, color=DARK, sb=2, sa=1)
S_STEP_T = S('st', font='Helvetica-Bold', size=10, color=DARK, sa=1)
S_CAP = S('cap', size=7, color=MUTED, align=TA_CENTER)

def sp(h=4):
    return Spacer(1, h * mm)

def HR(c=BORDER, t=0.5):
    return HRFlowable(width='100%', thickness=t, color=c, spaceAfter=5, spaceBefore=5)


# ── Step badge flowable ───────────────────────────────────────────────
class StepBadge(Flowable):
    def __init__(self, n, size=18):
        super().__init__()
        self.n = str(n)
        self.size = size
        self.width = size
        self.height = size

    def draw(self):
        c = self.canv
        r = self.size / 2
        c.setFillColor(PURPLE)
        c.circle(r, r, r, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont('Helvetica-Bold', self.size * 0.5)
        c.drawCentredString(r, r - self.size * 0.17, self.n)


# ── Helpers ───────────────────────────────────────────────────────────
def card(rows_content, bg=GREY_BG, pad=10, border=None, radius=6):
    """Single-column card"""
    t = Table([[rows_content]], colWidths=[COL_W])
    cmds = [
        ('BACKGROUND', (0,0), (-1,-1), bg),
        ('TOPPADDING',    (0,0), (-1,-1), pad),
        ('BOTTOMPADDING', (0,0), (-1,-1), pad),
        ('LEFTPADDING',   (0,0), (-1,-1), pad+2),
        ('RIGHTPADDING',  (0,0), (-1,-1), pad),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROUNDEDCORNERS', [radius]),
    ]
    if border:
        cmds.append(('BOX', (0,0), (-1,-1), 0.5, border))
    t.setStyle(TableStyle(cmds))
    return t


def step_row(number, title, body):
    badge = Table([[StepBadge(number)]], colWidths=[9*mm])
    badge.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    text = [Paragraph(title, S_STEP_T), Paragraph(body, S_BODY)]
    row = Table([[badge, text]], colWidths=[11*mm, COL_W - 11*mm])
    row.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    return KeepTogether(row)


def faq_item(q, a):
    return KeepTogether([
        Paragraph(q, S_FAQ_Q),
        Paragraph(a, S_BODY),
        HR(BORDER, 0.4),
    ])


def dark_table(headers, rows, col_widths):
    data = [[Paragraph(h, S('th', 'Helvetica-Bold', 9, WHITE, leading=12)) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), S('td', size=9, color=DARK, leading=13)) for c in row])
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), DARK),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [CARD_BG, GREY_BG]),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.3, BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROUNDEDCORNERS', [4]),
    ]))
    return t


def section_start(num, title):
    """Returns list of flowables for a section header — always KeepTogether with first content"""
    return [
        Paragraph(f'SECTION {num}', S_SECBADGE),
        Paragraph(title, S_H1),
        HR(PURPLE, 1.2),
        sp(2),
    ]


# ── Page template ─────────────────────────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(PURPLE)
    canvas.rect(0, H - 5, W, 5, fill=1, stroke=0)
    canvas.setFillColor(MUTED)
    canvas.setFont('Helvetica', 8)
    canvas.drawString(20*mm, 11*mm, 'Syntharra Global AI Solutions')
    canvas.drawRightString(W - 20*mm, 11*mm, f'Page {doc.page}')
    canvas.setFillColor(BORDER)
    canvas.rect(20*mm, 9.5*mm, W - 40*mm, 0.4, fill=1, stroke=0)
    canvas.restoreState()


# ── Build ─────────────────────────────────────────────────────────────
def build():
    out = '/mnt/user-data/outputs/Syntharra-Onboarding-Guide.pdf'
    doc = SimpleDocTemplate(
        out, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=20*mm, bottomMargin=20*mm,
        title='Syntharra — AI Receptionist Onboarding Guide',
        author='Syntharra Global AI Solutions',
    )

    story = []

    # ═══════════════════════════════════════════
    # COVER
    # ═══════════════════════════════════════════
    story.append(sp(14))

    # Logo — real PNG from disk
    logo_path = '/home/claude/syntharra-logo.png'
    logo_img = Image(logo_path, width=52, height=52)

    logo_name_tbl = Table([
        [
            logo_img,
            [
                Paragraph('Syntharra', S('ln', 'Helvetica-Bold', 22, DARK, leading=24)),
                Paragraph('GLOBAL AI SOLUTIONS', S('ls', 'Helvetica-Bold', 8, PURPLE, leading=10)),
            ]
        ]
    ], colWidths=[18*mm, COL_W - 18*mm])
    logo_name_tbl.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))

    cover_logo = Table([[logo_name_tbl]], colWidths=[COL_W])
    cover_logo.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(cover_logo)
    story.append(sp(10))

    # Title block
    title_data = [
        [Paragraph('AI Receptionist', S('ct1', 'Helvetica-Bold', 30, WHITE, leading=34, align=TA_CENTER))],
        [Paragraph('Onboarding Guide', S('ct2', 'Helvetica-Bold', 30, CYAN, leading=34, align=TA_CENTER))],
        [sp(3)],
        [Paragraph('Everything you need to get the most from your AI Receptionist',
                   S('cs', size=12, color=colors.HexColor('#C4C0FF'), leading=17, align=TA_CENTER))],
    ]
    title_tbl = Table(title_data, colWidths=[COL_W])
    title_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), DARK),
        ('ROUNDEDCORNERS', [10]),
        ('TOPPADDING', (0,0), (0,0), 30),
        ('TOPPADDING', (0,1), (0,1), 0),
        ('TOPPADDING', (0,2), (0,2), 6),
        ('TOPPADDING', (0,3), (0,3), 2),
        ('BOTTOMPADDING', (0,3), (-1,-1), 30),
        ('LEFTPADDING', (0,0), (-1,-1), 16),
        ('RIGHTPADDING', (0,0), (-1,-1), 16),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(title_tbl)
    story.append(sp(8))

    # Stat strip
    stat_tbl = Table([
        [
            Paragraph('24/7', S('sv', 'Helvetica-Bold', 20, PURPLE, leading=22, align=TA_CENTER)),
            Paragraph('475+', S('sv2', 'Helvetica-Bold', 20, PURPLE, leading=22, align=TA_CENTER)),
            Paragraph('<2s', S('sv3', 'Helvetica-Bold', 20, PURPLE, leading=22, align=TA_CENTER)),
        ],
        [
            Paragraph('Always answering', S('sl', size=8, color=MUTED, leading=10, align=TA_CENTER)),
            Paragraph('Minutes per month', S('sl2', size=8, color=MUTED, leading=10, align=TA_CENTER)),
            Paragraph('Answer time', S('sl3', size=8, color=MUTED, leading=10, align=TA_CENTER)),
        ]
    ], colWidths=[COL_W/3]*3)
    stat_tbl.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.3, BORDER),
        ('ROUNDEDCORNERS', [6]),
        ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(stat_tbl)
    story.append(sp(6))
    story.append(Paragraph('support@syntharra.com  ·  syntharra.com',
                            S('cf', size=9, color=MUTED, leading=12, align=TA_CENTER)))
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # TABLE OF CONTENTS
    # ═══════════════════════════════════════════
    story.append(KeepTogether([
        Paragraph('Contents', S('toc_h', 'Helvetica-Bold', 16, DARK, sb=0, sa=4)),
        HR(PURPLE, 1.5),
        sp(2),
    ]))

    toc = [
        ('1', 'Getting Started — Call Forwarding Setup',  '3'),
        ('2', 'How Your AI Receptionist Works',           '5'),
        ('3', 'Frequently Asked Questions',               '6'),
        ('4', 'Your Dashboard',                           '8'),
        ('5', 'Call Summaries & Notifications',           '9'),
        ('6', 'Making Changes to Your AI',               '10'),
        ('7', 'Minutes & Billing',                       '10'),
        ('8', 'Premium — Integrations Guide',            '11'),
        ('9', 'Getting Support',                         '12'),
    ]
    for num, title, pg in toc:
        row = Table([[Paragraph(f'<b>{num}.</b>  {title}', S_BODY),
                      Paragraph(pg, S('pgn', size=10, color=MUTED, leading=15, align=TA_LEFT))]],
                    colWidths=[COL_W - 14*mm, 14*mm])
        row.setStyle(TableStyle([
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LINEBELOW', (0,0), (-1,-1), 0.3, BORDER),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(row)
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # SECTION 1 — CALL FORWARDING
    # ═══════════════════════════════════════════
    story += section_start(1, 'Getting Started — Call Forwarding Setup')
    story.append(KeepTogether([
        Paragraph(
            'To route your calls through your AI Receptionist, forward your existing business phone '
            'number to your dedicated AI number. Takes under 2 minutes — pick whichever method suits your setup.',
            S_BODY),
        sp(3),
    ]))

    # Number box
    num_box = Table([
        [Paragraph('Your AI Receptionist Number',
                   S('nbl', 'Helvetica-Bold', 8, colors.HexColor('#C4C0FF'), leading=10, align=TA_CENTER))],
        [Paragraph('+1 (XXX) XXX-XXXX',
                   S('nbn', 'Helvetica-Bold', 18, WHITE, leading=22, align=TA_CENTER))],
    ], colWidths=[COL_W])
    num_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), DARK),
        ('ROUNDEDCORNERS', [8]),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (0,0), 14),
        ('TOPPADDING', (0,1), (0,1), 2),
        ('BOTTOMPADDING', (0,1), (-1,-1), 14),
        ('LEFTPADDING', (0,0), (-1,-1), 16),
        ('RIGHTPADDING', (0,0), (-1,-1), 16),
    ]))
    story.append(KeepTogether([num_box, sp(2),
        Paragraph('Your number is in your welcome email and at syntharra.com/dashboard',
                  S('hint', size=8, color=MUTED, leading=11, sa=6))]))

    # iPhone
    story.append(KeepTogether([
        Paragraph('iPhone (iOS)', S_H2),
        step_row(1, 'Open Settings', 'Tap the Settings icon on your home screen.'),
        step_row(2, 'Go to Phone → Call Forwarding', 'Scroll down and tap Phone, then tap Call Forwarding.'),
        step_row(3, 'Enable Call Forwarding', 'Toggle Call Forwarding to ON (green).'),
        step_row(4, 'Enter your AI number', 'Tap "Forward To" and type your dedicated AI Receptionist number.'),
        step_row(5, 'Done', 'Return to the previous screen. The number will now appear under Call Forwarding. '
                  'To cancel forwarding at any time, come back here and toggle it OFF.'),
        sp(3),
    ]))

    # Android
    story.append(KeepTogether([
        Paragraph('Android', S_H2),
        step_row(1, 'Open the Phone app', 'Tap the Phone/dialler icon on your home screen.'),
        step_row(2, 'Open Settings', 'Tap the ⋮ (three dots) menu in the top-right corner, then tap Settings.'),
        step_row(3, 'Find Call Forwarding', 'Tap Calls → Call Forwarding. Samsung users: Supplementary Services → Call Forwarding.'),
        step_row(4, 'Select Always Forward', 'Tap "Always Forward" and enter your AI Receptionist number.'),
        step_row(5, 'Confirm', 'Tap Enable or Turn On. A confirmation will appear when forwarding is active.'),
        sp(3),
    ]))

    # Carrier codes
    story.append(KeepTogether([
        Paragraph('Carrier Dial Codes (any phone)', S_H2),
        Paragraph('The fastest method — just dial the code from your keypad and press Call.', S_BODY),
        sp(2),
        dark_table(
            ['Carrier', 'Forward All Calls', 'Forward Unanswered', 'Cancel'],
            [
                ['AT&T, T-Mobile, Cricket, Mint, Google Fi, Metro', '**21*[AI number]#', '**61*[AI number]#', '##21#'],
                ['Verizon, Visible, Xfinity Mobile, Spectrum', '*72[AI number]', '*71[AI number]', '*73'],
                ['Landline (any carrier)', '*72 [AI number]', '*71 [AI number]', '*73'],
            ],
            [52*mm, 38*mm, 40*mm, 26*mm]
        ),
        sp(2),
        Paragraph('Replace [AI number] with your AI Receptionist number including country code (e.g. 18129944371).', S_MUTED),
        sp(3),
    ]))

    # VoIP — each provider kept together
    story.append(Paragraph('VoIP, Office Lines & Landlines', S_H2))
    voip = [
        ('RingCentral', 'Log in to admin portal → Phone System → Groups → Call Handling & Members → Add Rule → Forward calls to your AI number.'),
        ('Grasshopper', 'Log in → Settings → Forwarding Numbers → Add your AI number → Enable.'),
        ('Google Voice', 'voice.google.com → Settings (gear) → Calls → Forward to this number.'),
        ('Dialpad / 8x8 / Nextiva', 'Log in to your web portal → Settings → Call Routing → Forward all to AI number.'),
        ('Traditional Landline', 'Dial *72 followed by your AI number and press Call. Wait for the confirmation tone. To cancel, dial *73.'),
        ('PBX / Enterprise System', 'Contact your IT administrator and ask them to set unconditional call forwarding to your AI number. Most PBX systems support this from the admin console in under 5 minutes.'),
    ]
    for title, body in voip:
        story.append(KeepTogether([
            Paragraph(f'<b>{title}</b>', S('vt', 'Helvetica-Bold', 10, DARK, leading=14, sa=1)),
            Paragraph(body, S_BODY),
            HR(BORDER, 0.3),
        ]))

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # SECTION 2 — HOW IT WORKS
    # ═══════════════════════════════════════════
    story += section_start(2, 'How Your AI Receptionist Works')
    story.append(KeepTogether([
        Paragraph('Once call forwarding is set up, your AI handles every inbound call automatically. '
                  'Here\'s exactly what happens from the moment a customer dials your number.', S_BODY),
        sp(4),
    ]))

    flow = [
        ('1', 'Customer Dials Your Number', 'A customer calls your existing business phone number — nothing changes from their end.'),
        ('2', 'Call Forwards Instantly', 'Your carrier forwards the call to your dedicated AI Receptionist number in under a second.'),
        ('3', 'AI Answers Within 2 Seconds', 'Your AI Receptionist picks up, greets the caller, and begins handling their enquiry professionally.'),
        ('4', 'AI Handles the Conversation', 'The AI qualifies the call — identifies the job type, collects the address, '
              'determines urgency, answers FAQs, provides pricing guidance, and captures all relevant details.'),
        ('5', 'Live Transfer if Needed', 'If a caller requests to speak to someone directly, your AI will call your '
              'transfer number and connect the caller immediately.'),
        ('6', 'You Get a Full Summary', 'Immediately after the call, you receive an email with the full summary — '
              'caller name, number, address, job type, urgency, and all captured details.'),
        ('7', 'You Follow Up on Your Schedule', 'You return calls knowing exactly what the job is before you even pick up the phone.'),
    ]
    for n, t, b in flow:
        story.append(step_row(n, t, b))
    story.append(sp(4))

    # Transfer note
    transfer = Table([[
        [
            Paragraph('Live Transfer', S_WHITE_B),
            Paragraph('When a caller says "Can I speak to someone?" your AI will ring your transfer number. '
                      'If you answer, the caller is connected. If not, the AI takes a message.',
                      S_WHITE),
        ]
    ]], colWidths=[COL_W])
    transfer.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), DARK),
        ('ROUNDEDCORNERS', [8]),
        ('TOPPADDING', (0,0), (-1,-1), 14), ('BOTTOMPADDING', (0,0), (-1,-1), 14),
        ('LEFTPADDING', (0,0), (-1,-1), 16), ('RIGHTPADDING', (0,0), (-1,-1), 16),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(KeepTogether([transfer]))
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # SECTION 3 — FAQs
    # ═══════════════════════════════════════════
    story += section_start(3, 'Frequently Asked Questions')

    faq_sections = [
        ('General', [
            ('What if I haven\'t set up call forwarding yet?',
             'Your calls go to your normal phone/voicemail as usual. The AI only answers calls forwarded to your AI number.'),
            ('Will customers know they\'re speaking to an AI?',
             'Your AI sounds natural and professional. You can choose to have it disclose it\'s an AI, or simply position it as your receptionist. Most customers respond well and appreciate the quick, consistent service.'),
            ('What if my AI can\'t answer something?',
             'It politely takes the caller\'s details and lets them know someone will follow up. You\'ll still receive the full call summary — nothing falls through the cracks.'),
            ('Can the AI handle multiple calls at the same time?',
             'Yes — unlimited simultaneous calls. No busy signals, no queues, no missed calls — ever.'),
        ]),
        ('Calls & Notifications', [
            ('Where do missed calls go?',
             'There are no missed calls. Your AI answers every inbound call 24/7/365 — including holidays. You receive a full summary email after every call.'),
            ('What does the call summary email include?',
             'Caller name, phone number, date and time, job type, property address, urgency level, key details from the conversation, and any specific requests made.'),
            ('How quickly do I get notified after a call?',
             'Typically within 30–60 seconds of the call ending.'),
            ('Can I add more email addresses to receive summaries?',
             'Yes — up to 3 email addresses and 3 SMS numbers. Email support@syntharra.com with the addresses to add.'),
        ]),
        ('Call Forwarding', [
            ('Do I need to keep call forwarding on all the time?',
             'Yes, while you want the AI answering calls. To take calls yourself during certain hours, use conditional forwarding (forward only when unanswered) using the carrier codes in Section 1.'),
            ('Will forwarding affect my voicemail?',
             'Unconditional forwarding bypasses your carrier voicemail — your AI answers instead. To keep voicemail as a fallback, use "forward when unanswered" codes.'),
            ('What does call forwarding cost?',
             'Forwarding is typically free or very low cost on most plans. Check with your carrier if unsure.'),
            ('Can I pause forwarding temporarily?',
             'Yes — cancel using the carrier code (*73 on most carriers, ##21# on GSM) or toggle it off in phone settings. Your AI number stays active and will reactivate when forwarding is turned back on.'),
        ]),
    ]

    for sec_title, items in faq_sections:
        story.append(KeepTogether([
            sp(2),
            Paragraph(sec_title, S('faq_sec', 'Helvetica-Bold', 10, PURPLE, leading=14, sa=2)),
            HR(LIGHT_P, 1),
        ]))
        for q, a in items:
            story.append(faq_item(q, a))

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # SECTION 4 — DASHBOARD
    # ═══════════════════════════════════════════
    story += section_start(4, 'Your Dashboard')
    story.append(KeepTogether([
        Paragraph('Your live dashboard gives you a real-time view of every call, lead, and your AI\'s activity. '
                  'Access it any time from any device.', S_BODY),
        sp(3),
        Paragraph('How to Access', S_H2),
        Paragraph('Your dashboard link is included in your welcome email. You can also access it directly at:', S_BODY),
        sp(1),
    ]))

    code_box = Table([[Paragraph('https://syntharra.com/dashboard.html?agent_id=YOUR_AGENT_ID', S_CODE)]],
                     colWidths=[COL_W])
    code_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_P),
        ('ROUNDEDCORNERS', [4]),
        ('TOPPADDING', (0,0), (-1,-1), 7), ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 10), ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(KeepTogether([code_box, sp(2),
        Paragraph('Your agent ID is unique to your account and is included in your welcome email.', S_MUTED)]))

    story.append(sp(3))
    story.append(Paragraph('What You\'ll See', S_H2))
    dash_items = [
        ('Call Log', 'Every call listed chronologically with caller, time, job type, urgency, and a link to the full summary.'),
        ('Call Summaries', 'Click any call to read the AI-generated summary with all captured details.'),
        ('Usage Stats', 'Minutes used this billing cycle and your remaining balance.'),
        ('Agent Status', 'Confirm your AI Receptionist is online and active.'),
        ('Weekly Trend', 'Rolling chart of call volume over the past 4 weeks.'),
    ]
    for title, desc in dash_items:
        story.append(KeepTogether([
            Paragraph(f'<b>{title}</b> — {desc}', S_BODY),
            sp(1),
        ]))

    story.append(sp(4))

    # ═══════════════════════════════════════════
    # SECTION 5 — NOTIFICATIONS
    # ═══════════════════════════════════════════
    story.append(KeepTogether(section_start(5, 'Call Summaries & Notifications') + [
        Paragraph('After every call, Syntharra sends you a full summary so you can follow up intelligently.', S_BODY),
        sp(3),
    ]))

    story.append(KeepTogether([
        Paragraph('What\'s in Each Summary Email', S_H2),
        Paragraph('• 📞 Caller name and phone number', S_BODY),
        Paragraph('• 📍 Property address (if provided)', S_BODY),
        Paragraph('• 🔧 Job type and service category', S_BODY),
        Paragraph('• ⚡ Urgency level (Emergency / Urgent / Standard)', S_BODY),
        Paragraph('• 📝 Key details from the conversation', S_BODY),
        Paragraph('• 💬 Notable requests or information volunteered by the caller', S_BODY),
        Paragraph('• 🕐 Date, time and call duration', S_BODY),
        sp(3),
    ]))

    story.append(KeepTogether([
        Paragraph('Weekly Report', S_H2),
        Paragraph('Every Sunday at 6pm in your local timezone, you\'ll receive a weekly summary covering '
                  'the past 7 days — total calls, job type breakdown, top service requests, and any trends worth noting.',
                  S_BODY),
        sp(4),
    ]))

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # SECTION 6 — MAKING CHANGES
    # ═══════════════════════════════════════════
    story += section_start(6, 'Making Changes to Your AI')
    story.append(KeepTogether([
        Paragraph('Your AI Receptionist is configured from your onboarding form. As your business evolves, '
                  'we can update it any time.', S_BODY),
        sp(3),
        Paragraph('What You Can Update', S_H2),
    ]))

    changes = [
        'Business hours and after-hours behaviour',
        'Services offered, pricing policy, and promotions',
        'Service area or coverage radius',
        'Diagnostic fees and standard pricing',
        'Transfer number (who calls are transferred to)',
        'Notification email addresses and SMS numbers',
        'Custom greeting or agent name',
        'Warranty terms, payment methods, financing details',
        'Seasonal services and membership programs',
    ]
    story.append(KeepTogether([Paragraph(f'• {c}', S_BODY) for c in changes] + [sp(3)]))

    story.append(KeepTogether([
        Paragraph('How to Request Changes', S_H2),
        Paragraph('Email <b>support@syntharra.com</b> with your change request. Most changes are live within 24 hours.', S_BODY),
        sp(2),
    ]))

    tip = Table([[Paragraph(
        '<b>Pro tip:</b> If you\'re launching a promotion or changing pricing, email us 24 hours '
        'before you want it live so your AI is updated in time.', S_BODY)]],
        colWidths=[COL_W])
    tip.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_P),
        ('ROUNDEDCORNERS', [6]),
        ('BOX', (0,0), (-1,-1), 0.5, PURPLE),
        ('TOPPADDING', (0,0), (-1,-1), 10), ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 14), ('RIGHTPADDING', (0,0), (-1,-1), 14),
    ]))
    story.append(KeepTogether([tip, sp(4)]))

    # ═══════════════════════════════════════════
    # SECTION 7 — MINUTES & BILLING
    # ═══════════════════════════════════════════
    story.append(KeepTogether(section_start(7, 'Minutes & Billing') + [
        Paragraph('How Minutes Work', S_H2),
        Paragraph('Your plan includes a monthly allocation of AI talk minutes. Only the time your AI '
                  'actively spends speaking with callers counts toward your usage.', S_BODY),
        sp(2),
        dark_table(
            ['Plan', 'Monthly Minutes', 'What Counts'],
            [
                ['Standard', '475 minutes', 'AI talk time only'],
                ['Premium', '1,000 minutes', 'AI talk time only'],
            ],
            [55*mm, 55*mm, 60*mm]
        ),
        sp(3),
    ]))

    story.append(KeepTogether([
        Paragraph('Usage Alerts', S_H2),
        Paragraph('You\'ll receive an email alert at <b>80% usage</b> and again at <b>100%</b>. '
                  'Your AI never stops answering — calls continue even if you exceed your allocation.', S_BODY),
        sp(2),
        Paragraph('Overages', S_H2),
        Paragraph('Overage minutes are billed at a low per-minute rate at the end of your billing cycle. '
                  'Usage resets on your billing anniversary date.', S_BODY),
        sp(4),
    ]))

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # SECTION 8 — PREMIUM INTEGRATIONS
    # ═══════════════════════════════════════════
    story += section_start(8, 'Premium — Integrations Guide')

    prem_note = Table([[Paragraph('Premium Plan Only', S('pb', 'Helvetica-Bold', 8, WHITE, leading=10, align=TA_CENTER))]],
                       colWidths=[COL_W])
    prem_note.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), PURPLE),
        ('ROUNDEDCORNERS', [4]),
        ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(KeepTogether([
        prem_note, sp(3),
        Paragraph('Premium clients connect their calendar and CRM so that job bookings and customer details '
                  'flow directly into your systems — no manual data entry required.', S_BODY),
        sp(3),
    ]))

    story.append(KeepTogether([
        Paragraph('Google Calendar Integration', S_H2),
        Paragraph('Once connected, your AI checks your Google Calendar in real time before confirming '
                  'appointment slots. Bookings are added automatically.', S_BODY),
        sp(2),
        step_row(1, 'Receive the integration setup email', 'A separate email with a one-click authorisation link is sent shortly after your welcome email.'),
        step_row(2, 'Click Authorise', 'Log in to the Google account you want to use for bookings.'),
        step_row(3, 'Grant permissions', 'Allow Syntharra to view and create calendar events. Read/write to your calendar only — no other Google data is accessed.'),
        step_row(4, 'Done', 'Your AI will now check your real availability and book appointments directly into your calendar.'),
        sp(3),
    ]))

    story.append(KeepTogether([
        Paragraph('CRM Integration (Jobber & others)', S_H2),
        Paragraph('New callers are automatically created as customers and job requests are logged in your CRM.', S_BODY),
        sp(2),
        step_row(1, 'Receive the integration setup email', 'Same email as above — contains authorisation links for both calendar and CRM.'),
        step_row(2, 'Click Authorise for your CRM', 'Click the Jobber (or other CRM) link and log in to your account.'),
        step_row(3, 'Grant permissions', 'Authorise Syntharra to create clients and jobs. No billing or financial data is accessed.'),
        step_row(4, 'Done', 'Every call that generates a lead will automatically create a record in your CRM.'),
        sp(3),
    ]))

    story.append(KeepTogether([
        Paragraph('Repeat Caller Recognition', S_H2),
        Paragraph('Premium clients benefit from intelligent repeat caller detection. When a customer calls more '
                  'than once, your AI recognises them by phone number, greets them by name, and references '
                  'their call history for a personalised experience.', S_BODY),
        sp(4),
    ]))

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # SECTION 9 — SUPPORT
    # ═══════════════════════════════════════════
    story += section_start(9, 'Getting Support')
    story.append(KeepTogether([
        Paragraph('We\'re here whenever you need us. For most queries, email is the fastest route.', S_BODY),
        sp(3),
        dark_table(
            ['Contact', 'Best For', 'Response Time'],
            [
                ['support@syntharra.com', 'Changes, billing, technical issues, all queries', 'Within a few hours'],
                ['syntharra.com/dashboard', 'View calls, usage, agent status', 'Live'],
            ],
            [60*mm, 72*mm, 38*mm]
        ),
        sp(3),
    ]))

    story.append(Paragraph('Quick Reference — Common Requests', S_H2))
    common = [
        ('"I want to update my business hours"', 'Email support@syntharra.com with your new hours'),
        ('"I want to add another notification email"', 'Email support@syntharra.com with the address'),
        ('"My AI said something incorrect"', 'Email support@syntharra.com with the call time and what was said'),
        ('"I want to pause the service temporarily"', 'Email support@syntharra.com — we can suspend and reactivate'),
        ('"I want to cancel my subscription"', 'Email support@syntharra.com with at least 30 days notice'),
        ('"I need help with call forwarding"', 'Refer to Section 1, or email support@syntharra.com'),
    ]
    for req, action in common:
        story.append(KeepTogether([
            Paragraph(f'<b>{req}</b>', S('crq', 'Helvetica-Bold', 10, DARK, leading=14, sa=1)),
            Paragraph(f'→ {action}', S_BODY),
            HR(BORDER, 0.3),
        ]))

    story.append(sp(6))

    # Final card
    footer_card = Table([[
        [
            Paragraph('Syntharra', S('fcn', 'Helvetica-Bold', 16, WHITE, leading=18, align=TA_CENTER, sa=2)),
            Paragraph('GLOBAL AI SOLUTIONS', S('fcs', 'Helvetica-Bold', 7, CYAN, leading=9, align=TA_CENTER, sa=6)),
            Paragraph('support@syntharra.com', S('fce', size=10, color=colors.HexColor('#C4C0FF'), leading=14, align=TA_CENTER, sa=2)),
            Paragraph('syntharra.com', S('fcw', size=10, color=CYAN, leading=14, align=TA_CENTER)),
        ]
    ]], colWidths=[COL_W])
    footer_card.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), DARK),
        ('ROUNDEDCORNERS', [10]),
        ('TOPPADDING', (0,0), (-1,-1), 22),
        ('BOTTOMPADDING', (0,0), (-1,-1), 22),
        ('LEFTPADDING', (0,0), (-1,-1), 20),
        ('RIGHTPADDING', (0,0), (-1,-1), 20),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(KeepTogether([footer_card]))

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f'✅ PDF saved to {out}')


if __name__ == '__main__':
    build()
