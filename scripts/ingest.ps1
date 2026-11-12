$root = Split-Path $PSScriptRoot -Parent
& "$PSScriptRoot/run-engine.ps1" -m adcs.plugins.cli aspose.words.cpp --catalog "$root/config/product-platform-plugins.json" --workspace "$root/engine" --python "$root/plugins/words-cpp/.venv/Scripts/python.exe" @args
exit $LASTEXITCODE
