#!/usr/bin/env python3
"""
Generate sitemap-images.xml (Google Image sitemap extension) from the actual
HTML on disk. Scans every published HTML page for same-site <img> tags and
og:image tags, maps the file path to its clean canonical URL, and writes one
<url> block per page that has at least one qualifying image.

Only images hosted on grewalregroup.com (local /assets/... paths or absolute
https://grewalregroup.com/... URLs) are included. Third-party hotlinked photos
(e.g. Unsplash) are excluded on purpose: an image sitemap asserts images this
site owns/hosts, and we don't hold rights to submit someone else's CDN URL to
Google Images under our domain.

Run: python3 scripts/generate-image-sitemap.py
Writes: sitemap-images.xml at repo root.
"""
import os
import re
import html as htmlmod
from urllib.parse import urljoin

SITE = "https://grewalregroup.com"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Directories that are never published / never contain content pages.
SKIP_DIRS = {
    "node_modules", ".git", "archive", "netlify", "scripts", "logs",
    "data", ".well-known", ".claude", "assets",
}
# Specific files that are internal or non-content and must not appear in the
# image sitemap (scaffolding, redirects targets already excluded via SKIP_DIRS).
SKIP_FILES = {"_TEMPLATE_ENHANCED.html", "thank-you.html", "404.html"}

IMG_SRC_RE = re.compile(r'<img\b[^>]*\bsrc=["\']([^"\']+)["\'][^>]*>', re.IGNORECASE)
ALT_RE = re.compile(r'\balt=["\']([^"\']*)["\']', re.IGNORECASE)
OG_IMAGE_RE = re.compile(r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)["\']', re.IGNORECASE)
TITLE_RE = re.compile(r'<title>([^<]*)</title>', re.IGNORECASE)


def file_to_url(path):
    """Map a repo-relative HTML file path to its clean canonical site URL."""
    rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
    if rel == "index.html":
        return SITE + "/"
    if rel.endswith("/index.html"):
        return f"{SITE}/{rel[:-len('index.html')]}"
    if rel.endswith(".html"):
        return f"{SITE}/{rel[:-len('.html')]}"
    return f"{SITE}/{rel}"


def is_local_image(src):
    if src.startswith("https://grewalregroup.com/"):
        return True
    if src.startswith("/"):
        return True
    return False


def normalize_local(src, page_rel_dir):
    if src.startswith("https://grewalregroup.com/"):
        return src
    if src.startswith("/"):
        return SITE + src
    # relative path (e.g. ../assets/x.jpg) resolved against the page's directory
    return urljoin(SITE + "/" + page_rel_dir + "/", src)


def collect_html_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        rel_dir = os.path.relpath(dirpath, ROOT)
        if rel_dir == ".":
            rel_dir = ""
        # skip anything under a SKIP_DIRS path even if nested deeper
        parts = set(rel_dir.split("/")) if rel_dir else set()
        if parts & SKIP_DIRS:
            continue
        for f in filenames:
            if f.endswith(".html") and f not in SKIP_FILES:
                yield os.path.join(dirpath, f)


def escape(s):
    return htmlmod.escape(s or "", quote=False)


def main():
    entries = []  # (page_url, [(img_url, caption), ...])
    total_images = 0
    for path in sorted(collect_html_files()):
        with open(path, encoding="utf-8") as fh:
            content = fh.read()

        rel_dir = os.path.dirname(os.path.relpath(path, ROOT)).replace(os.sep, "/")
        page_url = file_to_url(path)

        seen = {}  # dedupe per page, preserve order
        for m in IMG_SRC_RE.finditer(content):
            src = m.group(1).strip()
            if not is_local_image(src):
                continue
            full_tag = m.group(0)
            alt_m = ALT_RE.search(full_tag)
            alt = htmlmod.unescape(alt_m.group(1)).strip() if alt_m else ""
            img_url = normalize_local(src, rel_dir).split("?")[0]
            if img_url not in seen:
                seen[img_url] = alt

        for m in OG_IMAGE_RE.finditer(content):
            src = m.group(1).strip()
            if not is_local_image(src):
                continue
            img_url = normalize_local(src, rel_dir).split("?")[0]
            if img_url not in seen:
                title_m = TITLE_RE.search(content)
                caption = htmlmod.unescape(title_m.group(1)).strip() if title_m else ""
                seen[img_url] = caption

        if seen:
            entries.append((page_url, list(seen.items())))
            total_images += len(seen)

    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"')
    lines.append('        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">')
    for page_url, images in entries:
        lines.append("  <url>")
        lines.append(f"    <loc>{escape(page_url)}</loc>")
        for img_url, caption in images:
            lines.append("    <image:image>")
            lines.append(f"      <image:loc>{escape(img_url)}</image:loc>")
            if caption:
                lines.append(f"      <image:caption>{escape(caption)}</image:caption>")
            lines.append("    </image:image>")
        lines.append("  </url>")
    lines.append("</urlset>")

    out_path = os.path.join(ROOT, "sitemap-images.xml")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    print(f"Pages with images: {len(entries)}")
    print(f"Total <image:image> entries: {total_images}")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
