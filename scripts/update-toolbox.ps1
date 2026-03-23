#Requires -Version 5.1
<#
.SYNOPSIS
    Claude Code 工具库更新检查脚本 v2.1（增强版）
.DESCRIPTION
    检查本地 skills/agents/rules/hooks 完整性，
    检测 MCP 服务器连接状态，校验 settings.json 中 hooks 配置的一致性，
    推荐热门工具和 MCP 服务器，生成更新报告。
.NOTES
    用法：powershell -ExecutionPolicy Bypass -File update-toolbox.ps1
#>

$ErrorActionPreference = "SilentlyContinue"

$CLAUDE_DIR = Join-Path $env:USERPROFILE ".claude"
$SKILLS_DIR = Join-Path $CLAUDE_DIR "skills"
$LOG_FILE = Join-Path (Join-Path $CLAUDE_DIR "logs") "toolbox-update.log"

Write-Host ""
Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Claude Code 工具库更新检查 v2.1 (增强版)   ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$logDir = Split-Path $LOG_FILE -Parent
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
"[$timestamp] 开始工具库更新检查" | Out-File -Append -FilePath $LOG_FILE

# ── 1. 统计当前工具库 ──────────────────────────────────
Write-Host "  当前工具库统计" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

$existingSkills = @()
if (Test-Path $SKILLS_DIR) {
    $existingSkills = Get-ChildItem -Path $SKILLS_DIR -Directory | Select-Object -ExpandProperty Name
}

$agentsDir = Join-Path $CLAUDE_DIR "agents"
$existingAgents = @()
if (Test-Path $agentsDir) {
    $existingAgents = Get-ChildItem -Path $agentsDir -File -Filter "*.md" | Select-Object -ExpandProperty BaseName
}

$rulesDir = Join-Path $CLAUDE_DIR "rules"
$existingRules = @()
if (Test-Path $rulesDir) {
    $existingRules = Get-ChildItem -Path $rulesDir -File -Filter "*.md" | Select-Object -ExpandProperty BaseName
}

$hooksDir = Join-Path $CLAUDE_DIR "hooks"
$existingHooks = @()
if (Test-Path $hooksDir) {
    $existingHooks = Get-ChildItem -Path $hooksDir -File -Filter "*.py" | Select-Object -ExpandProperty BaseName
}

$scriptsDir = Join-Path $CLAUDE_DIR "scripts"
$existingScripts = @()
if (Test-Path $scriptsDir) {
    $existingScripts = Get-ChildItem -Path $scriptsDir -File | Select-Object -ExpandProperty Name
}

Write-Host "   Skills:  $($existingSkills.Count) 个" -ForegroundColor White
Write-Host "   Agents:  $($existingAgents.Count) 个" -ForegroundColor White
Write-Host "   Rules:   $($existingRules.Count) 个" -ForegroundColor White
Write-Host "   Hooks:   $($existingHooks.Count) 个" -ForegroundColor White
Write-Host "   Scripts: $($existingScripts.Count) 个" -ForegroundColor White
Write-Host ""

# ── 2. 全栈开发必备技能检查 ───────────────────────────
Write-Host "  全栈开发工具完整性检查" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

$requiredSkills = @{
    "前端基础"     = @("frontend-design", "react-component", "vue-development", "typescript")
    "后端基础"     = @("api-development", "nodejs-backend", "python-backend")
    "数据库"       = @("sql-database", "db-migration", "database-design")
    "测试"         = @("testing-standards", "code-review")
    "部署运维"     = @("docker-devops", "deploy-script", "nginx-config", "cicd-pipeline")
    "安全"         = @("security-best-practices")
    "文档"         = @("report-generator", "docx", "pdf")
    "工具链"       = @("git-workflow", "api-mock", "regex-helper")
    "状态管理"     = @("state-management")
    "WebSocket"    = @("websocket-realtime", "socket-event")
    "国际化"       = @("i18n-support")
    "环境管理"     = @("env-config")
    "Monorepo"     = @("monorepo-management")
    "性能优化"     = @("performance-optimization")
    "错误处理"     = @("error-handling")
    "缓存策略"     = @("caching-strategy")
    "文件上传"     = @("file-upload")
    "日志监控"     = @("logging-monitoring")
    "数据校验"     = @("data-validation")
    "搜索引擎"     = @("search-engine")
    "消息队列"     = @("message-queue")
    "限流策略"     = @("rate-limiting")
}

$missingSkills = @()
$existingSkillsLower = $existingSkills | ForEach-Object { $_.ToLower() }

