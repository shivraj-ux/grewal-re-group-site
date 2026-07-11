#!/usr/bin/env python3
"""One-off: revert the all-platform review total sitewide (189 -> 149).

RateMyAgent was briefly added as a 5th source, then excluded after review:
a large share of its 40 reviews are the same clients' testimonials already
counted under the Grewal RE Group Google profile, cross-posted verbatim or
near-verbatim to both platforms (matching typos confirm same underlying
review in at least one case). See data/reviews.json ->
checked_no_additional_reviews.ratemyagent_excluded_2026-07-11 for the full
reasoning and the preserved dataset. This script reverses the 149 -> 189
propagation using the same conservative pattern list.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {'.git', 'archive', 'relocation-edition', 'schools-edition', 'node_modules', 'questions'}

OLD_TOTAL, NEW_TOTAL = 189, 149

SUBS = [
    (f"{OLD_TOTAL} Five-Star", f"{NEW_TOTAL} Five-Star"),
    (f"{OLD_TOTAL} five-star", f"{NEW_TOTAL} five-star"),
    (f'data-value="{OLD_TOTAL}"', f'data-value="{NEW_TOTAL}"'),
    (f'"ratingCount": "{OLD_TOTAL}"', f'"ratingCount": "{NEW_TOTAL}"'),
    (f'"ratingCount":"{OLD_TOTAL}"', f'"ratingCount":"{NEW_TOTAL}"'),
    (f'class="ps-num">{OLD_TOTAL}<', f'class="ps-num">{NEW_TOTAL}<'),
]

# Patterns that must NOT change -- platform-specific, still accurately their own number.
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
    print(f'Reverted all-platform review total ({OLD_TOTAL} -> {NEW_TOTAL}) on {changed} files.')


if __name__ == '__main__':
    main()
