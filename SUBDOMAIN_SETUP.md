# Subdomain Setup for Grewal RE Group

After this branch is merged to main and deployed, follow these steps to enable subdomain routing.

## Overview

Subdomains will redirect via 301 to their canonical pages. Examples:
- `westlake.grewalregroup.com` → `https://grewalregroup.com/communities/west-lake-hills`
- `tarrytown.grewalregroup.com` → `https://grewalregroup.com/communities/tarrytown`
- `relocation.grewalregroup.com` → `https://grewalregroup.com/relocation-guide`

## Prerequisites

1. The site is already deployed to Netlify at `grewalregroup.com`
2. Netlify DNS is managing the domain (check: Site settings → Domain management)
3. You have admin access to the Netlify dashboard

## Manual Steps in Netlify Dashboard

### Step 1: Configure Netlify DNS

1. Go to **Netlify Dashboard** → **Sites** → **grewal-re-group-site**
2. Click **Site settings** → **Domain management** → **Custom domains**
3. Verify that **Netlify DNS** is active (not external DNS provider)
   - If external: migrate to Netlify DNS first (this requires DNS record updates)

### Step 2: Add Wildcard Domain

1. In **Domain management**, click **Add domain alias**
2. Enter: `*.grewalregroup.com`
3. Click **Verify**
4. Netlify will show a DNS check — verify passes automatically once nameservers point to Netlify DNS

### Step 3: Enable Edge Function

1. Go to **Site settings** → **Functions**
2. Enable **Edge Functions** (may be under Beta features)
3. Verify that `subdomain-router.mjs` is deployed and visible in the functions list

### Step 4: Wire Edge Function in netlify.toml

The netlify.toml file should have this section (verify it's present after deploy):

```toml
[[edge_functions]]
path = "/*"
function = "subdomain-router"
```

If not present, add it and deploy again.

### Step 5: Provision Wildcard Certificate

1. Netlify automatically provisions wildcard SSL certificates for `*.grewalregroup.com` once the domain alias is added
2. This may take 5-15 minutes
3. Check **Site settings** → **Domain management** → **SSL/TLS certificates**
4. You should see a certificate for `*.grewalregroup.com` with status "Active"

## Verification

After setup is complete, test these URLs in a browser (should all redirect to canonical paths):

- `https://westlake.grewalregroup.com` → `/communities/west-lake-hills`
- `https://tarrytown.grewalregroup.com` → `/communities/tarrytown`
- `https://bartoncreek.grewalregroup.com` → `/communities/barton-creek`
- `https://relocation.grewalregroup.com` → `/relocation-guide`
- `https://schools.grewalregroup.com` → `/austin-schools-guide`
- `https://calculators.grewalregroup.com` → `/calculators`

All should return HTTP 301 (permanent redirect) to the canonical URL.

## Troubleshooting

**DNS not resolving**: Ensure Netlify DNS is active and propagated (up to 48 hours globally, usually 5-15 minutes)

**Certificate not provisioning**: Wait 15 minutes after adding the domain alias. Netlify provisions certificates on a schedule.

**Edge function not running**: Verify `netlify.toml` has the `[[edge_functions]]` block and redeploy.

**Redirect not working**: Check Netlify function logs (Site settings → Functions → subdomain-router) for errors.

## Subdomain Map

The current subdomain redirects are defined in `netlify/edge-functions/subdomain-router.mjs`. To add more subdomains or change mappings, update the `SUBDOMAIN_MAP` object in that file and redeploy.

Full list of available subdomains is in `data/subdomain-map.json` (generated from sitemap.xml).
