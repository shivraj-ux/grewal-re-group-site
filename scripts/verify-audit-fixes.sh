#!/bin/bash
# PHASE 8: Verify audit fixes before shipping
# Run after all PHASE 1-7 changes are complete

set -e
cd "$(dirname "$0")/.."

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PHASE 8: Verification Checks"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

PASS=0
FAIL=0

check() {
  local name="$1"
  local cmd="$2"
  echo -n "✓ $name ... "
  if eval "$cmd" > /dev/null 2>&1; then
    echo "PASS"
    ((PASS++))
  else
    echo "FAIL"
    ((FAIL++))
  fi
}

# 1. No stray Finder-copy files
echo ""
echo "File Integrity Checks:"
check "No Finder-copy files" '! grep -r "\\* 2\\.html" . --include="*.html" --exclude-dir=.git'
check "No tools/ directory" '! test -d tools'
check "No root home-value-estimator.html" '! test -f home-value-estimator.html'
check "No root seller-net-proceeds-calculator.html" '! test -f seller-net-proceeds-calculator.html'

# 2. Sitemap matches disk
echo ""
echo "Sitemap Validation:"
check "Sitemap XML is valid" 'xmllint --noout sitemap.xml'

# 3. Review counts unified (119)
echo ""
echo "Fact Unification Checks:"
check "Review count unified to 119" '! grep -r "123\|117" . --include="*.html" --include="*.mjs" --exclude-dir=archive --exclude-dir=.git | grep -i "review\|rating"'
check "Page count unified to 154" '! grep -r "144\|153" . --include="*.html" --exclude-dir=archive --exclude-dir=.git | grep -i "page\|relocation"'

# 4. Schema validation
echo ""
echo "Schema & Structure Checks:"
check "Homepage has exactly one h1" '[ $(grep -o "<h1" index.html | wc -l) -eq 1 ]'
check "About page has exactly one h1" '[ $(grep -o "<h1" about.html | wc -l) -eq 1 ]'
check "Buy page has exactly one h1" '[ $(grep -o "<h1" buy.html | wc -l) -eq 1 ]'

check "All JSON-LD blocks are valid JSON" '! grep -r "<script type=\"application/ld+json\"" . --include="*.html" --exclude-dir=archive -A 50 | grep -o "{.*}" | while read json; do echo "$json" | jq empty 2>/dev/null || exit 1; done'

# 5. Canonicals and titles
echo ""
echo "SEO Checks:"
check "Homepage has canonical" 'grep -q "rel=\"canonical\"" index.html'
check "About page has canonical" 'grep -q "rel=\"canonical\"" about.html'
check "Buy page has canonical" 'grep -q "rel=\"canonical\"" buy.html'

check "Titles are ≤ 60 chars" '! find . -name "*.html" -type f ! -path "./archive/*" -exec grep -l "<title>" {} \; | xargs -I {} sh -c '\''grep "<title>" {} | sed "s/<[^>]*>//g" | wc -c | awk "{if (\$1 > 65) print {} }"'\'' | grep -q "."'

check "Descriptions are 100-165 chars" '! find . -name "*.html" -type f ! -path "./archive/*" ! -path "./.git/*" -exec grep -l "<meta name=\"description\"" {} \; | while read f; do grep "name=\"description\"" "$f" | sed "s/.*content=\"//;s/\".*//" | awk "{if (length < 100 || length > 165) print \"$f: \" length}"; done | grep -q "."'

# 6. No broken internal links to deleted files
echo ""
echo "Link Integrity Checks:"
check "No links to /tools/" '! grep -r "href=\"/tools/" . --include="*.html" --exclude-dir=.git'
check "No links to deleted root calculators" '! grep -r "href=\"/home-value-estimator\|href=\"/seller-net-proceeds" . --include="*.html" --exclude-dir=.git'

# 7. No competitor domains
echo ""
echo "Content Policy Checks:"
check "No Team Price references" '! grep -ri "teamprice\|team price" . --include="*.html" --include="*.mjs" --exclude-dir=.git --exclude-dir=archive'
check "No Orchard references" '! grep -ri "orchard\\.com" . --include="*.html" --include="*.mjs" --exclude-dir=.git --exclude-dir=archive'
check "No Kumara Wilcoxon references" '! grep -ri "kumarawilcoxon" . --include="*.html" --include="*.mjs" --exclude-dir=.git --exclude-dir=archive'

check "No em dashes in new pages" '! grep -E "—" about.html buy.html'

# 8. New pages exist and are in sitemap
echo ""
echo "New Pages Checks:"
check "About page exists" 'test -f about.html'
check "Buy page exists" 'test -f buy.html'
check "About in sitemap" 'grep -q "grewalregroup.com/about" sitemap.xml'
check "Buy in sitemap" 'grep -q "grewalregroup.com/buy" sitemap.xml'

# 9. Redirect shadowing fixed
echo ""
echo "Redirect Checks:"
check "_redirects has forced rules" 'grep -q "301!" _redirects'
check "Relocation guide in redirects" 'grep -q "/relocation-guide" _redirects'

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Results: $PASS passed, $FAIL failed"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $FAIL -eq 0 ]; then
  echo "✓ All checks passed! Ready to ship."
  exit 0
else
  echo "✗ $FAIL checks failed. Review above and fix before shipping."
  exit 1
fi
