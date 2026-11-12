#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
for argument in "$@"; do
  case "$argument" in --source-kind*) echo 'Omit --source-kind: this command ingests Words docs plus examples.' >&2; exit 2;; esac
done
"$ROOT/.venv/bin/python" "$ROOT/scripts/prepare_cpp_examples.py"
exec sh "$ROOT/scripts/run-engine.sh" -m adcs.plugins.cli aspose.words.cpp \
  --catalog "$ROOT/config/product-platform-plugins.json" --workspace "$ROOT/engine" \
  --python "$ROOT/plugins/words-cpp/.venv/bin/python" --source-kind docs "$@"
