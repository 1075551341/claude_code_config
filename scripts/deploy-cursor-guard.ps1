#Requires -Version 5.1
<#
.SYNOPSIS
    Deploy Cursor Guard to ~/.cursor/ (isolated from Claude Code hooks)

.PARAMETER Force
    Overwrite guard-config.json entirely

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts/deploy-cursor-guard.ps1
#>

param([switch]$Force)

$ErrorActionPreference = "Stop"
$CLAUDE_DIR = Join-Path $env:USERPROFILE ".claude"
$SRC = Join-Path $CLAUDE_DIR "templates\cursor-guard"
$DST = Join-Path $env:USERPROFILE ".cursor"
$HOOKS_DST = Join-Path $DST "hooks"

function Write-Ok { param($m) Write-Host "  [OK]  $m" -ForegroundColor Green }
function Write-Fix { param($m) Write-Host "  [+]  $m" -ForegroundColor Cyan }

function Write-Utf8NoBom {
    param([string]$Path, [string]$Content)
    $utf8 = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($Path, $Content, $utf8)
}

function Resolve-HookCommands {
    param($HooksJsonPath, [string]$HooksDir)
    $pyExe = (Get-Command python).Source
    $raw = Get-Content $HooksJsonPath -Raw -Encoding utf8 | ConvertFrom-Json
    foreach ($prop in $raw.hooks.PSObject.Properties) {
        foreach ($entry in @($prop.Value)) {
            if (-not $entry.command) { continue }
            if ($entry.command -match 'hooks[\\/]([^\\/\s"]+\.py)') {
                $scriptName = $Matches[1]
                $abs = Join-Path $HooksDir $scriptName
                $entry.command = "`"$pyExe`" `"$abs`""
            }
        }
    }
    Write-Utf8NoBom -Path $HooksJsonPath -Content ($raw | ConvertTo-Json -Depth 10)
}

Write-Host ""
Write-Host "  Cursor Guard deploy" -ForegroundColor Cyan
Write-Host "  src: $SRC" -ForegroundColor DarkGray
Write-Host "  dst: $DST" -ForegroundColor DarkGray
Write-Host ""

if (-not (Test-Path $SRC)) {
    Write-Host "  [XX] template missing: $SRC" -ForegroundColor Red
    exit 1
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "  [XX] python not found" -ForegroundColor Red
    exit 1
}
Write-Ok "Python: $(& python --version 2>&1)"

if (-not (Test-Path (Join-Path $CLAUDE_DIR "scripts\sync.ps1"))) {
    Write-Host "  [XX] sync.ps1 missing" -ForegroundColor Red
    exit 1
}
Write-Ok "sync.ps1 ready"

if (-not (Test-Path $DST)) {
    New-Item -ItemType Directory -Path $DST -Force | Out-Null
}

$stateDir = Join-Path $DST ".state"
if (-not (Test-Path $stateDir)) {
    New-Item -ItemType Directory -Path $stateDir -Force | Out-Null
}

# hooks/ (before hooks.json so Resolve can point at real files)
if (Test-Path $HOOKS_DST) { Remove-Item $HOOKS_DST -Recurse -Force }
Copy-Item (Join-Path $SRC "hooks") $HOOKS_DST -Recurse -Force
Write-Fix "hooks/ ($((Get-ChildItem $HOOKS_DST -Recurse -File).Count) files)"

Copy-Item (Join-Path $SRC "hooks.json") (Join-Path $DST "hooks.json") -Force
Resolve-HookCommands -HooksJsonPath (Join-Path $DST "hooks.json") -HooksDir $HOOKS_DST
Write-Fix "hooks.json (absolute script paths)"

