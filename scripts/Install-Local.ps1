param(
    [string]$InstallRoot = (Join-Path $env:LOCALAPPDATA 'OutlookClassicMCP'),
    [string]$UvPath,
    [string]$PythonPath
)
$ErrorActionPreference = 'Stop'
$sourceRoot = Split-Path -Parent $PSScriptRoot
$InstallRoot = [IO.Path]::GetFullPath($InstallRoot)
$userLocal = [IO.Path]::GetFullPath($env:LOCALAPPDATA).TrimEnd('\') + '\'
if (-not $InstallRoot.StartsWith($userLocal, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'InstallRoot must be below this user LocalAppData. No administrator installation is supported.'
}
$wheel = @(Get-ChildItem -LiteralPath (Join-Path $sourceRoot 'dist') -Filter 'outlook_classic_mcp-*.whl')
if ($wheel.Count -ne 1) { throw 'Expected exactly one reviewed wheel in dist. Build it before installation.' }
$hashFile = Join-Path $sourceRoot 'dist\SHA256SUMS.txt'
$expected = ((Get-Content -LiteralPath $hashFile | Where-Object { $_.EndsWith($wheel[0].Name) }) -split '\s+')[0]
if (-not $expected -or (Get-FileHash -LiteralPath $wheel[0].FullName -Algorithm SHA256).Hash -ne $expected) {
    throw 'Wheel checksum mismatch'
}
New-Item -ItemType Directory -Path $InstallRoot -Force | Out-Null
$env:UV_CACHE_DIR = Join-Path $InstallRoot 'uv-cache'
$env:UV_LINK_MODE = 'copy'
if (-not $UvPath) {
    $existing = Get-Command uv -ErrorAction SilentlyContinue
    if ($existing) { $UvPath = $existing.Source }
}
if (-not $UvPath) {
    $toolDir = Join-Path $InstallRoot 'tools'
    New-Item -ItemType Directory -Path $toolDir -Force | Out-Null
    $UvPath = Join-Path $toolDir 'uv.exe'
    if (-not (Test-Path -LiteralPath $UvPath)) {
        $archive = Join-Path $toolDir 'uv-0.13.6.zip'
        Invoke-WebRequest 'https://github.com/astral-sh/uv/releases/download/0.13.6/uv-x86_64-pc-windows-msvc.zip' -OutFile $archive -UseBasicParsing
        if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash -ne 'a2a8820d5eea32f08ef467ef3b7f66883a9b076d5737a2fc2fbb5f458d1bb50f') {
            throw 'uv checksum mismatch'
        }
        Expand-Archive -LiteralPath $archive -DestinationPath $toolDir
    }
}
if (-not $PythonPath) {
    $runtime = Join-Path $InstallRoot 'python'
    & $UvPath python install --install-dir $runtime --no-bin --no-registry 3.12.16
    if ($LASTEXITCODE -ne 0) { throw 'Python installation failed. Do not bypass Windows protections.' }
    $PythonPath = Join-Path $runtime 'cpython-3.12.16-windows-x86_64-none\python.exe'
}
& $PythonPath -c "import sys; assert sys.version_info[:3] == (3,12,16), 'Expected Python 3.12.16'; assert sys.maxsize > 2**32, 'Expected x64 Python'"
if ($LASTEXITCODE -ne 0) { throw 'Python runtime check failed' }
$venv = Join-Path $InstallRoot 'venv'
$python = Join-Path $venv 'Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    & $UvPath venv --python $PythonPath $venv
    if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed' }
}
& $UvPath pip sync --python $python --require-hashes (Join-Path $sourceRoot 'requirements.lock')
if ($LASTEXITCODE -ne 0) { throw 'Locked dependency installation failed' }
& $UvPath pip install --python $python --no-deps --reinstall-package outlook-classic-mcp $wheel[0].FullName
if ($LASTEXITCODE -ne 0) { throw 'Reviewed package installation failed' }
& $python -c "import outlook_mcp, pythoncom; print('Installed',outlook_mcp.__version__)"
if ($LASTEXITCODE -ne 0) { throw 'Package import check failed' }
Copy-Item -LiteralPath (Join-Path $sourceRoot 'requirements.lock') -Destination (Join-Path $InstallRoot 'requirements.lock') -Force
Write-Output "Installed for current user: $InstallRoot"
Write-Output 'No MCP configuration, account, task or startup service was changed. Next: prepare_codex_config.py.'
