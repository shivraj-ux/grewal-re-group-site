// Content negotiation: when an agent requests the homepage with
// `Accept: text/markdown`, serve the markdown rendering (index.md) instead of
// the HTML. Any other Accept value passes through to the static index.html.
//
// Bound to "/" in netlify.toml. Runs on Netlify's edge (Deno).

export default async (request, context) => {
  const accept = request.headers.get("accept") || "";

  // Only intercept an explicit markdown preference. A browser sending
  // "text/html, ... , */*" passes straight through to the normal page.
  const wantsMarkdown =
    /\btext\/markdown\b/i.test(accept) && !/\btext\/html\b/i.test(accept);

  if (!wantsMarkdown) {
    return context.next();
  }

  const md = await context.next(new Request(new URL("/index.md", request.url), request));
  const body = await md.text();

  return new Response(body, {
    status: 200,
    headers: {
      "Content-Type": "text/markdown; charset=utf-8",
      "Cache-Control": "public, max-age=3600",
      "Vary": "Accept",
    },
  });
};

export const config = { path: "/" };
