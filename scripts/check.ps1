#Requires -Version 5.1
<#
.SYNOPSIS
    Claude Code 环境检查脚本 v3.2（由原「环境健康检查 v2.0」与「工具箱更新 v2.4」合并；已移除对已废弃 settings.sync.json 的检查）

.DESCRIPTION
    全量环境体检：逐项检查、打分并生成报告。

    检查段落：
    S1  目录结构
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
     powershell -ExecutionPolicy Bypass -File C:\Users\dell\.claude\scripts\fix.ps1 -Fix
     powershell -ExecutionPolicy Bypass -File C:\Users\dell\.claude\scripts\sync.ps1
     powershell -ExecutionPolicy Bypass -File C:\Users\dell\.claude\scripts\check.ps1 -Quick
#>

param([switch]$Quick)

Set-StrictMode -Off
$ErrorActionPreference = "SilentlyContinue"

$CLAUDE_DIR = Join-Path $env:USERPROFILE ".claude"
$EDITORS    = @("cursor", "trae", "windsurf", "qoder")
$LINK_DIRS  = @("skills", "agents", "rules")
$SYNC_FILES = @("CLAUDE.md", "CLAUDE-ROUTER.mdc", "SPEC.md", "MANIFEST.yaml", "skills-INDEX.md", "agents-INDEX.md", "rules-INDEX.md")
$ROUTER_DEPLOY_BASENAME = "00-CLAUDE-ROUTER"
$STALE_LINKS = @("hooks", "scripts")
$NATIVE_RULES = @{
    "cursor"   = @{ Dir = (Join-Path $env:USERPROFILE ".cursor\rules"); Ext = ".mdc" }
    "windsurf" = @{ Dir = (Join-Path $env:USERPROFILE ".windsurf\rules"); Ext = ".md" }
    "trae"     = @{ Dir = (Join-Path $env:USERPROFILE ".trae\user_rules"); Ext = ".md" }
    "qoder"    = @{ Dir = (Join-Path $env:USERPROFILE ".qoder\rules"); Ext = ".mdc" }
}
$NATIVE_SKILLS = @{
    "cursor"   = Join-Path $env:USERPROFILE ".cursor\skills-native"
    "windsurf" = Join-Path $env:USERPROFILE ".windsurf\skills-native"
    "trae"     = Join-Path $env:USERPROFILE ".trae\skills-native"
    "qoder"    = Join-Path $env:USERPROFILE ".qoder\skills-native"
}

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

function Get-EditorSettingsPath {
    param([string]$Editor)

    $candidates = switch ($Editor.ToLower()) {
        "cursor" {
            @(
                (Join-Path $env:APPDATA "Cursor\User\settings.json"),
                (Join-Path (Join-Path $env:USERPROFILE ".cursor") "settings.json")
            )
        }
        "windsurf" {
            @(
                (Join-Path $env:APPDATA "Windsurf\User\settings.json"),
                (Join-Path (Join-Path $env:USERPROFILE ".windsurf") "settings.json")
            )
        }
        "trae" {
            @(
                (Join-Path $env:APPDATA "Trae\User\settings.json"),
                (Join-Path (Join-Path $env:USERPROFILE ".trae") "settings.json")
            )
        }
        "qoder" {
            @(
                (Join-Path $env:APPDATA "Qoder\User\settings.json"),
                (Join-Path (Join-Path $env:USERPROFILE ".qoder") "settings.json")
            )
        }
        default {
            @((Join-Path (Join-Path $env:USERPROFILE ".$Editor") "settings.json"))
        }
    }

    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path $candidate)) { return $candidate }
    }
    return $candidates[0]
}

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
    @{ P = "experiences"; D = "Experiences" }
    @{ P = "plans";       D = "Plans" }
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
# S3: Symlink sync status (v14 dual mode)
# =============================================================
Write-Section 3 "Symlink Sync Status (v14)"

function Test-IsReparseLink {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return $false }
    return [bool]((Get-Item $Path -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)
}

function Get-SyncMode {
    param([string]$EditorDir)
    $modePath = Join-Path $EditorDir "sync-mode.json"
    if (-not (Test-Path $modePath)) { return "unknown" }
    try {
        $obj = Get-Content $modePath -Raw -Encoding utf8 | ConvertFrom-Json
        return [string]$obj.mode
    } catch { return "unknown" }
}

