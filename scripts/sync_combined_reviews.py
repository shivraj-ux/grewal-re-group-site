#!/usr/bin/env python3
"""One-off: propagate the verified all-platform review total sitewide.

Google count itself is unchanged (119, re-verified live against the real
Google Business Profile). What changed is the "extra" — real, live-checked
counts from Zillow (3) and Realtor.com (1 testimonial) for Shivraj, plus
Arsh Khaira and Modernaire Group checked across Zillow, Realtor.com, HAR,
Yelp, and ProvenExpert (all verified at 0 reviews today, contributing
nothing to add yet). This mirrors sync_reviews.py's own
update_counts_everywhere() substitution patterns exactly — the "total"
patterns only, since old_google == new_google == 119 this run.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {'.git', 'archive', 'relocation-edition', 'schools-edition', 'node_modules', 'questions'}

OLD_TOTAL, NEW_TOTAL = 119, 123

# Same "all-platform total" substitution patterns as sync_reviews.py's
# update_counts_everywhere(), total-only (Google-specific "119 Google
# reviews" / "119 reviews on Google" style mentions are deliberately NOT
# touched -- those stay 119, accurately describing that one platform).
SUBS = [
    (f"{OLD_TOTAL} Five-Star", f"{NEW_TOTAL} Five-Star"),
    (f"{OLD_TOTAL} five-star", f"{NEW_TOTAL} five-star"),
    (f'data-value="{OLD_TOTAL}"', f'data-value="{NEW_TOTAL}"'),
    (f'"ratingCount": "{OLD_TOTAL}"', f'"ratingCount": "{NEW_TOTAL}"'),
    (f'"ratingCount":"{OLD_TOTAL}"', f'"ratingCount":"{NEW_TOTAL}"'),
    (f'class="ps-num">{OLD_TOTAL}<', f'class="ps-num">{NEW_TOTAL}<'),
    (f'>{OLD_TOTAL}</strong> Google', f'>{NEW_TOTAL}</strong> Google'),  # unqualified-total author cards
]

# Patterns that must NOT change -- Google-specific, still accurately 119.
PROTECT_MARKERS = ('Google review', 'reviews on Google', 'Google Reviews', 'data-review-count')


def process(path: Path) -> bool:
    text = path.read_text(encoding='utf-8', errors='ignore')
    original = text
    for a, b in SUBS:
        text = text.replace(a, b)
    if text != original:
        path.write_text(text, encoding='utf-8')
        return True
    return False


def main():
    changed = 0
    targets = list(ROOT.glob('*.html')) + list(ROOT.glob('blog/*.html')) + \
        list(ROOT.glob('communities/*.html')) + list(ROOT.glob('calculators/*.html')) + \
        [ROOT / 'llms.txt', ROOT / 'index.md', ROOT / 'AGENTS.md']
    for f in targets:
        if not f.exists():
            continue
        if set(f.relative_to(ROOT).parts) & SKIP_DIRS:
            continue
        if process(f):
            changed += 1
    print(f'Updated all-platform review total ({OLD_TOTAL} -> {NEW_TOTAL}) on {changed} files.')


if __name__ == '__main__':
    main()
