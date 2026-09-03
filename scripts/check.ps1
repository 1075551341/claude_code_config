<#
.SYNOPSIS
    快速诊断（<5秒）— 检查关键文件和目录存在性

.DESCRIPTION
    轻量级健康检查，验证文件/目录存在、基本格式。
    深度校验（冲突检测、R16扫描、完整验证）→ scripts/validate_config.py。
    设计原则：check.ps1 = 快速诊断；validate_config.py = 深度校验。
    S2  配置文件（格式与安全）
    S3  软链接 / 同步状态
    S4  Hook 安全（死循环风险 / 超时 / Stop Hook）
    S5  Python / Node.js / Git / Docker
    S6  MCP 相关连通性（可选）
    S7  工具箱统计
    S8  得分与汇总

.PARAMETER Quick
    跳过 MCP 连通性测试（更快完成）

.EXAMPLE
    # 全部命令（本脚本仅一个开关）
    pwsh -ExecutionPolicy Bypass -File scripts/check.ps1           # 完整诊断，含 MCP 连通性（PS5.1 回退用 powershell）
    pwsh -ExecutionPolicy Bypass -File scripts/check.ps1 -Quick    # 跳过 MCP 探测，最快

.NOTES
    配套命令（本脚本不代跑，按需单独执行）：
      python scripts/validate_config.py            # 深度校验 V1-V20
      pwsh -File scripts/sync.ps1                # 修同步/软链问题
      pwsh -File scripts/fix.ps1 -Fix            # 修 hook launcher 问题
#>
# 注意：#Requires 必须放在帮助块之后，否则 PowerShell 不会把上面的块识别为
# comment-based help，Get-Help 将读不到这些命令示例。
#Requires -Version 5.1

param([switch]$Quick)

Set-StrictMode -Off
$ErrorActionPreference = "SilentlyContinue"

function Resolve-ClaudeDir {
    if ($env:CLAUDE_HOME -and (Test-Path (Join-Path $env:CLAUDE_HOME "CLAUDE.md"))) {
        return $env:CLAUDE_HOME
    }
    $repo = Split-Path $PSScriptRoot -Parent
    if (Test-Path (Join-Path $repo "CLAUDE.md")) { return $repo }
    $up = $env:USERPROFILE
    if (-not $up) { $up = $env:HOME }
    return (Join-Path $up ".claude")
}

