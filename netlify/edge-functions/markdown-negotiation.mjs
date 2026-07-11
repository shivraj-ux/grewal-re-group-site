// Content negotiation: when an agent requests a page with
// `Accept: text/markdown`, serve the markdown rendering of that same page
// (a sibling .md file) instead of the HTML. Any other Accept value passes
// through to the normal static page, unchanged.
//
// Path -> markdown file:
//   /                              -> /index.md
//   /blog/                         -> /blog/index.md
//   /blog/some-post                -> /blog/some-post.md
//   /communities/tarrytown         -> /communities/tarrytown.md
//   /relocation-guide              -> /relocation-guide.md
//   /some-page.html                -> /some-page.md   (direct .html requests too)
//
// If no matching .md file has been published for a path, this falls through
// to the normal HTML page — nothing breaks for pages not yet covered.
//
// Bound broadly in netlify.toml (see [[edge_functions]]); cheap to run since
// it returns immediately unless the request explicitly prefers markdown.
// Runs on Netlify's edge (Deno).

function markdownPathFor(pathname) {
  if (pathname === "/") return "/index.md";
  if (pathname.endsWith("/")) return pathname + "index.md";
  if (pathname.endsWith(".html")) return pathname.slice(0, -".html".length) + ".md";
  if (pathname.endsWith(".md")) return pathname;
  return pathname + ".md";
}

export default async (request, context) => {
  const accept = request.headers.get("accept") || "";

  // Only intercept an explicit markdown preference. A browser sending
  // "text/html, ... , */*" passes straight through to the normal page.
  const wantsMarkdown =
    /\btext\/markdown\b/i.test(accept) && !/\btext\/html\b/i.test(accept);

  if (!wantsMarkdown) {
    return context.next();
  }

  const url = new URL(request.url);
  const mdPath = markdownPathFor(url.pathname);
  const mdUrl = new URL(mdPath, request.url);

  const md = await context.next(new Request(mdUrl, request));

  // No markdown rendering published for this path yet — serve the normal
  // page rather than a dead end.
  if (!md.ok) {
    return context.next();
  }

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

export const config = { path: "/*" };
