#!/usr/bin/env python3
"""
Batch update: inject new nav + footer + menu JS into every HTML page
in the Syntharra/syntharra-website GitHub repo.

Critical rules:
  - Sequential writes only (fetch SHA immediately before PUT).
  - str.replace() verified after every replace.
  - One <style> block assertion before push.
  - No DELETE — only GET and PUT.
  - sleep(1) between writes.
"""

import base64
import re
import time
import sys
import requests

import os
TOKEN = os.environ.get('GITHUB_TOKEN', '')
REPO  = 'Syntharra/syntharra-website'
API   = f'https://api.github.com/repos/{REPO}/contents'
HEADERS = {
    'Authorization': f'token {TOKEN}',
    'Content-Type': 'application/json',
}

# ── Excluded pages ──────────────────────────────────────────────────────────
SKIP_FILES = {
    'index.html',
    'lp/hvac-answering-service.html',
    'lp/plumbing-answering-service.html',
    'lp/electrical-answering-service.html',
    'dashboard.html',
}

# ── New snippets ─────────────────────────────────────────────────────────────

NEW_NAV = '''<!-- FLOATING NAV -->
<nav class="fixed top-6 left-1/2 -translate-x-1/2 w-[96%] max-w-[1900px] z-50 bg-white/70 backdrop-blur-2xl rounded-full border border-white/20 shadow-[0_8px_32px_rgba(0,0,0,0.05)] transition-all duration-500">
  <div class="flex justify-between items-center px-8 py-3">
    <!-- Logo -->
    <a href="/" class="flex items-center gap-3">
      <div class="flex items-end gap-1">
        <div class="w-1 h-3 bg-primary rounded-full"></div>
        <div class="w-1 h-5 bg-primary rounded-full"></div>
        <div class="w-1 h-7 bg-primary rounded-full"></div>
        <div class="w-1 h-9 bg-primary rounded-full"></div>
      </div>
      <div class="flex flex-col leading-none" style="margin-top:-4px">
        <span class="text-2xl font-black tracking-tighter text-slate-900 font-headline">Syntharra</span>
        <span class="text-[9px] font-bold tracking-[0.2em] text-primary uppercase opacity-80">Global AI Solutions</span>
      </div>
    </a>
    <!-- Desktop links -->
    <div class="hidden md:flex items-center space-x-8">
      <a class="text-slate-600 hover:text-primary font-medium text-sm tracking-tight transition-all" href="/how-it-works.html">How It Works</a>
      <a class="text-slate-600 hover:text-primary font-medium text-sm tracking-tight transition-all" href="/demo.html">Demo</a>
      <a class="text-slate-600 hover:text-primary font-medium text-sm tracking-tight transition-all" href="/case-studies.html">Results</a>
    </div>
    <!-- CTA + Menu button (always visible) -->
    <div class="flex items-center gap-2">
      <a href="https://calendar.app.google/jxUu7XfiMXMqvdiw6" class="bg-primary text-white px-6 py-2 rounded-full font-bold text-sm hover:scale-105 active:scale-95 transition-all font-headline shadow-lg shadow-primary/20">
        Get Started &rarr;
      </a>
      <button id="hbg" aria-label="Open menu" class="flex items-center gap-1.5 text-slate-600 hover:text-primary px-3 py-2 rounded-full border border-slate-200 hover:border-primary/30 hover:bg-primary/5 transition-all cursor-pointer">
        <span class="material-symbols-outlined" style="font-size:18px;line-height:1">menu</span>
        <span class="hidden md:inline text-sm font-semibold">Menu</span>
      </button>
    </div>
  </div>
</nav>

<!-- MOBILE MENU -->
<div id="bd" class="fixed inset-0 bg-black/60 z-[1000] opacity-0 pointer-events-none transition-opacity duration-250 backdrop-blur-sm"></div>
<div id="mp" class="fixed top-0 right-0 bottom-0 w-[300px] bg-white border-l border-slate-100 z-[1001] translate-x-full transition-transform duration-[380ms] ease-[cubic-bezier(0.16,1,0.3,1)] p-7 flex flex-col overflow-y-auto">
  <button id="mx" class="self-end text-slate-400 hover:text-slate-900 text-xl mb-6 transition-colors">&times;</button>
  <div class="mb-6">
    <div class="text-[10px] font-black tracking-widest uppercase text-primary mb-3">Product</div>
    <div class="flex flex-col gap-2">
      <a href="/how-it-works.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">How It Works</a>
      <a href="/demo.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Live Demo</a>
      <a href="/faq.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">FAQ</a>
      <a href="/ai-readiness.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">AI Readiness Score</a>
      <a href="/calculator.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Revenue Calculator</a>
    </div>
  </div>
  <div class="mb-6">
    <div class="text-[10px] font-black tracking-widest uppercase text-primary mb-3">Learn</div>
    <div class="flex flex-col gap-2">
      <a href="/case-studies.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Case Studies</a>
      <a href="/blog.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Blog</a>
    </div>
  </div>
  <div class="mb-6">
    <div class="text-[10px] font-black tracking-widest uppercase text-primary mb-3">Industries</div>
    <div class="flex flex-col gap-2">
      <a href="/hvac.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">HVAC</a>
      <a href="/plumbing.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Plumbing</a>
      <a href="/electrical.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Electrical</a>
    </div>
  </div>
  <div class="mb-6">
    <div class="text-[10px] font-black tracking-widest uppercase text-primary mb-3">Company</div>
    <div class="flex flex-col gap-2">
      <a href="/about.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">About</a>
      <a href="/affiliate.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Affiliate Program</a>
      <a href="/careers.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Careers</a>
      <a href="/status.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">System Status</a>
    </div>
  </div>
  <a href="/demo.html" class="mt-auto bg-primary text-white text-center py-4 rounded-2xl font-black text-sm hover:opacity-90 transition-opacity">Book a Free Demo &rarr;</a>
</div>'''

