#!/usr/bin/env bash
set -euo pipefail

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FILE="${1:-}"
COUNT="${2:-all}"
OUT="${3:-}"

if [[ -z "$FILE" || ! -f "$FILE" ]]; then
  echo "usage: render.sh <html-file> [N|all] [out-dir]" >&2
  exit 1
fi

if [[ ! -x "$CHROME" ]]; then
  echo "error: Google Chrome not found" >&2
  exit 1
fi

ABS="$(cd "$(dirname "$FILE")" && pwd)/$(basename "$FILE")"
STEM="$(basename "${FILE%.*}")"

if [[ "$COUNT" == "all" ]]; then
  COUNT="$(grep -c '<section class="slide' "$FILE" || true)"
fi

if [[ -z "$COUNT" || "$COUNT" -lt 1 ]]; then
  echo "error: no slides found" >&2
  exit 1
fi

if [[ -z "$OUT" ]]; then
  OUT="$(dirname "$FILE")/${STEM}-png"
fi
mkdir -p "$OUT"

for i in $(seq 1 "$COUNT"); do
  target="$OUT/${STEM}_$(printf '%02d' "$i").png"
  "$CHROME" \
    --headless=new \
    --disable-gpu \
    --hide-scrollbars \
    --no-sandbox \
    --virtual-time-budget=4000 \
    --window-size=1920,1080 \
    --screenshot="$target" \
    "file://$ABS#/$i" >/dev/null 2>&1
  [[ -s "$target" ]] || { echo "error: failed to render slide $i" >&2; exit 1; }
  echo "rendered: $target"
done

echo "done: $COUNT slide(s)"
