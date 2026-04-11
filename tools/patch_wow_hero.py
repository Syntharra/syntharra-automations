#!/usr/bin/env python3
"""Patch hero section — aurora orbs, word reveals, live ticker, pulsing glow"""
import requests, base64, json, sys

TOKEN = "GITHUB_TOKEN_REDACTED"
REPO = "Syntharra/syntharra-website"
FILE = "index.html"
API = f"https://api.github.com/repos/{REPO}/contents/{FILE}"
HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}

print("Fetching page...")
r = requests.get(API, headers=HEADERS)
r.raise_for_status()
sha = r.json()["sha"]
c = base64.b64decode(r.json()["content"]).decode("utf-8")
print(f"SHA: {sha} | {len(c)} chars")

orig = c  # keep original for diff check

# ── 1. NEW CSS ─────────────────────────────────────────────────────────────────
NEW_CSS = """
/* AURORA ORBS */
.aurora{position:absolute;border-radius:50%;pointer-events:none}
.a1{width:60vw;height:60vw;background:radial-gradient(ellipse,rgba(108,99,255,.22) 0%,transparent 60%);top:-20%;right:-8%;filter:blur(70px);animation:drift1 10s ease-in-out infinite}
.a2{width:40vw;height:40vw;background:radial-gradient(ellipse,rgba(0,140,255,.13) 0%,transparent 60%);bottom:5%;left:2%;filter:blur(60px);animation:drift2 13s ease-in-out infinite}
.a3{width:30vw;height:30vw;background:radial-gradient(ellipse,rgba(160,80,255,.18) 0%,transparent 60%);top:30%;left:28%;filter:blur(55px);animation:drift3 8s ease-in-out infinite}
@keyframes drift1{0%,100%{transform:translate(0,0) scale(1)}40%{transform:translate(-35px,28px) scale(1.1)}70%{transform:translate(18px,-18px) scale(.92)}}
@keyframes drift2{0%,100%{transform:translate(0,0)}50%{transform:translate(48px,-36px) scale(1.13)}}
@keyframes drift3{0%,100%{transform:translate(0,0)}50%{transform:translate(-24px,20px) scale(1.08)}}

/* WORD REVEAL */
.wr{display:block;overflow:hidden;line-height:1.02}
.wi{display:block;animation:wIn .95s cubic-bezier(.16,1,.3,1) both;animation-delay:var(--d,.1s)}
@keyframes wIn{from{transform:translateY(108%)}to{transform:translateY(0)}}

/* LIVE TICKER */
.ticker-wrap{
  display:flex;align-items:center;gap:12px;
  margin-top:36px;max-width:560px;overflow:hidden;
}
.ticker-pill{
  font-size:9px;font-weight:800;letter-spacing:1.6px;text-transform:uppercase;
  color:#4ade80;background:rgba(74,222,128,.1);border:1px solid rgba(74,222,128,.2);
  border-radius:5px;padding:5px 8px;flex-shrink:0;white-space:nowrap;
}
.ticker-track{
  overflow:hidden;flex:1;
  -webkit-mask-image:linear-gradient(90deg,transparent 0%,#000 12%,#000 88%,transparent 100%);
  mask-image:linear-gradient(90deg,transparent 0%,#000 12%,#000 88%,transparent 100%);
}
.ticker-reel{
  display:flex;gap:0;
  animation:tickRoll 30s linear infinite;
  width:max-content;
}
.ticker-reel span{
  font-size:12px;color:rgba(255,255,255,.4);
  white-space:nowrap;font-weight:500;
  padding:0 24px;border-right:1px solid rgba(255,255,255,.07);
}
@keyframes tickRoll{from{transform:translateX(0)}to{transform:translateX(-50%)}}

/* PULSING CARD GLOW */
@keyframes glowPulse{0%,100%{opacity:.55}50%{opacity:1}}
"""

# ── 2. CSS PATCHES ──────────────────────────────────────────────────────────────

# Make hero background deeper + add bottom gradient for cinematic feel
c = c.replace(
    ".hero{background:var(--hero-bg);min-height:100dvh;display:flex;align-items:center;padding:110px 48px 180px;position:relative;overflow:hidden;clip-path:polygon(0 0,100% 0,100% calc(100% - 80px),0 100%);margin-bottom:-2px}",
    ".hero{background:var(--hero-bg);min-height:100dvh;display:flex;align-items:center;padding:110px 48px 180px;position:relative;overflow:hidden;clip-path:polygon(0 0,100% 0,100% calc(100% - 80px),0 100%);margin-bottom:-2px;isolation:isolate}"
)

