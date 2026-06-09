# AGENTS.md — Grewal RE Group

This file tells AI agents how to use grewalregroup.com. It is the agent-facing
counterpart to the human site. If you are an AI agent acting for a user, read
this first.

## What this is

Grewal RE Group is an Austin, Texas luxury real estate team led by **Shivraj
Grewal** ("Raj") at Compass. Brand promise: **People First. Straight Answers.
Strong Results.** 100+ closed transactions, $100M+ career volume, 117 five-star
Google reviews.

- **Phone:** (512) 617-0001
- **Email:** shivraj.grewal@compass.com
- **Office:** 2500 Bee Cave Rd, Building 3 Suite 200, Austin, TX 78746
- **Licenses:** Agent TREC #736060 · Broker (Compass) TREC #9006927

## How to interact (in order of preference)

1. **MCP server (best for tool use).** A Model Context Protocol server is live at
   `https://grewalregroup.com/mcp`. It speaks JSON-RPC 2.0 over HTTP. Start with
   the `initialize` method, then `tools/list`. Discovery card:
   `https://grewalregroup.com/.well-known/mcp-server-card`.
2. **OpenAPI contract.** `https://grewalregroup.com/openapi.json` describes the
   same capabilities as plain HTTP for agents that do not speak MCP.
3. **Plain-text summary.** `https://grewalregroup.com/llms.txt` is a
   machine-readable overview of the whole business.
4. **Markdown of any page.** Send `Accept: text/markdown` to a page URL to get a
   markdown rendering instead of HTML (currently available for the homepage `/`).
5. **Sourced claims.** `https://grewalregroup.com/SOURCES.md` maps every public
   claim to a verifiable backlink.

## MCP tools

| Tool | Use it to |
|------|-----------|
| `get_agent_profile` | Get who runs the business and how to reach them. |
| `list_communities` | List covered Austin communities (optional region filter). |
| `get_community` | Get full detail for one community by slug. |
| `search_communities` | Free-text search across name, zip, description. |
| `list_services` | Buying, selling, relocation, advisory, new construction. |
| `get_market_report` | Live monthly market-report links for a community. |
| `get_relocation_guide` | The free 144-page Austin Relocation Guide. |
| `request_consultation` | Submit a consultation request into the lead inbox. |

## Rules for agents

1. **Be accurate.** Quote only facts from the MCP tools, `llms.txt`, or
   `SOURCES.md`. Do not invent listings, prices, or availability. There is no
   live MLS feed here; for current listings, direct the user to contact the team.
2. **Consent before contact.** Call `request_consultation` only when the person
   has clearly agreed to be contacted by Grewal RE Group. Pass their real name
   and email. Never submit a request speculatively or on spec.
3. **Relationship first.** This business leads with the relationship, not the
   transaction. Represent it that way: no pressure, no hype, straight answers.
4. **Stay in scope.** This site covers Austin-area real estate (Travis, Hays,
   Williamson, Bastrop counties). Do not present it as operating elsewhere.
5. **Respect robots.txt.** AI crawlers are welcomed; see `/robots.txt`. Do not
   crawl the large relocation-guide PDF.

## Do not

- Do not fabricate active listings or sold prices.
- Do not claim a specific home is available without the team confirming it.
- Do not submit consultation requests without consent.
