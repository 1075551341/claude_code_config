#Requires -Version 5.1
<#
.SYNOPSIS
    修复 Windows 上 `claude` 命令反复失效，并保证 GitHub MCP 本地二进制存在。

.DESCRIPTION
    根因（会反复出现）：
    1. Volta/npm 全局安装 @anthropic-ai/claude-code 后，shim 指向
       ...\bin\claude.exe；Claude 自更新会把 exe 改名为 claude.exe.old.*，
       新文件写不进 Volta image，于是 cmd 报「不是内部或外部命令」。
    2. User PATH 里 Volta/npm-prefix 排在 ~/.local\bin 前面，native 安装
       永远抢不过坏掉的 shim。
    3. GitHub 远端 https://api.githubcopilot.com/mcp/ 在 Cursor/Claude 里
       走 OAuth，只暴露 mcp_auth、0 tools；PAT 实际可用，应改本地 stdio。

    本脚本可重复执行（幂等）：卸 Volta/npm shim、保证 ~/.local\bin 在 User
    PATH 最前、缺 native 则跑官方安装器、关闭 Claude 自动更新（DISABLE_AUTOUPDATER）、
    同步 GITHUB_PERSONAL_ACCESS_TOKEN、缺 github-mcp-server.exe 则下载官方 Windows 包。

.PARAMETER DiagnoseOnly
    只诊断，不改 PATH / 不卸载 / 不下载。

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts/fix-claude-cli.ps1
    powershell -ExecutionPolicy Bypass -File scripts/fix-claude-cli.ps1 -DiagnoseOnly
#>
param([switch]$DiagnoseOnly)

Set-StrictMode -Off
$ErrorActionPreference = 'Continue'

$LocalBin = Join-Path $env:USERPROFILE '.local\bin'
$VoltaHome = if ($env:VOLTA_HOME) { $env:VOLTA_HOME } else { 'D:\config_sys\dev-cache\volta' }
$NpmPrefix = 'D:\config_sys\dev-cache\npm-prefix'
$NativeExe = Join-Path $LocalBin 'claude.exe'
$GhMcpExe = Join-Path $LocalBin 'github-mcp-server.exe'
$GhMcpVersion = 'v1.9.0'

function Write-Step([string]$t) {
    Write-Host ""
    Write-Host "=== $t ===" -ForegroundColor Cyan
}

function Test-Pe([string]$path) {
    if (-not (Test-Path -LiteralPath $path)) { return $false }
    try {
        $b = [System.IO.File]::ReadAllBytes($path)
        return ($b.Length -ge 2 -and $b[0] -eq 0x4D -and $b[1] -eq 0x5A)
    } catch { return $false }
}

function Get-ClaudeResolution {
    $cmd = Get-Command claude -ErrorAction SilentlyContinue
    if (-not $cmd) { return $null }
    return [string]$cmd.Source
}

Write-Host ""
Write-Host "Claude CLI + GitHub MCP repair" -ForegroundColor Cyan
Write-Host ("Mode: " + $(if ($DiagnoseOnly) { 'diagnose-only' } else { 'fix' })) -ForegroundColor DarkGray

# --- diagnose ---
Write-Step 'Diagnose'
$src = Get-ClaudeResolution
Write-Host ("claude -> " + $(if ($src) { $src } else { '(not found)' }))
Write-Host ("native PE = " + (Test-Pe $NativeExe) + "  path=" + $NativeExe)
Write-Host ("volta shim = " + (Test-Path (Join-Path $VoltaHome 'bin\claude.cmd')))
Write-Host ("npm-prefix shim = " + (Test-Path (Join-Path $NpmPrefix 'claude.cmd')))
Write-Host ("github-mcp-server PE = " + (Test-Pe $GhMcpExe))

