# View Allure report — auto-downloads Allure CLI + portable JRE if not installed.

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\allure_cli.ps1"

$Root = Split-Path -Parent $PSScriptRoot
$Results = Join-Path $Root "reports\allure-results"

if (-not (Test-Path $Results)) {
    Write-Error "No Allure results at $Results. Run 'pytest' first."
}

Write-Host "Serving Allure report from $Results ..."
Write-Host "(First run may download Allure + Java - one-time setup, ~80 MB)"
Invoke-Allure -AllureArgumentList @("serve", $Results)