$CLAUDE_DIR = Resolve-ClaudeDir
# 根文件集合与编辑器清单单源：config/sync-manifest.json（与 sync.ps1 / impact_sync.py 共用）；读取失败回退内置默认
$SYNC_FILES = @("CLAUDE.md", "SPEC.md", "MANIFEST.yaml", "skills-INDEX.md", "agents-INDEX.md", "rules-INDEX.md")
# v11.1 多编辑器（1+N）：managed 编辑器白名单（cursor 走专用校验块；下表为其余编辑器）
$MANAGED_EDITORS = [ordered]@{
    "qoder-cn"  = @{ Home = "$env:USERPROFILE\.qoder-cn";     Enabled = $true; RulesChannel = "rules";      RulesExt = ".mdc"; RootIndex = $true;  Special = "" }
    "trae-cn"   = @{ Home = "$env:USERPROFILE\.trae-cn";      Enabled = $true; RulesChannel = "user_rules"; RulesExt = ".md";  RootIndex = $true;  Special = "" }
    "workbuddy" = @{ Home = "$env:USERPROFILE\.workbuddy";    Enabled = $true; RulesChannel = "";           RulesExt = "";     RootIndex = $false; Special = "claude_md_plus_skills" }
    "qoder"     = @{ Home = "$env:USERPROFILE\.qoder";        Enabled = $true; RulesChannel = "rules";      RulesExt = ".mdc"; RootIndex = $true;  Special = "" }
    "trae"      = @{ Home = "$env:USERPROFILE\.trae";         Enabled = $true; RulesChannel = "user_rules"; RulesExt = ".md";  RootIndex = $true;  Special = "" }
    "codearts"  = @{ Home = "$env:USERPROFILE\.codeartsdoer"; Enabled = $true; RulesChannel = "rule";       RulesExt = ".mdc"; RootIndex = $true;  Special = "" }
    "opencode"  = @{ Home = "$env:USERPROFILE\.config\opencode"; Enabled = $false; RulesChannel = "";       RulesExt = "";     RootIndex = $false; Special = "agents_md" }
}
$syncManifestPath = Join-Path $CLAUDE_DIR "config\sync-manifest.json"
if (Test-Path $syncManifestPath) {
    try {
        $syncMf = Get-Content $syncManifestPath -Raw -Encoding utf8 | ConvertFrom-Json
        if ($syncMf.root_files) { $SYNC_FILES = @($syncMf.root_files) }
        if ($syncMf.editors) {
            $MANAGED_EDITORS = [ordered]@{}
            foreach ($e in $syncMf.editors.PSObject.Properties) {
                if ($e.Name -eq "_comment" -or $e.Name -eq "cursor") { continue }
                $v = $e.Value
                $MANAGED_EDITORS[$e.Name] = @{
                    Home         = ("$($v.home)" -replace '^~', $env:USERPROFILE -replace '/', '\')
                    Enabled      = ($v.enabled -ne $false)
                    RulesChannel = "$(if ($v.rules_channel) { $v.rules_channel } else { '' })"
                    RulesExt     = "$(if ($v.rules_ext) { $v.rules_ext } else { '' })"
                    RootIndex    = ($v.root_index -eq $true)
                    Special      = "$(if ($v.special) { $v.special } else { '' })"
                }
            }
        }
    } catch { }
}
$STALE_LINKS = @("hooks", "scripts")

$results   = [System.Collections.Generic.List[hashtable]]::new()
$passCount = 0
$warnCount = 0
$failCount = 0

function Add-Check {
    param([string]$Cat, [string]$Item, [string]$Status, [string]$Detail = "")
    $results.Add(@{ Cat = $Cat; Item = $Item; Status = $Status; Detail = $Detail })
    switch ($Status) {
        "pass" { $script:passCount++; Write-Host "   [OK]  $Item" -ForegroundColor Green   -NoNewline }
        "warn" { $script:warnCount++; Write-Host "   [!!]  $Item" -ForegroundColor Yellow  -NoNewline }
        "fail" { $script:failCount++; Write-Host "   [XX]  $Item" -ForegroundColor Red     -NoNewline }
    }
    if ($Detail) { Write-Host " -- $Detail" -ForegroundColor DarkGray } else { Write-Host "" }
}

function Write-Section { param($n, $t) Write-Host ""; Write-Host "  S$n  $t" -ForegroundColor Green; Write-Host "  $('='*50)" -ForegroundColor DarkGray }

# v11 曾移除 Get-EditorSettingsPath；v11.1 S3 改为 manifest 驱动的 managed 白名单循环，
# 落点校验直接用 home 路径拼接，无需该函数。

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  Claude Code Environment Check v3.2" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  Dir : $CLAUDE_DIR" -ForegroundColor DarkGray
Write-Host "  Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor DarkGray
if ($Quick) { Write-Host "  Mode: Quick (MCP connectivity tests skipped)" -ForegroundColor Yellow }

# =============================================================
# S1: Directory structure
# =============================================================
Write-Section 1 "Directory Structure"

$requiredDirs = @(
    @{ P = "skills";      D = "Skills library" }
    @{ P = "agents";      D = "Agent configs" }
    @{ P = "rules";       D = "Rules" }
    @{ P = "hooks";       D = "Hook scripts" }
    @{ P = "scripts";     D = "Tool scripts" }
    @{ P = "logs";        D = "Logs" }
    # experiences/ 已于 v11 归档至 docs/archive/experiences/（学习产物统一 claude-mem）
    # plans/ 已于 v10.17 移出版本库（计划/设计为本地制品，见 .gitignore），不再作为必备目录
    @{ P = "backups";     D = "Backups" }
)

foreach ($d in $requiredDirs) {
    $fp = Join-Path $CLAUDE_DIR $d.P
    if (Test-Path $fp) {
        $cnt = (Get-ChildItem $fp -Recurse -File -EA SilentlyContinue).Count
        Add-Check "Dir" "$($d.D) ($($d.P)/)" "pass" "$cnt files"
    } else {
        Add-Check "Dir" "$($d.D) ($($d.P)/)" "warn" "directory missing"
    }
}

# =============================================================
# S2: Config files
# =============================================================
Write-Section 2 "Config Files"

$settingsPath = Join-Path $CLAUDE_DIR "settings.json"
$mcpPath      = Join-Path $CLAUDE_DIR ".mcp.json"
$settingsObj  = $null

$configFiles = @(
    @{ P = "settings.json"; D = "CLI full config";     R = $true }
    @{ P = ".mcp.json";     D = "MCP server config";   R = $true }
    @{ P = "CLAUDE.md";    D = "Global behavior doc"; R = $false }
)

foreach ($f in $configFiles) {
    $fp = Join-Path $CLAUDE_DIR $f.P
    if (Test-Path $fp) {
        $kb = [math]::Round((Get-Item $fp).Length / 1KB, 1)
        Add-Check "Config" $f.D "pass" "$($f.P) (${kb}KB)"
    } else {
        Add-Check "Config" $f.D (if ($f.R) { "fail" } else { "warn" }) "$($f.P) missing"
    }
}

# Parse settings.json
if (Test-Path $settingsPath) {
    try {
        $settingsObj = Get-Content $settingsPath -Raw -Encoding utf8 | ConvertFrom-Json
        $fields = @()
        if ($settingsObj.hooks)       { $fields += "hooks" }
        if ($settingsObj.permissions) { $fields += "permissions" }
        if ($settingsObj.mcpServers)  {
            $mc = ($settingsObj.mcpServers | Get-Member -MemberType NoteProperty).Count
            $fields += "mcpServers($mc)"
        }
        if ($settingsObj.env)   { $fields += "env" }
        if ($settingsObj.model) { $fields += "model=$($settingsObj.model)" }
        Add-Check "Config" "settings.json format" "pass" "fields: $($fields -join ', ')"
    } catch {
        Add-Check "Config" "settings.json format" "fail" "JSON parse failed"
    }
}

# Parse .mcp.json
if (Test-Path $mcpPath) {
    try {
        $mcpObj = Get-Content $mcpPath -Raw -Encoding utf8 | ConvertFrom-Json
        $cnt    = ($mcpObj.mcpServers | Get-Member -MemberType NoteProperty -EA SilentlyContinue).Count
        Add-Check "Config" ".mcp.json format" "pass" "$cnt MCP servers configured"
    } catch {
        Add-Check "Config" ".mcp.json format" "fail" "JSON parse failed"
    }
}

# =============================================================
# S3: Sync status (v11.1 multi-editor: 1+N)
# =============================================================
Write-Section 3 "Sync Status (v11.1 multi-editor: 1+N)"

function Test-IsReparseLink {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return $false }
    return [bool]((Get-Item $Path -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)
}

$cursorDir = Join-Path $env:USERPROFILE ".cursor"
if (-not (Test-Path $cursorDir)) {
    Add-Check "Symlink" ".cursor" "warn" "~/.cursor not found -- Cursor not installed?"
} else {
    $issues = @()
    $passes = 0

    foreach ($file in $SYNC_FILES) {
        $fp = Join-Path $cursorDir $file
        $expected = Join-Path $CLAUDE_DIR $file
        if (-not (Test-Path $fp)) {
            $issues += "$file(missing)"
        } elseif (Test-IsReparseLink $fp) {
            $actual = (Get-Item $fp -Force).Target
            if ($actual -is [array]) { $actual = $actual[0] }
            if ($actual -eq $expected) { $passes++ } else { $issues += "$file(wrong target)" }
        } else {
            # symlink 不可用时回退 Copy-Item — 内容一致视为通过
            try {
                $h1 = (Get-FileHash $fp -Algorithm SHA256).Hash
                $h2 = (Get-FileHash $expected -Algorithm SHA256).Hash
                if ($h1 -eq $h2) { $passes++ } else { $issues += "$file(stale copy)" }
            } catch { $issues += "$file(not a link)" }
        }
    }

    # skills/ agents/ junction（-Skills/-All 部署；存在则校验指向）
    foreach ($dir in @("skills", "agents")) {
        $lp = Join-Path $cursorDir $dir
        $et = Join-Path $CLAUDE_DIR $dir
        if (Test-IsReparseLink $lp) {
            $actual = (Get-Item $lp -Force).Target
            if ($actual -is [array]) { $actual = $actual[0] }
            if ($actual -eq $et) { $passes++ } else { $issues += "$dir(wrong target)" }
        } elseif (Test-Path $lp) { $issues += "$dir(not a link)" }
        # 不存在 = 未用 -Skills/-All 部署，可接受
    }

    foreach ($stale in $STALE_LINKS) {
        $sp = Join-Path $cursorDir $stale
        if ((Test-Path $sp) -and (Test-IsReparseLink $sp)) { $issues += "$stale(stale link)" }
    }
    # v11 已移除的旧根文件残留
    foreach ($legacy in @("CLAUDE-ROUTER.mdc", "agent.yaml")) {
        if (Test-Path (Join-Path $cursorDir $legacy)) { $issues += "$legacy(stale, removed in v11)" }
    }

    if ($issues.Count -eq 0) {
        Add-Check "Symlink" ".cursor" "pass" "$passes checks OK"
    } else {
        Add-Check "Symlink" ".cursor" "warn" "$($issues -join ', ') -- run sync.ps1"
    }
}

# v11.1 managed 编辑器白名单校验：在装编辑器应有预期落点（缺失才告警）；
# enabled=false 的编辑器反向扫残留链（不应再有 ~/.claude 链接）
foreach ($edName in @($MANAGED_EDITORS.Keys)) {
    $ed = $MANAGED_EDITORS[$edName]
    if (-not (Test-Path $ed.Home)) { continue }  # 未安装 → 跳过

    if (-not $ed.Enabled) {
        $links = @(Get-ChildItem $ed.Home -Force -ErrorAction SilentlyContinue |
            Where-Object {
                ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -and
                ($_.Target -and ("$($_.Target)" -like "*\.claude\*" -or "$($_.Target)" -like "*\.claude"))
            })
        if ($links.Count -eq 0) {
            Add-Check "Symlink" "$edName (disabled)" "pass" "no residual ~/.claude links"
        } else {
            Add-Check "Symlink" "$edName (disabled)" "warn" "$($links.Count) residual link(s) -- editor disabled in sync-manifest, safe to delete"
        }
        continue
    }

    $edIssues = @()
    $edPasses = 0

    if ($ed.Special -eq "claude_md_plus_skills") {
        # workbuddy：仅 CLAUDE.md + skills/ 联接；SOUL/USER 等自有命名空间不校验
        $cm = Join-Path $ed.Home "CLAUDE.md"
        $cmSrc = Join-Path $CLAUDE_DIR "CLAUDE.md"
        if (-not (Test-Path $cm)) { $edIssues += "CLAUDE.md(missing)" }
        elseif (Test-IsReparseLink $cm) { $edPasses++ }
        else {
            try {
                if ((Get-FileHash $cm -Algorithm SHA256).Hash -eq (Get-FileHash $cmSrc -Algorithm SHA256).Hash) { $edPasses++ }
                else { $edIssues += "CLAUDE.md(stale copy)" }
            } catch { $edIssues += "CLAUDE.md(unreadable)" }
        }
        $sk = Join-Path $ed.Home "skills"
        if (Test-IsReparseLink $sk) { $edPasses++ }
        elseif (Test-Path $sk) { $edIssues += "skills(not a link)" }
        else { $edIssues += "skills(missing)" }
    } elseif ($ed.Special -eq "agents_md") {
        # v11.4.4：enabled 应为 false；若误开，不把 AGENTS.md 与 CLAUDE.md 做 hash 对齐（OpenCode 自管）
        Add-Check "Symlink" "$edName (decoupled)" "pass" "AGENTS.md owned by OpenCode; not compared to CLAUDE.md"
    } else {
        if ($ed.RootIndex) {
            foreach ($file in $SYNC_FILES) {
                $fp = Join-Path $ed.Home $file
                $expected = Join-Path $CLAUDE_DIR $file
                if (-not (Test-Path $fp)) { $edIssues += "$file(missing)" }
                elseif (Test-IsReparseLink $fp) {
                    $actual = (Get-Item $fp -Force).Target
                    if ($actual -is [array]) { $actual = $actual[0] }
                    if ($actual -eq $expected) { $edPasses++ } else { $edIssues += "$file(wrong target)" }
                } else {
                    try {
                        if ((Get-FileHash $fp -Algorithm SHA256).Hash -eq (Get-FileHash $expected -Algorithm SHA256).Hash) { $edPasses++ }
                        else { $edIssues += "$file(stale copy)" }
                    } catch { $edIssues += "$file(not a link)" }
                }
            }
        }
        if ($ed.RulesChannel) {
            $chanDir = Join-Path $ed.Home $ed.RulesChannel
            $srcRules = @(Get-ChildItem (Join-Path $CLAUDE_DIR "rules") -Filter "*.md" -ErrorAction SilentlyContinue |
                Where-Object { $_.Name -ne "README.md" })
            $ruleOk = 0
            foreach ($r in $srcRules) {
                $dst = Join-Path $chanDir "$($r.BaseName)$($ed.RulesExt)"
                if (-not (Test-Path -LiteralPath $dst)) { $edIssues += "$($ed.RulesChannel)/$($r.BaseName)$($ed.RulesExt)(missing)"; continue }
                try {
                    if ((Get-FileHash -LiteralPath $dst -Algorithm SHA256).Hash -eq (Get-FileHash -LiteralPath $r.FullName -Algorithm SHA256).Hash) { $ruleOk++ }
                    else { $edIssues += "$($ed.RulesChannel)/$($r.BaseName)$($ed.RulesExt)(stale)" }
                } catch { $edIssues += "$($ed.RulesChannel)/$($r.BaseName)$($ed.RulesExt)(unreadable)" }
            }
            $edPasses += $ruleOk
        }
    }

    if ($edIssues.Count -eq 0) {
        Add-Check "Symlink" $edName "pass" "$edPasses checks OK"
    } else {
        Add-Check "Symlink" $edName "warn" "$($edIssues -join ', ') -- run sync.ps1"
    }
}

# v11.4.13 harness adapter：home 缺席跳过；存在则便携文件在，且 AGENTS.md 不是 CLAUDE.md 软链
if ($syncMf -and $syncMf.harnesses) {
    foreach ($hProp in $syncMf.harnesses.PSObject.Properties) {
        if ($hProp.Name -eq "_comment") { continue }
        $hv = $hProp.Value
        $hHome = "$($hv.home)" -replace '^~', $(if ($env:USERPROFILE) { $env:USERPROFILE } else { $env:HOME })
        $hHome = $hHome -replace '/', [IO.Path]::DirectorySeparatorChar
        if (-not (Test-Path -LiteralPath $hHome)) {
            Add-Check "Harness" $hProp.Name "pass" "home absent, skipped"
            continue
        }
        $hIssues = @()
        $deployDir = "$(if ($hv.deploy_dir) { $hv.deploy_dir } else { 'tools' })"
        foreach ($f in @($hv.deploy)) {
            $fp = Join-Path (Join-Path $hHome $deployDir) $f
            if (-not (Test-Path -LiteralPath $fp)) { $hIssues += "$deployDir/$f(missing)" }
        }
        if ($hv.plugins) {
            $pdir = "$(if ($hv.plugin_dir) { $hv.plugin_dir } else { 'plugins' })"
            foreach ($f in @($hv.plugins)) {
                $fp = Join-Path (Join-Path $hHome $pdir) $f
                if (-not (Test-Path -LiteralPath $fp)) { $hIssues += "$pdir/$f(missing)" }
            }
        }
        if ("$($hv.agents_md)" -eq "self-managed") {
            $ag = Join-Path $hHome "AGENTS.md"
            if (Test-Path -LiteralPath $ag) {
                $item = Get-Item -LiteralPath $ag -Force
                if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                    $tgt = "$($item.Target)"
                    if ($tgt -like "*CLAUDE.md") {
                        $hIssues += "AGENTS.md is symlink to CLAUDE.md (forbidden)"
                    }
                }
            }
        }
        if ($hIssues.Count -eq 0) {
            Add-Check "Harness" $hProp.Name "pass" "portable files OK; AGENTS.md not CLAUDE.md overlay"
        } else {
            Add-Check "Harness" $hProp.Name "warn" "$($hIssues -join ', ') -- run sync.ps1 or deploy-editor-graph-hooks.ps1"
        }
    }
}