$ghToken = [Environment]::GetEnvironmentVariable('GITHUB_TOKEN', 'User')
$ghPat = [Environment]::GetEnvironmentVariable('GITHUB_PERSONAL_ACCESS_TOKEN', 'User')
Write-Host ("GITHUB_TOKEN User = " + $(if ($ghToken) { "present len=$($ghToken.Length)" } else { 'MISSING' }))
Write-Host ("GITHUB_PERSONAL_ACCESS_TOKEN User = " + $(if ($ghPat) { "present len=$($ghPat.Length) same=$( $ghPat -eq $ghToken )" } else { 'MISSING' }))

$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
$head = ($userPath -split ';' | Select-Object -First 1)
Write-Host ("User PATH head = " + $head)

$auStatus = ''
$auEnv = ''
try {
    $so = Get-Content (Join-Path $env:USERPROFILE '.claude\settings.json') -Raw -Encoding utf8 | ConvertFrom-Json
    $auStatus = [string]$so.autoUpdaterStatus
    if ($so.env) { $auEnv = [string]$so.env.DISABLE_AUTOUPDATER }
} catch {}
Write-Host ("autoUpdaterStatus=" + $auStatus)
Write-Host ("settings DISABLE_AUTOUPDATER=" + $auEnv)
Write-Host ("User DISABLE_AUTOUPDATER=" + [Environment]::GetEnvironmentVariable('DISABLE_AUTOUPDATER', 'User'))

if ($DiagnoseOnly) { return }

