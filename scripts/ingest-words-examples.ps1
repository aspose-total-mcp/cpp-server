$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
foreach ($argument in $args) {
    if ($argument -like '--source-kind*') { throw 'This command ingests Words documentation plus examples; omit --source-kind.' }
}
& "$root/.venv/Scripts/python.exe" "$PSScriptRoot/prepare_cpp_examples.py"
if ($LASTEXITCODE -ne 0) { throw 'C++ example preparation failed.' }
& "$PSScriptRoot/ingest.ps1" --source-kind docs @args
exit $LASTEXITCODE
