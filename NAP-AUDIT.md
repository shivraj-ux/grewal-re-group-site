# NAP-AUDIT.md — Name / Address / Phone Consistency Audit

Generated 2026-07-11. This is a **manual handoff list** — Claude does not have
credentials for any of these platforms and has not logged into or edited any
of them. Every URL below was pulled from data already in this repo
(`data/reviews.json`, homepage `sameAs` list, `SOURCES.md`); none were
invented.

## Canonical NAP (what every platform below should match)

- **Name:** Grewal RE Group (agent: Shivraj Grewal)
- **Address:** 2500 Bee Cave Rd, Building 3, Suite 200, Austin, TX 78746
- **Phone:** (512) 617-0001
- **Email:** shivraj.grewal@compass.com
- **Brokerage (disclosure only, not part of the brand name):** Compass RE Texas, LLC

Confirmed by code audit: every occurrence of this NAP inside the codebase
(homepage, all 30 community pages, all 322 blog posts, JSON-LD, footers) is
consistent — no page states a different business address or phone number for
Grewal RE Group itself. (Other cities named across blog content, e.g.
Georgetown, Round Rock, Fredericksburg, are the *subject* of those articles —
towns being described — not claims about the business's own location, and
are not a NAP problem.)

## Platform checklist

| Platform | URL on file | Status | What to check/fix |
|---|---|---|---|
| Google Business Profile | share link `share.google/1pYwueIVdeVLAtANo`, CID `14895348687569356370` | 5.0★, 119 reviews (per `data/reviews.json`) | Confirm listed address is exactly "2500 Bee Cave Rd, Building 3, Suite 200, Austin, TX 78746" and phone is (512) 617-0001. This is the highest-priority listing (local pack + AggregateRating source) — verify first. |
| Zillow (agent profile) | zillow.com/profile/Shivraj%20Grewal | 5.0★, 3 reviews on file | Confirm profile city says Austin, TX (not Rollingwood/Westlake Hills) and phone matches. |
| Zillow (team profile) | zillow.com/profile/Grewal%20RE%20Group | Listed in homepage sameAs | Same check — confirm this is still an active, separate profile from the personal one and NAP matches. |
| Realtor.com | realtor.com/realestateagents/62691e42baa428baf4d88cda | 0 native ratings on file; a syndicated testimonial (Steve Mayo) appears on-site | Confirm office address/phone on the profile match canonical NAP. Consider actively soliciting reviews here since native rating is empty. |
| Yelp | yelp.com/biz/grewal-re-group-austin | 0 reviews (per `data/reviews.json`) | Confirm the business address/phone on the Yelp listing match canonical NAP. This is a review-generation gap, not just a NAP gap — 0 reviews on a claimed profile looks worse than no profile. |
| Nextdoor | nextdoor.com/pages/shivraj-grewal-realtor-austin-tx/ | On file, no rating data captured | Confirm NAP on the page and that the neighborhood/service-area setting is Austin, TX-based. |
| Compass agent bio | compass.com/agents/shivraj-grewal/ | Live, already cited on-site as a source | This is Compass's own system — confirm the office address it displays matches 2500 Bee Cave Rd, Austin, TX 78746 (Compass sometimes shows a different branch office by default). |
| LinkedIn (company page) | linkedin.com/company/grewal-re-group/ | In sameAs | Confirm the "Location" field on the LinkedIn company page says Austin, TX, not a personal profile default or blank. |
| Facebook | facebook.com/Shivraj.Grewal.Realtor | In sameAs | Confirm the Page's "About" address/phone match canonical NAP (Facebook Pages have a dedicated address field separate from the bio text). |
| Instagram | instagram.com/grewalregroup/ | In sameAs | Bio-only platform (no structured address field) — confirm the bio text says "Austin, TX" if it states a city at all. |
| YouTube | youtube.com/@GrewalREGroup | In sameAs | Confirm channel "About" location is set to Austin, TX. |
| TikTok | tiktok.com/@grewalregroup | In sameAs | No structured address field — confirm bio text location, if present, says Austin, TX. |
| X (Twitter) | x.com/ShivrajGrewal1 | In sameAs | Confirm profile "Location" field says Austin, TX. |
| Threads | threads.com/@grewalregroup | In sameAs | Confirm profile location field, if set, says Austin, TX. |
| Pinterest | pinterest.com/grewalshivraj/ | In sameAs | Confirm profile location, if set, says Austin, TX. |
| Alignable | alignable.com/rollingwood-tx/grewal-re-group | In sameAs | **Flag: the listing URL slug itself is `rollingwood-tx`, not `austin-tx`.** Alignable assigns the slug from whatever city was entered at signup. Log into Alignable and check whether the profile's actual address field says Austin, TX 78746 (the URL slug alone may just be stale/cosmetic) — if the underlying address is genuinely set to Rollingwood, update it to the canonical Austin, TX address. |
| Apple Maps | maps.apple/p/oTc0Km7azgEjNC | In sameAs | Confirm the pin/listing address matches canonical NAP exactly (Apple Business Connect pulls from a claimed listing, similar to GBP). |
| Reddit | reddit.com/r/AustinREAdvisor/ | In sameAs | This is a subreddit/community, not a business listing with an address field — no NAP action needed, included here only for completeness. |
| BBB (Better Business Bureau) | Not found on file | **No listing found in this repo.** | Not currently claimed anywhere in site content or sameAs. Decide whether to create one; if created, use the canonical NAP above from day one. |

## Priority order for manual fixes

1. **Google Business Profile** — the single highest-leverage listing (local
   pack ranking + the AggregateRating this site's schema cites). Verify first.
2. **Alignable** — the only listing where the audit found a concrete signal
   (`rollingwood-tx` in the URL) that the address on file might not say
   Austin, TX. Check this one specifically, don't just spot-check it like
   the others.
3. **Yelp** and **Realtor.com** — both show 0 native reviews. Fixing NAP here
   is easy; the bigger unlock is review generation (Yelp review-gen is a
   known gap — the profile is claimed but has never been actively promoted
   to past clients).
4. Everything else — spot-check on your next pass through each platform's
   dashboard; low risk, but easy to let drift once someone edits a profile
   directly on the platform instead of through this checklist.

## What this file is not

This is not a scraped or logged-in audit — no platform was visited to verify
its *current* listed address; every "Status"/"Confirm" note above is a
todo for a human with login access. Re-run a code grep for
`addressLocality`, `geo.placename`, and `streetAddress` after any future
office move to make sure the canonical NAP above still matches the codebase
before re-checking these platforms.
