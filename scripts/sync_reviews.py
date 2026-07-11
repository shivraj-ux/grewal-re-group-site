#!/usr/bin/env python3
"""
Grewal RE Group — Live Google Review Sync
===========================================
Keeps the website's Google review count and featured testimonials in sync with
the live Google Business Profile, with ZERO hand-editing.

Runs in GitHub Actions (.github/workflows/review-sync.yml) a few times a day.
When the count or the featured reviews change, it rewrites the site files and
the workflow commits + pushes — which auto-deploys via Netlify.

Data backends (first one that has credentials wins):
  1. Google Places API  — set GOOGLE_PLACES_API_KEY (+ optional GOOGLE_PLACE_ID).
                           Sanctioned, returns rating, user_ratings_total, 5 reviews.
  2. Firecrawl scrape    — set FIRECRAWL_API_KEY. Scrapes the public profile.
                           (Proven to return the real count + top reviews.)

Optional notification:
  NOTION_TOKEN + NOTION_NOTIFY_PARENT  -> appends a "New Google review" note in Notion
  when the review count increases.

Nothing here invents data. If neither backend has a key, it exits 0 without changes.
"""

import json
import os
import re
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
REVIEWS_JSON = ROOT / "data" / "reviews.json"
INDEX_HTML = ROOT / "index.html"
LLMS_TXT = ROOT / "llms.txt"

PROFILE_URL = "https://share.google/1pYwueIVdeVLAtANo"
PLACE_FID = "0x865b2d8559b35f0f:0xceb6e8b660270652"

# Author display names we never want to surface verbatim (bare initials / spam-looking).
# We still COUNT them; we just prefer fuller names for the on-site carousel.
MIN_FEATURED = 3
MAX_FEATURED = 6


# ─────────────────────────────────────────────────────────────────────────────
# Backends
# ─────────────────────────────────────────────────────────────────────────────
def fetch_via_places():
    key = os.environ.get("GOOGLE_PLACES_API_KEY")
    if not key:
        return None
    place_id = os.environ.get("GOOGLE_PLACE_ID")
    if not place_id:
        # Resolve place_id once from the business name + locality.
        r = requests.get(
            "https://maps.googleapis.com/maps/api/place/findplacefromtext/json",
            params={
                "input": "Grewal RE Group, 2500 Bee Caves Rd, Austin TX",
                "inputtype": "textquery",
                "fields": "place_id",
                "key": key,
            },
            timeout=30,
        )
        cands = r.json().get("candidates") or []
        if not cands:
            print("Places: could not resolve place_id", file=sys.stderr)
            return None
        place_id = cands[0]["place_id"]
        print(f"Places: resolved place_id={place_id} (set GOOGLE_PLACE_ID to cache it)")

    r = requests.get(
        "https://maps.googleapis.com/maps/api/place/details/json",
        params={
            "place_id": place_id,
            "fields": "rating,user_ratings_total,reviews",
            "reviews_sort": "newest",
            "key": key,
        },
        timeout=30,
    )
    res = r.json().get("result") or {}
    if "user_ratings_total" not in res:
        return None
    reviews = []
    for rev in res.get("reviews", []):
        text = (rev.get("text") or "").strip()
        if not text:
            continue
        reviews.append({
            "author": rev.get("author_name", "Google reviewer"),
            "when": rev.get("relative_time_description", "Google review"),
            "location": "",
            "text": text,
            "rating": rev.get("rating", 5),
        })
    return {
        "rating": str(res.get("rating", "5.0")),
        "count": int(res["user_ratings_total"]),
        "reviews": reviews,
    }


