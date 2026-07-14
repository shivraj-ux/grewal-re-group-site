#!/usr/bin/env bash
#
# submit-indexnow.sh — notify IndexNow (Bing, Yandex, and other participating
# search engines) that one or more URLs on grewalregroup.com were added,
# changed, or deleted, so they can be picked up immediately instead of
# waiting for the next crawl.
#
# THIS IS NOT AUTOMATIC. It is not wired into the deploy pipeline
# (.github/workflows/netlify-deploy.yml). Run it by hand every time you
# publish a new page, edit an existing page, or remove a page — after the
# deploy has actually gone live, not before.
#
# Usage:
#   ./submit-indexnow.sh https://grewalregroup.com/blog/some-post
#   ./submit-indexnow.sh https://grewalregroup.com/buy https://grewalregroup.com/sell
#   ./submit-indexnow.sh -f urls.txt      # one URL per line
#
# NOTE: www.grewalregroup.com 301-redirects to the bare apex grewalregroup.com
# (confirmed 2026-07-14) — that's the canonical host used in this site's
# sitemap.xml and canonical tags. Submit apex URLs, not www ones.
#
set -euo pipefail

HOST="grewalregroup.com"
KEY="e6de7aae7f18449186579a0b292e63ee"
KEY_LOCATION="https://grewalregroup.com/e6de7aae7f18449186579a0b292e63ee.txt"
ENDPOINT="https://api.indexnow.org/IndexNow"

usage() {
  echo "Usage: $0 <url> [<url> ...]" >&2
  echo "       $0 -f <file-of-urls>" >&2
  exit 1
}

if [ "$#" -eq 0 ]; then
  usage
fi

urls=()
if [ "$1" = "-f" ]; then
  if [ -z "${2:-}" ]; then
    usage
  fi
  file="$2"
  if [ ! -f "$file" ]; then
    echo "Error: file not found: $file" >&2
    exit 1
  fi
  while IFS= read -r line || [ -n "$line" ]; do
    line="$(echo "$line" | xargs)"  # trim whitespace
    [ -z "$line" ] && continue
    urls+=("$line")
  done < "$file"
else
  urls=("$@")
fi

if [ "${#urls[@]}" -eq 0 ]; then
  echo "Error: no URLs to submit." >&2
  exit 1
fi

# Build the JSON urlList array.
url_json=""
for u in "${urls[@]}"; do
  if [ -n "$url_json" ]; then
    url_json="${url_json},"
  fi
  url_json="${url_json}\"${u}\""
done

payload=$(cat <<EOF
{
  "host": "${HOST}",
  "key": "${KEY}",
  "keyLocation": "${KEY_LOCATION}",
  "urlList": [${url_json}]
}
EOF
)

echo "Submitting ${#urls[@]} URL(s) to IndexNow..."
for u in "${urls[@]}"; do
  echo "  - $u"
done

http_code=$(curl -s -o /tmp/indexnow-response.txt -w "%{http_code}" \
  -X POST "$ENDPOINT" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "Host: api.indexnow.org" \
  -d "$payload")

echo ""
echo "HTTP response code: $http_code"

case "$http_code" in
  200)
    echo "200 = Accepted. IndexNow received the submission."
    ;;
  202)
    echo "202 = Accepted, key validation is pending (some endpoints use this instead of 200)."
    ;;
  400)
    echo "400 = Bad request. The JSON body was malformed or a required field was missing."
    ;;
  403)
    echo "403 = Forbidden. The key file was not found at keyLocation, or its contents don't match the key. Check: $KEY_LOCATION"
    ;;
  422)
    echo "422 = Unprocessable. One or more URLs don't belong to the host ($HOST), or the URL list is otherwise invalid."
    ;;
  429)
    echo "429 = Too many requests. You're being rate-limited — wait before retrying."
    ;;
  *)
    echo "Unrecognized response code. Raw response body:"
    cat /tmp/indexnow-response.txt
    ;;
esac

rm -f /tmp/indexnow-response.txt
