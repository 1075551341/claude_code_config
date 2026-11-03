#Requires -Version 7.5
<#
.SYNOPSIS
    Sync ~/.claude (SSOT) to editor homes. Schema v2 entry point.

.DESCRIPTION
    Thin dispatcher kept for backward compatibility with Cursor Guard hooks
    (sync.ps1 -Scope rules|indexes|all -Force) and docs.

    Editor layout (see scripts/sync-editors.ps1):
      Cursor   -> plugins/local/claude-config/rules/00-AGENTS.mdc + rules/*.mdc
      Qoder    -> rules/AGENTS.md + rules/*.md
      Trae     -> user_rules/AGENTS.md + user_rules/*.md
      Trae CN  -> user_rules/AGENTS.md + user_rules/*.md
      all      -> <home>/skills and (cursor/qoder) <home>/agents

    -Lint / -InitProject are handled here (templates copied into the CWD).

    Never syncs MCP configs (.mcp.json / mcp.json), settings.json, hooks/, commands/.

.EXAMPLE
    pwsh -File scripts/sync.ps1 -DryRun
    pwsh -File scripts/sync.ps1 -Scope all -CleanLegacy
    pwsh -File scripts/sync.ps1 -All
#>
param(
    [switch]$DryRun,
    [switch]$Skills,
    [switch]$All,
    [switch]$ProjectRules,
    [string]$ProjectRulesPath = "",
    [ValidateSet("rules", "indexes", "all")][string]$Scope = "",
    [switch]$Force,
    [switch]$CleanLegacy,
    [switch]$Lint,
    [switch]$InitProject
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"
$CLAUDE_DIR = Join-Path $env:USERPROFILE ".claude"

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

function Copy-TemplateSet {
    param([array]$List, [string]$Name)
    Write-Host ""
    Write-Host "  -- $Name -> $((Get-Location).Path)" -ForegroundColor DarkGray
    foreach ($item in $List) {
        $src = Join-Path $CLAUDE_DIR $item.SrcRel
        $dst = Join-Path (Get-Location).Path $item.DstName
        if (-not (Test-Path $src)) { Write-Host "    [--]  source missing: $($item.DstName)"; continue }
        if (Test-Path $dst) { Write-Host "    [--]  exists (skip): $($item.DstName)"; continue }
        Copy-Item $src $dst -Force
        Write-Host "    [OK]  copied: $($item.DstName)" -ForegroundColor Green
    }
    Write-Host ""
}

if ($Lint) { Copy-TemplateSet -List $LINT_TEMPLATES -Name "Lint Templates"; exit 0 }
if ($InitProject) { Copy-TemplateSet -List $PROJECT_TEMPLATES -Name "Project-Init Templates"; exit 0 }

$engine = Join-Path $PSScriptRoot "sync-editors.ps1"
if (-not (Test-Path $engine)) {
    Write-Host "  [XX] sync engine missing: $engine" -ForegroundColor Red
    exit 1
}

# Single source: rules/CORE.md -> CLAUDE.md / OpenCode/DSH AGENTS.md+CORE.md.
$principles = Join-Path $CLAUDE_DIR "scripts\principles.py"
if (-not (Test-Path $principles)) {
    Write-Host "  [XX] principles.py missing: $principles" -ForegroundColor Red
    exit 1
}
$pArgs = @($principles, "sync")
if ($DryRun) { $pArgs += "--dry-run" }
& python @pArgs
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [XX] principles sync failed" -ForegroundColor Red
    exit 1
}

$fwd = @{}
if ($DryRun) { $fwd.DryRun = $true }
if ($Skills) { $fwd.Skills = $true }
if ($All) { $fwd.All = $true }
if ($ProjectRules) { $fwd.ProjectRules = $true }
if ($ProjectRulesPath) { $fwd.ProjectRulesPath = $ProjectRulesPath }
if ($Scope) { $fwd.Scope = $Scope }
if ($Force) { $fwd.Force = $true }
if ($CleanLegacy) { $fwd.CleanLegacy = $true }

& $engine @fwd
exit $LASTEXITCODE
