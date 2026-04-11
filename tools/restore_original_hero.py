#!/usr/bin/env python3
"""Restore the original light-themed hero while keeping all sections below intact."""
import requests, base64, json, sys

TOKEN = "GITHUB_TOKEN_REDACTED"
REPO = "Syntharra/syntharra-website"
FILE = "index.html"
API = f"https://api.github.com/repos/{REPO}/contents/{FILE}"
HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}

print("Fetching current page...")
r = requests.get(API, headers=HEADERS)
r.raise_for_status()
sha = r.json()["sha"]
c = base64.b64decode(r.json()["content"]).decode("utf-8")
print(f"SHA: {sha} | {len(c)} chars")

orig = c

# ── 1. ADD FONT IMPORTS (Inter + JetBrains Mono for phone mockup) ──────────────
c = c.replace(
    '<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,500;12..96,700;12..96,800&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">',
    '<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,500;12..96,700;12..96,800&family=DM+Sans:wght@300;400;500;600&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@600&display=swap" rel="stylesheet">'
)

# ── 2. ADD ORIGINAL CSS VARS (as aliases) ─────────────────────────────────────
# Add original vars after :root { block, these are needed by the hero CSS
ORIG_VARS = """
  /* Original hero vars */
  --violet:#6C63FF; --violet-2:#8B85FF; --violet-d:#5A52E0;
  --ink:#0E0E1A; --ink-2:#1A1A2E; --body:#4A4A6A; --muted:#8A8AA8;
  --bg:#F7F7FB; --card:#FFFFFF; --border:#E8E8F0; --line:#EFEFF6;
  --green:#10B981; --red:#EF4444;"""

c = c.replace(
    "--surface:#f7f7fb;\n}",
    "--surface:#f7f7fb;" + ORIG_VARS + "\n}"
)

# ── 3. REPLACE HERO CSS (/* HERO */ through /* DASHBOARD CARD */ through /* STATS STRIP */) ──
OLD_HERO_CSS_START = "\n/* HERO */"
OLD_HERO_CSS_END = "\n/* STATS STRIP */"

# Find the boundaries
hero_css_start_idx = c.find(OLD_HERO_CSS_START)
stats_css_start_idx = c.find(OLD_HERO_CSS_END)

assert hero_css_start_idx != -1, "Could not find /* HERO */ comment"
assert stats_css_start_idx != -1, "Could not find /* STATS STRIP */ comment"

