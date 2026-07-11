#!/usr/bin/env python3
"""
Fix broken footer fragment links (/#services, /#about, /#resources) across all HTML files.
Replaces with proper page links: /buy, /about, /calculators, /blog, etc.
Idempotent: only modifies files that have the broken links.
"""

import os
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
ARCHIVE_DIR = REPO_ROOT / "archive"
SKIP_PATTERNS = [" 2"]

REPLACEMENTS = {
    r'href="/#services"': 'href="/buy"',
    r'href="/#about"': 'href="/about"',
    r'href="/#resources"': 'href="/calculators"',
}

def should_skip(file_path):
    """Check if file should be skipped."""
    if "archive" in file_path.parts:
        return True
    filename = file_path.name
    if any(pattern in filename for pattern in SKIP_PATTERNS):
        return True
    return False

def fix_footer(html_content):
    """Replace broken footer links. Return (new_content, changed)."""
    original = html_content
    for pattern, replacement in REPLACEMENTS.items():
        html_content = re.sub(pattern, replacement, html_content)

    return html_content, html_content != original

def main():
    html_files = list(REPO_ROOT.glob("**/*.html"))
    html_files = [f for f in html_files if not should_skip(f)]

    changed_count = 0
    skipped_count = 0

    for html_file in sorted(html_files):
        rel_path = html_file.relative_to(REPO_ROOT)

        with open(html_file, "r", encoding="utf-8") as f:
            original_content = f.read()

        updated_content, changed = fix_footer(original_content)

        if changed:
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(updated_content)
            print(f"  ✓ {rel_path}")
            changed_count += 1
        else:
            skipped_count += 1

    print(f"\n{'='*60}")
    print(f"Fixed: {changed_count} files")
    print(f"Skipped: {skipped_count} files (no broken links or already fixed)")
    print(f"Total HTML files processed: {len(html_files)}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
