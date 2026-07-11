#!/usr/bin/env python3
"""
Propagate the canonical <nav> block from index.html to all .html files in the repo.
Skips archive/ and files containing " 2" in the filename.
Idempotent: compares before/after to report changed/skipped files.
"""

import os
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
CANONICAL_FILE = REPO_ROOT / "index.html"
ARCHIVE_DIR = REPO_ROOT / "archive"
SKIP_PATTERNS = [" 2"]

def extract_nav(html_content):
    """Extract the <nav> block from HTML content."""
    match = re.search(
        r'(<nav\s+class="gh-nav"[^>]*>.*?</nav>)',
        html_content,
        re.DOTALL
    )
    return match.group(1) if match else None

def replace_nav(html_content, new_nav):
    """Replace the <nav> block in HTML content. Return (new_content, changed)."""
    pattern = r'<nav\s+class="gh-nav"[^>]*>.*?</nav>'
    old_nav_match = re.search(pattern, html_content, re.DOTALL)

    if not old_nav_match:
        return html_content, False

    old_nav = old_nav_match.group(0)
    if old_nav == new_nav:
        return html_content, False

    updated = html_content[:old_nav_match.start()] + new_nav + html_content[old_nav_match.end():]
    return updated, True

def should_skip(file_path):
    """Check if file should be skipped."""
    if "archive" in file_path.parts:
        return True
    filename = file_path.name
    if any(pattern in filename for pattern in SKIP_PATTERNS):
        return True
    return False

def main():
    # Extract canonical nav from index.html
    with open(CANONICAL_FILE, "r", encoding="utf-8") as f:
        canonical_html = f.read()

    canonical_nav = extract_nav(canonical_html)
    if not canonical_nav:
        print(f"ERROR: Could not extract nav from {CANONICAL_FILE}")
        return

    print(f"Canonical nav block ({len(canonical_nav)} chars) extracted from {CANONICAL_FILE.name}")
    print(f"Propagating to all .html files...\n")

    # Collect all .html files
    html_files = list(REPO_ROOT.glob("**/*.html"))
    html_files = [f for f in html_files if not should_skip(f)]

    changed_count = 0
    skipped_count = 0

    for html_file in sorted(html_files):
        rel_path = html_file.relative_to(REPO_ROOT)

        with open(html_file, "r", encoding="utf-8") as f:
            original_content = f.read()

        updated_content, changed = replace_nav(original_content, canonical_nav)

        if changed:
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(updated_content)
            print(f"  ✓ {rel_path}")
            changed_count += 1
        else:
            skipped_count += 1

    print(f"\n{'='*60}")
    print(f"Changed: {changed_count} files")
    print(f"Skipped: {skipped_count} files (no nav or already current)")
    print(f"Total HTML files processed: {len(html_files)}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
