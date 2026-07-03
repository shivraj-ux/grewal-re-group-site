// Grewal RE Group — Model Context Protocol (MCP) server.
//
// Runs as a Netlify Function (Web API / Functions v2). Speaks MCP over HTTP
// using JSON-RPC 2.0, stateless. Exposes verb-first, Zod-validated tools that
// let an AI agent read the same facts a human reads on grewalregroup.com and
// submit a consultation request straight into the website's lead inbox.
//
// Public endpoint: https://grewalregroup.com/mcp  (redirected here in netlify.toml)
// Discovery card:  https://grewalregroup.com/.well-known/mcp-server-card

import { z } from "zod";
import { zodToJsonSchema } from "zod-to-json-schema";
import communitiesFile from "../../data/communities.json" with { type: "json" };

// Canonical brand domain (used only as a fallback when no request origin is
// available). All live links are resolved against the actual serving origin so
// the server works correctly on the netlify.app test host now and on
// grewalregroup.com after launch.
const FALLBACK_SITE = "https://grewalregroup.com";
const COMPASS_REPORTS =
  "https://compasstxmarketreports.com/austin-communities/?emailTo=shivraj.grewal@compass.com&agent=Grewal_RE_Group";

function originFromReq(req) {
  const host = req.headers.get("x-forwarded-host") || req.headers.get("host");
  const proto = req.headers.get("x-forwarded-proto") || "https";
  if (host) return `${proto}://${host}`;
  try {
    return new URL(req.url).origin;
  } catch {
    return FALLBACK_SITE;
  }
}

const COMMUNITIES = communitiesFile.communities;

// ── Static facts (single source of truth: llms.txt + the homepage) ──────────
const AGENT = {
  name: "Shivraj Grewal",
  goesBy: "Raj",
  title: "Founder & Principal, Luxury Real Estate Advisor",
  brand: "Grewal RE Group",
  promise: "People First. Straight Answers. Strong Results.",
  brokerage: "Compass",
  brokerLicense: "TREC #9006927",
  agentLicense: "TREC #736060",
  designations: ["CLHMS Guild", "CNE"],
  office: "2500 Bee Cave Rd, Building 3, Suite 200, Austin, TX 78746",
  phone: "(512) 617-0001",
  email: "shivraj.grewal@compass.com",
  stats: {
    transactions: "100+ closed",
    careerVolume: "$100M+",
    googleReviews: "117 five-star",
  },
  counties: ["Travis", "Hays", "Williamson", "Bastrop"],
};

const SERVICES = [
  { key: "buying", name: "Buyer representation", detail: "Luxury, first-time, move-up, and investor buyers. Discovery call, financing coordination, neighborhood comparison, tailored search, offer strategy with comparable-sales data, inspection guidance, closing management." },
  { key: "selling", name: "Seller representation", detail: "Data-driven pricing, Compass Concierge prep, professional marketing, showing management, negotiation, and contract-to-close coordination built around your net proceeds." },
  { key: "relocation", name: "Relocation advisory", detail: "Neighborhood shortlists, virtual and in-person tours, side-by-side Austin vs. current-city comparisons, and coordination with your current-city agent." },
  { key: "advisory", name: "Investment & advisory", detail: "Investor analysis, portfolio review, and market positioning. Clear numbers, honest cash-flow view, no speculation." },
  { key: "new-construction", name: "New construction representation", detail: "Builder representation, contract negotiation, upgrade guidance, lot through walk-through." },
];

// West/Central/etc. grouping mirrors the structure published in /llms.txt.
const REGION = {
  "west-lake-hills": "West Austin", "tarrytown": "West Austin", "barton-hills": "West Austin",
  "barton-creek": "West Austin", "zilker": "West Austin", "circle-c-ranch": "West Austin",
  "northwest-hills": "North/Northwest", "north-central-austin": "North/Northwest",
  "downtown": "Central + East", "central-austin": "Central + East", "east-austin": "Central + East",
  "travis-heights": "Central + East", "mueller": "Central + East",
  "lake-travis": "Lake & Hill Country", "dripping-springs": "Lake & Hill Country",
  "fredericksburg": "Lake & Hill Country", "steiner-ranch": "Lake & Hill Country",
  "leander-cedar-park": "Surrounding Metro", "round-rock": "Surrounding Metro",
  "pflugerville": "Surrounding Metro", "georgetown": "Surrounding Metro",
  "kyle": "Surrounding Metro", "buda": "Surrounding Metro",
};