# =============================================================
# S4: Hook safety
# =============================================================
Write-Section 4 "Hook Safety"

$hooksDir = Join-Path $CLAUDE_DIR "hooks"
if (Test-Path $hooksDir) {
    $pyFiles = Get-ChildItem $hooksDir -File -Filter "*.py"
    Add-Check "Hooks" "Hook file count" "pass" "$($pyFiles.Count) .py files in hooks/"

    # ralph-loop detection
    if ($settingsObj -and $settingsObj.hooks) {
        $ralphFound = $false
        $cats = $settingsObj.hooks | Get-Member -MemberType NoteProperty -EA SilentlyContinue | Select-Object -ExpandProperty Name
        foreach ($cat in $cats) {
            foreach ($entry in $settingsObj.hooks.$cat) {
                foreach ($h in $entry.hooks) {
                    if ([string]$h.command -match "ralph-loop|stop-hook") {
                        Add-Check "Hooks" "ralph-loop risk" "fail" "Found in $cat -- run fix.ps1 -Fix"
                        $ralphFound = $true
                    }
                    if ([string]$h.command -match "post-auto-commit") {
                        Add-Check "Hooks" "post-auto-commit loop" "warn" "auto commit -> file change -> PostToolUse again = infinite loop"
                    }
                }
            }
        }
        if (-not $ralphFound) {
            Add-Check "Hooks" "ralph-loop risk" "pass" "Not found in CLI settings.json"
        }
    }

    # Cross-reference check
    if ($settingsObj -and $settingsObj.hooks) {
        $referenced = @()
        $cats = $settingsObj.hooks | Get-Member -MemberType NoteProperty -EA SilentlyContinue | Select-Object -ExpandProperty Name
        foreach ($cat in $cats) {
            foreach ($entry in $settingsObj.hooks.$cat) {
                foreach ($h in $entry.hooks) {
                    if ([string]$h.command -match "([^\s/\\]+\.py)") { $referenced += $Matches[1] }
                }
            }
        }
        $localNames = $pyFiles | Select-Object -ExpandProperty Name
        $missing    = $referenced | Where-Object { $localNames -notcontains $_ } | Select-Object -Unique
        if ($missing.Count -gt 0) {
            Add-Check "Hooks" "Reference integrity" "fail" "Referenced but missing: $($missing -join ', ')"
        } else {
            Add-Check "Hooks" "Reference integrity" "pass" "$($referenced.Count) references all exist"
        }
    }

    $launcherPath = Join-Path $hooksDir "_editor_hook_launcher.py"
    $launcherOk = $false
    if (Test-Path $launcherPath) {
        $launcherContent = Get-Content $launcherPath -Raw -Encoding utf8
        if ($launcherContent -match 'GetConsoleWindow') { $launcherOk = $true }
    }

    $registeredHooks = 0
    $launcherHooks = 0
    if ($settingsObj -and $settingsObj.hooks) {
        $cats = $settingsObj.hooks | Get-Member -MemberType NoteProperty -EA SilentlyContinue | Select-Object -ExpandProperty Name
        foreach ($cat in $cats) {
            foreach ($entry in $settingsObj.hooks.$cat) {
                foreach ($h in $entry.hooks) {
                    $registeredHooks++
                    if ([string]$h.command -match "_editor_hook_launcher") { $launcherHooks++ }
                }
            }
        }
    }

    if (-not $launcherOk) {
        Add-Check "Hooks" "Editor guard (launcher)" "fail" "launcher missing or outdated -- run fix.ps1 -Fix"
    } elseif ($registeredHooks -gt 0 -and $launcherHooks -lt $registeredHooks) {
        Add-Check "Hooks" "Editor guard (launcher)" "fail" "$launcherHooks/$registeredHooks hooks use launcher -- run fix.ps1 -Fix"
    } else {
        Add-Check "Hooks" "Editor guard (launcher)" "pass" "launcher v2.0 + $launcherHooks/$registeredHooks hooks routed"
    }
} else {
    Add-Check "Hooks" "hooks/ directory" "fail" "Directory not found"
}

