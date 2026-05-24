#!/usr/bin/env python3
"""
Build the 22 community pages from data + blog index + template.

What it does:
  1. On first run, extracts each community's existing description, ZIP, and
     related-community list from /communities/<slug>.html into data/communities.json.
     Subsequent runs use the JSON as the source of truth — edit that file.
  2. Generates the new community page for every slug in the JSON. Pages have:
       - Hero (name, description, ZIP)
       - Market signup (Netlify Forms lead magnet — "Send me the report")
       - Commentary (Shivraj's take, editable in JSON)
       - Blog insights (auto-matched by keyword in blog filename)
       - Nearby communities (from JSON)
       - CTA
     The Compass iframe is removed.
  3. Appends the new CSS sections to communities.css if not already present.

Idempotent. Re-run after editing data/communities.json or adding blogs.
"""

import json
import re
import html
from pathlib import Path
from datetime import date

ROOT      = Path("/Users/shivrajsinghgrewal/Library/Mobile Documents/com~apple~CloudDocs/Desktop/realestate-landing")
BLOG_DIR  = ROOT / "blog"
COMM_DIR  = ROOT / "communities"
DATA_DIR  = ROOT / "data"
DATA_FILE = DATA_DIR / "communities.json"
CSS_FILE  = COMM_DIR / "communities.css"

# ────────────────────────────────────────────────────────────────
# Community slugs and their default commentary (used on first bootstrap)
# ────────────────────────────────────────────────────────────────

DEFAULT_COMMENTARY = {
    "barton-creek": "The gates, the golf, the trails. Buyers here value privacy and amenity-rich community over raw downtown access. Inventory is the binding constraint, so plan to wait for the right listing rather than force a fit.",
    "barton-hills": "South Austin character with central access. Buyers trade lot size for Greenbelt walks, food culture, and a 10-minute downtown commute. Smaller homes, but the lifestyle premium is real.",
    "buda": "South suburb growth. Good schools, growing infrastructure, accessible commutes. Buyers here choose space and value over central proximity.",
    "central-austin": "The broad central corridor: walkability, food, Mueller-adjacent. Tighter lots, character homes, strong investor interest. Pricing varies meaningfully by exact pocket, so the comp set matters.",
    "circle-c-ranch": "Family-focused, master-planned, pools and trails. Less luxury price tag, more lifestyle value. Best for buyers prioritizing schools, amenities, and community over downtown adjacency.",
    "downtown": "Downtown is condos. Verticality buys you skyline views and walkability to everything. Best for buyers who value lock-and-leave living over backyard space.",
    "dripping-springs": "Texas Hill Country with proximity to Austin. Acreage, master-planned communities (Belterra, Caliterra, Headwaters), excellent schools. A 30-minute commute, but the lifestyle trade is real.",
    "east-austin": "East Austin keeps reinventing itself. Mueller, Holly, French Place, Govalle, each pocket has its own pace. Strong for buyers betting on long-term appreciation.",
    "fredericksburg": "Hill Country wine country. Buyers here are usually second-home or relocation, drawn by Main Street, wineries, and ranchette acreage. Different rhythm than Austin proper.",
    "georgetown": "North-corridor anchor city. Historic downtown, Sun City retirement community, Southwestern University. Family-friendly with strong long-term appreciation.",
    "kyle": "Hays County growth corridor. Strong appreciation, new construction, increasingly diverse amenities. Watch the school district and master-planned community choices carefully.",
    "lake-travis": "Waterfront premium, lake-access premium, and pure-view premium are three different markets. Inventory varies by sub-area (Hudson Bend, Point Venture, Lago Vista). Patience pays off.",
    "leander-cedar-park": "North-corridor suburbia with strong family schools (Leander ISD) and accelerating tech-corridor growth. Newer construction dominates. Predictable buyer demographics, predictable pricing.",
    "mueller": "Mueller is the master-planned anomaly: New Urbanism in the heart of Austin. Walkable, strong schools, amenities, mixed-use. Predictable inventory cycles, premium pricing.",
    "north-central-austin": "The bridge between downtown and the suburbs. Allandale, Crestview, Brentwood. Affordable entry into central Austin, strong school options, and quick redevelopment activity.",
    "northwest-hills": "Northwest Hills offers hill country views without leaving the central core. Older inventory, larger lots, and Anderson High School. Buyers seeking established neighborhood feel.",
    "pflugerville": "Affordable entry into the Austin metro with growing amenities. Strong demand from first-time buyers and investors. Inventory turns reliably, so deals move quickly when priced right.",
    "round-rock": "Strong corporate base (Dell) and Round Rock ISD. Suburb life with good amenities. Buyer pool is wide; sellers move quickly when priced right.",
    "tarrytown": "Tarrytown's defining feature is supply. Lots are limited, character is irreplaceable, and most sellers prefer a quiet, pre-marketed process over a public listing. Buying here means patience plus access.",
    "travis-heights": "Travis Heights is the most charming pocket of South Austin. Walkable to South Congress, Continental Club, downtown over the bridge. Tight inventory, fierce buyer competition.",
    "west-lake-hills": "West Lake Hills sells on schools and trees, not square footage. Eanes ISD is the magnet. Smart buyers focus on the lot, the canopy, and walkability to downtown, not granite countertops.",
    "zilker": "Zilker sits at the intersection of Barton Springs, downtown, and South Lamar. Walkable, central, and impossible to expand. Buyers here pay for location and lifestyle, not square footage.",
}

