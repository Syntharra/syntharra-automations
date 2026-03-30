"""
Syntharra — Client Onboarding FAQ & How-To Guide PDF
Brand: #6C63FF purple, #00D4FF cyan, #1A1A2E dark, #F7F7FB light bg
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, KeepTogether, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus.flowables import Flowable
import urllib.request, io

W, H = A4

# ── Colours ──────────────────────────────────────────────────────────
PURPLE   = colors.HexColor('#6C63FF')
CYAN     = colors.HexColor('#00D4FF')
DARK     = colors.HexColor('#1A1A2E')
GREY_BG  = colors.HexColor('#F7F7FB')
CARD_BG  = colors.HexColor('#FFFFFF')
MUTED    = colors.HexColor('#6B7280')
BORDER   = colors.HexColor('#E5E7EB')
ORANGE   = colors.HexColor('#F59E0B')
GREEN    = colors.HexColor('#10B981')
LIGHT_P  = colors.HexColor('#F3F0FF')
WHITE    = colors.white

# ── Styles ────────────────────────────────────────────────────────────
def style(name, font='Helvetica', size=10, color=DARK, leading=None,
          align=TA_LEFT, space_before=0, space_after=0, bold=False):
    f = font + '-Bold' if bold else font
    return ParagraphStyle(
        name, fontName=f, fontSize=size, textColor=color,
        leading=leading or size * 1.4,
        alignment=align,
        spaceAfter=space_after, spaceBefore=space_before,
        wordWrap='CJK'
    )

S_TITLE     = style('title',  'Helvetica-Bold', 26, DARK,   leading=30, align=TA_CENTER, space_after=4)
S_SUBTITLE  = style('sub',    'Helvetica',      12, MUTED,  leading=16, align=TA_CENTER, space_after=0)
S_H1        = style('h1',     'Helvetica-Bold', 15, DARK,   leading=20, space_before=6, space_after=4)
S_H2        = style('h2',     'Helvetica-Bold', 11, PURPLE, leading=15, space_before=4, space_after=2)
S_BODY      = style('body',   'Helvetica',      10, DARK,   leading=15, space_after=3)
S_MUTED     = style('muted',  'Helvetica',       9, MUTED,  leading=13, space_after=2)
S_CODE      = style('code',   'Courier',        10, PURPLE, leading=14, space_after=2)
S_STEP_NUM  = style('stepn',  'Helvetica-Bold', 11, WHITE,  leading=14, align=TA_CENTER)
S_LABEL     = style('label',  'Helvetica-Bold',  8, MUTED,  leading=11,
                    space_after=1)
S_CAPTION   = style('capt',   'Helvetica',       8, MUTED,  leading=11, align=TA_CENTER)
S_WHITE_SML = style('wsml',   'Helvetica',       9, WHITE,  leading=12, space_after=2)
S_WHITE_H   = style('wh',     'Helvetica-Bold', 11, WHITE,  leading=15)
S_SECTION_BADGE = style('badge','Helvetica-Bold',8, PURPLE, leading=10,
                         space_after=4)

def HR(color=BORDER, thickness=0.5):
    return HRFlowable(width='100%', thickness=thickness, color=color,
                      spaceAfter=6, spaceBefore=6)

def sp(h=4):
    return Spacer(1, h * mm)


# ── Coloured round step badge ─────────────────────────────────────────
class StepBadge(Flowable):
    def __init__(self, number, size=18):
        super().__init__()
        self.number = str(number)
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
        c.drawCentredString(r, r - self.size * 0.17, self.number)


class IconBadge(Flowable):
    """Small coloured square icon for section headers"""
    def __init__(self, emoji_char, size=24, bg=LIGHT_P):
        super().__init__()
        self.emoji = emoji_char
        self.size = size
        self.bg = bg
        self.width = size
        self.height = size

    def draw(self):
        c = self.canv
        c.setFillColor(self.bg)
        c.roundRect(0, 0, self.size, self.size, 4, fill=1, stroke=0)
        c.setFillColor(DARK)
        c.setFont('Helvetica', self.size * 0.55)
        c.drawCentredString(self.size / 2, self.size * 0.2, self.emoji)


def section_card(content_rows, bg=GREY_BG, radius=6, border_color=None):
    """Wrap content in a rounded card table"""
    t = Table([[content_rows]], colWidths=[155 * mm])
    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, -1), bg),
        ('ROUNDEDCORNERS', [radius], ),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]
    if border_color:
        style_cmds.append(('BOX', (0, 0), (-1, -1), 0.5, border_color))
    t.setStyle(TableStyle(style_cmds))
    return t


def left_border_card(items, border_color=PURPLE, bg=GREY_BG):
    """Card with left colour border accent"""
    content = Table([[items]], colWidths=[150 * mm])
    content.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    outer = Table(
        [[ Table([['']], colWidths=[3], rowHeights=[None]),  content ]],
        colWidths=[3, 153 * mm]
    )
    outer.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), border_color),
        ('BACKGROUND', (1, 0), (1, -1), bg),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
        ('ROUNDEDCORNERS', [4]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (0, -1), 0),
        ('RIGHTPADDING', (0, 0), (0, -1), 0),
    ]))
    return outer


def faq_block(question, answer):
    return KeepTogether([
        Paragraph(question, style('fq', 'Helvetica-Bold', 10, DARK, leading=14, space_before=2, space_after=1)),
        Paragraph(answer, S_BODY),
        HR(BORDER, 0.4),
    ])


def step_row(number, title, body):
    badge_cell = Table([[StepBadge(number)]], colWidths=[8 * mm])
    badge_cell.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    text_cell = [
        Paragraph(title, style('st', 'Helvetica-Bold', 10, DARK, leading=14, space_after=1)),
        Paragraph(body, S_BODY),
    ]
    row = Table([[badge_cell, text_cell]], colWidths=[10 * mm, 148 * mm])
    row.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    return row


def code_pill(text):
    t = Table([[Paragraph(text, S_CODE)]], colWidths=[155 * mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F3F0FF')),
        ('ROUNDEDCORNERS', [4]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    return t


def dark_table(headers, rows, col_widths):
    data = [[Paragraph(h, style('th', 'Helvetica-Bold', 9, WHITE, leading=12)) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), style('td', 'Helvetica', 9, DARK, leading=13)) for c in row])
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK),
        ('BACKGROUND', (0, 1), (-1, -1), CARD_BG),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [CARD_BG, GREY_BG]),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.3, BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROUNDEDCORNERS', [4]),
    ]))
    return t


# ── Page template (header/footer) ─────────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    # Top bar
    canvas.setFillColor(PURPLE)
    canvas.rect(0, H - 6, W, 6, fill=1, stroke=0)
    # Footer
    canvas.setFillColor(MUTED)
    canvas.setFont('Helvetica', 8)
    canvas.drawString(20 * mm, 12 * mm, 'Syntharra Global AI Solutions')
    canvas.drawRightString(W - 20 * mm, 12 * mm, f'Page {doc.page}')
    canvas.setFillColor(BORDER)
    canvas.rect(20 * mm, 10 * mm, W - 40 * mm, 0.5, fill=1, stroke=0)
    canvas.restoreState()


# ── Build PDF ─────────────────────────────────────────────────────────
def build():
    output = '/mnt/user-data/outputs/Syntharra-Onboarding-Guide.pdf'
    doc = SimpleDocTemplate(
        output,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=22 * mm,
        bottomMargin=22 * mm,
        title='Syntharra — AI Receptionist Onboarding Guide',
        author='Syntharra Global AI Solutions',
    )

    story = []

    # ═══════════════════════════════════════════════════════════════════
    # COVER PAGE
    # ═══════════════════════════════════════════════════════════════════
    story.append(sp(20))

    # Logo text (no image dependency)
    logo_tbl = Table([
        [
            Paragraph('Syntharra', style('logoname', 'Helvetica-Bold', 22, DARK, leading=24, align=TA_CENTER)),
        ],
        [
            Paragraph('GLOBAL AI SOLUTIONS', style('logsub', 'Helvetica-Bold', 8, PURPLE, leading=10,
                       align=TA_CENTER, space_after=0)),
        ]
    ], colWidths=[155 * mm])
    logo_tbl.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(logo_tbl)
    story.append(sp(10))

    # Title bar
    title_bg = Table([
        [Paragraph('AI Receptionist', style('ct1', 'Helvetica-Bold', 28, WHITE, leading=32, align=TA_CENTER))],
        [Paragraph('Onboarding Guide', style('ct2', 'Helvetica-Bold', 28, CYAN, leading=32, align=TA_CENTER))],
        [sp(2)],
        [Paragraph('Everything you need to get the most from your AI Receptionist',
                   style('cs', 'Helvetica', 11, colors.HexColor('#C4C0FF'), leading=15, align=TA_CENTER))],
    ], colWidths=[155 * mm])
    title_bg.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK),
        ('ROUNDEDCORNERS', [10]),
        ('TOPPADDING', (0, 0), (-1, 0), 28),
        ('TOPPADDING', (0, 1), (-1, 1), 0),
        ('TOPPADDING', (0, 2), (-1, 2), 8),
        ('TOPPADDING', (0, 3), (-1, 3), 4),
        ('BOTTOMPADDING', (0, 3), (-1, -1), 28),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(title_bg)
    story.append(sp(8))

    # 3-col stat strip
    stat_tbl = Table([
        [
            Paragraph('24/7', style('sv', 'Helvetica-Bold', 18, PURPLE, leading=20, align=TA_CENTER)),
            Paragraph('475+', style('sv2', 'Helvetica-Bold', 18, PURPLE, leading=20, align=TA_CENTER)),
            Paragraph('<2s', style('sv3', 'Helvetica-Bold', 18, PURPLE, leading=20, align=TA_CENTER)),
        ],
        [
            Paragraph('Always answering', style('sl', 'Helvetica', 8, MUTED, leading=10, align=TA_CENTER)),
            Paragraph('Minutes per month', style('sl2', 'Helvetica', 8, MUTED, leading=10, align=TA_CENTER)),
            Paragraph('Answer time', style('sl3', 'Helvetica', 8, MUTED, leading=10, align=TA_CENTER)),
        ]
    ], colWidths=[51 * mm, 51 * mm, 53 * mm])
    stat_tbl.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.3, BORDER),
        ('ROUNDEDCORNERS', [6]),
        ('BACKGROUND', (0, 0), (-1, -1), CARD_BG),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(stat_tbl)
    story.append(sp(6))

    story.append(Paragraph(
        'support@syntharra.com  ·  syntharra.com',
        style('cover_foot', 'Helvetica', 9, MUTED, leading=12, align=TA_CENTER)
    ))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════
    # TABLE OF CONTENTS
    # ═══════════════════════════════════════════════════════════════════
    story.append(Paragraph('Contents', style('toc_title', 'Helvetica-Bold', 16, DARK, leading=20, space_after=4)))
    story.append(HR(PURPLE, 1.5))
    story.append(sp(2))

    toc_items = [
        ('1', 'Getting Started — Call Forwarding Setup',  '3'),
        ('2', 'How Your AI Receptionist Works',           '5'),
        ('3', 'Frequently Asked Questions',               '6'),
        ('4', 'Your Dashboard',                           '8'),
        ('5', 'Call Summaries & Notifications',           '9'),
        ('6', 'Making Changes to Your AI',               '9'),
        ('7', 'Minutes & Billing',                       '10'),
        ('8', 'Premium — Integrations Guide',            '11'),
        ('9', 'Getting Support',                         '12'),
    ]
    for num, title, pg in toc_items:
        row = Table([
            [
                Paragraph(f'<b>{num}.</b> {title}', S_BODY),
                Paragraph(pg, style('pgn', 'Helvetica', 10, MUTED, leading=15, align=TA_LEFT)),
            ]
        ], colWidths=[140 * mm, 15 * mm])
        row.setStyle(TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LINEBELOW', (0, 0), (-1, -1), 0.3, BORDER),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(row)

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════
    # SECTION 1 — CALL FORWARDING
    # ═══════════════════════════════════════════════════════════════════
    story.append(Paragraph('SECTION 1', style('secbadge', 'Helvetica-Bold', 8, PURPLE,
                                               leading=10, space_after=2)))
    story.append(Paragraph('Getting Started — Call Forwarding Setup', S_H1))
    story.append(HR(PURPLE, 1))
    story.append(sp(2))
    story.append(Paragraph(
        'To route your incoming calls through your AI Receptionist, you need to forward your existing business '
        'phone number to your dedicated AI number. This takes under 2 minutes. Pick whichever method matches your setup.',
        S_BODY))
    story.append(sp(3))

    # Number display box
    num_box = Table([[
        Paragraph('Your AI Receptionist Number', style('nb_l', 'Helvetica-Bold', 8,
                   colors.HexColor('#C4C0FF'), leading=10, align=TA_CENTER, space_after=2)),
        Paragraph('+1 (XXX) XXX-XXXX', style('nb_n', 'Helvetica-Bold', 16, WHITE,
                  leading=18, align=TA_CENTER)),
    ]], colWidths=[155 * mm])
    num_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK),
        ('ROUNDEDCORNERS', [8]),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (0, 0), 14),
        ('TOPPADDING', (0, 1), (0, 1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 14),
        ('LEFTPADDING', (0, 0), (-1, -1), 16),
        ('RIGHTPADDING', (0, 0), (-1, -1), 16),
        ('SPAN', (0, 0), (-1, 0)),
        ('SPAN', (0, 1), (-1, 1)),
    ]))
    story.append(num_box)
    story.append(sp(3))

    story.append(Paragraph(
        'Your number is shown in the welcome email and your dashboard at syntharra.com/dashboard',
        style('hint', 'Helvetica', 8, MUTED, leading=11, space_after=6)
    ))

    # iPhone
    story.append(Paragraph('iPhone (iOS)', S_H2))
    story.append(step_row(1, 'Open Settings', 'Tap the Settings icon on your home screen.'))
    story.append(step_row(2, 'Go to Phone → Call Forwarding',
                          'Scroll down and tap Phone, then tap Call Forwarding.'))
    story.append(step_row(3, 'Enable Call Forwarding',
                          'Toggle Call Forwarding to ON (green).'))
    story.append(step_row(4, 'Enter your AI number',
                          'Tap "Forward To" and type your dedicated AI Receptionist number.'))
    story.append(step_row(5, 'Done',
                          'Return to the previous screen — the number will now appear under Call Forwarding. '
                          'You\'re live. To cancel, come back here and toggle it OFF.'))
    story.append(sp(3))

    # Android
    story.append(Paragraph('Android', S_H2))
    story.append(step_row(1, 'Open the Phone app',
                          'Tap the Phone/dialler icon on your home screen.'))
    story.append(step_row(2, 'Open Settings',
                          'Tap the ⋮ (three dots) menu in the top-right corner, then tap Settings.'))
    story.append(step_row(3, 'Find Call Forwarding',
                          'Tap Calls → Call Forwarding. On Samsung: Supplementary Services → Call Forwarding.'))
    story.append(step_row(4, 'Select Always Forward',
                          'Tap "Always Forward" and enter your AI Receptionist number.'))
    story.append(step_row(5, 'Confirm',
                          'Tap Enable or Turn On. A confirmation will appear when forwarding is active.'))
    story.append(sp(3))

    # Carrier codes
    story.append(Paragraph('Carrier Dial Codes (any phone)', S_H2))
    story.append(Paragraph(
        'The fastest method on most phones — just dial the code from your keypad and press Call.',
        S_BODY))
    story.append(sp(2))

    carrier_data = dark_table(
        ['Carrier', 'Forward All Calls', 'Forward When Unanswered', 'Cancel Forwarding'],
        [
            ['AT&T, T-Mobile, Cricket,\nMint, Google Fi, Metro', '**21*[AI number]#', '**61*[AI number]#', '##21#'],
            ['Verizon, Visible,\nXfinity Mobile, Spectrum', '*72[AI number]', '*71[AI number]', '*73'],
            ['Landline (any carrier)',  '*72 [AI number]', '*71 [AI number]', '*73'],
        ],
        [42 * mm, 37 * mm, 42 * mm, 34 * mm]
    )
    story.append(carrier_data)
    story.append(sp(2))
    story.append(Paragraph(
        'Replace [AI number] with your dedicated AI Receptionist number including country code (e.g. 18129944371).',
        S_MUTED))
    story.append(sp(3))

    # VoIP / Office
    story.append(Paragraph('VoIP, Office Lines & Landlines', S_H2))

    voip_items = [
        ('RingCentral', 'Log in to admin portal → Phone System → Groups → Call Handling & Members → '
                        'Add Rule → Forward calls to your AI number.'),
        ('Grasshopper', 'Log in → Settings → Forwarding Numbers → Add your AI number → Enable.'),
        ('Google Voice', 'voice.google.com → Settings (gear) → Calls → Forward to this number.'),
        ('Dialpad / 8x8 / Nextiva', 'Log in to your web portal → Settings → Call Routing → Forward all to AI number.'),
        ('Traditional Landline', 'Dial *72 followed by your AI number and press Call. '
                                  'Wait for confirmation tone. To cancel, dial *73.'),
        ('PBX / Enterprise System', 'Contact your IT administrator and ask them to set unconditional call '
                                     'forwarding to your AI number. Most PBX systems support this from '
                                     'the admin console in under 5 minutes.'),
    ]
    for title, body in voip_items:
        story.append(KeepTogether([
            Paragraph(f'<b>{title}</b>', style('vt', 'Helvetica-Bold', 10, DARK, leading=14, space_after=1)),
            Paragraph(body, S_BODY),
            HR(BORDER, 0.3),
        ]))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════
    # SECTION 2 — HOW IT WORKS
    # ═══════════════════════════════════════════════════════════════════
    story.append(Paragraph('SECTION 2', style('secbadge', 'Helvetica-Bold', 8, PURPLE, leading=10, space_after=2)))
    story.append(Paragraph('How Your AI Receptionist Works', S_H1))
    story.append(HR(PURPLE, 1))
    story.append(sp(2))
    story.append(Paragraph(
        'Once call forwarding is set up, your AI handles every inbound call automatically. Here\'s exactly '
        'what happens from the moment a customer dials your number.',
        S_BODY))
    story.append(sp(4))

    flow_steps = [
        ('1', 'Customer Dials Your Number',
         'A customer calls your existing business phone number — nothing changes from their end.'),
        ('2', 'Call Forwards Instantly',
         'Your carrier forwards the call to your dedicated AI Receptionist number in under a second.'),
        ('3', 'AI Answers Within 2 Seconds',
         'Your AI Receptionist picks up, greets the caller by name (if a returning caller), '
         'and begins handling their enquiry professionally.'),
        ('4', 'AI Handles the Conversation',
         'The AI qualifies the call — identifies the job type, collects the customer\'s address, '
         'determines urgency, answers FAQs, provides pricing guidance, and captures all relevant details.'),
        ('5', 'Live Transfer if Needed',
         'If a caller requests to speak to someone directly, or if the AI determines an urgent '
         'live transfer is needed, it will call your transfer number and connect the caller immediately.'),
        ('6', 'You Get a Full Summary',
         'Immediately after the call ends, you receive an email with the complete call summary — '
         'caller name, number, address, job type, urgency level, and any notes captured.'),
        ('7', 'You Follow Up on Your Schedule',
         'You return calls knowing exactly what the job is, what was discussed, and how urgent '
         'it is — before you even pick up the phone.'),
    ]
    for num, title, body in flow_steps:
        story.append(step_row(num, title, body))
        story.append(sp(1))

    story.append(sp(4))

    # Live Transfer box
    transfer_box = Table([[
        [
            Paragraph('Live Transfer', style('lt_t', 'Helvetica-Bold', 11, WHITE, leading=14, space_after=3)),
            Paragraph(
                'When a caller says "Can I speak to someone?" or the AI determines the call needs '
                'immediate human attention, it will ring your transfer number. If you answer, the '
                'caller is connected. If you don\'t, the AI continues and takes a message.',
                S_WHITE_SML),
        ]
    ]], colWidths=[155 * mm])
    transfer_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK),
        ('ROUNDEDCORNERS', [8]),
        ('TOPPADDING', (0, 0), (-1, -1), 16),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 16),
        ('LEFTPADDING', (0, 0), (-1, -1), 16),
        ('RIGHTPADDING', (0, 0), (-1, -1), 16),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(transfer_box)

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════
    # SECTION 3 — FAQs
    # ═══════════════════════════════════════════════════════════════════
    story.append(Paragraph('SECTION 3', style('secbadge', 'Helvetica-Bold', 8, PURPLE, leading=10, space_after=2)))
    story.append(Paragraph('Frequently Asked Questions', S_H1))
    story.append(HR(PURPLE, 1))
    story.append(sp(2))

    faqs = [
        ('General'),
        ('What if a customer calls and I haven\'t set up forwarding yet?',
         'Your calls will go to your normal phone/voicemail as usual. The AI only answers calls that have been '
         'forwarded to your AI number. Set up forwarding first — it takes under 2 minutes.'),
        ('Will customers know they\'re speaking to an AI?',
         'Your AI Receptionist is designed to sound natural and professional. You can choose to have it '
         'disclose that it\'s an AI assistant, or position it simply as your receptionist. We recommend '
         'transparency — most customers respond well to it and appreciate the quick, consistent service.'),
        ('What happens if my AI doesn\'t know how to answer something?',
         'If a question falls outside its knowledge, the AI will politely let the caller know that someone '
         'will follow up with them, take their details, and end the call professionally. Nothing falls '
         'through the cracks — you\'ll still receive the full call summary.'),
        ('Can the AI handle multiple calls at the same time?',
         'Yes. Your AI Receptionist can handle unlimited simultaneous calls. No busy signals, no queues, '
         'no missed calls — ever.'),
        ('What languages does the AI speak?',
         'Your AI is configured in English by default. If you need additional language support, '
         'contact support@syntharra.com and we can discuss options.'),

        ('Calls & Notifications'),
        ('Where do missed calls go?',
         'There are no missed calls. Your AI answers every inbound call 24 hours a day, 7 days a week, '
         '365 days a year — including holidays. You will receive a full summary email after every call.'),
        ('What does the call summary email include?',
         'Each summary includes: caller name, caller phone number, date and time, job type, property '
         'address, urgency level, key details from the conversation, and any specific requests made. '
         'Premium clients also get AI-generated analysis of the lead quality.'),
        ('How quickly do I get notified after a call?',
         'Typically within 30 to 60 seconds of the call ending. The AI processes the transcript, '
         'extracts the key data, and sends the summary email almost immediately.'),
        ('Can I add additional email addresses to receive call summaries?',
         'Yes. You can have up to 3 email addresses and 3 SMS numbers receiving call notifications. '
         'Email support@syntharra.com with the addresses you want to add.'),
        ('What if a caller hangs up immediately?',
         'Very short calls (under 10 seconds) are typically missed calls or wrong numbers and do not '
         'generate a summary. Calls with meaningful conversation always generate a full summary.'),

        ('Call Forwarding'),
        ('Do I need to keep call forwarding on all the time?',
         'Yes, while you want the AI to answer your calls. If you want to take calls yourself during '
         'certain hours (e.g. during business hours), you can set up conditional forwarding — '
         'forwarding only when unanswered — using the carrier codes in Section 1.'),
        ('Will forwarding affect my existing voicemail?',
         'When you activate unconditional forwarding (forward all calls), your carrier voicemail is '
         'bypassed — your AI answers instead. This is the recommended setup. If you prefer to keep '
         'your voicemail as a fallback, use "forward when unanswered" codes instead.'),
        ('What does call forwarding cost?',
         'Forwarding itself is typically free or very low cost on most mobile and landline plans. '
         'Check with your carrier if you\'re unsure. The calls you receive on your AI number are '
         'counted against your Syntharra minutes allocation.'),
        ('Can I pause forwarding temporarily?',
         'Yes — cancel forwarding using the carrier code (*73 on most, ##21# on GSM carriers) or '
         'toggle it off in your phone settings. Your AI number stays active; it just won\'t receive '
         'any calls until forwarding is reactivated.'),
    ]

    current_section = None
    for item in faqs:
        if isinstance(item, str):
            # Section header
            story.append(sp(2))
            story.append(Paragraph(item, style('faq_sec', 'Helvetica-Bold', 10, PURPLE, leading=14, space_after=2)))
            story.append(HR(LIGHT_P, 1))
        else:
            q, a = item
            story.append(faq_block(q, a))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════
    # SECTION 4 — DASHBOARD
    # ═══════════════════════════════════════════════════════════════════
    story.append(Paragraph('SECTION 4', style('secbadge', 'Helvetica-Bold', 8, PURPLE, leading=10, space_after=2)))
    story.append(Paragraph('Your Dashboard', S_H1))
    story.append(HR(PURPLE, 1))
    story.append(sp(2))
    story.append(Paragraph(
        'Your live dashboard gives you a real-time view of every call, lead, and your AI\'s activity. '
        'Access it any time from any device.',
        S_BODY))
    story.append(sp(3))

    story.append(Paragraph('How to Access', S_H2))
    story.append(Paragraph(
        'Your dashboard link is included in your welcome email. You can also access it directly at:', S_BODY))
    story.append(sp(1))
    story.append(code_pill('https://syntharra.com/dashboard.html?agent_id=YOUR_AGENT_ID'))
    story.append(sp(2))
    story.append(Paragraph(
        'Your agent ID is unique to your account and is included in your welcome email.', S_MUTED))
    story.append(sp(3))

    story.append(Paragraph('What You\'ll See', S_H2))
    dashboard_features = [
        ('Call Log', 'A chronological list of every call — caller, time, job type, urgency, and a link to the full summary.'),
        ('Call Summaries', 'Click any call to read the AI-generated summary including all captured details.'),
        ('Usage Stats', 'See how many minutes you\'ve used this billing cycle and your remaining balance.'),
        ('Agent Status', 'Confirm your AI Receptionist is online and active.'),
        ('Weekly Trend', 'A rolling chart of call volume over the past 4 weeks.'),
    ]
    for title, desc in dashboard_features:
        story.append(KeepTogether([
            Paragraph(f'<b>{title}</b> — {desc}', S_BODY),
            sp(1),
        ]))

    story.append(sp(4))

    # ═══════════════════════════════════════════════════════════════════
    # SECTION 5 — NOTIFICATIONS
    # ═══════════════════════════════════════════════════════════════════
    story.append(Paragraph('SECTION 5', style('secbadge', 'Helvetica-Bold', 8, PURPLE, leading=10, space_after=2)))
    story.append(Paragraph('Call Summaries & Notifications', S_H1))
    story.append(HR(PURPLE, 1))
    story.append(sp(2))
    story.append(Paragraph(
        'After every call, Syntharra sends you a full call summary so you can follow up intelligently.',
        S_BODY))
    story.append(sp(3))

    story.append(Paragraph('What\'s in Each Summary Email', S_H2))
    summary_fields = [
        '📞 Caller name and phone number',
        '📍 Property address (if provided)',
        '🔧 Job type and service category',
        '⚡ Urgency level (Emergency / Urgent / Standard)',
        '📝 Key details from the conversation',
        '💬 Notable requests or information volunteered by the caller',
        '🕐 Date and time of call',
        '⏱ Call duration',
    ]
    for f in summary_fields:
        story.append(Paragraph(f, S_BODY))

    story.append(sp(3))
    story.append(Paragraph('Weekly Report', S_H2))
    story.append(Paragraph(
        'Every Monday morning you\'ll receive a weekly summary covering the past 7 days — '
        'total calls, job types breakdown, top service requests, and any trends worth noting.',
        S_BODY))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════
    # SECTION 6 — MAKING CHANGES
    # ═══════════════════════════════════════════════════════════════════
    story.append(Paragraph('SECTION 6', style('secbadge', 'Helvetica-Bold', 8, PURPLE, leading=10, space_after=2)))
    story.append(Paragraph('Making Changes to Your AI', S_H1))
    story.append(HR(PURPLE, 1))
    story.append(sp(2))
    story.append(Paragraph(
        'Your AI Receptionist is configured based on the information you provided during onboarding. '
        'As your business evolves, we can update it any time.',
        S_BODY))
    story.append(sp(3))

    changes = [
        ('What You Can Update', [
            'Business hours and after-hours behaviour',
            'Services offered, pricing policy, and promotions',
            'Service area or coverage radius',
            'Diagnostic fees and standard pricing',
            'Transfer number (who calls are transferred to)',
            'Notification email addresses and SMS numbers',
            'Custom greeting or agent name',
            'Warranty terms, payment methods, financing details',
            'Seasonal services, membership programs',
        ]),
    ]
    for sec_title, items in changes:
        story.append(Paragraph(sec_title, S_H2))
        for item in items:
            story.append(Paragraph(f'• {item}', S_BODY))
        story.append(sp(2))

    story.append(Paragraph('How to Request Changes', S_H2))
    story.append(Paragraph(
        'Email <b>support@syntharra.com</b> with your change request. Be as specific as possible. '
        'Most changes are live within 24 hours. Complex prompt changes may take slightly longer.',
        S_BODY))
    story.append(sp(2))

    # Tip box
    tip = Table([[
        Paragraph(
            '<b>Pro tip:</b> If you\'re launching a promotion or changing your pricing, email us '
            '24 hours before you want it live. We\'ll make sure your AI is updated before the change goes public.',
            S_BODY)
    ]], colWidths=[155 * mm])
    tip.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F3F0FF')),
        ('ROUNDEDCORNERS', [6]),
        ('BOX', (0, 0), (-1, -1), 0.5, PURPLE),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
        ('RIGHTPADDING', (0, 0), (-1, -1), 14),
    ]))
    story.append(tip)

    # ═══════════════════════════════════════════════════════════════════
    # SECTION 7 — MINUTES & BILLING
    # ═══════════════════════════════════════════════════════════════════
    story.append(sp(5))
    story.append(Paragraph('SECTION 7', style('secbadge', 'Helvetica-Bold', 8, PURPLE, leading=10, space_after=2)))
    story.append(Paragraph('Minutes & Billing', S_H1))
    story.append(HR(PURPLE, 1))
    story.append(sp(2))

    story.append(Paragraph('How Minutes Work', S_H2))
    story.append(Paragraph(
        'Your plan includes a monthly allocation of AI talk minutes. Only the time your AI '
        'Receptionist actively spends speaking with callers counts toward your usage.',
        S_BODY))
    story.append(sp(2))

    mins_table = dark_table(
        ['Plan', 'Monthly Minutes', 'What Counts'],
        [
            ['Standard', '475 minutes', 'AI talk time only'],
            ['Premium', '1,000 minutes', 'AI talk time only'],
        ],
        [50 * mm, 50 * mm, 55 * mm]
    )
    story.append(mins_table)
    story.append(sp(3))

    story.append(Paragraph('Usage Alerts', S_H2))
    story.append(Paragraph(
        'We\'ll email you at <b>80% usage</b> to give you a heads-up. At <b>100%</b>, you\'ll receive '
        'another alert. Your AI never stops answering — calls continue even if you go over your allocation.',
        S_BODY))
    story.append(sp(2))

    story.append(Paragraph('Overages', S_H2))
    story.append(Paragraph(
        'If you exceed your monthly allocation, overage minutes are billed at a low per-minute rate '
        'and invoiced at the end of your billing cycle. Your usage resets on your billing anniversary date.',
        S_BODY))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════
    # SECTION 8 — PREMIUM INTEGRATIONS
    # ═══════════════════════════════════════════════════════════════════
    story.append(Paragraph('SECTION 8', style('secbadge', 'Helvetica-Bold', 8, PURPLE, leading=10, space_after=2)))
    story.append(Paragraph('Premium — Integrations Guide', S_H1))
    story.append(HR(PURPLE, 1))
    story.append(sp(1))

    prem_badge = Table([[
        Paragraph('Premium Plan Only', style('pb', 'Helvetica-Bold', 8, WHITE, leading=10, align=TA_CENTER))
    ]], colWidths=[155 * mm])
    prem_badge.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), PURPLE),
        ('ROUNDEDCORNERS', [4]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(prem_badge)
    story.append(sp(3))

    story.append(Paragraph(
        'Premium clients connect their calendar and CRM so that job bookings and customer details '
        'flow directly into your systems — no manual data entry required.',
        S_BODY))
    story.append(sp(3))

    story.append(Paragraph('Google Calendar Integration', S_H2))
    story.append(Paragraph(
        'Once connected, your AI Receptionist checks your Google Calendar in real time before '
        'confirming appointment slots with callers. Bookings are added automatically.',
        S_BODY))
    story.append(sp(2))
    story.append(step_row(1, 'Receive the integration setup email',
                          'A separate email is sent shortly after your welcome email with a one-click authorisation link.'))
    story.append(step_row(2, 'Click Authorise',
                          'Click the link and log in to the Google account you want to use for bookings.'))
    story.append(step_row(3, 'Grant permissions',
                          'Allow Syntharra to view and create calendar events. This is read/write access '
                          'to your calendar only — no other Google data is accessed.'))
    story.append(step_row(4, 'Done',
                          'Your AI will now check your real availability and create bookings directly in your calendar.'))
    story.append(sp(3))

    story.append(Paragraph('CRM Integration (Jobber & others)', S_H2))
    story.append(Paragraph(
        'When connected, new callers are automatically created as customers in your CRM, and job '
        'requests are logged as new jobs or requests.',
        S_BODY))
    story.append(sp(2))
    story.append(step_row(1, 'Receive the integration setup email',
                          'Same email as above — contains separate authorisation links for calendar and CRM.'))
    story.append(step_row(2, 'Click Authorise for your CRM',
                          'Click the Jobber (or other CRM) authorisation link and log in to your CRM account.'))
    story.append(step_row(3, 'Grant permissions',
                          'Authorise Syntharra to create clients and jobs. No billing or financial data is accessed.'))
    story.append(step_row(4, 'Done',
                          'Every call that generates a lead will now automatically create a record in your CRM.'))
    story.append(sp(3))

    story.append(Paragraph('Repeat Caller Recognition', S_H2))
    story.append(Paragraph(
        'Premium clients benefit from intelligent repeat caller detection. When a customer calls more '
        'than once, your AI recognises them by their phone number, greets them by name, and '
        'references their call history for a more personalised experience.',
        S_BODY))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════
    # SECTION 9 — SUPPORT
    # ═══════════════════════════════════════════════════════════════════
    story.append(Paragraph('SECTION 9', style('secbadge', 'Helvetica-Bold', 8, PURPLE, leading=10, space_after=2)))
    story.append(Paragraph('Getting Support', S_H1))
    story.append(HR(PURPLE, 1))
    story.append(sp(2))

    story.append(Paragraph(
        'We\'re here whenever you need us. For most queries, email is the fastest route.',
        S_BODY))
    story.append(sp(3))

    support_tbl = dark_table(
        ['Contact', 'Best For', 'Response Time'],
        [
            ['support@syntharra.com', 'All queries — changes, billing, technical issues', 'Within a few hours'],
            ['syntharra.com/dashboard', 'View calls, usage, agent status', 'Live'],
        ],
        [60 * mm, 65 * mm, 30 * mm]
    )
    story.append(support_tbl)
    story.append(sp(3))

    story.append(Paragraph('Quick Reference — Common Requests', S_H2))
    common = [
        ('I want to update my business hours', 'Email support@syntharra.com with your new hours'),
        ('I want to add another notification email', 'Email support@syntharra.com with the address'),
        ('My AI said something incorrect', 'Email support@syntharra.com with the call time and what was said'),
        ('I want to pause the service temporarily', 'Email support@syntharra.com — we can suspend and reactivate'),
        ('I want to cancel my subscription', 'Email support@syntharra.com with at least 30 days notice'),
        ('I need help with call forwarding', 'Refer to Section 1 of this guide, or email support@syntharra.com'),
    ]
    for req, action in common:
        story.append(KeepTogether([
            Paragraph(f'<b>"{req}"</b>', style('cr_q', 'Helvetica-Bold', 10, DARK, leading=14, space_after=1)),
            Paragraph(f'→ {action}', S_BODY),
            HR(BORDER, 0.3),
        ]))

    story.append(sp(6))

    # Final footer card
    footer_card = Table([[
        [
            Paragraph('Syntharra', style('fc_n', 'Helvetica-Bold', 14, WHITE, leading=16, align=TA_CENTER, space_after=2)),
            Paragraph('GLOBAL AI SOLUTIONS', style('fc_s', 'Helvetica-Bold', 7, CYAN, leading=9,
                       align=TA_CENTER, space_after=8)),
            Paragraph('support@syntharra.com', style('fc_e', 'Helvetica', 10, colors.HexColor('#C4C0FF'),
                       leading=14, align=TA_CENTER, space_after=2)),
            Paragraph('syntharra.com', style('fc_w', 'Helvetica', 10, CYAN, leading=14, align=TA_CENTER)),
        ]
    ]], colWidths=[155 * mm])
    footer_card.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK),
        ('ROUNDEDCORNERS', [10]),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(footer_card)

    # Build
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f'PDF saved to {output}')


if __name__ == '__main__':
    build()
