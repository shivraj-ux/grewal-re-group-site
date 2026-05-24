#!/usr/bin/env python3
"""
Grewal RE Group — Daily Site Agent
Runs every morning at 6 AM CST via GitHub Actions.

Steps executed:
  1. Update market data JSON from public sources
  2. Audit competitor sites for new content / gaps
  3. Create one piece of daily content (rotation)
  4. Write PR description to /tmp/agent-pr-body.md
  5. Update logs/agent-errors.json with any failures

Requires:
  ANTHROPIC_API_KEY environment variable
"""

import json
import os
import sys
import traceback
from datetime import datetime, timezone, timedelta
from pathlib import Path

import anthropic
import requests

# ─── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
MARKET_DATA_DIR = DATA_DIR / "market-data"
LOGS_DIR = ROOT / "logs"
BLOG_DIR = ROOT / "blog"
COMMUNITIES_DIR = ROOT / "communities"
PR_BODY_PATH = Path("/tmp/agent-pr-body.md")

# ─── Brand constants ──────────────────────────────────────────────────────────
TODAY = datetime.now(tz=timezone(timedelta(hours=-5))).strftime("%Y-%m-%d")
TODAY_DISPLAY = datetime.now(tz=timezone(timedelta(hours=-5))).strftime("%B %-d, %Y")
AGENT_VERSION = "1.0"

# ─── Error log ────────────────────────────────────────────────────────────────
errors = []
warnings = []
changes_made = []

def log_error(step: str, target: str, error: str):
    errors.append({
        "step": step,
        "target": target,
        "error": error,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action": "Skipped. Will retry on next run."
    })
    print(f"ERROR [{step}] {target}: {error}", file=sys.stderr)

def log_warning(step: str, message: str):
    warnings.append({
        "step": step,
        "message": message,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })
    print(f"WARNING [{step}]: {message}")

def log_change(description: str, file_path: str = ""):
    changes_made.append({"description": description, "file": file_path})
    print(f"CHANGE: {description}" + (f" ({file_path})" if file_path else ""))


# ─── Step 3: Market data update ───────────────────────────────────────────────
def update_market_data():
    """
    Fetch latest Austin market data via Claude web search and update
    data/market-data/latest.json.
    """
    print("\n=== STEP 3: Market Data Update ===")
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    prompt = f"""You are updating market data for Grewal RE Group, an Austin TX luxury real estate team.
Today is {TODAY_DISPLAY}.

Search for and return the most recent available data for:
1. Austin metro median sold home price (most recent month available)
2. Westlake Hills (78746) median sold price and days on market
3. Barton Creek (78735) median sold price
4. Steiner Ranch (78732) median sold price and days on market
5. Austin metro months of inventory
6. Austin luxury segment ($1M+) months of supply and median price

Return ONLY a JSON object with this exact structure (no markdown, no explanation):
{{
  "date": "{TODAY}",
  "source": "Austin Board of Realtors, Redfin, or credible source name",
  "austin_metro": {{
    "medianSoldPrice": number,
    "medianSoldPriceYoYChange": "string like +5.2%",
    "monthsOfInventory": number,
    "avgDaysOnMarket": "string like 85-106"
  }},
  "luxury_segment": {{
    "threshold": 1000000,
    "medianPrice": number,
    "monthsOfSupply": number
  }},
  "neighborhoods": {{
    "westlake_hills": {{
      "zip": "78746",
      "medianSoldPrice": number,
      "avgDaysOnMarket": "string",
      "dataSource": "source name"
    }},
    "barton_creek": {{
      "zip": "78735",
      "medianSoldPrice": number,
      "dataSource": "source name"
    }},
    "steiner_ranch": {{
      "zip": "78732",
      "medianSoldPrice": number,
      "avgDaysOnMarket": "string",
      "dataSource": "source name"
    }}
  }},
  "lastUpdated": "{TODAY}",
  "note": "brief note about data quality or gaps"
}}

If a specific value cannot be verified, use null and note it.
Do NOT fabricate numbers. Only return data you found from real sources."""

    try:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.content[0].text.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        market_data = json.loads(raw)

        MARKET_DATA_DIR.mkdir(parents=True, exist_ok=True)
        out_path = MARKET_DATA_DIR / "latest.json"
        out_path.write_text(json.dumps(market_data, indent=2))
        # Also write dated copy
        dated_path = MARKET_DATA_DIR / f"{TODAY}.json"
        dated_path.write_text(json.dumps(market_data, indent=2))

        log_change("Market data updated", str(out_path.relative_to(ROOT)))
        return market_data

    except Exception as e:
        log_error("STEP 3 — Market Data", "data/market-data/latest.json", str(e))
        return None