# --- PATH: ~/.local/bin first ---
Write-Step 'User PATH: ~/.local/bin first'
$parts = @($userPath -split ';' | Where-Object { $_ -and $_.Trim() -ne '' })
$norm = $LocalBin.TrimEnd('\')
$parts = @($parts | Where-Object { $_.TrimEnd('\') -ne $norm })
$newPath = (@($LocalBin) + $parts) -join ';'
[Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
if (-not $env:PATH.StartsWith($LocalBin + ';')) {
    $env:PATH = $LocalBin + ';' + (($env:PATH -split ';' | Where-Object { $_.TrimEnd('\') -ne $norm }) -join ';')
}
Write-Host 'done'

# --- drop Volta/npm shims ---
Write-Step 'Remove Volta / npm-prefix claude shims'
if (Get-Command volta -ErrorAction SilentlyContinue) {
    volta uninstall claude 2>&1 | Out-Null
    volta uninstall '@anthropic-ai/claude-code' 2>&1 | Out-Null
}
$shimTargets = @(
    (Join-Path $VoltaHome 'bin\claude'),
    (Join-Path $VoltaHome 'bin\claude.cmd'),
    (Join-Path $VoltaHome 'tools\user\bins\claude.json'),
    (Join-Path $VoltaHome 'tools\user\packages\@anthropic-ai'),
    (Join-Path $NpmPrefix 'claude'),
    (Join-Path $NpmPrefix 'claude.cmd'),
    (Join-Path $NpmPrefix 'claude.ps1'),
    (Join-Path $NpmPrefix 'node_modules\@anthropic-ai\claude-code')
)
foreach ($t in $shimTargets) {
    if (Test-Path $t) {
        Remove-Item $t -Recurse -Force
        Write-Host ("removed " + $t)
    }
}

# --- native claude ---
Write-Step 'Native claude.exe'
if (Test-Pe $NativeExe) {
    Write-Host ("already present: " + $NativeExe)
} else {
    Write-Host 'running official installer (irm https://claude.ai/install.ps1)'
    $ProgressPreference = 'SilentlyContinue'
    irm https://claude.ai/install.ps1 | iex
}
if (-not (Test-Pe $NativeExe)) {
    Write-Host 'ERROR: native claude.exe still missing' -ForegroundColor Red
    exit 1
}
& $NativeExe --version

# --- GitHub PAT alias ---
Write-Step 'GITHUB_PERSONAL_ACCESS_TOKEN'
if ($ghToken) {
    if ($ghPat -ne $ghToken) {
        [Environment]::SetEnvironmentVariable('GITHUB_PERSONAL_ACCESS_TOKEN', $ghToken, 'User')
        $env:GITHUB_PERSONAL_ACCESS_TOKEN = $ghToken
        Write-Host 'synced from GITHUB_TOKEN (User)'
    } else {
        Write-Host 'already synced'
    }
} else {
    Write-Host 'WARN: GITHUB_TOKEN missing at User scope; GitHub MCP will have no tools' -ForegroundColor Yellow
}

# --- github-mcp-server ---
Write-Step 'github-mcp-server.exe'
if (Test-Pe $GhMcpExe) {
    Write-Host ("already present: " + $GhMcpExe)
    & $GhMcpExe --version
} else {
    New-Item -ItemType Directory -Path $LocalBin -Force | Out-Null
    $tmp = Join-Path $env:TEMP 'github-mcp-server-install'
    if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
    New-Item -ItemType Directory -Path $tmp -Force | Out-Null
    Write-Host ("downloading github/github-mcp-server " + $GhMcpVersion)
    gh release download --repo github/github-mcp-server --pattern 'github-mcp-server_Windows_x86_64.zip' --dir $tmp --clobber
    Expand-Archive -Path (Join-Path $tmp 'github-mcp-server_Windows_x86_64.zip') -DestinationPath $tmp -Force
    $found = Get-ChildItem $tmp -Recurse -Filter 'github-mcp-server.exe' | Select-Object -First 1
    if (-not $found) { throw 'github-mcp-server.exe not in zip' }
    Copy-Item $found.FullName $GhMcpExe -Force
    Remove-Item $tmp -Recurse -Force
    & $GhMcpExe --version
}

# --- disable CLI auto-update (native updater renaming claude.exe is the recurrence) ---
Write-Step 'Disable Claude auto-update'
[Environment]::SetEnvironmentVariable('DISABLE_AUTOUPDATER', '1', 'User')
[Environment]::SetEnvironmentVariable('FORCE_AUTOUPDATE_PLUGINS', '1', 'User')
$env:DISABLE_AUTOUPDATER = '1'
$env:FORCE_AUTOUPDATE_PLUGINS = '1'
Write-Host 'User env DISABLE_AUTOUPDATER=1 FORCE_AUTOUPDATE_PLUGINS=1'

$py = @'
import json
from pathlib import Path
p = Path.home() / ".claude" / "settings.json"
data = json.loads(p.read_text(encoding="utf-8"))
env = data.setdefault("env", {})
changed = False
if env.get("DISABLE_AUTOUPDATER") != "1":
    env["DISABLE_AUTOUPDATER"] = "1"
    changed = True
if env.get("FORCE_AUTOUPDATE_PLUGINS") != "1":
    env["FORCE_AUTOUPDATE_PLUGINS"] = "1"
    changed = True
if data.get("autoUpdaterStatus") != "disabled":
    data["autoUpdaterStatus"] = "disabled"
    changed = True
if data.get("autoUpdatesChannel") != "stable":
    data["autoUpdatesChannel"] = "stable"
    changed = True
if changed:
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("settings.json patched")
else:
    print("settings.json already disabled")
'@
$pyFile = Join-Path $env:TEMP 'patch-claude-noupdate.py'
Set-Content -Path $pyFile -Value $py -Encoding UTF8
& python $pyFile
Remove-Item $pyFile -Force -ErrorAction SilentlyContinue

Write-Step 'Verify'
where.exe claude 2>&1 | Select-Object -First 3 | ForEach-Object { Write-Host $_ }
claude --version
Write-Host ""
Write-Host 'OK. Fully quit Cursor and Claude Code, then reopen so MCP hosts pick up PATH + PAT.' -ForegroundColor Green
Write-Host 'Auto-update is OFF (DISABLE_AUTOUPDATER=1). Do not run claude update / npm i -g / volta install claude-code.' -ForegroundColor Yellow
Write-Host ""
