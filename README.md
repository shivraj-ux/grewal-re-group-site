---
type: folder-readme
name: realestate-landing
last_updated: 2026-04-17
---

Hub: [[Welcome]]. Index: [[0-WIKI/index]]. Schema: [[CLAUDE]].

# realestate-landing

## Purpose

Standalone landing page. Single-page asset with `index.html` and supporting assets.

## Why this folder exists

Campaign-specific or niche landing page kept separate from the main website project.

## What is inside

`index.html` and `assets/` folder.

## How this connects to the wiki

Not wiki-ingested. Campaign performance and decisions that reference this landing page get filed to `../0-WIKI/topics/` or `../5-CLAUDE-OUTPUTS/analytics/`.

## Graph position

This folder is part of the Grewal RE Group Brain. From this page, you can reach everything else in two clicks: up to [[Welcome]], then out to any other folder.

## MCP Server

grewalregroup.com runs a Model Context Protocol server so an AI assistant can
query the site's facts directly instead of scraping HTML.

- **Endpoint:** `POST https://grewalregroup.com/mcp` (JSON-RPC 2.0, stateless).
  A plain `GET` on the same path returns a human-readable descriptor.
- **Discovery card:** `https://grewalregroup.com/.well-known/mcp-server-card`
  (and `.json`) — machine-readable name/description/tool list/auth, per the
  MCP server-card convention.
- **Auth:** none. All read tools are public; `request_consultation` requires
  the prospect's explicit consent before it's called.
- **Implementation:** `netlify/functions/mcp.mjs`, a Netlify Function. Every
  tool's parameters are validated with a Zod schema (`tool.input.safeParse(...)`)
  before the handler runs; invalid input returns a JSON-RPC error, never a
  loosely-typed pass-through.

### Tools exposed (all verb-first)

| Tool | What it does |
|---|---|
| `get_agent_profile` | Profile, credentials, licenses, contact, and track record for Shivraj Grewal / Grewal RE Group. |
| `list_communities` | All covered Austin-area communities, optionally filtered by region. |
| `get_community` | Full detail for one community by slug (description, commentary, zip, related communities, market report link). |
| `search_communities` | Free-text search across community name, zip, and description. |
| `list_services` | Buying, selling, relocation, advisory, new-construction services. |
| `get_market_report` | Live monthly market-report links for a community. |
| `get_relocation_guide` | The free 154-page Austin Relocation Guide (URL + summary). |
| `request_consultation` | Submits a lead into the same inbox as the website contact form. Requires consent. |

### Example queries

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}
{"jsonrpc":"2.0","id":2,"method":"tools/list"}
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_community","arguments":{"slug":"west-lake-hills"}}}
{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"search_communities","arguments":{"query":"Eanes ISD"}}}
```

### Other agent-facing entry points

- `/AGENTS.md` — instructions for AI agents acting on a user's behalf.
- `/llms.txt` and `/llms-full.txt` — plain-text manifests (short and full)
  per the llms.txt standard.
- `/openapi.json` — OpenAPI contract for the MCP endpoint and the read-only
  data files (sitemap, image sitemap, communities dataset, llms.txt).
- `robots.txt` explicitly allows the major AI crawlers (GPTBot, ClaudeBot,
  anthropic-ai, PerplexityBot, Google-Extended, CCBot, Bytespider, cohere-ai,
  and others) with a per-bot `Content-Signal` policy (`search=yes,
  ai-input=yes, ai-train=no`), also sent as an HTTP response header.
