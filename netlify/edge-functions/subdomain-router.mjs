// Subdomain router for Netlify edge functions
// Maps *.grewalregroup.com subdomains to canonical paths
// Usage: Wire in netlify.toml with path "/*"

// Subdomain map generated from sitemap.xml (see data/subdomain-map.json)
// This should be updated at build time or loaded from data/subdomain-map.json
const SUBDOMAIN_MAP = {
  'westlake': '/communities/west-lake-hills',
  'tarrytown': '/communities/tarrytown',
  'bartoncreek': '/communities/barton-creek',
  'relocation': '/relocation-guide',
  'schools': '/austin-schools-guide',
  'calculators': '/calculators',
  'reviews': '/reviews',
  'about': '/about',
  'buy': '/buy',
  'contact': '/contact',
  'blog': '/blog/',
  'communities': '/communities/',
  'faq': '/faq'
};

export default async (request, context) => {
  const url = new URL(request.url);
  const host = url.hostname;

  // Skip if it's the main domain (not a subdomain)
  if (host === 'grewalregroup.com' || host === 'www.grewalregroup.com' || /^\d+\.\d+\.\d+\.\d+$/.test(host)) {
    return context.next();
  }

  // Extract subdomain (first part of hostname)
  const subdomain = host.split('.')[0];

  // Look up in subdomain map
  const targetPath = SUBDOMAIN_MAP[subdomain];

  if (targetPath) {
    // Found a mapping, redirect to the canonical URL with 301
    const redirectUrl = `https://grewalregroup.com${targetPath}`;
    return new Response(null, {
      status: 301,
      headers: {
        'Location': redirectUrl,
        'Cache-Control': 'public, max-age=86400'
      }
    });
  }

  // Unknown subdomain, redirect to homepage with 301
  return new Response(null, {
    status: 301,
    headers: {
      'Location': 'https://grewalregroup.com/',
      'Cache-Control': 'public, max-age=86400'
    }
  });
};
