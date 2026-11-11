# ============================================================================
# CYBER-OS // ONE-CLICK WINDOWS POWERSHELL INSTALLER
# Usage (in PowerShell):
#   powershell -ExecutionPolicy Bypass -File .\install.ps1
#   powershell -ExecutionPolicy Bypass -File .\install.ps1 -Packages
#   powershell -ExecutionPolicy Bypass -File .\install.ps1 -Uninstall
# ============================================================================
param(
    [switch]$Packages,
    [switch]$Uninstall
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProfileFile = $PROFILE
$ProfileDir = Split-Path -Parent $ProfileFile
$MarkerBegin = "# >>> CYBER-OS SCI-FI TERMINAL >>>"
$MarkerEnd = "# <<< CYBER-OS SCI-FI TERMINAL <<<"

if (-not (Test-Path $ProfileDir)) {
    New-Item -ItemType Directory -Path $ProfileDir -Force | Out-Null
}
if (-not (Test-Path $ProfileFile)) {
    New-Item -ItemType File -Path $ProfileFile -Force | Out-Null
}

function Remove-CyberBlock {
    $content = Get-Content $ProfileFile -Raw -ErrorAction SilentlyContinue
    if ($content -and $content.Contains($MarkerBegin)) {
        $pattern = "(?s)\r?\n?$([regex]::Escape($MarkerBegin)).*?$([regex]::Escape($MarkerEnd))"
        $newContent = [regex]::Replace($content, $pattern, "")
        Set-Content -Path $ProfileFile -Value $newContent -Encoding UTF8
    }
}

if ($Uninstall) {
    Remove-CyberBlock
    Write-Host "✔ Uninstalled Cyber-OS Terminal from $ProfileFile" -ForegroundColor Green
    exit 0
}

Remove-CyberBlock
$HookBlock = @"

$MarkerBegin
if (Test-Path "$ScriptDir\cyberpunk_profile.ps1") {
    . "$ScriptDir\cyberpunk_profile.ps1"
}
$MarkerEnd
"@

Add-Content -Path $ProfileFile -Value $HookBlock -Encoding UTF8
Write-Host "✔ Configured PowerShell Profile: $ProfileFile" -ForegroundColor Cyan

if ($Packages -and (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "❖ Installing Starship, Nmap & CLI tools via winget..." -ForegroundColor Magenta
    winget install --id Starship.Starship -e --silent
    winget install --id Insecure.Nmap -e --silent
}

. "$ScriptDir\cyberpunk_profile.ps1"
Write-Host "`n✔ INSTALLATION COMPLETE! Restart PowerShell / Windows Terminal or run: . `$PROFILE" -ForegroundColor Green
