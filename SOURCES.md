# Backlinks & Sources — Grewal RE Group Landing Page

Every factual claim on `index.html` mapped to a verifiable, public source.
Update this file whenever a stat changes (review count, transaction count,
volume, blog data) and propagate the change to `index.html` in the same PR.

**Last updated:** 2026-05-05
**Owner:** Shivraj Grewal · shivraj.grewal@compass.com

---

## 1. Identity & Credentials

| Claim on site | Authoritative source / backlink |
|---|---|
| Shivraj Grewal — TREC License #736060 | https://www.trec.texas.gov/apps/license-holder-search/ (search by license number) |
| Compass — TREC Broker License #9006927 | https://www.trec.texas.gov/apps/license-holder-search/ (search by broker license) |
| Office address: 2500 Bee Cave Rd, Bldg 3 Ste 200, Austin, TX 78746 | Google Business: https://share.google/1pYwueIVdeVLAtANo · Apple Maps: https://maps.apple/p/oTc0Km7azgEjNC |
| Compass affiliation | Compass Texas: https://www.compass.com/agents/shivraj-grewal/ (canonical agent page) |
| Tagline "People First. Straight Answers. Strong Results." | Internal brand standard — `Grewal RE Group Brain/4-REFERENCES/brand/GrewalREGroup_BrandGuidelines.pdf` |

## 2. Stats (the big numbers in the proof slab)

| Claim | Source | Verification cadence |
|---|---|---|
| **119 Google Reviews · ★5.0** | https://share.google/1pYwueIVdeVLAtANo (live Google Business Profile count) | **Auto-synced** every 6h by `scripts/sync_reviews.py` via `.github/workflows/review-sync.yml` → updates count sitewide + featured reviews in `data/reviews.json` + `index.html`, then auto-deploys. Needs `FIRECRAWL_API_KEY` (or `GOOGLE_PLACES_API_KEY`) repo secret. |
| **100+ closed transactions** | Compass internal sales record · MLS production report (Austin Board of REALTORS®) | Check quarterly |
| **$100M+ career volume** | Compass internal sales record · MLS production report | Check quarterly |
| **★5.0 average rating** | Google Business Profile (same Google source as review count) | Same cadence as #1 |

> **Note:** Earlier draft copy claimed 750 transactions / $600M / 255 reviews — those numbers were never accurate and have been removed everywhere. Memory file at `~/.claude/projects/-Users-shivrajsinghgrewal-Downloads-website/memory/user_real_estate_credentials.md` flags this so future drafts won't regress.

## 3. Designations & Memberships

| Claim | Source |
|---|---|
| **CLHMS Guild** (Certified Luxury Home Marketing Specialist) | The Institute for Luxury Home Marketing — https://www.luxuryhomemarketing.com/ (member directory lookup) |
| **CNE** (Certified Negotiation Expert) | Real Estate Negotiation Institute — https://www.therenegotiator.com/ |
| **NOT REALM Luxury Network member** | Confirmed by Shivraj 2026-05-05; do NOT add this designation back |

## 4. Service Areas Served

All neighborhood claims verified via:
- Travis County: https://www.traviscountytx.gov/
- Austin Board of REALTORS® area definitions: https://abor.com/
- Compass area pages (linked from each neighborhood card)

| Neighborhood card | Backing data source |
|---|---|
| Westlake Hills | Eanes ISD: https://www.eanesisd.net/ · Compass area: https://www.compass.com/homes-for-sale/west-lake-hills-tx/ |
| Barton Creek | Compass area: https://www.compass.com/homes-for-sale/barton-creek-austin-tx/ |
| Davenport Ranch | Compass area: https://www.compass.com/homes-for-sale/davenport-ranch-austin-tx/ |
| Tarrytown | Compass area: https://www.compass.com/homes-for-sale/tarrytown-austin-tx/ |
| Lakeway | Compass area: https://www.compass.com/homes-for-sale/lakeway-tx/ |
| Mueller | Compass area: https://www.compass.com/homes-for-sale/mueller-austin-tx/ |
| South Congress | Compass area: https://www.compass.com/homes-for-sale/south-congress-austin-tx/ |
| Rollingwood | Compass area: https://www.compass.com/homes-for-sale/rollingwood-tx/ |

## 5. Blog Posts — Sources for Every Data Claim

Source files live at: `Grewal RE Group Brain/5-CLAUDE-OUTPUTS/seo-outputs/`

### Steiner Ranch Buyer's Guide (Mar 23, 2026)
- "Selling in 49 days, down from 82 days a year ago" → **Redfin Steiner Ranch market data** https://www.redfin.com/neighborhood/118432/TX/Austin/Steiner-Ranch/housing-market
- "Median sale price $830,250" → Redfin (same URL)
- "4,600 acres between Lake Austin and Lake Travis" → Steiner Ranch HOA https://www.steinerranchhoa.org/
- "Eanes ISD" → https://www.eanesisd.net/
- ZIP 78732 demographics → US Census https://data.census.gov/profile?q=78732