def fetch_via_firecrawl():
    key = os.environ.get("FIRECRAWL_API_KEY")
    if not key:
        return None
    r = requests.post(
        "https://api.firecrawl.dev/v2/scrape",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={"url": PROFILE_URL, "formats": ["markdown"], "onlyMainContent": True, "waitFor": 6000},
        timeout=90,
    )
    md = (r.json().get("data") or {}).get("markdown", "")
    if not md:
        return None

    m = re.search(r"(\d\.\d)\s*\[?\s*(\d{1,5})\s+Google reviews", md)
    if not m:
        m2 = re.search(r"(\d{1,5})\s+Google reviews", md)
        if not m2:
            return None
        rating, count = "5.0", int(m2.group(1))
    else:
        rating, count = m.group(1), int(m.group(2))

    # Featured snippets: contributor link followed by a quoted snippet.
    reviews = []
    for am in re.finditer(
        r"\[!\[([^\]]+)\]\([^)]*\)\]\([^)]*contrib[^)]*\)\s*\n+\s*\[\"([^\"]+)\"\]",
        md,
    ):
        author = am.group(1).strip()
        text = am.group(2).strip()
        if author and text:
            reviews.append({"author": author, "when": "Google review",
                            "location": "", "text": text, "rating": 5})
    return {"rating": rating, "count": count, "reviews": reviews}


# ─────────────────────────────────────────────────────────────────────────────
# Writers
# ─────────────────────────────────────────────────────────────────────────────
def tidy_author(name: str) -> str:
    """'Z A' -> 'Z. A.' so initials read as initials, not a typo."""
    parts = name.split()
    if len(parts) <= 3 and all(len(p) == 1 for p in parts):
        return ". ".join(parts) + "."
    return name


def other_platform_count(current: dict) -> int:
    """Reviews we display from platforms other than the primary Grewal RE Group
    Google profile (Zillow, Realtor.com, the second Modernaire Group Google
    profile, RateMyAgent).

    Hand-maintained in reviews.json -> other_platforms / modernaire_group_google /
    ratemyagent_grewal. The site shows the all-platform total (primary Google +
    these) in the hero/proof stats and schema, so the total must move together
    with the primary Google count on every sync.
    """
    other = current.get("other_platforms", {}) or {}
    n = 0
    n += int((other.get("zillow") or {}).get("review_count") or 0)
    n += len((other.get("realtor_com") or {}).get("testimonials") or [])
    n += int((current.get("modernaire_group_google") or {}).get("review_count") or 0)
    n += int((current.get("ratemyagent_grewal") or {}).get("review_count") or 0)
    return n


def update_counts_everywhere(old: int, new: int, extra: int = 0):
    if old == new:
        return 0
    changed = 0
    targets = list(ROOT.glob("*.html")) + list(ROOT.glob("blog/*.html")) + \
        list(ROOT.glob("communities/*.html")) + \
        [LLMS_TXT, ROOT / "index.md", ROOT / "AGENTS.md"]  # served markdown mirrors
    old_total, new_total = old + extra, new + extra
    subs = [
        (f"{old} Google", f"{new} Google"),
        (f"{old} reviews", f"{new} reviews"),
        (f"{old} Reviews", f"{new} Reviews"),
        (f"{old} five-star", f"{new} five-star"),
        (f'data-review-count="{old}"', f'data-review-count="{new}"'),
        # Blog author-bio cards wrap the number in its own tag, e.g.
        # <strong>119</strong> Google Reviews / <span>119</span> Google Reviews
        (f'>{old}</strong> Google', f'>{new}</strong> Google'),
        (f'>{old}</span> Google', f'>{new}</span> Google'),
        (f'>{old} ★ 5.0<', f'>{new} ★ 5.0<'),
        # All-platform totals (hero/proof stats, FAQ schema, aggregateRating)
        (f"{old_total} Five-Star", f"{new_total} Five-Star"),
        (f"{old_total} five-star", f"{new_total} five-star"),
        (f'data-value="{old_total}"', f'data-value="{new_total}"'),
        (f'"ratingCount": "{old_total}"', f'"ratingCount": "{new_total}"'),
        # Proof-strip badge: bare number in its own span (index.html)
        (f'class="ps-num">{old_total}<', f'class="ps-num">{new_total}<'),
        # Legacy Google-count forms of the same attributes, in case a page
        # still carries the platform-specific number.
        (f'data-value="{old}"', f'data-value="{new}"'),
        (f'"ratingCount": "{old}"', f'"ratingCount": "{new}"'),
    ]
    for f in targets:
        if not f.exists():
            continue
        txt = f.read_text(encoding="utf-8")
        new_txt = txt
        for a, b in subs:
            new_txt = new_txt.replace(a, b)
        if new_txt != txt:
            f.write_text(new_txt, encoding="utf-8")
            changed += 1
    return changed


