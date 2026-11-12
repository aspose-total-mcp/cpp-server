#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"
# Do not recurse into the engine's historical documentation submodules.
git submodule sync -- engine plugins/words-cpp plugins/tex-cpp
git submodule update --init engine plugins/words-cpp plugins/tex-cpp
# The inherited source registry expects these roots even before corpus setup.
mkdir -p "$ROOT/engine/source-repo-docs" "$ROOT/engine/source-repo-apiref"
PYTHON=${PYTHON:-python3.12}
"$PYTHON" -m venv "$ROOT/.venv"
"$ROOT/.venv/bin/python" -m pip install -e "$ROOT/engine"
"$PYTHON" -m venv --without-pip "$ROOT/plugins/words-cpp/.venv"
"$PYTHON" -m venv --without-pip "$ROOT/plugins/tex-cpp/.venv"
"$ROOT/.venv/bin/python" "$ROOT/scripts/verify_registration.py"