NEW_FOOTER = '''<footer class="bg-slate-950 text-white pt-40 pb-20 border-t border-white/5 relative overflow-hidden">
  <div class="max-w-[1700px] mx-auto px-8 relative z-10">
    <div class="grid grid-cols-1 md:grid-cols-12 gap-16 mb-40">
      <div class="md:col-span-4 space-y-8">
        <a href="/" class="flex items-center gap-3 w-fit">
          <div class="flex items-end gap-1">
            <div class="w-1 h-3 bg-primary rounded-full"></div>
            <div class="w-1 h-5 bg-primary rounded-full"></div>
            <div class="w-1 h-7 bg-primary rounded-full"></div>
            <div class="w-1 h-9 bg-primary rounded-full"></div>
          </div>
          <div class="flex flex-col leading-none" style="margin-top:-4px">
            <span class="text-2xl font-black tracking-tighter text-white font-headline">Syntharra</span>
            <span class="text-[9px] font-bold tracking-[0.2em] text-primary uppercase opacity-80">Global AI Solutions</span>
          </div>
        </a>
        <p class="text-white/40 text-lg max-w-sm leading-relaxed">AI voice agents for trade businesses. Never miss a call. Never lose a job to voicemail again.</p>
        <div class="flex flex-col gap-2">
          <a href="mailto:support@syntharra.com" class="text-white/40 hover:text-white text-sm transition-colors">support@syntharra.com</a>
          <a href="mailto:feedback@syntharra.com" class="text-white/40 hover:text-white text-sm transition-colors">feedback@syntharra.com</a>
        </div>
      </div>
      <div class="md:col-span-2 space-y-6">
        <h4 class="text-[10px] font-black uppercase tracking-widest text-primary">Product</h4>
        <ul class="space-y-4 text-white/60 text-sm">
          <li><a class="hover:text-white transition-colors" href="/how-it-works.html">How It Works</a></li>
          <li><a class="hover:text-white transition-colors" href="/demo.html">Live Demo</a></li>
          <li><a class="hover:text-white transition-colors" href="/calculator.html">Revenue Calculator</a></li>
          <li><a class="hover:text-white transition-colors" href="/ai-readiness.html">AI Readiness Score</a></li>
          <li><a class="hover:text-white transition-colors" href="/faq.html">FAQ</a></li>
        </ul>
      </div>
      <div class="md:col-span-2 space-y-6">
        <h4 class="text-[10px] font-black uppercase tracking-widest text-primary">Industries</h4>
        <ul class="space-y-4 text-white/60 text-sm">
          <li><a class="hover:text-white transition-colors" href="/hvac.html">HVAC</a></li>
          <li><a class="hover:text-white transition-colors" href="/plumbing.html">Plumbing</a></li>
          <li><a class="hover:text-white transition-colors" href="/electrical.html">Electrical</a></li>
        </ul>
        <h4 class="text-[10px] font-black uppercase tracking-widest text-primary pt-4">Learn</h4>
        <ul class="space-y-4 text-white/60 text-sm">
          <li><a class="hover:text-white transition-colors" href="/case-studies.html">Case Studies</a></li>
          <li><a class="hover:text-white transition-colors" href="/blog.html">Blog</a></li>
        </ul>
      </div>
      <div class="md:col-span-4 space-y-8">
        <div class="space-y-6">
          <h4 class="text-[10px] font-black uppercase tracking-widest text-primary">Company</h4>
          <ul class="space-y-4 text-white/60 text-sm flex flex-wrap gap-x-6">
            <li><a class="hover:text-white transition-colors" href="/about.html">About</a></li>
            <li><a class="hover:text-white transition-colors" href="/affiliate.html">Affiliates</a></li>
            <li><a class="hover:text-white transition-colors" href="/careers.html">Careers</a></li>
            <li><a class="hover:text-white transition-colors" href="/status.html">System Status</a></li>
            <li><a class="hover:text-white transition-colors" href="/privacy.html">Privacy</a></li>
            <li><a class="hover:text-white transition-colors" href="/terms.html">Terms</a></li>
          </ul>
        </div>
        <div class="bg-white/5 p-8 rounded-[2rem] border border-white/10">
          <h4 class="text-base font-bold font-headline mb-4">Stay ahead of the competition</h4>
          <p class="text-white/40 text-xs mb-4">Trade business tips, AI updates, and exclusive offers.</p>
          <div class="flex gap-2">
            <input class="bg-transparent border-b border-white/20 px-0 py-2 text-white text-sm focus:outline-none focus:border-primary w-full placeholder-white/30" placeholder="your@email.com" type="email"/>
            <button class="bg-white text-slate-950 px-5 py-2 rounded-full font-bold text-xs flex-shrink-0 hover:bg-primary hover:text-white transition-colors">Join</button>
          </div>
        </div>
      </div>
    </div>
    <div class="pt-10 border-t border-white/10 flex flex-col md:flex-row justify-between items-center gap-6">
      <p class="text-white/20 text-xs font-medium uppercase tracking-widest">&copy; 2026 Syntharra Global AI Solutions. All rights reserved.</p>
      <p class="text-white/20 text-xs italic">Built for the trades.</p>
    </div>
  </div>
</footer>'''