foreach ($category in $requiredSkills.Keys | Sort-Object) {
    $skills = $requiredSkills[$category]
    $categoryMissing = @()

    foreach ($skill in $skills) {
        if ($existingSkillsLower -notcontains $skill.ToLower()) {
            $categoryMissing += $skill
            $missingSkills += @{ Category = $category; Skill = $skill }
        }
    }

    if ($categoryMissing.Count -eq 0) {
        Write-Host "   [OK] $category" -ForegroundColor Green
    } else {
        Write-Host "   [缺失] ${category}: $($categoryMissing -join ', ')" -ForegroundColor Red
    }
}

Write-Host ""

# ── 3. MCP 服务器状态检查 ─────────────────────────────
Write-Host "  MCP 服务器状态检查" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

$mcpChecks = @(
    @{ Name = "Redis";      Cmd = "redis-cli"; TestCmd = "redis-cli ping"; Expected = "PONG"; Port = 6379 }
    @{ Name = "PostgreSQL"; Cmd = "psql";      TestCmd = $null;            Expected = $null;  Port = 5432 }
    @{ Name = "SQLite";     Cmd = "sqlite3";   TestCmd = $null;            Expected = $null;  Port = $null }
)

$mcpStatusList = @()

foreach ($mcp in $mcpChecks) {
    $installed = Get-Command $mcp.Cmd -ErrorAction SilentlyContinue
    if (-not $installed) {
        Write-Host "   [ ] $($mcp.Name): 未安装客户端工具" -ForegroundColor DarkGray
        $mcpStatusList += @{ Name = $mcp.Name; Status = "未安装" }
        continue
    }

    if ($mcp.Port) {
        $portOpen = $false
        try {
            $tcp = New-Object System.Net.Sockets.TcpClient
            $tcp.Connect("127.0.0.1", $mcp.Port)
            $portOpen = $tcp.Connected
            $tcp.Close()
        } catch { }

        if (-not $portOpen) {
            Write-Host "   [停] $($mcp.Name): 已安装，服务未运行 (端口 $($mcp.Port))" -ForegroundColor Yellow
            $mcpStatusList += @{ Name = $mcp.Name; Status = "服务未运行" }
            continue
        }
    }

    if ($mcp.TestCmd) {
        try {
            $result = Invoke-Expression $mcp.TestCmd 2>&1
            if ($result -and $result.ToString().Trim() -eq $mcp.Expected) {
                Write-Host "   [运行] $($mcp.Name): 运行正常" -ForegroundColor Green
                $mcpStatusList += @{ Name = $mcp.Name; Status = "正常" }
            } else {
                Write-Host "   [异常] $($mcp.Name): 已安装，响应异常" -ForegroundColor Yellow
                $mcpStatusList += @{ Name = $mcp.Name; Status = "响应异常" }
            }
        } catch {
            Write-Host "   [异常] $($mcp.Name): 已安装，连接测试失败" -ForegroundColor Yellow
            $mcpStatusList += @{ Name = $mcp.Name; Status = "连接失败" }
        }
    } else {
        Write-Host "   [OK] $($mcp.Name): 客户端已安装" -ForegroundColor Green
        $mcpStatusList += @{ Name = $mcp.Name; Status = "已安装" }
    }
}

# ── 3.1 检查 .mcp.json 配置的服务器 ──────────────────
$mcpJsonPath = Join-Path $CLAUDE_DIR ".mcp.json"
if (Test-Path $mcpJsonPath) {
    try {
        $mcpContent = Get-Content $mcpJsonPath -Raw -Encoding utf8
        $mcpConfig = $mcpContent | ConvertFrom-Json
        if ($mcpConfig.mcpServers) {
            $configuredServers = ($mcpConfig.mcpServers | Get-Member -MemberType NoteProperty).Name
            Write-Host ""
            Write-Host "   .mcp.json 中配置了 $($configuredServers.Count) 个服务器:" -ForegroundColor DarkCyan
            foreach ($srv in $configuredServers) {
                $desc = $mcpConfig.mcpServers.$srv._description
                if ($desc) {
                    Write-Host "     · $srv — $desc" -ForegroundColor DarkGray
                } else {
                    Write-Host "     · $srv" -ForegroundColor DarkGray
                }
            }
        }
    } catch {
        Write-Host "   .mcp.json 解析失败: $_" -ForegroundColor Red
    }
}

Write-Host ""

# ── 4. settings.json Hooks 交叉校验 ──────────────────
Write-Host "  Hooks 配置一致性校验" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

$settingsPath = Join-Path $CLAUDE_DIR "settings.json"
$hookIntegrityOk = $true

