param([switch]$SkipInstall)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
if ($env:OS -ne 'Windows_NT') { throw 'Windows 10/11 x64 is required. PyInstaller cannot cross-compile from Linux.' }
$Root = $PSScriptRoot
Push-Location $Root
$OldCache = $env:PIP_CACHE_DIR
$OldQt = $env:QT_QPA_PLATFORM
try {
    $env:PIP_CACHE_DIR = Join-Path $Root '.cache\pip'
    if (!(Test-Path '.venv\Scripts\python.exe')) {
        if ($env:pythonLocation -and (Test-Path (Join-Path $env:pythonLocation 'python.exe'))) {
            # actions/setup-python supplies a tool-cache interpreter, not a py-launcher registration.
            & (Join-Path $env:pythonLocation 'python.exe') -m venv .venv
        } else {
            & py -3.12 -m venv .venv
        }
        if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.12 x64 for the build machine.' }
    }
    $Python = Join-Path $Root '.venv\Scripts\python.exe'
    & $Python -c "import sys,struct; assert sys.version_info[:2]==(3,12) and struct.calcsize('P')==8"
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.12 x64 is required.' }
    if (!$SkipInstall) {
        & $Python -m pip install -r requirements-windows.txt
        if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
    }
    $env:QT_QPA_PLATFORM = 'offscreen'
    & $Python -m pytest -q --junitxml=release/windows-test-results.xml
    if ($LASTEXITCODE -ne 0) { throw 'Tests failed; release cancelled.' }
    & $Python scripts\make_icon.py
    if ($LASTEXITCODE -ne 0) { throw 'Icon generation failed.' }
    & $Python scripts\build.py --target windows
    if ($LASTEXITCODE -ne 0) { throw 'Windows build failed.' }
    & $Python scripts\verify_package.py dist\UzluksizBCMS.exe
    if ($LASTEXITCODE -ne 0) { throw 'Packaged executable verification failed.' }
    $File = Get-Item dist\UzluksizBCMS.exe
    Get-FileHash $File.FullName -Algorithm SHA256 | Format-List
    Write-Host "Windows one-file EXE: $($File.FullName) ($($File.Length) bytes)."
    Write-Host 'Automated packaged checks passed. Perform the interactive offline Windows checks in docs/WINDOWS_RELEASE.md before release sign-off.'
} finally {
    $env:PIP_CACHE_DIR = $OldCache
    $env:QT_QPA_PLATFORM = $OldQt
    Pop-Location
}