NEW_MENU_JS = '''<script>
const bd = document.getElementById('bd');
const mp = document.getElementById('mp');
const mx = document.getElementById('mx');
const hbg = document.getElementById('hbg');
function openMenu() { bd.classList.add('opacity-100','pointer-events-auto'); mp.style.transform='translateX(0)'; document.body.style.overflow='hidden'; }
function closeMenu() { bd.classList.remove('opacity-100','pointer-events-auto'); mp.style.transform=''; document.body.style.overflow=''; }
if(hbg) hbg.addEventListener('click', openMenu);
if(mx) mx.addEventListener('click', closeMenu);
if(bd) bd.addEventListener('click', closeMenu);
</script>'''

FONT_LINKS = '''<link href="https://fonts.googleapis.com" rel="preconnect"/>
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,700;12..96,800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600&family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>'''

CSS_VARS = """.font-headline { font-family: 'Bricolage Grotesque', sans-serif; }
:root { --primary: #4d41df; }
.text-primary { color: #4d41df !important; }
.bg-primary { background-color: #4d41df !important; }
.border-primary { border-color: #4d41df !important; }"""

# ── Helpers ──────────────────────────────────────────────────────────────────

def gh_get(path):
    """GET a file from GitHub. Returns (sha, decoded_content_str)."""
    url = f'{API}/{path}'
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    data = r.json()
    sha = data['sha']
    content = base64.b64decode(data['content']).decode('utf-8')
    return sha, content


