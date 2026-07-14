#!/usr/bin/env python3
"""
Phase 2 structured-data gap fill, sitewide.

1. Add the Compass agent-bio URL (a real, already-cited profile:
   https://www.compass.com/agents/shivraj-grewal/) to every existing
   "sameAs" array that already carries the canonical Grewal RE Group
   profile list (identified by the Alignable URL, which only appears in
   that one canonical list) -- homepage + community pages.

2. For every blog post: add a "sameAs" array to the BlogPosting author
   Person object if it doesn't already have one, using the same personal
   profile set as the homepage Person schema (LinkedIn, Zillow, realtor.com,
   Compass bio).

3. Inject a lightweight, consistent RealEstateAgent JSON-LD block (identical
   NAP to the homepage, referenced by @id so it reads as one entity) into
   every public page that doesn't already carry Organization/RealEstateAgent
   schema: all blog posts, and the standalone top-level pages.

Idempotent: every insertion is guarded by a check for existing content, so
re-running is a no-op on already-patched files.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

COMPASS_BIO = "https://www.compass.com/agents/shivraj-grewal/"

PERSON_SAMEAS = [
    "https://www.linkedin.com/company/grewal-re-group/",
    "https://www.instagram.com/grewalregroup/",
    "https://x.com/ShivrajGrewal1",
    "https://www.zillow.com/profile/Shivraj%20Grewal",
    "https://www.realtor.com/realestateagents/62691e42baa428baf4d88cda",
    COMPASS_BIO,
]

ORG_SCHEMA_TEMPLATE = """  <script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "RealEstateAgent",
  "@id": "https://grewalregroup.com/#realestateagent",
  "name": "Grewal RE Group",
  "image": "https://grewalregroup.com/assets/logos/logo-black.png?v=2",
  "url": "https://grewalregroup.com",
  "telephone": "(512) 617-0001",
  "email": "shivraj.grewal@compass.com",
  "address": {{
    "@type": "PostalAddress",
    "streetAddress": "2500 Bee Cave Rd, Building 3, Suite 200",
    "addressLocality": "Austin",
    "addressRegion": "TX",
    "postalCode": "78746",
    "addressCountry": "US"
  }},
  "geo": {{ "@type": "GeoCoordinates", "latitude": 30.3327, "longitude": -97.8160 }},
  "priceRange": "$$$",
  "parentOrganization": {{ "@type": "RealEstateAgent", "name": "Compass RE Texas, LLC" }},
  "sameAs": {sameas_json}
}}
  </script>
</head>"""

import json


def load(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def save(path, content):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def add_compass_bio_to_canonical_lists():
    """Step 1: append the Compass bio to every sameAs array that already
    contains the Alignable URL (the fingerprint of the canonical list)."""
    changed_files = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in
                       {"node_modules", ".git", "archive", "netlify", ".claude"}
                       and not d.startswith(".")]
        for f in filenames:
            if not f.endswith(".html"):
                continue
            path = os.path.join(dirpath, f)
            content = load(path)
            if "alignable.com/rollingwood-tx/grewal-re-group" not in content:
                continue
            if COMPASS_BIO in content:
                continue
            new_content = content.replace(
                '"https://www.alignable.com/rollingwood-tx/grewal-re-group",',
                f'"https://www.alignable.com/rollingwood-tx/grewal-re-group",\n    "{COMPASS_BIO}",',
                1,
            )
            if new_content != content:
                save(path, new_content)
                changed_files.append(path)
    return changed_files


AUTHOR_PERSON_RE = re.compile(
    r'("author"\s*:\s*\{\s*"@type"\s*:\s*"Person"[^}]*?)(\})',
    re.DOTALL,
)


def add_sameas_to_blog_authors():
    blog_dir = os.path.join(ROOT, "blog")
    changed = []
    sameas_json = json.dumps(PERSON_SAMEAS)
    for f in sorted(os.listdir(blog_dir)):
        if not f.endswith(".html") or f.startswith("_TEMPLATE"):
            continue
        path = os.path.join(blog_dir, f)
        content = load(path)

        def repl(m):
            body, close = m.group(1), m.group(2)
            if "sameAs" in body:
                return m.group(0)
            return f'{body},"sameAs":{sameas_json}{close}'

        new_content, n = AUTHOR_PERSON_RE.subn(repl, content)
        if n > 0 and new_content != content:
            save(path, new_content)
            changed.append(path)
    return changed


def has_org_schema(content):
    # Only a standalone RealEstateAgent entity satisfies "sitewide Organization
    # schema" here. A "publisher":{"@type":"Organization",...} stub nested
    # inside a BlogPosting graph is NOT enough -- it carries no NAP (address/
    # phone), so every blog post still needs the real block injected.
    return '"@type": "RealEstateAgent"' in content or '"@type":"RealEstateAgent"' in content


def inject_org_schema_everywhere():
    """Step 3: inject the compact RealEstateAgent block before </head> on
    every public page that doesn't already carry Organization/RealEstateAgent
    schema."""
    sameas_json = json.dumps(PERSON_SAMEAS[:-1] + [COMPASS_BIO], indent=4).replace("\n", "\n  ")
    block = ORG_SCHEMA_TEMPLATE.format(sameas_json=sameas_json)

    targets = []
    blog_dir = os.path.join(ROOT, "blog")
    for f in sorted(os.listdir(blog_dir)):
        if f.endswith(".html") and not f.startswith("_TEMPLATE"):
            targets.append(os.path.join(blog_dir, f))

    top_level = [
        "buy.html", "sell.html", "about.html", "contact.html", "faq.html",
        "reviews.html", "relocation-guide.html", "austin-schools-guide.html",
        "search.html", "terms.html", "privacy.html",
    ]
    for f in top_level:
        p = os.path.join(ROOT, f)
        if os.path.exists(p):
            targets.append(p)

    for sub in ("calculators", "questions"):
        d = os.path.join(ROOT, sub)
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                if f.endswith(".html"):
                    targets.append(os.path.join(d, f))

    changed = []
    for path in targets:
        content = load(path)
        if has_org_schema(content):
            continue
        if "</head>" not in content:
            continue
        new_content = content.replace("</head>", block, 1)
        save(path, new_content)
        changed.append(path)
    return changed


def main():
    step1 = add_compass_bio_to_canonical_lists()
    print(f"Step 1 - Compass bio added to canonical sameAs lists: {len(step1)} files")

    step2 = add_sameas_to_blog_authors()
    print(f"Step 2 - sameAs added to blog author Person objects: {len(step2)} files")

    step3 = inject_org_schema_everywhere()
    print(f"Step 3 - RealEstateAgent schema injected sitewide: {len(step3)} files")


if __name__ == "__main__":
    main()
