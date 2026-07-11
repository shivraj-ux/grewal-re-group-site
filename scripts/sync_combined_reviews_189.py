#!/usr/bin/env python3
"""One-off: propagate the verified all-platform review total sitewide (149 -> 189).

Google counts themselves are unchanged (119 Grewal RE Group, 26 Modernaire
Group). What's new is RateMyAgent: 40 real, verified, claimed-profile
reviews for Shivraj Grewal, confirmed additive (zero overlap with Google/
Zillow/Realtor.com). Mirrors sync_reviews.py's own update_counts_everywhere()
substitution patterns -- the "total" patterns only, since the Google-specific
counts are unchanged this run. Uses the conservative pattern list from the
123->149 round (excludes the risky '>{OLD}</strong> Google' pattern that
caused a misattribution bug in the 119->123 round).
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {'.git', 'archive', 'relocation-edition', 'schools-edition', 'node_modules', 'questions'}

OLD_TOTAL, NEW_TOTAL = 149, 189

SUBS = [
    (f"{OLD_TOTAL} Five-Star", f"{NEW_TOTAL} Five-Star"),
    (f"{OLD_TOTAL} five-star", f"{NEW_TOTAL} five-star"),
    (f'data-value="{OLD_TOTAL}"', f'data-value="{NEW_TOTAL}"'),
    (f'"ratingCount": "{OLD_TOTAL}"', f'"ratingCount": "{NEW_TOTAL}"'),
    (f'"ratingCount":"{OLD_TOTAL}"', f'"ratingCount":"{NEW_TOTAL}"'),
    (f'class="ps-num">{OLD_TOTAL}<', f'class="ps-num">{NEW_TOTAL}<'),
]

# Patterns that must NOT change -- platform-specific, still accurately their own number.
PROTECT_MARKERS = ('Google review', 'reviews on Google', 'Google Reviews', 'data-review-count',
                    'on RateMyAgent')


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
