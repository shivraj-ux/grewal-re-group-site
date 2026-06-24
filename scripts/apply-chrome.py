#!/usr/bin/env python3
"""
apply-chrome.py — Grewal RE Group "build step" for a no-build static site.

Single source of truth for the site header + footer. Run this to write the
identical, accessible header/footer into every page's HTML (server-rendered,
crawlable, zero layout shift). Edit HEADER/FOOTER below, re-run, done.

Usage:
  python3 scripts/apply-chrome.py sample   # apply to 3 sample pages only
  python3 scripts/apply-chrome.py all       # apply to every page
  python3 scripts/apply-chrome.py contact   # (re)generate /contact.html
Idempotent: pages already carrying the new chrome (.gh-header) are skipped.
"""
import re, sys, glob, os

# ============================ CANONICAL HEADER ============================
HEADER = '''<a class="gh-skip" href="#gh-main">Skip to main content</a>
<header class="gh-header">
  <div class="gh-bar">
    <a href="/" class="gh-logo" aria-label="Grewal RE Group — home">
      <img src="/assets/logos/logo-horizontal-white.png" alt="Grewal RE Group" class="gh-logo-w" width="187" height="56">
      <img src="/assets/logos/logo-horizontal.png" alt="" aria-hidden="true" class="gh-logo-b" width="187" height="56">
    </a>
    <button class="gh-toggle" type="button" aria-expanded="false" aria-controls="gh-primary-nav" aria-label="Open menu">
      <span></span><span></span><span></span>
    </button>
    <nav class="gh-nav" id="gh-primary-nav" aria-label="Primary">
      <ul class="gh-menu">
        <li><a href="/communities/">Communities</a></li>
        <li class="gh-has-sub">
          <button class="gh-sub-toggle" type="button" aria-expanded="false">Buy / Sell
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M6 9l6 6 6-6"/></svg>
          </button>
          <ul class="gh-sub">
            <li><a href="/#services">Buying</a></li>
            <li><a href="/home-value-estimator.html">Selling &amp; Home Value</a></li>
            <li><a href="/seller-net-proceeds-calculator.html">Net Proceeds Calculator</a></li>
            <li><a href="/relocation-guide.html">Relocating to Austin</a></li>
          </ul>
        </li>
        <li class="gh-has-sub">
          <button class="gh-sub-toggle" type="button" aria-expanded="false">Resources
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M6 9l6 6 6-6"/></svg>
          </button>
          <ul class="gh-sub">
            <li><a href="/blog/">Blog</a></li>
            <li><a href="/#resources">Guides</a></li>
            <li><a href="/faq.html">FAQ</a></li>
          </ul>
        </li>
        <li><a href="/#about">About</a></li>
        <li><a href="/search.html">Search</a></li>
        <li class="gh-cta-li"><a href="/contact.html" class="gh-cta">Contact</a></li>
      </ul>
    </nav>
  </div>
</header>
<div id="gh-main" tabindex="-1"></div>'''

