<#
.SYNOPSIS
    将图谱保鲜 hook 合并进 TRAE / Qoder 已有 hooks 配置（不覆盖用户其余项）。

.DESCRIPTION
    - TRAE: ~/.trae-cn/hooks.json（及 ~/.trae/hooks.json 若存在）
    - Qoder: ~/.qoder-cn/settings.json 与 ~/.qoder/settings.json 的 hooks 段
    命令一律 python <~/.claude/hooks/*.py>，不经 _editor_hook_launcher。
    已有相同脚本路径的条目则更新 timeout，不重复添加。

.EXAMPLE
    pwsh -File scripts/deploy-editor-graph-hooks.ps1
#>
#Requires -Version 5.1

$ErrorActionPreference = "Stop"
$Claude = Join-Path $env:USERPROFILE ".claude"
$Py = Join-Path $Claude "hooks"

function Get-Python {
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    throw "python not on PATH"
}

$python = Get-Python
$script = Join-Path $Claude "scripts\_merge_editor_graph_hooks.py"
& $python $script
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "  [OK] editor graph hooks merged" -ForegroundColor Green

$cliSrc = Join-Path $Claude "templates\editor-graph-hooks\graph_freshness_cli.py"
$dshTools = Join-Path $env:USERPROFILE ".dsh\tools"
$ocScripts = Join-Path $env:USERPROFILE ".config\opencode\scripts"
if (Test-Path -LiteralPath $cliSrc) {
    if (Test-Path -LiteralPath (Join-Path $env:USERPROFILE ".dsh")) {
        New-Item -ItemType Directory -Force -Path $dshTools | Out-Null
        Copy-Item -LiteralPath $cliSrc -Destination (Join-Path $dshTools "graph_freshness_cli.py") -Force
        Write-Host "  [OK] DSH tools/graph_freshness_cli.py" -ForegroundColor Green
    }
    if (Test-Path -LiteralPath (Join-Path $env:USERPROFILE ".config\opencode")) {
        New-Item -ItemType Directory -Force -Path $ocScripts | Out-Null
        Copy-Item -LiteralPath $cliSrc -Destination (Join-Path $ocScripts "graph_freshness_cli.py") -Force
        Write-Host "  [OK] OpenCode scripts/graph_freshness_cli.py" -ForegroundColor Green
        $ocPlugins = Join-Path $env:USERPROFILE ".config\opencode\plugins"
        $pluginSrc = Join-Path $Claude "templates\editor-graph-hooks\graph-freshness.ts"
        if (Test-Path -LiteralPath $pluginSrc) {
            New-Item -ItemType Directory -Force -Path $ocPlugins | Out-Null
            Copy-Item -LiteralPath $pluginSrc -Destination (Join-Path $ocPlugins "graph-freshness.ts") -Force
            Write-Host "  [OK] OpenCode plugins/graph-freshness.ts" -ForegroundColor Green
        }
        $r20Src = Join-Path $Claude "templates\editor-graph-hooks\r20_check.py"
        if (Test-Path -LiteralPath $r20Src) {
            Copy-Item -LiteralPath $r20Src -Destination (Join-Path $ocScripts "r20_check.py") -Force
            Write-Host "  [OK] OpenCode scripts/r20_check.py" -ForegroundColor Green
        }
        $vgSrc = Join-Path $Claude "templates\editor-graph-hooks\verify-gate.ts"
        if (Test-Path -LiteralPath $vgSrc) {
            Copy-Item -LiteralPath $vgSrc -Destination (Join-Path $ocPlugins "verify-gate.ts") -Force
            Write-Host "  [OK] OpenCode plugins/verify-gate.ts" -ForegroundColor Green
        }
    }
}
$r20Src = Join-Path $Claude "templates\editor-graph-hooks\r20_check.py"
if ((Test-Path -LiteralPath $r20Src) -and (Test-Path -LiteralPath (Join-Path $env:USERPROFILE ".dsh"))) {
    New-Item -ItemType Directory -Force -Path $dshTools | Out-Null
    Copy-Item -LiteralPath $r20Src -Destination (Join-Path $dshTools "r20_check.py") -Force
    Write-Host "  [OK] DSH tools/r20_check.py" -ForegroundColor Green
}

function Copy-GraphFreshnessJsonIfMissing {
    param([string]$HomeDir)
    $src = Join-Path $Claude "templates\editor-graph-hooks\graph-freshness.json"
    $dstDir = Join-Path $HomeDir "config"
    $dst = Join-Path $dstDir "graph-freshness.json"
    if ((Test-Path -LiteralPath $src) -and (Test-Path -LiteralPath $HomeDir) -and -not (Test-Path -LiteralPath $dst)) {
        New-Item -ItemType Directory -Force -Path $dstDir | Out-Null
        Copy-Item -LiteralPath $src -Destination $dst -Force
        Write-Host "  [OK] $HomeDir\config\graph-freshness.json (new)" -ForegroundColor Green
    }
}
Copy-GraphFreshnessJsonIfMissing (Join-Path $env:USERPROFILE ".dsh")
Copy-GraphFreshnessJsonIfMissing (Join-Path $env:USERPROFILE ".config\opencode")
