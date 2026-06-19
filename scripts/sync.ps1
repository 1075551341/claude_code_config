#Requires -Version 5.1
<#
.SYNOPSIS
    Claude Code multi-editor layered sync script v16.0
    Modes: default (L0 entry files) | --skills (+ skills/) | --all (everything)

.DESCRIPTION
    Default: sync L0 entry files (CLAUDE.md, CORE.md, CLAUDE-ROUTER.mdc)
    --skills: additionally sync skills/ directory
    --all:    full sync (rules + skills + agents + CLAUDE.md)
    --dryRun: preview only, no disk writes

    Sync method: symbolic link preferred, Copy-Item fallback
    Before syncing: delete existing target of same name (dedup)
    Rules extension: cursor/qoder/codearts -> .mdc, devin/trae -> .md

    Excluded: hooks/ scripts/ MCP configs plugins/ commands/ settings.json

.PARAMETER DryRun
    Preview only, do not execute actual operations

.PARAMETER Skills
    Additionally sync the skills/ directory

.PARAMETER All
    Full sync: rules + skills + agents + CLAUDE.md

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File sync.ps1
    powershell -ExecutionPolicy Bypass -File sync.ps1 -Skills
    powershell -ExecutionPolicy Bypass -File sync.ps1 -All
    powershell -ExecutionPolicy Bypass -File sync.ps1 -All -DryRun
#>

param(
    [switch]$DryRun,
    [switch]$Skills,
    [switch]$All
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
    "devin"    = "$env:USERPROFILE\.claude\.devin"
    "qoder"    = "$env:USERPROFILE\.qoder"
    "trae"     = "$env:USERPROFILE\.trae"
    "codearts" = "$env:USERPROFILE\.config\codeartsdoer"
}

# Rules subdirectory name within each target base
$RULES_SUBDIR = [ordered]@{
    "cursor"   = "rules"
    "devin"    = "rules"
    "qoder"    = "rules"
    "trae"     = "user_rules"
    "codearts" = "rule"
}

# Rules file extension per editor
$RULES_EXT = [ordered]@{
    "cursor"   = ".mdc"
    "devin"    = ".md"
    "qoder"    = ".mdc"
    "trae"     = ".md"
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

# CLAUDE-ROUTER source (deployed as 00-CLAUDE-ROUTER.{ext} into rules/)
$ROUTER_SRC_REL = "CLAUDE-ROUTER.mdc"
$ROUTER_DST_BASE = "00-CLAUDE-ROUTER"

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

    # Dedup: remove existing target first
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
# Print header
# =============================================================

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  Claude Code Multi-Editor Layered Sync v16.0" -ForegroundColor Cyan
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
# Main loop: iterate over each editor target
# =============================================================

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

    # ---- 1. L0 root files (CLAUDE.md) ----
    foreach ($item in $L0_ROOT_ITEMS) {
        $srcPath = Join-Path $CLAUDE_DIR $item.SrcRel
        $dstPath = Join-Path $targetBase $item.DstName
        Sync-File -SrcPath $srcPath -DstPath $dstPath -Label "$($item.DstName) -> $editor"
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
Write-Host "  Extensions : cursor/qoder/codearts=.mdc, devin/trae=.md" -ForegroundColor DarkGray
Write-Host "  Method     : symlink preferred, Copy-Item fallback" -ForegroundColor DarkGray
Write-Host "  Dedup      : delete existing same-name target before sync" -ForegroundColor DarkGray
Write-Host "  Excluded   : hooks/ scripts/ MCP configs plugins/ commands/ settings.json" -ForegroundColor DarkGray
Write-Host ""
