# Downloads Allure Commandline into tools/allure (no Scoop or global install required).

$ErrorActionPreference = "Stop"

$AllureVersion = "2.34.0"
$Root = Split-Path -Parent $PSScriptRoot
$ToolsDir = Join-Path $Root "tools"
$ZipPath = Join-Path $ToolsDir "allure-$AllureVersion.zip"
$InstallDir = Join-Path $ToolsDir "allure"
$AllureHome = Join-Path $InstallDir "allure-$AllureVersion"
$AllureBat = Join-Path $AllureHome "bin\allure.bat"

function Find-AllureBat {
    if (Test-Path $AllureBat) { return $AllureBat }
    $found = Get-ChildItem -Path $InstallDir -Recurse -Filter "allure.bat" -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($found) { return $found.FullName }
    return $null
}

$existing = Find-AllureBat
if ($existing) {
    Write-Host "Allure CLI already installed: $existing"
    return $existing
}

Write-Host "Downloading Allure $AllureVersion ..."
New-Item -ItemType Directory -Force -Path $ToolsDir | Out-Null

$Url = "https://github.com/allure-framework/allure2/releases/download/$AllureVersion/allure-$AllureVersion.zip"
Invoke-WebRequest -Uri $Url -OutFile $ZipPath -UseBasicParsing

Write-Host "Extracting to $InstallDir ..."
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
# tar handles long paths better than Expand-Archive on Windows
tar -xf $ZipPath -C $InstallDir
Remove-Item $ZipPath -Force

$AllureBat = Find-AllureBat
if (-not $AllureBat) {
    Write-Error "Allure install failed. Expected allure.bat under $InstallDir"
}

Write-Host "Allure CLI ready: $AllureBat"
return $AllureBat