# =============================================================
# S4b: Cursor Guard (editor-native hooks)
# =============================================================
Write-Section "4b" "Cursor Guard"

$guardTemplate = Join-Path $CLAUDE_DIR "templates\cursor-guard\hooks.json"
$guardDeployed = Join-Path $env:USERPROFILE ".cursor\hooks.json"
$guardHooksDir = Join-Path $env:USERPROFILE ".cursor\hooks"
$requiredGuardScripts = @(
    "sync_on_edit.py",
    "sync_on_prompt.py",
    "context_pre_tool.py",
    "context_post_tool.py",
    "context_stop.py",
    "session_bootstrap.py",
    "pre_compact_snapshot.py",
    "explore_router.py",
    "maintenance_hints.py",
    "shell_guard.py",
    "prompt_secret_scan.py"
)
$guardEditorRule = Join-Path $env:USERPROFILE ".cursor\plugins\local\claude-config\rules\CURSOR-EDITOR.mdc"
$guardEditorRuleTpl = Join-Path $CLAUDE_DIR "templates\cursor-guard\rules\CURSOR-EDITOR.mdc"

if (-not (Test-Path $guardTemplate)) {
    Add-Check "CursorGuard" "template" "fail" "templates/cursor-guard/hooks.json missing"
} else {
    Add-Check "CursorGuard" "template" "pass" "templates/cursor-guard present"
}