foreach ($editor in $EDITORS) {
    $editorDir = Join-Path $env:USERPROFILE ".$editor"
    if (-not (Test-Path $editorDir)) {
        Add-Check "Symlink" ".$editor" "warn" "directory not found -- run sync.ps1"
        continue
    }

    $issues = @()
    $passes = 0
    $syncMode = Get-SyncMode -EditorDir $editorDir

    foreach ($file in $SYNC_FILES) {
        $fp = Join-Path $editorDir $file
        $expected = Join-Path $CLAUDE_DIR $file
        if (-not (Test-Path $fp)) {
            $issues += "$file(missing)"
        } elseif (Test-IsReparseLink $fp) {
            $actual = (Get-Item $fp -Force).Target
            if ($actual -is [array]) { $actual = $actual[0] }
            if ($actual -eq $expected) { $passes++ } else { $issues += "$file(wrong target)" }
        } else {
            $issues += "$file(not a link)"
        }
    }

    $routerExt = if ($NATIVE_RULES.ContainsKey($editor)) { $NATIVE_RULES[$editor].Ext } else { ".mdc" }
    $routerRulesDir = if ($NATIVE_RULES.ContainsKey($editor)) { $NATIVE_RULES[$editor].Dir } else { Join-Path $editorDir "rules" }
    $routerPath = Join-Path $routerRulesDir "${ROUTER_DEPLOY_BASENAME}$routerExt"
    if (Test-Path $routerPath) { $passes++ } else { $issues += "router(missing)" }

    $agentsPath = Join-Path $editorDir "agents"
    $agentsExpected = Join-Path $CLAUDE_DIR "agents"
    if (Test-IsReparseLink $agentsPath) {
        $actual = (Get-Item $agentsPath -Force).Target
        if ($actual -is [array]) { $actual = $actual[0] }
        if ($actual -eq $agentsExpected) { $passes++ } else { $issues += "agents(wrong target)" }
    } else { $issues += "agents(not a link)" }

    if ($syncMode -eq "full") {
        $skillsPath = Join-Path $editorDir "skills"
        if (Test-Path $skillsPath) {
            if (Test-IsReparseLink $skillsPath) { $issues += "skills(should not be link in full)" }
            else { $issues += "skills(entity dir in full)" }
        } else { $passes++ }

        $rulesPath = Join-Path $editorDir "rules"
        if (Test-IsReparseLink $rulesPath) { $issues += "rules(should not be link in full)" }
        elseif (Test-Path $rulesPath) { $passes++ }
        else { $issues += "rules(native missing)" }

        if ($NATIVE_RULES.ContainsKey($editor)) {
            $native = $NATIVE_RULES[$editor]
            $rulesSrc = Join-Path $CLAUDE_DIR "rules"
            $expectedRules = if (Test-Path $rulesSrc) {
                (Get-ChildItem $rulesSrc -Filter "*.md" | Where-Object { $_.Name -ne "README.md" }).Count
            } else { 0 }
            $nativeCount = if (Test-Path $native.Dir) {
                (Get-ChildItem $native.Dir -Filter "*$($native.Ext)" -ErrorAction SilentlyContinue).Count
            } else { 0 }
            if ($nativeCount -ge $expectedRules) { $passes++ } else { $issues += "rules-native($nativeCount/$expectedRules)" }
        }

        if ($NATIVE_SKILLS.ContainsKey($editor)) {
            $skillsNative = $NATIVE_SKILLS[$editor]
            $skillsSrc = Join-Path $CLAUDE_DIR "skills"
            $expectedSkills = if (Test-Path $skillsSrc) {
                (Get-ChildItem $skillsSrc -Directory | Where-Object { Test-Path (Join-Path $_.FullName "SKILL.md") }).Count
            } else { 0 }
            $nativeSkillCount = 0
            if (Test-Path $skillsNative) {
                $nativeSkillCount = (Get-ChildItem $skillsNative -Directory -ErrorAction SilentlyContinue |
                    Where-Object { Test-Path (Join-Path $_.FullName "SKILL.md") }).Count
            }
            if ($nativeSkillCount -ge [Math]::Min(1, $expectedSkills)) { $passes++ }
            else { $issues += "skills-native($nativeSkillCount/$expectedSkills)" }
        }
    }
    else {
        foreach ($dir in @("skills")) {
            $lp = Join-Path $editorDir $dir
            $et = Join-Path $CLAUDE_DIR $dir
            if (Test-IsReparseLink $lp) {
                $actual = (Get-Item $lp -Force).Target
                if ($actual -is [array]) { $actual = $actual[0] }
                if ($actual -eq $et) { $passes++ } else { $issues += "$dir(wrong target)" }
            } elseif (Test-Path $lp) { $issues += "$dir(not a link)" }
            else { $issues += "$dir(missing)" }
        }

        if ($NATIVE_RULES.ContainsKey($editor)) {
            $native = $NATIVE_RULES[$editor]
            $rulesPath = $native.Dir
            if (Test-IsReparseLink $rulesPath) { $issues += "rules(should not be link in index)" }
            elseif (Test-Path $rulesPath) { $passes++ }
            else { $issues += "rules(missing)" }
        }

        if ($NATIVE_SKILLS.ContainsKey($editor)) {
            $skillsNative = $NATIVE_SKILLS[$editor]
            if (Test-Path $skillsNative) {
                $issues += "skills-native(stale from full mode)"
            } else { $passes++ }
        }
    }

    foreach ($stale in $STALE_LINKS) {
        $sp = Join-Path $editorDir $stale
        if (Test-Path $sp) {
            if (Test-IsReparseLink $sp) { $issues += "$stale(stale link)" }
        }
    }

    $esPath = Get-EditorSettingsPath $editor
    if (Test-Path $esPath) {
        try {
            $es = Get-Content $esPath -Raw -Encoding utf8 | ConvertFrom-Json
            if ($es.hooks -and $es.hooks.Stop) { $issues += "settings has Stop hooks" }
            $termEditor = $es.'terminal.integrated.env.windows'.'CLAUDE_IN_EDITOR'
            if ($termEditor) { $issues += "terminal CLAUDE_IN_EDITOR pollutes CLI" }
        } catch {}
    }

    $modeLabel = if ($syncMode -eq "unknown") { "mode?" } else { $syncMode }
    if ($issues.Count -eq 0) {
        Add-Check "Symlink" ".$editor" "pass" "$passes checks OK ($modeLabel)"
    } elseif ($passes -ge 6) {
        Add-Check "Symlink" ".$editor" "warn" "${modeLabel}: $($issues -join ', ')"
    } else {
        Add-Check "Symlink" ".$editor" "warn" "not synced ($modeLabel) -- run sync.ps1"
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