# ============================ CANONICAL FOOTER ============================
FOOTER = '''<footer class="gh-footer">
  <div class="gh-foot-inner">
    <div class="gh-foot-grid">
      <div class="gh-foot-brand">
        <img src="/assets/logos/logo-white.png" alt="Grewal RE Group" width="113" height="34">
        <p class="gh-foot-tag">People First. Straight Answers. Strong Results.</p>
        <p><a href="tel:+15126170001">(512) 617-0001</a></p>
        <p><a href="mailto:shivraj.grewal@compass.com">shivraj.grewal@compass.com</a></p>
        <p>2500 Bee Cave Rd, Bldg 3, Ste 200<br>Austin, TX 78746</p>
      </div>
      <nav aria-label="Explore">
        <h2>Explore</h2>
        <ul>
          <li><a href="/communities/">Communities</a></li>
          <li><a href="/search.html">Search Properties</a></li>
          <li><a href="/blog/">Blog</a></li>
          <li><a href="/faq.html">FAQ</a></li>
          <li><a href="/#about">About</a></li>
          <li><a href="/contact.html">Contact</a></li>
        </ul>
      </nav>
      <nav aria-label="Buy and sell">
        <h2>Buy &amp; Sell</h2>
        <ul>
          <li><a href="/#services">Buying</a></li>
          <li><a href="/home-value-estimator.html">Home Value Estimator</a></li>
          <li><a href="/seller-net-proceeds-calculator.html">Net Proceeds Calculator</a></li>
          <li><a href="/relocation-guide.html">Relocating to Austin</a></li>
        </ul>
      </nav>
      <nav aria-label="Guides and resources">
        <h2>Guides</h2>
        <ul>
          <li><a href="/relocation-guide.html">Relocation Guide</a></li>
          <li><a href="/austin-schools-guide.html">Schools Guide</a></li>
          <li><a href="/#resources">All Resources</a></li>
        </ul>
      </nav>
    </div>
    <div class="gh-foot-legal">
      <p>&copy; 2026 Grewal RE Group &middot; Shivraj Grewal &middot; TREC #736060 &middot; Brokered by Compass RE Texas, LLC &middot; TREC Broker #9006927</p>
      <p>
        <a href="/privacy.html">Privacy</a> &middot;
        <a href="/terms.html">Terms</a> &middot;
        <a href="/assets/legal/iabs.pdf" target="_blank" rel="noopener noreferrer">Information About Brokerage Services</a> &middot;
        <a href="/assets/legal/consumer-protection-notice.pdf" target="_blank" rel="noopener noreferrer">TREC Consumer Protection Notice</a> &middot;
        <button type="button" data-cookie-prefs class="gh-link-btn">Cookie preferences</button>
      </p>
    </div>
  </div>
</footer>'''

CSS_LINK = '<link rel="stylesheet" href="/assets/css/site-chrome.css">'
JS_LINK  = '<script defer src="/assets/js/site-chrome.js"></script>'

def remove_balanced_div(s, cls):
    """Remove a <div class="cls" ...>...</div> block with balanced nesting."""
    m = re.search(r'<div class="'+re.escape(cls)+r'"[^>]*>', s)
    if not m: return s
    start = m.start(); depth = 0; end = None
    for mm in re.finditer(r'<div\b|</div>', s[start:]):
        depth += 1 if mm.group(0) == '<div' else -1
        if depth == 0: end = start + mm.end(); break
    if end is None: return s
    seg = s[start:end]
    # drop trailing newline if present
    after = s[end:]
    return s[:start] + after.lstrip('\n') if after[:1] == '\n' else s[:start] + after

def apply_to(path):
    s = open(path, encoding='utf-8').read()
    if 'gh-header' in s:
        # RE-APPLY: swap the existing canonical header block for the current HEADER
        s2 = re.sub(r'<a class="gh-skip".*?<div id="gh-main" tabindex="-1"></div>',
                    lambda m: HEADER, s, count=1, flags=re.S)
        if s2 != s:
            open(path, 'w', encoding='utf-8').write(s2)
            return 'reapplied'
        return 'nochange'
    orig = s
    # 1) replace the FIRST <header> (always the site nav) with canonical header + skip target
    s, n = re.subn(r'<header\b.*?</header>', lambda m: HEADER, s, count=1, flags=re.S)
    if n == 0:
        return 'skip(no-header)'
    # 2) remove any redundant secondary nav <header class="...site-nav...">
    s = re.sub(r'<header[^>]*class="[^"]*\bsite-nav\b[^"]*".*?</header>\s*', '', s, flags=re.S)
    # 3) remove orphaned .mobile-nav sibling (homepage, search)
    s = remove_balanced_div(s, 'mobile-nav')
    # 4) replace the (single) footer with canonical footer
    s = re.sub(r'<footer\b.*?</footer>', lambda m: FOOTER, s, count=1, flags=re.S)
    # 5) ensure chrome CSS + JS are linked
    if '/assets/css/site-chrome.css' not in s:
        s = s.replace('</head>', '  ' + CSS_LINK + '\n</head>', 1)
    if '/assets/js/site-chrome.js' not in s:
        s = s.replace('</body>', JS_LINK + '\n</body>', 1)
    if s == orig:
        return 'nochange'
    open(path, 'w', encoding='utf-8').write(s)
    return 'applied'

