#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
exec sh "$ROOT/scripts/run-engine.sh" -m adcs.plugins.cli aspose.tex.cpp \
  --catalog "$ROOT/config/product-platform-plugins.json" \
  --workspace "$ROOT/engine" \
  --python "$ROOT/plugins/tex-cpp/.venv/bin/python" "$@"