# Blog-filename match patterns per community slug
BLOG_PATTERNS = {
    "barton-creek":         [r"barton-creek"],
    "barton-hills":         [r"barton-hills"],
    "buda":                 [r"(?:^|[-/])buda(?:[-.]|$)"],
    "central-austin":       [r"(?<![a-z-])central-austin"],
    "circle-c-ranch":       [r"circle-c"],
    "downtown":             [r"downtown.*austin", r"austin.*downtown", r"rainey-street-downtown"],
    "dripping-springs":     [r"dripping-springs", r"belterra", r"caliterra", r"headwaters"],
    "east-austin":          [r"east-austin"],
    "fredericksburg":       [r"fredericksburg"],
    "georgetown":           [r"georgetown"],
    "kyle":                 [r"(?:^|[-/])kyle(?:[-.]|$)"],
    "lake-travis":          [r"lake-travis", r"hudson-bend", r"jonestown", r"point-venture"],
    "leander-cedar-park":   [r"leander", r"cedar-park"],
    "mueller":              [r"mueller"],
    "north-central-austin": [r"north-central", r"^n-central"],
    "northwest-hills":      [r"northwest-hills", r"northwest-austin"],
    "pflugerville":         [r"pflugerville"],
    "round-rock":           [r"round-rock"],
    "tarrytown":            [r"tarrytown"],
    "travis-heights":       [r"travis-heights"],
    "west-lake-hills":      [r"west-lake-hills", r"westlake-hills", r"westlake-eanes"],
    "zilker":               [r"zilker"],
}

# ────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────

TITLE_RE       = re.compile(r"<title>(.*?)</title>", re.DOTALL | re.IGNORECASE)
H1_RE          = re.compile(r"<h1>(.*?)</h1>", re.DOTALL | re.IGNORECASE)
HERO_P_RE      = re.compile(r'<section class="cm-detail-hero".*?<p>(.*?)</p>', re.DOTALL | re.IGNORECASE)
ZIP_RE         = re.compile(r'<span class="cm-zip">(.*?)</span>', re.DOTALL | re.IGNORECASE)
META_DESC_RE   = re.compile(r'<meta name="description" content="(.*?)"', re.DOTALL | re.IGNORECASE)
RELATED_RE     = re.compile(r'<section class="cm-related"(?! cm-related--blog).*?</section>', re.DOTALL | re.IGNORECASE)
RELATED_HREF_RE = re.compile(r'<a href="([a-z0-9-]+)\.html" class="cm-card">', re.IGNORECASE)
GREWAL_SUFFIX_RE = re.compile(r"\s*\|\s*Grewal RE Group.*$", re.IGNORECASE)


def strip_html(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s).strip()


