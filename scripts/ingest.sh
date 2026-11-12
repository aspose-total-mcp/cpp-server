#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PRODUCT=words
case "${1:-}" in
  words|tex) PRODUCT=$1; shift ;;
  ''|--*) ;;
  *) echo 'Usage: ingest.sh [words|tex] [ingestion options]' >&2; exit 2 ;;
esac
for arg in "$@"; do
  case "$arg" in
    --workspace*|--catalog*|--python*) echo 'Use the fixed deployment workspace, catalog and interpreter.' >&2; exit 2 ;;
  esac
done
exec sh "$ROOT/scripts/run-engine.sh" -m adcs.plugins.cli "aspose.$PRODUCT.cpp" \
  --catalog "$ROOT/config/product-platform-plugins.json" --workspace "$ROOT/engine" \
  --python "$ROOT/plugins/$PRODUCT-cpp/.venv/bin/python" "$@"
