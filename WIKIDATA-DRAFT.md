# WIKIDATA-DRAFT.md — Manual Submission Packet

**This is a manual handoff task.** Wikidata entries require a human account in
good standing and are subject to community notability review; Claude cannot
create or submit one on your behalf. Everything below is drafted so Shivraj
(or whoever submits it) can paste it directly into Wikidata's entry creation
form at https://www.wikidata.org/wiki/Special:NewItem.

## Before submitting: notability check

Wikidata is more permissive than Wikipedia (it accepts many local businesses
and professionals that Wikipedia would reject), but an entry can still be
challenged or deleted if it has zero independent, verifiable references. Right
now the strongest available references are the business's own website,
Google/Zillow/Realtor.com profiles, and the Compass agent bio — all of which
are self-published or platform-hosted, not independent editorial coverage.
**Recommendation:** submit the entity, but expect it may need a news mention,
industry-award listing, or other third-party source added later to withstand
scrutiny. Don't be surprised if it needs a second edit pass after an initial
community review.

## Proposed entity

- **Label (entity name):** Grewal RE Group
- **Description (short, Wikidata-style, ~1 line):** American real estate
  agency based in Austin, Texas
- **Also known as / aliases:** Shivraj Grewal (principal agent); "Grewal Real
  Estate Group"

## Instance of (P31)

- **real estate company** (Q3538403) — primary claim
- Consider also: **business** (Q4830453) as a broader fallback if "real
  estate company" isn't accepted by a reviewer

## Core statements to add

| Property | Value | Source |
|---|---|---|
| headquarters location (P159) | Austin, Texas (Q16559) | grewalregroup.com footer + GBP listing |
| country (P17) | United States of America (Q30) | — |
| located in the administrative territorial entity (P131) | Travis County, Texas (Q383403) | office address is in Travis County |
| official website (P856) | https://grewalregroup.com | — |
| inception (P571) | *(fill in: year Grewal RE Group was founded — verify with Shivraj before submitting, not in this repo)* | — |
| founder (P112) | Shivraj Grewal *(create/link a separate Wikidata item for him if one doesn't exist, or omit until one does)* | grewalregroup.com/about |
| industry (P452) | real estate (Q12280) | — |
| parent organization / affiliation | Compass, Inc. (Q60755316 — verify this Q-ID before use; Compass is the brokerage Grewal RE Group operates under, not its owner) | Compass agent bio: compass.com/agents/shivraj-grewal/ |

## sameAs / identifiers (verified profiles only — do not add unverified ones)

- Official website: https://grewalregroup.com
- LinkedIn (company): https://www.linkedin.com/company/grewal-re-group/
- Instagram: https://www.instagram.com/grewalregroup/
- Facebook: https://www.facebook.com/Shivraj.Grewal.Realtor
- YouTube: https://www.youtube.com/@GrewalREGroup
- X (Twitter): https://x.com/ShivrajGrewal1
- Zillow profile: https://www.zillow.com/profile/Grewal%20RE%20Group
- Realtor.com profile: https://www.realtor.com/realestateagents/62691e42baa428baf4d88cda
- Compass agent bio: https://www.compass.com/agents/shivraj-grewal/
- Google Business Profile: https://share.google/1pYwueIVdeVLAtANo

## Address / location detail (for reference, not all of these map to Wikidata properties directly)

- 2500 Bee Cave Rd, Building 3, Suite 200, Austin, TX 78746
- Phone: (512) 617-0001
- Email: shivraj.grewal@compass.com

## What to double-check before submitting

1. **Founding year (inception)** — not stored anywhere in this codebase.
   Confirm with Shivraj before adding a P571 claim; an entity with a wrong
   founding date is worse than one with the field left blank.
2. **Compass's exact Wikidata Q-ID** — Q60755316 above is a placeholder guess
   and must be verified on wikidata.org before use (search "Compass, Inc."
   real estate company). Do not submit an unverified Q-ID.
3. **Whether a separate "Shivraj Grewal" (person) entity should exist** —
   Wikidata prefers a person entity linked via P112 (founder) rather than
   folding a person's full biography into the company entity. If Shivraj
   wants both, draft the person entity as a second, separate submission
   after this one exists (P112 can point to a redlink until then, but a
   completed link is stronger).
4. Re-read Wikidata's notability guidance
   (https://www.wikidata.org/wiki/Wikidata:Notability) once at submission
   time in case the policy has changed since this draft was written.