# guard-config
$cfgSrc = Join-Path $SRC "guard-config.json"
$cfgDst = Join-Path $DST "guard-config.json"
if (-not (Test-Path $cfgDst) -or $Force) {
    Copy-Item $cfgSrc $cfgDst -Force
    Write-Fix "guard-config.json"
} else {
    try {
        $tpl = Get-Content $cfgSrc -Raw -Encoding utf8 | ConvertFrom-Json
        $usr = Get-Content $cfgDst -Raw -Encoding utf8 | ConvertFrom-Json
        foreach ($prop in $tpl.PSObject.Properties) {
            if (-not $usr.PSObject.Properties.Match($prop.Name).Count) {
                $usr | Add-Member -NotePropertyName $prop.Name -NotePropertyValue $prop.Value -Force
            }
        }
        # Nested merge: explore.enforce_mode (v10.5 soft_block)
        if ($tpl.explore) {
            if (-not $usr.explore) {
                $usr | Add-Member -NotePropertyName explore -NotePropertyValue $tpl.explore -Force
            } else {
                foreach ($ep in $tpl.explore.PSObject.Properties) {
                    if (-not $usr.explore.PSObject.Properties.Match($ep.Name).Count) {
                        $usr.explore | Add-Member -NotePropertyName $ep.Name -NotePropertyValue $ep.Value -Force
                    }
                }
            }
        }
        if (-not $usr.version) { $usr | Add-Member -NotePropertyName version -NotePropertyValue $tpl.version -Force }
        Write-Utf8NoBom -Path $cfgDst -Content ($usr | ConvertTo-Json -Depth 8)
        Write-Ok "guard-config.json merged new keys"
    } catch {
        Write-Host "  [!!] guard-config merge failed, kept user file" -ForegroundColor Yellow
    }
}

# CURSOR-EDITOR.mdc — 先删同类型同名变体，再写入（与 sync.ps1 L0 部署一致）
$rulesDst = Join-Path $DST "rules"
if (-not (Test-Path $rulesDst)) {
    New-Item -ItemType Directory -Path $rulesDst -Force | Out-Null
}
$ceSrc = Join-Path $SRC "rules\CURSOR-EDITOR.mdc"
$ceDst = Join-Path $rulesDst "CURSOR-EDITOR.mdc"
foreach ($f in Get-ChildItem $rulesDst -File -Force -ErrorAction SilentlyContinue) {
    if ($f.BaseName -ieq "CURSOR-EDITOR") { Remove-Item $f.FullName -Force }
}
Copy-Item $ceSrc $ceDst -Force
Write-Fix "rules/CURSOR-EDITOR.mdc (delete-then-write)"

# .cursorignore merge
$ignoreSrc = Join-Path $SRC "dot-cursorignore"
$ignoreDst = Join-Path $DST ".cursorignore"
if (Test-Path $ignoreSrc) {
    $newLines = Get-Content $ignoreSrc -Encoding utf8 | Where-Object { $_.Trim() -ne "" }
    if (-not (Test-Path $ignoreDst)) {
        $newLines | Set-Content $ignoreDst -Encoding utf8
        Write-Fix ".cursorignore created"
    } else {
        $existing = Get-Content $ignoreDst -Encoding utf8
        $added = 0
        foreach ($line in $newLines) {
            if ($existing -notcontains $line) {
                Add-Content $ignoreDst $line -Encoding utf8
                $added++
            }
        }
        Write-Ok ".cursorignore merged ($added new lines)"
    }
}

$templateHooks = Get-Content (Join-Path $DST "hooks.json") -Raw -Encoding utf8 | ConvertFrom-Json
$hookCount = 0
foreach ($prop in $templateHooks.hooks.PSObject.Properties) {
    $hookCount += @($prop.Value).Count
}

Write-Host ""
Write-Host "  Deployed $hookCount hooks (guard_version=$($templateHooks.guard_version))" -ForegroundColor Green
Write-Host "  Hook commands use absolute paths under $HOOKS_DST" -ForegroundColor DarkGray
Write-Host "  Restart Cursor -> Settings -> Hooks" -ForegroundColor DarkGray
Write-Host "  Regression: powershell -ExecutionPolicy Bypass -File $CLAUDE_DIR\scripts\test-cursor-guard-regression.ps1" -ForegroundColor DarkGray
Write-Host ""