# Tone down old ::before (aurora divs handle it now)
c = c.replace(
    ".hero::before{content:'';position:absolute;top:-20%;right:-10%;width:70vw;height:70vw;border-radius:50%;background:radial-gradient(ellipse,rgba(108,99,255,.14) 0%,transparent 65%);pointer-events:none}",
    ".hero::before{display:none}"
)
c = c.replace(
    ".hero::after{content:'';position:absolute;bottom:0;left:-5%;width:50vw;height:40vw;border-radius:50%;background:radial-gradient(ellipse,rgba(108,99,255,.07) 0%,transparent 65%);pointer-events:none}",
    ".hero::after{display:none}"
)

# Stronger pulsing card glow
c = c.replace(
    ".card-glow{position:absolute;bottom:-50px;left:50%;transform:translateX(-50%);width:60%;height:70px;background:radial-gradient(ellipse,rgba(108,99,255,.5) 0%,transparent 70%);filter:blur(18px);pointer-events:none}",
    ".card-glow{position:absolute;bottom:-64px;left:50%;transform:translateX(-50%);width:88%;height:110px;background:radial-gradient(ellipse,rgba(108,99,255,.8) 0%,transparent 65%);filter:blur(26px);pointer-events:none;animation:glowPulse 3.2s ease-in-out infinite}"
)

# Inject CSS before </style>
assert c.count("</style>") == 1
c = c.replace("</style>", NEW_CSS + "\n</style>")

# ── 3. HTML PATCHES ─────────────────────────────────────────────────────────────

# Add aurora orbs right after hero-dots
c = c.replace(
    '<div class="hero-dots"></div>',
    '<div class="hero-dots"></div>\n  <div class="aurora a1"></div>\n  <div class="aurora a2"></div>\n  <div class="aurora a3"></div>'
)

# Word-by-word h1 reveal
c = c.replace(
    '<h1>Never miss<br>a service<br><span class="hl">call.</span></h1>',
    '''<h1>
        <span class="wr"><span class="wi" style="--d:.05s">Never miss</span></span>
        <span class="wr"><span class="wi" style="--d:.2s">a service</span></span>
        <span class="wr"><span class="wi hl" style="--d:.35s">call.</span></span>
      </h1>'''
)

# Live ticker — insert after hero-social closing div, before hero-right
TICKER_HTML = '''
      <div class="ticker-wrap">
        <div class="ticker-pill">&#9679; LIVE</div>
        <div class="ticker-track">
          <div class="ticker-reel">
            <span>&#128222;&nbsp; AC Repair booked &mdash; Phoenix, AZ</span>
            <span>&#128176;&nbsp; $520 recovered &mdash; after-hours call</span>
            <span>&#128197;&nbsp; Furnace service booked &mdash; Denver, CO</span>
            <span>&#11088;&nbsp; 5-star review: &ldquo;Professional and fast&rdquo;</span>
            <span>&#128222;&nbsp; Drain cleaning &mdash; Austin, TX</span>
            <span>&#128176;&nbsp; $740 job &mdash; competitor&rsquo;s voicemail was full</span>
            <span>&#128197;&nbsp; Panel upgrade booked &mdash; Atlanta, GA</span>
            <span>&#128222;&nbsp; AC Repair booked &mdash; Phoenix, AZ</span>
            <span>&#128176;&nbsp; $520 recovered &mdash; after-hours call</span>
            <span>&#128197;&nbsp; Furnace service booked &mdash; Denver, CO</span>
            <span>&#11088;&nbsp; 5-star review: &ldquo;Professional and fast&rdquo;</span>
            <span>&#128222;&nbsp; Drain cleaning &mdash; Austin, TX</span>
            <span>&#128176;&nbsp; $740 job &mdash; competitor&rsquo;s voicemail was full</span>
            <span>&#128197;&nbsp; Panel upgrade booked &mdash; Atlanta, GA</span>
          </div>
        </div>
      </div>'''

# Insert ticker just before the closing of the left hero column (before rv-r d2)
c = c.replace(
    '</div>\n    <div class="rv-r d2">',
    TICKER_HTML + '\n    </div>\n    <div class="rv-r d2">'
)

# ── 4. VERIFY ──────────────────────────────────────────────────────────────────
assert c.count("<style>") == 1, "Multiple style blocks"
assert c != orig, "No changes made — check patterns"
assert "aurora" in c, "Aurora not in output"
assert "ticker-reel" in c, "Ticker not in output"
assert "wIn" in c, "Word reveal not in output"
print("All checks passed.")

# ── 5. PUSH ────────────────────────────────────────────────────────────────────
payload = {
    "message": "feat(hero): wow hero — aurora orbs, word reveals, live activity ticker, pulsing card glow",
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