function communityView(slug, site) {
  const c = COMMUNITIES[slug];
  if (!c) return null;
  return {
    slug,
    name: c.name,
    zip: c.zip,
    region: REGION[slug] || "Greater Austin",
    description: c.description,
    commentary: c.commentary,
    related: c.related || [],
    pageUrl: `${site}/communities/${slug}.html`,
    marketReportUrl: `${site}/communities/${slug}.html`,
  };
}

// ── Tool definitions: verb-first names, Zod input schemas ────────────────────
const TOOLS = {
  get_agent_profile: {
    description:
      "Get the profile, credentials, licenses, contact details, and track record for Shivraj Grewal and Grewal RE Group. Call this when an agent needs to know who runs the business or how to reach them.",
    input: z.object({}),
    handler: async (_args, site) => ({ ...AGENT, website: site }),
  },

  list_communities: {
    description:
      "List the Austin-area communities Grewal RE Group covers, with zip, region, and a one-line description. Optionally filter by region (West Austin, Central + East, North/Northwest, Lake & Hill Country, Surrounding Metro).",
    input: z.object({
      region: z.string().optional().describe("Optional region filter, matched case-insensitively."),
    }),
    handler: async ({ region }, site) => {
      let slugs = Object.keys(COMMUNITIES);
      if (region) {
        const r = region.toLowerCase();
        slugs = slugs.filter((s) => (REGION[s] || "").toLowerCase().includes(r));
      }
      return { count: slugs.length, communities: slugs.map((s) => communityView(s, site)) };
    },
  },

  get_community: {
    description:
      "Get full detail for one community by slug: description, on-the-ground commentary, zip, related communities, and the page URL with its live monthly market report.",
    input: z.object({
      slug: z.string().describe("Community slug, e.g. 'west-lake-hills', 'barton-creek', 'mueller'."),
    }),
    handler: async ({ slug }, site) => {
      const v = communityView(slug, site);
      if (!v) {
        return {
          error: `Unknown community '${slug}'.`,
          validSlugs: Object.keys(COMMUNITIES),
        };
      }
      return v;
    },
  },

  search_communities: {
    description:
      "Search the covered communities by free-text query against name, zip, and description. Returns the best matches.",
    input: z.object({
      query: z.string().min(1).describe("Search text, e.g. 'Eanes ISD', '78746', 'greenbelt', 'gated golf'."),
    }),
    handler: async ({ query }, site) => {
      const q = query.toLowerCase();
      const matches = Object.keys(COMMUNITIES)
        .map((s) => communityView(s, site))
        .filter(
          (c) =>
            c.name.toLowerCase().includes(q) ||
            String(c.zip).toLowerCase().includes(q) ||
            c.description.toLowerCase().includes(q) ||
            c.commentary.toLowerCase().includes(q)
        );
      return { query, count: matches.length, matches };
    },
  },

  list_services: {
    description:
      "List the services Grewal RE Group offers (buying, selling, relocation, investment advisory, new construction) with a short description of each.",
    input: z.object({}),
    handler: async () => ({ services: SERVICES }),
  },

  get_market_report: {
    description:
      "Get the live monthly market-report links for a community. Each community page embeds a Compass market report refreshed monthly. Returns the community page URL plus the master Austin report.",
    input: z.object({
      slug: z.string().describe("Community slug to get the market report for."),
    }),
    handler: async ({ slug }, site) => {
      const v = communityView(slug, site);
      if (!v) {
        return { error: `Unknown community '${slug}'.`, validSlugs: Object.keys(COMMUNITIES) };
      }
      return {
        community: v.name,
        slug,
        communityReportUrl: v.marketReportUrl,
        masterAustinReportUrl: COMPASS_REPORTS,
        note: "Reports embed live Compass data and refresh monthly.",
      };
    },
  },

  get_relocation_guide: {
    description:
      "Get the free Austin Relocation Guide: a 154-page PDF covering neighborhoods, schools, cost of living, and the market. Returns the guide URL and a summary.",
    input: z.object({}),
    handler: async (_args, site) => ({
      title: "Austin Relocation Guide (The Relocation Edition)",
      pages: 144,
      url: `${site}/assets/guides/the-relocation-edition.pdf`,
      landingUrl: `${site}/relocation-guide`,
      covers: ["Neighborhoods", "Schools & districts", "Cost of living", "Market context", "Commute & lifestyle"],
    }),
  },

  request_consultation: {
    description:
      "Submit a consultation request on behalf of a prospective client. Drops the lead into the same inbox as the website contact form. Shivraj follows up the same day. Use this only with the person's explicit consent to be contacted.",
    input: z.object({
      name: z.string().min(1).describe("Full name of the prospective client."),
      email: z.string().email().describe("Contact email."),
      phone: z.string().optional().describe("Contact phone (optional)."),
      interest: z
        .enum(["Buying", "Selling", "Relocation", "Advisory / Investment", "Just Exploring"])
        .describe("What they need help with."),
      message: z.string().optional().describe("Free-text detail about their plans."),
    }),
    handler: async ({ name, email, phone, interest, message }, site) => {
      // Netlify Forms ingests urlencoded POSTs that carry a registered form-name.
      // Post to the same origin the server runs on so the lead lands in this
      // deploy's Netlify Forms inbox (test host now, grewalregroup.com later).
      const body = new URLSearchParams({
        "form-name": "contact-section",
        name,
        email,
        phone: phone || "",
        interest,
        message: message || "",
        consent: "agreed",
        source: "mcp-server",
      });
      try {
        const res = await fetch(`${site}/`, {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: body.toString(),
        });
        if (res.ok) {
          return {
            submitted: true,
            status: res.status,
            confirmation: `Thanks ${name.split(" ")[0]} — your request reached Grewal RE Group. Shivraj follows up the same day at ${email}.`,
            bookingFallback: `${site}/#contact`,
          };
        }
        // Form capture not active on this deploy yet. Never leave the agent
        // without a way to reach the team.
        return {
          submitted: false,
          status: res.status,
          confirmation:
            "Automatic submission is not active on this deploy yet. To reach Grewal RE Group directly:",
          phone: AGENT.phone,
          email: AGENT.email,
          bookingFallback: `${site}/#contact`,
        };
      } catch (e) {
        return {
          submitted: false,
          error: String(e),
          bookingFallback: `${site}/#contact`,
          phone: AGENT.phone,
          email: AGENT.email,
        };
      }
    },
  },
};

