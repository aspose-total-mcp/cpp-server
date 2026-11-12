$root = Split-Path $PSScriptRoot -Parent
& "$PSScriptRoot/run-engine.ps1" -m adcs.plugins.cli aspose.tex.cpp --catalog "$root/config/product-platform-plugins.json" --workspace "$root/engine" --python "$root/plugins/tex-cpp/.venv/Scripts/python.exe" @args
exit $LASTEXITCODE
