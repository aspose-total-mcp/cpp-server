$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$env:PYTHONPATH = Join-Path $root 'engine/src'
$env:PYTHONUTF8 = '1'
$env:ADCS_PRODUCT_PLUGIN_CATALOG = Join-Path $root 'config/product-platform-plugins.json'
$env:ADCS_RETRIEVAL_PLUGIN_CATALOG = $env:ADCS_PRODUCT_PLUGIN_CATALOG
Push-Location (Join-Path $root 'engine')
try {
    & (Join-Path $root '.venv/Scripts/python.exe') @args
    $code = $LASTEXITCODE
} finally { Pop-Location }
exit $code