if (-not (Test-Path $guardDeployed)) {
    Add-Check "CursorGuard" "deployed hooks.json" "fail" "Run deploy-cursor-guard.ps1"
} else {
    try {
        $tpl = Get-Content $guardTemplate -Raw -Encoding utf8 | ConvertFrom-Json
        $dep = Get-Content $guardDeployed -Raw -Encoding utf8 | ConvertFrom-Json
        $tplVer = [string]$tpl.guard_version
        $depVer = [string]$dep.guard_version
        if ($tplVer -and $depVer -eq $tplVer) {
            Add-Check "CursorGuard" "version" "pass" "guard_version=$depVer"
        } elseif ($tplVer) {
            Add-Check "CursorGuard" "version" "warn" "deployed=$depVer template=$tplVer -- redeploy"
        } else {
            Add-Check "CursorGuard" "deployed hooks.json" "pass" "present"
        }
    } catch {
        Add-Check "CursorGuard" "hooks.json parse" "fail" $_.Exception.Message
    }
}

$missingGuard = @()
foreach ($s in $requiredGuardScripts) {
    if (-not (Test-Path (Join-Path $guardHooksDir $s))) { $missingGuard += $s }
}
if ($missingGuard.Count -gt 0) {
    Add-Check "CursorGuard" "hook scripts" "fail" "Missing: $($missingGuard -join ', ')"
} elseif (Test-Path $guardHooksDir) {
    Add-Check "CursorGuard" "hook scripts" "pass" "$($requiredGuardScripts.Count) scripts"
} else {
    Add-Check "CursorGuard" "hook scripts" "fail" "~/.cursor/hooks/ not found"
}

$guardCfg = Join-Path $env:USERPROFILE ".cursor\guard-config.json"
if (Test-Path $guardCfg) {
    Add-Check "CursorGuard" "guard-config.json" "pass" "user config present"
} else {
    Add-Check "CursorGuard" "guard-config.json" "warn" "Run deploy-cursor-guard.ps1"
}

if (-not (Test-Path $guardEditorRuleTpl)) {
    Add-Check "CursorGuard" "CURSOR-EDITOR.mdc tpl" "fail" "template missing"
} else {
    Add-Check "CursorGuard" "CURSOR-EDITOR.mdc tpl" "pass" "present"
}
if (Test-Path $guardEditorRule) {
    Add-Check "CursorGuard" "CURSOR-EDITOR deployed" "pass" "~/.cursor/plugins/local/claude-config/rules/"
} else {
    Add-Check "CursorGuard" "CURSOR-EDITOR deployed" "warn" "Run sync.ps1 or deploy-cursor-guard.ps1"
}

# S4b-L0: Cursor 个人桥接 = local plugin claude-config（~/.cursor/rules 实测不生效，plugin 永久通道）
$cursorPluginRulesDir = Join-Path $env:USERPROFILE ".cursor\plugins\local\claude-config\rules"
$cursorRulesDir = Join-Path $env:USERPROFILE ".cursor\rules"
$cursorProjectRulesDir = Join-Path $CLAUDE_DIR ".cursor\rules"
# v11: ROUTER 并入 CLAUDE.md，插件 L0 承载文件为 00-CLAUDE.mdc
$l0Bases = @("00-CLAUDE", "CORE", "CURSOR-EDITOR")
$l0SrcMap = @{
    "00-CLAUDE"     = Join-Path $CLAUDE_DIR "CLAUDE.md"
    "CORE"          = Join-Path $CLAUDE_DIR "rules\CORE.md"
    "CURSOR-EDITOR" = Join-Path $CLAUDE_DIR "templates\cursor-guard\rules\CURSOR-EDITOR.mdc"
}
# plugin 三件套：存在 + hash 与真源一致
$pluginMissing = @()
$pluginStale = @()
foreach ($base in $l0Bases) {
    $p = Join-Path $cursorPluginRulesDir "$base.mdc"
    if (-not (Test-Path $p)) { $pluginMissing += "$base.mdc"; continue }
    try {
        $h1 = (Get-FileHash $p -Algorithm SHA256).Hash
        $h2 = (Get-FileHash $l0SrcMap[$base] -Algorithm SHA256).Hash
        if ($h1 -ne $h2) { $pluginStale += "$base(hash drift)" }
    } catch { $pluginStale += "$base(hash check failed)" }
}
if ($pluginMissing.Count -eq 0 -and $pluginStale.Count -eq 0) {
    Add-Check "CursorGuard" "plugin L0 rules" "pass" "3/3 in plugin claude-config (hash match)"
} elseif ($pluginMissing.Count -gt 0) {
    Add-Check "CursorGuard" "plugin L0 rules" "fail" "Missing: $($pluginMissing -join ', ') -- run sync.ps1"
} else {
    Add-Check "CursorGuard" "plugin L0 rules" "warn" "$($pluginStale -join ', ') -- run sync.ps1"
}
# ~/.cursor/rules 期望为空（plugin 永久通道；避免双份 Always Apply）
$cursorRulesFiles = @(Get-ChildItem $cursorRulesDir -File -Force -ErrorAction SilentlyContinue)
if ($cursorRulesFiles.Count -eq 0) {
    Add-Check "CursorGuard" "~/.cursor/rules empty" "pass" "empty by design (plugin-only channel)"
} else {
    Add-Check "CursorGuard" "~/.cursor/rules empty" "warn" "non-plugin files: $($cursorRulesFiles.Name -join ', ')"
}
# project L0 rules（~/.claude/.cursor/rules）: v14.5 personal-only，期望空
$projFiles = @(Get-ChildItem $cursorProjectRulesDir -File -Force -ErrorAction SilentlyContinue)
if ($projFiles.Count -eq 0) {
    Add-Check "CursorGuard" "project L0 rules" "pass" "empty/absent (v14.5 — personal-only)"
} else {
    Add-Check "CursorGuard" "project L0 rules" "warn" "files present: $($projFiles.Name -join ', ')"
}

