$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$product = 'words'
$forward = @($args)
if ($forward.Count -gt 0 -and $forward[0] -in @('words','tex')) {
    $product = $forward[0]
    $forward = @($forward | Select-Object -Skip 1)
} elseif ($forward.Count -gt 0 -and -not $forward[0].StartsWith('--')) {
    throw 'Usage: ingest.ps1 [words|tex] [ingestion options]'
}
foreach ($argument in $forward) {
    if ($argument -match '^--(workspace|catalog|python)') {
        throw 'Use the fixed deployment workspace, catalog and interpreter.'
    }
}
& "$PSScriptRoot/run-engine.ps1" -m adcs.plugins.cli "aspose.$product.cpp" --catalog "$root/config/product-platform-plugins.json" --workspace "$root/engine" --python "$root/plugins/$product-cpp/.venv/Scripts/python.exe" @forward
exit $LASTEXITCODE
