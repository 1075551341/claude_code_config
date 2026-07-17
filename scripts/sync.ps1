#Requires -Version 5.1
<#
.SYNOPSIS
    Claude Code multi-editor layered sync script v18.0
    Modes: default (L0 entry files) | -Skills (+ skills/) | -All (everything)
    Project: -Lint (prettier+eslint) | -InitProject (CLAUDE.md+MANIFEST+.env+.gitignore)

.DESCRIPTION
    Default: sync L0 entry files (CLAUDE.md, CORE.md, CLAUDE-ROUTER.mdc)
    -Skills: additionally sync skills/ directory
    -All:    full sync (rules + skills + agents + CLAUDE.md)
    -DryRun: preview only, no disk writes
    -Lint:   deploy prettier + eslint templates to current project (skip existing)
    -InitProject: deploy project-init templates to current project (skip existing)

    Sync method: symbolic link preferred, Copy-Item fallback
    Before syncing: delete same-basename siblings in the target dir
      (any extension / case — e.g. CORE.md + core.mdc before writing CORE.mdc)
    Rules extension: cursor/qoder/codearts -> .mdc, devin/trae -> .md

    Excluded: hooks/ scripts/ MCP configs plugins/ commands/ settings.json

.PARAMETER DryRun
    Preview only, do not execute actual operations

.PARAMETER Skills
    Additionally sync the skills/ directory

.PARAMETER All
    Full sync: rules + skills + agents + CLAUDE.md

.PARAMETER Lint
    Deploy prettier + eslint 9 flat config templates to current working directory.
    Copies .prettierrc.json, .prettierignore, eslint.config.js (skip if exists).

.PARAMETER InitProject
    Deploy project-init templates to current working directory.
    Copies CLAUDE.md, MANIFEST.yaml, .env.example, .gitignore (skip if exists).

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File sync.ps1
    powershell -ExecutionPolicy Bypass -File sync.ps1 -Skills
    powershell -ExecutionPolicy Bypass -File sync.ps1 -All
    powershell -ExecutionPolicy Bypass -File sync.ps1 -All -DryRun
    powershell -ExecutionPolicy Bypass -File sync.ps1 -Lint
    powershell -ExecutionPolicy Bypass -File sync.ps1 -InitProject
#>