def slug_to_name(slug: str) -> str:
    overrides = {
        "leander-cedar-park": "Leander / Cedar Park",
        "west-lake-hills": "West Lake Hills",
        "north-central-austin": "North Central Austin",
        "circle-c-ranch": "Circle C Ranch",
    }
    return overrides.get(slug, slug.replace("-", " ").title())


def extract_blog_title(p: Path) -> str:
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return p.stem.replace("-", " ").title()
    m = TITLE_RE.search(txt)
    if not m:
        return p.stem.replace("-", " ").title()
    t = m.group(1).strip()
    t = GREWAL_SUFFIX_RE.sub("", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def find_blogs(slug: str):
    patterns = BLOG_PATTERNS.get(slug, [])
    seen = set()
    matches = []
    for f in sorted(BLOG_DIR.iterdir()):
        if not f.name.endswith(".html"): continue
        if f.name.startswith("_"): continue
        for pat in patterns:
            if re.search(pat, f.name, re.IGNORECASE):
                if f.name not in seen:
                    seen.add(f.name)
                    matches.append(f)
                break
    return matches


# ────────────────────────────────────────────────────────────────
# Bootstrap: extract from existing community pages → JSON
# ────────────────────────────────────────────────────────────────

def bootstrap_from_existing():
    """Build communities.json by reading each existing /communities/<slug>.html."""
    communities = {}
    for slug in BLOG_PATTERNS.keys():
        page = COMM_DIR / f"{slug}.html"
        if not page.exists():
            print(f"  WARN: {slug}.html missing — using defaults")
            communities[slug] = {
                "name": slug_to_name(slug),
                "zip": "",
                "description": "",
                "metaDescription": "",
                "commentary": DEFAULT_COMMENTARY.get(slug, ""),
                "related": [],
            }
            continue
        html_text = page.read_text(encoding="utf-8")

        h1 = H1_RE.search(html_text)
        name = strip_html(h1.group(1)) if h1 else slug_to_name(slug)

        hp = HERO_P_RE.search(html_text)
        description = strip_html(hp.group(1)) if hp else ""

        zp = ZIP_RE.search(html_text)
        zip_code = strip_html(zp.group(1)) if zp else ""

        md = META_DESC_RE.search(html_text)
        meta_description = (md.group(1) if md else "").strip()

        related = []
        rel_section = RELATED_RE.search(html_text)
        if rel_section:
            related = RELATED_HREF_RE.findall(rel_section.group(0))[:3]

        communities[slug] = {
            "name": name,
            "zip": zip_code,
            "description": description,
            "metaDescription": meta_description,
            "commentary": DEFAULT_COMMENTARY.get(slug, ""),
            "related": related,
        }
    return communities


# ────────────────────────────────────────────────────────────────
# Page template
# ────────────────────────────────────────────────────────────────

def render_page(slug, c, blogs, today_iso):
    name = c["name"]
    name_html = html.escape(name)
    zip_code = html.escape(c.get("zip", ""))
    desc = c.get("description", "") or f"Live market insights for {name}, Austin TX."
    desc_html = html.escape(desc)
    meta_desc = c.get("metaDescription") or f"{name} Austin market insights, listings, and live data. Get the monthly {name} report by email. Local intel from Grewal RE Group."
    meta_desc_html = html.escape(meta_desc, quote=True)
    commentary = c.get("commentary", "") or DEFAULT_COMMENTARY.get(slug, "")
    commentary_html = html.escape(commentary)

    related_slugs = c.get("related", []) or []
    related_cards = []
    for rs in related_slugs:
        rname = slug_to_name(rs)
        related_cards.append(
            f'      <a href="{rs}.html" class="cm-card">'
            f'<span class="cm-card-name">{html.escape(rname)}</span>'
            f'<span class="cm-card-arrow">→</span></a>'
        )
    related_html = "\n".join(related_cards) if related_cards else \
        '      <a href="index.html" class="cm-card"><span class="cm-card-name">All Communities</span><span class="cm-card-arrow">→</span></a>'

    if blogs:
        blog_cards = []
        for b in blogs:
            t = extract_blog_title(b)
            blog_cards.append(
                f'      <a href="../blog/{b.name}" class="cm-card">'
                f'<span class="cm-card-name">{html.escape(t)}</span>'
                f'<span class="cm-card-arrow">→</span></a>'
            )
        blog_grid = "\n".join(blog_cards)
        blog_section = f"""<section class="cm-related cm-related--blog">
  <div class="container">
    <h2>{name_html} Insights</h2>
    <p class="cm-related-sub">Deep dives, buyer guides, and market commentary from our writing on {name_html}.</p>
    <div class="cm-related-grid">
{blog_grid}
    </div>
  </div>
</section>"""
    else:
        blog_section = f"""<section class="cm-related cm-related--blog">
  <div class="container">
    <h2>{name_html} Insights</h2>
    <p class="cm-related-sub">Deep dives, buyer guides, and market commentary from our writing on {name_html}.</p>
    <div class="cm-related-grid">
      <p class="cm-related-empty">New {name_html} insights are coming soon. In the meantime, <a href="../index.html#contact">ask us anything about the area</a>.</p>
    </div>
  </div>
</section>"""

    zip_block = f'<span class="cm-zip">{zip_code}</span>' if zip_code else ""

    schema = {
        "@context": "https://schema.org",
        "@type": "Place",
        "name": name,
        "description": desc,
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "Austin",
            "addressRegion": "TX",
            "postalCode": zip_code,
            "addressCountry": "US",
        },
        "url": f"https://grewalregroup.com/communities/{slug}.html",
    }
    schema_json = json.dumps(schema, indent=2)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name_html} Real Estate Market Insights | Grewal RE Group</title>
