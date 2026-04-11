#!/usr/bin/env python3
"""Push light premium homepage — Stripe/Figma quality"""
import requests, base64, json, sys

TOKEN = "GITHUB_TOKEN_REDACTED"
REPO = "Syntharra/syntharra-website"
FILE = "index.html"
API = f"https://api.github.com/repos/{REPO}/contents/{FILE}"
HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}

HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Syntharra — AI Voice Agents for Trade Businesses</title>
<meta name="description" content="Never miss a service call again. Syntharra deploys AI voice agents that answer every call, book jobs, and grow your trade business — 24/7, automatically.">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
body{font-family:'Plus Jakarta Sans',sans-serif;background:#ffffff;color:#0d0d1f;overflow-x:clip}

:root{
  --purple:#6C63FF;
  --purple-dark:#4f46e5;
  --purple-light:#f0eeff;
  --ink:#0d0d1f;
  --ink-mid:#4a4a6a;
  --ink-light:#8a8aaa;
  --border:#e4e4f0;
  --surface:#f7f7fc;
  --white:#ffffff;
}

/* SCROLL REVEAL */
.sr{opacity:0;transform:translateY(32px);transition:opacity .85s cubic-bezier(.16,1,.3,1),transform .85s cubic-bezier(.16,1,.3,1)}
.sr.in{opacity:1;transform:none}
.sr-l{opacity:0;transform:translateX(-32px);transition:opacity .85s cubic-bezier(.16,1,.3,1),transform .85s cubic-bezier(.16,1,.3,1)}
.sr-l.in{opacity:1;transform:none}
.sr-r{opacity:0;transform:translateX(32px);transition:opacity .85s cubic-bezier(.16,1,.3,1),transform .85s cubic-bezier(.16,1,.3,1)}
.sr-r.in{opacity:1;transform:none}
.d1{transition-delay:.07s}.d2{transition-delay:.14s}.d3{transition-delay:.21s}
.d4{transition-delay:.28s}.d5{transition-delay:.35s}

/* ===== NAV ===== */
nav{
  position:fixed;top:0;left:0;right:0;z-index:900;
  height:68px;padding:0 48px;
  display:flex;align-items:center;justify-content:space-between;
  background:rgba(255,255,255,0);
  transition:background .3s,box-shadow .3s;
}
nav.scrolled{
  background:rgba(255,255,255,.94);
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  box-shadow:0 1px 0 #e4e4f0;
}
.logo{display:flex;align-items:center;gap:11px;text-decoration:none}
.logo svg{display:block}
.logo-text{line-height:1}
.logo-name{font-size:16px;font-weight:800;letter-spacing:-.3px;color:var(--ink)}
.logo-sub{font-size:7.5px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:var(--purple);margin-top:3px;display:block}
.nav-links{display:flex;align-items:center;gap:36px;list-style:none}
.nav-links a{font-size:14px;font-weight:500;color:var(--ink-mid);text-decoration:none;transition:color .2s}
.nav-links a:hover{color:var(--ink)}
.nav-right{display:flex;align-items:center;gap:12px}
.btn-nav-ghost{
  font-size:14px;font-weight:600;color:var(--ink-mid);
  padding:9px 18px;border-radius:8px;text-decoration:none;
  transition:color .2s,background .2s;
}
.btn-nav-ghost:hover{color:var(--ink);background:var(--surface)}
.btn-nav{
  font-size:14px;font-weight:700;
  background:var(--purple);color:#fff;
  padding:10px 22px;border-radius:8px;text-decoration:none;
  transition:background .2s,transform .2s,box-shadow .2s;
}
.btn-nav:hover{background:var(--purple-dark);transform:translateY(-1px);box-shadow:0 6px 20px rgba(108,99,255,.3)}
.hamburger{
  display:flex;flex-direction:column;gap:5px;
  background:none;border:none;cursor:pointer;padding:8px;
}
.hamburger span{display:block;width:22px;height:1.5px;background:var(--ink-mid);border-radius:2px;transition:background .2s}
.hamburger:hover span{background:var(--ink)}

/* MENU */
.menu-bd{position:fixed;inset:0;background:rgba(13,13,31,.5);z-index:1000;opacity:0;pointer-events:none;transition:opacity .25s;backdrop-filter:blur(4px)}
.menu-bd.on{opacity:1;pointer-events:all}
.menu-panel{
  position:fixed;top:0;right:0;bottom:0;width:300px;
  background:#fff;border-left:1px solid var(--border);
  z-index:1001;transform:translateX(100%);transition:transform .35s cubic-bezier(.16,1,.3,1);
  padding:28px;display:flex;flex-direction:column;overflow-y:auto;
}
.menu-panel.on{transform:none}
.menu-x{
  align-self:flex-end;width:34px;height:34px;border-radius:8px;
  background:var(--surface);border:1px solid var(--border);cursor:pointer;
  color:var(--ink-mid);font-size:16px;display:flex;align-items:center;justify-content:center;
  margin-bottom:28px;transition:background .2s,color .2s;
}
.menu-x:hover{background:var(--border);color:var(--ink)}
.menu-g{margin-bottom:24px}
.menu-g-title{font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--ink-light);margin-bottom:8px}
.menu-g a{
  display:block;font-size:15px;font-weight:500;color:var(--ink-mid);
  text-decoration:none;padding:8px 0;border-bottom:1px solid var(--border);
  transition:color .2s;
}
.menu-g a:last-child{border:none}
.menu-g a:hover{color:var(--purple)}
.menu-cta{
  margin-top:auto;display:block;text-align:center;
  background:var(--purple);color:#fff;padding:15px;border-radius:10px;
  font-weight:700;font-size:15px;text-decoration:none;
  transition:background .2s,transform .2s;
}
.menu-cta:hover{background:var(--purple-dark);transform:translateY(-1px)}