# ─── Step 2: Competitor audit ─────────────────────────────────────────────────
def audit_competitors():
    """
    Crawl competitor sites and log findings.
    """
    print("\n=== STEP 2: Competitor Audit ===")
    competitors = [
        {"name": "Kumara Wilcoxon", "url": "https://kumarawilcoxon.com"},
        {"name": "Meryl Hawk", "url": "https://merylhawk.com"},
        {"name": "Luxe Homes Austin", "url": "https://www.luxehomesaustin.com"},
    ]

    findings = []
    for comp in competitors:
        try:
            resp = requests.get(comp["url"], timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200:
                findings.append({
                    "name": comp["name"],
                    "url": comp["url"],
                    "status": "crawled",
                    "httpStatus": resp.status_code,
                    "crawledAt": datetime.utcnow().isoformat() + "Z",
                    "contentLength": len(resp.text)
                })
                print(f"  OK: {comp['name']} ({resp.status_code})")
            else:
                log_error("STEP 2 — Competitor Crawl", comp["url"], f"HTTP {resp.status_code}")
                findings.append({"name": comp["name"], "url": comp["url"], "status": "error", "httpStatus": resp.status_code})
        except Exception as e:
            log_error("STEP 2 — Competitor Crawl", comp["url"], str(e))
            findings.append({"name": comp["name"], "url": comp["url"], "status": "error", "error": str(e)})

    log_path = DATA_DIR / "competitor-log.json"
    existing = {}
    if log_path.exists():
        try:
            existing = json.loads(log_path.read_text())
        except Exception:
            pass

    existing["lastUpdated"] = TODAY
    existing["latestCrawl"] = findings
    log_path.write_text(json.dumps(existing, indent=2))
    log_change("Competitor log updated", "data/competitor-log.json")
    return findings


# ─── Daily content rotation ───────────────────────────────────────────────────
CONTENT_ROTATION = [
    "neighborhood_faq",
    "market_update",
    "competitor_gap",
    "buyer_seller_guide",
    "school_district",
    "relocation",
    "review_spotlight",
]

def get_rotation_day() -> str:
    """Return today's content rotation type based on day of year."""
    day_of_year = datetime.now().timetuple().tm_yday
    return CONTENT_ROTATION[day_of_year % len(CONTENT_ROTATION)]


def create_daily_content(market_data: dict | None):
    """
    Generate one piece of content based on the daily rotation.
    Uses Claude to write the HTML, then saves to blog/.
    """
    print("\n=== DAILY CONTENT: Creating rotation piece ===")
    rotation = get_rotation_day()
    print(f"  Rotation today: {rotation}")

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    # Determine what to write
    if rotation == "market_update":
        existing = list(BLOG_DIR.glob("austin-market-update-*.html"))
        if any(TODAY[:7] in str(f) for f in existing):
            print("  Market update for this month already exists. Skipping.")
            return None
        prompt_type = "market_update"
    elif rotation == "neighborhood_faq":
        # Find a neighborhood not yet covered in blog
        prompt_type = "neighborhood_faq"
    elif rotation == "relocation":
        prompt_type = "relocation"
    else:
        prompt_type = rotation

    market_context = ""
    if market_data:
        metro = market_data.get("austin_metro", {})
        market_context = f"""
Current Austin market data (as of {TODAY}):
- Metro median sold price: ${metro.get('medianSoldPrice', 'N/A'):,} {metro.get('medianSoldPriceYoYChange', '')}
- Months of inventory: {metro.get('monthsOfInventory', 'N/A')}
- Average days on market: {metro.get('avgDaysOnMarket', 'N/A')}
"""

    WRITING_RULES = """
WRITING RULES — follow exactly:
- No em dashes, en dashes, or hyphens used as sentence connectors
- No emojis anywhere
- No exclamation marks in body copy
- No AI-sounding phrases: no "straightforward", "genuinely", "honestly", "dive into", "leverage", "delve"
- Plain, simple, human language. Short sentences. Conversational tone.
- Never mention "Compass" in page copy or headings
- Phone always formatted as: 512.617.0001
- Brand name always: Grewal RE Group
- Agent name: Shivraj Grewal (goes by Raj)
"""

    HTML_TEMPLATE_INSTRUCTIONS = """
Output a complete HTML page following this exact structure:
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Title here — 50 to 60 chars] | Grewal RE Group</title>
  <meta name="description" content="[140 to 160 char description]">
  <link rel="canonical" href="https://grewalregroup.com/blog/[slug].html">
  <link rel="icon" href="../assets/favicon.png" type="image/png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    /* minimal inline styles matching brand: black #0a0a0a, gold #B8963E, cream #FAF7F2 */
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Inter', system-ui, sans-serif; color: #171717; background: #fff; line-height: 1.65; }
    h1,h2,h3,h4 { font-family: 'Cormorant Garamond', Georgia, serif; font-weight: 700; }
    .container { max-width: 780px; margin: 0 auto; padding: 0 1.5rem; }
    .article-hero { background: #0a0a0a; color: #fff; padding: 5rem 1.5rem 3rem; text-align: center; }
    .article-hero h1 { font-size: clamp(2rem, 5vw, 3rem); margin-bottom: 1rem; }
    .article-hero p { color: #aaa; max-width: 600px; margin: 0 auto; }
    .article-body { padding: 3rem 1.5rem; }
    .article-body h2 { font-size: 1.5rem; margin: 2.5rem 0 0.75rem; }
    .article-body h3 { font-size: 1.2rem; margin: 1.5rem 0 0.5rem; }
    .article-body p { margin-bottom: 1rem; }
    .article-body a { color: #B8963E; }
    .cta-block { background: #FAF7F2; border-left: 3px solid #B8963E; padding: 1.5rem 2rem; margin: 2.5rem 0; }
    .cta-block p { margin-bottom: 0.5rem; }
    .cta-block a { display: inline-block; margin-top: 0.75rem; padding: 0.65rem 1.5rem; background: #B8963E; color: #fff; text-decoration: none; font-size: 0.8rem; letter-spacing: 0.08em; text-transform: uppercase; }
    footer { background: #0a0a0a; color: #aaa; padding: 2rem 1.5rem; text-align: center; font-size: 0.8rem; margin-top: 4rem; }
    footer a { color: #B8963E; }
  </style>
</head>
<body>
  <nav style="background:#fff;border-bottom:1px solid #e8e3d8;padding:0.85rem 2.5rem;display:flex;align-items:center;justify-content:space-between;">
    <a href="../index.html"><img src="../assets/logos/logo-black.png" alt="Grewal RE Group" style="height:36px;"></a>
    <a href="../index.html#contact" style="padding:0.55rem 1.25rem;background:#B8963E;color:#fff;font-size:0.75rem;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;text-decoration:none;">Schedule a Call</a>
  </nav>

  <div class="article-hero">
    <h1>[H1 here]</h1>
    <p>[Deck / subtitle — one sentence]</p>
  </div>

  <div class="article-body container">
    [body content with h2s, paragraphs, the CTA block near the end]

    <div class="cta-block">
      <p>Ready to talk about [topic]?</p>
      <p>Raj has worked with buyers and sellers in [area] throughout 2026. A 20-minute call is usually enough to answer the most important questions.</p>
      <a href="../index.html#contact">Schedule a Call</a>
    </div>
  </div>

  <footer>
    <p>&copy; 2026 Grewal RE Group &middot; Shivraj Grewal &middot; TREC #736060 &middot;
    <a href="tel:+15126170001">512.617.0001</a> &middot;
    <a href="https://www.trec.texas.gov/sites/default/files/pdf-forms/IABS%201-0.pdf" target="_blank" rel="noopener">IABS</a> &middot;
    <a href="https://www.trec.texas.gov/forms/consumer-protection-notice" target="_blank" rel="noopener">TREC Consumer Protection</a></p>
  </footer>
</body>
</html>
"""

    if prompt_type == "market_update":
        user_prompt = f"""Write a complete HTML blog post: May {TODAY[:4]} Austin Luxury Market Update for Grewal RE Group.

{WRITING_RULES}
{market_context}

Filename: austin-market-update-{TODAY[:7]}.html
Title: May {TODAY[:4]} Austin Luxury Market Update | Grewal RE Group

Requirements:
- 600 to 800 words of body copy
- Use the market data above as specific citable figures
- Structure: intro, data snapshot, what it means for buyers, what it means for sellers, Raj's read, CTA
- Every factual claim needs a data source label (Austin Board of Realtors, Redfin, etc.)
- End with a clear next action for the reader

{HTML_TEMPLATE_INSTRUCTIONS}"""

    elif prompt_type == "relocation":
        # Pick a city not yet heavily covered
        user_prompt = f"""Write a complete HTML blog post about moving to Austin from Washington DC for Grewal RE Group.

{WRITING_RULES}

Filename: moving-to-austin-from-washington-dc-2026.html
Title: Moving to Austin from Washington DC in 2026 | Grewal RE Group

Requirements:
- 600 to 800 words of body copy
- Focus on: why DC professionals choose Austin, neighborhood comparison (Tarrytown/Westlake vs Georgetown/Capitol Hill feel), cost of living shift, commute trade, school districts
- Specific, citable comparisons — not vague
- Tone: helpful advisor, not a sales pitch
- End with a clear next action

{HTML_TEMPLATE_INSTRUCTIONS}"""

    else:
        # Default fallback: create a neighborhood FAQ for Rollingwood (Priority 1 missing page)
        user_prompt = f"""Write a complete HTML blog post: 10 Common Questions About Rollingwood TX Real Estate for Grewal RE Group.

{WRITING_RULES}

Filename: rollingwood-tx-faq-2026.html
Title: 10 Questions About Rollingwood TX Real Estate | Grewal RE Group

Requirements:
- 10 FAQ pairs in AEO format: H2 question, then a 40 to 60 word direct answer, then optional brief expansion
- Total 800+ words
- Rollingwood ZIP is 78746, Eanes ISD, city of Rollingwood (separate municipality from Austin)
- Specific: include home price ranges, school names, commute times, lot sizes
- Every factual claim is labeled as estimate or sourced

{HTML_TEMPLATE_INSTRUCTIONS}"""

    try:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=4096,
            messages=[{"role": "user", "content": user_prompt}]
        )
        html_content = response.content[0].text.strip()

        # Extract filename from content if present, otherwise derive it
        if prompt_type == "market_update":
            filename = f"austin-market-update-{TODAY[:7]}.html"
        elif prompt_type == "relocation":
            filename = "moving-to-austin-from-washington-dc-2026.html"
        else:
            filename = "rollingwood-tx-faq-2026.html"

        out_path = BLOG_DIR / filename
        if out_path.exists():
            print(f"  Content file already exists: {filename}. Skipping.")
            return None

        out_path.write_text(html_content)
        log_change(f"Daily content created: {filename}", f"blog/{filename}")
        return filename

    except Exception as e:
        log_error("Daily Content", "blog/", str(e))
        return None


