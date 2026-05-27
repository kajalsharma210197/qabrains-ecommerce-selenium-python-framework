# Downloads a portable JRE (Temurin 17) into tools/jre for running Allure CLI.

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$ToolsDir = Join-Path $Root "tools"
$JreDir = Join-Path $ToolsDir "jre"
$ZipPath = Join-Path $ToolsDir "jre.zip"

function Find-JavaExe {
    if (-not (Test-Path $JreDir)) { return $null }
    $java = Get-ChildItem -Path $JreDir -Recurse -Filter "java.exe" -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -match "\\bin\\java\.exe$" } |
        Select-Object -First 1
    if ($java) { return $java.FullName }
    return $null
}

$existing = Find-JavaExe
if ($existing) {
    Write-Host "Portable JRE already installed: $existing"
    return $existing
}

Write-Host "Downloading portable JRE (Temurin 17) ..."
New-Item -ItemType Directory -Force -Path $ToolsDir | Out-Null

$Url = "https://api.adoptium.net/v3/binary/latest/17/ga/windows/x64/jre/hotspot/normal/eclipse?project=jdk"
Invoke-WebRequest -Uri $Url -OutFile $ZipPath -UseBasicParsing

Write-Host "Extracting JRE to $JreDir ..."
if (Test-Path $JreDir) {
    Remove-Item -Recurse -Force $JreDir
}
New-Item -ItemType Directory -Force -Path $JreDir | Out-Null
tar -xf $ZipPath -C $JreDir
Remove-Item $ZipPath -Force

$javaExe = Find-JavaExe
if (-not $javaExe) {
    Write-Error "JRE install failed. Expected java.exe under $JreDir"
}

Write-Host "Portable JRE ready: $javaExe"
return $javaExe