/* ===== HERO ===== */
.hero{
  min-height:100dvh;display:flex;align-items:center;
  padding:130px 48px 100px;
  position:relative;overflow:hidden;
  background:#ffffff;
}
/* gradient background */
.hero::before{
  content:'';position:absolute;inset:0;
  background:
    radial-gradient(ellipse 70% 60% at 60% 10%,rgba(108,99,255,.07) 0%,transparent 60%),
    radial-gradient(ellipse 50% 70% at 10% 80%,rgba(108,99,255,.05) 0%,transparent 60%),
    radial-gradient(ellipse 80% 40% at 100% 50%,rgba(168,139,250,.04) 0%,transparent 60%);
}
.hero-inner{
  position:relative;z-index:1;
  max-width:1240px;margin:0 auto;width:100%;
  display:grid;grid-template-columns:1fr 480px;align-items:center;gap:80px;
}
.hero-eyebrow{
  display:inline-flex;align-items:center;gap:8px;
  font-size:12px;font-weight:700;letter-spacing:1.4px;text-transform:uppercase;
  color:var(--purple);background:var(--purple-light);
  border-radius:100px;padding:7px 16px;margin-bottom:32px;
}
.hero-eyebrow-dot{
  width:6px;height:6px;border-radius:50%;background:var(--purple);
  animation:pulse 2.5s ease infinite;
}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(.7)}}
h1{
  font-size:clamp(52px,5.8vw,88px);
  font-weight:800;letter-spacing:-3px;line-height:.98;
  color:var(--ink);margin-bottom:28px;
}
h1 .accent{color:var(--purple)}
.hero-sub{
  font-size:19px;line-height:1.72;color:var(--ink-mid);
  max-width:500px;margin-bottom:48px;font-weight:400;
}
.hero-btns{display:flex;flex-wrap:wrap;gap:14px;align-items:center;margin-bottom:52px}
.btn-primary{
  font-size:15px;font-weight:700;
  background:var(--purple);color:#fff;
  padding:16px 32px;border-radius:10px;text-decoration:none;
  transition:background .2s,transform .2s,box-shadow .2s;
  box-shadow:0 4px 16px rgba(108,99,255,.25);
}
.btn-primary:hover{background:var(--purple-dark);transform:translateY(-2px);box-shadow:0 10px 32px rgba(108,99,255,.35)}
.btn-secondary{
  font-size:15px;font-weight:600;color:var(--ink-mid);
  padding:16px 28px;border-radius:10px;text-decoration:none;
  border:1.5px solid var(--border);
  transition:color .2s,border-color .2s,background .2s;
}
.btn-secondary:hover{color:var(--ink);border-color:rgba(108,99,255,.3);background:var(--purple-light)}
.hero-proof{display:flex;align-items:center;gap:14px}
.hero-proof-avatars{display:flex}
.hero-proof-av{
  width:34px;height:34px;border-radius:50%;border:2.5px solid #fff;
  background:linear-gradient(135deg,var(--purple),#a78bfa);
  display:flex;align-items:center;justify-content:center;
  font-size:11px;font-weight:800;color:#fff;margin-left:-10px;
  box-shadow:0 2px 8px rgba(0,0,0,.1);
}
.hero-proof-av:first-child{margin-left:0}
.hero-proof-text{font-size:13px;color:var(--ink-mid);font-weight:500}
.hero-proof-text strong{color:var(--ink);font-weight:700}

/* HERO VISUAL */
.hero-visual{position:relative;animation:float 6s ease-in-out infinite}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-12px)}}