### Rollingwood Neighborhood Guide (Mar 30, 2026)
- "Average home value $2,257,398" → **Zillow Rollingwood market** https://www.zillow.com/rollingwood-tx/home-values/
- "~500 homes, less than 1 sq mile" → City of Rollingwood https://www.rollingwoodtx.gov/
- "Eanes ISD" → https://www.eanesisd.net/
- ZIP 78746 stats → US Census https://data.census.gov/profile?q=78746

### East Austin Buyer Brief (Apr 6, 2026)
- East Austin trend data → Austin Board of REALTORS® monthly reports https://abor.com/marketstatistics
- Pricing benchmarks → Redfin East Austin https://www.redfin.com/neighborhood/4823/TX/Austin/East-Austin/housing-market

### Spring 2026 West Austin Market Guide (Mar 30, 2026)
- 78746 luxury data → Compass Texas Market Reports https://compasstxmarketreports.com/west-lake-hills/
- Westlake / Tarrytown comp data → Redfin neighborhood pages

### Austin Real Estate 2026 Central & East (Apr 13, 2026)
- Citywide trend data → ABoR Central Texas Housing Report https://abor.com/marketstatistics
- Compass market reports → https://compasstxmarketreports.com/austin-communities/

### West Austin Luxury Homes 2026 (Mar 23, 2026)
- Same underlying sources as the Spring 2026 guide above

### What's Happening with West Austin Luxury This Spring (Mar 16, 2026)
- ABoR Central Texas Housing Report
- Compass internal pipeline data

## 6. Compass Concierge Program

| Claim | Source |
|---|---|
| "Fronts the cost of pre-listing improvements" | https://www.compass.com/concierge/ |
| "No interest, no fees, pay at closing" | https://www.compass.com/concierge/ (program terms page) |
| Eligible improvements list | https://www.compass.com/concierge/ |

## 7. Market Reports Hub

All 22 city-level market report links in the Reports section point to:
`https://compasstxmarketreports.com/<city-slug>/?emailTo=Shivraj.Grewal@compass.com&agent=Grewal_RE_Group`

These are official Compass-maintained reports updated monthly.

## 8. Relocation Guide PDF

- **File on site:** `assets/guides/the-relocation-edition.pdf` (144 pages, **163 MB — full print quality** as authoritative source-of-truth per Shivraj 2026-05-05)
- **Source file:** `~/Downloads/Relocation guide_.pdf` (matches `Grewal RE Group Brain/10-MARKETING/relocation-guide/Relocation guide_.pdf`)
- **Backup compressed copy:** `assets/guides/the-relocation-edition_22mb-compressed.pdf.bak` (same 144 pages, ~22 MB, kept locally not deployed)
- **Earlier "141 pages" reference** was an approximation — file is 144 pages
- **Note:** if download speed becomes a friction point for users, the .bak copy can be promoted with no content change

## 9. Social / Profile Verification (the `sameAs` JSON-LD entries)

All 15 are verified live:

| Platform | URL | Notes |
|---|---|---|
| Instagram | https://www.instagram.com/grewalregroup/ | Brand handle |
| Facebook | https://www.facebook.com/Shivraj.Grewal.Realtor | Personal page used for business |
| LinkedIn (company) | https://www.linkedin.com/company/grewal-re-group/?viewAsMember=true | |
| X | https://x.com/ShivrajGrewal1 | |
| YouTube | https://www.youtube.com/@GrewalREGroup | |
| TikTok | https://www.tiktok.com/@grewalregroup | |
| Threads | https://www.threads.com/@grewalregroup | |
| Pinterest | https://www.pinterest.com/grewalshivraj/ | |
| Google Business | https://share.google/1pYwueIVdeVLAtANo | Source of truth for review count |
| Zillow (team) | https://www.zillow.com/profile/Grewal%20RE%20Group | |
| Zillow (Shivraj) | https://www.zillow.com/profile/Shivraj%20Grewal | 5.0 ★ · 3 reviews quoted verbatim on `/reviews.html` + homepage carousel + JSON-LD (`data/reviews.json → other_platforms.zillow`) |
| Realtor.com | https://www.realtor.com/realestateagents/62691e42baa428baf4d88cda | Steve Mayo testimonial quoted verbatim on `/reviews.html` + homepage carousel + JSON-LD (`data/reviews.json → other_platforms.realtor_com`) |
| Yelp | https://www.yelp.com/biz/grewal-re-group-austin | Claimed, 0 reviews yet — linked from `/reviews.html` "leave a review" CTA |
| Nextdoor | https://nextdoor.com/pages/shivraj-grewal-realtor-austin-tx/ | Neighbor recommendations (login-walled) — linked from `/reviews.html` hero |
| Reddit | https://www.reddit.com/r/AustinREAdvisor/ | Community owned by team |
| Alignable | https://www.alignable.com/rollingwood-tx/grewal-re-group | |
| Apple Maps | https://maps.apple/p/oTc0Km7azgEjNC | |
| Bing Maps | https://www.bing.com/maps/search?...local_ypid:%22YNBB07B358209CFB8F%22 | |