<meta name="description" content="{meta_desc_html}">
<link rel="canonical" href="https://grewalregroup.com/communities/{slug}.html">

<meta property="og:title" content="{name_html} Real Estate Market Insights">
<meta property="og:description" content="{meta_desc_html}">
<meta property="og:type" content="website">
<meta property="og:url" content="https://grewalregroup.com/communities/{slug}.html">
<meta name="twitter:card" content="summary_large_image">
<meta name="robots" content="index, follow">

<link rel="icon" type="image/png" href="../assets/logos/logo-mark.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="communities.css">

<script type="application/ld+json">
{schema_json}
</script>
</head>
<body>

<header class="cm-header">
  <div class="cm-header-inner">
    <a href="../index.html" class="cm-header-logo" aria-label="Grewal RE Group home"><img src="../assets/logos/logo-black.png" alt="Grewal RE Group"></a>
    <nav class="cm-header-nav">
      <a href="../index.html#about">About</a>
      <a href="../index.html#team">Team</a>
      <a href="index.html">Communities</a>
      <a href="../blog/index.html">Insights</a>
      <a href="../index.html#contact" class="cm-cta">Schedule a Call</a>
    </nav>
  </div>
</header>

<section class="cm-detail-hero">
  <div class="cm-detail-hero-inner">
    <p class="cm-breadcrumb"><a href="../index.html">Home</a> <span class="sep">/</span> <a href="index.html">Communities</a> <span class="sep">/</span> {name_html}</p>
    <h1>{name_html}</h1>
    <p>{desc_html}</p>
    {zip_block}
  </div>
</section>

<!-- ─── MARKET REPORT LEAD MAGNET (Netlify Forms) ─── -->
<section class="cm-signup">
  <div class="cm-signup-inner">
    <div class="cm-signup-text">
      <p class="eyebrow" style="color: var(--gold-light)">Monthly Market Insights</p>
      <h2>Get the latest {name_html} market report</h2>
      <p>Median sold price, days on market, inventory trends, and what they mean for {name_html} buyers and sellers. Sent monthly by Shivraj Grewal. No fluff, no spam, unsubscribe anytime.</p>
    </div>
    <form class="cm-signup-form" name="insights-signup" method="POST" action="/thank-you.html" data-netlify="true" netlify-honeypot="bot-field">
      <input type="hidden" name="form-name" value="insights-signup">
      <input type="hidden" name="community" value="{name_html}">
      <p style="position:absolute;left:-9999px"><label>Don't fill: <input name="bot-field"></label></p>
      <label for="signup-name-{slug}" class="cm-sr-only">Your name</label>
      <input id="signup-name-{slug}" type="text" name="name" placeholder="Your name" required>
      <label for="signup-email-{slug}" class="cm-sr-only">Your email</label>
      <input id="signup-email-{slug}" type="email" name="email" placeholder="your@email.com" required>
      <button type="submit" class="btn btn-gold">Send me the {name_html} report</button>
      <p class="cm-signup-meta">By submitting, you'll get the monthly {name_html} email. We never share your details.</p>
    </form>
  </div>
