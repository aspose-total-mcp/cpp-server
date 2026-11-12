#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
export PYTHONPATH="$ROOT/engine/src"
export ADCS_PRODUCT_PLUGIN_CATALOG="$ROOT/config/product-platform-plugins.json"
export ADCS_RETRIEVAL_PLUGIN_CATALOG="$ROOT/config/product-platform-plugins.json"
cd "$ROOT/engine"
exec "$ROOT/.venv/bin/python" "$@"