# v11.1: WorkBuddy / CodeArts 等编辑器校验已并入 S3 managed 白名单循环
# （清单单源 sync-manifest.json editors 段），此处不再单设检查段。

# =============================================================
# S5: Runtime environment
# =============================================================
Write-Section 5 "Runtime Environment"

$py = Get-Command python -EA SilentlyContinue
if ($py) {
    Add-Check "Runtime" "Python" "pass" (& python --version 2>&1)
} else {
    Add-Check "Runtime" "Python" "fail" "Not installed - hooks will not run"
}

$runtimeTools = @(
    @{ C = "node"; N = "Node.js"; Req = $true }
    @{ C = "npm";  N = "npm";     Req = $true }
    @{ C = "npx";  N = "npx";     Req = $true }
    @{ C = "uvx";  N = "uvx(uv)"; Req = $false }
    @{ C = "pnpm"; N = "pnpm";    Req = $false }
)

foreach ($t in $runtimeTools) {
    $found = Get-Command $t.C -EA SilentlyContinue
    if ($found) {
        $ver = & $t.C --version 2>&1 | Select-Object -First 1
        Add-Check "Runtime" $t.N "pass" $ver
    } else {
        Add-Check "Runtime" $t.N (if ($t.Req) { "fail" } else { "warn" }) "Not installed$(if(-not $t.Req){' (optional)'})"
    }
}

$gitCmd = Get-Command git -EA SilentlyContinue
if ($gitCmd) {
    Add-Check "Runtime" "Git" "pass" (& git --version 2>&1)
    $gname = & git config --global user.name 2>&1
    Add-Check "Runtime" "git user.name" (if ($gname) { "pass" } else { "warn" }) "$gname"
} else {
    Add-Check "Runtime" "Git" "fail" "Not installed"
}

$dk = Get-Command docker -EA SilentlyContinue
if ($dk) {
    Add-Check "Runtime" "Docker" "pass" (& docker --version 2>&1)
} else {
    Add-Check "Runtime" "Docker" "warn" "Not installed (docker MCP unavailable)"
}

# Claude CLI: native PE at ~/.local/bin, never a Volta/npm shim (recurring broken claude.exe)
function Test-PeFile([string]$p) {
    if (-not (Test-Path -LiteralPath $p)) { return $false }
    try {
        $b = [System.IO.File]::ReadAllBytes($p)
        return ($b.Length -ge 2 -and $b[0] -eq 0x4D -and $b[1] -eq 0x5A)
    } catch { return $false }
}
$nativeClaude = Join-Path $env:USERPROFILE ".local\bin\claude.exe"
$claudeCmd = Get-Command claude -EA SilentlyContinue
$claudeSrc = if ($claudeCmd) { [string]$claudeCmd.Source } else { "" }
if (-not $claudeSrc) {
    Add-Check "Runtime" "Claude CLI" "fail" "claude not on PATH -- run scripts/fix-claude-cli.ps1"
} elseif ($claudeSrc -match '(?i)[\\/]volta[\\/]|npm-prefix') {
    Add-Check "Runtime" "Claude CLI" "fail" "Volta/npm shim $claudeSrc -- run scripts/fix-claude-cli.ps1"
} elseif (-not (Test-PeFile $claudeSrc)) {
    Add-Check "Runtime" "Claude CLI" "fail" "not a PE executable: $claudeSrc -- run scripts/fix-claude-cli.ps1"
} else {
    $ver = & $claudeSrc --version 2>&1 | Select-Object -First 1
    Add-Check "Runtime" "Claude CLI" "pass" "$ver ($claudeSrc)"
}
if ($claudeSrc -and ($claudeSrc -ne $nativeClaude) -and (Test-PeFile $nativeClaude)) {
    Add-Check "Runtime" "Claude CLI PATH order" "warn" "native exists at $nativeClaude but PATH hits $claudeSrc first"
}

$auStatus = if ($settingsObj) { [string]$settingsObj.autoUpdaterStatus } else { "" }
$auEnv = ""
if ($settingsObj -and $settingsObj.env) { $auEnv = [string]$settingsObj.env.DISABLE_AUTOUPDATER }
$auUser = [Environment]::GetEnvironmentVariable("DISABLE_AUTOUPDATER", "User")
$auOff = ($auStatus -eq "disabled" -or $auStatus -eq "off") -and ($auEnv -eq "1" -or $auEnv -eq "true")
if ($auOff) {
    Add-Check "Runtime" "Claude auto-update" "pass" "autoUpdaterStatus=$auStatus DISABLE_AUTOUPDATER=$auEnv"
} else {
    Add-Check "Runtime" "Claude auto-update" "fail" "must stay off (native updater renames claude.exe) -- run scripts/fix-claude-cli.ps1 (status=$auStatus env=$auEnv)"
}
if ($auUser -eq "1" -or $auUser -eq "true") {
    Add-Check "Runtime" "DISABLE_AUTOUPDATER User env" "pass" "User=$auUser"
} else {
    Add-Check "Runtime" "DISABLE_AUTOUPDATER User env" "warn" "User env unset; Claude CLI still honors settings.json env"
}

$ghMcpExe = Join-Path $env:USERPROFILE ".local\bin\github-mcp-server.exe"
if (Test-PeFile $ghMcpExe) {
    Add-Check "Runtime" "github-mcp-server" "pass" $ghMcpExe
} else {
    Add-Check "Runtime" "github-mcp-server" "fail" "missing PE at $ghMcpExe -- run scripts/fix-claude-cli.ps1"
}

