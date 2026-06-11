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
