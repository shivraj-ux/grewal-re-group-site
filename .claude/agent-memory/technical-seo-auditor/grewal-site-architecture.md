---
name: grewal-site-architecture
description: Where key SEO files live and how the Grewal RE Group site builds/deploys
metadata:
  type: reference
---

Repo: `/Users/shivrajsinghgrewal/Desktop/grewal-site-work` (branch `main`). Static HTML on Netlify, git-connected: push to `main` auto-deploys. Live: https://grewalregroup.com (also grewal-re-group-site.netlify.app).

Key paths:
- `blog/` — 379 article HTML files (plus `_TEMPLATE_ENHANCED.html`, `blog.css`, `blog-enhanced.css`). Posts carry BlogPosting + FAQPage + Person + Place + Organization JSON-LD; NO BreadcrumbList.
- `communities/` — 25 community landing pages (slug.html).
- `data/communities.json`, `data/site-audit.json`, `data/competitor-log.json`, `data/market-data/`.
- `sitemap.xml` — 413 `<loc>` entries; 10 are homepage `#fragment` anchors (noise).
- `_redirects` — Netlify 301 file, currently empty (comment header only). Format: `/blog/old.html  /blog/new.html  301`.
- `netlify.toml`, `robots.txt`, `llms.txt`, `AGENTS.md`, `index.md`, `openapi.json`, `.well-known/`.

Internal-link href conventions inside a blog post (relative to /blog/): sibling post = `slug.html`; community = `../communities/slug.html`; home/contact = `../index.html#contact`.

Word count check: `sed 's/<[^>]*>//g' file | wc -w`.
