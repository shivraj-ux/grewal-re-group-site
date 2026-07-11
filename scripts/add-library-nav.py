#!/usr/bin/env python3
"""Add 'The Library' to the Resources dropdown and Guides footer group,
sitewide. Mechanical, additive-only — no other text changes."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {'.git', 'archive', 'relocation-edition', 'schools-edition', 'node_modules'}

NAV_OLD = '<li><a href="/blog/">Blog</a></li>'
NAV_NEW = '<li><a href="/library">The Library</a></li>\n            <li><a href="/blog/">Blog</a></li>'

FOOT_OLD = '<li><a href="/relocation-guide">Relocation Guide</a></li>\n          <li><a href="/austin-schools-guide">Schools Guide</a></li>'
FOOT_NEW = '<li><a href="/library">The Library</a></li>\n          <li><a href="/relocation-guide">Relocation Guide</a></li>\n          <li><a href="/austin-schools-guide">Schools Guide</a></li>'


def process(path: Path) -> bool:
    html = path.read_text(encoding='utf-8')
    original = html
    if 'href="/library"' not in html:
        if NAV_OLD in html:
            html = html.replace(NAV_OLD, NAV_NEW, 1)
        if FOOT_OLD in html:
            html = html.replace(FOOT_OLD, FOOT_NEW, 1)
    if html != original:
        path.write_text(html, encoding='utf-8')
        return True
    return False


def main():
    updated = 0
    for path in ROOT.rglob('*.html'):
        if set(path.relative_to(ROOT).parts) & SKIP_DIRS:
            continue
        if process(path):
            updated += 1
    print(f'Added Library nav link to {updated} pages.')


if __name__ == '__main__':
    main()
