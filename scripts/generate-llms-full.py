#!/usr/bin/env python3
"""
Generate llms-full.txt: the expanded companion to llms.txt with the full
inventory of buyer/seller/market content (llms.txt stays a short pointer;
llms-full.txt enumerates every article and community page so an AI agent can
find the exact resource without crawling 300+ pages one at a time).

Run: python3 scripts/generate-llms-full.py
Writes: llms-full.txt at repo root.
"""
import os
import re
import html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://grewalregroup.com"

TITLE_RE = re.compile(r"<title>([^<]*)</title>", re.IGNORECASE)
DESC_RE = re.compile(r'<meta\s+name="description"\s+content="([^"]*)"', re.IGNORECASE)
PUBDATE_RE = re.compile(r'"datePublished"\s*:\s*"([^"]+)"')

# Category buckets by filename keyword, in priority order (first match wins).
CATEGORIES = [
    ("Relocation & Moving Guides", re.compile(r"moving-to|relocation|executive-relocation")),
    ("School District Guides", re.compile(r"isd-school-guide|isd-market-report")),
    ("Neighborhood & Community Guides", re.compile(r"neighborhood|-guide-2026$|tarrytown|westlake|barton|zilker|mueller|colony-park|driftwood|lake-travis|hill-country|wine-country|lost-creek|west-austin")),
    ("Market Reports & Forecasts", re.compile(r"market-report|market-overview|price-forecast|market-timing|price-forecast")),
    ("Buying Guides", re.compile(r"buyer|buying|first-time-homebuyer|homebuyer-programs|is-now-good-time-buy")),
    ("Selling Guides", re.compile(r"sell|seller|home-selling|renovation-roi|concessions|home-selling-costs")),
    ("Investment Guides", re.compile(r"investment|investor|condo-investment|cap-rate")),
    ("Cost & Tax Guides", re.compile(r"property-tax|no-income-tax|cost-comparison|cost-of-living")),
    ("Lifestyle & Comparison Guides", re.compile(r"vs-|dog-friendly|walkable|commute|public-transportation")),
]
DEFAULT_CATEGORY = "Other Austin Real Estate Guides"

SKIP_BLOG_FILES = {
    "_TEMPLATE_ENHANCED.html", "index.html", "buying.html", "selling.html",
    "relocation.html", "neighborhoods.html", "lifestyle.html", "luxury.html",
    "market-reports.html",
}


def extract(path):
    with open(path, encoding="utf-8") as fh:
        content = fh.read()
    t = TITLE_RE.search(content)
    d = DESC_RE.search(content)
    title = html.unescape(t.group(1)).split("|")[0].strip() if t else path
    desc = html.unescape(d.group(1)).strip() if d else ""
    return title, desc


def slug_url(path, base):
    rel = os.path.relpath(path, base).replace(os.sep, "/")
    return f"{SITE}/{('blog/' if base.endswith('blog') else 'communities/')}{rel[:-5]}"


def categorize(filename):
    for label, pattern in CATEGORIES:
        if pattern.search(filename):
            return label
    return DEFAULT_CATEGORY


def build_blog_section():
    blog_dir = os.path.join(ROOT, "blog")
    buckets = {}
    count = 0
    for f in sorted(os.listdir(blog_dir)):
        if not f.endswith(".html") or f in SKIP_BLOG_FILES:
            continue
        path = os.path.join(blog_dir, f)
        title, desc = extract(path)
        url = slug_url(path, blog_dir)
        label = categorize(f)
        buckets.setdefault(label, []).append((title, url, desc))
        count += 1

    lines = [f"## Blog & Resource Articles ({count} total)", ""]
    order = [c for c, _ in CATEGORIES] + [DEFAULT_CATEGORY]
    for label in order:
        items = buckets.get(label)
        if not items:
            continue
        lines.append(f"### {label} ({len(items)})")
        for title, url, desc in items:
            lines.append(f"- {title}: {url}")
            if desc:
                lines.append(f"  {desc}")
        lines.append("")
    return "\n".join(lines)


