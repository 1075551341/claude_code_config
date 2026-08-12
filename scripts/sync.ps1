<#
.SYNOPSIS
    Claude Code multi-editor layered sync script v18.4
    Modes: default (all rules + Cursor claude-config) | -Skills (+ skills/) | -All (+ agents)
    Project: -Lint (prettier+eslint) | -InitProject (CLAUDE.md+MANIFEST+.env+.gitignore)

.DESCRIPTION
    Default: sync all rules/*.md (symlink) + CLAUDE.md + Cursor local plugin claude-config
    -Skills: additionally sync skills/ directory
    -All:    also sync agents/ (+ skills if not already)
    -DryRun: preview only, no disk writes
    -Lint:   deploy prettier + eslint templates to current project (skip existing)
    -InitProject: deploy project-init templates to current project (skip existing)

    Sync method: symbolic link preferred, Copy-Item fallback
    Cursor: sync ONLY to personal ~/.cursor (rules/skills/agents) — never into
      business project trees unless -ProjectRules / -ProjectRulesPath is explicit.
    Cursor rules channel: local plugin ONLY. ~/.cursor/rules is actively deduped
      against the plugin (same basename removed) — Cursor would otherwise load
      Always-Apply rules twice. Do not expect global rules to land there.
    Cursor Settings visibility: every run refreshes plugins/local/claude-config
      (real .mdc copies from SSOT — plugin forbids external symlinks).
    -ProjectRules: OPTIONAL opt-in for <CWD>/.cursor/rules (default OFF).
    Before syncing: delete same-basename siblings in the target dir
      (any extension / case — e.g. CORE.md + core.mdc before writing CORE.mdc)
    Rules extension: cursor/qoder/codearts -> .mdc, trae -> .md
    WorkBuddy: CLAUDE.md + skills/ only (no rules/ channel)

    Excluded: hooks/ scripts/ MCP configs plugins/ commands/ settings.json

.PARAMETER DryRun
    Preview only, do not execute actual operations

.PARAMETER Skills
    Additionally sync the skills/ directory

.PARAMETER All
    Full sync: rules + skills + agents + CLAUDE.md

.PARAMETER ProjectRules
    Also deploy Cursor rules (L0, or all rules with -All) into the current
    working directory's .cursor/rules (Project Rules for Settings UI).
    Does NOT write into ~/.claude/.cursor/rules by default (that caused
    duplicate CORE/ROUTER entries when the config repo was the open workspace).

.PARAMETER ProjectRulesPath
    Deploy Project Rules into one or more absolute project roots (semicolon-
    or comma-separated). Same payload as -ProjectRules but ignores CWD.
    Example: -All -ProjectRulesPath "D:\apdms\pdms\pdms-teoms2"

.PARAMETER Lint
    Deploy prettier + eslint 9 flat config templates to current working directory.
    Copies .prettierrc.json, .prettierignore, eslint.config.js (skip if exists).

.PARAMETER InitProject
    Deploy project-init templates to current working directory.
    Copies CLAUDE.md, MANIFEST.yaml, .env.example, .gitignore (skip if exists).

.PARAMETER Scope
    Cursor Guard 契约参数（sync_runner.py 调用）：rules | indexes | all
    all=等价 -All；rules=默认 L0 模式；indexes=仅入口文件，跳过全量 rules。

.PARAMETER Force
    配合 -Scope 使用，跳过变更检测强制重写。

.EXAMPLE
    # ---- 日常同步 ----
    pwsh -ExecutionPolicy Bypass -File sync.ps1                    # 默认：8 个根索引 + 全量 rules + Cursor 插件
    pwsh -ExecutionPolicy Bypass -File sync.ps1 -Skills            # 追加 skills/
    pwsh -ExecutionPolicy Bypass -File sync.ps1 -All               # 全量：rules + skills + agents
    pwsh -ExecutionPolicy Bypass -File sync.ps1 -All -DryRun       # 预演，不落盘

    # ---- 项目级投放（默认关闭，需显式开启）----
    pwsh -ExecutionPolicy Bypass -File sync.ps1 -ProjectRules      # 投放到当前目录 .cursor/rules
    pwsh -ExecutionPolicy Bypass -File sync.ps1 -All -ProjectRules
    pwsh -ExecutionPolicy Bypass -File sync.ps1 -All -ProjectRulesPath "D:\apdms\pdms\pdms-teoms2"

    # ---- 项目脚手架 ----
    powershell -ExecutionPolicy Bypass -File sync.ps1 -Lint        # 投放 prettier + eslint 模板
    powershell -ExecutionPolicy Bypass -File sync.ps1 -InitProject # 投放 CLAUDE.md/MANIFEST/.env/.gitignore

    # ---- Cursor Guard 自动调用（一般不手敲）----
    pwsh -File sync.ps1 -Scope indexes
    pwsh -File sync.ps1 -Scope all -Force

.NOTES
    验证与回归：
      powershell -File scripts/check.ps1              # 同步结果健康检查
      powershell -File scripts/test-sync-dedup.ps1    # 去重逻辑回归
    Linux/macOS 等价物：bash scripts/sync.sh full
#>
# 注意：#Requires 必须放在帮助块之后，否则 Get-Help 读不到上面的命令示例。
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

# Scope normalization (Cursor Guard contract). -Force skips change detection.
#   all     -> full sync (-All semantics: rules + skills + agents + plugin)
#   rules   -> default L0 mode (root files + L0 rules + plugin + full rules)
#   indexes -> entry-level only (root files + L0 rules + plugin, skip full rules)
$IndexesOnly = $false
if ($Scope -eq "all") { $All = $true }
if ($Scope -eq "indexes") { $IndexesOnly = $true }
if ($All) { $IndexesOnly = $false }

# =============================================================
# Configuration
# =============================================================

$CLAUDE_DIR = "$env:USERPROFILE\.claude"

# Target editor base directories
# Supported: cursor / trae(+cn) / qoder(+cn) / workbuddy / codearts
$TARGETS = [ordered]@{
    "cursor"    = "$env:USERPROFILE\.cursor"
    "qoder"     = "$env:USERPROFILE\.qoder"
    "qoder-cn"  = "$env:USERPROFILE\.qoder-cn"
    "trae"      = "$env:USERPROFILE\.trae"
    "trae-cn"   = "$env:USERPROFILE\.trae-cn"
    "workbuddy" = "$env:USERPROFILE\.workbuddy"
    "codearts"  = "$env:USERPROFILE\.codeartsdoer"
}

# Rules subdirectory name within each target base
# workbuddy: placeholder only — rules sync skipped (no native rules channel)
$RULES_SUBDIR = [ordered]@{
    "cursor"    = "rules"
    "qoder"     = "rules"
    "qoder-cn"  = "rules"
    "trae"      = "user_rules"
    "trae-cn"   = "user_rules"
    "workbuddy" = "rules"
    "codearts"  = "rule"
}

# Rules file extension per editor
$RULES_EXT = [ordered]@{
    "cursor"    = ".mdc"
    "qoder"     = ".mdc"
    "qoder-cn"  = ".mdc"
    "trae"      = ".md"
    "trae-cn"   = ".md"
    "workbuddy" = ".md"
    "codearts"  = ".mdc"
}

# L0 entry rules: deployed into rules/ subdirectory (extension converted per editor)
$L0_RULE_ITEMS = @(
    @{ SrcRel = "rules/CORE.md"; DstBase = "CORE" }
)

# L0 root files: deployed to editor root directory (name preserved)
# v18.4: IndexFile items are the router's Tool-First chain (总纲 -> 归属矩阵 -> 三索引).
# Agents Read them by editor-relative path, so every editor with a rules channel needs them —
# v18.3 shipped them to Cursor only, which left qoder/trae/codearts unable to resolve the chain.
# Kept identical across sync.ps1 / sync.sh / check.ps1 / impact_sync.SYNC_FILES.
$L0_ROOT_ITEMS = @(
    @{ SrcRel = "CLAUDE.md";         DstName = "CLAUDE.md";         PerEditorName = $true }
    @{ SrcRel = "CLAUDE-ROUTER.mdc"; DstName = "CLAUDE-ROUTER.mdc"; IndexFile = $true }
    @{ SrcRel = "SPEC.md";           DstName = "SPEC.md";           IndexFile = $true }
    @{ SrcRel = "MANIFEST.yaml";     DstName = "MANIFEST.yaml";     IndexFile = $true }
    @{ SrcRel = "agent.yaml";        DstName = "agent.yaml";        IndexFile = $true }
    @{ SrcRel = "skills-INDEX.md";   DstName = "skills-INDEX.md";   IndexFile = $true }
    @{ SrcRel = "agents-INDEX.md";   DstName = "agents-INDEX.md";   IndexFile = $true }
    @{ SrcRel = "rules-INDEX.md";    DstName = "rules-INDEX.md";    IndexFile = $true }
)

# Editors that receive CLAUDE.md only (no index root files).
# workbuddy has no rules channel and owns its root namespace (SOUL/USER/IDENTITY/BOOTSTRAP);
# dropping 7 more files there would collide with its own bootstrap contract.
$ROOT_INDEX_SKIP_EDITORS = @("workbuddy")

# L0 root file destination name per editor (override DstName when needed)
$L0_ROOT_DSTNAME = [ordered]@{
    "cursor"    = "CLAUDE.md"
    "qoder"     = "CLAUDE.md"
    "qoder-cn"  = "CLAUDE.md"
    "trae"      = "CLAUDE.md"
    "trae-cn"   = "CLAUDE.md"
    "workbuddy" = "CLAUDE.md"
    "codearts"  = "CLAUDE.md"
}

# Editors that skip rules/ softlinks (native channel differs or absent)
$RULES_SKIP_EDITORS = @("cursor", "workbuddy")

# CLAUDE-ROUTER source (deployed as 00-CLAUDE-ROUTER.{ext} into rules/)
$ROUTER_SRC_REL = "CLAUDE-ROUTER.mdc"
$ROUTER_DST_BASE = "00-CLAUDE-ROUTER"

# ─── -Lint: prettier + eslint template files (copy to CWD, skip existing) ───
$LINT_TEMPLATES = @(
    @{ SrcRel = "templates/lint/.prettierrc.json"; DstName = ".prettierrc.json" }
    @{ SrcRel = "templates/lint/.prettierignore";  DstName = ".prettierignore" }
    @{ SrcRel = "templates/lint/eslint.config.js"; DstName = "eslint.config.js" }
)

# ─── -InitProject: project bootstrap files (copy to CWD, skip existing) ───
$PROJECT_TEMPLATES = @(
    @{ SrcRel = "templates/project-init/CLAUDE.md";     DstName = "CLAUDE.md" }
    @{ SrcRel = "templates/project-init/MANIFEST.yaml"; DstName = "MANIFEST.yaml" }
    @{ SrcRel = "templates/project-init/.env.example";  DstName = ".env.example" }
    @{ SrcRel = "templates/project-init/.gitignore";    DstName = ".gitignore" }
)

# Statistics
$script:STATS = @{ Synced = 0; Removed = 0; Skipped = 0; Failed = 0 }

# =============================================================
# Build sync item lists based on mode flags
# =============================================================

# Directory sync items
$DIR_SYNC_ITEMS = @()
if ($Skills -or $All) {
    $DIR_SYNC_ITEMS += @{ SrcRel = "skills"; DstRel = "skills" }
}
if ($All) {
    $DIR_SYNC_ITEMS += @{ SrcRel = "agents"; DstRel = "agents" }
}

# Determine mode label
$MODE_LABEL = "all rules + Cursor claude-config"
if ($Skills) { $MODE_LABEL = "$MODE_LABEL + skills/" }
if ($All)    { $MODE_LABEL = "ALL (rules + skills + agents + claude-config)" }
if ($ProjectRules) { $MODE_LABEL = "$MODE_LABEL + CWD ProjectRules" }
if ($ProjectRulesPath) { $MODE_LABEL = "$MODE_LABEL + ProjectRulesPath" }
if ($Lint)       { $MODE_LABEL = "Lint templates -> CWD" }
if ($InitProject) { $MODE_LABEL = "Project-init templates -> CWD" }
# Lint/InitProject are standalone modes — skip editor sync entirely
$SKIP_EDITOR_SYNC = $Lint -or $InitProject

# =============================================================
# Utility functions
# =============================================================

function Write-Ok   { param($m) Write-Host "    [OK]  $m" -ForegroundColor Green }
function Write-Fail { param($m) Write-Host "    [XX]  $m" -ForegroundColor Red }
function Write-Skip { param($m) Write-Host "    [--]  $m" -ForegroundColor DarkGray }
function Write-Fix  { param($m) Write-Host "    [FIX] $m" -ForegroundColor DarkCyan }
function Write-Info { param($m) Write-Host "  >> $m" -ForegroundColor Cyan }
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

# =============================================================
# Dedup: remove target path (file or directory) before syncing
# =============================================================

function Remove-Target {
    param(
        [string]$Path,
        [string]$Label
    )
    if (-not (Test-Path $Path)) { return }

    if ($DryRun) {
        if (Test-Path $Path -PathType Container) {
            Write-Dry "Would remove dir : $Label"
        } else {
            Write-Dry "Would remove file: $Label"
        }
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

# Same-type same-name: purge ALL siblings with same basename (any ext / case)
# e.g. before writing rules/CORE.mdc, also remove CORE.md / core.mdc / Core.MD
function Remove-SameBasenameVariants {
    param(
        [string]$Directory,
        [string]$BaseName,
        [string]$LabelPrefix
    )
    if (-not $Directory -or -not (Test-Path $Directory)) { return }
    if ([string]::IsNullOrWhiteSpace($BaseName)) { return }

    $matches = @(Get-ChildItem -LiteralPath $Directory -File -Force -ErrorAction SilentlyContinue |
        Where-Object { $_.BaseName -ieq $BaseName })
    foreach ($f in $matches) {
        $lbl = if ($LabelPrefix) { "$LabelPrefix/$($f.Name)" } else { $f.Name }
        Remove-Target -Path $f.FullName -Label $lbl
    }
}

# =============================================================
# Sync a single file (symlink -> fallback Copy-Item)
# =============================================================

function Sync-File {
    param(
        [string]$SrcPath,
        [string]$DstPath,
        [string]$Label,
        [switch]$PreferCopy
    )

    if (-not (Test-Path $SrcPath)) {
        Write-Skip "Source missing: $Label"
        $script:STATS.Skipped++
        return
    }

    # Change detection: skip identical targets unless -Force (Cursor Guard contract)
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

    # Ensure parent directory exists
    $dstDir = Split-Path $DstPath -Parent
    if (-not (Test-Path $dstDir) -and -not $DryRun) {
        New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
    }

    # Dedup: same-basename siblings (any ext/case) then exact path
    $dstBase = [System.IO.Path]::GetFileNameWithoutExtension($DstPath)
    $scopeName = Split-Path $dstDir -Leaf
    Remove-SameBasenameVariants -Directory $dstDir -BaseName $dstBase -LabelPrefix "$scopeName"
    Remove-Target -Path $DstPath -Label $Label

    if ($DryRun) {
        if ($PreferCopy) {
            Write-Ok "Would copy (Settings-safe): $Label"
        } else {
            Write-Ok "Would symlink: $Label"
        }
        $script:STATS.Synced++
        return
    }

    # Prefer symlink; PreferCopy forces copy (legacy/rare). Fallback to copy if symlink fails.
    if (-not $PreferCopy) {
        $linkErr = $null
        try {
            # Prefer cmd mklink on Windows — New-Item SymbolicLink is flaky under
            # $ErrorActionPreference=Stop in some PS 5.1 hosts (silently fails → copy).
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

    # Copy-Item fallback when symlink unavailable
    try {
        Copy-Item $SrcPath $DstPath -Force
        if ($PreferCopy) {
            Write-Ok "Copied (Settings-safe): $Label"
        } else {
            Write-Ok "Copied (symlink unavailable): $Label"
        }
        $script:STATS.Synced++
    } catch {
        Write-Fail "Failed: $Label -- $_"
        $script:STATS.Failed++
    }
}

# =============================================================
# Sync a directory (junction -> fallback Copy-Item -Recurse)
# =============================================================

function Sync-Directory {
    param(
        [string]$SrcPath,
        [string]$DstPath,
        [string]$Label
    )

    if (-not (Test-Path $SrcPath)) {
        Write-Skip "Source dir missing: $Label"
        $script:STATS.Skipped++
        return
    }

    # Ensure parent directory exists
    $dstParent = Split-Path $DstPath -Parent
    if (-not (Test-Path $dstParent) -and -not $DryRun) {
        New-Item -ItemType Directory -Path $dstParent -Force | Out-Null
    }

    # Dedup: remove existing target first
    Remove-Target -Path $DstPath -Label "$Label/"

    if ($DryRun) {
        Write-Ok "Would junction: $Label/"
        $script:STATS.Synced++
        return
    }

    # Try directory junction or symbolic link
    try {
        if (Test-IsAdmin) {
            New-Item -ItemType SymbolicLink -Path $DstPath -Target $SrcPath -Force | Out-Null
        } else {
            $r = & cmd.exe /c "mklink /J `"$DstPath`" `"$SrcPath`"" 2>&1
            if ($LASTEXITCODE -ne 0) { throw "mklink /J failed: $r" }
        }
        Write-Ok "Junction: $Label/"
        $script:STATS.Synced++
        return
    } catch {
        # Junction failed, fall through to copy
    }

    # Fallback: Copy-Item -Recurse
    try {
        Copy-Item $SrcPath $DstPath -Recurse -Force
        Write-Ok "Copied dir (junction unavailable): $Label/"
        $script:STATS.Synced++
    } catch {
        Write-Fail "Failed: $Label/ -- $_"
        $script:STATS.Failed++
    }
}

# =============================================================
# Cursor local plugin: surface global .mdc rules in Settings → User
# (~/.cursor/rules files are NOT listed in User tab — Cursor UI limit)
# =============================================================

function Deploy-CursorLocalPlugin {
    # Cursor rejects plugin rules that symlink outside the plugin tree
    # (plugin-quality-gates: paths must stay inside plugin dir). Working
    # marketplace plugins (exa) use real .mdc files + "rules": "./rules/".
    # Every sync.ps1 run refreshes copies from ~/.claude SSOT so Settings stay current.
    $localRoot = Join-Path $env:USERPROFILE ".cursor\plugins\local"
    $install = Join-Path $localRoot "claude-config"
    $installRules = Join-Path $install "rules"
    $installManifestDir = Join-Path $install ".cursor-plugin"
    $installManifest = Join-Path $installManifestDir "plugin.json"
    $tplSrc = Join-Path $CLAUDE_DIR "templates\cursor-claude-config-plugin"
    $tplManifest = Join-Path $tplSrc ".cursor-plugin\plugin.json"
    $tplRules = Join-Path $tplSrc "rules"

    if ($DryRun) {
        Write-Ok "Would refresh local plugin claude-config (real .mdc copies from SSOT)"
        $script:STATS.Synced++
        return
    }

    if (-not (Test-Path $localRoot)) {
        New-Item -ItemType Directory -Path $localRoot -Force | Out-Null
    }
    # If prior install was a Junction to template, replace with real directory
    if ((Test-Path $install) -and (IsLink $install)) {
        $null = & cmd.exe /c "rmdir `"$install`"" 2>&1
    }
    New-Item -ItemType Directory -Path $installManifestDir -Force | Out-Null
    New-Item -ItemType Directory -Path $installRules -Force | Out-Null
    New-Item -ItemType Directory -Path (Split-Path $tplManifest -Parent) -Force | Out-Null
    New-Item -ItemType Directory -Path $tplRules -Force | Out-Null

    $pluginVer = "10.7.0"
    try {
        $mf = Get-Content (Join-Path $CLAUDE_DIR "MANIFEST.yaml") -TotalCount 20 -ErrorAction Stop
        $vm = ($mf | Select-String -Pattern '^\s*version:\s*"?([0-9.]+)"?').Matches
        if ($vm.Count -gt 0) { $pluginVer = $vm[0].Groups[1].Value }
    } catch { }
    $stamp = Get-Date -Format "yyyyMMddHHmm"
    # JSON lines: prefer single quotes so PS5.1 does not treat braces as script blocks
    $manifestObj = [ordered]@{
        name        = "claude-config"
        displayName = "Claude Config Rules"
        description = "Global AI assistant rules from ~/.claude (SSOT). Refreshed by sync.ps1."
        version     = "$pluginVer+$stamp"
        author      = @{ name = "local" }
        rules       = "./rules/"
        keywords    = @("claude", "rules", "governance", "local")
    }
    $manifestBody = ($manifestObj | ConvertTo-Json -Depth 5)
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($installManifest, $manifestBody + "`n", $utf8NoBom)
    [System.IO.File]::WriteAllText($tplManifest, $manifestBody + "`n", $utf8NoBom)

    $pairs = [System.Collections.Generic.List[hashtable]]::new()
    Get-ChildItem (Join-Path $CLAUDE_DIR "rules") -Filter "*.md" -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -ne "README.md" } |
        ForEach-Object { $pairs.Add(@{ Src = $_.FullName; Dst = "$($_.BaseName).mdc" }) }
    $pairs.Add(@{ Src = (Join-Path $CLAUDE_DIR "CLAUDE-ROUTER.mdc"); Dst = "00-CLAUDE-ROUTER.mdc" })
    $pairs.Add(@{
            Src = (Join-Path $CLAUDE_DIR "templates\cursor-guard\rules\CURSOR-EDITOR.mdc")
            Dst = "CURSOR-EDITOR.mdc"
        })

    $expected = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    $expectedBases = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    $copied = 0
    foreach ($p in $pairs) {
        if (-not (Test-Path -LiteralPath $p.Src)) { continue }
        $null = $expected.Add($p.Dst)
        $base = [System.IO.Path]::GetFileNameWithoutExtension($p.Dst)
        $null = $expectedBases.Add($base)
        $dstPath = Join-Path $installRules $p.Dst
        $dstTpl = Join-Path $tplRules $p.Dst
        # Change detection: copy only when content differs (unless -Force)
        $needCopy = $Force
        if (-not $needCopy) {
            try {
                $srcHash = (Get-FileHash -LiteralPath $p.Src -Algorithm SHA256).Hash
                foreach ($dst in @($dstPath, $dstTpl)) {
                    if (-not (Test-Path -LiteralPath $dst)) { $needCopy = $true; break }
                    if ((Get-FileHash -LiteralPath $dst -Algorithm SHA256).Hash -ne $srcHash) { $needCopy = $true; break }
                }
            } catch { $needCopy = $true }
        }
        if (-not $needCopy) { continue }
        # 同步前先删同类型同名，避免残留双份（.md/.mdc/大小写）
        Remove-SameBasenameVariants -Directory $installRules -BaseName $base -LabelPrefix "plugin-rules"
        Remove-SameBasenameVariants -Directory $tplRules -BaseName $base -LabelPrefix "plugin-tpl-rules"
        Copy-Item -LiteralPath $p.Src -Destination $dstPath -Force
        Copy-Item -LiteralPath $p.Src -Destination $dstTpl -Force
        $copied++
    }

    # Purge orphaned .mdc removed from SSOT (keeps plugin list exact)
    Get-ChildItem $installRules -Filter "*.mdc" -ErrorAction SilentlyContinue | ForEach-Object {
        if (-not $expected.Contains($_.Name)) {
            Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
            Write-Fix "Removed stale plugin rule: $($_.Name)"
            $script:STATS.Removed++
        }
    }
    Get-ChildItem $tplRules -Filter "*.mdc" -ErrorAction SilentlyContinue | ForEach-Object {
        if (-not $expected.Contains($_.Name)) {
            Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
        }
    }

    # Cursor 同时加载 ~/.cursor/rules 与 local plugin → UI/Agent 双份 Always Apply。
    # 全局 SSOT 规则只走 plugin；从个人 rules/ 清除同 basename，杜绝如图重复。
    $cursorRules = Join-Path $env:USERPROFILE ".cursor\rules"
    if (Test-Path $cursorRules) {
        foreach ($base in $expectedBases) {
            Remove-SameBasenameVariants -Directory $cursorRules -BaseName $base `
                -LabelPrefix "cursor-rules(dedupe-vs-plugin)"
        }
    }

    # Sync stamp for diagnostics
    [System.IO.File]::WriteAllText(
        (Join-Path $install ".sync-stamp"),
        "synced=$stamp`nversion=$pluginVer+$stamp`nrules=$copied`n",
        $utf8NoBom
    )

    if (Test-Path $installManifest) {
        if ($copied -gt 0) {
            Write-Ok "Local plugin claude-config refreshed ($copied rules) -> plugins/local/claude-config"
            Write-Ok "Deduped ~/.cursor/rules vs plugin (same basename removed; User UI = plugin only)"
            $script:STATS.Synced++
        } else {
            # v10.11: 无变更（hash 跳过）也是同步成功——不误报 Failed（原 $copied -gt 0 条件在稳定状态下恒失败）
            Write-Ok "Local plugin claude-config unchanged ($copied rules, hash skip)"
        }
    } else {
        Write-Fail "Failed refreshing local plugin claude-config (manifest missing)"
        $script:STATS.Failed++
    }
}

# =============================================================
# Sync a rule file (with extension conversion for target editor)
# =============================================================

function Sync-RuleFile {
    param(
        [string]$SrcRelPath,
        [string]$DstBaseName,
        [string]$TargetRulesDir,
        [string]$EditorExt,
        [string]$EditorName
    )

    $srcPath = Join-Path $CLAUDE_DIR $SrcRelPath
    $dstName = "$DstBaseName$EditorExt"
    $dstPath = Join-Path $TargetRulesDir $dstName
    $label = "rules/$dstName -> $EditorName"

    # Prefer symlink for all editors (including Cursor personal ~/.cursor/rules).
    # PreferCopy only when caller passes it (rare); default = symlink → copy fallback.
    Sync-File -SrcPath $srcPath -DstPath $dstPath -Label $label
}

# =============================================================
# Deploy template files to current working directory (skip existing)
# Used by -Lint and -InitProject flags
# =============================================================

function Deploy-Templates {
    param(
        [array]$TemplateList,
        [string]$ModeName
    )

    $cwd = (Get-Location).Path
    Write-Host ""
    Write-Host "  -- $ModeName -----------------------------------------" -ForegroundColor DarkGray
    Write-Host "  Target: $cwd" -ForegroundColor DarkGray
    Write-Host ""

    foreach ($item in $TemplateList) {
        $srcPath = Join-Path $CLAUDE_DIR $item.SrcRel
        $dstPath = Join-Path $cwd $item.DstName
        $label = "$($item.DstName)"

        if (-not (Test-Path $srcPath)) {
            Write-Skip "Source missing: $label"
            $script:STATS.Skipped++
            continue
        }

        # Skip existing files (do not overwrite customizations)
        if (Test-Path $dstPath) {
            Write-Skip "Already exists (skip): $label"
            $script:STATS.Skipped++
            continue
        }

        if ($DryRun) {
            Write-Dry "Would copy: $label"
            $script:STATS.Synced++
            continue
        }

        try {
            Copy-Item $srcPath $dstPath -Force
            Write-Ok "Copied: $label"
            $script:STATS.Synced++
        } catch {
            Write-Fail "Failed: $label -- $_"
            $script:STATS.Failed++
        }
    }

    Write-Host ""
}

# =============================================================
# Print header
# =============================================================

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  Claude Code Multi-Editor Layered Sync v18.4" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Source       : $CLAUDE_DIR" -ForegroundColor DarkGray
Write-Host "  Targets      : $($TARGETS.Keys -join ', ')" -ForegroundColor DarkGray
Write-Host "  Mode         : $MODE_LABEL" -ForegroundColor DarkGray
if ($DryRun) {
    Write-Host "  [DRY RUN] Preview only -- no changes will be made" -ForegroundColor Yellow
}
Write-Host ""

# =============================================================
# Standalone modes: -Lint / -InitProject (deploy to CWD, skip editor sync)
# =============================================================

if ($Lint) {
    Deploy-Templates -TemplateList $LINT_TEMPLATES -ModeName "Lint Templates"
} elseif ($InitProject) {
    Deploy-Templates -TemplateList $PROJECT_TEMPLATES -ModeName "Project-Init Templates"
}

# =============================================================
# Main loop: iterate over each editor target (skip for standalone modes)
# =============================================================

if (-not $SKIP_EDITOR_SYNC) {
foreach ($editor in ($TARGETS.Keys | Sort-Object)) {
    $targetBase = $TARGETS[$editor]

    if (-not (Test-Path $targetBase)) {
        Write-Host "  -- $editor -------------------------------------------" -ForegroundColor DarkGray
        Write-Skip "Target directory not found, skipped: $targetBase"
        $script:STATS.Skipped++
        Write-Host ""
        continue
    }

    Write-Host "  -- $editor -------------------------------------------" -ForegroundColor DarkGray

    $rulesDir = Join-Path $targetBase $RULES_SUBDIR[$editor]
    $ext = $RULES_EXT[$editor]

    # ---- 1. L0 root files (CLAUDE.md / AGENTS.md) ----
    foreach ($item in $L0_ROOT_ITEMS) {
        if ($item.IndexFile -and $ROOT_INDEX_SKIP_EDITORS -contains $editor) { continue }

        $srcPath = Join-Path $CLAUDE_DIR $item.SrcRel
        $dstName = if ($item.PerEditorName) { $L0_ROOT_DSTNAME[$editor] } else { $item.DstName }
        $dstPath = Join-Path $targetBase $dstName
        Sync-File -SrcPath $srcPath -DstPath $dstPath -Label "$dstName -> $editor"

        # Purge misplaced same-basename copies under rules/ (e.g. rules/CLAUDE.md).
        # Only for the per-editor entry file; index files never had rules/ variants.
        if ($item.PerEditorName) {
            $rootBase = [System.IO.Path]::GetFileNameWithoutExtension($dstName)
            if (Test-Path $rulesDir) {
                Remove-SameBasenameVariants -Directory $rulesDir -BaseName $rootBase `
                    -LabelPrefix "rules(misplaced)"
            }
        }
    }

    # ---- 2. L0 rule files (CORE, CLAUDE-ROUTER) ----
    # Cursor: SSOT rules live ONLY in local plugin (claude-config) to avoid
    # User Settings + Agent double Always-Apply. WorkBuddy: no rules channel.
    # Other editors keep softlinks.
    if ($RULES_SKIP_EDITORS -notcontains $editor) {
        foreach ($item in $L0_RULE_ITEMS) {
            Sync-RuleFile -SrcRelPath $item.SrcRel -DstBaseName $item.DstBase `
                -TargetRulesDir $rulesDir -EditorExt $ext -EditorName $editor
        }

        $routerSrc = Join-Path $CLAUDE_DIR $ROUTER_SRC_REL
        if (Test-Path $routerSrc) {
            Sync-RuleFile -SrcRelPath $ROUTER_SRC_REL -DstBaseName $ROUTER_DST_BASE `
                -TargetRulesDir $rulesDir -EditorExt $ext -EditorName $editor
        }
    }

    # Cursor Guard 专有 + local plugin（唯一 Always Apply 通道）
    if ($editor -eq 'cursor') {
        Deploy-CursorLocalPlugin
    }

    # ---- 3. Directory sync (skills/, agents/) ----
    foreach ($item in $DIR_SYNC_ITEMS) {
        $srcPath = Join-Path $CLAUDE_DIR $item.SrcRel
        $dstPath = Join-Path $targetBase $item.DstRel
        Sync-Directory -SrcPath $srcPath -DstPath $dstPath -Label "$($item.DstRel) -> $editor"
    }
    # WorkBuddy: always junction skills/ (recommended entry; no rules channel)
    if ($editor -eq 'workbuddy') {
        $wbSkillsSrc = Join-Path $CLAUDE_DIR "skills"
        $wbSkillsDst = Join-Path $targetBase "skills"
        $already = $DIR_SYNC_ITEMS | Where-Object { $_.SrcRel -eq "skills" }
        if (-not $already) {
            Sync-Directory -SrcPath $wbSkillsSrc -DstPath $wbSkillsDst -Label "skills -> workbuddy"
        }
    }

    # ---- 4. Always sync all rules/*.md (symlink preferred) ----
    # Cursor / WorkBuddy: skip rules softlinks
    if ($RULES_SKIP_EDITORS -contains $editor) {
        if ($editor -eq 'cursor') {
            Write-Host "  [skip] ~/.cursor/rules softlinks (deduped; SSOT via claude-config plugin)" -ForegroundColor DarkGray
        } else {
            Write-Host "  [skip] ~/.workbuddy/rules (no native rules channel; CLAUDE.md + skills only)" -ForegroundColor DarkGray
        }
    } elseif ($IndexesOnly) {
        Write-Host "  [skip] full rules softlinks (indexes scope)" -ForegroundColor DarkGray
    } elseif (Test-Path (Join-Path $CLAUDE_DIR "rules")) {
        $rulesSrcDir = Join-Path $CLAUDE_DIR "rules"
        $ruleFiles = Get-ChildItem $rulesSrcDir -Filter "*.md" -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -ne "README.md" } |
            Sort-Object Name

        $l0SkipSet = [System.Collections.Generic.HashSet[string]]::new()
        foreach ($item in $L0_RULE_ITEMS) {
            $null = $l0SkipSet.Add($item.DstBase)
        }
        $null = $l0SkipSet.Add($ROUTER_DST_BASE)

        $expectedRuleBases = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
        foreach ($item in $L0_RULE_ITEMS) { $null = $expectedRuleBases.Add($item.DstBase) }
        $null = $expectedRuleBases.Add($ROUTER_DST_BASE)

        foreach ($rf in $ruleFiles) {
            $null = $expectedRuleBases.Add($rf.BaseName)
            if ($l0SkipSet.Contains($rf.BaseName)) { continue }
            $srcPath = $rf.FullName
            $dstPath = Join-Path $rulesDir "$($rf.BaseName)$ext"
            $label = "rules/$($rf.BaseName)$ext -> $editor"
            Sync-File -SrcPath $srcPath -DstPath $dstPath -Label $label
        }

        if (Test-Path $rulesDir) {
            Get-ChildItem $rulesDir -File -ErrorAction SilentlyContinue |
                Where-Object { $_.Extension -match '^\.(mdc|md)$' -and -not $expectedRuleBases.Contains($_.BaseName) } |
                ForEach-Object {
                    Remove-Target -Path $_.FullName -Label "stale rules/$($_.Name) -> $editor"
                }
        }
    }

    Write-Host ""
}
}  # end if (-not $SKIP_EDITOR_SYNC)

# =============================================================
# Optional OPT-IN: deploy Cursor Project Rules into workspace(s)
# Default is OFF — AI rules stay in personal ~/.cursor only.
# Use -ProjectRules / -ProjectRulesPath only when you explicitly want
# <workspace>/.cursor/rules for a business project.
# =============================================================

function Deploy-ProjectRules {
    param([string]$ProjectRoot)
    $rootFull = [System.IO.Path]::GetFullPath($ProjectRoot)
    $claudeFull = [System.IO.Path]::GetFullPath($CLAUDE_DIR)
    $projectRulesDir = Join-Path $rootFull ".cursor\rules"
    $ext = ".mdc"

    Write-Host "  -- project-rules --------------------------------------" -ForegroundColor DarkGray
    Write-Host "  Target: $projectRulesDir" -ForegroundColor DarkGray

    if ($rootFull.TrimEnd('\') -ieq $claudeFull.TrimEnd('\')) {
        Write-Skip "Target is ~/.claude — skip ProjectRules mirror (use ~/.cursor/rules only; avoids Settings duplicates)"
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

    foreach ($item in $L0_RULE_ITEMS) {
        Sync-RuleFile -SrcRelPath $item.SrcRel -DstBaseName $item.DstBase `
            -TargetRulesDir $projectRulesDir -EditorExt $ext -EditorName 'cursor'
    }
    $routerSrc = Join-Path $CLAUDE_DIR $ROUTER_SRC_REL
    if (Test-Path $routerSrc) {
        Sync-RuleFile -SrcRelPath $ROUTER_SRC_REL -DstBaseName $ROUTER_DST_BASE `
            -TargetRulesDir $projectRulesDir -EditorExt $ext -EditorName 'cursor'
    }
    $ceSrc = Join-Path $CLAUDE_DIR "templates\cursor-guard\rules\CURSOR-EDITOR.mdc"
    if (Test-Path $ceSrc) {
        Sync-File -SrcPath $ceSrc -DstPath (Join-Path $projectRulesDir "CURSOR-EDITOR.mdc") `
            -Label "project rules/CURSOR-EDITOR.mdc"
    }
    if ($All) {
        $rulesSrcDir = Join-Path $CLAUDE_DIR "rules"
        $l0SkipSet = [System.Collections.Generic.HashSet[string]]::new()
        foreach ($item in $L0_RULE_ITEMS) { $null = $l0SkipSet.Add($item.DstBase) }
        $null = $l0SkipSet.Add($ROUTER_DST_BASE)
        Get-ChildItem $rulesSrcDir -Filter "*.md" -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -ne "README.md" -and -not $l0SkipSet.Contains($_.BaseName) } |
            Sort-Object Name |
            ForEach-Object {
                $dst = Join-Path $projectRulesDir "$($_.BaseName)$ext"
                Sync-File -SrcPath $_.FullName -DstPath $dst -Label "project rules/$($_.BaseName)$ext"
            }
    }
    Write-Host ""
}

if (($ProjectRules -or $ProjectRulesPath) -and -not $SKIP_EDITOR_SYNC) {
    $targets = [System.Collections.Generic.List[string]]::new()
    if ($ProjectRules) {
        $targets.Add((Get-Location).Path)
    }
    if ($ProjectRulesPath) {
        foreach ($part in ($ProjectRulesPath -split '[;,]')) {
            $p = $part.Trim().Trim('"')
            if ($p) { $targets.Add($p) }
        }
    }
    foreach ($t in $targets) {
        Deploy-ProjectRules -ProjectRoot $t
    }
}

# =============================================================
# Summary report
# =============================================================

Write-Host "  =====================================================" -ForegroundColor DarkGray
$doneLabel = if ($DryRun) { "Dry run complete" } else { "Sync complete" }
Write-Host "  $doneLabel" -ForegroundColor Green
Write-Host ""

$syncedLabel = if ($DryRun) { "Would sync" } else { "Synced" }
Write-Host "  $syncedLabel          : $($script:STATS.Synced)" -ForegroundColor White
Write-Host "  Removed (dedup)    : $($script:STATS.Removed)" -ForegroundColor White
Write-Host "  Skipped            : $($script:STATS.Skipped)" -ForegroundColor White
if ($script:STATS.Failed -gt 0) {
    Write-Host "  Failed             : $($script:STATS.Failed)" -ForegroundColor Red
}

Write-Host ""
Write-Host "  Mode       : $MODE_LABEL" -ForegroundColor DarkGray
Write-Host "  Extensions : cursor/qoder/qoder-cn/codearts=.mdc, trae/trae-cn=.md; workbuddy=CLAUDE.md+skills (no rules)" -ForegroundColor DarkGray
Write-Host "  Method     : symlink preferred; Copy-Item fallback" -ForegroundColor DarkGray
Write-Host "  Cursor     : personal ~/.cursor (claude-config plugin refresh every run); -ProjectRules opt-in" -ForegroundColor DarkGray
Write-Host "  RootIndex  : CLAUDE.md + ROUTER/SPEC/MANIFEST/agent.yaml/3 INDEX -> all editors except $($ROOT_INDEX_SKIP_EDITORS -join ', ')" -ForegroundColor DarkGray
Write-Host "  WorkBuddy  : ~/.workbuddy CLAUDE.md + skills/ junction (SOUL/USER untouched)" -ForegroundColor DarkGray
Write-Host "  CodeArts   : ~/.codeartsdoer (CLAUDE.md + rule/*.mdc)" -ForegroundColor DarkGray
Write-Host "  Dedup      : delete same-basename variants (any ext/case) then write" -ForegroundColor DarkGray
Write-Host "  Excluded   : hooks/ scripts/ MCP configs plugins/ commands/ settings.json" -ForegroundColor DarkGray
Write-Host ""

# =============================================================
# Knowledge graph refresh (codegraph only; codebase-memory disabled)
# =============================================================
if (-not $DryRun) {
    $kgSync = Join-Path $CLAUDE_DIR "hooks\_lib\knowledge_graph_sync.py"
    if (Test-Path $kgSync) {
        Write-Host "  Refreshing knowledge graphs (debounced, non-force) ..." -ForegroundColor Cyan
        try {
            $kgOut = & python $kgSync $CLAUDE_DIR 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  [OK]  knowledge graph sync" -ForegroundColor Green
            } else {
                Write-Host "  [!!]  knowledge graph sync exit $LASTEXITCODE" -ForegroundColor Yellow
                if ($kgOut) { Write-Host "         $kgOut" -ForegroundColor DarkGray }
            }
        } catch {
            Write-Host "  [!!]  knowledge graph sync failed: $_" -ForegroundColor Yellow
        }
        Write-Host ""
    }
}
