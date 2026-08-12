<#
.SYNOPSIS
    Deploy Cursor Guard to ~/.cursor/ (isolated from Claude Code hooks)

.DESCRIPTION
    把 templates/cursor-guard/ 下的 hooks.json + hooks/ + guard-config.json 部署到 ~/.cursor/。
    默认增量合并 guard-config.json：模板新增键补齐，用户已有值保留，version 始终跟随模板。

.PARAMETER Force
    Overwrite guard-config.json entirely（放弃用户本地改动，整体覆盖）

.EXAMPLE
    # 全部命令（本脚本仅一个开关）
    powershell -ExecutionPolicy Bypass -File scripts/deploy-cursor-guard.ps1          # 增量合并部署
    powershell -ExecutionPolicy Bypass -File scripts/deploy-cursor-guard.ps1 -Force   # 整体覆盖配置

.NOTES
    部署后回归（必须全绿）：
      powershell -ExecutionPolicy Bypass -File scripts/test-cursor-guard-regression.ps1
      powershell -ExecutionPolicy Bypass -File scripts/test-cursor-guard-regression.ps1 -Deploy
#>
# 注意：#Requires 必须放在帮助块之后，否则 Get-Help 读不到上面的命令示例。
#Requires -Version 5.1

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
            if ($entry.command -match 'hooks[\\/]([^\\/\s"]+\.py)(.*)$') {
                $scriptName = $Matches[1]
                $tail = ($Matches[2] | ForEach-Object { $_.Trim() })
                $abs = Join-Path $HooksDir $scriptName
                if ($tail) {
                    $entry.command = "`"$pyExe`" `"$abs`" $tail"
                } else {
                    $entry.command = "`"$pyExe`" `"$abs`""
                }
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
        # v18.3 通用嵌套合并：模板中任何对象型键都逐字段补齐，用户已有值一律保留。
        # 原先 explore / verification / knowledge_graph 是同一段逻辑的三份拷贝，
        # 新增 impact / issue_tracker 等键时会被漏掉。
        foreach ($prop in $tpl.PSObject.Properties) {
            $name = $prop.Name
            if (-not $usr.PSObject.Properties.Match($name).Count) {
                $usr | Add-Member -NotePropertyName $name -NotePropertyValue $prop.Value -Force
                continue
            }
            if ($prop.Value -is [PSCustomObject] -and $usr.$name -is [PSCustomObject]) {
                foreach ($sub in $prop.Value.PSObject.Properties) {
                    if (-not $usr.$name.PSObject.Properties.Match($sub.Name).Count) {
                        $usr.$name | Add-Member -NotePropertyName $sub.Name -NotePropertyValue $sub.Value -Force
                    }
                }
            }
        }
        # Always pin off — indexing user home exhausted RAM
        if ($usr.knowledge_graph) { $usr.knowledge_graph.codebase_memory = $false }
        # version 是部署标记而非用户偏好：必须始终跟随模板。原先只在缺失时写入，
        # 导致模板升版后部署副本永远停留在旧版本（test-cursor-guard-hooks 的
        # deploy_config 用例长期不过就是这个原因）。
        $usr | Add-Member -NotePropertyName version -NotePropertyValue $tpl.version -Force
        Write-Utf8NoBom -Path $cfgDst -Content ($usr | ConvertTo-Json -Depth 8)
        Write-Ok "guard-config.json merged new keys"
    } catch {
        Write-Host "  [!!] guard-config merge failed, kept user file" -ForegroundColor Yellow
    }
}

# CURSOR-EDITOR / SSOT rules: owned by claude-config plugin only.
# Do NOT write into ~/.cursor/rules — that duplicates Always Apply in UI/Agent.
$rulesDst = Join-Path $DST "rules"
if (Test-Path $rulesDst) {
    foreach ($f in Get-ChildItem $rulesDst -File -Force -ErrorAction SilentlyContinue) {
        if ($f.BaseName -ieq "CURSOR-EDITOR") {
            Remove-Item $f.FullName -Force -ErrorAction SilentlyContinue
            Write-Fix "removed ~/.cursor/rules/$($f.Name) (use plugin claude-config)"
        }
    }
}

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
