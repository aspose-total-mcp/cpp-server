param([string]$Python = 'py')
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Push-Location $root
try {
    git submodule sync -- engine plugins/words-cpp plugins/tex-cpp
    if ($LASTEXITCODE -ne 0) { throw 'Submodule sync failed.' }
    git submodule update --init engine plugins/words-cpp plugins/tex-cpp
    if ($LASTEXITCODE -ne 0) { throw 'Submodule initialization failed.' }
    New-Item -ItemType Directory -Force engine/source-repo-docs,engine/source-repo-apiref | Out-Null
    $pythonArgs = @()
    if ($Python -eq 'py') { $pythonArgs = @('-3.12') }
    & $Python @pythonArgs -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Engine environment creation failed.' }
    & ./.venv/Scripts/python.exe -m pip install -e ./engine
    if ($LASTEXITCODE -ne 0) { throw 'Engine installation failed.' }
    & $Python @pythonArgs -m venv --without-pip plugins/words-cpp/.venv
    if ($LASTEXITCODE -ne 0) { throw 'Plugin environment creation failed.' }
    & $Python @pythonArgs -m venv --without-pip plugins/tex-cpp/.venv
    if ($LASTEXITCODE -ne 0) { throw 'TeX plugin environment creation failed.' }
    & ./.venv/Scripts/python.exe scripts/verify_registration.py
    if ($LASTEXITCODE -ne 0) { throw 'Registration verification failed.' }
} finally { Pop-Location }
