#!/usr/bin/env python3
"""Replace lingering 'Cormorant Garamond' / 'Inter' font-family string
references (in inline <style> blocks) with the real self-hosted brand
fonts, sitewide. Mechanical, font-name-only, no content touched."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {'.git', 'archive', 'relocation-edition', 'schools-edition', 'node_modules'}

REPLACEMENTS = [
    (re.compile(r"'Cormorant Garamond',\s*serif"), "'GRG Serif', serif"),
    (re.compile(r"'Cormorant Garamond',\s*Georgia,\s*serif"), "'GRG Serif', Georgia, serif"),
    (re.compile(r"'Cormorant Garamond'"), "'GRG Serif'"),
    (re.compile(r"'Inter',\s*sans-serif"), "'GRG Sans', sans-serif"),
    (re.compile(r"'Inter',\s*system-ui,\s*-apple-system,\s*sans-serif"), "'GRG Sans', system-ui, -apple-system, sans-serif"),
    (re.compile(r"'Inter'"), "'GRG Sans'"),
]


def process(path: Path) -> bool:
    html = path.read_text(encoding='utf-8')
    original = html
    for pattern, repl in REPLACEMENTS:
        html = pattern.sub(repl, html)
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
    print(f'Fixed lingering font-family references on {updated} pages.')


if __name__ == '__main__':
    main()
