#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
for argument in "$@"; do
  case "$argument" in --workspace*|--catalog*|--python*) echo 'Use fixed deployment arguments.' >&2; exit 2;; --source-kind*) echo 'Omit --source-kind: this command ingests Words docs plus examples.' >&2; exit 2;; esac
done
"$ROOT/.venv/bin/python" "$ROOT/scripts/prepare_cpp_examples.py"
exec sh "$ROOT/scripts/ingest.sh" words --source-kind docs "$@"