.card-main{
  background:#fff;border-radius:20px;
  border:1px solid var(--border);
  box-shadow:0 32px 80px rgba(13,13,31,.1),0 8px 24px rgba(13,13,31,.06);
  overflow:hidden;
}
.card-header{
  padding:20px 24px;border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;
}
.card-header-title{font-size:14px;font-weight:700;color:var(--ink)}
.card-live{
  display:flex;align-items:center;gap:6px;
  font-size:11px;font-weight:700;color:#16a34a;
  background:#f0fdf4;border-radius:100px;padding:4px 10px;
}
.card-live-dot{width:5px;height:5px;border-radius:50%;background:#16a34a;animation:pulse 1.4s ease infinite}
.card-body{padding:20px 24px;display:flex;flex-direction:column;gap:12px}

.metric-row{
  display:grid;grid-template-columns:1fr 1fr;gap:12px;
}
.metric{
  background:var(--surface);border-radius:12px;padding:16px;
  border:1px solid var(--border);
}
.metric-l{font-size:11px;font-weight:600;color:var(--ink-light);text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px}
.metric-v{font-size:28px;font-weight:800;color:var(--ink);letter-spacing:-1px;line-height:1}
.metric-c{font-size:11px;font-weight:600;color:#16a34a;margin-top:5px}

.call-item{
  display:flex;align-items:center;justify-content:space-between;
  padding:13px 16px;background:var(--surface);border-radius:10px;
  border:1px solid var(--border);
}
.call-item-left{display:flex;align-items:center;gap:10px}
.call-av{
  width:34px;height:34px;border-radius:50%;
  background:linear-gradient(135deg,var(--purple),#a78bfa);
  display:flex;align-items:center;justify-content:center;
  font-size:11px;font-weight:800;color:#fff;flex-shrink:0;
}
.call-name{font-size:13px;font-weight:700;color:var(--ink)}
.call-detail{font-size:12px;color:var(--ink-light);margin-top:2px}
.call-badge{
  font-size:10px;font-weight:700;padding:4px 10px;border-radius:100px;white-space:nowrap;
}
.badge-green{background:#f0fdf4;color:#16a34a}
.badge-purple{background:var(--purple-light);color:var(--purple)}
.badge-gray{background:var(--surface);color:var(--ink-light);border:1px solid var(--border)}

.card-footer{
  padding:16px 24px;border-top:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;
}
.card-footer-stat{font-size:13px;font-weight:500;color:var(--ink-mid)}
.card-footer-stat strong{color:var(--purple);font-weight:800}

/* floating card */
.float-card{
  position:absolute;background:#fff;border-radius:14px;
  border:1px solid var(--border);padding:14px 16px;
  box-shadow:0 16px 40px rgba(13,13,31,.1);
  display:flex;align-items:center;gap:10px;
  animation:floatCard .8s cubic-bezier(.16,1,.3,1) both;
}
@keyframes floatCard{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
.float-card-1{top:-20px;right:-40px;animation-delay:.6s}
.float-card-2{bottom:20px;left:-48px;animation-delay:.9s}
.float-ico{font-size:22px}
.float-label{font-size:11px;font-weight:600;color:var(--ink-mid);line-height:1.3}
.float-val{font-size:15px;font-weight:800;color:var(--ink)}

/* ===== STATS BAND ===== */
.stats-band{
  background:var(--ink);padding:60px 48px;
}
.stats-inner{
  max-width:1240px;margin:0 auto;
  display:grid;grid-template-columns:repeat(5,1fr);
  gap:0;
}
.stat-item{
  padding:0 32px;
  border-right:1px solid rgba(255,255,255,.1);
  text-align:center;
}
.stat-item:first-child{padding-left:0;text-align:left}
.stat-item:last-child{border-right:none;text-align:right;padding-right:0}
.stat-n{
  font-size:44px;font-weight:800;letter-spacing:-2px;color:#fff;
  line-height:1;margin-bottom:8px;
}
.stat-n span{color:var(--purple)}
.stat-l{font-size:13px;color:rgba(255,255,255,.4);font-weight:500;line-height:1.5}

/* ===== HOW IT WORKS ===== */
.how{padding:140px 48px;background:#fff}
.s-inner{max-width:1240px;margin:0 auto}
.s-eyebrow{
  font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;
  color:var(--purple);margin-bottom:18px;display:block;
}
h2{
  font-size:clamp(38px,4vw,60px);font-weight:800;
  letter-spacing:-2px;line-height:1.05;color:var(--ink);margin-bottom:20px;
}
.s-sub{font-size:18px;line-height:1.75;color:var(--ink-mid);max-width:540px;font-weight:400}

.steps{
  display:grid;grid-template-columns:repeat(4,1fr);
  margin-top:80px;border:1px solid var(--border);border-radius:20px;
  overflow:hidden;
}
.step{
  padding:44px 36px;border-right:1px solid var(--border);
  background:#fff;transition:background .25s;
}
.step:last-child{border-right:none}
.step:hover{background:var(--surface)}
.step-num{
  width:36px;height:36px;border-radius:10px;
  background:var(--purple-light);
  display:flex;align-items:center;justify-content:center;
  font-size:13px;font-weight:800;color:var(--purple);
  margin-bottom:28px;
}
.step-title{font-size:18px;font-weight:800;color:var(--ink);margin-bottom:12px;letter-spacing:-.3px}
.step-body{font-size:14px;line-height:1.7;color:var(--ink-mid)}

/* ===== SPLITS ===== */
.splits{padding:0 48px 140px;background:#fff}
.split{
  max-width:1240px;margin:0 auto;
  display:grid;grid-template-columns:1fr 1fr;gap:100px;
  align-items:center;padding:100px 0;
  border-top:1px solid var(--border);
}
.split.flip .split-visual{order:-1}
.split-text .s-eyebrow{display:block}
.split-text h2{max-width:460px}
.split-text .s-sub{margin-top:20px;margin-bottom:36px;max-width:420px}
.split-link{
  display:inline-flex;align-items:center;gap:8px;
  font-size:15px;font-weight:700;color:var(--purple);text-decoration:none;
  transition:gap .2s;
}
.split-link:hover{gap:14px}

.split-visual-box{
  background:var(--surface);border:1px solid var(--border);
  border-radius:20px;padding:32px;overflow:hidden;
}
.vis-row{
  display:flex;align-items:center;justify-content:space-between;
  padding:15px 18px;background:#fff;border:1px solid var(--border);
  border-radius:12px;margin-bottom:10px;
}
.vis-row:last-child{margin-bottom:0}
.vis-row-l{font-size:14px;font-weight:500;color:var(--ink)}
.vis-row-r{font-size:13px;font-weight:700;color:var(--ink-mid)}
.pill-green{font-size:11px;font-weight:700;background:#f0fdf4;color:#16a34a;border-radius:100px;padding:4px 12px}
.pill-purple{font-size:11px;font-weight:700;background:var(--purple-light);color:var(--purple);border-radius:100px;padding:4px 12px}

.vis-bar-box{
  background:var(--surface);border:1px solid var(--border);
  border-radius:20px;padding:36px;
  display:flex;flex-direction:column;gap:24px;
}
.vb-item{}
.vb-top{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:10px}
.vb-label{font-size:14px;font-weight:600;color:var(--ink)}
.vb-val{font-size:22px;font-weight:800;color:var(--ink);letter-spacing:-.5px}
.vb-track{height:8px;background:var(--border);border-radius:4px;overflow:hidden}
.vb-fill{height:100%;border-radius:4px;background:linear-gradient(90deg,var(--purple),#a78bfa)}

/* ===== INDUSTRIES ===== */
.industries{padding:140px 48px;background:var(--surface)}
.ind-grid{
  display:grid;grid-template-columns:repeat(3,1fr);gap:20px;
  margin-top:80px;
}
.ind-card{
  background:#fff;border:1px solid var(--border);border-radius:20px;
  padding:44px;display:flex;flex-direction:column;
  text-decoration:none;
  transition:border-color .25s,box-shadow .35s,transform .35s cubic-bezier(.16,1,.3,1);
}
.ind-card:hover{
  border-color:rgba(108,99,255,.25);
  box-shadow:0 24px 60px rgba(108,99,255,.08);
  transform:translateY(-5px);
}
.ind-icon-wrap{
  width:60px;height:60px;border-radius:16px;
  background:var(--purple-light);display:flex;align-items:center;justify-content:center;
  font-size:28px;margin-bottom:28px;
}
.ind-name{font-size:22px;font-weight:800;color:var(--ink);letter-spacing:-.5px;margin-bottom:10px}
.ind-desc{font-size:15px;line-height:1.7;color:var(--ink-mid);flex:1;margin-bottom:28px}
.ind-link{
  display:flex;align-items:center;gap:8px;
  font-size:14px;font-weight:700;color:var(--purple);
  transition:gap .2s;
}
.ind-card:hover .ind-link{gap:12px}

/* ===== TESTIMONIALS ===== */
.testimonials{padding:140px 48px;background:#fff}
.test-grid{
  display:grid;grid-template-columns:repeat(3,1fr);gap:24px;
  margin-top:80px;
}
.test-card{
  background:var(--surface);border:1px solid var(--border);
  border-radius:20px;padding:40px;
  transition:border-color .25s,box-shadow .25s;
}
.test-card:hover{border-color:rgba(108,99,255,.2);box-shadow:0 12px 40px rgba(108,99,255,.06)}
.test-stars{display:flex;gap:3px;margin-bottom:24px}
.test-star{font-size:16px;color:#f59e0b}
.test-quote{
  font-size:16px;line-height:1.78;color:var(--ink-mid);
  margin-bottom:28px;font-weight:400;
}
.test-author{display:flex;align-items:center;gap:13px}
.test-av{
  width:42px;height:42px;border-radius:50%;flex-shrink:0;
  background:linear-gradient(135deg,var(--purple),#a78bfa);
  display:flex;align-items:center;justify-content:center;
  font-size:13px;font-weight:800;color:#fff;
}
.test-name{font-size:14px;font-weight:700;color:var(--ink);margin-bottom:2px}
.test-role{font-size:12px;color:var(--ink-light)}

/* ===== CTA ===== */
.cta-section{
  padding:140px 48px;
  background:var(--purple);
  position:relative;overflow:hidden;
}
.cta-section::before{
  content:'';position:absolute;
  top:-300px;right:-200px;width:700px;height:700px;border-radius:50%;
  background:rgba(255,255,255,.05);pointer-events:none;
}
.cta-section::after{
  content:'';position:absolute;
  bottom:-200px;left:-100px;width:500px;height:500px;border-radius:50%;
  background:rgba(0,0,0,.06);pointer-events:none;
}
.cta-inner{max-width:860px;margin:0 auto;text-align:center;position:relative;z-index:1}
.cta-eyebrow{
  font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;
  color:rgba(255,255,255,.6);margin-bottom:22px;display:block;
}
.cta-h2{
  font-size:clamp(44px,5vw,72px);font-weight:800;
  letter-spacing:-2.5px;line-height:1.02;color:#fff;margin-bottom:24px;
}
.cta-sub{font-size:18px;line-height:1.75;color:rgba(255,255,255,.7);margin-bottom:52px;font-weight:400}
.cta-btns{display:flex;flex-wrap:wrap;gap:14px;justify-content:center}
.btn-white{
  font-size:15px;font-weight:800;
  background:#fff;color:var(--purple);
  padding:18px 36px;border-radius:10px;text-decoration:none;
  transition:transform .2s,box-shadow .2s;
  box-shadow:0 8px 24px rgba(0,0,0,.15);
}
.btn-white:hover{transform:translateY(-2px);box-shadow:0 14px 36px rgba(0,0,0,.2)}
.btn-white-outline{
  font-size:15px;font-weight:700;color:#fff;
  padding:18px 32px;border-radius:10px;text-decoration:none;
  border:1.5px solid rgba(255,255,255,.35);
  transition:background .2s,border-color .2s;
}
.btn-white-outline:hover{background:rgba(255,255,255,.1);border-color:rgba(255,255,255,.7)}
.cta-note{font-size:13px;color:rgba(255,255,255,.45);margin-top:24px}

/* ===== FOOTER ===== */
footer{background:var(--ink);padding:100px 48px 48px}
.ft-inner{max-width:1240px;margin:0 auto}
.ft-top{display:grid;grid-template-columns:1.5fr 1fr 1fr 1fr;gap:56px;margin-bottom:80px}
.ft-logo-wrap{display:flex;align-items:center;gap:11px;text-decoration:none;margin-bottom:18px}
.ft-logo-name{font-size:16px;font-weight:800;color:#fff}
.ft-logo-sub{font-size:7.5px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:var(--purple);display:block;margin-top:3px}
.ft-desc{font-size:14px;line-height:1.75;color:rgba(255,255,255,.35);max-width:260px;margin-bottom:22px}
.ft-contact a{display:block;font-size:13px;color:rgba(255,255,255,.3);text-decoration:none;margin-bottom:6px;transition:color .2s}
.ft-contact a:hover{color:rgba(255,255,255,.8)}
.ft-col-h{font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:rgba(255,255,255,.25);margin-bottom:18px}
.ft-col a{display:block;font-size:14px;color:rgba(255,255,255,.4);text-decoration:none;margin-bottom:12px;transition:color .2s}
.ft-col a:last-child{margin:0}
.ft-col a:hover{color:rgba(255,255,255,.9)}
.ft-bottom{padding-top:40px;border-top:1px solid rgba(255,255,255,.07);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px}
.ft-copy{font-size:13px;color:rgba(255,255,255,.2)}
.ft-legal{display:flex;gap:24px}
.ft-legal a{font-size:13px;color:rgba(255,255,255,.2);text-decoration:none;transition:color .2s}
.ft-legal a:hover{color:rgba(255,255,255,.6)}

/* RESPONSIVE */
@media(max-width:1100px){
  .hero-inner{grid-template-columns:1fr;gap:0}
  .hero-visual{display:none}
  h1{letter-spacing:-2px}
  .steps{grid-template-columns:1fr 1fr}
  .step{border-right:none;border-bottom:1px solid var(--border)}
  .step:nth-child(odd){border-right:1px solid var(--border)}
  .split{grid-template-columns:1fr;gap:56px}
  .split.flip .split-visual{order:unset}
  .ind-grid{grid-template-columns:1fr 1fr}
  .test-grid{grid-template-columns:1fr}
  .ft-top{grid-template-columns:1fr 1fr}
  .stats-inner{grid-template-columns:repeat(3,1fr);row-gap:32px}
  .stat-item:nth-child(3){border-right:none}
  .stat-item:nth-child(4){padding-left:0;text-align:left}
  .stat-item{text-align:center!important;padding:0 24px!important}
  .stat-item:first-child,.stat-item:last-child{text-align:center!important}
}
@media(max-width:768px){
  nav{padding:0 20px}
  .nav-links,.btn-nav-ghost{display:none}
  .hero,.how,.splits,.industries,.testimonials,.cta-section,footer,.stats-band{padding-left:20px;padding-right:20px}
  .hero{padding-top:110px;padding-bottom:80px}
  h1{font-size:clamp(44px,9vw,64px);letter-spacing:-1.5px}
  .steps{grid-template-columns:1fr}
  .step:nth-child(odd){border-right:none}
  .ind-grid{grid-template-columns:1fr}
  .ft-top{grid-template-columns:1fr}
  .ft-bottom{flex-direction:column;text-align:center}
  .stats-inner{grid-template-columns:1fr 1fr}
  .stat-item:nth-child(3){border-right:1px solid rgba(255,255,255,.1)}
  .stat-item{border-bottom:1px solid rgba(255,255,255,.07)!important;padding-bottom:24px!important;margin-bottom:0}
  .stats-band{padding:48px 20px}
}
</style>
</head>
<body>

<!-- NAV -->
<nav id="nav">
  <a href="/" class="logo">
    <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
      <rect x="3" y="20" width="6" height="9" rx="2.5" fill="#6C63FF"/>
      <rect x="13" y="13" width="6" height="16" rx="2.5" fill="#6C63FF"/>
      <rect x="23" y="7" width="6" height="22" rx="2.5" fill="#6C63FF"/>
    </svg>
    <div class="logo-text">
      <span class="logo-name">Syntharra</span>
      <span class="logo-sub">Global AI Solutions</span>
    </div>
  </a>
  <ul class="nav-links">
    <li><a href="/how-it-works.html">How It Works</a></li>
    <li><a href="/hvac.html">HVAC</a></li>
    <li><a href="/case-studies.html">Case Studies</a></li>
    <li><a href="/faq.html">FAQ</a></li>
  </ul>
  <div class="nav-right">
    <a href="/calculator.html" class="btn-nav-ghost">Revenue Calculator</a>
    <a href="/demo.html" class="btn-nav">Get a Demo</a>
    <button class="hamburger" id="hbg" aria-label="Menu">
      <span></span><span></span><span></span>
    </button>
  </div>
</nav>

<!-- MENU -->
<div class="menu-bd" id="bd"></div>
<div class="menu-panel" id="mp">
  <button class="menu-x" id="mx">&#x2715;</button>
  <div class="menu-g">
    <div class="menu-g-title">Product</div>
    <a href="/how-it-works.html">How It Works</a>
    <a href="/demo.html">Live Demo</a>
    <a href="/faq.html">FAQ</a>
    <a href="/ai-readiness.html">AI Readiness Score</a>
    <a href="/calculator.html">Revenue Calculator</a>
  </div>
  <div class="menu-g">
    <div class="menu-g-title">Learn</div>
    <a href="/case-studies.html">Case Studies</a>
    <a href="/blog.html">Blog</a>
  </div>
  <div class="menu-g">
    <div class="menu-g-title">Industries</div>
    <a href="/hvac.html">HVAC</a>
    <a href="/plumbing.html">Plumbing</a>
    <a href="/electrical.html">Electrical</a>
  </div>
  <div class="menu-g">
    <div class="menu-g-title">Company</div>
    <a href="/about.html">About</a>
    <a href="/affiliate.html">Affiliate Program</a>
    <a href="/careers.html">Careers</a>
    <a href="/status.html">System Status</a>
  </div>
  <a href="/demo.html" class="menu-cta">Book a Free Demo &rarr;</a>
</div>

<!-- HERO -->
<section class="hero">
  <div class="hero-inner">
    <div class="sr">
      <div class="hero-eyebrow">
        <span class="hero-eyebrow-dot"></span>
        AI Voice Agents &mdash; Live 24/7
      </div>
      <h1>Never miss a<br>service call.<br><span class="accent">Ever again.</span></h1>
      <p class="hero-sub">Syntharra deploys AI voice agents that answer every call, book jobs automatically, and cover your phones 24/7 &mdash; so your trade business grows without you being glued to the phone.</p>
      <div class="hero-btns">
        <a href="/demo.html" class="btn-primary">See It In Action &rarr;</a>
        <a href="/calculator.html" class="btn-secondary">Calculate Your Revenue Gap</a>
      </div>
      <div class="hero-proof">
        <div class="hero-proof-avatars">
          <div class="hero-proof-av">MT</div>
          <div class="hero-proof-av">JS</div>
          <div class="hero-proof-av">RC</div>
          <div class="hero-proof-av">AB</div>
        </div>
        <div class="hero-proof-text"><strong>40+ trade businesses</strong> already using Syntharra</div>
      </div>
    </div>
    <div class="hero-visual sr d2">
      <div class="card-main">
        <div class="card-header">
          <span class="card-header-title">Today&rsquo;s Performance</span>
          <div class="card-live"><div class="card-live-dot"></div> Live</div>
        </div>
        <div class="card-body">
          <div class="metric-row">
            <div class="metric">
              <div class="metric-l">Calls Handled</div>
              <div class="metric-v">47</div>
              <div class="metric-c">&#8593; 23% this week</div>
            </div>
            <div class="metric">
              <div class="metric-l">Revenue Added</div>
              <div class="metric-v">$8.4k</div>
              <div class="metric-c">&#8593; This month</div>
            </div>
          </div>
          <div class="call-item">
            <div class="call-item-left">
              <div class="call-av">MT</div>
              <div>
                <div class="call-name">Mike T. &mdash; AC Repair</div>
                <div class="call-detail">Booked: Thu 2pm &bull; Est. $380&ndash;520</div>
              </div>
            </div>
            <div class="call-badge badge-green">Booked</div>
          </div>
          <div class="call-item">
            <div class="call-item-left">
              <div class="call-av" style="background:linear-gradient(135deg,#06b6d4,#0891b2)">SL</div>
              <div>
                <div class="call-name">Sarah L. &mdash; Furnace Service</div>
                <div class="call-detail">Booking in progress&hellip;</div>
              </div>
            </div>
            <div class="call-badge badge-purple">Live</div>
          </div>
          <div class="call-item">
            <div class="call-item-left">
              <div class="call-av" style="background:linear-gradient(135deg,#f59e0b,#d97706)">RK</div>
              <div>
                <div class="call-name">Rob K. &mdash; Drain Cleaning</div>
                <div class="call-detail">After-hours &bull; Booked: Fri 9am</div>
              </div>
            </div>
            <div class="call-badge badge-green">Booked</div>
          </div>
        </div>
        <div class="card-footer">
          <span class="card-footer-stat">Jobs booked today: <strong>12</strong></span>
          <span class="card-footer-stat">Missed calls: <strong style="color:#16a34a">0</strong></span>
        </div>
      </div>
      <div class="float-card float-card-1">
        <div class="float-ico">&#9989;</div>
        <div>
          <div class="float-label">After-hours call answered</div>
          <div class="float-val">2:47am &bull; Booked</div>
        </div>
      </div>
      <div class="float-card float-card-2">
        <div class="float-ico">&#128176;</div>
        <div>
          <div class="float-label">Revenue recovered</div>
          <div class="float-val">+$1,240 this week</div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- STATS BAND -->
<div class="stats-band">
  <div class="stats-inner">
    <div class="stat-item sr d1">
      <div class="stat-n">97<span>%</span></div>
      <div class="stat-l">Call answer rate</div>
    </div>
    <div class="stat-item sr d2">
      <div class="stat-n">24/7</div>
      <div class="stat-l">Always on, never sleeps</div>
    </div>
    <div class="stat-item sr d3">
      <div class="stat-n">&lt;3<span>min</span></div>
      <div class="stat-l">Average time to go live</div>
    </div>
    <div class="stat-item sr d4">
      <div class="stat-n">$10<span>k+</span></div>
      <div class="stat-l">Avg. monthly revenue added</div>
    </div>
    <div class="stat-item sr d5">
      <div class="stat-n">0</div>
      <div class="stat-l">Missed calls after go-live</div>
    </div>
  </div>
</div>

<!-- HOW IT WORKS -->
<section class="how">
  <div class="s-inner">
    <div class="sr">
      <span class="s-eyebrow">How It Works</span>
      <h2>Live in minutes.<br>No setup required.</h2>
      <p class="s-sub">We handle everything. Fill out one form &mdash; we deploy a trained AI agent that sounds like your own front desk staff and starts booking jobs immediately.</p>
    </div>
    <div class="steps">
      <div class="step sr d1">
        <div class="step-num">01</div>
        <div class="step-title">Onboard in 5 minutes</div>
        <p class="step-body">Fill out a short form with your services, service area, pricing, and hours. No technical knowledge needed.</p>
      </div>
      <div class="step sr d2">
        <div class="step-num">02</div>
        <div class="step-title">We train your agent</div>
        <p class="step-body">Your AI learns your business &mdash; how to qualify leads, answer questions, and book jobs directly into your calendar.</p>
      </div>
      <div class="step sr d3">
        <div class="step-num">03</div>
        <div class="step-title">Forward your number</div>
        <p class="step-body">Point your business line to Syntharra. Works with any phone system in under 60 seconds. No new hardware.</p>
      </div>
      <div class="step sr d4">
        <div class="step-num">04</div>
        <div class="step-title">Watch revenue grow</div>
        <p class="step-body">Every call answered. Every job booked. Your dashboard shows every call, booking, and dollar recovered in real time.</p>
      </div>
    </div>
  </div>
</section>

<!-- FEATURE SPLITS -->
<div class="splits">

  <div class="split">
    <div class="split-text sr-l">
      <span class="s-eyebrow">Natural Conversation</span>
      <h2>Books jobs,<br>not just messages.</h2>
      <p class="s-sub">Your AI doesn&rsquo;t just take a name and number. It qualifies the lead, checks availability, gives a price range, and books directly into your calendar. Callers never know it&rsquo;s AI.</p>
      <a href="/how-it-works.html" class="split-link">See how it works &rarr;</a>
    </div>
    <div class="split-visual sr-r">
      <div class="vis-row">
        <span class="vis-row-l">&#128222; Incoming: Sarah M.</span>
        <span class="pill-green">Live</span>
      </div>
      <div class="vis-row">
        <span class="vis-row-l">Service identified</span>
        <span class="vis-row-r">AC Not Cooling</span>
      </div>
      <div class="vis-row">
        <span class="vis-row-l">Lead qualified</span>
        <span class="pill-green">&#10003; Yes</span>
      </div>
      <div class="vis-row">
        <span class="vis-row-l">Appointment booked</span>
        <span class="vis-row-r">Thu 2:00pm</span>
      </div>
      <div class="vis-row">
        <span class="vis-row-l">SMS confirmation sent</span>
        <span class="pill-green">&#10003; Sent</span>
      </div>
      <div class="vis-row">
        <span class="vis-row-l">Estimated job value</span>
        <span class="vis-row-r" style="color:var(--ink);font-size:15px">$380&ndash;$520</span>
      </div>
    </div>
  </div>

  <div class="split flip">
    <div class="split-text sr-r">
      <span class="s-eyebrow">After-Hours Coverage</span>
      <h2>The calls you&rsquo;re<br>missing right now.</h2>
      <p class="s-sub">Most missed calls happen outside business hours. Your Syntharra agent handles every single one &mdash; nights, weekends, holidays &mdash; without overtime pay or voicemail.</p>
      <a href="/calculator.html" class="split-link">Calculate your revenue gap &rarr;</a>
    </div>
    <div class="split-visual sr-l">
      <div class="vis-bar-box">
        <div class="vb-item">
          <div class="vb-top">
            <span class="vb-label">Business hours answered</span>
            <span class="vb-val">100%</span>
          </div>
          <div class="vb-track"><div class="vb-fill" data-w="100" style="width:0"></div></div>
        </div>
        <div class="vb-item">
          <div class="vb-top">
            <span class="vb-label">After-hours answered</span>
            <span class="vb-val">100%</span>
          </div>
          <div class="vb-track"><div class="vb-fill" data-w="100" style="width:0"></div></div>
        </div>
        <div class="vb-item">
          <div class="vb-top">
            <span class="vb-label">Calls converted to bookings</span>
            <span class="vb-val">74%</span>
          </div>
          <div class="vb-track"><div class="vb-fill" data-w="74" style="width:0"></div></div>
        </div>
        <div class="vb-item">
          <div class="vb-top">
            <span class="vb-label">Customer satisfaction</span>
            <span class="vb-val">4.9 / 5</span>
          </div>
          <div class="vb-track"><div class="vb-fill" data-w="98" style="width:0"></div></div>
        </div>
      </div>
    </div>
  </div>

  <div class="split">
    <div class="split-text sr-l">
      <span class="s-eyebrow">Real-Time Dashboard</span>
      <h2>Every call. Every<br>dollar. One screen.</h2>
      <p class="s-sub">See every call, booking, and dollar recovered in a clean dashboard built for trade business owners. No spreadsheets, no manual tracking, no guessing.</p>
      <a href="/demo.html" class="split-link">See the demo &rarr;</a>
    </div>
    <div class="split-visual sr-r">
      <div class="vis-row">
        <span class="vis-row-l">Calls handled today</span>
        <span class="vis-row-r" style="font-size:18px;color:var(--ink)">47</span>
      </div>
      <div class="vis-row">
        <span class="vis-row-l">Jobs booked today</span>
        <span class="vis-row-r" style="font-size:18px;color:var(--ink)">12</span>
      </div>
      <div class="vis-row">
        <span class="vis-row-l">Revenue added this month</span>
        <span class="vis-row-r" style="font-size:18px;color:#16a34a;font-weight:800">$8,420</span>
      </div>
      <div class="vis-row">
        <span class="vis-row-l">Missed calls</span>
        <span class="pill-green">0</span>
      </div>
      <div class="vis-row">
        <span class="vis-row-l">Agent uptime</span>
        <span class="pill-purple">100%</span>
      </div>
    </div>
  </div>

</div>

<!-- INDUSTRIES -->
<section class="industries">
  <div class="s-inner">
    <div class="sr">
      <span class="s-eyebrow">Industries</span>
      <h2>Built for the trades.<br>Not generic call centres.</h2>
      <p class="s-sub">Syntharra agents are trained specifically on HVAC, plumbing, and electrical &mdash; the terminology, job types, and pricing conversations your customers expect.</p>
    </div>
    <div class="ind-grid">
      <a href="/hvac.html" class="ind-card sr d1">
        <div class="ind-icon-wrap">&#10052;&#65039;</div>
        <div class="ind-name">HVAC</div>
        <p class="ind-desc">AC repair, furnace service, duct cleaning, system installs &mdash; your AI agent knows every job type and books them effortlessly.</p>
        <div class="ind-link">Explore HVAC &rarr;</div>
      </a>
      <a href="/plumbing.html" class="ind-card sr d2">
        <div class="ind-icon-wrap">&#128166;</div>
        <div class="ind-name">Plumbing</div>
        <p class="ind-desc">Emergency leaks, drain cleaning, water heater service &mdash; capture every call before your competitor picks it up.</p>
        <div class="ind-link">Explore Plumbing &rarr;</div>
      </a>
      <a href="/electrical.html" class="ind-card sr d3">
        <div class="ind-icon-wrap">&#9889;</div>
        <div class="ind-name">Electrical</div>
        <p class="ind-desc">Panel upgrades, EV charger installs, service calls &mdash; your agent qualifies and books every lead automatically.</p>
        <div class="ind-link">Explore Electrical &rarr;</div>
      </a>
    </div>
  </div>
</section>

<!-- TESTIMONIALS -->
<section class="testimonials">
  <div class="s-inner">
    <div class="sr">
      <span class="s-eyebrow">Results</span>
      <h2>Real businesses.<br>Real revenue.</h2>
      <p class="s-sub">Trade business owners who switched to Syntharra don&rsquo;t go back.</p>
    </div>
    <div class="test-grid">
      <div class="test-card sr d1">
        <div class="test-stars">
          <span class="test-star">&#9733;</span><span class="test-star">&#9733;</span>
          <span class="test-star">&#9733;</span><span class="test-star">&#9733;</span>
          <span class="test-star">&#9733;</span>
        </div>
        <p class="test-quote">&ldquo;We were losing 8&ndash;10 calls a week after hours. Syntharra fixed that in the first 24 hours. Within a month we&rsquo;d recovered over $14k in jobs we would have missed entirely.&rdquo;</p>
        <div class="test-author">
          <div class="test-av">MT</div>
          <div>
            <div class="test-name">Mark T.</div>
            <div class="test-role">Owner, Arctic Breeze HVAC &bull; Phoenix, AZ</div>
          </div>
        </div>
      </div>
      <div class="test-card sr d2">
        <div class="test-stars">
          <span class="test-star">&#9733;</span><span class="test-star">&#9733;</span>
          <span class="test-star">&#9733;</span><span class="test-star">&#9733;</span>
          <span class="test-star">&#9733;</span>
        </div>
        <p class="test-quote">&ldquo;My receptionist cost $3,200 a month and still missed calls on busy days. Syntharra costs less and never misses. It&rsquo;s not even a comparison anymore.&rdquo;</p>
        <div class="test-author">
          <div class="test-av">JS</div>
          <div>
            <div class="test-name">Jason S.</div>
            <div class="test-role">Owner, Reliable Plumbing Co. &bull; Denver, CO</div>
          </div>
        </div>
      </div>
      <div class="test-card sr d3">
        <div class="test-stars">
          <span class="test-star">&#9733;</span><span class="test-star">&#9733;</span>
          <span class="test-star">&#9733;</span><span class="test-star">&#9733;</span>
          <span class="test-star">&#9733;</span>
        </div>
        <p class="test-quote">&ldquo;I was skeptical about AI on the phone, but customers genuinely can&rsquo;t tell. We booked 40+ jobs in the first month. The ROI is insane for a small electrical shop.&rdquo;</p>
        <div class="test-author">
          <div class="test-av">RC</div>
          <div>
            <div class="test-name">Rachel C.</div>
            <div class="test-role">Owner, Bright Spark Electric &bull; Austin, TX</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- CTA -->
<section class="cta-section">
  <div class="cta-inner sr">
    <span class="cta-eyebrow">Get Started Today</span>
    <h2 class="cta-h2">Every missed call is<br>revenue left behind.</h2>
    <p class="cta-sub">Every unanswered call costs your business $400&ndash;$800 on average. Syntharra makes sure that never happens again &mdash; starting today.</p>
    <div class="cta-btns">
      <a href="/demo.html" class="btn-white">Get Your Free Demo</a>
      <a href="/calculator.html" class="btn-white-outline">Calculate Your Revenue Gap</a>
    </div>
    <p class="cta-note">No contract &bull; No technical setup &bull; Live in under 3 minutes</p>
  </div>
</section>

<!-- FOOTER -->
<footer>
  <div class="ft-inner">
    <div class="ft-top">
      <div>
        <a href="/" class="ft-logo-wrap">
          <svg width="28" height="28" viewBox="0 0 32 32" fill="none">
            <rect x="3" y="20" width="6" height="9" rx="2.5" fill="#6C63FF"/>
            <rect x="13" y="13" width="6" height="16" rx="2.5" fill="#6C63FF"/>
            <rect x="23" y="7" width="6" height="22" rx="2.5" fill="#6C63FF"/>
          </svg>
          <div>
            <span class="ft-logo-name">Syntharra</span>
            <span class="ft-logo-sub">Global AI Solutions</span>
          </div>
        </a>
        <p class="ft-desc">AI voice agents for trade businesses. Never miss a call. Never lose a job to voicemail again.</p>
        <div class="ft-contact">
          <a href="mailto:support@syntharra.com">support@syntharra.com</a>
          <a href="mailto:feedback@syntharra.com">feedback@syntharra.com</a>
        </div>
      </div>
      <div>
        <div class="ft-col-h">Product</div>
        <div class="ft-col">
          <a href="/how-it-works.html">How It Works</a>
          <a href="/demo.html">Live Demo</a>
          <a href="/calculator.html">Revenue Calculator</a>
          <a href="/ai-readiness.html">AI Readiness Score</a>
          <a href="/faq.html">FAQ</a>
        </div>
      </div>
      <div>
        <div class="ft-col-h">Industries</div>
        <div class="ft-col">
          <a href="/hvac.html">HVAC</a>
          <a href="/plumbing.html">Plumbing</a>
          <a href="/electrical.html">Electrical</a>
        </div>
        <div class="ft-col-h" style="margin-top:28px">Learn</div>
        <div class="ft-col">
          <a href="/case-studies.html">Case Studies</a>
          <a href="/blog.html">Blog</a>
        </div>
      </div>
      <div>
        <div class="ft-col-h">Company</div>
        <div class="ft-col">
          <a href="/about.html">About</a>
          <a href="/affiliate.html">Affiliates</a>
          <a href="/careers.html">Careers</a>
          <a href="/status.html">System Status</a>
        </div>
        <div class="ft-col-h" style="margin-top:28px">Legal</div>
        <div class="ft-col">
          <a href="/privacy.html">Privacy Policy</a>
          <a href="/terms.html">Terms of Service</a>
          <a href="/security.html">Security</a>
        </div>
      </div>
    </div>
    <div class="ft-bottom">
      <div class="ft-copy">&copy; 2026 Syntharra Global AI Solutions. All rights reserved.</div>
      <div class="ft-legal">
        <a href="/privacy.html">Privacy</a>
        <a href="/terms.html">Terms</a>
        <a href="/security.html">Security</a>
      </div>
    </div>
  </div>
</footer>

<script>
// Nav
const nav = document.getElementById('nav');
window.addEventListener('scroll', () => {
  nav.classList.toggle('scrolled', window.scrollY > 30);
}, {passive: true});

// Menu
const open = () => { mp.classList.add('on'); bd.classList.add('on'); document.body.style.overflow='hidden'; };
const close = () => { mp.classList.remove('on'); bd.classList.remove('on'); document.body.style.overflow=''; };
document.getElementById('hbg').addEventListener('click', open);
document.getElementById('mx').addEventListener('click', close);
document.getElementById('bd').addEventListener('click', close);

// Scroll reveal
const obs = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('in'); });
}, { threshold: 0.08, rootMargin: '0px 0px -32px 0px' });
document.querySelectorAll('.sr,.sr-l,.sr-r').forEach(el => obs.observe(el));

// Animated bars
const barObs = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.style.width = e.target.dataset.w + '%';
      barObs.unobserve(e.target);
    }
  });
}, { threshold: 0.3 });
document.querySelectorAll('.vb-fill').forEach(b => barObs.observe(b));
</script>

</body>
</html>'''

print("Fetching SHA...")
r = requests.get(API, headers=HEADERS)
r.raise_for_status()
sha = r.json()["sha"]
print(f"SHA: {sha}")

assert HTML.count("<style>") == 1
print("Style OK")

payload = {
    "message": "feat(website): premium light homepage — Stripe/Intercom quality, white base, bold fills, 88px headline, clean splits",
    "content": base64.b64encode(HTML.encode('utf-8')).decode(),
    "sha": sha
}

resp = requests.put(API, headers=HEADERS, data=json.dumps(payload))
if resp.status_code in (200, 201):
    print(f"SUCCESS — {resp.json()['commit']['sha'][:8]}")
    print("Live at https://syntharra.com in ~60-90s")
else:
    print(f"FAILED {resp.status_code}")
    sys.stdout.buffer.write(resp.text.encode('utf-8'))
    sys.exit(1)