## 10. Compliance & Legal

| Claim | Source |
|---|---|
| TREC IABS form | https://www.trec.texas.gov/sites/default/files/pdf-forms/IABS%201-0.pdf |
| TREC Consumer Protection Notice | https://www.trec.texas.gov/forms/consumer-protection-notice |
| Equal Housing Opportunity statement | HUD: https://www.hud.gov/program_offices/fair_housing_equal_opp |
| MLS attribution (listings) | Austin Board of REALTORS® IDX: https://abor.com/idx |

## 11. Image Sources / Rights

| Image | Source | Rights |
|---|---|---|
| `assets/headshots/*.jpg` | Professional shoot, owned by Shivraj | Owned |
| `assets/listings/stephanie-lee-*.jpg` | Listing photoshoot for 1139 Stephanie Lee Ln | Owned (use only for "represented buyer" framing, not as active listing photos) |
| `assets/listings/featured-properties.jpg`, `single-level.jpg` | Brand "Header Images" set in `Grewal RE Group Brain/4-REFERENCES/Website, Grewal RE Group/Design Refresh 3/` | Owned (curated brand asset library) |
| `assets/images/hero.jpg` and other neighborhood photos | Brand asset library — see source folder above | Owned |
| `assets/logos/*.png` | Grewal RE Group brand kit at `grewal-re-group-design-system/assets/logos/` | Owned |

---

## 12. AEO FAQ Market Data — June 2026

### June 2026 (current — used in live FAQ, blog posts, and community pages)
| Claim | Source | Date |
|---|---|---|
| Austin metro ~12,508 active listings | Unlock MLS / Austin Board of REALTORS® (reported via KXAN) | June 11, 2026 |
| Austin metro ~$440,000 median sold price | Unlock MLS / Austin Board of REALTORS® (reported via KXAN) | June 11, 2026 |
| Austin metro ~4.7 months of inventory | Unlock MLS / Austin Board of REALTORS® (reported via KXAN) | June 11, 2026 |
| Austin metro 61 avg days on market | Unlock MLS / Austin Board of REALTORS® (reported via KXAN) | June 11, 2026 |
| 78746 zip median ~$1.72M | Unlock MLS / Austin Board of REALTORS® (zip-level table, via KXAN) | June 11, 2026 |

> **Competitor-source removal (2026-07-01):** Earlier drafts sourced metro
> figures (17,317 active, 5,042 pending, $473,745 median, 6.0 months) to the
> **Team Price Austin Market Update**. Team Price Real Estate is a competing
> Austin brokerage/team, so per the competitor-source rule in `/CLAUDE.md` all
> such citations were removed sitewide and re-sourced to the Unlock MLS / ABoR
> figures above. Team Price's proprietary "80-month recovery" forecast was
> removed from the blog and reframed as illustrative CAGR arithmetic on ABoR /
> Texas A&M TRERC data. "Orchard" (orchard.com, an Austin brokerage) was also
> dropped as a neighborhood-comp source in favor of Redfin/Realtor.com.

### Luxury Segment (current)
| Claim | Source | Date |
|---|---|---|
| Luxury segment $1,945,000 median sold price | Institute for Luxury Home Marketing, June 2026 Market Report | June 2026 |
| Luxury segment 25 days on market | Institute for Luxury Home Marketing, June 2026 Market Report | June 2026 |
| Luxury sales volume +10.3% YoY | Institute for Luxury Home Marketing, June 2026 Market Report | June 2026 |
| Luxury inventory -5.8% YoY | Institute for Luxury Home Marketing, June 2026 Market Report | June 2026 |

---

## 13. Things still needing primary-source citations (action items)

- [ ] Replace "100+ transactions" with exact verified count from Compass dashboard once available
- [ ] Add a "Last verified: <date>" stamp next to the review count chip on the site
- [ ] Add inline `<cite>` or footnote markers on each blog post page when those are built (Phase 2)
- [ ] Add a `/sources` HTML page for visitors to view this same data publicly (currently file-only)
- [ ] Verify ILHM June 2026 luxury report figures once full PDF is accessible (used summary data from ILHM website)
