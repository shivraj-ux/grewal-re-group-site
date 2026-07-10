// Grewal RE Group — Lead intake automation.
//
// Netlify fires this function automatically on every VERIFIED form submission
// (the special "submission-created" event — no dashboard webhook needed).
// It pushes the lead into:
//   1. Notion  → "Lead Tracker" database (Source = Website, Status = New)
//   2. Airtable → a "Website Leads" table (optional)
//   3. Notion  → a comment on the new lead page = your notification
//
// Required env (Netlify → Site settings → Environment variables):
//   NOTION_TOKEN        Internal integration token; share the integration with
//                       the "Lead Tracker" database in Notion.
//   NOTION_LEADS_DB_ID  The Lead Tracker database ID (set in Netlify env vars).
// Optional env:
//   AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE (default "Website Leads")
//   NOTION_NOTIFY_PAGE_ID  Extra page to drop a "🔔 new lead" note onto.
//
// Nothing here throws on a missing integration — each sink is best-effort so a
// lead is never lost just because one destination is unconfigured.
//
// Optional env for email:
//   RESEND_API_KEY   API key from resend.com — add in Netlify site env vars.
//                    Free tier: 3,000 emails/month. Sending domain must be
//                    verified in Resend, or use onboarding@resend.dev for testing.
//   RESEND_FROM      "From" address, e.g. "Grewal RE Group <leads@grewalregroup.com>"
//                    Defaults to "leads@grewalregroup.com" if not set.
//   LEAD_EMAIL       Destination address. Defaults to shivraj.grewal@compass.com.

const NOTION_DB = process.env.NOTION_LEADS_DB_ID;
const NOTION_VERSION = "2022-06-28";

const INTEREST_MAP = [
  [/buy|purchase|home ?search|first.?time/i, "Buy"],
  [/sell|list(ing)?|valuation|home ?value/i, "Sell"],
  [/lease|rent/i, "Lease"],
  [/invest|portfolio|rental|flip/i, "Invest"],
];

function mapInterest(raw = "") {
  for (const [re, val] of INTEREST_MAP) if (re.test(raw)) return val;
  return "Unknown";
}

async function toNotion(lead) {
  const token = process.env.NOTION_TOKEN;
  if (!token) return { skipped: "no NOTION_TOKEN" };
  const props = {
    Name: { title: [{ text: { content: lead.name || "Website inquiry" } }] },
    Source: { select: { name: "Website" } },
    Status: { select: { name: "New" } },
    Interest: { select: { name: lead.interest } },
    "Last Contact": { date: { start: lead.iso } },
  };
  if (lead.email) props.Email = { email: lead.email };
  if (lead.phone) props.Phone = { phone_number: lead.phone };
  if (lead.notes) props.Notes = { rich_text: [{ text: { content: lead.notes.slice(0, 1900) } }] };

  const res = await fetch("https://api.notion.com/v1/pages", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Notion-Version": NOTION_VERSION,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ parent: { database_id: NOTION_DB }, properties: props }),
  });
  const json = await res.json();
  if (!res.ok) throw new Error(`Notion ${res.status}: ${JSON.stringify(json).slice(0, 300)}`);

  // Notification: a comment on the new lead page surfaces in your Notion feed.
  await fetch("https://api.notion.com/v1/comments", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Notion-Version": NOTION_VERSION,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      parent: { page_id: json.id },
      rich_text: [{ text: { content:
        `🔔 New website lead — ${lead.name || "?"} · ${lead.interest} · ${lead.email || ""} ${lead.phone || ""}`.trim() } }],
    }),
  }).catch(() => {});

  if (process.env.NOTION_NOTIFY_PAGE_ID) {
    await fetch("https://api.notion.com/v1/blocks/" + process.env.NOTION_NOTIFY_PAGE_ID + "/children", {
      method: "PATCH",
      headers: {
        Authorization: `Bearer ${token}`,
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ children: [{ object: "block", type: "callout", callout: {
        icon: { emoji: "🔔" },
        rich_text: [{ text: { content:
          `New website lead: ${lead.name || "?"} (${lead.interest}) — ${lead.email || ""} ${lead.phone || ""} · ${lead.page}` } }],
      } }] }),
    }).catch(() => {});
  }
  return { ok: true, pageId: json.id };
}

async function toEmail(lead) {
  const key = process.env.RESEND_API_KEY;
  if (!key) return { skipped: "no RESEND_API_KEY" };

  const from = process.env.RESEND_FROM || "leads@grewalregroup.com";
  const to = process.env.LEAD_EMAIL || "shivraj.grewal@compass.com";

  const lines = [
    `Name: ${lead.name || "(not provided)"}`,
    `Email: ${lead.email || "(not provided)"}`,
    `Phone: ${lead.phone || "(not provided)"}`,
    `Interest: ${lead.interest}`,
    `Page: ${lead.page}`,
    lead.notes ? `Notes:\n${lead.notes}` : null,
    `Submitted: ${lead.iso}`,
  ].filter(Boolean).join("\n");

  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      from,
      to,
      subject: `New lead: ${lead.name || "Website visitor"} (${lead.interest})`,
      text: `New website lead\n\n${lines}\n\n---\nSent from grewalregroup.com`,
    }),
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Resend ${res.status}: ${err.slice(0, 300)}`);
  }
  return { ok: true };
}

async function toAirtable(lead) {
  const { AIRTABLE_TOKEN, AIRTABLE_BASE_ID } = process.env;
  if (!AIRTABLE_TOKEN || !AIRTABLE_BASE_ID) return { skipped: "no Airtable env" };
  const table = encodeURIComponent(process.env.AIRTABLE_TABLE || "Website Leads");
  const res = await fetch(`https://api.airtable.com/v0/${AIRTABLE_BASE_ID}/${table}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${AIRTABLE_TOKEN}`, "Content-Type": "application/json" },
    body: JSON.stringify({ typecast: true, fields: {
      Name: lead.name, Email: lead.email, Phone: lead.phone,
      Interest: lead.interest, Source: "Website", Status: "New",
      Notes: lead.notes, Page: lead.page, Submitted: lead.iso,
    } }),
  });
  if (!res.ok) throw new Error(`Airtable ${res.status}: ${(await res.text()).slice(0, 300)}`);
  return { ok: true };
}

export const handler = async (event) => {
  let data = {};
  let formName = "";
  let page = "";
  try {
    const body = JSON.parse(event.body || "{}");
    const sub = body.payload || body;
    data = sub.data || {};
    formName = sub.form_name || data["form-name"] || "";
    page = sub.path || data.page || "";
  } catch {
    return { statusCode: 400, body: "bad payload" };
  }

  // Newsletter signups: capture email only, still as a Website lead.
  const lead = {
    name: data.name || data["full-name"] || "",
    email: data.email || "",
    phone: data.phone || "",
    notes: [data.message, data.interest && `Interest: ${data.interest}`, formName && `Form: ${formName}`]
      .filter(Boolean).join("\n"),
    interest: mapInterest(data.interest || data.message || formName),
    page: page || formName,
    iso: new Date().toISOString(),
  };

  const results = {};
  for (const [k, fn] of [["notion", toNotion], ["airtable", toAirtable], ["email", toEmail]]) {
    try { results[k] = await fn(lead); }
    catch (e) { results[k] = { error: String(e.message || e) }; }
  }
  console.log("lead-intake", JSON.stringify({ lead: { ...lead, notes: undefined }, results }));
  return { statusCode: 200, body: JSON.stringify(results) };
};