def update_index_reviews(featured):
    if len(featured) < MIN_FEATURED:
        return False
    block_items = []
    for r in featured[:MAX_FEATURED]:
        text = r["text"].replace('"', '\\"')
        block_items.append(
            f"    {{ author: '{r['author']}', when: '{r['when']}', location: '{r['location']}',\n"
            f"      text: \"{text}\" }}"
        )
    block = ("  const REVIEWS = [\n" + ",\n".join(block_items) + "\n  ];")
    html = INDEX_HTML.read_text(encoding="utf-8")
    new_html, n = re.subn(
        r"  const REVIEWS = \[.*?\n  \];",
        block,
        html,
        count=1,
        flags=re.DOTALL,
    )
    if n:
        INDEX_HTML.write_text(new_html, encoding="utf-8")
    return bool(n)


def notify_notion(old_count, new_count, top_review):
    token = os.environ.get("NOTION_TOKEN")
    parent = os.environ.get("NOTION_NOTIFY_PARENT")
    if not (token and parent and new_count > old_count):
        return
    try:
        requests.post(
            "https://api.notion.com/v1/pages",
            headers={
                "Authorization": f"Bearer {token}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json",
            },
            json={
                "parent": {"page_id": parent},
                "properties": {"title": {"title": [{"text": {
                    "content": f"⭐ New Google review — now {new_count} (was {old_count})"}}]}},
                "children": [{"object": "block", "type": "paragraph", "paragraph": {
                    "rich_text": [{"text": {"content":
                        f'"{top_review.get("text", "")}" — {top_review.get("author", "")}'}}]}}],
            },
            timeout=30,
        )
        print("Notion: notified.")
    except Exception as e:  # noqa: BLE001
        print(f"Notion notify failed (non-fatal): {e}", file=sys.stderr)


# ─────────────────────────────────────────────────────────────────────────────
def main():
    data = fetch_via_places() or fetch_via_firecrawl()
    current = json.loads(REVIEWS_JSON.read_text(encoding="utf-8"))
    old_count = int(current.get("review_count", 0))

    if not data:
        print("No backend credentials (GOOGLE_PLACES_API_KEY or FIRECRAWL_API_KEY). "
              "No changes made.")
        return 0

    new_count = data["count"]
    featured = [
        {**r, "author": tidy_author(r["author"])}
        for r in data["reviews"] if r.get("text")
    ][:MAX_FEATURED]

    # Persist machine-readable mirror.
    current["rating"] = data["rating"]
    current["review_count"] = new_count
    current["last_synced"] = os.environ.get("SYNC_DATE", current.get("last_synced", ""))
    current["last_sync_status"] = "ok"
    if len(featured) >= MIN_FEATURED:
        current["featured"] = [
            {k: r[k] for k in ("author", "when", "location", "text")} for r in featured
        ]
    REVIEWS_JSON.write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")

    changed_files = update_counts_everywhere(old_count, new_count,
                                             extra=other_platform_count(current))
    updated_reviews = update_index_reviews(current["featured"])

    if new_count > old_count and current["featured"]:
        notify_notion(old_count, new_count, current["featured"][0])

    print(f"Sync complete. count {old_count} -> {new_count} "
          f"({changed_files} files), reviews updated: {updated_reviews}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
