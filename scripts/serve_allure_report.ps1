# View the latest Allure report from reports/allure-results (auto-installs CLI if needed).

$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "view_allure_report.ps1")