if (Test-Path $settingsPath) {
    try {
        $settingsContent = Get-Content $settingsPath -Raw -Encoding utf8
        $settings = $settingsContent | ConvertFrom-Json

        if ($settings.hooks) {
            $referencedHooks = @()
            $hookCategories = $settings.hooks | Get-Member -MemberType NoteProperty | Select-Object -ExpandProperty Name

            foreach ($cat in $hookCategories) {
                $entries = $settings.hooks.$cat
                foreach ($entry in $entries) {
                    foreach ($h in $entry.hooks) {
                        if ($h.command -match "python\s+(.+\.py)") {
                            $hookFile = $Matches[1] -replace '/', '\'
                            $referencedHooks += @{
                                Category = $cat
                                File     = $hookFile
                                Timeout  = $h.timeout
                            }
                        }
                    }
                }
            }

            $missingHookFiles = @()
            $validHookFiles = @()
            foreach ($ref in $referencedHooks) {
                if (Test-Path $ref.File) {
                    $validHookFiles += $ref
                } else {
                    $missingHookFiles += $ref
                    $hookIntegrityOk = $false
                }
            }

            Write-Host "   settings.json 引用了 $($referencedHooks.Count) 个 hook 脚本" -ForegroundColor White
            Write-Host "   有效文件: $($validHookFiles.Count) 个" -ForegroundColor Green

            if ($missingHookFiles.Count -gt 0) {
                Write-Host "   缺失文件: $($missingHookFiles.Count) 个" -ForegroundColor Red
                foreach ($mh in $missingHookFiles) {
                    Write-Host "     · [$($mh.Category)] $($mh.File)" -ForegroundColor Red
                }
            }

            # 检查 hooks 目录中有但 settings.json 未引用的文件
            $referencedNames = $referencedHooks | ForEach-Object {
                [System.IO.Path]::GetFileNameWithoutExtension($_.File)
            }
            $unreferenced = $existingHooks | Where-Object { $referencedNames -notcontains $_ }
            if ($unreferenced.Count -gt 0) {
                Write-Host "   未在 settings.json 中引用的 hook: $($unreferenced.Count) 个" -ForegroundColor Yellow
                foreach ($ur in $unreferenced) {
                    Write-Host "     · $ur.py" -ForegroundColor Yellow
                }
            }
        } else {
            Write-Host "   settings.json 中未配置 hooks" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   settings.json 解析失败: $_" -ForegroundColor Red
        $hookIntegrityOk = $false
    }
} else {
    Write-Host "   settings.json 不存在" -ForegroundColor Red
    $hookIntegrityOk = $false
}

Write-Host ""

# ── 5. 推荐 MCP 服务器 ───────────────────────────────
Write-Host "  推荐的 MCP 服务器" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

$recommendedMcps = @(
    @{ Name = "filesystem";         Desc = "本地文件系统读写";        Pkg = "@modelcontextprotocol/server-filesystem" }
    @{ Name = "memory";             Desc = "知识图谱持久化记忆";      Pkg = "@modelcontextprotocol/server-memory" }
    @{ Name = "brave-search";       Desc = "Brave 搜索引擎";          Pkg = "@modelcontextprotocol/server-brave-search" }
    @{ Name = "fetch";              Desc = "网页内容抓取";             Pkg = "@modelcontextprotocol/server-fetch" }
    @{ Name = "redis";              Desc = "Redis 数据库操作";         Pkg = "@modelcontextprotocol/server-redis" }
    @{ Name = "postgres";           Desc = "PostgreSQL 数据库查询";    Pkg = "@modelcontextprotocol/server-postgres" }
    @{ Name = "sqlite";             Desc = "SQLite 数据库操作";        Pkg = "@modelcontextprotocol/server-sqlite" }
    @{ Name = "puppeteer";          Desc = "浏览器自动化操作";         Pkg = "@modelcontextprotocol/server-puppeteer" }
    @{ Name = "sequential-thinking"; Desc = "分步推理增强";            Pkg = "@modelcontextprotocol/server-sequential-thinking" }
    @{ Name = "github";             Desc = "GitHub 仓库管理";          Pkg = "@modelcontextprotocol/server-github" }
)

foreach ($mcp in $recommendedMcps) {
    Write-Host "   $($mcp.Name)" -ForegroundColor Cyan -NoNewline
    Write-Host " - $($mcp.Desc)" -ForegroundColor White
    Write-Host "      $($mcp.Pkg)" -ForegroundColor DarkGray
}

Write-Host ""

# ── 6. 推荐 GitHub 热门工具 ──────────────────────────
Write-Host "  推荐安装的热门开发工具" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

$recommendations = @(
    @{ Name = "shadcn/ui";      Use = "React UI 组件库";         URL = "https://github.com/shadcn-ui/ui" }
    @{ Name = "TanStack Query"; Use = "前端数据请求管理";        URL = "https://github.com/TanStack/query" }
    @{ Name = "Zod";            Use = "TypeScript 数据校验";     URL = "https://github.com/colinhacks/zod" }
    @{ Name = "Prisma";         Use = "Node.js ORM 数据库工具";  URL = "https://github.com/prisma/prisma" }
    @{ Name = "tRPC";           Use = "类型安全的全栈 API";      URL = "https://github.com/trpc/trpc" }
    @{ Name = "Turborepo";      Use = "Monorepo 构建系统";       URL = "https://github.com/vercel/turborepo" }
    @{ Name = "Vitest";         Use = "Vite 原生测试框架";       URL = "https://github.com/vitest-dev/vitest" }
    @{ Name = "Playwright";     Use = "E2E 测试自动化";          URL = "https://github.com/microsoft/playwright" }
    @{ Name = "Biome";          Use = "高性能 Lint + Format";    URL = "https://github.com/biomejs/biome" }
    @{ Name = "Hono";           Use = "轻量高性能 Web 框架";     URL = "https://github.com/honojs/hono" }
    @{ Name = "Drizzle ORM";    Use = "TypeScript ORM";          URL = "https://github.com/drizzle-team/drizzle-orm" }
    @{ Name = "Zustand";        Use = "轻量 React 状态管理";     URL = "https://github.com/pmndrs/zustand" }
    @{ Name = "Pinia";          Use = "Vue 官方状态管理";         URL = "https://github.com/vuejs/pinia" }
    @{ Name = "Socket.io";      Use = "WebSocket 实时通信";      URL = "https://github.com/socketio/socket.io" }
    @{ Name = "i18next";        Use = "国际化解决方案";           URL = "https://github.com/i18next/i18next" }
    @{ Name = "BullMQ";         Use = "Redis 消息队列";           URL = "https://github.com/taskforcesh/bullmq" }
    @{ Name = "Meilisearch";    Use = "轻量全文搜索引擎";         URL = "https://github.com/meilisearch/meilisearch" }
    @{ Name = "ioredis";        Use = "高性能 Redis 客户端";      URL = "https://github.com/redis/ioredis" }
)

foreach ($tool in $recommendations) {
    Write-Host "   $($tool.Name)" -ForegroundColor Cyan -NoNewline
    Write-Host " - $($tool.Use)" -ForegroundColor White
    Write-Host "      $($tool.URL)" -ForegroundColor DarkGray
}

Write-Host ""

# ── 7. 本地开发工具检查 ──────────────────────────────
Write-Host "  本地开发工具检查" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

$devTools = @(
    @{ Cmd = "node";      Name = "Node.js" }
    @{ Cmd = "npm";       Name = "npm" }
    @{ Cmd = "pnpm";      Name = "pnpm" }
    @{ Cmd = "python";    Name = "Python" }
    @{ Cmd = "pip";       Name = "pip" }
    @{ Cmd = "git";       Name = "Git" }
    @{ Cmd = "docker";    Name = "Docker" }
    @{ Cmd = "redis-cli"; Name = "Redis CLI" }
    @{ Cmd = "psql";      Name = "PostgreSQL CLI" }
    @{ Cmd = "code";      Name = "VS Code" }
    @{ Cmd = "cursor";    Name = "Cursor" }
)

$toolInstalled = 0
$toolMissing = 0

foreach ($tool in $devTools) {
    $found = Get-Command $tool.Cmd -ErrorAction SilentlyContinue
    if ($found) {
        $version = ""
        try {
            $versionOutput = & $tool.Cmd --version 2>&1 | Select-Object -First 1
            if ($versionOutput -and $versionOutput -notmatch "error|not recognized") {
                $version = " ($versionOutput)"
            }
        } catch { }
        Write-Host "   [OK] $($tool.Name)$version" -ForegroundColor Green
        $toolInstalled++
    } else {
        Write-Host "   [缺失] $($tool.Name) 未安装" -ForegroundColor Red
        $toolMissing++
    }
}

Write-Host ""

# ── 8. Hooks 详情 ────────────────────────────────────
Write-Host "  Hooks 钩子详情" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

if ($existingHooks.Count -gt 0) {
    $hookTypes = @{ pre = @(); post = @(); stop = @(); other = @() }
    foreach ($hook in $existingHooks) {
        if ($hook -match "^pre-")  { $hookTypes.pre  += $hook }
        elseif ($hook -match "^post-") { $hookTypes.post += $hook }
        elseif ($hook -match "^stop-") { $hookTypes.stop += $hook }
        else { $hookTypes.other += $hook }
    }
    Write-Host "   pre-*  钩子: $($hookTypes.pre.Count) 个" -ForegroundColor White
    foreach ($h in $hookTypes.pre)  { Write-Host "     · $h" -ForegroundColor DarkGray }
    Write-Host "   post-* 钩子: $($hookTypes.post.Count) 个" -ForegroundColor White
    foreach ($h in $hookTypes.post) { Write-Host "     · $h" -ForegroundColor DarkGray }
    Write-Host "   stop-* 钩子: $($hookTypes.stop.Count) 个" -ForegroundColor White
    foreach ($h in $hookTypes.stop) { Write-Host "     · $h" -ForegroundColor DarkGray }
    if ($hookTypes.other.Count -gt 0) {
        Write-Host "   其他钩子: $($hookTypes.other.Count) 个" -ForegroundColor White
        foreach ($h in $hookTypes.other) { Write-Host "     · $h" -ForegroundColor DarkGray }
    }
} else {
    Write-Host "   未发现任何 hooks" -ForegroundColor Yellow
}

Write-Host ""

# ── 9. 生成报告 ──────────────────────────────────────
$mcpSummary = ($mcpStatusList | ForEach-Object { "- $($_.Name): $($_.Status)" }) -join "`n"
$hookSummary = ($existingHooks | ForEach-Object { "- $_" }) -join "`n"

$hookIntegrityText = if ($hookIntegrityOk) { "全部一致" } else { "存在不一致" }

$report = @"
# 工具库更新检查报告
生成时间：$timestamp

## 当前统计
- Skills: $($existingSkills.Count) 个
- Agents: $($existingAgents.Count) 个
- Rules: $($existingRules.Count) 个
- Hooks: $($existingHooks.Count) 个
- Scripts: $($existingScripts.Count) 个

## MCP 服务器状态
$mcpSummary

## Hooks 列表
$hookSummary

## Hooks 配置一致性
$hookIntegrityText

## 缺失技能
$($missingSkills | ForEach-Object { "- [$($_.Category)] $($_.Skill)" } | Out-String)

## 本地工具
- 已安装: $toolInstalled 个
- 未安装: $toolMissing 个

## 建议
1. 运行 sync-tools.ps1 同步到所有编辑器
2. 为缺失技能创建 SKILL.md 文件
3. 确保 MCP 服务器正常运行
4. 检查 settings.json 中 hooks 配置的文件是否都存在
5. 定期检查 GitHub 热门工具是否有新版本
"@

$reportPath = Join-Path (Join-Path $CLAUDE_DIR "logs") "toolbox-report-$(Get-Date -Format 'yyyyMMdd').md"
$report | Out-File -FilePath $reportPath -Encoding utf8

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  报告已保存：$reportPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "  检查结果汇总" -ForegroundColor Green
Write-Host "┌──────────────────────────────────────────────┐" -ForegroundColor DarkGray
Write-Host "│  Skills: $($existingSkills.Count.ToString().PadLeft(3)) 个 | 缺失: $($missingSkills.Count.ToString().PadLeft(2)) 个                │" -ForegroundColor White
Write-Host "│  Hooks:  $($existingHooks.Count.ToString().PadLeft(3)) 个 | 配置: $(if($hookIntegrityOk){'一致'}else{'不一致'})               │" -ForegroundColor White
Write-Host "│  工具:   $($toolInstalled.ToString().PadLeft(3))/$($devTools.Count) 已安装                          │" -ForegroundColor White
Write-Host "│  MCP:    $($mcpStatusList.Count.ToString().PadLeft(3)) 个已检查                          │" -ForegroundColor White
Write-Host "└──────────────────────────────────────────────┘" -ForegroundColor DarkGray
Write-Host ""

if ($missingSkills.Count -eq 0 -and $hookIntegrityOk) {
    Write-Host "  工具库完整，所有检查通过！" -ForegroundColor Green
} elseif ($missingSkills.Count -gt 0) {
    Write-Host "  缺失 $($missingSkills.Count) 个技能，建议补充" -ForegroundColor Yellow
}
if (-not $hookIntegrityOk) {
    Write-Host "  Hooks 配置存在不一致，请检查 settings.json" -ForegroundColor Yellow
}
Write-Host ""
