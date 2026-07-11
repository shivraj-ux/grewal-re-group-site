#!/usr/bin/env python3
"""Fix the redesign CSS load order: site-chrome.css and system.css must
load BEFORE any page-specific inline <style> block, so a page's own
overrides (e.g. .org-node--admin's dark gradient) reliably win cascade
ties against system.css's generic component rules, instead of losing to
whichever happens to load later in source order."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {'.git', 'archive', 'relocation-edition', 'schools-edition', 'node_modules'}

LINK_BLOCK_RE = re.compile(
    r'[ \t]*<link rel="stylesheet" href="/assets/css/site-chrome\.css\?v=4">\s*\n'
    r'[ \t]*<link rel="stylesheet" href="/assets/css/system\.css\?v=1">\s*\n?'
)


def process(path: Path) -> bool:
    html = path.read_text(encoding='utf-8', errors='ignore')
    match = LINK_BLOCK_RE.search(html)
    if not match:
        return False
    style_idx = html.find('<style>')
    if style_idx == -1 or style_idx > match.start():
        return False  # already in correct order, or no inline style to worry about

    block = match.group(0)
    html_without_block = html[:match.start()] + html[match.end():]
    # style_idx shifts if the block we removed was before it
    new_style_idx = html_without_block.find('<style>')
    fixed = html_without_block[:new_style_idx] + block + html_without_block[new_style_idx:]
    path.write_text(fixed, encoding='utf-8')
    return True


def main():
    fixed = 0
    for path in ROOT.rglob('*.html'):
        if set(path.relative_to(ROOT).parts) & SKIP_DIRS:
            continue
        if process(path):
            fixed += 1
    print(f'Reordered CSS links (before inline <style>) on {fixed} pages.')


if __name__ == '__main__':
    main()
