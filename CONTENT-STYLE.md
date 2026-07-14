# CONTENT-STYLE.md — LLM-Ready Content Rules

These five rules apply to every new blog/resource article and to any existing
article being substantially edited. They exist so a single section, pulled out
of the page on its own, can be read, quoted, and understood correctly by an AI
system without the surrounding page for context. They are separate from the
brand-voice rules in `CLAUDE.md` (sourcing) and the internal brand-voice
guidelines (banned words, "Grewal RE Group at Compass" phrasing) — apply all
of them together.

Reference implementation: `blog/eanes-isd-school-guide-2026.html` (rewritten
2026-07-11 to this standard).

## 1. Visible "Last updated" date

Every article shows a visible, human-readable last-updated line under the
headline — not just a `dateModified` value buried in JSON-LD:

```html
<p class="last-updated">
  <strong>Last updated: <time datetime="2026-07-11">July 11, 2026</time></strong>
  — what changed or was reverified.
</p>
```

Update this line, the `<meta property="article:modified_time">` tag, and the
JSON-LD `dateModified` field together, in the same edit, whenever the content
changes. All three must always agree — an AI system that reads one and
double-checks another should never find a mismatch.

## 2. No fragment-only sections

A section must carry enough context to be quoted on its own, out of the
page, and still make sense. A label-only card (name + one stat, no sentence)
fails this test even if a full paragraph happens to sit right after it in the
DOM — an extraction pass that grabs the card and not the paragraph gets
nothing useful.

- If you have 3+ items that are naturally parallel data (schools, price
  tiers, comparison rows), use rule 5's table instead of a card grid.
- If a section is prose, write at least one full paragraph (3+ sentences)
  before moving to a bulleted list. Bullets that follow a paragraph are fine;
  bullets that replace the paragraph are not.

## 3. Subheadings preview the answer, not a label

A subheading should tell the reader (or an LLM skimming just the headings)
what they'll learn, in plain language, in the way a person would actually ask
it.

- Bad: "Schools", "Boundaries", "Enrollment"
- Good: "How Eanes ISD boundaries affect resale value", "Can you enroll in
  Eanes ISD without living inside the district?"

Numbered H2s are fine for navigation (`2. Which elementary school will your
home be zoned to?`) — keep the number, replace the label with the question or
claim it answers.

## 4. Answer-first section intros

The first sentence of a section states the conclusion. Supporting detail,
data, and caveats follow. Do not open with a windup ("Here's what the data
shows...", "Let's look at...") — say the answer, then support it.

- Bad: "The financial case for the Eanes ISD premium is well-documented.
  Here is what the data shows for 2025–26:"
- Good: "Homes zoned to Eanes ISD sell for 15–25% more than comparable homes
  just outside the district... The rest of this section breaks down where
  that premium is largest and why."

## 5. At least one real HTML `<table>` per data-heavy article

Any article comparing 3+ things on the same 2+ attributes (neighborhoods,
price tiers, school ratings, tax rates, year-over-year figures) gets a real
`<table>` with `<thead>`/`<tbody>`, not a prose list or a styled `<div>` grid.
Tables are what both search engines' rich-result parsers and LLM extraction
passes handle most reliably for comparable facts — a `<div>` grid styled to
look like a table structurally isn't one.

Use the existing `.data-table-wrap > table` pattern (see
`blog/eanes-isd-school-guide-2026.html`) for consistent styling.

## Checklist before publishing or substantially editing an article

1. Visible "Last updated" line present, and matches `article:modified_time`
   and JSON-LD `dateModified` exactly.
2. No section is a label-only fragment; convert card grids of parallel data
   to a table (rule 5) or add a full paragraph.
3. Every subheading previews its section's actual answer.
4. Every section's first sentence states the answer; detail follows.
5. At least one `<table>` for any comparable, data-heavy content.
6. Still true from `CLAUDE.md`: no competitor-agent sourcing, real dates only,
   no fabricated stats, and no "Grewal RE Group at Compass" phrasing —
   Compass affiliation belongs in the footer disclosure line, not the bio.