$ghTokenUser = [Environment]::GetEnvironmentVariable("GITHUB_TOKEN", "User")
$ghPatUser = [Environment]::GetEnvironmentVariable("GITHUB_PERSONAL_ACCESS_TOKEN", "User")
if ($ghTokenUser) {
    Add-Check "Runtime" "GITHUB_TOKEN" "pass" "User present"
} else {
    Add-Check "Runtime" "GITHUB_TOKEN" "fail" "User env missing -- GitHub MCP will have 0 tools"
}
if ($ghPatUser) {
    Add-Check "Runtime" "GITHUB_PERSONAL_ACCESS_TOKEN" "pass" $(if ($ghTokenUser -and $ghPatUser -eq $ghTokenUser) { "User present, matches GITHUB_TOKEN" } else { "User present" })
} else {
    Add-Check "Runtime" "GITHUB_PERSONAL_ACCESS_TOKEN" "fail" "User env missing -- run scripts/fix-claude-cli.ps1"
}

function Test-GithubMcpStdio([string]$mcpFile, [string]$label) {
    if (-not (Test-Path $mcpFile)) {
        Add-Check "MCP" "$label github transport" "fail" "$mcpFile missing"
        return
    }
    try {
        $obj = Get-Content $mcpFile -Raw -Encoding utf8 | ConvertFrom-Json
        $gh = $obj.mcpServers.github
        if (-not $gh) {
            Add-Check "MCP" "$label github transport" "fail" "no github server"
            return
        }
        $cmd = [string]$gh.command
        $url = [string]$gh.url
        if ($url -match 'githubcopilot\.com') {
            Add-Check "MCP" "$label github transport" "fail" "HTTP api.githubcopilot.com causes mcp_auth + 0 tools -- use local github-mcp-server.exe"
        } elseif ($cmd -match 'github-mcp-server') {
            Add-Check "MCP" "$label github transport" "pass" "stdio $cmd"
        } else {
            Add-Check "MCP" "$label github transport" "warn" "unexpected github config"
        }
    } catch {
        Add-Check "MCP" "$label github transport" "fail" $_.Exception.Message
    }
}
Test-GithubMcpStdio (Join-Path $CLAUDE_DIR ".mcp.json") "Claude"
Test-GithubMcpStdio (Join-Path $env:USERPROFILE ".cursor\mcp.json") "Cursor"
Test-GithubMcpStdio (Join-Path $env:USERPROFILE ".qoder-cn\mcp.json") "Qoder-cn"

# sync.ps1 永不同步 MCP：manifest 不得列出 mcp.json；脚本不得把 mcp.json 写到编辑器 home
$syncPs1 = Join-Path $CLAUDE_DIR "scripts\sync.ps1"
$manifestPath = Join-Path $CLAUDE_DIR "config\sync-manifest.json"
$syncText = if (Test-Path $syncPs1) { Get-Content $syncPs1 -Raw -Encoding utf8 } else { "" }
$manifestText = if (Test-Path $manifestPath) { Get-Content $manifestPath -Raw -Encoding utf8 } else { "" }
if ($manifestText -match '"\.?mcp\.json"') {
    Add-Check "Sync" "manifest excludes MCP" "fail" "sync-manifest.json must not list mcp.json"
} else {
    Add-Check "Sync" "manifest excludes MCP" "pass" "root_files has no mcp.json"
}
if ($syncText -match 'Copy-Item[^\n]*mcp\.json' -or $syncText -match 'mcp\.json[^\n]*(cursor|qoder|trae|workbuddy)') {
    Add-Check "Sync" "sync.ps1 does not copy mcp.json" "fail" "sync.ps1 appears to write editor mcp.json"
} elseif ($syncText -match 'MCP configs' -or $syncText -match 'MCP 配置') {
    Add-Check "Sync" "sync.ps1 does not copy mcp.json" "pass" "MCP listed in exclusion banner"
} else {
    Add-Check "Sync" "sync.ps1 does not copy mcp.json" "warn" "no explicit MCP exclusion banner"
}

# =============================================================
# S6: MCP server status
# =============================================================
Write-Section 6 "MCP Server Status$(if($Quick){' [Quick mode - connectivity skipped]'})"

