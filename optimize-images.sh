#!/usr/bin/env bash
# optimize-images.sh — Grewal RE Group landing page
# ═════════════════════════════════════════════════
# Compresses and resizes the asset folder for web delivery.
# Uses macOS built-in `sips` (no installs needed).
#
# WHAT IT DOES:
#   1. Backs up assets/ → assets-original-backup/
#   2. Resizes any JPG wider than 1920px down to 1920px max width
#   3. Recompresses JPGs at quality 78 (visually identical, ~10x smaller)
#   4. Reports before/after sizes
#
# EXPECTED SAVINGS:
#   Before: ~140 MB across assets/images + assets/listings
#   After:  ~6–10 MB total (15–20× smaller)
#   Page load time impact: 4 MB hero image → 250 KB (~16× faster on mobile)
#
# USAGE:
#   bash optimize-images.sh           # dry-run, prints what it would do
#   bash optimize-images.sh --run     # actually compress
#
# REVERSAL:
#   rm -rf assets && mv assets-original-backup assets

set -e
cd "$(dirname "$0")"

DRY_RUN=true
if [ "$1" = "--run" ]; then DRY_RUN=false; fi

# ── Config ──────────────────────────────────────────────────
MAX_WIDTH=1920
JPEG_QUALITY=78
TARGETS=(
  "assets/images"
  "assets/listings"
  "assets/headshots"
)

# ── Backup ──────────────────────────────────────────────────
if [ "$DRY_RUN" = false ] && [ ! -d "assets-original-backup" ]; then
  echo "📦 Backing up assets/ → assets-original-backup/"
  cp -R assets assets-original-backup
fi

# ── Helpers ─────────────────────────────────────────────────
human() {
  awk -v b="$1" 'BEGIN{
    if (b > 1048576) printf "%.1f MB", b/1048576;
    else if (b > 1024) printf "%.0f KB", b/1024;
    else printf "%d B", b;
  }'
}

before_total=0
after_total=0

for dir in "${TARGETS[@]}"; do
  [ ! -d "$dir" ] && continue
  echo ""
  echo "── $dir ─────────────────────────────"

  while IFS= read -r -d '' f; do
    before=$(stat -f%z "$f")
    before_total=$((before_total + before))

    if [ "$DRY_RUN" = true ]; then
      printf "  WOULD COMPRESS  %s  (%s)\n" "$(basename "$f")" "$(human "$before")"
      continue
    fi

    # Resize if wider than MAX_WIDTH
    width=$(sips -g pixelWidth "$f" 2>/dev/null | tail -1 | awk '{print $2}')
    if [ "$width" -gt "$MAX_WIDTH" ] 2>/dev/null; then
      sips --resampleWidth "$MAX_WIDTH" "$f" >/dev/null 2>&1
    fi

    # Recompress JPG
    sips -s format jpeg -s formatOptions "$JPEG_QUALITY" "$f" --out "$f" >/dev/null 2>&1

    after=$(stat -f%z "$f")
    after_total=$((after_total + after))
    saved=$((before - after))
    pct=$((saved * 100 / before))
    printf "  ✓ %s  %s → %s  (-%d%%)\n" "$(basename "$f")" "$(human "$before")" "$(human "$after")" "$pct"
  done < <(find "$dir" -type f \( -iname "*.jpg" -o -iname "*.jpeg" \) -print0)
done

echo ""
echo "═══════════════════════════════════════════════════"
if [ "$DRY_RUN" = true ]; then
  echo "DRY RUN — no files modified."
  echo "Total bytes that would be processed: $(human "$before_total")"
  echo ""
  echo "Run for real:  bash optimize-images.sh --run"
else
  saved_total=$((before_total - after_total))
  pct_total=$((saved_total * 100 / before_total))
  echo "DONE."
  echo "  Before: $(human "$before_total")"
  echo "  After:  $(human "$after_total")"
  echo "  Saved:  $(human "$saved_total")  ($pct_total%)"
  echo ""
  echo "Backup at: assets-original-backup/"
  echo "To revert: rm -rf assets && mv assets-original-backup assets"
fi