NEW_HERO_CSS = """
/* HERO */
.hero{padding:108px 0 92px;position:relative;overflow:hidden}
.hero::before{content:"";position:absolute;inset:0;background:radial-gradient(60% 50% at 80% 20%,rgba(108,99,255,.12),transparent 70%),radial-gradient(40% 40% at 10% 80%,rgba(139,133,255,.10),transparent 70%);pointer-events:none}
.hero-grid{display:grid;grid-template-columns:1.05fr .95fr;gap:72px;align-items:center;position:relative}
.eyebrow{display:inline-flex;align-items:center;gap:8px;font-size:13px;font-weight:600;color:var(--violet);background:rgba(108,99,255,.08);padding:8px 14px;border-radius:999px;border:1px solid rgba(108,99,255,.18);margin-bottom:24px}
.eyebrow .dot{width:6px;height:6px;border-radius:50%;background:var(--green);box-shadow:0 0 0 4px rgba(16,185,129,.18);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
h1.headline{font-family:'Inter',system-ui,sans-serif;font-size:88px;line-height:1.04;letter-spacing:-.035em;font-weight:800;color:var(--ink);margin-bottom:22px}
h1.headline em{font-style:normal;background:linear-gradient(110deg,var(--violet) 20%,var(--violet-2) 80%);-webkit-background-clip:text;background-clip:text;color:transparent}
.sub{font-size:20px;line-height:1.55;color:var(--body);margin-bottom:32px;max-width:600px}
.sub strong{color:var(--ink-2);font-weight:600}
.cta-row{display:flex;gap:14px;align-items:center;flex-wrap:wrap;margin-bottom:28px}
.proof-row{display:flex;align-items:center;gap:18px;font-size:13px;color:var(--muted);flex-wrap:wrap}
.avatars{display:flex}
.avatars span{width:32px;height:32px;border-radius:50%;border:2px solid #fff;margin-left:-10px;background-size:cover}
.avatars span:first-child{margin-left:0}
.avatars span:nth-child(1){background:linear-gradient(135deg,#FCA5A5,#F87171)}
.avatars span:nth-child(2){background:linear-gradient(135deg,#93C5FD,#3B82F6)}
.avatars span:nth-child(3){background:linear-gradient(135deg,#FCD34D,#F59E0B)}
.avatars span:nth-child(4){background:linear-gradient(135deg,#A7F3D0,#10B981)}
.stars{color:#F59E0B;letter-spacing:2px;font-size:14px}

/* HERO BTN */
.btn{display:inline-flex;align-items:center;gap:8px;font-family:inherit;font-weight:600;font-size:15px;padding:13px 22px;border-radius:12px;border:none;cursor:pointer;transition:all .2s ease;text-decoration:none}
.btn-primary{background:var(--violet);color:#fff;box-shadow:0 6px 24px -8px rgba(108,99,255,.55)}
.btn-primary:hover{background:var(--violet-d);transform:translateY(-1px);box-shadow:0 12px 32px -8px rgba(108,99,255,.65)}
.btn-ghost{background:transparent;color:var(--ink-2);border:1px solid var(--border)}
.btn-ghost:hover{border-color:var(--violet);color:var(--violet)}

/* HERO PHONE MOCKUP */
.phone-wrap{position:relative;display:flex;justify-content:center}
.phone{width:350px;height:710px;background:linear-gradient(180deg,#1A1A2E,#0E0E1A);border-radius:44px;padding:14px;box-shadow:0 50px 80px -30px rgba(14,14,26,.55),0 0 0 1px rgba(108,99,255,.15);position:relative}
.phone-screen{width:100%;height:100%;background:#F7F7FB;border-radius:32px;overflow:hidden;display:flex;flex-direction:column;position:relative}
.notch{position:absolute;top:8px;left:50%;transform:translateX(-50%);width:108px;height:24px;background:#0E0E1A;border-radius:16px;z-index:2}
.call-bar{padding:38px 22px 14px;display:flex;justify-content:space-between;align-items:center;font-size:11px;font-weight:700;color:var(--ink-2)}
.call-card{margin:8px 18px;background:#fff;border-radius:18px;padding:18px;box-shadow:0 8px 24px -12px rgba(14,14,26,.12);border:1px solid var(--line)}
.call-status{display:flex;align-items:center;gap:8px;font-size:11px;font-weight:700;color:var(--green);text-transform:uppercase;letter-spacing:.06em;margin-bottom:10px}
.call-status .ring{width:8px;height:8px;border-radius:50%;background:var(--green);animation:ring 1.6s infinite}
@keyframes ring{0%{box-shadow:0 0 0 0 rgba(16,185,129,.5)}70%{box-shadow:0 0 0 8px rgba(16,185,129,0)}100%{box-shadow:0 0 0 0 rgba(16,185,129,0)}}
.caller{font-size:17px;font-weight:700;color:var(--ink)}
.caller-meta{font-size:12px;color:var(--muted);margin-top:2px}
.timer{margin-top:14px;font-family:'JetBrains Mono',monospace;font-size:13px;color:var(--violet);font-weight:600}
.transcript{margin:0 18px;padding:14px;background:rgba(108,99,255,.06);border-radius:14px;border:1px solid rgba(108,99,255,.14)}
.bubble{font-size:12px;color:var(--ink-2);line-height:1.45;margin-bottom:10px}
.bubble:last-child{margin-bottom:0}
.bubble .who{display:block;font-size:10px;font-weight:700;color:var(--violet);text-transform:uppercase;letter-spacing:.08em;margin-bottom:3px}
.bubble.user .who{color:var(--muted)}
.captured{margin:14px 18px 18px;background:linear-gradient(135deg,var(--violet),var(--violet-2));border-radius:16px;padding:14px;color:#fff}
.captured .lbl{font-size:10px;text-transform:uppercase;letter-spacing:.1em;opacity:.85;font-weight:700;margin-bottom:6px}
.captured .row{display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px;font-weight:500}
.captured .row strong{font-weight:700}
.float-badge{position:absolute;background:#fff;border-radius:14px;padding:12px 16px;box-shadow:0 20px 40px -16px rgba(14,14,26,.18);display:flex;align-items:center;gap:12px;font-size:13px;font-weight:600;color:var(--ink-2);border:1px solid var(--line);z-index:3}
.float-badge .icon{width:36px;height:36px;border-radius:10px;background:rgba(108,99,255,.1);color:var(--violet);display:flex;align-items:center;justify-content:center;font-size:18px}
.fb-1{top:50px;left:-30px;animation:float 5s ease-in-out infinite}
.fb-2{bottom:90px;right:-30px;animation:float 5s ease-in-out infinite .8s}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
.fb-1 .icon{background:rgba(16,185,129,.12);color:var(--green)}
@media(max-width:1200px){h1.headline{font-size:72px}}
@media(max-width:900px){.hero-grid{grid-template-columns:1fr;gap:48px}.phone-wrap{display:none}h1.headline{font-size:56px}}
@media(max-width:600px){h1.headline{font-size:42px}.hero{padding:88px 0 64px}}
"""

c = c[:hero_css_start_idx] + NEW_HERO_CSS + c[stats_css_start_idx:]

# ── 4. REMOVE AURORA / WOW CSS from end of style ──────────────────────────────
# These are the patches added by patch_wow_hero.py — no longer needed
aurora_start = c.find("\n/* AURORA ORBS */")
style_end = c.find("</style>")
if aurora_start != -1 and aurora_start < style_end:
    c = c[:aurora_start] + "\n" + c[style_end:]

