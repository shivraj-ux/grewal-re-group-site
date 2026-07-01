# CLAUDE.md — READ THIS FIRST before creating or editing ANY content

This is the Grewal RE Group website (`grewalregroup.com`). Before you write a
new page, blog post, FAQ answer, market stat, community page, or edit anything
that cites data, you MUST follow the sourcing rule below. This rule overrides
convenience. When in doubt, leave the claim out.

---

## 🚫 THE COMPETITOR-SOURCE RULE (non-negotiable)

**No information on this site may be gathered from, attributed to, or linked to
any real estate AGENT, BROKER, TEAM, GROUP, or boutique BROKERAGE that serves
the Austin, Texas area.** We do not cite competitors as a source, and we never
name or link their websites as a source anywhere on our platform.

This applies to page copy, blog posts, FAQ answers, JSON-LD structured data,
`<cite>`/footnote/`[n]` reference lists, "Sources:" lines, `SOURCES.md`, and any
meta/`measurementTechnique` fields.

### What IS prohibited (local Austin competitors)
Any Austin-area agent / team / group / boutique brokerage and their market
newsletters, forecasts, blogs, "market update" PDFs, or data aggregations —
including but not limited to:

- **Team Price Real Estate** (teamprice.com) — market updates & recovery forecasts
- **Orchard** (orchard.com) — Austin-based brokerage/iBuyer, comp data
- **Kumara Wilcoxon** (kumarawilcoxon.com) — Sotheby's
- **Meryl Hawk** (merylhawk.com) — Coldwell Banker
- **Luxe Homes Austin** (luxehomesaustin.com)
- Bramlett Residential, Spyglass Realty, Realty Austin / @properties,
  Kuper Sotheby's International Realty, Moreland Properties, Gottesman
  Residential, JBGoodwin, Twelve Rivers, Turnquist Partners, Dochen,
  Homecity, Urbanspace, Pauly Presley, and any similar Austin agent/team/brokerage.

> Compass is **our own** brokerage — it is not a competitor. `compass.com` and
> `compasstxmarketreports.com` are allowed.

### What IS allowed (permitted sources)
- **Government / public data:** *.gov, Census, BLS, FRED, HUD, IRS, FEMA, TREC,
  Texas Comptroller, county appraisal districts (TCAD/WCAD/etc.), city sites.
- **Industry boards & MLS (the board itself, not a member brokerage):**
  Austin Board of REALTORS® (abor.com), **Unlock MLS** (unlockmls.org),
  NAR (nar.realtor), Texas REALTORS® (texasrealtors.com).
- **Academic / research:** Texas A&M **TRERC / recenter.tamu.edu**,
  Harvard JCHS, Institute for Luxury Home Marketing (ILHM).
- **National consumer portals / data aggregators (NOT treated as local
  competitors):** Redfin, Zillow, Realtor.com, Walk Score, GreatSchools, Niche.
- **Schools, HOAs, community developers, chambers, news outlets** (KXAN,
  Austin Monitor, Austin Business Journal), Compass (our brokerage).

If a stat only exists on a competitor's site, either (a) find it at the primary
source (MLS board / county / Census), or (b) do not publish it.

---

## ✅ Checklist to run every time you add or edit sourced content

1. For every external link, name, or "per <X>" attribution, ask: *Is X an Austin
   real-estate agent, team, group, or boutique brokerage?* If yes → do not use it.
2. Re-source the underlying fact to a permitted primary source, or drop the claim.
3. Never relabel a competitor's numbers as a permitted source — that is
   fabrication. Use the permitted source's own published figures.
4. Update `SOURCES.md` in the same change so the source map stays accurate.
5. Grep your change for competitor names/domains before committing:
   `grep -riE 'team price|teamprice|orchard\.com|kumarawilcoxon|merylhawk|luxehomesaustin|bramlett|spyglass realty|realty austin|kuper|moreland|gottesman' .`

> `data/competitor-log.json` is an **internal** competitive-research file. It is
> not a public source citation. Do not cite anything from it on the live site.

Deploy = push to `main` (Netlify auto-deploys). Do not push competitor sources.