param(
    [switch]$DryRun,
    [switch]$Skills,
    [switch]$All,
    [switch]$Lint,
    [switch]$InitProject
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

# =============================================================
# Configuration
# =============================================================

$CLAUDE_DIR = "$env:USERPROFILE\.claude"

# Target editor base directories
$TARGETS = [ordered]@{
    "cursor"   = "$env:USERPROFILE\.cursor"
    "devin"    = "$env:APPDATA\devin"
    "qoder"    = "$env:USERPROFILE\.qoder"
    "qoder-cn" = "$env:USERPROFILE\.qoder-cn"
    "trae"     = "$env:USERPROFILE\.trae"
    "trae-cn"  = "$env:USERPROFILE\.trae-cn"
    "codearts" = "$env:USERPROFILE\.codeartsdoer"
}

# Rules subdirectory name within each target base
$RULES_SUBDIR = [ordered]@{
    "cursor"   = "rules"
    "devin"    = "rules"
    "qoder"    = "rules"
    "qoder-cn" = "rules"
    "trae"     = "user_rules"
    "trae-cn"  = "user_rules"
    "codearts" = "rule"
}

# Rules file extension per editor
$RULES_EXT = [ordered]@{
    "cursor"   = ".mdc"
    "devin"    = ".md"
    "qoder"    = ".mdc"
    "qoder-cn" = ".mdc"
    "trae"     = ".md"
    "trae-cn"  = ".md"
    "codearts" = ".mdc"
}

# L0 entry rules: deployed into rules/ subdirectory (extension converted per editor)
$L0_RULE_ITEMS = @(
    @{ SrcRel = "rules/CORE.md"; DstBase = "CORE" }
)

# L0 root files: deployed to editor root directory (name preserved)
$L0_ROOT_ITEMS = @(
    @{ SrcRel = "CLAUDE.md"; DstName = "CLAUDE.md" }
)

# L0 root file destination name per editor (override DstName when needed)
# Devin CLI uses AGENTS.md as global rules; others use CLAUDE.md
$L0_ROOT_DSTNAME = [ordered]@{
    "cursor"   = "CLAUDE.md"
    "devin"    = "AGENTS.md"
    "qoder"    = "CLAUDE.md"
    "qoder-cn" = "CLAUDE.md"
    "trae"     = "CLAUDE.md"
    "trae-cn"  = "CLAUDE.md"
    "codearts" = "CLAUDE.md"
}

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
$MODE_LABEL = "L0 entry files"
if ($Skills) { $MODE_LABEL = "L0 + skills/" }
if ($All)    { $MODE_LABEL = "ALL (rules + skills + agents + CLAUDE.md)" }
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
        [string]$Label
    )

    if (-not (Test-Path $SrcPath)) {
        Write-Skip "Source missing: $Label"
        $script:STATS.Skipped++
        return
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
        Write-Ok "Would symlink: $Label"
        $script:STATS.Synced++
        return
    }

    # Try symbolic link first
    try {
        New-Item -ItemType SymbolicLink -Path $DstPath -Target $SrcPath -Force | Out-Null
        Write-Ok "Symlinked: $Label"
        $script:STATS.Synced++
        return
    } catch {
        # Symlink failed, fall through to copy
    }

    # Fallback: Copy-Item
    try {
        Copy-Item $SrcPath $DstPath -Force
        Write-Ok "Copied (symlink unavailable): $Label"
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
Write-Host "  Claude Code Multi-Editor Layered Sync v18.0" -ForegroundColor Cyan
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
        $srcPath = Join-Path $CLAUDE_DIR $item.SrcRel
        $dstName = $L0_ROOT_DSTNAME[$editor]
        $dstPath = Join-Path $targetBase $dstName
        Sync-File -SrcPath $srcPath -DstPath $dstPath -Label "$dstName -> $editor"

        # Purge misplaced same-basename copies under rules/ (e.g. rules/CLAUDE.md)
        $rootBase = [System.IO.Path]::GetFileNameWithoutExtension($dstName)
        if (Test-Path $rulesDir) {
            Remove-SameBasenameVariants -Directory $rulesDir -BaseName $rootBase `
                -LabelPrefix "rules(misplaced)"
        }
    }

    # ---- 2. L0 rule files (CORE, CLAUDE-ROUTER) ----
    foreach ($item in $L0_RULE_ITEMS) {
        Sync-RuleFile -SrcRelPath $item.SrcRel -DstBaseName $item.DstBase `
            -TargetRulesDir $rulesDir -EditorExt $ext -EditorName $editor
    }

    # Add CLAUDE-ROUTER if source exists
    $routerSrc = Join-Path $CLAUDE_DIR $ROUTER_SRC_REL
    if (Test-Path $routerSrc) {
        Sync-RuleFile -SrcRelPath $ROUTER_SRC_REL -DstBaseName $ROUTER_DST_BASE `
            -TargetRulesDir $rulesDir -EditorExt $ext -EditorName $editor
    }

    # ---- 3. Directory sync (skills/, agents/) ----
    foreach ($item in $DIR_SYNC_ITEMS) {
        $srcPath = Join-Path $CLAUDE_DIR $item.SrcRel
        $dstPath = Join-Path $targetBase $item.DstRel
        Sync-Directory -SrcPath $srcPath -DstPath $dstPath -Label "$($item.DstRel) -> $editor"
    }

    # ---- 4. --all: sync all rules/*.md files individually ----
    if ($All) {
        $rulesSrcDir = Join-Path $CLAUDE_DIR "rules"
        if (Test-Path $rulesSrcDir) {
            $ruleFiles = Get-ChildItem $rulesSrcDir -Filter "*.md" -ErrorAction SilentlyContinue |
                Where-Object { $_.Name -ne "README.md" } |
                Sort-Object Name

            # Build set of L0 base names to skip (already synced above)
            $l0SkipSet = [System.Collections.Generic.HashSet[string]]::new()
            foreach ($item in $L0_RULE_ITEMS) {
                $null = $l0SkipSet.Add($item.DstBase)
            }
            $null = $l0SkipSet.Add($ROUTER_DST_BASE)

            foreach ($rf in $ruleFiles) {
                if ($l0SkipSet.Contains($rf.BaseName)) { continue }

                $srcPath = $rf.FullName
                $dstPath = Join-Path $rulesDir "$($rf.BaseName)$ext"
                $label = "rules/$($rf.BaseName)$ext -> $editor"
                Sync-File -SrcPath $srcPath -DstPath $dstPath -Label $label
            }
        }
    }

    Write-Host ""
}
}  # end if (-not $SKIP_EDITOR_SYNC)

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
Write-Host "  Extensions : cursor/qoder/qoder-cn/codearts=.mdc, devin/trae/trae-cn=.md" -ForegroundColor DarkGray
Write-Host "  Method     : symlink preferred, Copy-Item fallback" -ForegroundColor DarkGray
Write-Host "  Dedup      : delete same-basename variants (any ext/case) then write" -ForegroundColor DarkGray
Write-Host "  Excluded   : hooks/ scripts/ MCP configs plugins/ commands/ settings.json" -ForegroundColor DarkGray
Write-Host ""
