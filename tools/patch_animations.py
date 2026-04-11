#!/usr/bin/env python3
"""Patch premium animations onto the current homepage"""
import requests, base64, json, sys, time

TOKEN = "GITHUB_TOKEN_REDACTED"
REPO = "Syntharra/syntharra-website"
FILE = "index.html"
API = f"https://api.github.com/repos/{REPO}/contents/{FILE}"
HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}

print("Fetching current page...")
r = requests.get(API, headers=HEADERS)
r.raise_for_status()
data = r.json()
sha = data["sha"]
content = base64.b64decode(data["content"]).decode("utf-8")
print(f"SHA: {sha} — {len(content)} chars")

# ── 1. EXTRA CSS ─────────────────────────────────────────────────────────────
EXTRA_CSS = """
/* ===== SCROLL PROGRESS BAR ===== */
#spb{
  position:fixed;top:0;left:0;z-index:9999;
  height:2px;width:0%;
  background:linear-gradient(90deg,#6C63FF,#a78bfa,#00D4FF);
  transition:width .1s linear;
  pointer-events:none;
}

/* ===== CURSOR GLOW (hero only) ===== */
#cursor-glow{
  position:fixed;z-index:0;pointer-events:none;
  width:500px;height:500px;border-radius:50%;
  background:radial-gradient(circle,rgba(108,99,255,.08) 0%,transparent 65%);
  transform:translate(-50%,-50%);
  transition:left .15s ease,top .15s ease;
  opacity:0;
}
body.hero-active #cursor-glow{opacity:1}

/* ===== SOCIAL PROOF TOAST ===== */
#sp-toast{
  position:fixed;bottom:28px;right:28px;z-index:9000;
  background:#fff;border-radius:16px;
  box-shadow:0 16px 48px rgba(0,0,0,.13),0 0 0 1px rgba(0,0,0,.06);
  padding:14px 18px;display:flex;align-items:center;gap:12px;
  max-width:320px;
  transform:translateY(20px) scale(.96);opacity:0;
  transition:transform .5s cubic-bezier(.16,1,.3,1),opacity .5s cubic-bezier(.16,1,.3,1);
  pointer-events:none;
}
#sp-toast.show{transform:none;opacity:1}
.sp-ico{font-size:24px;flex-shrink:0}
.sp-content{}
.sp-label{font-size:11px;font-weight:600;color:#aaa;text-transform:uppercase;letter-spacing:.8px;margin-bottom:3px}
.sp-msg{font-size:13px;font-weight:600;color:#0c0c1d;line-height:1.35}
.sp-time{font-size:11px;color:#aaa;margin-top:3px}
.sp-dot{
  position:absolute;top:12px;right:12px;
  width:6px;height:6px;border-radius:50%;background:#6C63FF;
  animation:blink 2s ease infinite;
}

/* ===== COUNTER ANIMATION ===== */
.count-target{display:inline-block}

/* ===== HERO TEXT REVEAL ===== */
.hero-line{
  display:block;overflow:hidden;
}
.hero-line-inner{
  display:block;
  transform:translateY(100%);
  animation:lineReveal .9s cubic-bezier(.16,1,.3,1) both;
}
.hero-line:nth-child(1) .hero-line-inner{animation-delay:.1s}
.hero-line:nth-child(2) .hero-line-inner{animation-delay:.22s}
.hero-line:nth-child(3) .hero-line-inner{animation-delay:.34s}
@keyframes lineReveal{from{transform:translateY(105%)}to{transform:translateY(0)}}

/* ===== ANIMATED GRADIENT BORDER on featured card ===== */
@keyframes borderSpin{from{--angle:0deg}to{--angle:360deg}}
@property --angle{syntax:'<angle>';initial-value:0deg;inherits:false}
.test-featured{
  position:relative;
}
.test-featured::before{
  content:'';position:absolute;inset:-1px;border-radius:33px;
  background:conic-gradient(from var(--angle),transparent 80%,rgba(108,99,255,.5) 90%,rgba(167,139,250,.4) 95%,transparent 100%);
  animation:borderSpin 4s linear infinite;
  pointer-events:none;z-index:0;
}
.test-featured > *{position:relative;z-index:1}

/* ===== HERO STAT PILL ===== */
.hero-live-pill{
  display:inline-flex;align-items:center;gap:8px;
  font-size:12px;font-weight:600;
  background:rgba(22,163,74,.1);color:#16a34a;
  border:1px solid rgba(22,163,74,.2);
  border-radius:100px;padding:7px 14px;margin-bottom:20px;
}
.hero-live-pill-dot{
  width:6px;height:6px;border-radius:50%;background:#16a34a;
  animation:blink 1.5s ease infinite;
}

/* ===== TYPING INDICATOR in dash card ===== */
.typing-dots span{
  display:inline-block;width:4px;height:4px;border-radius:50%;
  background:#aaa;margin:0 1.5px;
  animation:typingDot 1.4s ease infinite;
}
.typing-dots span:nth-child(2){animation-delay:.2s}
.typing-dots span:nth-child(3){animation-delay:.4s}
@keyframes typingDot{0%,80%,100%{transform:translateY(0);opacity:.4}40%{transform:translateY(-4px);opacity:1}}

/* ===== HOVER MAGNETIC BUTTONS ===== */
.btn-primary,.btn-white{
  will-change:transform;
}

/* ===== INDUSTRY CARD ICON ANIMATE ===== */
.ind-ico{
  display:inline-block;
  transition:transform .4s cubic-bezier(.16,1,.3,1);
}
.ind-card:hover .ind-ico{transform:scale(1.2) rotate(-5deg)}

/* ===== BENTO shimmer on dark card ===== */
.b1::before{
  content:'';position:absolute;
  top:0;left:-100%;width:50%;height:100%;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.03),transparent);
  animation:shimmer 3s ease infinite;
}
@keyframes shimmer{0%{left:-100%}100%{left:200%}}

/* ===== NOTIFICATION COUNTER BADGE ===== */
.nav-notif{
  position:relative;
  display:inline-flex;align-items:center;
}
"""

