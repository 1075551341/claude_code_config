# Claude Code 全局配置文档

> Claude Code / Trae / Windsurf / Cursor 等 AI 编辑器的统一全局配置。完整索引 → [`SPEC.md`](SPEC.md) | 归属 → [`MANIFEST.yaml`](MANIFEST.yaml)

---

## 目录

- [简介](#简介)
- [目录结构](#目录结构)
- [MCP 工具](#mcp-工具)
- [智能体 Agents](#智能体-agents)
- [技能库 Skills](#技能库-skills)
- [规则规范 Rules](#规则规范-rules)
- [生命周期钩子 Hooks](#生命周期钩子-hooks)
- [同步脚本 Scripts](#同步脚本-scripts)
- [使用指南](#使用指南)

---

## 简介

本仓库包含 `Claude Code` / `Trae` / `Windsurf` / `Cursor` 等 AI 编程助手的全局配置，通过统一的代理 (Agents)、技能 (Skills)、规则 (Rules)、模型上下文协议 (MCP) 和生命周期脚本，打造高度自动化、规范化和高效的 AI 辅助开发环境。

---

## 目录结构

```text
.claude/
├── .mcp.json           # MCP 服务器配置
├── settings.json       # Claude 编辑器设置
├── CLAUDE.md           # 全局行为规范
├── README.md           # 本文件（总览）
│
├── agents/             # 8 核心 Agent + catalog 43（见 agents/README.md）
├── skills/             # 17 全局 skill + catalog 97（见 skills/README.md）
├── rules/              # 8 全局规则 + catalog 15（见 rules/README.md）
├── hooks/              # 24 个 .py 生命周期钩子（CLI 专用，见 hooks/README.md）
├── scripts/            # 维护脚本 sync/check/fix 等（14 个，见 scripts/README.md）
├── plugins/            # 插件与市场（plugins/cache/ 为下载缓存，可删后自动重建）
├── plans/              # 全局计划（多数环境已 gitignore，按需创建）
├── experiences/        # 经验教训与复盘速记（配合 collect-experience 脚本）
├── tasks/              # 任务记录（运行时）
├── sessions/           # 会话历史（运行时）
├── logs/               # 运行日志
├── projects/           # 按项目索引的会话/元数据（运行时）
├── file-history/       # 编辑历史快照（运行时）
├── backups/            # 配置备份（按需）
├── cache/              # 通用缓存（可清空）
├── shell-snapshots/    # Shell 快照临时文件（可清空）
├── daily_summary/      # 每日总结输出（钩子生成）
├── session-env/        # 会话环境状态（运行时）
├── telemetry/          # 遥测/统计（如有）
└── history.jsonl       # 操作历史记录
```

以下目录/文件通常**不应**手动删除：`settings.json`、`.mcp.json`、`agents/`、`skills/`、`rules/`、`hooks/`、`scripts/`、`CLAUDE.md`；会话与日志按个人需要归档。

**缓存清理（安全、可再下载）**：停止相关进程后，可删除 `plugins/cache/` 下全部内容、`cache/`、`shell-snapshots/*`，下次使用插件或 MCP 时会重新拉取。

**详细维护说明**（同步策略、launcher、`fix.ps1` 行为）：见 [`scripts/README.md`](scripts/README.md）。

---

## 停止所有相关进程

```powershell
# 终止所有 node 进程和 claude 相关进程
Get-Process | Where-Object { $_.Name -eq "node" } | Stop-Process -Force
Get-Process | Where-Object { $_.Name -like "*claude*" } | Stop-Process -Force
```

---

## MCP 工具

MCP (Model Context Protocol) 为 AI 助手提供外部环境和数据交互能力。

### 已配置服务器（18，以 `~/.claude/.mcp.json` 为准）

| 服务器        | 类型     | 功能说明                           |
| ------------- | -------- | ---------------------------------- |
| **redis**     | 数据库   | Redis 缓存、队列、键值存储操作     |
| **sqlite**    | 数据库   | SQLite 数据库 SQL 查询和管理       |
| **postgres**  | 数据库   | PostgreSQL 数据库操作              |
| **fs**        | 文件系统 | 本地文件系统读写操作               |
| **fetch**     | HTTP     | 网页内容和 API 数据获取            |
| **brave**     | 搜索     | Brave 搜索引擎，网页搜索能力       |
| **crawl**     | 爬虫     | Firecrawl 网页爬取和内容提取       |
| **pw**        | 浏览器   | Playwright 浏览器自动化 + E2E 测试 |
| **puppeteer** | 浏览器   | 浏览器自动化、截图、爬虫（备选）   |
| **git**       | 开发工具 | 本地 Git 历史、diff、分支          |
| **gh**        | 开发工具 | GitHub PR/Issue/仓库操作           |
| **ctx7**      | 文档     | 技术文档实时查询检索               |
| **docker**    | 基础设施 | 容器与镜像管理                     |
| **time**      | 基础设施 | 时间与时区                         |
| **thinking**  | 推理     | 结构化逐步思考（Sequential Thinking） |
| **memory**    | 记忆     | 持久化知识图谱和会话记忆           |
| **slack**     | 通信     | Slack 消息发送与频道管理           |
| **exa**       | 搜索     | Exa AI 语义搜索引擎                |
| **linear**    | 项目管理 | Linear 项目管理与 Issue 跟踪       |

---

## 智能体 Agents

**8 核心**（`agents/`）+ **43 领域**（`catalog/agents/`，含 gstack 5 角色）。详表 → [`agents/README.md`](agents/README.md)

| 类型 | 示例 |
|------|------|
| 核心 8 | planner, code-explorer, code-reviewer, build-error-resolver, architect, spec-reviewer, context-manager, agentic-orchestrator |
| Catalog | frontend-developer, security-reviewer, eng-reviewer, python-reviewer … |

```
使用 [agent-name] 处理 [任务描述]
```

---

## 技能库 Skills

**17 全局**（`skills/`：P0×4 + workflow×9 + meta×4）+ **97 领域**（`catalog/skills/`）。详表 → [`skills/README.md`](skills/README.md)

| 层级 | 技能 |
|------|------|
| P0 强制 | using-superpowers, brainstorming, verification-before-completion, systematic-debugging |
| Workflow | writing-plans, executing-plans, test-driven-development, subagent-driven-development … |
| Meta | memory-compression, spec-validation, karpathy-guidelines, caveman-compress |
| Catalog | api-development, frontend-design, deep-research, ui-ux-pro-max … |

项目级按需复制：`python ~/.claude/scripts/migrate-from-legacy.py --project <path> --skill <name>`

---

## 规则规范 Rules

**8 全局**（`rules/`）+ **15 领域**（`catalog/rules/`）。详表 → [`rules/README.md`](rules/README.md)

| 文件 | 加载 |
|------|------|
| CORE.md | alwaysApply |
| SECURITY, GIT, WORKFLOW, AGENTS, MCP, DESIGN | lazy |
| catalog/rules/RULES_*.md | 项目级 lazy-load |

同步：`sync.ps1` 将 `rules/` **格式转换复制**到 Cursor `.mdc` 等原生目录（非目录联接）。

---

## 生命周期钩子 Hooks

`hooks/` 共 **24** 个 `.py` 文件（CLI 专用，`sync.ps1` 不同步到编辑器）。事件映射与 profile → [`hooks/README.md`](hooks/README.md) | [`SPEC.md`](SPEC.md#hooksclaude-code-专用不同步编辑器)

> 编辑器与 CLI 共用 `settings.json`；`fix.ps1 -Fix` 部署 `_editor_hook_launcher.py v2.0`，经 GetConsoleWindow 在编辑器内快速跳过。详见 [`scripts/README.md`](scripts/README.md)。

---

## 同步脚本 Scripts（`~/.claude/scripts/`）

当前为 **PowerShell** 脚本：

| 脚本                        | 版本 | 用途                                                                                                                                               |
| --------------------------- | ---- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **sync.ps1**                | v11.0 | 链接 `CLAUDE.md`/`AGENTS.md`/`skills/`/`agents/`；**格式转换复制** `rules/` 到编辑器原生目录；详见 [`SYNC_GUIDE.md`](SYNC_GUIDE.md) |
| **check.ps1**               | v3.2 | 环境与健康检查（目录、配置、软链接、原生 rules、钩子、运行时、MCP、工具箱），报告 → `logs/check-YYYYMMDD.md`                                    |
| **fix.ps1**                 | v5.0 | 部署 launcher v2.0 + 改写 settings 中 Hook 命令；支持 `-Fix` / `-Restore` |
| **search-github-tools.ps1** | v1.0 | GitHub 热门工具检索与本地技能库对比                                                                                                                |
| **collect-experience.ps1**  | v1.0 | 从日志/Git 等整理经验到 `experiences/`                                                                                                             |

---

## 使用指南

### 1. 修复 Hooks（防止编辑器僵死）

编辑器（Cursor/Windsurf/Trae）与 Claude CLI 共用 `~/.claude/settings.json`。因此在编辑器日志中看到 `C:\Users\DELL\.claude\hooks\*.py` 是正常现象，不代表 `sync.ps1` 同步了 `hooks/`。Hooks 在编辑器中执行会导致**阻塞/死循环**。

**解决方案**：`fix.ps1 -Fix` 部署 `_editor_hook_launcher.py`，将所有 Hook 命令改为经 launcher 调用；编辑器（无控制台）快速跳过，CLI 正常执行。

```powershell
# 诊断（launcher、Hook 命令格式、CLAUDE_IN_EDITOR）
powershell -ExecutionPolicy Bypass -File .claude\scripts\fix.ps1

# 修复：部署 launcher + 改写 settings.json 中 Hook 命令
powershell -ExecutionPolicy Bypass -File .claude\scripts\fix.ps1 -Fix

# 撤销 launcher 包装
powershell -ExecutionPolicy Bypass -File .claude\scripts\fix.ps1 -Restore
```

修复后建议**重启编辑器**，并结合 `check.ps1 -Quick` 与 `~/.claude/logs/operations.log` 验证不再僵死。

### 2. 同步到编辑器

```powershell
# 同步到已安装的编辑器 (Cursor, Windsurf, Trae, Qoder, CodeArts)
powershell -ExecutionPolicy Bypass -File .claude\scripts\sync.ps1

# 预览模式（不实际执行）
powershell -ExecutionPolicy Bypass -File .claude\scripts\sync.ps1 -DryRun

# 强制重建所有软链接
powershell -ExecutionPolicy Bypass -File .claude\scripts\sync.ps1 -Force
```

### 3. 环境检查

```powershell
# 完整检查（含 MCP 连通性测试）
powershell -ExecutionPolicy Bypass -File .claude\scripts\check.ps1

# 快速检查（跳过 MCP 连通性）
powershell -ExecutionPolicy Bypass -File .claude\scripts\check.ps1 -Quick
```

| 前缀     | 行为             |
| -------- | ---------------- |
| `[方法]` | 生成具体功能代码 |
| `[方案]` | 输出技术实现规划 |
| `[解释]` | 逐步解析现有代码 |
| `[修改]` | 对项目增删改查   |
| `[审查]` | 代码质量评审     |

### 4. 快速指令前缀

```powershell
# 检查服务
sc query Redis
Get-Service -Name redis

# 检查端口
netstat -ano | findstr :3000
Get-NetTCPConnection -LocalPort 3000

# 检查进程
tasklist | findstr node
Get-Process node

# 启停服务
net start Redis
net stop Redis
```

---

## 参考来源

本配置整合自以下优质资源：

- [anthropics/skills](https://github.com/anthropics/skills) - Claude 官方技能
- [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) - 完整配置参考
- [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) - 社区技能合集
- [obra/superpowers](https://github.com/obra/superpowers) - 增强技能
- [Chalarangelo/30-seconds-of-code](https://github.com/Chalarangelo/30-seconds-of-code) - 代码片段
- [bytedance/deer-flow](https://github.com/bytedance/deer-flow) - 工作流最佳实践

---

## 配置状态

### Git 提交行为

- **自动提交已禁用**：所有 Git 操作需手动执行
- 手动执行：`git add` → `git commit` → `git push`

### 环境变量

在 `settings.json` 中配置：

- ANTHROPIC_MODEL: 默认模型
- ANTHROPIC_BASE_URL: API 基础地址
- CLAUDE_CODE_MAX_AUTONOMY: 最大自主权模式

---

## 统计（与 SPEC.md / 仓库实际同步，2026-05-23）

| 类别 | 全局 | Catalog | 说明 |
| ---- | ---- | ------- | ---- |
| Skills | 17 | 97 | P0×4 + workflow×9 + meta×4 |
| Agents | 8 | 43 | 含 gstack 5 角色 |
| Rules | 8 | 15 | 语言/领域 lazy-load |
| MCP 服务器 | 18 | — | 权威源 `.mcp.json` |
| Hooks（.py） | 24 | — | CLI 专用 |
| 维护脚本 | 14 | — | `scripts/` |

---
