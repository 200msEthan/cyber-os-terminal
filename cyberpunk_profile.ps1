# ============================================================================
# CYBER-OS // NEURAL POWERSHELL PROFILE (WINDOWS TERMINAL & POWERSHELL 5/7+)
# Palette: Cyberpunk Neon (Electric Cyan, Neon Magenta, Synthwave Purple)
# ============================================================================

$CyberDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:STARSHIP_CONFIG = Join-Path $CyberDir "starship.toml"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Detect python executable on Windows (python or python3)
$PythonExe = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { "python3" }

# ----------------------------------------------------------------------------
# 1. BUILT-IN SCI-FI TELEMETRY & CYBER ARSENAL FUNCTIONS
# ----------------------------------------------------------------------------
function hud          { & $PythonExe (Join-Path $CyberDir "scifi_hud.py") @args }
function cyber-watch  { & $PythonExe (Join-Path $CyberDir "scifi_hud.py") --watch @args }
function cyber-matrix { & $PythonExe (Join-Path $CyberDir "scifi_hud.py") --matrix @args }
function cyber-scan   { & $PythonExe (Join-Path $CyberDir "scifi_hud.py") --scan @args }

function cyber-tools  { & $PythonExe (Join-Path $CyberDir "cyber_tools.py") --menu @args }
function cyber-jobs   { & $PythonExe (Join-Path $CyberDir "cyber_tools.py") --jobs @args }
function cyber-conn   { & $PythonExe (Join-Path $CyberDir "cyber_tools.py") --conn @args }
function cyber-audit  { & $PythonExe (Join-Path $CyberDir "cyber_tools.py") --audit @args }
function cyber-arsenal{ & $PythonExe (Join-Path $CyberDir "cyber_tools.py") --arsenal @args }

function cyber-ports {
    param([string]$Target = "127.0.0.1", [string]$Range = "common")
    & $PythonExe (Join-Path $CyberDir "cyber_tools.py") --ports $Target --range $Range @args
}

function cyber-kill {
    param([Parameter(Mandatory=$true, Position=0)][int]$Port,
          [Parameter(ValueFromRemainingArguments=$true)][string[]]$RemainingArgs = @())
    # taskkill without /F commonly cannot stop Windows console dev servers.
    if ($RemainingArgs -notcontains "--force") {
        $RemainingArgs = @("--force") + $RemainingArgs
    }
    & $PythonExe (Join-Path $CyberDir "cyber_tools.py") --kill-port $Port @RemainingArgs
}

function cyber-recon {
    param([string]$Target = "example.com")
    & $PythonExe (Join-Path $CyberDir "cyber_tools.py") --recon $Target @args
}

function cyber-ssl {
    param([string]$Target = "github.com")
    & $PythonExe (Join-Path $CyberDir "cyber_tools.py") --ssl $Target @args
}

function cyber-headers {
    param([string]$Url = "https://github.com")
    & $PythonExe (Join-Path $CyberDir "cyber_tools.py") --headers $Url @args
}

function cyber-hash {
    param([string]$InputVal = "cyberdeck")
    & $PythonExe (Join-Path $CyberDir "cyber_tools.py") --hash $InputVal @args
}

function cyber-decode {
    param([Parameter(Mandatory=$true, Position=0)][string]$Payload,
          [Parameter(ValueFromRemainingArguments=$true)][string[]]$RemainingArgs = @())
    & $PythonExe (Join-Path $CyberDir "cyber_tools.py") --decode $Payload @RemainingArgs
}

function cyber-keygen {
    param([int]$Length = 32)
    & $PythonExe (Join-Path $CyberDir "cyber_tools.py") --keygen $Length @args
}

function cyber-fim {
    param([string]$Dir = ".")
    & $PythonExe (Join-Path $CyberDir "cyber_tools.py") --fim $Dir @args
}

function cyber-secrets {
    param([string]$Dir = ".")
    & $PythonExe (Join-Path $CyberDir "cyber_tools.py") --secrets $Dir @args
}

function cyber-nmap {
    param([string]$Target = "127.0.0.1")
    & $PythonExe (Join-Path $CyberDir "cyber_tools.py") --nmap $Target @args
}

function cyber-cam {
    & $PythonExe (Join-Path $CyberDir "cyber_vision.py") @args
}

function cyber-search {
    param([string]$Query = "cyber")
    & $PythonExe (Join-Path $CyberDir "cyber_search.py") --omni $Query
}

function cyber-find {
    param([string]$Query = "cyber", [string]$Dir = ".")
    & $PythonExe (Join-Path $CyberDir "cyber_search.py") --files $Query --dir $Dir @args
}

function cyber-history {
    param([string]$Query = "recent")
    & $PythonExe (Join-Path $CyberDir "cyber_search.py") --history $Query
}

function cyber-web {
    param([string]$Query = "cybersecurity")
    & $PythonExe (Join-Path $CyberDir "cyber_search.py") --web $Query
}

# ----------------------------------------------------------------------------
# 2. CYBERPUNK NEON PROMPT (STARSHIP OR BUILT-IN TRUECOLOR FALLBACK)
# ----------------------------------------------------------------------------
if (Get-Command starship -ErrorAction SilentlyContinue) {
    Invoke-Expression (&starship init powershell)
} else {
    function global:prompt {
        $esc = [char]27
        $cMag = "$esc[1;38;2;255;0;160m"
        $cCyan = "$esc[1;38;2;0;243;255m"
        $cPurple = "$esc[1;38;2;189;0;255m"
        $cYellow = "$esc[1;38;2;252;238;10m"
        $cBlue = "$esc[1;38;2;90;100;255m"
        $cReset = "$esc[0m"
        $user = $env:USERNAME
        $hostName = $env:COMPUTERNAME
        $cwd = (Get-Location).Path
        $timeStr = (Get-Date).ToString("HH:mm:ss")
        return "`n${cMag}╔═[${cCyan}⚡ ${user}${cPurple}@${hostName}${cMag}]═[${cYellow} ◈ ${cwd} ${cMag}]${cBlue}═[ ⌚ ${timeStr} ]${cReset}`n${cMag}╚═${cCyan}◢◤ ${cMag}❯${cReset} "
    }
}

# ----------------------------------------------------------------------------
# 3. LAUNCH CYBERPUNK STARTUP TELEMETRY HUD
# ----------------------------------------------------------------------------
if (-not $env:CYBER_HUD_SHOWN) {
    $env:CYBER_HUD_SHOWN = "1"
    & $PythonExe (Join-Path $CyberDir "scifi_hud.py") --boot
}