# ── 2. JS ADDITIONS ───────────────────────────────────────────────────────────
EXTRA_JS = """
// ── SCROLL PROGRESS BAR ──
const spb = document.getElementById('spb');
window.addEventListener('scroll', () => {
  const pct = window.scrollY / (document.body.scrollHeight - window.innerHeight) * 100;
  spb.style.width = Math.min(pct, 100) + '%';
}, {passive: true});

// ── CURSOR GLOW (hero section only) ──
const glow = document.getElementById('cursor-glow');
const heroSection = document.querySelector('.hero');
document.addEventListener('mousemove', e => {
  glow.style.left = e.clientX + 'px';
  glow.style.top = e.clientY + 'px';
});
const heroObs = new IntersectionObserver(entries => {
  entries.forEach(e => {
    document.body.classList.toggle('hero-active', e.isIntersecting);
  });
}, {threshold: 0.1});
if (heroSection) heroObs.observe(heroSection);

// ── SOCIAL PROOF TOASTS ──
const notifications = [
  {ico:'📅', label:'New Booking', msg:'Mike T. just booked an AC repair — Phoenix, AZ', time:'Just now'},
  {ico:'💰', label:'Revenue Recovered', msg:'$520 job recovered — after-hours call at 11:42pm', time:'2 min ago'},
  {ico:'📞', label:'Call Answered', msg:'Sarah L. — Furnace service booked for Thu 2pm', time:'4 min ago'},
  {ico:'⭐', label:'5-Star Review', msg:'"Answered immediately — very professional" — Rob K.', time:'8 min ago'},
  {ico:'🗓️', label:'New Booking', msg:'Emma R. booked drain cleaning — Denver, CO', time:'12 min ago'},
  {ico:'💰', label:'Revenue Recovered', msg:'$740 job booked — competitor\'s voicemail was full', time:'18 min ago'},
];
let toastIdx = 0;
const toast = document.getElementById('sp-toast');
function showToast() {
  const n = notifications[toastIdx % notifications.length];
  toast.querySelector('.sp-ico').textContent = n.ico;
  toast.querySelector('.sp-label').textContent = n.label;
  toast.querySelector('.sp-msg').textContent = n.msg;
  toast.querySelector('.sp-time').textContent = n.time;
  toast.classList.add('show');
  toastIdx++;
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(showToast, 3200);
  }, 5000);
}
// Start after 4s delay
setTimeout(showToast, 4000);

// ── COUNTING STATS ──
function animateCount(el, target, suffix, duration) {
  const start = performance.now();
  const isDecimal = target % 1 !== 0;
  function update(ts) {
    const progress = Math.min((ts - start) / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3); // cubic ease out
    const current = isDecimal ? (ease * target).toFixed(1) : Math.round(ease * target);
    el.textContent = current + suffix;
    if (progress < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}

const statDefs = [
  {sel:'.stats-row .stat:nth-child(1) .stat-n', from:0, to:97, suffix:'%'},
  {sel:'.stats-row .stat:nth-child(4) .stat-n', from:0, to:10, suffix:'k+'},
];

const statEls = document.querySelectorAll('.stat-n');
let statsAnimated = false;
const statsSection = document.querySelector('.stats-strip');
if (statsSection) {
  new IntersectionObserver(entries => {
    if (entries[0].isIntersecting && !statsAnimated) {
      statsAnimated = true;
      // Animate the 97% stat
      const stat1 = document.querySelector('.stats-row .stat:nth-child(1) .stat-n');
      if (stat1) {
        stat1.innerHTML = '';
        animateCount(stat1, 97, '', 1800);
        setTimeout(() => { if(stat1) stat1.innerHTML += '<sup>%</sup>'; }, 1850);
      }
    }
  }, {threshold: 0.4}).observe(statsSection);
}

// ── MAGNETIC BUTTON EFFECT ──
document.querySelectorAll('.btn-primary, .btn-white').forEach(btn => {
  btn.addEventListener('mousemove', e => {
    const rect = btn.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    btn.style.transform = `translate(${x * 0.12}px, ${y * 0.18}px) translateY(-2px)`;
  });
  btn.addEventListener('mouseleave', () => {
    btn.style.transform = '';
  });
});

// ── SMOOTH PARALLAX ON HERO BACKGROUND ──
const heroBg = document.querySelector('.hero');
if (heroBg) {
  window.addEventListener('scroll', () => {
    const y = window.scrollY;
    if (y < window.innerHeight * 1.5) {
      heroBg.style.backgroundPositionY = (y * 0.4) + 'px';
    }
  }, {passive: true});
}
"""