if (-not $Quick) {
    $redisCli = Get-Command redis-cli -EA SilentlyContinue
    if ($redisCli) {
        $ping = & redis-cli ping 2>&1
        Add-Check "MCP" "Redis" (if ($ping.ToString().Trim() -eq "PONG") { "pass" } else { "warn" }) `
            (if ($ping.ToString().Trim() -eq "PONG") { "Connected" } else { "Not responding" })
    } else {
        Add-Check "MCP" "Redis" "warn" "redis-cli not installed"
    }

    $pg = $false
    try { $t = New-Object System.Net.Sockets.TcpClient; $t.Connect("127.0.0.1",5432); $pg=$t.Connected; $t.Close() } catch {}
    Add-Check "MCP" "PostgreSQL" (if ($pg) { "pass" } else { "warn" }) (if ($pg) { "port 5432 reachable" } else { "service not running" })
}

$dbPath = "D:\apdms\database.db"
Add-Check "MCP" "SQLite" (if (Test-Path $dbPath) { "pass" } else { "warn" }) `
    (if (Test-Path $dbPath) { "$dbPath exists" } else { "auto-created on first use" })

$npxOk = $null -ne (Get-Command npx -EA SilentlyContinue)
$uvxOk = $null -ne (Get-Command uvx -EA SilentlyContinue)

$mcpDeps = @(
    @{ N = "git MCP (uvx)";   Ok = $uvxOk -and ($null -ne $gitCmd) }
    @{ N = "fetch MCP (uvx)"; Ok = $uvxOk }
    @{ N = "ctx7 MCP (npx)";  Ok = $npxOk }
    @{ N = "time MCP (npx)";  Ok = $npxOk }
    @{ N = "Docker MCP (npx)"; Ok = $npxOk -and ($null -ne $dk) }
)

foreach ($m in $mcpDeps) {
    Add-Check "MCP" $m.N (if ($m.Ok) { "pass" } else { "warn" }) (if ($m.Ok) { "dependencies available" } else { "dependency missing" })
}

# =============================================================
# S7: Toolbox stats
# =============================================================
Write-Section 7 "Toolbox Stats"

$skillsDir  = Join-Path $CLAUDE_DIR "skills"
$agentsDir  = Join-Path $CLAUDE_DIR "agents"
$rulesDir   = Join-Path $CLAUDE_DIR "rules"
$hooksDir2  = Join-Path $CLAUDE_DIR "hooks"
$scriptsDir = Join-Path $CLAUDE_DIR "scripts"

$skillCnt  = if (Test-Path $skillsDir)  { (Get-ChildItem $skillsDir  -Directory -EA SilentlyContinue).Count } else { 0 }
$agentCnt  = if (Test-Path $agentsDir)  { (Get-ChildItem $agentsDir  -File -Filter "*.md" -EA SilentlyContinue).Count } else { 0 }
$ruleCnt   = if (Test-Path $rulesDir)   { (Get-ChildItem $rulesDir   -File -Filter "*.md" -EA SilentlyContinue).Count } else { 0 }
$hookCnt   = if (Test-Path $hooksDir2)  { (Get-ChildItem $hooksDir2  -File -Filter "*.py" -EA SilentlyContinue).Count } else { 0 }
$scriptCnt = if (Test-Path $scriptsDir) { (Get-ChildItem $scriptsDir -File -EA SilentlyContinue).Count } else { 0 }

Add-Check "Toolbox" "Skills"  (if ($skillCnt  -gt 0) { "pass" } else { "warn" }) "$skillCnt skill(s)"
Add-Check "Toolbox" "Agents"  (if ($agentCnt  -gt 0) { "pass" } else { "warn" }) "$agentCnt agent(s)"
Add-Check "Toolbox" "Rules"   (if ($ruleCnt   -gt 0) { "pass" } else { "warn" }) "$ruleCnt rule(s)"
Add-Check "Toolbox" "Hooks"   (if ($hookCnt   -gt 0) { "pass" } else { "warn" }) "$hookCnt Python hook(s)"
Add-Check "Toolbox" "Scripts" (if ($scriptCnt -gt 0) { "pass" } else { "warn" }) "$scriptCnt script(s)"

if ($hookCnt -gt 0) {
    $pyNames = Get-ChildItem $hooksDir2 -File -Filter "*.py" -EA SilentlyContinue | Select-Object -ExpandProperty BaseName
    $pre  = ($pyNames | Where-Object { $_ -like "pre-*" }).Count
    $post = ($pyNames | Where-Object { $_ -like "post-*" }).Count
    $stop = ($pyNames | Where-Object { $_ -like "stop-*" }).Count
    Write-Host "         pre-*: $pre  post-*: $post  stop-*: $stop" -ForegroundColor DarkGray
    if ($stop -gt 0) {
        Write-Host "         NOTE: stop-* hooks valid in CLI settings.json only, not editor sync" -ForegroundColor Yellow
    }
}

try {
    $drv    = (Get-Item $CLAUDE_DIR).PSDrive
    $freeGB = [math]::Round($drv.Free / 1GB, 1)
    $pct    = [math]::Round($drv.Free / ($drv.Free + $drv.Used) * 100)
    Add-Check "Toolbox" "Disk space" (if ($pct -gt 20) { "pass" } elseif ($pct -gt 10) { "warn" } else { "fail" }) "${freeGB}GB free (${pct}%)"
} catch {}

# =============================================================
# S8: Score + report
# =============================================================
Write-Host ""
$total = $passCount + $warnCount + $failCount
$score = if ($total -gt 0) { [math]::Round($passCount / $total * 100) } else { 0 }
$color = if ($score -ge 90) { "Green" } elseif ($score -ge 70) { "Yellow" } else { "Red" }
$grade = if ($score -ge 90) { "Excellent" } elseif ($score -ge 70) { "Good" } else { "Needs Work" }

Write-Host "  =====================================================" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  Health Score: $score/100  [$grade]" -ForegroundColor $color
Write-Host "  Pass: $passCount   Warn: $warnCount   Fail: $failCount   Total: $total" -ForegroundColor White
Write-Host ""

$fails = $results | Where-Object { $_.Status -eq "fail" }
$warns = $results | Where-Object { $_.Status -eq "warn" }

if ($fails.Count -gt 0) {
    Write-Host "  Must fix:" -ForegroundColor Red
    foreach ($f in $fails) { Write-Host "    [$($f.Cat)] $($f.Item): $($f.Detail)" -ForegroundColor Red }
    Write-Host ""
}
if ($warns.Count -gt 0) {
    Write-Host "  Suggestions:" -ForegroundColor Yellow
    foreach ($w in $warns) { Write-Host "    [$($w.Cat)] $($w.Item): $($w.Detail)" -ForegroundColor Yellow }
    Write-Host ""
}

# Action hints
$tips = @()
if ($warns | Where-Object { $_.Cat -eq "Symlink" }) {
    $tips += "run sync.ps1         -- sync tools to editors"
}
if ($fails | Where-Object { $_.Cat -eq "Hooks" -and $_.Item -like "*ralph*" }) {
    $tips += "run fix.ps1 -Fix     -- remove ralph-loop Stop hook"
}
if ($fails | Where-Object { $_.Cat -eq "Hooks" -and $_.Item -like "*launcher*" }) {
    $tips += "run fix.ps1 -Fix     -- deploy launcher + route hooks via settings.json"
}
if ($fails | Where-Object { $_.Item -match 'Claude CLI|Claude auto-update|github-mcp-server|GITHUB_PERSONAL_ACCESS_TOKEN|github transport' }) {
    $tips += "run fix-claude-cli.ps1  -- native claude.exe + disable auto-update + github-mcp-server"
}
if ($tips.Count -gt 0) {
    Write-Host "  Recommended actions:" -ForegroundColor Cyan
    foreach ($tip in $tips) { Write-Host "    $tip" -ForegroundColor White }
    Write-Host ""
}

# Save report
$logDir = Join-Path $CLAUDE_DIR "logs"
New-Item -ItemType Directory -Path $logDir -Force | Out-Null

$lines = @(
    "# Claude Code Environment Check Report"
    "Time : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    "Score: $score/100 [$grade]"
    "Pass : $passCount  Warn: $warnCount  Fail: $failCount"
    ""
)
foreach ($cat in ($results | ForEach-Object { $_.Cat } | Select-Object -Unique)) {
    $lines += "## $cat"
    foreach ($r in ($results | Where-Object { $_.Cat -eq $cat })) {
        $icon = switch ($r.Status) { "pass"{"[OK]"}; "warn"{"[!!]"}; "fail"{"[XX]"} }
        $lines += "- $icon $($r.Item)$(if($r.Detail){': '+$r.Detail})"
    }
    $lines += ""
}

$reportPath = Join-Path $logDir "check-$(Get-Date -Format 'yyyyMMdd').md"
$lines -join "`n" | Out-File $reportPath -Encoding utf8
Write-Host "  Report saved: $reportPath" -ForegroundColor DarkGray
Write-Host ""
