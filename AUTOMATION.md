# Site Automations

Two background automations keep the site and your CRM in sync. Both are built and
committed; each needs a couple of credentials to go fully live.

## 1. Live Google Review Sync
- **What:** Every 6h, pulls the real Google rating + review count + top reviews and
  rewrites the count sitewide, `data/reviews.json`, and the homepage carousel —
  then commits and auto-deploys. Notifies Notion when a new review lands.
- **Files:** `scripts/sync_reviews.py`, `.github/workflows/review-sync.yml`
- **Needs (GitHub → Settings → Secrets → Actions):**
  - `FIRECRAWL_API_KEY` *(or)* `GOOGLE_PLACES_API_KEY` (+ optional `GOOGLE_PLACE_ID`)
  - optional: `NOTION_TOKEN`, `NOTION_NOTIFY_PARENT`
- **Status:** Count already corrected to the real **119** by hand; sync activates on key.

## 2. Lead Intake (forms → Notion + Airtable + notification)
- **What:** Every verified Netlify form submission (contact, modal, newsletter, all
  community pages) is pushed into the Notion **Lead Tracker** (Source = Website,
  Status = New), mirrored to Airtable, and a 🔔 comment is posted as your notification.
- **File:** `netlify/functions/submission-created.mjs` (auto-fires; no webhook setup)
- **Needs (Netlify → Site settings → Environment variables):**
  - `NOTION_TOKEN` — internal integration token; **share the integration with the
    Lead Tracker database** in Notion.
  - `NOTION_LEADS_DB_ID` — defaults to the live Lead Tracker (`90ac0029…`).
  - optional: `AIRTABLE_TOKEN`, `AIRTABLE_BASE_ID`, `AIRTABLE_TABLE` (default `Website Leads`)
  - optional: `NOTION_NOTIFY_PAGE_ID` — a page to also drop lead callouts onto.

## 3. Daily Site Agent (existing)
- **File:** `scripts/daily_agent.py`, `.github/workflows/daily-agent.yml`
- **Fixed:** added `requirements.txt` so it stops insta-failing on the pip-cache step.
- **Needs:** `ANTHROPIC_API_KEY` secret to actually generate content.

## 4. SEO Analytics Agent (read-only monitor)
- **What:** Weekly (Mondays) pull of **Google Search Console** (rankings, clicks, CTR,
  page-2 opportunities, priority-keyword tracking), **GA4** (sessions, channels,
  conversions, top landing pages), and **PageSpeed** (Core Web Vitals). Writes a report
  and opens a PR. Does **not** modify site content — that stays with the Daily Agent.
- **Files:** `scripts/seo_agent.py`, `.github/workflows/seo-agent.yml`, `data/seo-config.json`
- **Outputs:** `logs/seo/report-YYYY-MM-DD.md` (+ `latest.md`), `data/seo/latest-insights.json`
- **Needs:**
  - Secret `GA_SERVICE_ACCOUNT_JSON` — service-account key JSON. ✅ set 2026-06-13.
  - **The service-account email must be granted access** (the key alone is not enough):
    - GA4 Admin → Property Access Management → add as **Viewer**
    - Search Console → Settings → Users and permissions → add as **Restricted/Full**
  - Repo **Variables** (Settings → Secrets and variables → Actions → *Variables*, not secrets):
    - `GA4_PROPERTY_ID` — e.g. `123456789` (or `properties/123456789`)
    - `GSC_SITE_URL` — e.g. `https://grewalregroup.com/` or `sc-domain:grewalregroup.com`
  - Optional secret `PAGESPEED_API_KEY` — raises PSI rate limits.
- **Cadence design:** daily = monitor only (no content writes); weekly = this report +
  page refresh via PR; monthly = new content via PR. Protects the site's
  helpful-content standing — no high-volume automated publishing.
- **Degrades gracefully:** a missing credential / un-granted source is logged in the
  report's *Run issues* section and skipped; a partial run still produces a report.