def build_communities_section():
    c_dir = os.path.join(ROOT, "communities")
    lines = ["## Communities Covered", ""]
    items = []
    for f in sorted(os.listdir(c_dir)):
        if not f.endswith(".html") or f == "index.html":
            continue
        path = os.path.join(c_dir, f)
        title, desc = extract(path)
        url = slug_url(path, c_dir)
        items.append((title, url, desc))
    lines.append(f"Directory: {SITE}/communities/ ({len(items)} community pages, each with a live monthly market report)")
    lines.append("")
    for title, url, desc in items:
        lines.append(f"- {title}: {url}")
        if desc:
            lines.append(f"  {desc}")
    lines.append("")
    return "\n".join(lines)


def build_mcp_section():
    mcp_path = os.path.join(ROOT, "netlify", "functions", "mcp.mjs")
    with open(mcp_path, encoding="utf-8") as fh:
        content = fh.read()
    tool_re = re.compile(r'^\s{2}(\w+):\s*\{\s*\n\s*description:\s*\n?\s*"([^"]+(?:"\s*\+?\s*"[^"]*)*)"', re.MULTILINE)
    # Simpler: split on top-level tool keys inside TOOLS block.
    tools_block_m = re.search(r"const TOOLS = \{(.*?)\n\};", content, re.DOTALL)
    lines = ["## MCP Server Tools (query this site programmatically)", "",
             f"Endpoint: {SITE}/mcp (JSON-RPC 2.0) | Server card: {SITE}/.well-known/mcp-server-card.json", ""]
    if tools_block_m:
        block = tools_block_m.group(1)
        for m in re.finditer(r'^\s{2}(\w+):\s*\{\s*\n\s*description:\s*\n(?:\s*"([^"]*)"[^\n]*\n)+', block, re.MULTILINE):
            pass
        # Fallback: pull name + first description line pairs via simpler regex
        for m in re.finditer(r'^\s{2}(\w+):\s*\{', block, re.MULTILINE):
            name = m.group(1)
            after = block[m.end():m.end() + 400]
            desc_m = re.search(r'"([^"]{20,300}?)"', after)
            desc = desc_m.group(1).replace("\n", " ").strip() if desc_m else ""
            desc = re.sub(r"\s+", " ", desc)
            lines.append(f"- {name}: {desc}")
    lines.append("")
    return "\n".join(lines)


def main():
    header = f"""# Grewal RE Group — Full AI/LLM Content Manifest (llms-full.txt)
# This is the expanded companion to /llms.txt (llmstxt.org standard). Use
# llms.txt for a fast overview; use this file when you need the complete
# inventory of buyer resources, seller resources, market updates, and
# community coverage without crawling every page individually.
# Shivraj Grewal, REALTOR | Grewal RE Group | Austin, TX | Compass brokerage
# Website: {SITE} | Phone: (512) 617-0001 | Email: shivraj.grewal@compass.com
# Brand promise: People First. Straight Answers. Strong Results.

## Site Sections
- Buyer resources: {SITE}/buy (guide), {SITE}/questions/buying.html (19 real Q&A), {SITE}/calculators (affordability/mortgage/rent-vs-buy/buydown)
- Seller resources: {SITE}/sell (guide), {SITE}/questions/selling.html (20 real Q&A), {SITE}/calculators/home-value-estimator, {SITE}/calculators/seller-net-proceeds-calculator
- Relocation resources: {SITE}/relocation-guide (154-page Austin Relocation Guide), {SITE}/questions/relocation.html (16 real Q&A)
- Market updates: {SITE}/blog/ (322 articles, see categorized index below), community-level live monthly reports on every {SITE}/communities/ page
- About: {SITE}/about, {SITE}/reviews (119 five-star Google reviews plus Zillow/Realtor.com)
- Contact: {SITE}/contact, or submit via the MCP tool request_consultation

"""
    out = header + build_mcp_section() + "\n" + build_communities_section() + "\n" + build_blog_section()
    out_path = os.path.join(ROOT, "llms-full.txt")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(out)
    print(f"Wrote {out_path} ({out.count(chr(10))} lines)")


if __name__ == "__main__":
    main()
