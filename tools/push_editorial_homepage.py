#!/usr/bin/env python3
"""Push editorial dark-to-light homepage — diagonal flow, mixed layouts, Bricolage Grotesque"""
import requests, base64, json, sys

TOKEN = "GITHUB_TOKEN_REDACTED"
REPO = "Syntharra/syntharra-website"
FILE = "index.html"
API = f"https://api.github.com/repos/{REPO}/contents/{FILE}"
HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}

HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Syntharra — AI Voice Agents for Trade Businesses</title>
<meta name="description" content="Never miss a service call again. Syntharra deploys AI voice agents that answer every call, book jobs, and grow your trade business — 24/7, automatically.">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,500;12..96,700;12..96,800&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
body{font-family:'DM Sans',sans-serif;background:#ffffff;color:#0c0c1d;overflow-x:clip}

:root{
  --ink:#0c0c1d;
  --hero-bg:#06060d;
  --purple:#6C63FF;
  --purple-mid:#8B84FF;
  --purple-dim:rgba(108,99,255,.12);
  --muted:rgba(255,255,255,.5);
  --muted-ink:#5c5c7a;
  --border-light:#e8e8f2;
  --surface:#f7f7fb;
  --white:#ffffff;
}

/* REVEAL */
.rv{opacity:0;transform:translateY(36px);transition:opacity .9s cubic-bezier(.16,1,.3,1),transform .9s cubic-bezier(.16,1,.3,1)}
.rv.on{opacity:1;transform:none}
.rv-l{opacity:0;transform:translateX(-36px);transition:opacity .9s cubic-bezier(.16,1,.3,1),transform .9s cubic-bezier(.16,1,.3,1)}
.rv-l.on{opacity:1;transform:none}
.rv-r{opacity:0;transform:translateX(36px);transition:opacity .9s cubic-bezier(.16,1,.3,1),transform .9s cubic-bezier(.16,1,.3,1)}
.rv-r.on{opacity:1;transform:none}
.rv-s{opacity:0;transform:scale(.94);transition:opacity .8s cubic-bezier(.16,1,.3,1),transform .8s cubic-bezier(.16,1,.3,1)}
.rv-s.on{opacity:1;transform:none}
.d1{transition-delay:.06s}.d2{transition-delay:.13s}.d3{transition-delay:.2s}.d4{transition-delay:.27s}.d5{transition-delay:.34s}

/* ===== NAV ===== */
nav{
  position:fixed;top:0;left:0;right:0;z-index:900;
  height:68px;padding:0 48px;
  display:flex;align-items:center;justify-content:space-between;
}
nav.lit{
  background:rgba(255,255,255,.92);
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  box-shadow:0 1px 0 var(--border-light);
}
.logo{display:flex;align-items:center;gap:10px;text-decoration:none}
.logo-text{line-height:1}
.logo-name{
  font-family:'Bricolage Grotesque',sans-serif;
  font-size:17px;font-weight:800;letter-spacing:-.3px;color:#fff;
  transition:color .3s;
}
nav.lit .logo-name{color:var(--ink)}
.logo-sub{font-size:7.5px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:var(--purple);margin-top:3px;display:block}
.nav-links{display:flex;align-items:center;gap:34px;list-style:none}
.nav-links a{font-size:14px;font-weight:500;color:rgba(255,255,255,.6);text-decoration:none;transition:color .2s}
.nav-links a:hover{color:#fff}
nav.lit .nav-links a{color:var(--muted-ink)}
nav.lit .nav-links a:hover{color:var(--ink)}
.nav-r{display:flex;align-items:center;gap:10px}
.btn-ghost-nav{font-size:14px;font-weight:500;color:rgba(255,255,255,.6);text-decoration:none;padding:8px 14px;border-radius:8px;transition:color .2s,background .2s}
.btn-ghost-nav:hover{color:#fff;background:rgba(255,255,255,.07)}
nav.lit .btn-ghost-nav{color:var(--muted-ink)}
nav.lit .btn-ghost-nav:hover{color:var(--ink);background:var(--surface)}
.btn-cta-nav{
  font-family:'Bricolage Grotesque',sans-serif;
  font-size:13px;font-weight:700;letter-spacing:.1px;
  background:var(--purple);color:#fff;
  padding:10px 22px;border-radius:10px;text-decoration:none;
  transition:background .2s,transform .2s,box-shadow .2s;
}
.btn-cta-nav:hover{background:#5850e8;transform:translateY(-1px);box-shadow:0 6px 20px rgba(108,99,255,.4)}
.hamburger{display:flex;flex-direction:column;gap:5px;background:none;border:none;cursor:pointer;padding:8px}
.hamburger span{display:block;width:22px;height:1.5px;background:rgba(255,255,255,.7);border-radius:2px;transition:background .3s}
nav.lit .hamburger span{background:var(--muted-ink)}

/* MENU */
.menu-bd{position:fixed;inset:0;background:rgba(6,6,13,.65);z-index:1000;opacity:0;pointer-events:none;transition:opacity .25s;backdrop-filter:blur(6px)}
.menu-bd.on{opacity:1;pointer-events:all}
.menu-panel{
  position:fixed;top:0;right:0;bottom:0;width:300px;
  background:#fff;border-left:1px solid var(--border-light);
  z-index:1001;transform:translateX(100%);transition:transform .38s cubic-bezier(.16,1,.3,1);
  padding:28px;display:flex;flex-direction:column;overflow-y:auto;
}
.menu-panel.on{transform:none}
.menu-x{align-self:flex-end;width:34px;height:34px;border-radius:8px;background:var(--surface);border:1px solid var(--border-light);cursor:pointer;color:var(--muted-ink);font-size:16px;display:flex;align-items:center;justify-content:center;margin-bottom:28px;transition:.2s}
.menu-x:hover{background:var(--border-light);color:var(--ink)}
.menu-g{margin-bottom:22px}
.menu-g-t{font-size:10px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:#aaa;margin-bottom:8px}
.menu-g a{display:block;font-size:15px;font-weight:500;color:var(--muted-ink);text-decoration:none;padding:8px 0;border-bottom:1px solid var(--border-light);transition:color .2s}
.menu-g a:last-child{border:none}
.menu-g a:hover{color:var(--purple)}
.menu-cta{margin-top:auto;display:block;text-align:center;background:var(--purple);color:#fff;padding:14px;border-radius:10px;font-family:'Bricolage Grotesque',sans-serif;font-weight:700;font-size:15px;text-decoration:none;transition:.2s}
.menu-cta:hover{background:#5850e8;transform:translateY(-1px)}

/* ===== HERO ===== */
.hero{
  background:var(--hero-bg);
  min-height:100dvh;display:flex;align-items:center;
  padding:110px 48px 180px;
  position:relative;overflow:hidden;
  /* diagonal bottom */
  clip-path:polygon(0 0, 100% 0, 100% calc(100% - 80px), 0 100%);
  margin-bottom:-2px;
}
/* ambient glow */
.hero::before{
  content:'';position:absolute;
  top:-20%;right:-10%;
  width:70vw;height:70vw;border-radius:50%;
  background:radial-gradient(ellipse,rgba(108,99,255,.14) 0%,transparent 65%);
  pointer-events:none;
}
.hero::after{
  content:'';position:absolute;
  bottom:0;left:-5%;
  width:50vw;height:40vw;border-radius:50%;
  background:radial-gradient(ellipse,rgba(108,99,255,.07) 0%,transparent 65%);
  pointer-events:none;
}
/* subtle dot grid */
.hero-grid{
  position:absolute;inset:0;
  background-image:radial-gradient(rgba(255,255,255,.04) 1px,transparent 1px);
  background-size:40px 40px;
  mask-image:radial-gradient(ellipse 100% 100% at 50% 50%,black 30%,transparent 100%);
  pointer-events:none;
}
.hero-inner{
  position:relative;z-index:1;
  max-width:1280px;margin:0 auto;width:100%;
  display:grid;grid-template-columns:1fr 520px;align-items:center;gap:80px;
}
.hero-tag{
  display:inline-flex;align-items:center;gap:8px;
  font-size:11px;font-weight:600;letter-spacing:1.6px;text-transform:uppercase;
  color:var(--purple-mid);border:1px solid rgba(108,99,255,.3);
  border-radius:100px;padding:7px 16px;margin-bottom:32px;
  background:rgba(108,99,255,.08);
}
.hero-tag-dot{width:6px;height:6px;border-radius:50%;background:var(--purple-mid);animation:blink 2.5s ease infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.25}}
h1{
  font-family:'Bricolage Grotesque',sans-serif;
  font-size:clamp(52px,6.5vw,100px);
  font-weight:800;letter-spacing:-3px;line-height:.96;
  color:#fff;margin-bottom:28px;
}
h1 .hl{
  color:transparent;
  -webkit-text-stroke:1.5px rgba(108,99,255,.7);
}
.hero-sub{
  font-size:18px;line-height:1.75;color:rgba(255,255,255,.55);
  max-width:460px;margin-bottom:44px;font-weight:300;
}
.hero-btns{display:flex;flex-wrap:wrap;gap:14px;align-items:center;margin-bottom:48px}
.btn-primary{
  font-family:'Bricolage Grotesque',sans-serif;
  font-size:15px;font-weight:700;
  background:var(--purple);color:#fff;
  padding:16px 34px;border-radius:12px;text-decoration:none;
  box-shadow:0 4px 24px rgba(108,99,255,.4);
  transition:background .2s,transform .2s,box-shadow .2s;
}
.btn-primary:hover{background:#5850e8;transform:translateY(-2px);box-shadow:0 10px 36px rgba(108,99,255,.5)}
.btn-ghost-hero{
  font-size:15px;font-weight:500;color:rgba(255,255,255,.6);
  padding:16px 28px;text-decoration:none;border-radius:12px;
  border:1px solid rgba(255,255,255,.12);
  transition:color .2s,border-color .2s,background .2s;
}
.btn-ghost-hero:hover{color:#fff;border-color:rgba(255,255,255,.3);background:rgba(255,255,255,.04)}
.hero-social{display:flex;align-items:center;gap:14px}
.hero-avs{display:flex}
.hero-av{
  width:32px;height:32px;border-radius:50%;border:2px solid rgba(255,255,255,.15);
  background:linear-gradient(135deg,var(--purple),#a78bfa);
  display:flex;align-items:center;justify-content:center;
  font-size:10px;font-weight:800;color:#fff;margin-left:-8px;
}
.hero-av:first-child{margin-left:0}
.hero-social-text{font-size:13px;color:rgba(255,255,255,.4);font-weight:500}
.hero-social-text b{color:rgba(255,255,255,.75)}

/* DASHBOARD CARD */
.hero-card-wrap{animation:floatCard 5.5s ease-in-out infinite;position:relative}
@keyframes floatCard{0%,100%{transform:translateY(0) rotate(-1deg)}50%{transform:translateY(-14px) rotate(-1deg)}}
.hero-card-glow{
  position:absolute;bottom:-60px;left:50%;transform:translateX(-50%);
  width:70%;height:80px;
  background:radial-gradient(ellipse,rgba(108,99,255,.5) 0%,transparent 70%);
  filter:blur(20px);pointer-events:none;
}
.dash-card{
  background:#fff;border-radius:28px;overflow:hidden;
  box-shadow:0 48px 100px rgba(0,0,0,.5),0 16px 40px rgba(0,0,0,.3),0 0 0 1px rgba(255,255,255,.08);
  width:100%;
}
.dash-top{
  padding:20px 24px;border-bottom:1px solid var(--border-light);
  display:flex;align-items:center;justify-content:space-between;
}
.dash-top-left{font-family:'Bricolage Grotesque',sans-serif;font-size:15px;font-weight:700;color:var(--ink)}
.dash-live{display:flex;align-items:center;gap:6px;font-size:11px;font-weight:600;color:#16a34a;background:#f0fdf4;border-radius:100px;padding:4px 11px}
.dash-live-dot{width:5px;height:5px;border-radius:50%;background:#16a34a;animation:blink 1.4s ease infinite}
.dash-nums{padding:20px 24px 16px;display:grid;grid-template-columns:1fr 1fr;gap:12px}
.dn{background:var(--surface);border-radius:16px;padding:16px 18px;border:1px solid var(--border-light)}
.dn-l{font-size:10px;font-weight:600;color:#aaa;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px}
.dn-v{font-family:'Bricolage Grotesque',sans-serif;font-size:30px;font-weight:800;color:var(--ink);letter-spacing:-1.5px;line-height:1}
.dn-c{font-size:11px;font-weight:600;color:#16a34a;margin-top:5px}
.dash-calls{padding:0 24px 20px;display:flex;flex-direction:column;gap:8px}
.dcall{
  display:flex;align-items:center;justify-content:space-between;
  padding:12px 14px;background:var(--surface);border-radius:12px;
  border:1px solid var(--border-light);
}
.dcall-l{display:flex;align-items:center;gap:10px}
.dcall-av{
  width:34px;height:34px;border-radius:50%;
  background:linear-gradient(135deg,var(--purple),#a78bfa);
  display:flex;align-items:center;justify-content:center;
  font-size:11px;font-weight:800;color:#fff;flex-shrink:0;
}
.dcall-name{font-size:13px;font-weight:600;color:var(--ink)}
.dcall-det{font-size:11px;color:#aaa;margin-top:2px}
.badge{font-size:10px;font-weight:700;padding:3px 10px;border-radius:100px;white-space:nowrap}
.badge-g{background:#f0fdf4;color:#16a34a}
.badge-p{background:rgba(108,99,255,.1);color:var(--purple)}
.dash-footer{padding:14px 24px;border-top:1px solid var(--border-light);display:flex;justify-content:space-between}
.dash-ft{font-size:12px;font-weight:500;color:#aaa}
.dash-ft b{color:var(--purple);font-weight:700}

/* floating badges */
.fbadge{
  position:absolute;background:#fff;border-radius:16px;
  padding:10px 14px;display:flex;align-items:center;gap:8px;
  box-shadow:0 12px 32px rgba(0,0,0,.18),0 0 0 1px rgba(0,0,0,.06);
  animation:fbIn .7s cubic-bezier(.16,1,.3,1) both;white-space:nowrap;
}
@keyframes fbIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.fb1{top:-16px;right:-28px;animation-delay:.7s}
.fb2{bottom:-8px;left:-44px;animation-delay:1s}
.fb-ico{font-size:20px}
.fb-lbl{font-size:11px;font-weight:600;color:var(--muted-ink);line-height:1.3}
.fb-val{font-family:'Bricolage Grotesque',sans-serif;font-size:14px;font-weight:800;color:var(--ink);margin-top:1px}

/* ===== STATS STRIP ===== */
.stats-strip{
  background:#ffffff;
  padding:52px 48px;
  border-bottom:1px solid var(--border-light);
}
.stats-row{
  max-width:1280px;margin:0 auto;
  display:flex;align-items:center;gap:0;
}
.stat{
  flex:1;text-align:center;padding:0 28px;
  border-right:1px solid var(--border-light);
}
.stat:first-child{text-align:left;padding-left:0}
.stat:last-child{border-right:none;text-align:right;padding-right:0}
.stat-n{
  font-family:'Bricolage Grotesque',sans-serif;
  font-size:44px;font-weight:800;letter-spacing:-2px;
  color:var(--ink);line-height:1;margin-bottom:6px;
}
.stat-n sup{font-size:.5em;vertical-align:top;margin-top:.2em;letter-spacing:0;color:var(--purple)}
.stat-l{font-size:13px;color:var(--muted-ink);font-weight:400;line-height:1.4}

/* ===== HOW IT WORKS ===== */
.how{padding:140px 48px;background:#fff}
.section-eyebrow{
  font-size:11px;font-weight:600;letter-spacing:2px;text-transform:uppercase;
  color:var(--purple);display:block;margin-bottom:16px;
}
h2{
  font-family:'Bricolage Grotesque',sans-serif;
  font-size:clamp(36px,4vw,58px);font-weight:800;
  letter-spacing:-2px;line-height:1.04;color:var(--ink);margin-bottom:18px;
}
.section-sub{font-size:17px;line-height:1.75;color:var(--muted-ink);max-width:520px;font-weight:300}

/* staggered steps */
.steps-wrap{position:relative;margin-top:80px;display:grid;grid-template-columns:repeat(4,1fr);gap:20px;align-items:start}
/* connector line */
.steps-wrap::before{
  content:'';position:absolute;
  top:28px;left:calc(12.5% + 10px);right:calc(12.5% + 10px);height:1px;
  background:linear-gradient(90deg,transparent,var(--purple-dim),var(--purple),var(--purple-dim),transparent);
  z-index:0;
}
.step{
  background:#fff;border-radius:22px;padding:32px 28px;
  border:1px solid var(--border-light);
  position:relative;z-index:1;
  transition:border-color .25s,box-shadow .35s,transform .35s cubic-bezier(.16,1,.3,1);
}
/* stagger heights */
.step:nth-child(even){margin-top:40px}
.step:hover{border-color:rgba(108,99,255,.25);box-shadow:0 20px 52px rgba(108,99,255,.08);transform:translateY(-4px)}
.step-dot{
  width:36px;height:36px;border-radius:50%;
  background:var(--white);border:2px solid var(--purple);
  display:flex;align-items:center;justify-content:center;
  margin-bottom:24px;
}
.step-dot-inner{width:10px;height:10px;border-radius:50%;background:var(--purple)}
.step-num{font-size:10px;font-weight:800;color:var(--purple);letter-spacing:1px;margin-bottom:14px}
.step-title{font-family:'Bricolage Grotesque',sans-serif;font-size:18px;font-weight:800;color:var(--ink);margin-bottom:10px;letter-spacing:-.3px}
.step-body{font-size:14px;line-height:1.7;color:var(--muted-ink)}

/* ===== BENTO FEATURES ===== */
.bento-section{
  padding:0 48px 140px;background:#fff;
}
.bento-grid{
  max-width:1280px;margin:0 auto;margin-top:80px;
  display:grid;
  grid-template-columns:repeat(12,1fr);
  grid-template-rows:auto;
  gap:18px;
}
.bento{
  background:var(--surface);border-radius:28px;padding:36px;
  border:1px solid var(--border-light);overflow:hidden;position:relative;
  transition:border-color .25s,box-shadow .35s,transform .35s cubic-bezier(.16,1,.3,1);
}
.bento:hover{border-color:rgba(108,99,255,.2);box-shadow:0 20px 56px rgba(108,99,255,.07);transform:translateY(-3px)}
.b1{grid-column:span 5;grid-row:span 2;background:var(--ink);border-color:transparent}
.b2{grid-column:span 7}
.b3{grid-column:span 4}
.b4{grid-column:span 3}
.b5{grid-column:span 7}
.b-icon{width:52px;height:52px;border-radius:16px;background:rgba(108,99,255,.12);display:flex;align-items:center;justify-content:center;font-size:24px;margin-bottom:24px}
.b-icon-dark{background:rgba(255,255,255,.1)}
.b-title{font-family:'Bricolage Grotesque',sans-serif;font-size:20px;font-weight:800;color:var(--ink);margin-bottom:10px;letter-spacing:-.4px;line-height:1.15}
.b-title-light{color:#fff}
.b-body{font-size:14px;line-height:1.7;color:var(--muted-ink)}
.b-body-light{color:rgba(255,255,255,.5)}
/* large bento visual */
.b1 .bento-metric-big{margin-top:auto;padding-top:28px}
.b-big-num{font-family:'Bricolage Grotesque',sans-serif;font-size:72px;font-weight:800;letter-spacing:-4px;color:#fff;line-height:1}
.b-big-label{font-size:13px;color:rgba(255,255,255,.4);margin-top:6px;font-weight:400}
.b1{display:flex;flex-direction:column}
/* mini bars inside a bento */
.b-bars{margin-top:20px;display:flex;flex-direction:column;gap:10px}
.b-bar-row{display:flex;align-items:center;gap:10px}
.b-bar-label{font-size:12px;color:var(--muted-ink);width:100px;flex-shrink:0}
.b-bar-track{flex:1;height:5px;background:var(--border-light);border-radius:3px;overflow:hidden}
.b-bar-fill{height:100%;border-radius:3px;background:linear-gradient(90deg,var(--purple),#a78bfa)}
.b-bar-val{font-size:12px;font-weight:600;color:var(--ink);width:32px;text-align:right}
/* stat bento */
.b-stat-big{
  font-family:'Bricolage Grotesque',sans-serif;
  font-size:56px;font-weight:800;letter-spacing:-3px;color:var(--ink);line-height:1;margin-bottom:8px;
}
.b-stat-big span{color:var(--purple)}

/* ===== INDUSTRIES ===== */
.industries{
  padding:140px 48px;
  background:var(--surface);
  position:relative;
  /* curved top */
}
.industries::before{
  content:'';position:absolute;
  top:-60px;left:0;right:0;height:120px;
  background:var(--surface);
  clip-path:ellipse(60% 100% at 50% 100%);
  z-index:0;
}
.ind-inner{max-width:1280px;margin:0 auto;position:relative;z-index:1}
.ind-grid{
  display:grid;grid-template-columns:repeat(3,1fr);gap:24px;
  margin-top:80px;
}
.ind-card{
  background:#fff;border-radius:28px;padding:44px 40px;
  border:1px solid var(--border-light);
  text-decoration:none;display:flex;flex-direction:column;
  transition:border-color .25s,box-shadow .4s,transform .4s cubic-bezier(.16,1,.3,1);
  position:relative;overflow:hidden;
}
.ind-card::after{
  content:'';position:absolute;top:0;left:0;right:0;height:4px;
  background:linear-gradient(90deg,var(--purple),#a78bfa);
  transform:scaleX(0);transform-origin:left;
  transition:transform .4s cubic-bezier(.16,1,.3,1);
}
.ind-card:hover{border-color:rgba(108,99,255,.2);box-shadow:0 28px 64px rgba(108,99,255,.1);transform:translateY(-6px)}
.ind-card:hover::after{transform:scaleX(1)}
.ind-ico{font-size:40px;margin-bottom:28px}
.ind-name{font-family:'Bricolage Grotesque',sans-serif;font-size:26px;font-weight:800;color:var(--ink);letter-spacing:-.8px;margin-bottom:12px}
.ind-desc{font-size:15px;line-height:1.72;color:var(--muted-ink);flex:1;margin-bottom:28px;font-weight:300}
.ind-link{font-family:'Bricolage Grotesque',sans-serif;font-size:14px;font-weight:700;color:var(--purple);display:flex;align-items:center;gap:8px;transition:gap .2s}
.ind-card:hover .ind-link{gap:13px}

/* ===== TESTIMONIALS ===== */
.testimonials{padding:140px 48px;background:#fff}
.test-layout{
  max-width:1280px;margin:0 auto;margin-top:80px;
  display:grid;grid-template-columns:1.3fr 1fr;gap:32px;
  align-items:start;
}
.test-featured{
  background:var(--ink);border-radius:32px;padding:52px;
}
.test-featured .test-stars{display:flex;gap:3px;margin-bottom:28px}
.test-featured .star{color:#f59e0b;font-size:20px}
.test-featured blockquote{
  font-family:'Bricolage Grotesque',sans-serif;
  font-size:clamp(20px,2vw,26px);font-weight:700;
  color:#fff;line-height:1.45;margin-bottom:36px;letter-spacing:-.5px;
}
.test-featured .author{display:flex;align-items:center;gap:14px}
.test-featured .av{
  width:48px;height:48px;border-radius:50%;
  background:linear-gradient(135deg,var(--purple),#a78bfa);
  display:flex;align-items:center;justify-content:center;
  font-family:'Bricolage Grotesque',sans-serif;
  font-size:15px;font-weight:800;color:#fff;flex-shrink:0;
}
.test-featured .auth-name{font-family:'Bricolage Grotesque',sans-serif;font-size:15px;font-weight:800;color:#fff;margin-bottom:3px}
.test-featured .auth-role{font-size:13px;color:rgba(255,255,255,.4)}
.test-stack{display:flex;flex-direction:column;gap:20px}
.test-mini{background:var(--surface);border-radius:24px;padding:36px;border:1px solid var(--border-light);transition:border-color .25s}
.test-mini:hover{border-color:rgba(108,99,255,.2)}
.test-mini .mini-stars{display:flex;gap:2px;margin-bottom:16px}
.test-mini .star{color:#f59e0b;font-size:14px}
.test-mini p{font-size:15px;line-height:1.72;color:var(--muted-ink);margin-bottom:20px;font-weight:300}
.test-mini .author{display:flex;align-items:center;gap:10px}
.test-mini .av{
  width:36px;height:36px;border-radius:50%;
  background:linear-gradient(135deg,var(--purple),#a78bfa);
  display:flex;align-items:center;justify-content:center;
  font-size:11px;font-weight:800;color:#fff;flex-shrink:0;
}
.test-mini .auth-name{font-size:13px;font-weight:700;color:var(--ink);margin-bottom:1px}
.test-mini .auth-role{font-size:12px;color:#aaa}

/* ===== CTA ===== */
.cta-section{
  margin:0 48px 100px;
  border-radius:36px;
  background:var(--purple);
  padding:120px 80px;
  position:relative;overflow:hidden;
}
.cta-section::before{
  content:'';position:absolute;
  top:-40%;right:-10%;width:70%;height:120%;border-radius:50%;
  background:rgba(255,255,255,.06);pointer-events:none;
}
.cta-section::after{
  content:'';position:absolute;
  bottom:-30%;left:-5%;width:40%;height:80%;border-radius:50%;
  background:rgba(0,0,0,.08);pointer-events:none;
}
.cta-inner{max-width:760px;margin:0 auto;text-align:center;position:relative;z-index:1}
.cta-eyebrow{font-size:11px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:rgba(255,255,255,.55);display:block;margin-bottom:20px}
.cta-h2{
  font-family:'Bricolage Grotesque',sans-serif;
  font-size:clamp(40px,5vw,70px);font-weight:800;
  letter-spacing:-2.5px;line-height:1.02;color:#fff;margin-bottom:22px;
}
.cta-sub{font-size:18px;line-height:1.75;color:rgba(255,255,255,.65);margin-bottom:52px;font-weight:300}
.cta-btns{display:flex;flex-wrap:wrap;gap:14px;justify-content:center}
.btn-white{
  font-family:'Bricolage Grotesque',sans-serif;
  font-size:16px;font-weight:800;
  background:#fff;color:var(--purple);
  padding:18px 40px;border-radius:14px;text-decoration:none;
  box-shadow:0 8px 32px rgba(0,0,0,.18);
  transition:transform .2s,box-shadow .2s;
}
.btn-white:hover{transform:translateY(-2px);box-shadow:0 14px 40px rgba(0,0,0,.24)}
.btn-ghost-white{
  font-size:15px;font-weight:600;color:rgba(255,255,255,.75);
  padding:18px 36px;border-radius:14px;text-decoration:none;
  border:1.5px solid rgba(255,255,255,.3);
  transition:color .2s,border-color .2s,background .2s;
}
.btn-ghost-white:hover{color:#fff;border-color:rgba(255,255,255,.7);background:rgba(255,255,255,.08)}
.cta-note{font-size:13px;color:rgba(255,255,255,.35);margin-top:24px}

/* ===== FOOTER ===== */
footer{background:var(--ink);padding:100px 48px 48px}
.ft-inner{max-width:1280px;margin:0 auto}
.ft-top{display:grid;grid-template-columns:1.5fr 1fr 1fr 1fr;gap:56px;margin-bottom:80px}
.ft-logo{display:flex;align-items:center;gap:10px;text-decoration:none;margin-bottom:18px}
.ft-logo-name{font-family:'Bricolage Grotesque',sans-serif;font-size:17px;font-weight:800;color:#fff}
.ft-logo-sub{font-size:7.5px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:var(--purple);margin-top:3px;display:block}
.ft-desc{font-size:14px;line-height:1.75;color:rgba(255,255,255,.3);max-width:250px;margin-bottom:22px;font-weight:300}
.ft-contact a{display:block;font-size:13px;color:rgba(255,255,255,.3);text-decoration:none;margin-bottom:5px;transition:color .2s}
.ft-contact a:hover{color:rgba(255,255,255,.8)}
.ft-col-h{font-size:10px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:rgba(255,255,255,.22);margin-bottom:18px}
.ft-col a{display:block;font-size:14px;color:rgba(255,255,255,.38);text-decoration:none;margin-bottom:12px;transition:color .2s;font-weight:400}
.ft-col a:last-child{margin:0}
.ft-col a:hover{color:rgba(255,255,255,.9)}
.ft-bottom{padding-top:40px;border-top:1px solid rgba(255,255,255,.07);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px}
.ft-copy{font-size:13px;color:rgba(255,255,255,.18)}
.ft-legal{display:flex;gap:24px}
.ft-legal a{font-size:13px;color:rgba(255,255,255,.18);text-decoration:none;transition:color .2s}
.ft-legal a:hover{color:rgba(255,255,255,.6)}

/* RESPONSIVE */
@media(max-width:1100px){
  .hero-inner{grid-template-columns:1fr;gap:0}
  .hero-card-wrap{display:none}
  h1{font-size:clamp(48px,8vw,80px)}
  .steps-wrap::before{display:none}
  .steps-wrap{grid-template-columns:1fr 1fr}
  .step:nth-child(even){margin-top:0}
  .bento-grid{grid-template-columns:1fr 1fr}
  .b1,.b2,.b3,.b4,.b5{grid-column:span 1;grid-row:auto}
  .b1{order:-1}
  .ind-grid{grid-template-columns:1fr 1fr}
  .test-layout{grid-template-columns:1fr}
  .ft-top{grid-template-columns:1fr 1fr}
  .stats-row{flex-wrap:wrap}
  .stat{flex:0 0 50%;border-right:none;border-bottom:1px solid var(--border-light);padding:20px 0;text-align:left!important}
  .stat:last-child,.stat:nth-child(even){border-bottom:none}
  .cta-section{margin:0 24px 80px;padding:80px 48px}
}
@media(max-width:768px){
  nav{padding:0 20px}
  .nav-links,.btn-ghost-nav{display:none}
  .hero{padding:100px 20px 160px}
  .how,.bento-section,.testimonials,.testimonials,.industries{padding-left:20px;padding-right:20px}
  .stats-strip{padding:40px 20px}
  footer{padding:80px 20px 40px}
  .cta-section{margin:0 16px 60px;padding:60px 28px;border-radius:24px}
  .steps-wrap{grid-template-columns:1fr}
  .ind-grid{grid-template-columns:1fr}
  .ft-top{grid-template-columns:1fr}
  .ft-bottom{flex-direction:column;text-align:center}
  h1{font-size:clamp(44px,10vw,64px);letter-spacing:-2px}
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
  <div class="nav-r">
    <a href="/calculator.html" class="btn-ghost-nav">Revenue Calculator</a>
    <a href="/demo.html" class="btn-cta-nav">Get a Demo</a>
    <button class="hamburger" id="hbg" aria-label="Menu">
      <span></span><span></span><span></span>
    </button>
  </div>
</nav>

<!-- MENU -->
<div class="menu-bd" id="bd"></div>
<div class="menu-panel" id="mp">
  <button class="menu-x" id="mx">&#x2715;</button>
  <div class="menu-g"><div class="menu-g-t">Product</div>
    <a href="/how-it-works.html">How It Works</a>
    <a href="/demo.html">Live Demo</a>
    <a href="/faq.html">FAQ</a>
    <a href="/ai-readiness.html">AI Readiness Score</a>
    <a href="/calculator.html">Revenue Calculator</a>
  </div>
  <div class="menu-g"><div class="menu-g-t">Learn</div>
    <a href="/case-studies.html">Case Studies</a>
    <a href="/blog.html">Blog</a>
  </div>
  <div class="menu-g"><div class="menu-g-t">Industries</div>
    <a href="/hvac.html">HVAC</a>
    <a href="/plumbing.html">Plumbing</a>
    <a href="/electrical.html">Electrical</a>
  </div>
  <div class="menu-g"><div class="menu-g-t">Company</div>
    <a href="/about.html">About</a>
    <a href="/affiliate.html">Affiliate Program</a>
    <a href="/careers.html">Careers</a>
    <a href="/status.html">System Status</a>
  </div>
  <a href="/demo.html" class="menu-cta">Book a Free Demo &rarr;</a>
</div>

<!-- HERO -->
<section class="hero">
  <div class="hero-grid"></div>
  <div class="hero-inner">
    <div class="rv">
      <div class="hero-tag">
        <span class="hero-tag-dot"></span>
        AI Voice Agents &mdash; Live 24/7
      </div>
      <h1>Never miss<br>a service<br><span class="hl">call.</span></h1>
      <p class="hero-sub">Syntharra deploys AI voice agents that answer every call, book jobs automatically, and cover your phones around the clock &mdash; so your trade business keeps growing while you&rsquo;re on the job.</p>
      <div class="hero-btns">
        <a href="/demo.html" class="btn-primary">See It In Action &rarr;</a>
        <a href="/calculator.html" class="btn-ghost-hero">Calculate Revenue Gap</a>
      </div>
      <div class="hero-social">
        <div class="hero-avs">
          <div class="hero-av">MT</div>
          <div class="hero-av" style="background:linear-gradient(135deg,#0891b2,#06b6d4)">JS</div>
          <div class="hero-av" style="background:linear-gradient(135deg,#d97706,#f59e0b)">RC</div>
          <div class="hero-av" style="background:linear-gradient(135deg,#16a34a,#4ade80)">AB</div>
        </div>
        <div class="hero-social-text"><b>40+ trade businesses</b> already answering every call</div>
      </div>
    </div>
    <div class="rv-r d2">
      <div class="hero-card-wrap">
        <div class="hero-card-glow"></div>
        <div class="dash-card">
          <div class="dash-top">
            <span class="dash-top-left">Live Dashboard</span>
            <div class="dash-live"><div class="dash-live-dot"></div> 3 calls active</div>
          </div>
          <div class="dash-nums">
            <div class="dn"><div class="dn-l">Calls Today</div><div class="dn-v">47</div><div class="dn-c">&#8593; 23% vs last week</div></div>
            <div class="dn"><div class="dn-l">Revenue Added</div><div class="dn-v">$8.4k</div><div class="dn-c">&#8593; This month</div></div>
          </div>
          <div class="dash-calls">
            <div class="dcall">
              <div class="dcall-l">
                <div class="dcall-av">MT</div>
                <div><div class="dcall-name">Mike T. &mdash; AC Repair</div><div class="dcall-det">Thu 2pm &bull; Est. $380&ndash;520</div></div>
              </div>
              <span class="badge badge-g">Booked</span>
            </div>
            <div class="dcall">
              <div class="dcall-l">
                <div class="dcall-av" style="background:linear-gradient(135deg,#0891b2,#06b6d4)">SL</div>
                <div><div class="dcall-name">Sarah L. &mdash; Furnace Service</div><div class="dcall-det">Booking in progress&hellip;</div></div>
              </div>
              <span class="badge badge-p">Live</span>
            </div>
            <div class="dcall">
              <div class="dcall-l">
                <div class="dcall-av" style="background:linear-gradient(135deg,#d97706,#f59e0b)">RK</div>
                <div><div class="dcall-name">Rob K. &mdash; Drain Cleaning</div><div class="dcall-det">After-hours &bull; Fri 9am</div></div>
              </div>
              <span class="badge badge-g">Booked</span>
            </div>
          </div>
          <div class="dash-footer">
            <span class="dash-ft">Jobs booked: <b>12</b></span>
            <span class="dash-ft">Missed calls: <b style="color:#16a34a">0</b></span>
          </div>
        </div>
        <div class="fbadge fb1">
          <div class="fb-ico">&#9989;</div>
          <div><div class="fb-lbl">After-hours booked</div><div class="fb-val">2:47am call</div></div>
        </div>
        <div class="fbadge fb2">
          <div class="fb-ico">&#128176;</div>
          <div><div class="fb-lbl">Revenue recovered</div><div class="fb-val">+$1,240 this week</div></div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- STATS STRIP -->
<div class="stats-strip rv">
  <div class="stats-row">
    <div class="stat rv d1"><div class="stat-n">97<sup>%</sup></div><div class="stat-l">Call answer rate</div></div>
    <div class="stat rv d2"><div class="stat-n">24/7</div><div class="stat-l">Always on, never sleeps</div></div>
    <div class="stat rv d3"><div class="stat-n">&lt;3<sup>min</sup></div><div class="stat-l">Time to go live</div></div>
    <div class="stat rv d4"><div class="stat-n">$10<sup>k+</sup></div><div class="stat-l">Avg. monthly revenue added</div></div>
    <div class="stat rv d5"><div class="stat-n">0</div><div class="stat-l">Missed calls after go-live</div></div>
  </div>
</div>

<!-- HOW IT WORKS -->
<section class="how">
  <div style="max-width:1280px;margin:0 auto">
    <div class="rv">
      <span class="section-eyebrow">How It Works</span>
      <h2>Live in minutes.<br>No setup required.</h2>
      <p class="section-sub">Fill out one form. We train your agent, you forward your number. Done.</p>
    </div>
    <div class="steps-wrap">
      <div class="step rv d1">
        <div class="step-num">STEP 01</div>
        <div class="step-title">Onboard in 5 minutes</div>
        <p class="step-body">Tell us your services, area, and hours. No technical knowledge needed whatsoever.</p>
      </div>
      <div class="step rv d2">
        <div class="step-num">STEP 02</div>
        <div class="step-title">We train your agent</div>
        <p class="step-body">Your AI learns your pricing, job types, and how to qualify and book calls into your calendar.</p>
      </div>
      <div class="step rv d3">
        <div class="step-num">STEP 03</div>
        <div class="step-title">Forward your number</div>
        <p class="step-body">Point your business line to Syntharra. Works with any phone system in under 60 seconds.</p>
      </div>
      <div class="step rv d4">
        <div class="step-num">STEP 04</div>
        <div class="step-title">Revenue starts growing</div>
        <p class="step-body">Every call answered, every job booked. Your dashboard shows every dollar recovered in real time.</p>
      </div>
    </div>
  </div>
</section>

<!-- BENTO FEATURES -->
<div class="bento-section">
  <div style="max-width:1280px;margin:0 auto">
    <div class="rv">
      <span class="section-eyebrow">The Platform</span>
      <h2>Everything you need.<br>Nothing you don&rsquo;t.</h2>
    </div>
  </div>
  <div class="bento-grid" style="max-width:1280px;margin-left:auto;margin-right:auto">

    <div class="bento b1 rv">
      <div class="b-icon b-icon-dark">&#127752;</div>
      <div class="b-title b-title-light">Natural conversation that actually books jobs</div>
      <p class="b-body b-body-light">Your AI qualifies leads, checks availability, and books directly into your calendar. Customers never know it&rsquo;s AI.</p>
      <div class="bento-metric-big">
        <div class="b-big-num">97%</div>
        <div class="b-big-label">of calls answered &amp; handled</div>
      </div>
    </div>

    <div class="bento b2 rv d1">
      <div class="b-icon">&#128336;</div>
      <div class="b-title">24/7 after-hours coverage</div>
      <p class="b-body">Most missed calls happen outside business hours. Your agent handles them all &mdash; nights, weekends, holidays.</p>
      <div class="b-bars">
        <div class="b-bar-row"><span class="b-bar-label">Business hours</span><div class="b-bar-track"><div class="b-bar-fill" data-w="100" style="width:0"></div></div><span class="b-bar-val">100%</span></div>
        <div class="b-bar-row"><span class="b-bar-label">After-hours</span><div class="b-bar-track"><div class="b-bar-fill" data-w="100" style="width:0"></div></div><span class="b-bar-val">100%</span></div>
        <div class="b-bar-row"><span class="b-bar-label">Converted</span><div class="b-bar-track"><div class="b-bar-fill" data-w="74" style="width:0"></div></div><span class="b-bar-val">74%</span></div>
      </div>
    </div>

    <div class="bento b3 rv d2">
      <div class="b-icon">&#128197;</div>
      <div class="b-title">Direct calendar booking</div>
      <p class="b-body">Jobs go straight to your scheduling software. No double-booking. No manual entry.</p>
    </div>

    <div class="bento b4 rv d3">
      <div class="b-stat-big">74<span>%</span></div>
      <div class="b-title" style="margin-top:12px">Calls converted<br>to booked jobs</div>
    </div>

    <div class="bento b5 rv d1">
      <div class="b-icon">&#128202;</div>
      <div class="b-title">Real-time revenue dashboard</div>
      <p class="b-body">See every call, booking, and dollar recovered &mdash; in one clean dashboard built for trade business owners, not IT teams. No spreadsheets. No guesswork.</p>
    </div>

  </div>
</div>

<!-- INDUSTRIES -->
<section class="industries">
  <div class="ind-inner">
    <div class="rv">
      <span class="section-eyebrow">Industries</span>
      <h2>Built for the trades.<br>Not generic call centres.</h2>
      <p class="section-sub">Trained specifically on HVAC, plumbing, and electrical &mdash; the terminology, job types, and pricing conversations your customers expect.</p>
    </div>
    <div class="ind-grid">
      <a href="/hvac.html" class="ind-card rv d1">
        <div class="ind-ico">&#10052;&#65039;</div>
        <div class="ind-name">HVAC</div>
        <p class="ind-desc">AC repair, furnace service, duct cleaning, system installs &mdash; your agent knows every job type and books them without hesitation.</p>
        <div class="ind-link">Explore HVAC &rarr;</div>
      </a>
      <a href="/plumbing.html" class="ind-card rv d2">
        <div class="ind-ico">&#128166;</div>
        <div class="ind-name">Plumbing</div>
        <p class="ind-desc">Emergency leaks, drain cleaning, water heater installs &mdash; capture every call before your competitor even picks up.</p>
        <div class="ind-link">Explore Plumbing &rarr;</div>
      </a>
      <a href="/electrical.html" class="ind-card rv d3">
        <div class="ind-ico">&#9889;</div>
        <div class="ind-name">Electrical</div>
        <p class="ind-desc">Panel upgrades, EV charger installs, service calls &mdash; your AI qualifies and books every lead automatically.</p>
        <div class="ind-link">Explore Electrical &rarr;</div>
      </a>
    </div>
  </div>
</section>

<!-- TESTIMONIALS -->
<section class="testimonials">
  <div style="max-width:1280px;margin:0 auto">
    <div class="rv">
      <span class="section-eyebrow">Results</span>
      <h2>Real businesses.<br>Real revenue.</h2>
    </div>
    <div class="test-layout">
      <div class="test-featured rv-l">
        <div class="test-stars">
          <span class="star">&#9733;</span><span class="star">&#9733;</span>
          <span class="star">&#9733;</span><span class="star">&#9733;</span>
          <span class="star">&#9733;</span>
        </div>
        <blockquote>&ldquo;We were losing 8&ndash;10 calls a week after hours. Syntharra fixed that in the first 24 hours. Within a month we&rsquo;d recovered over $14,000 in jobs we would have lost entirely.&rdquo;</blockquote>
        <div class="author">
          <div class="av">MT</div>
          <div>
            <div class="auth-name">Mark T.</div>
            <div class="auth-role">Owner, Arctic Breeze HVAC &bull; Phoenix, AZ</div>
          </div>
        </div>
      </div>
      <div class="test-stack rv-r">
        <div class="test-mini">
          <div class="mini-stars">
            <span class="star">&#9733;</span><span class="star">&#9733;</span>
            <span class="star">&#9733;</span><span class="star">&#9733;</span>
            <span class="star">&#9733;</span>
          </div>
          <p>&ldquo;My receptionist cost $3,200 a month and still missed calls on busy days. Syntharra costs less and never misses. Not even a comparison.&rdquo;</p>
          <div class="author">
            <div class="av">JS</div>
            <div><div class="auth-name">Jason S.</div><div class="auth-role">Reliable Plumbing Co. &bull; Denver, CO</div></div>
          </div>
        </div>
        <div class="test-mini">
          <div class="mini-stars">
            <span class="star">&#9733;</span><span class="star">&#9733;</span>
            <span class="star">&#9733;</span><span class="star">&#9733;</span>
            <span class="star">&#9733;</span>
          </div>
          <p>&ldquo;Customers genuinely can&rsquo;t tell it&rsquo;s AI. We booked 40+ jobs in the first month. The ROI is insane for a small electrical shop.&rdquo;</p>
          <div class="author">
            <div class="av" style="background:linear-gradient(135deg,#d97706,#f59e0b)">RC</div>
            <div><div class="auth-name">Rachel C.</div><div class="auth-role">Bright Spark Electric &bull; Austin, TX</div></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- CTA -->
<div class="cta-section rv">
  <div class="cta-inner">
    <span class="cta-eyebrow">Get Started Today</span>
    <h2 class="cta-h2">Every missed call is revenue left behind.</h2>
    <p class="cta-sub">Every unanswered call costs your business $400&ndash;$800 on average. Syntharra makes sure that never happens again &mdash; starting today.</p>
    <div class="cta-btns">
      <a href="/demo.html" class="btn-white">Get Your Free Demo</a>
      <a href="/calculator.html" class="btn-ghost-white">Calculate Your Revenue Gap</a>
    </div>
    <p class="cta-note">No contract &bull; No technical setup &bull; Live in under 3 minutes</p>
  </div>
</div>

<!-- FOOTER -->
<footer>
  <div class="ft-inner">
    <div class="ft-top">
      <div>
        <a href="/" class="ft-logo">
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
  nav.classList.toggle('lit', window.scrollY > 40);
}, {passive:true});

// Menu
const open = () => { document.getElementById('mp').classList.add('on'); document.getElementById('bd').classList.add('on'); document.body.style.overflow='hidden'; };
const close = () => { document.getElementById('mp').classList.remove('on'); document.getElementById('bd').classList.remove('on'); document.body.style.overflow=''; };
document.getElementById('hbg').addEventListener('click', open);
document.getElementById('mx').addEventListener('click', close);
document.getElementById('bd').addEventListener('click', close);

// Scroll reveal
const obs = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('on'); });
}, {threshold:0.07, rootMargin:'0px 0px -28px 0px'});
document.querySelectorAll('.rv,.rv-l,.rv-r,.rv-s').forEach(el => obs.observe(el));

// Bars
const bObs = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) { e.target.style.width = e.target.dataset.w + '%'; bObs.unobserve(e.target); }
  });
}, {threshold:.3});
document.querySelectorAll('[data-w]').forEach(b => bObs.observe(b));
</script>
</body>
</html>'''

print("Fetching SHA...")
r = requests.get(API, headers=HEADERS)
r.raise_for_status()
sha = r.json()["sha"]
print(f"SHA: {sha}")
assert HTML.count("<style>") == 1, "Style block count error"
print("Style OK")

payload = {
    "message": "feat(website): editorial dark-to-light homepage — Bricolage Grotesque, diagonal hero, bento grid, asymmetric testimonials",
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