const SERVER_INFO = { name: "grewal-re-group", version: "1.0.0" };

// MCP discovery card, built with absolute URLs resolved against the serving
// host so the transport endpoint is verifiable on any domain (the test host
// now, grewalregroup.com at launch). Served at /.well-known/mcp-server-card.
function buildCard(site) {
  return {
    schemaVersion: "2025-06-18",
    name: "grewal-re-group",
    title: "Grewal RE Group MCP Server",
    version: "1.0.0",
    description:
      "Verb-first MCP tools for Grewal RE Group, an Austin luxury real estate team led by Shivraj Grewal at Compass. Read the agent profile, covered communities, services, live market reports, and the relocation guide, and submit a consultation request.",
    vendor: { name: "Grewal RE Group", url: site, contact: "shivraj.grewal@compass.com" },
    transport: { type: "http", protocol: "json-rpc-2.0", url: `${site}/mcp` },
    authentication: {
      type: "none",
      note: "Read tools are public. request_consultation requires the prospect's explicit consent to be contacted.",
    },
    capabilities: { tools: true, resources: false, prompts: false },
    tools: Object.entries(TOOLS).map(([name, t]) => ({ name, description: t.description })),
    documentation: {
      agents: `${site}/AGENTS.md`,
      openapi: `${site}/openapi.json`,
      llms: `${site}/llms.txt`,
      sources: `${site}/SOURCES.md`,
    },
  };
}

