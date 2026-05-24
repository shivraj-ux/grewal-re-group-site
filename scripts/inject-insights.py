#!/usr/bin/env python3
"""Inject 'Related Insights' sections into each /communities/{slug}.html page,
matching blog posts by filename keyword. Idempotent — re-running replaces
any previously injected block."""

import re
from pathlib import Path

ROOT = Path("/Users/shivrajsinghgrewal/Library/Mobile Documents/com~apple~CloudDocs/Desktop/realestate-landing")
BLOG_DIR = ROOT / "blog"
COMM_DIR = ROOT / "communities"

# slug -> (display name, list of regex patterns for matching blog filenames)
COMMUNITIES = {
    "barton-creek":         ("Barton Creek",         [r"barton-creek"]),
    "barton-hills":         ("Barton Hills",         [r"barton-hills"]),
    "buda":                 ("Buda",                 [r"(?:^|[-/])buda(?:[-.]|$)"]),
    "central-austin":       ("Central Austin",       [r"(?<![a-z-])central-austin"]),
    "circle-c-ranch":       ("Circle C Ranch",       [r"circle-c"]),
    "downtown":             ("Downtown",             [r"downtown.*austin", r"austin.*downtown", r"rainey-street-downtown"]),
    "dripping-springs":     ("Dripping Springs",     [r"dripping-springs", r"belterra", r"caliterra", r"headwaters"]),
    "east-austin":          ("East Austin",          [r"east-austin"]),
    "fredericksburg":       ("Fredericksburg",       [r"fredericksburg"]),
    "georgetown":           ("Georgetown",           [r"georgetown"]),
    "kyle":                 ("Kyle",                 [r"(?:^|[-/])kyle(?:[-.]|$)"]),
    "lake-travis":          ("Lake Travis",          [r"lake-travis", r"hudson-bend", r"jonestown", r"point-venture"]),
    "leander-cedar-park":   ("Leander / Cedar Park", [r"leander", r"cedar-park"]),
    "mueller":              ("Mueller",              [r"mueller"]),
    "north-central-austin": ("North Central Austin", [r"north-central", r"^n-central"]),
    "northwest-hills":      ("Northwest Hills",      [r"northwest-hills", r"northwest-austin"]),
    "pflugerville":         ("Pflugerville",         [r"pflugerville"]),
    "round-rock":           ("Round Rock",           [r"round-rock"]),
    "tarrytown":            ("Tarrytown",            [r"tarrytown"]),
    "travis-heights":       ("Travis Heights",       [r"travis-heights"]),
    "west-lake-hills":      ("West Lake Hills",      [r"west-lake-hills", r"westlake-hills", r"westlake-eanes"]),
    "zilker":               ("Zilker",               [r"zilker"]),
}

# ------------- helpers -------------

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.DOTALL | re.IGNORECASE)
SUFFIX_RE = re.compile(r"\s*\|\s*Grewal RE Group.*$", re.IGNORECASE)
INJECT_START = "<!-- INSIGHTS:START -->"
INJECT_END   = "<!-- INSIGHTS:END -->"

def extract_title(p: Path) -> str:
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return p.stem.replace("-", " ").title()
    m = TITLE_RE.search(txt)
    if not m:
        return p.stem.replace("-", " ").title()
    t = m.group(1).strip()
    t = SUFFIX_RE.sub("", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def find_blogs(patterns):
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

def render_section(name: str, blogs):
    if not blogs:
        cards = (
            '      <p class="cm-related-empty">New '
            f'{name} insights are coming soon. In the meantime, '
            '<a href="../index.html#contact">ask us anything about the area</a>.</p>'
        )
    else:
        cards_html = []
        for b in blogs:
            title = extract_title(b)
            cards_html.append(
                f'      <a href="../blog/{b.name}" class="cm-card">'
                f'<span class="cm-card-name">{title}</span>'
                f'<span class="cm-card-arrow">→</span></a>'
            )
        cards = "\n".join(cards_html)
    return f"""{INJECT_START}
<section class="cm-related cm-related--blog">
  <div class="container">
    <h2>{name} Insights</h2>
    <p class="cm-related-sub">Deep dives, buyer guides, and market commentary from our writing on {name}.</p>
    <div class="cm-related-grid">
{cards}
    </div>
  </div>
</section>
{INJECT_END}"""

def upsert(html: str, block: str) -> str:
    # If a previous block exists, replace it.
    if INJECT_START in html and INJECT_END in html:
        return re.sub(
            re.escape(INJECT_START) + r".*?" + re.escape(INJECT_END),
            lambda m: block,
            html,
            count=1,
            flags=re.DOTALL,
        )
    # Otherwise insert before the CTA section ("cm-cta-section"), falling back to before </body>.
    cta_anchor = '<section class="cm-cta-section">'
    if cta_anchor in html:
        return html.replace(cta_anchor, block + "\n\n" + cta_anchor, 1)
    return html.replace("</body>", block + "\n\n</body>", 1)

# ------------- run -------------

print(f"{'Community':<24}{'Posts':>6}  Status")
print("-" * 60)
total_posts = 0
for slug, (name, patterns) in COMMUNITIES.items():
    page = COMM_DIR / f"{slug}.html"
    if not page.exists():
        print(f"{name:<24}{'--':>6}  page missing")
        continue
    blogs = find_blogs(patterns)
    total_posts += len(blogs)
    block = render_section(name, blogs)
    html = page.read_text(encoding="utf-8")
    new_html = upsert(html, block)
    if new_html != html:
        page.write_text(new_html, encoding="utf-8")
        action = "INJECTED"
    else:
        action = "UNCHANGED"
    print(f"{name:<24}{len(blogs):>6}  {action}")

print("-" * 60)
print(f"TOTAL: {total_posts} blog cards across {len(COMMUNITIES)} communities")