# ─── PR description ────────────────────────────────────────────────────────────
def write_pr_description(market_data: dict | None, content_file: str | None):
    """Write /tmp/agent-pr-body.md for the GitHub PR."""
    lines = [
        f"## Daily AI Agent Run — {TODAY}",
        "",
        "### What Was Fixed",
    ]

    if changes_made:
        for c in changes_made:
            lines.append(f"- {c['description']}" + (f" — `{c['file']}`" if c.get("file") else ""))
    else:
        lines.append("- No fixes required on this run")

    lines += ["", "### Market Data Updated"]
    if market_data:
        metro = market_data.get("austin_metro", {})
        lines.append(f"- Austin metro median sold price: ${metro.get('medianSoldPrice', 'N/A'):,} {metro.get('medianSoldPriceYoYChange', '')}")
        lines.append(f"- Source: {market_data.get('source', 'see data/market-data/latest.json')}")
    else:
        lines.append("- Market data update failed. See logs/agent-errors.json")

    lines += ["", "### New Content Created"]
    if content_file:
        lines.append(f"- `blog/{content_file}`")
    else:
        lines.append("- No new content created on this run (already exists or generation failed)")

    lines += ["", "### Competitor Report"]
    lines.append("- See `data/competitor-log.json` for latest crawl results")

    lines += ["", "### Remaining Issues (not yet fixable)"]
    lines.append("- IDX: Awaiting MLS approval and Showcase IDX key from Raj")
    lines.append("- Missing Priority 1 community pages: Rollingwood, Davenport Ranch, Lost Creek")
    lines.append("- Large PDF (`the-relocation-edition.pdf`, 163MB) excluded from git — serve via Netlify manual upload")

    if errors:
        lines += ["", "### Errors Encountered"]
        for e in errors:
            lines.append(f"- [{e['step']}] `{e['target']}`: {e['error']}")

    lines += ["", "---", f"_Agent version {AGENT_VERSION} · Run {TODAY}_"]

    PR_BODY_PATH.write_text("\n".join(lines))
    print(f"\nPR description written to {PR_BODY_PATH}")