function toolList() {
  return Object.entries(TOOLS).map(([name, t]) => ({
    name,
    description: t.description,
    inputSchema: zodToJsonSchema(t.input, { target: "jsonSchema7", $refStrategy: "none" }),
  }));
}

function rpcResult(id, result) {
  return { jsonrpc: "2.0", id, result };
}
function rpcError(id, code, message) {
  return { jsonrpc: "2.0", id, error: { code, message } };
}

async function handleRpc(msg, site) {
  const { id, method, params } = msg;

  if (method === "initialize") {
    return rpcResult(id, {
      protocolVersion: params?.protocolVersion || "2025-06-18",
      capabilities: { tools: { listChanged: false } },
      serverInfo: SERVER_INFO,
      instructions:
        "Read-first MCP server for Grewal RE Group, an Austin luxury real estate team. Use the read tools to answer questions about the agent, communities, services, market reports, and the relocation guide. Use request_consultation only with the client's explicit consent.",
    });
  }

  // Notifications carry no id and expect no response.
  if (method === "notifications/initialized" || method === "notifications/cancelled") {
    return null;
  }

  if (method === "ping") return rpcResult(id, {});

  if (method === "tools/list") {
    return rpcResult(id, { tools: toolList() });
  }

  if (method === "tools/call") {
    const name = params?.name;
    const tool = TOOLS[name];
    if (!tool) return rpcError(id, -32602, `Unknown tool: ${name}`);
    const parsed = tool.input.safeParse(params?.arguments || {});
    if (!parsed.success) {
      return rpcResult(id, {
        isError: true,
        content: [{ type: "text", text: `Invalid arguments: ${parsed.error.message}` }],
      });
    }
    try {
      const data = await tool.handler(parsed.data, site);
      return rpcResult(id, {
        content: [{ type: "text", text: JSON.stringify(data, null, 2) }],
        structuredContent: data,
      });
    } catch (e) {
      return rpcResult(id, {
        isError: true,
        content: [{ type: "text", text: `Tool error: ${String(e)}` }],
      });
    }
  }

  return rpcError(id ?? null, -32601, `Method not found: ${method}`);
}

export default async (req) => {
  const cors = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Mcp-Session-Id, Mcp-Protocol-Version",
  };

  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });

  const site = originFromReq(req);

  // Serve the MCP discovery card (rewritten here from /.well-known/mcp-server-card).
  let pathname = "";
  try {
    pathname = new URL(req.url).pathname;
  } catch {}
  if (pathname.includes("mcp-server-card")) {
    return Response.json(buildCard(site), {
      headers: { ...cors, "Cache-Control": "public, max-age=300" },
    });
  }

  // A plain GET returns a small human/agent-readable descriptor.
  if (req.method === "GET") {
    return Response.json(
      {
        server: SERVER_INFO,
        transport: "http (json-rpc 2.0)",
        usage: "POST a JSON-RPC 2.0 message. Start with the 'initialize' method, then 'tools/list'.",
        tools: Object.keys(TOOLS),
        card: `${site}/.well-known/mcp-server-card`,
      },
      { headers: cors }
    );
  }

  if (req.method !== "POST") {
    return new Response("Method Not Allowed", { status: 405, headers: cors });
  }

  let payload;
  try {
    payload = await req.json();
  } catch {
    return Response.json(rpcError(null, -32700, "Parse error"), { status: 400, headers: cors });
  }

  // Support JSON-RPC batches and single messages.
  if (Array.isArray(payload)) {
    const out = [];
    for (const m of payload) {
      const r = await handleRpc(m, site);
      if (r) out.push(r);
    }
    return Response.json(out, { headers: cors });
  }

  const result = await handleRpc(payload, site);
  if (result === null) return new Response(null, { status: 202, headers: cors });
  return Response.json(result, { headers: cors });
};
