---
name: grewal-canonical-facts
description: The standardized review count for Grewal RE Group and the single location where the conflicting value lives
metadata:
  type: project
---

Standard Google review count is **117** (schema `ratingCount` 117, llms.txt 117, index.md 117, AGENTS.md 117, and ~392 blog files say "117 Google reviews"). Recommended future-proof display pattern: **117+** in visible text, but keep JSON-LD `ratingCount` as an exact integer.

The ONLY place the conflicting **119** appears is `index.html`: line 1422 (`data-review-count="119"` and "119 reviews on Google") and line 1460 ("View All 119 Reviews"). (Note: most other "119" hits across the repo are an Unsplash photo ID, not a review count.)

**Why:** AI engines and Google cross-verify facts; one stray 119 lowers citation confidence.
**How to apply:** If review count drifts again, the fix is almost always in index.html. Bake "update index.html review count + schema ratingCount" into monthly maintenance. Flag any new file that shows a count other than 117/117+.
