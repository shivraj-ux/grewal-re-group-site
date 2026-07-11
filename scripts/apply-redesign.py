#!/usr/bin/env python3
"""Batch-inject the redesign system (system.css + motion.js) into every real
page and swap Google Fonts for the self-hosted brand fonts. Mechanical only:
never touches page text, schema, forms, or links."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {'.git', 'archive', 'relocation-edition', 'schools-edition', 'node_modules'}

SYSTEM_CSS_TAG = '<link rel="stylesheet" href="/assets/css/system.css?v=1">'
MOTION_JS_TAG = '<script defer src="/assets/js/motion.js?v=1"></script>'

GOOGLE_FONT_RE = re.compile(
    r'<link[^>]*fonts\.googleapis\.com[^>]*>\s*'
)
PRECONNECT_RE = re.compile(
    r'<link rel="preconnect" href="https://fonts\.(googleapis|gstatic)\.com"[^>]*>\s*'
)


def process(path: Path) -> bool:
    html = path.read_text(encoding='utf-8')
    original = html
    changed = False

    if 'system.css' not in html:
        if 'site-chrome.css?v=4' in html:
            html = html.replace(
                '<link rel="stylesheet" href="/assets/css/site-chrome.css?v=4">',
                '<link rel="stylesheet" href="/assets/css/site-chrome.css?v=4">\n  ' + SYSTEM_CSS_TAG,
                1,
            )
            changed = True
        elif '</head>' in html:
            html = html.replace('</head>', '  ' + SYSTEM_CSS_TAG + '\n</head>', 1)
            changed = True

    if 'motion.js' not in html:
        if 'site-chrome.js?v=4' in html:
            html = html.replace(
                '<script defer src="/assets/js/site-chrome.js?v=4"></script>',
                '<script defer src="/assets/js/site-chrome.js?v=4"></script>\n<script defer src="/assets/js/motion.js?v=1"></script>',
                1,
            )
            changed = True
        elif '</body>' in html:
            html = html.replace('</body>', MOTION_JS_TAG + '\n</body>', 1)
            changed = True

    # Remove Google Fonts (Inter/Cormorant) — real brand fonts are self-hosted now.
    if 'fonts.googleapis.com' in html:
        html = GOOGLE_FONT_RE.sub('', html)
        html = PRECONNECT_RE.sub('', html)
        changed = True

    if changed and html != original:
        path.write_text(html, encoding='utf-8')
        return True
    return False


def main():
    updated = 0
    for path in ROOT.rglob('*.html'):
        rel_parts = set(path.relative_to(ROOT).parts)
        if rel_parts & SKIP_DIRS:
            continue
        if process(path):
            updated += 1
    print(f'Updated {updated} pages with system.css + motion.js includes.')


if __name__ == '__main__':
    main()