# ── 5. REPLACE HERO HTML ──────────────────────────────────────────────────────
OLD_HERO_HTML_START = "<!-- HERO -->\n<section"
OLD_HERO_HTML_END = "</section>"

# Find hero section HTML boundaries
hero_html_marker = c.find("<!-- HERO -->")
assert hero_html_marker != -1, "Could not find <!-- HERO --> marker"

# Find the section start
section_start = c.find("<section", hero_html_marker)
# Find the matching closing </section>
section_end = c.find("</section>", section_start) + len("</section>")

NEW_HERO_HTML = """<!-- HERO -->
<section class="hero">
    <div class="container hero-grid">
        <div>
            <div class="eyebrow"><span class="dot"></span> Built for HVAC contractors</div>
            <h1 class="headline">Stop missing calls.<br>Stop losing <em>$80,000 a year.</em></h1>
            <p class="sub">Every missed call is <strong>$300 to $2,000</strong> walking to your competitor. Syntharra answers every call, captures every lead, hands it to you instantly &mdash; <strong>24/7, in under 3 seconds.</strong> Like you're always there.</p>
            <div class="cta-row">
                <a href="https://calendar.app.google/jxUu7XfiMXMqvdiw6" class="btn btn-primary">Book Your Free Demo &rarr;</a>
                <a href="demo.html" class="btn btn-ghost">&#9654; Hear the AI live</a>
            </div>
            <div class="proof-row">
                <div>No credit card. Live in 24 hours. Cancel anytime.</div>
            </div>
        </div>

        <div class="phone-wrap">
            <div class="float-badge fb-1"><div class="icon">&#10003;</div><div>Lead captured<br><span style="font-weight:400;color:var(--muted);font-size:11px">in 2.8 seconds</span></div></div>
            <div class="float-badge fb-2"><div class="icon">$</div><div>$1,450 lead<br><span style="font-weight:400;color:var(--muted);font-size:11px">handed off to owner</span></div></div>
            <div class="phone">
                <div class="phone-screen">
                    <div class="notch"></div>
                    <div class="call-bar"><span>9:41</span><span>&#11044;&#11044;&#11044;&#11044;&#11044; 5G</span></div>
                    <div class="call-card">
                        <div class="call-status"><span class="ring"></span> Live call</div>
                        <div class="caller">+1 (512) 555-0188</div>
                        <div class="caller-meta">Austin, TX &bull; Unknown caller</div>
                        <div class="timer">&#9201; 00:02.8 &mdash; Syntharra answered</div>
                    </div>
                    <div class="transcript">
                        <div class="bubble user"><span class="who">Caller</span>&ldquo;My AC just stopped working and it&rsquo;s 95 degrees in the house.&rdquo;</div>
                        <div class="bubble"><span class="who">Syntharra</span>&ldquo;I&rsquo;m sorry to hear that &mdash; I can get a tech out today. Can I grab your address and a callback number?&rdquo;</div>
                    </div>
                    <div class="captured">
                        <div class="lbl">&#10003; Lead captured</div>
                        <div class="row"><span>Name</span><strong>Sarah M.</strong></div>
                        <div class="row"><span>Issue</span><strong>AC failure (urgent)</strong></div>
                        <div class="row"><span>Sent to</span><strong>Owner&rsquo;s phone</strong></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>"""

c = c[:hero_html_marker] + NEW_HERO_HTML + c[section_end:]

# ── 6. VERIFY ─────────────────────────────────────────────────────────────────
assert c.count("<style>") == 1, f"Multiple <style> blocks: {c.count('<style>')}"
assert c.count("</style>") == 1, f"Multiple </style> blocks"
assert c != orig, "No changes made"
assert "phone-wrap" in c, "Phone mockup not in output"
assert "hero-grid" in c, "hero-grid not in output"
assert "aurora" not in c.lower() or "aurora" in c[:c.find("</style>")].lower() == False, "Aurora still in HTML"
# Make sure aurora is NOT in HTML (only might appear in CSS class definitions in style if not removed)
html_part = c[c.find("</style>"):]
assert "aurora" not in html_part.lower(), f"Aurora still in HTML section"
assert "ticker-reel" not in html_part, "Ticker still in HTML"
assert "hero-grid" in c, "hero-grid missing"
assert "float-badge" in c, "Float badge missing"
print(f"All checks passed. Output: {len(c)} chars")

# ── 7. PUSH ───────────────────────────────────────────────────────────────────
payload = {
    "message": "feat(hero): restore original light hero — phone mockup, purple text, light bg",
    "content": base64.b64encode(c.encode("utf-8")).decode(),
    "sha": sha
}
resp = requests.put(API, headers=HEADERS, data=json.dumps(payload))
if resp.status_code in (200, 201):
    print(f"SUCCESS — {resp.json()['commit']['sha'][:8]}")
    print("Live at https://syntharra.com in ~60-90s")
else:
    print(f"FAILED {resp.status_code}")
    sys.stdout.buffer.write(resp.text.encode("utf-8"))
    sys.exit(1)
