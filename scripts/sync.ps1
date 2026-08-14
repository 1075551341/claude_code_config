<#
.SYNOPSIS
    Claude config multi-editor sync v20.0 (v11.1：1+N — Claude Code 原生零同步 + N 编辑器落点)
    Claude Code 原生读 ~/.claude（无需同步）；本脚本维护 Cursor + qoder-cn/trae-cn/workbuddy 等编辑器落点。

.DESCRIPTION
    默认执行（幂等，hash/link 跳过无变更项）：
      1. 根文件 6 项 -> ~/.cursor（软链）：CLAUDE.md/SPEC/MANIFEST/3 INDEX
         （集合单源：config/sync-manifest.json，与 check.ps1 / impact_sync.py 共用）
      2. Cursor local plugin claude-config（Cursor 唯一规则通道，实体 .mdc）：
         rules/*.md（除 README）+ CLAUDE.md->00-CLAUDE.mdc + Guard CURSOR-EDITOR.mdc
         直接从 SSOT 生成（v11 起无 templates/ 镜像层），含孤儿清除
      3. 去重 ~/.cursor/rules 中与 plugin 同 basename 的文件（防双份 Always-Apply）
      4. 其他编辑器（v11.1 恢复，编辑器清单单源 sync-manifest.json editors 段，home 缺席自动跳过）：
         qoder-cn -> 根 6 软链 + rules/*.mdc；trae-cn -> 根 6 软链 + user_rules/*.md；
         workbuddy -> 仅 CLAUDE.md + skills/ 联接（SOUL/USER/IDENTITY/BOOTSTRAP 自有命名空间禁触，跳根索引）；
         规则实体复制带 .claude-managed 台账，孤儿清除只删自己管理过的文件（不动用户自有规则）
    -Skills:  另同步 skills/ junction -> ~/.cursor/skills
    -All:     skills/ + agents/ junction
    -DryRun:  仅预览
    -ProjectRules / -ProjectRulesPath: 显式投放 <project>/.cursor/rules（默认关）
    -Lint / -InitProject: 项目脚手架模板复制（跳过已存在）

    Cursor 规则通道 = local plugin（~/.cursor/rules 实测不生效）；plugin 禁外链软链接，
    故规则用实体复制 + 每次运行刷新 + hash 跳过。

    排除：hooks/ scripts/ MCP 配置 plugins/ commands/ settings.json

.PARAMETER Scope
    Cursor Guard 契约参数（sync_runner.py 调用）：rules | indexes | all
    all=等价 -All；rules=默认；indexes=仅根文件 + plugin（当前默认已很小，等价默认）。

.PARAMETER Force
    跳过变更检测（hash/link 对比）强制重写。

.EXAMPLE
    pwsh -ExecutionPolicy Bypass -File sync.ps1                 # 默认：根 6 + plugin 规则（PS5.1 回退用 powershell）
    pwsh -ExecutionPolicy Bypass -File sync.ps1 -All            # + skills/ + agents/ junction
    pwsh -ExecutionPolicy Bypass -File sync.ps1 -All -DryRun    # 预演
    pwsh -ExecutionPolicy Bypass -File sync.ps1 -ProjectRules   # 投放当前项目 .cursor/rules
    pwsh -ExecutionPolicy Bypass -File sync.ps1 -Lint           # prettier+eslint 模板
    pwsh -File sync.ps1 -Scope all -Force                       # Guard 自动调用

.NOTES
    验证：scripts/check.ps1 | 回归：scripts/test-sync-dedup.ps1
    v11 曾收敛为仅 Cursor；v11.1 按用户决策恢复多编辑器（qoder-cn/trae-cn/workbuddy，
    以 config/sync-manifest.json editors 段为单源），sync.sh（Linux/macOS）维持已删。
#>
#Requires -Version 5.1

param(
    [switch]$DryRun,
    [switch]$Skills,
    [switch]$All,
    [switch]$ProjectRules,
    [string]$ProjectRulesPath = "",
    [switch]$Lint,
    [switch]$InitProject,
    # Cursor Guard contract (sync_runner.py): -Scope rules|indexes|all [-Force]
    [ValidateSet("rules", "indexes", "all")][string]$Scope = "",
    [switch]$Force
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

if ($Scope -eq "all") { $All = $true }

# =============================================================
# Configuration（根文件集合单源：config/sync-manifest.json）
# =============================================================

$CLAUDE_DIR = "$env:USERPROFILE\.claude"
$CURSOR_DIR = "$env:USERPROFILE\.cursor"

# 单源清单读取；缺失/损坏时回退内置默认（与 manifest 内容一致）
$ROOT_FILES = @("CLAUDE.md", "SPEC.md", "MANIFEST.yaml", "skills-INDEX.md", "agents-INDEX.md", "rules-INDEX.md")
$PLUGIN_EXTRA = [ordered]@{
    "00-CLAUDE"     = "CLAUDE.md"
    "CURSOR-EDITOR" = "templates\cursor-guard\rules\CURSOR-EDITOR.mdc"
}
# 编辑器目标（v11.1 恢复；cursor 走专用 plugin 通道，此表用于其余编辑器循环）
# 内置默认与 manifest editors 段一致；home 缺席自动跳过
$EDITOR_TARGETS = [ordered]@{
    "qoder-cn"  = @{ Home = "$env:USERPROFILE\.qoder-cn";     Enabled = $true; RulesChannel = "rules";      RulesExt = ".mdc"; RootIndex = $true;  Special = "" }
    "trae-cn"   = @{ Home = "$env:USERPROFILE\.trae-cn";      Enabled = $true; RulesChannel = "user_rules"; RulesExt = ".md";  RootIndex = $true;  Special = "" }
    "workbuddy" = @{ Home = "$env:USERPROFILE\.workbuddy";    Enabled = $true; RulesChannel = "";           RulesExt = "";     RootIndex = $false; Special = "claude_md_plus_skills" }
    "qoder"     = @{ Home = "$env:USERPROFILE\.qoder";        Enabled = $true; RulesChannel = "rules";      RulesExt = ".mdc"; RootIndex = $true;  Special = "" }
    "trae"      = @{ Home = "$env:USERPROFILE\.trae";         Enabled = $true; RulesChannel = "user_rules"; RulesExt = ".md";  RootIndex = $true;  Special = "" }
    "codearts"  = @{ Home = "$env:USERPROFILE\.codeartsdoer"; Enabled = $true; RulesChannel = "rule";       RulesExt = ".mdc"; RootIndex = $true;  Special = "" }
}
$manifestPath = Join-Path $CLAUDE_DIR "config\sync-manifest.json"
if (Test-Path $manifestPath) {
    try {
        $mf = Get-Content $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($mf.root_files) { $ROOT_FILES = @($mf.root_files) }
        if ($mf.plugin_rule_sources) {
            $PLUGIN_EXTRA = [ordered]@{}
            foreach ($p in $mf.plugin_rule_sources.PSObject.Properties) {
                if ($p.Name -ne "_comment") {
                    $PLUGIN_EXTRA[$p.Name] = ($p.Value -replace '/', '\')
                }
            }
        }
        if ($mf.editors) {
            $EDITOR_TARGETS = [ordered]@{}
            foreach ($e in $mf.editors.PSObject.Properties) {
                if ($e.Name -eq "_comment" -or $e.Name -eq "cursor") { continue }
                $v = $e.Value
                $home_ = "$($v.home)" -replace '^~', $env:USERPROFILE -replace '/', '\'
                $EDITOR_TARGETS[$e.Name] = @{
                    Home         = $home_
                    Enabled      = ($v.enabled -ne $false)
                    RulesChannel = "$(if ($v.rules_channel) { $v.rules_channel } else { '' })"
                    RulesExt     = "$(if ($v.rules_ext) { $v.rules_ext } else { '' })"
                    RootIndex    = ($v.root_index -eq $true)
                    Special      = "$(if ($v.special) { $v.special } else { '' })"
                }
            }
        }
    } catch {
        Write-Host "  [!!] sync-manifest.json 解析失败，使用内置默认: $_" -ForegroundColor Yellow
    }
}

# ─── -Lint / -InitProject templates（copy to CWD, skip existing）───
$LINT_TEMPLATES = @(
    @{ SrcRel = "templates/lint/.prettierrc.json"; DstName = ".prettierrc.json" }
    @{ SrcRel = "templates/lint/.prettierignore";  DstName = ".prettierignore" }
    @{ SrcRel = "templates/lint/eslint.config.js"; DstName = "eslint.config.js" }
)
$PROJECT_TEMPLATES = @(
    @{ SrcRel = "templates/project-init/CLAUDE.md";     DstName = "CLAUDE.md" }
    @{ SrcRel = "templates/project-init/MANIFEST.yaml"; DstName = "MANIFEST.yaml" }
    @{ SrcRel = "templates/project-init/.env.example";  DstName = ".env.example" }
    @{ SrcRel = "templates/project-init/.gitignore";    DstName = ".gitignore" }
)

$script:STATS = @{ Synced = 0; Removed = 0; Skipped = 0; Failed = 0 }

$MODE_LABEL = "root 6 + Cursor plugin + editors (1+N)"
if ($Skills) { $MODE_LABEL = "$MODE_LABEL + skills/" }
if ($All)    { $MODE_LABEL = "ALL (root + plugin + skills + agents)" }
if ($ProjectRules) { $MODE_LABEL = "$MODE_LABEL + CWD ProjectRules" }
if ($ProjectRulesPath) { $MODE_LABEL = "$MODE_LABEL + ProjectRulesPath" }
if ($Lint)        { $MODE_LABEL = "Lint templates -> CWD" }
if ($InitProject) { $MODE_LABEL = "Project-init templates -> CWD" }
$SKIP_EDITOR_SYNC = $Lint -or $InitProject

# =============================================================
# Utility functions
# =============================================================

function Write-Ok   { param($m) Write-Host "    [OK]  $m" -ForegroundColor Green }
function Write-Fail { param($m) Write-Host "    [XX]  $m" -ForegroundColor Red }
function Write-Skip { param($m) Write-Host "    [--]  $m" -ForegroundColor DarkGray }
function Write-Fix  { param($m) Write-Host "    [FIX] $m" -ForegroundColor DarkCyan }
function Write-Dry  { param($m) Write-Host "    [DRY] $m" -ForegroundColor Yellow }

function IsLink {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return $false }
    return [bool]((Get-Item $Path -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)
}

function Test-IsAdmin {
    return ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Remove-Target {
    param([string]$Path, [string]$Label)
    if (-not (Test-Path $Path)) { return }
    if ($DryRun) {
        Write-Dry "Would remove: $Label"
        $script:STATS.Removed++
        return
    }
    try {
        if (IsLink $Path) {
            if (Test-Path $Path -PathType Container) {
                $null = & cmd.exe /c "rmdir `"$Path`"" 2>&1
            }
            if (Test-Path $Path) {
                Remove-Item $Path -Recurse -Force -ErrorAction SilentlyContinue
            }
        } else {
            Remove-Item $Path -Recurse -Force -ErrorAction SilentlyContinue
        }
        Write-Fix "Removed: $Label"
        $script:STATS.Removed++
    } catch {
        Write-Fail "Failed removing $Label : $_"
    }
}

# 写前去重：删除同 basename 全变体（任意扩展名/大小写），防 CORE.md + core.mdc 双份
function Remove-SameBasenameVariants {
    param([string]$Directory, [string]$BaseName, [string]$LabelPrefix)
    if (-not $Directory -or -not (Test-Path $Directory)) { return }
    if ([string]::IsNullOrWhiteSpace($BaseName)) { return }
    $found = @(Get-ChildItem -LiteralPath $Directory -File -Force -ErrorAction SilentlyContinue |
        Where-Object { $_.BaseName -ieq $BaseName })
    foreach ($f in $found) {
        $lbl = if ($LabelPrefix) { "$LabelPrefix/$($f.Name)" } else { $f.Name }
        Remove-Target -Path $f.FullName -Label $lbl
    }
}

# 单文件同步：软链优先，Copy 兜底；无变更（同链/同 hash）跳过
function Sync-File {
    param([string]$SrcPath, [string]$DstPath, [string]$Label, [switch]$PreferCopy)

    if (-not (Test-Path $SrcPath)) {
        Write-Skip "Source missing: $Label"
        $script:STATS.Skipped++
        return
    }

    if (-not $Force -and (Test-Path -LiteralPath $DstPath)) {
        if ((IsLink $DstPath) -and (Get-Item -LiteralPath $DstPath -Force).LinkType -eq 'SymbolicLink') {
            $linkTarget = (Get-Item -LiteralPath $DstPath -Force).Target
            if ($linkTarget -and ([IO.Path]::GetFullPath($linkTarget) -ieq [IO.Path]::GetFullPath($SrcPath))) {
                Write-Skip "Unchanged (link): $Label"
                $script:STATS.Skipped++
                return
            }
        } else {
            try {
                $srcHash = (Get-FileHash -LiteralPath $SrcPath -Algorithm SHA256).Hash
                $dstHash = (Get-FileHash -LiteralPath $DstPath -Algorithm SHA256).Hash
                if ($srcHash -eq $dstHash) {
                    Write-Skip "Unchanged: $Label"
                    $script:STATS.Skipped++
                    return
                }
            } catch { }
        }
    }

    $dstDir = Split-Path $DstPath -Parent
    if (-not (Test-Path $dstDir) -and -not $DryRun) {
        New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
    }

    $dstBase = [System.IO.Path]::GetFileNameWithoutExtension($DstPath)
    $scopeName = Split-Path $dstDir -Leaf
    Remove-SameBasenameVariants -Directory $dstDir -BaseName $dstBase -LabelPrefix "$scopeName"
    Remove-Target -Path $DstPath -Label $Label

    if ($DryRun) {
        Write-Ok $(if ($PreferCopy) { "Would copy: $Label" } else { "Would symlink: $Label" })
        $script:STATS.Synced++
        return
    }

    if (-not $PreferCopy) {
        $linkErr = $null
        try {
            # cmd mklink 优先 — New-Item SymbolicLink 在部分 PS5.1 宿主下静默失败
            $mklinkOut = & cmd.exe /c "mklink `"$DstPath`" `"$SrcPath`"" 2>&1
            if ((Test-Path -LiteralPath $DstPath) -and (IsLink $DstPath)) {
                Write-Ok "Symlinked: $Label"
                $script:STATS.Synced++
                return
            }
            $linkErr = ($mklinkOut | Out-String).Trim()
        } catch {
            $linkErr = $_.Exception.Message
        }
        try {
            if (Test-Path -LiteralPath $DstPath) {
                Remove-Item -LiteralPath $DstPath -Force -ErrorAction SilentlyContinue
            }
            New-Item -ItemType SymbolicLink -Path $DstPath -Target $SrcPath -Force -ErrorAction Stop | Out-Null
            Write-Ok "Symlinked: $Label"
            $script:STATS.Synced++
            return
        } catch {
            if (-not $linkErr) { $linkErr = $_.Exception.Message }
            Write-Host "    [--]  symlink failed ($Label): $linkErr" -ForegroundColor DarkYellow
        }
    }

    try {
        Copy-Item $SrcPath $DstPath -Force
        Write-Ok $(if ($PreferCopy) { "Copied: $Label" } else { "Copied (symlink unavailable): $Label" })
        $script:STATS.Synced++
    } catch {
        Write-Fail "Failed: $Label -- $_"
        $script:STATS.Failed++
    }
}

# 目录同步：junction 优先（免管理员），symlink/Copy 兜底
function Sync-Directory {
    param([string]$SrcPath, [string]$DstPath, [string]$Label)

    if (-not (Test-Path $SrcPath)) {
        Write-Skip "Source dir missing: $Label"
        $script:STATS.Skipped++
        return
    }
    # 已是指向同一目标的联接/软链 → 跳过（幂等）
    if (-not $Force -and (IsLink $DstPath)) {
        $cur = (Get-Item -LiteralPath $DstPath -Force).Target
        if ($cur -and ([IO.Path]::GetFullPath("$cur") -ieq [IO.Path]::GetFullPath($SrcPath))) {
            Write-Skip "Unchanged (junction): $Label/"
            $script:STATS.Skipped++
            return
        }
    }

    $dstParent = Split-Path $DstPath -Parent
    if (-not (Test-Path $dstParent) -and -not $DryRun) {
        New-Item -ItemType Directory -Path $dstParent -Force | Out-Null
    }
    Remove-Target -Path $DstPath -Label "$Label/"

    if ($DryRun) {
        Write-Ok "Would junction: $Label/"
        $script:STATS.Synced++
        return
    }

    try {
        if (Test-IsAdmin) {
            New-Item -ItemType SymbolicLink -Path $DstPath -Target $SrcPath -Force | Out-Null
        } else {
            $r = & cmd.exe /c "mklink /J `"$DstPath`" `"$SrcPath`"" 2>&1
            if ($LASTEXITCODE -ne 0) { throw "mklink /J failed: $r" }
        }
        Write-Ok "Junction: $Label/"
        $script:STATS.Synced++
    } catch {
        try {
            Copy-Item $SrcPath $DstPath -Recurse -Force
            Write-Ok "Copied dir (junction unavailable): $Label/"
            $script:STATS.Synced++
        } catch {
            Write-Fail "Failed: $Label/ -- $_"
            $script:STATS.Failed++
        }
    }
}

# =============================================================
# Cursor local plugin claude-config（唯一 Always-Apply 规则通道）
# v11：直接从 SSOT 生成实体 .mdc，无 templates/ 镜像层
# =============================================================

function Deploy-CursorLocalPlugin {
    $localRoot = Join-Path $CURSOR_DIR "plugins\local"
    $install = Join-Path $localRoot "claude-config"
    $installRules = Join-Path $install "rules"
    $installManifestDir = Join-Path $install ".cursor-plugin"
    $installManifest = Join-Path $installManifestDir "plugin.json"

    if ($DryRun) {
        Write-Ok "Would refresh local plugin claude-config (real .mdc from SSOT)"
        $script:STATS.Synced++
        return
    }

    if (-not (Test-Path $localRoot)) {
        New-Item -ItemType Directory -Path $localRoot -Force | Out-Null
    }
    # 旧版本曾把 install 做成指向 templates 的 Junction — 换成实体目录
    if ((Test-Path $install) -and (IsLink $install)) {
        $null = & cmd.exe /c "rmdir `"$install`"" 2>&1
    }
    New-Item -ItemType Directory -Path $installManifestDir -Force | Out-Null
    New-Item -ItemType Directory -Path $installRules -Force | Out-Null

    $pluginVer = "11.0.0"
    try {
        $mfHead = Get-Content (Join-Path $CLAUDE_DIR "MANIFEST.yaml") -TotalCount 20 -ErrorAction Stop
        $vm = ($mfHead | Select-String -Pattern '^\s*version:\s*"?([0-9.]+)"?').Matches
        if ($vm.Count -gt 0) { $pluginVer = $vm[0].Groups[1].Value }
    } catch { }
    $stamp = Get-Date -Format "yyyyMMddHHmm"
    $manifestObj = [ordered]@{
        name        = "claude-config"
        displayName = "Claude Config Rules"
        description = "Global AI assistant rules from ~/.claude (SSOT). Refreshed by sync.ps1."
        version     = "$pluginVer+$stamp"
        author      = @{ name = "local" }
        rules       = "./rules/"
        keywords    = @("claude", "rules", "governance", "local")
    }
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($installManifest, ($manifestObj | ConvertTo-Json -Depth 5) + "`n", $utf8NoBom)

    # 规则来源：rules/*.md（除 README）+ manifest 特殊映射（00-CLAUDE / CURSOR-EDITOR）
    $pairs = [System.Collections.Generic.List[hashtable]]::new()
    Get-ChildItem (Join-Path $CLAUDE_DIR "rules") -Filter "*.md" -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -ne "README.md" } |
        ForEach-Object { $pairs.Add(@{ Src = $_.FullName; Dst = "$($_.BaseName).mdc" }) }
    foreach ($key in $PLUGIN_EXTRA.Keys) {
        $pairs.Add(@{ Src = (Join-Path $CLAUDE_DIR $PLUGIN_EXTRA[$key]); Dst = "$key.mdc" })
    }

    $expected = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    $expectedBases = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    $copied = 0
    foreach ($p in $pairs) {
        if (-not (Test-Path -LiteralPath $p.Src)) { continue }
        $null = $expected.Add($p.Dst)
        $base = [System.IO.Path]::GetFileNameWithoutExtension($p.Dst)
        $null = $expectedBases.Add($base)
        $dstPath = Join-Path $installRules $p.Dst
        $needCopy = $Force
        if (-not $needCopy) {
            try {
                if (-not (Test-Path -LiteralPath $dstPath)) { $needCopy = $true }
                elseif ((Get-FileHash -LiteralPath $p.Src -Algorithm SHA256).Hash -ne
                        (Get-FileHash -LiteralPath $dstPath -Algorithm SHA256).Hash) { $needCopy = $true }
            } catch { $needCopy = $true }
        }
        if (-not $needCopy) { continue }
        Remove-SameBasenameVariants -Directory $installRules -BaseName $base -LabelPrefix "plugin-rules"
        Copy-Item -LiteralPath $p.Src -Destination $dstPath -Force
        $copied++
    }

    # 孤儿清除：SSOT 已删的规则从 plugin 移除，保持列表精确
    Get-ChildItem $installRules -Filter "*.mdc" -ErrorAction SilentlyContinue | ForEach-Object {
        if (-not $expected.Contains($_.Name)) {
            Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
            Write-Fix "Removed stale plugin rule: $($_.Name)"
            $script:STATS.Removed++
        }
    }

    # Cursor 同时加载 ~/.cursor/rules 与 plugin → 双份 Always-Apply；个人 rules/ 清同名
    $cursorRules = Join-Path $CURSOR_DIR "rules"
    if (Test-Path $cursorRules) {
        foreach ($base in $expectedBases) {
            Remove-SameBasenameVariants -Directory $cursorRules -BaseName $base `
                -LabelPrefix "cursor-rules(dedupe-vs-plugin)"
        }
    }

    [System.IO.File]::WriteAllText(
        (Join-Path $install ".sync-stamp"),
        "synced=$stamp`nversion=$pluginVer+$stamp`nrules=$copied`n",
        $utf8NoBom
    )

    if (Test-Path $installManifest) {
        if ($copied -gt 0) {
            Write-Ok "Local plugin claude-config refreshed ($copied rules) -> plugins/local/claude-config"
        } else {
            Write-Ok "Local plugin claude-config unchanged (hash skip)"
        }
        $script:STATS.Synced++
    } else {
        Write-Fail "Failed refreshing local plugin claude-config (manifest missing)"
        $script:STATS.Failed++
    }
}

# =============================================================
# 通用编辑器规则通道（v11.1：qoder-cn rules/*.mdc、trae-cn user_rules/*.md 等）
# 实体复制 + hash 跳过；.claude-managed 台账记录管理集，
# 孤儿清除只删台账内条目 — 编辑器目录中用户自有规则不受影响
# =============================================================

function Deploy-EditorRules {
    param([string]$EditorName, [string]$EditorHome, [string]$ChannelDir, [string]$Ext)

    $rulesSrc = Join-Path $CLAUDE_DIR "rules"
    if (-not (Test-Path $rulesSrc)) { return }
    $rulesDst = Join-Path $EditorHome $ChannelDir

    if ($DryRun) {
        Write-Ok "Would refresh $EditorName rules -> $ChannelDir/*$Ext"
        $script:STATS.Synced++
        return
    }
    New-Item -ItemType Directory -Path $rulesDst -Force | Out-Null

    $ledgerPath = Join-Path $rulesDst ".claude-managed"
    $prevManaged = @()
    if (Test-Path -LiteralPath $ledgerPath) {
        $prevManaged = @(Get-Content -LiteralPath $ledgerPath -ErrorAction SilentlyContinue | Where-Object { $_ })
    }

    $expected = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    $copied = 0
    Get-ChildItem $rulesSrc -Filter "*.md" -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -ne "README.md" } | ForEach-Object {
        $dstName = "$($_.BaseName)$Ext"
        $null = $expected.Add($dstName)
        $dstPath = Join-Path $rulesDst $dstName
        $needCopy = $Force
        if (-not $needCopy) {
            try {
                if (-not (Test-Path -LiteralPath $dstPath)) { $needCopy = $true }
                elseif ((Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash -ne
                        (Get-FileHash -LiteralPath $dstPath -Algorithm SHA256).Hash) { $needCopy = $true }
            } catch { $needCopy = $true }
        }
        if ($needCopy) {
            Remove-SameBasenameVariants -Directory $rulesDst -BaseName $_.BaseName -LabelPrefix "$EditorName-rules"
            Copy-Item -LiteralPath $_.FullName -Destination $dstPath -Force
            $copied++
        }
    }

    # 孤儿清除：仅删「上次台账有、本次不再期望」的条目（SSOT 已删的规则）
    foreach ($old in $prevManaged) {
        if (-not $expected.Contains($old)) {
            $p = Join-Path $rulesDst $old
            if (Test-Path -LiteralPath $p) {
                Remove-Target -Path $p -Label "stale $EditorName-rules/$old"
            }
        }
    }

    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($ledgerPath, ((@($expected) | Sort-Object) -join "`n") + "`n", $utf8NoBom)

    if ($copied -gt 0) {
        Write-Ok "$EditorName rules refreshed ($copied) -> $ChannelDir/"
    } else {
        Write-Ok "$EditorName rules unchanged (hash skip)"
    }
    $script:STATS.Synced++
}

# =============================================================
# 项目脚手架（-Lint / -InitProject）：复制到 CWD，跳过已存在
# =============================================================

function Deploy-Templates {
    param([array]$TemplateList, [string]$ModeName)
    $cwd = (Get-Location).Path
    Write-Host ""
    Write-Host "  -- $ModeName -----------------------------------------" -ForegroundColor DarkGray
    Write-Host "  Target: $cwd" -ForegroundColor DarkGray
    Write-Host ""
    foreach ($item in $TemplateList) {
        $srcPath = Join-Path $CLAUDE_DIR $item.SrcRel
        $dstPath = Join-Path $cwd $item.DstName
        if (-not (Test-Path $srcPath)) {
            Write-Skip "Source missing: $($item.DstName)"
            $script:STATS.Skipped++
            continue
        }
        if (Test-Path $dstPath) {
            Write-Skip "Already exists (skip): $($item.DstName)"
            $script:STATS.Skipped++
            continue
        }
        if ($DryRun) {
            Write-Dry "Would copy: $($item.DstName)"
            $script:STATS.Synced++
            continue
        }
        try {
            Copy-Item $srcPath $dstPath -Force
            Write-Ok "Copied: $($item.DstName)"
            $script:STATS.Synced++
        } catch {
            Write-Fail "Failed: $($item.DstName) -- $_"
            $script:STATS.Failed++
        }
    }
    Write-Host ""
}

# =============================================================
# 可选 OPT-IN：项目级 Cursor Project Rules（默认关闭）
# =============================================================

function Deploy-ProjectRules {
    param([string]$ProjectRoot)
    $rootFull = [System.IO.Path]::GetFullPath($ProjectRoot)
    $claudeFull = [System.IO.Path]::GetFullPath($CLAUDE_DIR)
    $projectRulesDir = Join-Path $rootFull ".cursor\rules"

    Write-Host "  -- project-rules --------------------------------------" -ForegroundColor DarkGray
    Write-Host "  Target: $projectRulesDir" -ForegroundColor DarkGray

    if ($rootFull.TrimEnd('\') -ieq $claudeFull.TrimEnd('\')) {
        Write-Skip "Target is ~/.claude — skip ProjectRules mirror (plugin-only; avoids Settings duplicates)"
        $script:STATS.Skipped++
        Write-Host ""
        return
    }
    if (-not (Test-Path $rootFull)) {
        Write-Fail "Project root not found: $rootFull"
        $script:STATS.Failed++
        Write-Host ""
        return
    }

    # 与 plugin 同一套载荷：CORE 必投；-All 时全量 rules；+00-CLAUDE/CURSOR-EDITOR
    Sync-File -SrcPath (Join-Path $CLAUDE_DIR "rules\CORE.md") `
        -DstPath (Join-Path $projectRulesDir "CORE.mdc") -Label "project rules/CORE.mdc"
    foreach ($key in $PLUGIN_EXTRA.Keys) {
        $src = Join-Path $CLAUDE_DIR $PLUGIN_EXTRA[$key]
        if (Test-Path $src) {
            Sync-File -SrcPath $src -DstPath (Join-Path $projectRulesDir "$key.mdc") `
                -Label "project rules/$key.mdc" -PreferCopy
        }
    }
    if ($All) {
        Get-ChildItem (Join-Path $CLAUDE_DIR "rules") -Filter "*.md" -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -ne "README.md" -and $_.BaseName -ne "CORE" } |
            Sort-Object Name |
            ForEach-Object {
                Sync-File -SrcPath $_.FullName -DstPath (Join-Path $projectRulesDir "$($_.BaseName).mdc") `
                    -Label "project rules/$($_.BaseName).mdc"
            }
    }
    Write-Host ""
}

# =============================================================
# Main
# =============================================================

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  Claude Config Multi-Editor Sync v20.0 (1+N)" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""
$presentEditors = @($EDITOR_TARGETS.Keys | Where-Object {
    $EDITOR_TARGETS[$_].Enabled -and (Test-Path $EDITOR_TARGETS[$_].Home) })
Write-Host "  Source : $CLAUDE_DIR" -ForegroundColor DarkGray
Write-Host "  Target : cursor$(if ($presentEditors) { ' + ' + ($presentEditors -join ' + ') }) (Claude Code reads ~/.claude natively)" -ForegroundColor DarkGray
Write-Host "  Mode   : $MODE_LABEL" -ForegroundColor DarkGray
if ($DryRun) {
    Write-Host "  [DRY RUN] Preview only -- no changes will be made" -ForegroundColor Yellow
}
Write-Host ""

if ($Lint) {
    Deploy-Templates -TemplateList $LINT_TEMPLATES -ModeName "Lint Templates"
} elseif ($InitProject) {
    Deploy-Templates -TemplateList $PROJECT_TEMPLATES -ModeName "Project-Init Templates"
}

if (-not $SKIP_EDITOR_SYNC) {
    if (-not (Test-Path $CURSOR_DIR)) {
        Write-Skip "~/.cursor not found — nothing to sync (Claude Code needs no sync)"
        $script:STATS.Skipped++
    } else {
        Write-Host "  -- cursor -------------------------------------------" -ForegroundColor DarkGray

        # ---- 1. 根文件 6 项（软链）----
        foreach ($name in $ROOT_FILES) {
            Sync-File -SrcPath (Join-Path $CLAUDE_DIR $name) `
                -DstPath (Join-Path $CURSOR_DIR $name) -Label "$name -> cursor"
        }
        # 根文件孤儿清除：manifest 已移除的旧根文件（如 CLAUDE-ROUTER.mdc / agent.yaml）
        $legacyRoot = @("CLAUDE-ROUTER.mdc", "agent.yaml")
        foreach ($stale in $legacyRoot) {
            $p = Join-Path $CURSOR_DIR $stale
            if (Test-Path $p) { Remove-Target -Path $p -Label "stale root/$stale -> cursor" }
        }

        # ---- 2. Local plugin（唯一规则通道）----
        Deploy-CursorLocalPlugin

        # ---- 3. skills/ agents/ junction（-Skills / -All）----
        if ($Skills -or $All) {
            Sync-Directory -SrcPath (Join-Path $CLAUDE_DIR "skills") `
                -DstPath (Join-Path $CURSOR_DIR "skills") -Label "skills -> cursor"
        }
        if ($All) {
            Sync-Directory -SrcPath (Join-Path $CLAUDE_DIR "agents") `
                -DstPath (Join-Path $CURSOR_DIR "agents") -Label "agents -> cursor"
        }

        Write-Host ""
    }

    # ---- 4. 其他编辑器（v11.1 恢复；清单单源 sync-manifest.json editors 段，home 缺席自动跳过）----
    foreach ($ed in @($EDITOR_TARGETS.Keys)) {
        $cfg = $EDITOR_TARGETS[$ed]
        if (-not $cfg.Enabled) { continue }
        if (-not (Test-Path $cfg.Home)) {
            Write-Skip "$ed`: $($cfg.Home) not found - skipped"
            $script:STATS.Skipped++
            continue
        }
        Write-Host "  -- $ed $('-' * [Math]::Max(1, 45 - $ed.Length))" -ForegroundColor DarkGray

        if ($cfg.Special -eq "claude_md_plus_skills") {
            # workbuddy：仅 CLAUDE.md + skills/ 联接；SOUL/USER/IDENTITY/BOOTSTRAP 自有命名空间禁触
            Sync-File -SrcPath (Join-Path $CLAUDE_DIR "CLAUDE.md") `
                -DstPath (Join-Path $cfg.Home "CLAUDE.md") -Label "CLAUDE.md -> $ed"
            Sync-Directory -SrcPath (Join-Path $CLAUDE_DIR "skills") `
                -DstPath (Join-Path $cfg.Home "skills") -Label "skills -> $ed"
        } else {
            if ($cfg.RootIndex) {
                foreach ($name in $ROOT_FILES) {
                    Sync-File -SrcPath (Join-Path $CLAUDE_DIR $name) `
                        -DstPath (Join-Path $cfg.Home $name) -Label "$name -> $ed"
                }
                # 根文件孤儿清除（v11 已并入的旧根文件）
                foreach ($stale in @("CLAUDE-ROUTER.mdc", "agent.yaml")) {
                    $p = Join-Path $cfg.Home $stale
                    if (Test-Path $p) { Remove-Target -Path $p -Label "stale root/$stale -> $ed" }
                }
            }
            if ($cfg.RulesChannel) {
                Deploy-EditorRules -EditorName $ed -EditorHome $cfg.Home `
                    -ChannelDir $cfg.RulesChannel -Ext $cfg.RulesExt
            }
        }
        Write-Host ""
    }
}

if (($ProjectRules -or $ProjectRulesPath) -and -not $SKIP_EDITOR_SYNC) {
    $targets = [System.Collections.Generic.List[string]]::new()
    if ($ProjectRules) { $targets.Add((Get-Location).Path) }
    if ($ProjectRulesPath) {
        foreach ($part in ($ProjectRulesPath -split '[;,]')) {
            $p = $part.Trim().Trim('"')
            if ($p) { $targets.Add($p) }
        }
    }
    foreach ($t in $targets) { Deploy-ProjectRules -ProjectRoot $t }
}

# =============================================================
# Summary
# =============================================================

Write-Host "  =====================================================" -ForegroundColor DarkGray
Write-Host "  $(if ($DryRun) { 'Dry run complete' } else { 'Sync complete' })" -ForegroundColor Green
Write-Host ""
Write-Host "  $(if ($DryRun) { 'Would sync' } else { 'Synced' })      : $($script:STATS.Synced)" -ForegroundColor White
Write-Host "  Removed     : $($script:STATS.Removed)" -ForegroundColor White
Write-Host "  Skipped     : $($script:STATS.Skipped)" -ForegroundColor White
if ($script:STATS.Failed -gt 0) {
    Write-Host "  Failed      : $($script:STATS.Failed)" -ForegroundColor Red
}
Write-Host ""
Write-Host "  Mode        : $MODE_LABEL" -ForegroundColor DarkGray
Write-Host "  Root files  : $($ROOT_FILES -join ', ') (single source: config/sync-manifest.json)" -ForegroundColor DarkGray
Write-Host "  Rules       : cursor=local plugin .mdc; qoder-cn=rules/*.mdc; trae-cn=user_rules/*.md; workbuddy=CLAUDE.md+skills only" -ForegroundColor DarkGray
Write-Host "  Editors     : cursor$(if ($presentEditors) { ' + ' + ($presentEditors -join ' + ') }) (absent homes auto-skipped)" -ForegroundColor DarkGray
Write-Host "  Excluded    : hooks/ scripts/ MCP configs plugins/ commands/ settings.json" -ForegroundColor DarkGray
Write-Host ""

# v11: 知识图谱刷新块已移除 — codegraph v1.5 MCP server 自带文件监听自动同步
# （watcher + connect-time catch-up），无需脚本触发；codebase-memory 已永久禁用。