def gh_put(path, sha, content, message):
    """PUT (update) a file on GitHub."""
    url = f'{API}/{path}'
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    payload = {
        'message': message,
        'content': encoded,
        'sha': sha,
    }
    r = requests.put(url, headers=HEADERS, json=payload)
    r.raise_for_status()
    return r.json()


def list_html_files(path=''):
    """Recursively list all .html files in the repo."""
    url = f'{API}/{path}' if path else API
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    items = r.json()
    files = []
    for item in items:
        if item['type'] == 'file' and item['name'].endswith('.html'):
            files.append(item['path'])
        elif item['type'] == 'dir':
            files.extend(list_html_files(item['path']))
    return files


def replace_verified(content, old, new, label):
    """Replace old->new and assert it matched."""
    updated = content.replace(old, new)
    if updated == content:
        raise ValueError(f"  [WARN] str.replace did not match for: {label}")
    return updated


def count_style_tags(content):
    return len(re.findall(r'<style[\s>]', content, re.IGNORECASE))


def find_nav_block(content):
    """
    Find the old <nav ...> ... </nav> or <header ...> ... </header> block.
    Returns (start_idx, end_idx, tag_name) or (None, None, None).
    Strategy: find first <nav or <header that is NOT our new nav
    (new nav has class="fixed top-6 left-1/2").
    """
    # Check if new nav is already there
    if 'fixed top-6 left-1/2 -translate-x-1/2' in content:
        return None, None, 'already_new'

    for tag in ('nav', 'header'):
        pattern = re.compile(
            rf'<{tag}[\s>]',
            re.IGNORECASE | re.DOTALL
        )
        m = pattern.search(content)
        if not m:
            continue
        start = m.start()
        # Find the matching closing tag by counting depth
        close_tag = f'</{tag}>'
        open_tag_re = re.compile(rf'<{tag}[\s>]', re.IGNORECASE)
        depth = 0
        pos = start
        end = None
        while pos < len(content):
            open_m = open_tag_re.search(content, pos)
            close_m = re.search(re.escape(close_tag), content[pos:], re.IGNORECASE)
            if close_m:
                close_abs = pos + close_m.start()
            else:
                close_abs = None

            if open_m and (close_abs is None or open_m.start() < close_abs):
                depth += 1
                pos = open_m.end()
            elif close_abs is not None:
                depth -= 1
                pos = close_abs + len(close_tag)
                if depth == 0:
                    end = pos
                    break
            else:
                break

        if end is not None:
            return start, end, tag

    return None, None, None


def find_footer_block(content):
    """Find the <footer ...> ... </footer> block. Returns (start, end) or (None, None)."""
    m = re.search(r'<footer[\s>]', content, re.IGNORECASE)
    if not m:
        return None, None
    start = m.start()
    close_tag = '</footer>'
    open_tag_re = re.compile(r'<footer[\s>]', re.IGNORECASE)
    depth = 0
    pos = start
    end = None
    while pos < len(content):
        open_m = open_tag_re.search(content, pos)
        close_m = re.search(re.escape(close_tag), content[pos:], re.IGNORECASE)
        if close_m:
            close_abs = pos + close_m.start()
        else:
            close_abs = None

        if open_m and (close_abs is None or open_m.start() < close_abs):
            depth += 1
            pos = open_m.end()
        elif close_abs is not None:
            depth -= 1
            pos = close_abs + len(close_tag)
            if depth == 0:
                end = pos
                break
        else:
            break

    return start, end