</section>

<!-- ─── COMMENTARY ─── -->
<section class="cm-commentary">
  <div class="container">
    <p class="eyebrow">Shivraj's Take</p>
    <h2>What's actually happening in {name_html} right now</h2>
    <p>{commentary_html}</p>
    <p class="cm-commentary-meta">— Shivraj Grewal, Grewal RE Group · Updated {today_iso}</p>
  </div>
</section>

<!-- ─── INSIGHTS (auto-matched blog posts) ─── -->
{blog_section}

<!-- ─── NEARBY COMMUNITIES ─── -->
<section class="cm-related">
  <div class="container">
    <h2>Nearby Communities</h2>
    <p class="cm-related-sub">Market insights for nearby Austin neighborhoods.</p>
    <div class="cm-related-grid">
{related_html}
    </div>
  </div>
</section>

<!-- ─── CTA ─── -->
<section class="cm-cta-section">
  <h2>Want a custom analysis on a specific street in {name_html}?</h2>
  <p>Neighborhood-level reports show the pattern. Street-level reports show your decision. I'll pull a custom comp-set for the exact block you're targeting, no obligation.</p>
  <a href="../index.html#contact" class="btn btn-gold">Request Your Analysis</a>
</section>

<footer class="cm-footer">
  <div class="cm-footer-inner">
    <div class="cm-footer-top">
      <div>
        <a href="../index.html" class="cm-footer-logo"><img src="../assets/logos/logo-white.png" alt="Grewal RE Group"></a>
        <p class="cm-footer-tagline">People First. Straight Answers. Strong Results.</p>
        <p class="cm-footer-about">Austin's luxury real estate team, Shivraj Grewal and Grewal RE Group. Westlake Hills, Tarrytown, Barton Creek, and the central + east Austin growth corridors.</p>
      </div>
      <div>
        <h4>Navigate</h4>
        <ul>
          <li><a href="../index.html">Home</a></li>
          <li><a href="../index.html#about">About</a></li>
          <li><a href="../index.html#team">Team</a></li>
          <li><a href="index.html">Communities</a></li>
          <li><a href="../blog/index.html">Insights</a></li>
          <li><a href="../index.html#contact">Contact</a></li>
        </ul>
      </div>
      <div>
        <h4>Contact</h4>
        <ul>
          <li><a href="tel:+15126170001">(512) 617-0001</a></li>
          <li><a href="mailto:shivraj.grewal@compass.com">shivraj.grewal@compass.com</a></li>
          <li>2500 Bee Cave Rd, Bldg 3, Ste 200<br>Austin, TX 78746</li>
        </ul>
      </div>
    </div>
    <div class="cm-footer-bottom">
      © 2026 Grewal RE Group · All Rights Reserved · Shivraj Grewal · TREC #736060 · Compass · TREC Broker #9006927<br>
      <a href="https://www.trec.texas.gov/sites/default/files/pdf-forms/IABS%201-0.pdf" target="_blank" rel="noopener">Information About Brokerage Services</a> · <a href="https://www.trec.texas.gov/forms/consumer-protection-notice" target="_blank" rel="noopener">TREC Consumer Protection Notice</a> · <a href="../SOURCES.md" target="_blank" rel="noopener">Sources</a>
    </div>
  </div>
</footer>

