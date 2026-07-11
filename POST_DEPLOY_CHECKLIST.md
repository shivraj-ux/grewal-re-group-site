# Post-Deploy Checklist — PHASE 8

After the fix/site-audit-2026-07 branch is merged and deployed to live (https://grewalregroup.com), follow this checklist.

## Live Site Verification (Immediate)

- [ ] Visit https://grewalregroup.com → homepage loads, no 404s or broken images
- [ ] /about page loads and displays correctly
- [ ] /buy page loads and displays correctly
- [ ] Navigation shows "About" and "Buying" links pointing to new pages
- [ ] Review count shows 119 (not 123 or 117)
- [ ] Page count shows 154 (not 153 or 144)
- [ ] Stat meters animate on homepage (100+, $100M+, 119)

## 301 Redirect Verification

Test these old URLs redirect to new canonicals (should be HTTP 301):

```bash
curl -sI https://grewalregroup.com/tools/mortgage-calculator
# Should redirect to /calculators/mortgage-calculator

curl -sI https://grewalregroup.com/home-value-estimator
# Should redirect to /calculators/home-value-estimator

curl -sI https://grewalregroup.com/seller-net-proceeds-calculator
# Should redirect to /calculators/seller-net-proceeds-calculator
```

All should return `301 Moved Permanently` with correct Location header.

## Google Search Console

- [ ] Resubmit sitemap: Search Console → Sitemaps → Add sitemap → https://grewalregroup.com/sitemap.xml
- [ ] Request reindex for these high-priority paths:
  - `/` (homepage)
  - `/about` (new page)
  - `/buy` (new page)
  - Any consolidated blog URLs (if redirected in PHASE 3)

**In Search Console → URL Inspection, paste each URL and click "Request indexing"**

## Netlify Form Notifications

Verify that Netlify is sending form notifications for new form names:

- [ ] Log into Netlify → Site settings → Forms → Verified email for notifications
- [ ] Check that notifications are ON for:
  - `about-lead` (new /about form)
  - `buyer-lead` (new /buy form)
  - `calculators-hub-lead` (hub page form)
  - `communities-hub-lead` (hub page form)
- [ ] Send a test submission on /about and confirm email arrives within 5 minutes

## Subdomains (if configured per SUBDOMAIN_SETUP.md)

- [ ] Test subdomain redirects:
  - `curl -sI https://westlake.grewalregroup.com` → 301 to `/communities/west-lake-hills`
  - `curl -sI https://relocation.grewalregroup.com` → 301 to `/relocation-guide`
- [ ] Wildcard SSL certificate is active (green lock in browser)
- [ ] Verify > 10 minutes after adding domain alias (Netlify needs time to provision cert)

## Lighthouse & Performance

- [ ] Run Lighthouse on https://grewalregroup.com (homepage):
  - SEO score ≥ 95
  - Performance ≥ 70 (mobile) — may be lower if images aren't fully optimized
  - Accessibility ≥ 90
- [ ] Run Lighthouse on a blog post (e.g., /blog/westlake-hills-austin-2026)
  - SEO ≥ 95
- [ ] Run Lighthouse on a calculator page (e.g., /calculators/affordability-calculator)
  - SEO ≥ 95

(Lighthouse: Chrome DevTools → Lighthouse tab)

## Content Spot Checks (Sample 5 random pages)

Pick 5 random blog posts or pages, visit each and verify:

- [ ] Page has exactly one `<h1>` (no more, no less)
- [ ] Meta title is ≤ 60 chars
- [ ] Meta description is 150-160 chars and unique
- [ ] Canonical link present
- [ ] Images have alt text or role="presentation"
- [ ] Links to old /tools/ paths work (should 301 redirect)

## Google My Business & Profile Links

- [ ] Verify Shivraj's Google Business Profile card displays:
  - 5.0 stars, 119 reviews
  - Current address and contact
  - Business hours
- [ ] Check Zillow profile: https://www.zillow.com/profile/Shivraj%20Grewal
  - 119 reviews showing
- [ ] Check Realtor.com profile (if published)

## Analytics & Events

- [ ] GA4 is tracking (Admin → Data Streams → Check Web stream is reporting)
- [ ] Check that form submissions fire the `contact_form` event in GA
- [ ] Verify lead form submissions appear in Netlify → Analytics → Forms

## Final Sanity Check

Run the verification script:

```bash
./scripts/verify-audit-fixes.sh
```

Should output: "✓ All checks passed! Ready to ship."

## Known Issues / Defer-to-Next

These items require async work or manual review post-deploy:

- **Consent expander** (PHASE 6f): Requires Shivraj's approval. Instructions in PR description.
- **Image alt text**: May need manual review on 10-20% of blog images
- **Video content**: Not in scope for this audit
- **Accessibility testing**: Consider manual testing with keyboard + screen reader
- **Mobile app deep links**: Not in scope

## Support

If issues arise:

1. Check **Netlify Deploy Log** for build errors: Netlify → Deploys → Latest → Logs
2. Check **Netlify Function Logs** for serverless errors: Netlify → Functions → Select function
3. Check **Netlify Form Logs** for form submission errors: Netlify → Forms → Form name
4. Review **Git log** for recent commits: `git log --oneline | head -20`

Contact: Shivraj Grewal (shivraj@grewalregroup.com) or Claude Code (if debugging).

---

**Estimated time to complete checklist:** 20-30 minutes

**Date completed:** _______________