def build_contact():
    ga = '''  <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('consent','default',{'ad_storage':'denied','analytics_storage':'denied','ad_user_data':'denied','ad_personalization':'denied','wait_for_update':500});</script>
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-X3GFZCS0JE"></script>
  <script>gtag('js',new Date());gtag('config','G-X3GFZCS0JE');</script>
  <script defer src="/assets/js/consent.js"></script>'''
    schema = '''<script type="application/ld+json">
{"@context":"https://schema.org","@type":"ContactPage","name":"Contact Grewal RE Group","url":"https://grewalregroup.com/contact.html","mainEntity":{"@type":"RealEstateAgent","name":"Grewal RE Group","telephone":"+1-512-617-0001","email":"shivraj.grewal@compass.com","url":"https://grewalregroup.com/","address":{"@type":"PostalAddress","streetAddress":"2500 Bee Cave Rd, Bldg 3, Ste 200","addressLocality":"Austin","addressRegion":"TX","postalCode":"78746","addressCountry":"US"},"areaServed":"Greater Austin, Texas"}}
</script>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":"https://grewalregroup.com/"},{"@type":"ListItem","position":2,"name":"Contact","item":"https://grewalregroup.com/contact.html"}]}
</script>'''
    body = '''<section class="ct-hero">
  <div class="ct-hero-inner">
    <span class="ct-eyebrow">Get in touch</span>
    <h1>Let's talk about your next move</h1>
    <p>Buying, selling, or relocating to Austin? Reach out for straight answers — no pressure, no spam. We typically reply within one business day.</p>
  </div>
</section>
<div class="ct-wrap">
  <div class="ct-grid">
    <div class="ct-info">
      <h2>Reach us directly</h2>
      <ul class="ct-list">
        <li><span class="ct-k">Call or text</span><a href="tel:+15126170001">(512) 617-0001</a></li>
        <li><span class="ct-k">Email</span><a href="mailto:shivraj.grewal@compass.com">shivraj.grewal@compass.com</a></li>
        <li><span class="ct-k">Office</span><address>2500 Bee Cave Rd, Bldg 3, Ste 200<br>Austin, TX 78746</address></li>
        <li><span class="ct-k">Hours</span>Mon–Sat, 8am–7pm CT</li>
      </ul>
      <p class="ct-trec">Shivraj Grewal · TREC #736060 · Brokered by Compass RE Texas, LLC</p>
    </div>
    <div class="ct-form-wrap">
      <h2>Send a message</h2>
      <form name="contact" method="POST" action="/thank-you.html" data-netlify="true" netlify-honeypot="bot-field">
        <input type="hidden" name="form-name" value="contact">
        <p style="position:absolute;left:-9999px"><label>Don't fill: <input name="bot-field"></label></p>
        <div class="ct-field"><label for="cn">Name</label><input id="cn" name="name" type="text" required autocomplete="name"></div>
        <div class="ct-row">
          <div class="ct-field"><label for="ce">Email</label><input id="ce" name="email" type="email" required autocomplete="email"></div>
          <div class="ct-field"><label for="cp">Phone</label><input id="cp" name="phone" type="tel" autocomplete="tel"></div>
        </div>
        <div class="ct-field"><label for="ci">I'm interested in</label>
          <select id="ci" name="interest"><option>Buying</option><option>Selling</option><option>Relocating to Austin</option><option>A home valuation</option><option>Just a question</option></select>
        </div>
        <div class="ct-field"><label for="cm">Message</label><textarea id="cm" name="message" rows="4" required></textarea></div>
        <button type="submit" class="ct-btn">Send Message</button>
        <p class="ct-fine">By sending, you agree to our <a href="/privacy.html">Privacy Policy</a>. We never share your info.</p>
      </form>
    </div>
  </div>
</div>'''
    css = '''  .ct-hero{background:#0a0a0a;color:#fff;padding:4.5rem 1.5rem 3rem;text-align:center}
  .ct-hero-inner{max-width:680px;margin:0 auto}
  .ct-eyebrow{display:block;font-size:.78rem;letter-spacing:.2em;text-transform:uppercase;color:#B8963E;font-weight:600;margin-bottom:.9rem}
  .ct-hero h1{font-family:'Cormorant Garamond',serif;font-size:clamp(2.1rem,5vw,3rem);font-weight:600;margin:0 0 1rem}
  .ct-hero p{color:rgba(255,255,255,.72);line-height:1.7;margin:0}
  .ct-wrap{max-width:1000px;margin:0 auto;padding:3.5rem 1.5rem 4.5rem}
  .ct-grid{display:grid;grid-template-columns:1fr 1.3fr;gap:3rem}
  .ct-info h2,.ct-form-wrap h2{font-family:'Cormorant Garamond',serif;font-size:1.7rem;color:#0a0a0a;margin:0 0 1.25rem}
  .ct-list{list-style:none;margin:0 0 1.5rem;padding:0}
  .ct-list li{padding:.75rem 0;border-bottom:1px solid #e8e3d8;display:flex;flex-direction:column;gap:.2rem}
  .ct-k{font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:#9a9488;font-weight:600}
  .ct-list a{color:#9a7c33;text-decoration:none;font-size:1.05rem}.ct-list a:hover{text-decoration:underline}
  .ct-list address{font-style:normal;color:#4f4a42;line-height:1.5}
  .ct-trec{font-size:.78rem;color:#8a8478;line-height:1.5}
  .ct-field{margin-bottom:1.1rem;display:flex;flex-direction:column}
  .ct-field label{font-size:.78rem;letter-spacing:.06em;text-transform:uppercase;font-weight:600;color:#6b6b6b;margin-bottom:.4rem}
  .ct-field input,.ct-field select,.ct-field textarea{padding:.8rem 1rem;font:1rem Inter,sans-serif;border:1px solid #d8d0c2;border-radius:6px;background:#fff;color:#1a1a1a}
  .ct-field input:focus,.ct-field select:focus,.ct-field textarea:focus{outline:none;border-color:#B8963E;box-shadow:0 0 0 3px rgba(184,150,62,.15)}
  .ct-row{display:grid;grid-template-columns:1fr 1fr;gap:1rem}
  .ct-btn{width:100%;padding:.9rem;background:#B8963E;color:#1a1a1a;font:700 .9rem Inter,sans-serif;letter-spacing:.05em;text-transform:uppercase;border:none;border-radius:6px;cursor:pointer}
  .ct-btn:hover{background:#9a7c33;color:#fff}
  .ct-fine{font-size:.75rem;color:#8a8478;text-align:center;margin-top:.7rem}
  @media(max-width:760px){.ct-grid{grid-template-columns:1fr;gap:2rem}.ct-row{grid-template-columns:1fr}}'''
    page = f'''<!DOCTYPE html>
<html lang="en">
<head>
{ga}
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Contact Grewal RE Group | Austin Real Estate</title>
<meta name="description" content="Contact Grewal RE Group for Austin real estate — buying, selling, or relocating. Call (512) 617-0001, email, or send a message. Straight answers, no pressure.">
<link rel="canonical" href="https://grewalregroup.com/contact.html">
<meta property="og:title" content="Contact Grewal RE Group"><meta property="og:description" content="Get straight answers about buying, selling, or relocating to Austin.">
<meta property="og:type" content="website"><meta property="og:url" content="https://grewalregroup.com/contact.html">
<meta property="og:image" content="https://grewalregroup.com/assets/og-image.jpg">
{schema}
<link rel="icon" type="image/png" href="/assets/logos/logo-mark.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/site-chrome.css">
<style>
{css}
</style>
</head>
<body>
{HEADER}
<main id="main">
{body}
</main>
{FOOTER}
{JS_LINK}
</body>
</html>'''
    open('contact.html', 'w', encoding='utf-8').write(page)
    return 'contact.html written'

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'sample'
    allf = [f for f in glob.glob('**/*.html', recursive=True)
            if '_TEMPLATE' not in f and 'edition/' not in f]
    if mode == 'contact':
        print(build_contact())
    elif mode == 'sample':
        for f in ['index.html', 'communities/west-lake-hills.html', 'blog/austin-home-prices-2026.html']:
            print(f'{f}: {apply_to(f)}')
    elif mode == 'all':
        from collections import Counter
        c = Counter()
        for f in allf:
            c[apply_to(f)] += 1
        print(dict(c))
