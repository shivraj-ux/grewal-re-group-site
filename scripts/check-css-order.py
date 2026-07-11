#!/usr/bin/env python3
"""Diagnostic: find pages where system.css loads AFTER a page-specific
inline <style> block, which lets system.css's generic component rules
silently win cascade ties against the page's own overrides."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {'.git', 'archive', 'relocation-edition', 'schools-edition', 'node_modules'}

affected = []
for path in ROOT.rglob('*.html'):
    if set(path.relative_to(ROOT).parts) & SKIP_DIRS:
        continue
    html = path.read_text(encoding='utf-8', errors='ignore')
    sys_idx = html.find('system.css')
    style_idx = html.find('<style>')
    if sys_idx == -1 or style_idx == -1:
        continue
    if style_idx < sys_idx:
        affected.append(str(path.relative_to(ROOT)))

print(f'{len(affected)} pages have an inline <style> block before system.css loads:')
for p in affected[:30]:
    print(' ', p)
if len(affected) > 30:
    print(f'  ...and {len(affected) - 30} more')
