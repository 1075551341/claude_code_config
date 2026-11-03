#Requires -Version 7.5
<#
.SYNOPSIS
    Deploy ~/.claude (SSOT) to editor homes: AGENTS.md + rules + skills + agents.

.DESCRIPTION
    Target layout (schema v2, config/sync-manifest.json):
      cursor  -> ~/.cursor/plugins/local/claude-config/rules/00-AGENTS.mdc + rules/*.mdc
      qoder   -> ~/.qoder/rules/AGENTS.md + rules/*.md
      trae    -> ~/.trae/user_rules/AGENTS.md + user_rules/*.md
      trae-cn -> ~/.trae-cn/user_rules/AGENTS.md + user_rules/*.md
      all     -> <home>/skills/<skill>/SKILL.md and (cursor/qoder) <home>/agents/*.md

    - AGENTS.md is generated from ~/.claude/CLAUDE.md and adapted per tool.
    - Rules are copied as real files; .mdc channels get alwaysApply, qoder keeps
      trigger, trae keeps the source frontmatter.
    - skills/agents are real copies with a .claude-managed ledger; only files in
      the ledger are ever removed.
    - No symlinks/junctions are created.

.PARAMETER Scope
    rules   = entry + rules (default)
    indexes = entry only (legacy name; entry is AGENTS.md)
    all     = entry + rules + skills + agents

.PARAMETER CleanLegacy
    Remove pre-v2 artifacts: root CLAUDE.md/SPEC/MANIFEST/INDEX links, the old
    Cursor plugin copy, stale Trae user_rules, and junctioned skills/agents.

.EXAMPLE
    pwsh -File scripts/sync-editors.ps1 -DryRun
    pwsh -File scripts/sync-editors.ps1 -Scope all -CleanLegacy
#>
param(
    [switch]$DryRun,
    [switch]$Skills,
    [switch]$All,
    [switch]$ProjectRules,
    [string]$ProjectRulesPath = "",
    [ValidateSet("rules", "indexes", "all")][string]$Scope = "",
    [switch]$Force,
    [switch]$CleanLegacy
)

$ErrorActionPreference = "Stop"
$CLAUDE_DIR = Join-Path $env:USERPROFILE ".claude"
$manifestPath = Join-Path $CLAUDE_DIR "config\sync-manifest.json"

if (-not (Test-Path $manifestPath)) {
    Write-Host "  [XX] sync-manifest.json missing: $manifestPath" -ForegroundColor Red
    exit 1
}
$MF = Get-Content $manifestPath -Raw -Encoding utf8 | ConvertFrom-Json

$ENTRY_SOURCE = if ($MF.entry_source) { "$($MF.entry_source)" } else { "CLAUDE.md" }
$ENTRY_NAME = if ($MF.entry_name) { "$($MF.entry_name)" } else { "AGENTS.md" }
$RULE_EXCLUDE = @($MF.rules.exclude | Where-Object { $_ })
$RULE_RENAMES = @{}
if ($MF.rules.renames) {
    foreach ($p in $MF.rules.renames.PSObject.Properties) { $RULE_RENAMES[$p.Name] = "$($p.Value)" }
}
$SKILL_EXCLUDE = @($MF.skills.exclude | Where-Object { $_ })
$AGENT_EXCLUDE = @($MF.agents.exclude | Where-Object { $_ })
$LEGACY_ROOT = @($MF.legacy_root_files | Where-Object { $_ })
$LEGACY_RULE_BASES = @($MF.legacy_rule_files | Where-Object { $_ })

# SSOT path allowlist: only these are rewritten to ~/.claude/... . Project-scoped
# tokens (openspec/, specs/, archive/, .planning/, _sandbox/, mcp.json) stay as-is.
$script:SSOT_EXACT = @(
    'MANIFEST.yaml', 'SPEC.md', 'CHANGELOG.md', 'RTK.md',
    'skills-INDEX.md', 'agents-INDEX.md', 'rules-INDEX.md'
)
$script:SSOT_PREFIXES = @(
    'config/', 'docs/', 'rules/', 'agents/', 'skills/', 'scripts/',
    'commands/', 'catalog/', 'templates/', 'hooks/', 'mcp-configs/', 'mcp/', 'plugins/'
)

# ---- scope -------------------------------------------------------------
if ($All -or $Scope -eq "all") { $DoSkills = $true; $DoAgents = $true; $DoRules = $true; $DoEntry = $true }
elseif ($Scope -eq "indexes") { $DoSkills = $false; $DoAgents = $false; $DoRules = $false; $DoEntry = $true }
elseif ($Scope -eq "rules" -or $Skills) {
    $DoSkills = [bool]$Skills; $DoAgents = $false; $DoRules = $true; $DoEntry = $true
}
else { $DoSkills = $false; $DoAgents = $false; $DoRules = $true; $DoEntry = $true }
# -CleanLegacy removes the plugin dir; always rebuild rules so indexes-only cannot
# leave Cursor without rules.
if ($CleanLegacy) { $DoRules = $true; $DoEntry = $true }

$script:STATS = @{ Changed = 0; Removed = 0; Skipped = 0; Failed = 0 }

function Get-ManagedPath { param([string]$Path) return ($Path -replace '^~', $env:USERPROFILE) -replace '/', '\' }
function Get-DisplayPath { param([string]$Path) return (($Path -replace [regex]::Escape($env:USERPROFILE), '~') -replace '\\', '/') }
function Write-Ok { param($m) Write-Host "    [OK]  $m" -ForegroundColor Green }
function Write-Fix { param($m) Write-Host "    [FIX] $m" -ForegroundColor Cyan }
function Write-Skip { param($m) Write-Host "    [--]  $m" -ForegroundColor DarkGray }
function Write-Dry { param($m) Write-Host "    [DRY] $m" -ForegroundColor Yellow }
function Write-Fail { param($m) Write-Host "    [XX]  $m" -ForegroundColor Red; $script:STATS.Failed++ }

function Get-Link {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    $it = Get-Item -LiteralPath $Path -Force
    if ($it.LinkType) { return $it }
    return $null
}

function Remove-Path {
    param([string]$Path, [string]$Label)
    if (-not (Test-Path -LiteralPath $Path)) { return }
    $link = Get-Link $Path
    if ($DryRun) {
        Write-Dry "Would remove: $Label"
        $script:STATS.Removed++
        return
    }
    if ($link) {
        if ($link.PSIsContainer) {
            & cmd.exe /c "rmdir `"$Path`"" 2>&1 | Out-Null
            if (Test-Path -LiteralPath $Path) {
                Write-Fail "Failed to remove junction: $Label"
                throw "junction removal failed: $Path"
            }
        } else {
            Remove-Item -LiteralPath $Path -Force
        }
    } else {
        Remove-Item -LiteralPath $Path -Recurse -Force
    }
    Write-Fix "Removed: $Label"
    $script:STATS.Removed++
}

function Write-IfChanged {
    param([string]$Path, [string]$Content, [string]$Label)
    $link = Get-Link $Path
    if ($link) { Remove-Path -Path $Path -Label "$Label (link)" }
    $fullPath = [IO.Path]::GetFullPath($Path)
    $fullClaude = [IO.Path]::GetFullPath($CLAUDE_DIR)
    if ($fullPath.StartsWith($fullClaude, [StringComparison]::OrdinalIgnoreCase)) {
        Write-Fail "refusing to write into SSOT: $Path"
        return
    }
    if ((Test-Path -LiteralPath $Path) -and -not (Get-Link $Path)) {
        $old = [IO.File]::ReadAllText($Path)
        if ([string]::Equals($old, $Content, [StringComparison]::Ordinal)) {
            Write-Skip "Unchanged: $Label"
            $script:STATS.Skipped++
            return
        }
    }
    if ($DryRun) {
        Write-Dry "Would write: $Label"
        $script:STATS.Changed++
        return
    }
    $dir = Split-Path $Path -Parent
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    $utf8 = New-Object System.Text.UTF8Encoding $false
    [IO.File]::WriteAllText($Path, $Content, $utf8)
    Write-Ok "Wrote: $Label"
    $script:STATS.Changed++
}

function Get-Frontmatter {
    param([string]$Text)
    $m = [regex]::Match($Text, '(?s)^---\r?\n(.*?)\r?\n---\r?\n?')
    if (-not $m.Success) { return @{ Present = $false; Raw = ""; Body = $Text } }
    return @{ Present = $true; Raw = $m.Groups[1].Value; Body = $Text.Substring($m.Length) }
}

function Get-FmField {
    param([string]$Frontmatter, [string]$Name)
    $m = [regex]::Match($Frontmatter, "(?m)^\s*$([regex]::Escape($Name)):\s*(.*)$")
    if ($m.Success) { return $m.Groups[1].Value.Trim() }
    return ""
}

function Convert-TextOnly {
    param([string]$Body)
    $b = $Body -replace "`r`n", "`n"
    $b = $b -replace [regex]::Escape('CLAUDE.md'), $ENTRY_NAME
    $b = $b -replace [regex]::Escape('claude-mem v13.13.1(记忆，钉扎 <13.14)'), '记忆：本工具无记忆插件（R18 跳过并注明）'
    $b = $b -replace [regex]::Escape('为什么/偏好 → claude-mem（R17-R18）'), '为什么/偏好 → 本工具无记忆插件，跳过并注明（R17-R18）'
    $b = $b -replace [regex]::Escape('疑似重复 → `claude-mem search`（R18）→'), '疑似重复 → 检查本会话上轮结论（本工具无记忆插件，R18 跳过并注明）→'
    $b = $b -replace [regex]::Escape('claude-mem 记录模式/决策（R18）'), '结论写入项目文档（R13；本工具无记忆插件）'
    $b = $b -replace [regex]::Escape('| R18 claude-mem 记忆 |'), '| R18 记忆优先（无插件则跳过并注明） |'
    $b = $b -replace [regex]::Escape('R18 claude-mem 记忆'), 'R18 记忆优先（无插件则跳过并注明）'
    $b = $b -replace [regex]::Escape('Cursor `/summarize`，Claude Code `/compact`'), '本工具压缩命令'
    $b = $b -replace [regex]::Escape('Cursor /summarize，Claude Code /compact'), '本工具压缩命令'
    $b = $b -replace [regex]::Escape('并行 Task'), '并行子 Agent'
    $b = $b -replace [regex]::Escape('Task 传参'), '子 Agent 传参'
    $b = $b -replace [regex]::Escape('在 Cursor / Claude Code 下'), '在 Cursor 或其他工具下'
    $b = $b -replace [regex]::Escape('（Cursor / Claude Code 通用）'), '（工具通用）'
    $b = $b -replace [regex]::Escape('在 Cursor 误调 Claude Code'), '在 Cursor 误调其他工具'
    $b = $b -replace [regex]::Escape('Claude Code 专属'), '其他工具专属'
    $b = $b -replace [regex]::Escape('Cursor / Claude Code'), 'Cursor / 其他工具'
    $b = $b -replace [regex]::Escape('重启 Claude Code'), '重启本工具'
    $b = $b -replace [regex]::Escape('只修改 `.mcp.json`'), '只修改本工具的 MCP 配置文件（`mcp.json`）'
    $b = $b -replace [regex]::Escape('2. 将 `mcpServers` 对象合并进 `~/.claude/.mcp.json` 的 `mcpServers`（仅当无对等 plugin）'), '2. 将 `mcpServers` 对象合并进本工具 home 的 `mcp.json` 的 `mcpServers`（仅当无对等 plugin）'
    $b = $b.Replace('1. 打开对应 `mcp-configs/<profile>.json`', '1. 打开对应 `~/.claude/mcp-configs/<profile>.json`')
    $b = $b.Replace('→ 编辑 .mcp.json（无 plugin 的常驻项）', '→ 编辑本工具 home 的 `mcp.json`（无 plugin 的常驻项）')
    $b = $b.Replace('→ 同步 mcp/servers.json toolsets.always_* 与 mcp-configs/dev.json', '→ 同步 `~/.claude/mcp/servers.json` toolsets.always_* 与 `~/.claude/mcp-configs/dev.json`')
    $b = $b.Replace('→ 验证 always_* ⊆ .mcp.json；按需 profile 仅在 mcp-configs/ 声明', '→ 验证 always_* ⊆ 本工具 mcp.json；按需 profile 仅在 `~/.claude/mcp-configs/` 声明')
    $b = $b.Replace('4. 任务完成后移除并重启（恢复 `.mcp.json` 常驻集）', '4. 任务完成后移除并重启（恢复本工具 MCP 配置常驻集）')
    $b = $b.Replace('`.mcp.json` 是 Claude Code MCP 服务器配置的**唯一权威源**（常驻）。', '`.mcp.json` 是 Claude Code MCP 服务器配置的权威源；本工具的 MCP 配置（Cursor/Qoder 的 `mcp.json`，Trae 设置 → MCP）才是本工具常驻配置的权威源。')
    $b = $b.Replace('- 禁止在 `.mcp.json` 与 `mcp-configs/` 两处维护不同参数定义', '- 禁止在本工具 MCP 配置与 `~/.claude/mcp-configs/` 两处维护不同参数定义')
    $b = $b.Replace('- 禁止将按需 profile（debug / fsaccess / ops）服务器默认写入常驻 `.mcp.json`', '- 禁止将按需 profile（debug / fsaccess / ops）服务器默认写入常驻本工具 MCP 配置')
    $b = $b.Replace('□ .mcp.json 无 context7', '□ 本工具 MCP 配置无 context7')
    $b = $b.Replace('□ .mcp.json 含 everything', '□ 本工具 MCP 配置含 everything')
    $b = $b.Replace('□ servers.json always_* ⊆ .mcp.json', '□ servers.json always_* ⊆ 本工具 MCP 配置')
    $b = $b.Replace('| `.mcp.json` |', '| 本工具 MCP 配置 |')
    $b = $b.Replace('禁止再写入 `.mcp.json`', '禁止再写入本工具 MCP 配置')
    $b = $b.Replace('与 `.mcp.json` 双挂', '与本工具 MCP 配置双挂')
    $b = $b.Replace('`.mcp.json` 只放', '本工具 MCP 配置只放')
    $b = $b -replace [regex]::Escape('已合并 claude-mem'), '已合并记忆能力'
    $b = $b -replace [regex]::Escape('记忆仅 claude-mem 插件'), '记忆仅由可用的记忆插件提供'
    $b = $b -replace [regex]::Escape('禁止升级 claude-mem 到'), '禁止升级记忆插件到'
    $b = $b -replace [regex]::Escape('禁止升级记忆插件到 ≥13.14（钉 13.13.1）'), '禁止升级记忆插件到不兼容版本（本工具无插件则跳过）'
    $b = $b -replace [regex]::Escape('thedotmack/claude-mem'), '上游记忆插件'
    $b = $b -replace [regex]::Escape('claude-mem platform_source'), '记忆来源标记'
    $b = $b -replace [regex]::Escape('claude-mem plugin 持久化'), '记忆持久化（无插件则写项目文档）'
    $b = $b -replace [regex]::Escape('禁止升级 claude-mem 到 ≥13.14（钉 13.13.1）'), '禁止升级记忆插件到不兼容版本（本工具无插件则跳过）'
    $b = $b -replace [regex]::Escape('claude-mem 整合记忆'), '记忆整合'
    $b = $b -replace [regex]::Escape('claude-mem 记忆整合'), '记忆整合'
    $b = $b -replace [regex]::Escape('查 claude-mem，'), '查记忆（无插件则跳过并注明），'
    $b = $b -replace [regex]::Escape('必须先查 claude-mem'), '必须先查记忆（无插件则跳过并注明）'
    $b = $b -replace [regex]::Escape('claude-mem 相关'), '记忆相关'
    $b = $b -replace [regex]::Escape('claude-mem 记忆'), '记忆'
    $b = $b -replace 'claude-mem\s+plugin', '记忆插件'
    $b = $b -replace 'claude-mem\s+observation', '记忆记录'
    $b = $b -replace 'claude-mem\s+search', '记忆检索（无插件则跳过并注明）'
    $b = $b -replace 'claude-mem\s*\+', '记忆插件 +'
    $b = $b -replace 'claude-mem', '记忆'
    $b = $b -replace [regex]::Escape(' → get_observations'), ''
    $b = $b -replace [regex]::Escape('get_observations'), '记忆检索'
    $b = $b -replace [regex]::Escape('并行 `Task`'), '并行子 Agent'
    $b = $b -replace [regex]::Escape('全新 `Task`'), '全新子 Agent'
    $b = $b -replace [regex]::Escape('全新 Task'), '全新子 Agent'
    $b = $b -replace [regex]::Escape('编辑器 Task 参数'), '编辑器子 Agent 参数'
    $b = $b -replace [regex]::Escape('`Task`'), '`子 Agent`'

    # Tool-neutral context table (source compares Cursor vs Claude Code).
    $oldThreshold = '| 使用率 | Cursor | Claude Code |' + "`n" +
        '| --- | --- | --- |' + "`n" +
        '| 70% | 择机 `/summarize`（或「压缩上下文」） | 择机 `/compact` |' + "`n" +
        '| 90% | 强制 `/summarize` 或新子 Agent | 强制 `/compact` 或新子 Agent |'
    $newThreshold = '| 使用率 | 建议动作 |' + "`n" +
        '| --- | --- |' + "`n" +
        '| 70% | 择机压缩上下文（或新建子 Agent） |' + "`n" +
        '| 90% | 强制压缩或新建子 Agent |'
    $b = $b.Replace($oldThreshold, $newThreshold)
    return $b
}

function Convert-BodyRefs {
    param([string]$Body)
    $b = Convert-TextOnly $Body

    $b = $b.Replace('python scripts/workflow.py render', 'python ~/.claude/scripts/workflow.py render')
    $b = [regex]::Replace($b, '`([^`\r\n]+)`', {
            param($m)
            $t = $m.Groups[1].Value.Trim()
            if ($t -eq '' -or $t -eq $ENTRY_NAME) { return $m.Value }
            if ($t -match '^[~/.-]') { return $m.Value }
            if ($t -notmatch '^[A-Za-z0-9_./*{}-]+$') { return $m.Value }
            $candidate = $null
            if ($script:SSOT_EXACT -contains $t) { $candidate = $t }
            else {
                foreach ($p in $script:SSOT_PREFIXES) {
                    if ($t.StartsWith($p)) { $candidate = $t; break }
                }
            }
            if (-not $candidate) { return $m.Value }
            $fs = Join-Path $CLAUDE_DIR ($candidate -replace '/', '\')
            if (-not (Test-Path -LiteralPath $fs) -and -not (Test-Path $fs)) { return $m.Value }
            return "``~/.claude/$candidate``"
        })
    $b = $b.Replace('| 主干 / 流程说明 | config/workflow.yaml + docs/DEV_FLOW.md |', '| 主干 / 流程说明 | ~/.claude/config/workflow.yaml + ~/.claude/docs/DEV_FLOW.md |')
    $b = $b.Replace('| 同步 | docs/SYNC_GUIDE.md', '| 同步 | ~/.claude/docs/SYNC_GUIDE.md')
    $b = $b.Replace('| Agent / MCP / Git / 安全 / 规格 | rules/AGENTS.md', '| Agent / MCP / Git / 安全 / 规格 | ~/.claude/rules/AGENTS.md')
    $b = $b.Replace('| 铁律 / 习惯 / 工具优先级 / 阈值 | rules/CORE.md |', '| 铁律 / 习惯 / 工具优先级 / 阈值 | ~/.claude/rules/CORE.md |')
    $b = $b.Replace('| 工具链地板 | config/toolchain.yaml |', '| 工具链地板 | ~/.claude/config/toolchain.yaml |')
    $b = $b.Replace('| 插件 | plugins/installed_plugins.json |', '| 插件 | ~/.claude/plugins/installed_plugins.json |')
    $b = $b.Replace('Read skills/brainstorming/SKILL.md', 'Read ~/.claude/skills/brainstorming/SKILL.md')
    $b = $b.Replace('catalog/agents/', '~/.claude/catalog/agents/')
    return $b
}

function Convert-RuleContent {
    param([string]$Text, [string]$Flavor, [string]$SourceName = "")
    $fm = Get-Frontmatter $Text
    $desc = ""
    $trigger = ""
    $always = ""
    $body = $Text
    if ($fm.Present) {
        $desc = Get-FmField $fm.Raw "description"
        $trigger = Get-FmField $fm.Raw "trigger"
        $always = Get-FmField $fm.Raw "alwaysApply"
        $body = $fm.Body
    }
    $body = Convert-BodyRefs $body
    if ($SourceName -eq 'MCP.md') {
        $mcpTarget = switch ($Flavor) {
            'cursor' { 'Cursor 的 `~/.cursor/mcp.json`' }
            'qoder' { 'Qoder 的 `~/.qoder/mcp.json`' }
            default { 'Trae 设置 → MCP 面板' }
        }
        $body = $body.Replace('本工具 home 的 `mcp.json`', $mcpTarget)
        $body = $body.Replace('本工具 home 下的 `mcp.json`', $mcpTarget)
        $body = $body.Replace('本工具 `mcp.json`', $mcpTarget)
        $body = $body.Replace('本工具的 MCP 配置文件（`mcp.json`）', $mcpTarget)
        $body = $body.Replace('本工具 mcp.json', $mcpTarget)
        $body = $body.Replace('本工具 MCP 配置', $mcpTarget)
        $body = $body.Replace('`claude mcp add task-master-ai --scope user --env TASK_MASTER_TOOLS="core" -- npx -y task-master-ai`', '`claude mcp add task-master-ai --scope user --env TASK_MASTER_TOOLS="core" -- npx -y task-master-ai`（Claude Code）；本工具在 MCP 配置中添加 `task-master-ai`（`npx -y task-master-ai`）')
        $body = "> **本工具适配**：``~/.claude/.mcp.json`` 仅 Claude Code 适用；本工具的 MCP 配置以本工具自身配置为准（Cursor ``~/.cursor/mcp.json``、Qoder ``~/.qoder/mcp.json``，Trae 设置 → MCP 面板）。下文涉及 Claude Code 的「重启」按「重启本工具」理解；「双平台对照」仅为参考。`n`n" + $body
    }
    if (-not $desc) {
        $h = [regex]::Match($body, '(?m)^#\s+(.+)$')
        if ($h.Success) { $desc = $h.Groups[1].Value.Trim() }
    }
    $isAlways = ($trigger -eq "always_on") -or ($always -eq "true")
    if ($Flavor -eq "cursor") {
        $aa = if ($isAlways) { "true" } else { "false" }
        return "---`ndescription: $desc`nalwaysApply: $aa`n---`n$body"
    }
    if ($Flavor -eq "qoder") {
        $tr = if ($trigger) { $trigger } elseif ($isAlways) { "always_on" } else { "model_decision" }
        return "---`ntrigger: $tr`ndescription: $desc`n---`n$body"
    }
    if ($fm.Present) { return "---`n$($fm.Raw -replace "`r`n", "`n")`n---`n$body" }
    return $body
}

function New-AgentsContent {
    param([string]$ToolName, [string]$HomeDisplay, [string]$RulesDisplay, [string]$Subagent, [string]$Flavor)

    $src = Join-Path $CLAUDE_DIR $ENTRY_SOURCE
    $raw = [IO.File]::ReadAllText($src)
    $fm = Get-Frontmatter $raw
    $body = $fm.Body.TrimStart("`r", "`n")
    $body = $body -replace [regex]::Escape('# Claude 全局配置'), "# $ToolName 全局配置"
    $body = Convert-BodyRefs $body
    $body = $body -replace [regex]::Escape('Claude Code'), $ToolName

    $profile = "> **本文件适配**：$ToolName · skills ``$HomeDisplay/skills`` · rules ``$RulesDisplay`` · 记忆：无记忆插件（R18 跳过并注明） · 子 Agent：$Subagent · 压缩：本工具命令`n" +
               "> 由 ``~/.claude`` 总纲生成；源头变更后运行 ``~/.claude/scripts/sync.ps1``。`n" +
               "> skill 内的 Claude 专用工具名（Task / Bash / Read / Write）按本工具同名能力执行；无同名能力时用最接近的工具。`n"
    $title = [regex]::Match($body, '(?m)^# .+$')
    if ($title.Success) {
        $i = $title.Index + $title.Length
        $tail = $body.Substring($i).TrimStart("`n")
        $body = $body.Substring(0, $i) + "`n`n" + $profile + "`n" + $tail
    } else {
        $body = $body + "`n`n" + $profile
    }

    if ($body -match '(?m)^## 命令\s*$') {
        $body = [regex]::Replace($body, '(?m)^(## 命令\s*)$', "`$1`n`n> 下列为源配置的命令名；本工具无同名命令时，按阶段语义直接执行。")
    }

    $desc = "$ToolName 全局配置总纲 — 路由 + 工作流主干 + 完成定义（由 ~/.claude 总纲生成）"
    if ($Flavor -eq "cursor") {
        return "---`ndescription: $desc`nalwaysApply: true`nlayer: router`n---`n$body"
    }
    return "---`ntrigger: always_on`ndescription: $desc`nlayer: router`n---`n$body"
}

function Get-Ledger {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return @() }
    return @(Get-Content -LiteralPath $Path -Encoding utf8 | Where-Object { $_.Trim() })
}

function Set-Ledger {
    param([string]$Path, [string[]]$Entries)
    $content = ((@($Entries) | Sort-Object -Unique) -join "`n") + "`n"
    Write-IfChanged -Path $Path -Content $content -Label (Get-DisplayPath $Path)
}

function Deploy-Editor {
    param($Cfg, [string]$Name)
    $EditorHome = Get-ManagedPath $Cfg.home
    if (-not (Test-Path $EditorHome)) {
        Write-Skip "$Name`: $EditorHome not found"
        return
    }
    $homeDisplay = Get-DisplayPath $EditorHome
    $rulesDir = Join-Path $EditorHome $Cfg.rules_dir
    $entryPath = Join-Path $EditorHome $Cfg.entry
    if (Get-Link $rulesDir) { Remove-Path -Path $rulesDir -Label "$Name rules (junction)" }
    if ($Cfg.plugin_dir) {
        $pd = Join-Path $EditorHome $Cfg.plugin_dir
        if (Get-Link $pd) { Remove-Path -Path $pd -Label "$Name plugin (junction)" }
    }
    $ext = if ($Cfg.rules_ext) { "$($Cfg.rules_ext)" } else { ".md" }
    $flavor = if ($Cfg.rules_flavor) { "$($Cfg.rules_flavor)" } else { "trae" }
    $display = if ($Cfg.display) { "$($Cfg.display)" } else { $Name }
    $subagent = if ($Cfg.subagent) { "$($Cfg.subagent)" } else { "内置 Agent" }
    $rulesDisplay = Get-DisplayPath $rulesDir
    $expected = [System.Collections.Generic.List[string]]::new()
    $hashLedger = [ordered]@{}
    $hashFile = Join-Path $rulesDir ".claude-hashes"
    if (Test-Path $hashFile) {
        try {
            $oldHashes = Get-Content $hashFile -Raw -Encoding utf8 | ConvertFrom-Json
            foreach ($p in $oldHashes.PSObject.Properties) { $hashLedger[$p.Name] = $p.Value }
        } catch {
            Write-Host "    [!!]  .claude-hashes parse failed: $($_.Exception.Message) -- rebuilding baseline" -ForegroundColor Yellow
        }
    }

    if ($CleanLegacy) {
        foreach ($n in $LEGACY_ROOT) {
            $p = Join-Path $EditorHome $n
            if (Test-Path -LiteralPath $p) { Remove-Path -Path $p -Label "$Name root/$n" }
        }
        if ($Cfg.plugin_dir) {
            $pd = Join-Path $EditorHome $Cfg.plugin_dir
            if (Test-Path -LiteralPath $pd) { Remove-Path -Path $pd -Label "$Name plugin/$($Cfg.plugin_dir)" }
        }
        $oldLedger = Get-Ledger (Join-Path $rulesDir ".claude-managed")
        foreach ($old in $oldLedger) {
            $p = Join-Path $rulesDir $old
            if (Test-Path -LiteralPath $p) { Remove-Path -Path $p -Label "$Name old-rule/$old" }
        }
        foreach ($base in $LEGACY_RULE_BASES) {
            foreach ($e in @(".md", ".mdc")) {
                $p = Join-Path $rulesDir "$base$e"
                if (Test-Path -LiteralPath $p) { Remove-Path -Path $p -Label "$Name stale-rule/$base$e" }
            }
        }
        foreach ($d in @("skills", "agents")) {
            $p = Join-Path $EditorHome $d
            $link = Get-Link $p
            if ($link) { Remove-Path -Path $p -Label "$Name $d (junction)" }
        }
    }

    if ($DoEntry) {
        $entry = New-AgentsContent -ToolName $display -HomeDisplay $homeDisplay -RulesDisplay $rulesDisplay -Subagent $subagent -Flavor $flavor
        $entryName = Split-Path $Cfg.entry -Leaf
        Write-IfChanged -Path $entryPath -Content $entry -Label "$Name entry/$($Cfg.entry)"
        $expected.Add($entryName) | Out-Null
        $hashLedger[$entryName] = [ordered]@{
            src     = $ENTRY_SOURCE
            srcHash = (Get-FileHash -LiteralPath (Join-Path $CLAUDE_DIR $ENTRY_SOURCE) -Algorithm SHA256).Hash
            dstHash = (Get-TextHash $entry)
        }
    }

    if ($DoRules) {
        $srcRules = @(Get-ChildItem (Join-Path $CLAUDE_DIR "rules") -File -Filter "*.md" |
            Where-Object { $RULE_EXCLUDE -notcontains $_.Name } | Sort-Object Name)
        foreach ($r in $srcRules) {
            $base = $r.BaseName
            if ($RULE_RENAMES.ContainsKey($r.Name)) { $base = [IO.Path]::GetFileNameWithoutExtension($RULE_RENAMES[$r.Name]) }
            elseif ($RULE_RENAMES.ContainsKey($base)) { $base = [IO.Path]::GetFileNameWithoutExtension($RULE_RENAMES[$base]) }
            $dst = Join-Path $rulesDir "$base$ext"
            $content = Convert-RuleContent -Text ([IO.File]::ReadAllText($r.FullName)) -Flavor $flavor -SourceName $r.Name
            Write-IfChanged -Path $dst -Content $content -Label "$Name rules/$base$ext"
            $expected.Add("$base$ext") | Out-Null
            $hashLedger["$base$ext"] = [ordered]@{
                src     = "rules/$($r.Name)"
                srcHash = (Get-FileHash -LiteralPath $r.FullName -Algorithm SHA256).Hash
                dstHash = (Get-TextHash $content)
            }
        }
    }

    if ($Cfg.guard_rule) {
        $guardSrc = Join-Path $CLAUDE_DIR $Cfg.guard_rule
        if (Test-Path -LiteralPath $guardSrc) {
            $guardName = Split-Path $guardSrc -Leaf
            $dst = Join-Path $rulesDir $guardName
            $guardText = [IO.File]::ReadAllText($guardSrc)
            Write-IfChanged -Path $dst -Content $guardText -Label "$Name rules/$guardName"
            $expected.Add($guardName) | Out-Null
            $hashLedger[$guardName] = [ordered]@{
                src     = "$($Cfg.guard_rule)"
                srcHash = (Get-FileHash -LiteralPath $guardSrc -Algorithm SHA256).Hash
                dstHash = (Get-TextHash $guardText)
            }
        }
    }

    if ($DoRules) {
        # Remove alt-extension variants for managed basenames (CORE.md vs CORE.mdc etc.)
        $expectedBases = @($expected | ForEach-Object { [IO.Path]::GetFileNameWithoutExtension($_) })
        foreach ($f in @(Get-ChildItem $rulesDir -File -Force -ErrorAction SilentlyContinue)) {
            if ($f.Name -eq ".claude-managed" -or $f.Name -eq ".claude-hashes" -or $expected.Contains($f.Name)) { continue }
            if ($expectedBases -contains $f.BaseName) {
                Remove-Path -Path $f.FullName -Label "$Name variant-rule/$($f.Name)"
            }
        }
        $ledger = Join-Path $rulesDir ".claude-managed"
        $prev = Get-Ledger $ledger
        foreach ($old in $prev) {
            if (-not $expected.Contains($old)) {
                $p = Join-Path $rulesDir $old
                if (Test-Path -LiteralPath $p) { Remove-Path -Path $p -Label "$Name orphan-rule/$old" }
            }
        }
        if (-not $DryRun) { New-Item -ItemType Directory -Path $rulesDir -Force | Out-Null }
        Set-Ledger -Path $ledger -Entries @($expected)
    }

    if (($DoRules -or $DoEntry) -and $hashLedger.Count -gt 0) {
        $finalHashes = $hashLedger
        if ($DoRules) {
            $finalHashes = [ordered]@{}
            foreach ($k in $hashLedger.Keys) {
                if ($expected.Contains($k)) { $finalHashes[$k] = $hashLedger[$k] }
            }
        }
        $hashJson = ($finalHashes | ConvertTo-Json -Depth 4) + "`n"
        Write-IfChanged -Path $hashFile -Content $hashJson -Label "$Name rules/.claude-hashes"
    }

    if ($Cfg.plugin_dir) {
        # The Cursor plugin rules dir is fully managed: drop anything not expected
        # (old 00-CLAUDE.mdc, injected variants) so no duplicate basenames remain.
        if ($DoRules) {
            foreach ($f in @(Get-ChildItem $rulesDir -File -Force -ErrorAction SilentlyContinue)) {
                if ($f.Name -eq ".claude-managed" -or $f.Name -eq ".claude-hashes") { continue }
                if (-not $expected.Contains($f.Name)) {
                    Remove-Path -Path $f.FullName -Label "$Name plugin-orphan/$($f.Name)"
                }
            }
            # ~/.cursor/rules shadows the plugin (double Always-Apply): drop collisions.
            $shadow = Join-Path $EditorHome "rules"
            if (Test-Path $shadow) {
                foreach ($f in @(Get-ChildItem $shadow -File -Force -ErrorAction SilentlyContinue)) {
                    $collides = $expected.Contains($f.Name) -or $expected.Contains("$($f.BaseName).mdc")
                    if ($collides) { Remove-Path -Path $f.FullName -Label "$Name shadow-rule/$($f.Name)" }
                }
            }
        }
        Deploy-CursorPluginMeta -Cfg $Cfg -HomeDir $EditorHome
    }

    if ($DoSkills -and $Cfg.skills_dir) {
        Deploy-Skills -Cfg $Cfg -EditorHome $EditorHome -Name $Name
    }
    if ($DoAgents -and $Cfg.agents_dir) {
        Deploy-Agents -Cfg $Cfg -EditorHome $EditorHome -Name $Name
    }
}

function Deploy-CursorPluginMeta {
    param($Cfg, [string]$HomeDir)
    $pluginDir = Join-Path $HomeDir $Cfg.plugin_dir
    $mfPath = Join-Path $CLAUDE_DIR "MANIFEST.yaml"
    if (-not (Test-Path $mfPath)) {
        Write-Fail "MANIFEST.yaml missing - skip plugin.json"
        return
    }
    $mf = Get-Content $mfPath -TotalCount 25
    $vm = [regex]::Match(($mf | Out-String), '(?m)^\s*version:\s*"?([0-9.]+)"?')
    if (-not $vm.Success) {
        Write-Fail "MANIFEST.yaml version missing - skip plugin.json"
        return
    }
    $ver = $vm.Groups[1].Value
    $metaDir = Join-Path $pluginDir ".cursor-plugin"
    $obj = [ordered]@{
        name        = "claude-config"
        displayName = "Claude Config Rules"
        description = "Global AI assistant rules adapted from ~/.claude (SSOT) by sync.ps1."
        version     = $ver
        author      = @{ name = "local" }
        rules       = "./rules/"
        keywords    = @("claude", "rules", "governance", "local")
    }
    $json = ($obj | ConvertTo-Json -Depth 5) + "`n"
    Write-IfChanged -Path (Join-Path $metaDir "plugin.json") -Content $json -Label "cursor plugin.json"
    $stamp = "version=$ver`nrules=$(@(Get-ChildItem (Join-Path $pluginDir "rules") -File -Filter *.mdc -ErrorAction SilentlyContinue).Count)`n"
    Write-IfChanged -Path (Join-Path $pluginDir ".sync-stamp") -Content $stamp -Label "cursor .sync-stamp"
}

function Get-TextHash {
    param([string]$Text)
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        return (($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($Text)) | ForEach-Object { $_.ToString('x2') }) -join '')
    } finally { $sha.Dispose() }
}

function Get-TransformedSkillText {
    param([string]$Text)
    $t = Convert-TextOnly $Text
    $t = $t -replace [regex]::Escape('Claude Code'), '本工具'
    $t = $t -replace [regex]::Escape('本工具 用对应原生工具'), '本工具使用对应原生工具'
    return $t
}

function Sync-SkillDir {
    param([string]$Src, [string]$Dst, [string]$ToolName, [string]$Label)
    if (-not (Test-Path -LiteralPath $Src)) { Write-Skip "Source missing: $Label"; return }
    $dstLink = Get-Link $Dst
    if ($dstLink) { Remove-Path -Path $Dst -Label "$Label (junction)" }
    $dstFull = [IO.Path]::GetFullPath($Dst)
    $claudeFull = [IO.Path]::GetFullPath($CLAUDE_DIR)
    if ($dstFull.StartsWith($claudeFull, [StringComparison]::OrdinalIgnoreCase)) {
        Write-Fail "refusing to write into SSOT: $Dst"
        return
    }
    $files = @(Get-ChildItem -LiteralPath $Src -Recurse -File | Sort-Object FullName)
    $expected = [ordered]@{}
    foreach ($f in $files) {
        $rel = $f.FullName.Substring($Src.Length).TrimStart('\')
        if ($f.Extension -ieq ".md") {
            $text = Get-TransformedSkillText ([IO.File]::ReadAllText($f.FullName))
            $expected[$rel] = @{ Kind = "text"; Hash = (Get-TextHash $text); Text = $text }
        } else {
            $expected[$rel] = @{ Kind = "file"; Hash = (Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash; Src = $f.FullName }
        }
    }
    $same = $true
    if (Test-Path -LiteralPath $Dst) {
        $dstFiles = @(Get-ChildItem -LiteralPath $Dst -Recurse -File)
        if ($dstFiles.Count -ne $expected.Count) { $same = $false }
        else {
            foreach ($rel in $expected.Keys) {
                $p = Join-Path $Dst $rel
                if (-not (Test-Path -LiteralPath $p)) { $same = $false; break }
                if ((Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash -ne $expected[$rel].Hash) { $same = $false; break }
            }
        }
    } else { $same = $false }
    if ($same) { Write-Skip "Unchanged: $Label"; $script:STATS.Skipped++; return }
    if ($DryRun) { Write-Dry "Would copy: $Label"; $script:STATS.Changed++; return }
    if (Test-Path -LiteralPath $Dst) { Remove-Item -LiteralPath $Dst -Recurse -Force }
    New-Item -ItemType Directory -Path $Dst -Force | Out-Null
    $utf8 = New-Object System.Text.UTF8Encoding $false
    foreach ($rel in $expected.Keys) {
        $p = Join-Path $Dst $rel
        $dir = Split-Path $p -Parent
        if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
        $e = $expected[$rel]
        if ($e.Kind -eq "text") { [IO.File]::WriteAllText($p, $e.Text, $utf8) }
        else { Copy-Item -LiteralPath $e.Src -Destination $p -Force }
    }
    Write-Fix "Copied: $Label ($($expected.Count) files)"
    $script:STATS.Changed++
}

function Deploy-Skills {
    param($Cfg, [string]$EditorHome, [string]$Name)
    $srcRoot = Join-Path $CLAUDE_DIR "skills"
    $dstRoot = Join-Path $EditorHome $Cfg.skills_dir
    if (Get-Link $dstRoot) { Remove-Path -Path $dstRoot -Label "$Name skills (junction)" }
    $skills = @(Get-ChildItem $srcRoot -Directory | Where-Object { $SKILL_EXCLUDE -notcontains $_.Name } | Sort-Object Name)
    $ledger = Join-Path $dstRoot ".claude-managed"
    $prev = Get-Ledger $ledger
    if (-not $DryRun) { New-Item -ItemType Directory -Path $dstRoot -Force | Out-Null }
    foreach ($s in $skills) {
        Sync-SkillDir -Src $s.FullName -Dst (Join-Path $dstRoot $s.Name) -Label "$Name skills/$($s.Name)"
    }
    foreach ($old in $prev) {
        if ($skills.Name -notcontains $old) {
            $p = Join-Path $dstRoot $old
            if (Test-Path -LiteralPath $p) { Remove-Path -Path $p -Label "$Name orphan-skill/$old" }
        }
    }
    Set-Ledger -Path $ledger -Entries @($skills.Name)
}

function Deploy-Agents {
    param($Cfg, [string]$EditorHome, [string]$Name)
    $srcRoot = Join-Path $CLAUDE_DIR "agents"
    $dstRoot = Join-Path $EditorHome $Cfg.agents_dir
    if (Get-Link $dstRoot) { Remove-Path -Path $dstRoot -Label "$Name agents (junction)" }
    $files = @(Get-ChildItem $srcRoot -File -Filter "*.md" | Where-Object { $AGENT_EXCLUDE -notcontains $_.Name } | Sort-Object Name)
    $ledger = Join-Path $dstRoot ".claude-managed"
    $prev = Get-Ledger $ledger
    if (-not $DryRun) { New-Item -ItemType Directory -Path $dstRoot -Force | Out-Null }
    foreach ($f in $files) {
        Write-IfChanged -Path (Join-Path $dstRoot $f.Name) -Content ([IO.File]::ReadAllText($f.FullName)) -Label "$Name agents/$($f.Name)"
    }
    foreach ($old in $prev) {
        if ($files.Name -notcontains $old) {
            $p = Join-Path $dstRoot $old
            if (Test-Path -LiteralPath $p) { Remove-Path -Path $p -Label "$Name orphan-agent/$old" }
        }
    }
    Set-Ledger -Path $ledger -Entries @($files.Name)
}

function Deploy-ProjectRules {
    param([string]$ProjectRoot)
    $rootFull = [IO.Path]::GetFullPath($ProjectRoot)
    $claudeFull = [IO.Path]::GetFullPath($CLAUDE_DIR).TrimEnd('\')
    if ($rootFull.TrimEnd('\') -ieq $claudeFull -or
        $rootFull.StartsWith($claudeFull + '\', [StringComparison]::OrdinalIgnoreCase)) {
        Write-Skip "Project root is ~/.claude (or inside it) - skip"
        return
    }
    if (-not (Test-Path $rootFull)) { Write-Fail "Project root missing: $rootFull"; return }
    $cfg = $MF.editors.cursor
    $rulesDir = Join-Path $rootFull ".cursor\rules"
    $subagent = if ($cfg.subagent) { "$($cfg.subagent)" } else { "Task" }
    $entry = New-AgentsContent -ToolName "Cursor" -HomeDisplay "~/.cursor" `
        -RulesDisplay (Get-DisplayPath $rulesDir) -Subagent $subagent -Flavor "cursor"
    Write-IfChanged -Path (Join-Path $rulesDir "00-AGENTS.mdc") -Content $entry -Label "project 00-AGENTS.mdc"
    $srcRules = @(Get-ChildItem (Join-Path $CLAUDE_DIR "rules") -File -Filter "*.md" |
        Where-Object { $RULE_EXCLUDE -notcontains $_.Name } | Sort-Object Name)
    foreach ($r in $srcRules) {
        $base = $r.BaseName
        if ($RULE_RENAMES.ContainsKey($r.Name)) { $base = [IO.Path]::GetFileNameWithoutExtension($RULE_RENAMES[$r.Name]) }
        elseif ($RULE_RENAMES.ContainsKey($base)) { $base = [IO.Path]::GetFileNameWithoutExtension($RULE_RENAMES[$base]) }
        $content = Convert-RuleContent -Text ([IO.File]::ReadAllText($r.FullName)) -Flavor "cursor" -SourceName $r.Name
        Write-IfChanged -Path (Join-Path $rulesDir "$base.mdc") -Content $content -Label "project rules/$base.mdc"
    }
}

# ---- main --------------------------------------------------------------
Write-Host ""
Write-Host "  Claude Config -> Editors (schema v2)" -ForegroundColor Cyan
Write-Host "  Source: $CLAUDE_DIR" -ForegroundColor DarkGray
Write-Host "  Scope : entry=$(if ($DoEntry) { 'yes' } else { 'no' }) rules=$(if ($DoRules) { 'yes' } else { 'no' }) skills=$(if ($DoSkills) { 'yes' } else { 'no' }) agents=$(if ($DoAgents) { 'yes' } else { 'no' })$(if ($CleanLegacy) { ' +clean' })" -ForegroundColor DarkGray
if ($DryRun) { Write-Host "  [DRY RUN] no changes" -ForegroundColor Yellow }
Write-Host ""

foreach ($name in @($MF.editors.PSObject.Properties.Name)) {
    if ($name -eq "_comment") { continue }
    $cfg = $MF.editors.$name
    if ($cfg.enabled -eq $false) { Write-Skip "$name disabled"; continue }
    if (-not $cfg.rules_dir -and -not $cfg.entry) { Write-Skip "$name has no channel"; continue }
    Write-Host "  -- $name -------------------------------------------" -ForegroundColor DarkGray
    Deploy-Editor -Cfg $cfg -Name $name
    Write-Host ""
}

if ($ProjectRules -or $ProjectRulesPath) {
    $targets = [System.Collections.Generic.List[string]]::new()
    if ($ProjectRules) { $targets.Add((Get-Location).Path) }
    if ($ProjectRulesPath) { foreach ($p in ($ProjectRulesPath -split '[;,]')) { $t = $p.Trim().Trim('"'); if ($t) { $targets.Add($t) } } }
    foreach ($t in $targets) { Deploy-ProjectRules -ProjectRoot $t }
}

Write-Host "  =====================================================" -ForegroundColor DarkGray
Write-Host "  Changed: $($script:STATS.Changed)  Removed: $($script:STATS.Removed)  Skipped: $($script:STATS.Skipped)  Failed: $($script:STATS.Failed)"
if ($script:STATS.Failed -gt 0) { exit 1 }
exit 0