# ── 3. PATCH HTML ─────────────────────────────────────────────────────────────

# Add CSS before </style>
old_css_end = "</style>"
assert content.count(old_css_end) == 1, "Multiple </style> tags"
content = content.replace(old_css_end, EXTRA_CSS + old_css_end, 1)

# Add scroll progress bar + cursor glow just after <body>
content = content.replace(
    "<body>",
    "<body>\n<div id='spb'></div>\n<div id='cursor-glow'></div>"
)

# Add social proof toast just before </body>
TOAST_HTML = """
<div id="sp-toast">
  <div class="sp-ico">📅</div>
  <div class="sp-content">
    <div class="sp-label">New Booking</div>
    <div class="sp-msg">Loading...</div>
    <div class="sp-time">Just now</div>
  </div>
  <div class="sp-dot"></div>
</div>
"""
content = content.replace("</body>", TOAST_HTML + "\n</body>")

# Add extra JS before </script> (last script tag)
# Find the last </script> and inject before it
last_script = content.rfind("</script>")
content = content[:last_script] + "\n" + EXTRA_JS + "\n" + content[last_script:]

# Add live pill above hero h1
content = content.replace(
    '<div class="hero-tag">',
    '<div class="hero-live-pill"><span class="hero-live-pill-dot"></span>3 calls being handled right now</div>\n      <div class="hero-tag">'
)

# Verify exactly ONE style block
assert content.count("<style>") == 1, f"Style block count: {content.count('<style>')}"
print("All patches applied. Style check OK.")

# Push
print("Pushing...")
payload = {
    "message": "feat(website): add premium animations — toast notifications, counter stats, cursor glow, magnetic buttons, scroll progress, animated border",
    "content": base64.b64encode(content.encode("utf-8")).decode(),
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