# ─── Error log flush ───────────────────────────────────────────────────────────
def flush_error_log():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / "agent-errors.json"
    payload = {
        "lastRun": datetime.utcnow().isoformat() + "Z",
        "errors": errors,
        "warnings": warnings
    }
    log_path.write_text(json.dumps(payload, indent=2))


# ─── Main ──────────────────────────────────────────────────────────────────────
def main():
    print(f"Grewal RE Group Daily Agent — {TODAY}")
    print("=" * 50)

    market_data = None
    content_file = None

    try:
        # Step 2: Competitor audit
        audit_competitors()
    except Exception:
        log_error("STEP 2", "competitor audit", traceback.format_exc())

    try:
        # Step 3: Market data
        market_data = update_market_data()
    except Exception:
        log_error("STEP 3", "market data", traceback.format_exc())

    try:
        # Daily content
        content_file = create_daily_content(market_data)
    except Exception:
        log_error("Daily Content", "blog generation", traceback.format_exc())

    # Write PR description and error log
    write_pr_description(market_data, content_file)
    flush_error_log()

    print("\n" + "=" * 50)
    print(f"Agent run complete. Changes: {len(changes_made)}. Errors: {len(errors)}.")

    # Exit 0 even if there were non-fatal errors so the workflow
    # can still commit whatever it managed to produce
    sys.exit(0)


if __name__ == "__main__":
    main()