</body>
</html>
"""


# ────────────────────────────────────────────────────────────────
# CSS additions
# ────────────────────────────────────────────────────────────────

CSS_ADDITIONS = """
/* ─── Email signup (lead magnet) ─── */
.cm-signup { background: var(--ink); color: #fff; padding: 4rem 0; }
.cm-signup-inner {
  max-width: 1100px; margin: 0 auto; padding: 0 1.5rem;
  display: grid; grid-template-columns: 1.2fr 1fr; gap: 3rem; align-items: center;
}
@media (max-width: 800px) {
  .cm-signup-inner { grid-template-columns: 1fr; gap: 2rem; }
}
.cm-signup-text h2 { color: #fff; font-size: clamp(1.6rem, 3vw, 2.2rem); margin: 0 0 .75rem; line-height: 1.15; }
.cm-signup-text p  { color: rgba(255,255,255,0.75); margin: 0; font-size: 1rem; }
.cm-signup-form    { display: flex; flex-direction: column; gap: .75rem; }
.cm-signup-form input[type="email"],
.cm-signup-form input[type="text"] {
  padding: .9rem 1rem; font-family: inherit; font-size: 0.95rem;
  background: #fff; color: var(--ink);
  border: 1px solid rgba(255,255,255,0.2); border-radius: 2px; outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.cm-signup-form input:focus { border-color: var(--gold); box-shadow: 0 0 0 3px rgba(184,150,62,0.25); }
.cm-signup-form button {
  padding: .95rem 1rem; font-family: inherit; font-size: 0.78rem;
  background: var(--gold); color: #fff;
  border: 1px solid var(--gold); border-radius: 2px;
  letter-spacing: 0.1em; text-transform: uppercase; font-weight: 600; cursor: pointer;
  transition: background 0.2s;
}
.cm-signup-form button:hover { background: var(--gold-dark); }
.cm-signup-meta { margin: .5rem 0 0; font-size: 0.78rem; color: rgba(255,255,255,0.55); }
.cm-sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); border: 0; }

/* ─── Commentary block ─── */
.cm-commentary { background: var(--cream); padding: 4rem 0; }
.cm-commentary .container { max-width: 760px; }
.cm-commentary h2 { font-size: clamp(1.6rem, 3vw, 2.2rem); margin: 0 0 1.5rem; line-height: 1.15; }
.cm-commentary p  { font-size: 1.05rem; line-height: 1.75; color: var(--ink); margin: 0 0 1.25rem; }
.cm-commentary-meta { margin-top: 1.5rem; font-size: 0.85rem; color: var(--muted); font-style: italic; }

/* ─── Empty insights message ─── */
.cm-related-empty {
  grid-column: 1 / -1;
  text-align: center; max-width: 32rem; margin: 0 auto;
  color: var(--muted); font-size: 0.95rem;
  padding: 1.5rem;
  background: #fff; border: 1px dashed var(--line);
}
.cm-related-empty a { color: var(--gold); text-decoration: none; font-weight: 600; }
"""

CSS_MARKER = "/* ─── Email signup (lead magnet) ─── */"


# ────────────────────────────────────────────────────────────────
# Run
# ────────────────────────────────────────────────────────────────

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: ensure communities.json exists
    if not DATA_FILE.exists():
        print("Bootstrapping data/communities.json from existing /communities/<slug>.html...")
        data = {
            "lastUpdated": date.today().isoformat(),
            "dataSource": "Compiled by Grewal RE Group from Unlock MLS data and on-the-ground experience.",
            "communities": bootstrap_from_existing(),
        }
        DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"  WROTE: {DATA_FILE}")
    else:
        print(f"Reading existing data/communities.json")
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    # Step 2: regenerate each community page
    today_iso = date.today().strftime("%B %Y")
    print(f"\n{'Community':<24}{'Blogs':>6}  Status")
    print("-" * 60)
    for slug, c in data["communities"].items():
        page = COMM_DIR / f"{slug}.html"
        blogs = find_blogs(slug)
        new_html = render_page(slug, c, blogs, today_iso)
        page.write_text(new_html, encoding="utf-8")
        print(f"{c['name']:<24}{len(blogs):>6}  REBUILT")
    print("-" * 60)
    print(f"Generated {len(data['communities'])} community pages.")

    # Step 3: append CSS if not already present
    css = CSS_FILE.read_text(encoding="utf-8")
    if CSS_MARKER not in css:
        CSS_FILE.write_text(css.rstrip() + "\n" + CSS_ADDITIONS, encoding="utf-8")
        print(f"\nAppended new sections to {CSS_FILE.name}")
    else:
        print(f"\nCSS additions already present in {CSS_FILE.name}, skipping.")


if __name__ == "__main__":
    main()