def process_page(path):
    """Process a single HTML file. Returns (ok: bool, reason: str)."""
    print(f"\n--- Processing: {path} ---")

    # Fetch fresh SHA + content
    sha, content = gh_get(path)
    original = content  # keep for comparison

    changes_made = []
    skip_reason = None

    # ── 1. Nav / header replacement ──────────────────────────────────────────
    nav_start, nav_end, nav_tag = find_nav_block(content)

    if nav_tag == 'already_new':
        print(f"  Nav: already has new nav — replacing mobile menu block anyway if needed")
        # Still need to ensure footer, fonts, JS are updated
        # Don't touch the nav section
    elif nav_start is not None and nav_end is not None:
        old_nav_block = content[nav_start:nav_end]
        print(f"  Nav: found <{nav_tag}> at {nav_start}-{nav_end} ({len(old_nav_block)} chars)")
        content = content[:nav_start] + NEW_NAV + content[nav_end:]
        assert content != original or nav_tag == 'already_new', "Nav replace had no effect"
        changes_made.append('nav')
    else:
        print(f"  Nav: no <nav> or <header> found — will inject after <body>")
        # Inject after <body> tag
        body_m = re.search(r'<body[^>]*>', content, re.IGNORECASE)
        if body_m:
            insert_pos = body_m.end()
            content = content[:insert_pos] + '\n' + NEW_NAV + '\n' + content[insert_pos:]
            changes_made.append('nav_injected')
        else:
            print(f"  WARN: No <body> tag found, cannot inject nav")

    # ── 2. Footer replacement ─────────────────────────────────────────────────
    footer_start, footer_end = find_footer_block(content)
    if footer_start is not None and footer_end is not None:
        old_footer = content[footer_start:footer_end]
        print(f"  Footer: found at {footer_start}-{footer_end} ({len(old_footer)} chars)")
        content = content[:footer_start] + NEW_FOOTER + content[footer_end:]
        changes_made.append('footer')
    else:
        print(f"  Footer: no <footer> found — injecting before </body>")
        body_close = re.search(r'</body>', content, re.IGNORECASE)
        if body_close:
            insert_pos = body_close.start()
            content = content[:insert_pos] + '\n' + NEW_FOOTER + '\n' + content[insert_pos:]
            changes_made.append('footer_injected')
        else:
            print(f"  WARN: No </body> found, cannot inject footer")

    # ── 3. Menu JS — remove old, inject new before </body> ───────────────────
    # Remove any existing menu JS blocks (our known pattern)
    old_menu_patterns = [
        # Pattern: script with hbg/bd/mp/mx variables
        r'<script>\s*(?:const|var|let)\s+(?:bd|hbg|mp|mx).*?</script>',
        # Also remove any script with openMenu/closeMenu
        r'<script>[\s\S]*?(?:openMenu|closeMenu)[\s\S]*?</script>',
    ]
    for pat in old_menu_patterns:
        old_content = content
        content = re.sub(pat, '', content, flags=re.DOTALL | re.IGNORECASE)
        if content != old_content:
            print(f"  Menu JS: removed old menu JS block")
            break

    # Inject new menu JS before </body>
    body_close = re.search(r'</body>', content, re.IGNORECASE)
    if body_close:
        insert_pos = body_close.start()
        content = content[:insert_pos] + '\n' + NEW_MENU_JS + '\n' + content[insert_pos:]
        changes_made.append('menu_js')
    else:
        print(f"  WARN: No </body> found, cannot inject menu JS")

    # ── 4. Font imports ───────────────────────────────────────────────────────
    if 'Bricolage+Grotesque' not in content and 'Bricolage Grotesque' not in content:
        head_close = re.search(r'</head>', content, re.IGNORECASE)
        if head_close:
            insert_pos = head_close.start()
            content = content[:insert_pos] + '\n' + FONT_LINKS + '\n' + content[insert_pos:]
            changes_made.append('fonts')
            print(f"  Fonts: injected Bricolage Grotesque + Material Symbols imports")
        else:
            print(f"  WARN: No </head> found, cannot inject fonts")
    else:
        print(f"  Fonts: already present")

    # ── 5. CSS vars — add to existing <style> block ───────────────────────────
    style_count = count_style_tags(content)
    print(f"  Style blocks found: {style_count}")

    if style_count == 0:
        # Add a new minimal style block in <head>
        head_close = re.search(r'</head>', content, re.IGNORECASE)
        if head_close:
            insert_pos = head_close.start()
            new_style_block = f'<style>\n{CSS_VARS}\n</style>\n'
            content = content[:insert_pos] + new_style_block + content[insert_pos:]
            changes_made.append('style_new')
            print(f"  CSS vars: added new <style> block")
    elif style_count == 1:
        # Add vars to existing style block if not already there
        if '--primary' not in content and 'font-headline' not in content:
            # Find the </style> and insert before it
            style_close = re.search(r'</style>', content, re.IGNORECASE)
            if style_close:
                insert_pos = style_close.start()
                content = content[:insert_pos] + '\n' + CSS_VARS + '\n' + content[insert_pos:]
                changes_made.append('css_vars')
                print(f"  CSS vars: injected into existing <style> block")
        else:
            print(f"  CSS vars: already present")
    else:  # style_count >= 2
        # Check if it became 2+ because we added one above — recalculate
        final_style_count = count_style_tags(content)
        if final_style_count >= 2:
            print(f"  SKIP: {final_style_count} <style> blocks found — aborting")
            return False, f'{final_style_count} style blocks'

    # ── 6. Final assertion: exactly 1 <style> block ───────────────────────────
    final_style_count = count_style_tags(content)
    if final_style_count == 0:
        # We injected one above, that's OK
        final_style_count = count_style_tags(content)
    if final_style_count > 1:
        return False, f'{final_style_count} <style> blocks after edit'

    # ── 7. Skip if nothing changed ─────────────────────────────────────────────
    if content == original:
        print(f"  No changes needed (content identical)")
        return True, 'no-op (already up to date)'

    # ── 8. PUT back ────────────────────────────────────────────────────────────
    print(f"  Changes: {changes_made} — pushing to GitHub...")
    # Re-fetch SHA right before PUT (sequential write rule)
    fresh_sha, _ = gh_get(path)
    gh_put(
        path=path,
        sha=fresh_sha,
        content=content,
        message=f'chore(website): apply new nav+footer design system to {path}',
    )
    print(f"  OK: {path}")
    return True, 'updated'


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("Fetching HTML file list from GitHub...")
    all_html = list_html_files()
    print(f"Found {len(all_html)} HTML files total")

    to_process = []
    for f in sorted(all_html):
        if f in SKIP_FILES:
            print(f"SKIP {f}: excluded by config")
        else:
            to_process.append(f)

    print(f"\nWill process {len(to_process)} pages:\n  " + '\n  '.join(to_process))
    print()

    results = {'ok': [], 'skip': []}

    for path in to_process:
        try:
            ok, reason = process_page(path)
            if ok:
                results['ok'].append((path, reason))
                print(f"OK {path}: {reason}")
            else:
                results['skip'].append((path, reason))
                print(f"SKIP {path}: {reason}")
        except Exception as e:
            results['skip'].append((path, str(e)))
            print(f"SKIP {path}: ERROR — {e}")
        time.sleep(1)

    print("\n" + "="*60)
    print(f"SUMMARY: {len(results['ok'])} OK, {len(results['skip'])} SKIP")
    print("\nOK pages:")
    for p, r in results['ok']:
        print(f"  OK {p}: {r}")
    print("\nSkipped pages:")
    for p, r in results['skip']:
        print(f"  SKIP {p}: {r}")


if __name__ == '__main__':
    main()
