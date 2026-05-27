# Resolves Allure + Java: uses global installs or auto-downloads into tools/.

function Get-JavaHome {
    $javaCmd = Get-Command java -ErrorAction SilentlyContinue
    if ($javaCmd) {
        $javaBin = Split-Path $javaCmd.Source -Parent
        return Split-Path $javaBin -Parent
    }

    $setupJava = Join-Path $PSScriptRoot "setup_java.ps1"
    $javaExe = & $setupJava
    return Split-Path (Split-Path $javaExe -Parent) -Parent
}

function Get-AllureExecutable {
    $cmd = Get-Command allure -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }

    $Root = Split-Path -Parent $PSScriptRoot
    $ToolsDir = Join-Path $Root "tools\allure"
    if (Test-Path $ToolsDir) {
        $bat = Get-ChildItem -Path $ToolsDir -Recurse -Filter "allure.bat" -ErrorAction SilentlyContinue |
            Select-Object -First 1
        if ($bat) {
            return $bat.FullName
        }
    }

    $setup = Join-Path $PSScriptRoot "setup_allure.ps1"
    return & $setup
}

function Invoke-Allure {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$AllureArgumentList
    )

    $env:JAVA_HOME = Get-JavaHome
    $env:Path = "$env:JAVA_HOME\bin;" + $env:Path

    $exe = Get-AllureExecutable
    Write-Host "Using Java: $env:JAVA_HOME"
    Write-Host "Using Allure: $exe"
    & $exe @AllureArgumentList
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}
