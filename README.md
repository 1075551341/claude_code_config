# Claude Code 全局配置文档

> Claude Code / Trae / Windsurf / Cursor 等 AI 编辑器的统一全局配置

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
├── agents/             # 39 个专业 AI 代理角色（见 agents/README.md）
├── skills/             # 57 个可复用技能模块（各技能目录下 SKILL.md）
├── rules/              # 3 个代码与行为规范
├── hooks/              # 15 个 .py（14 个生命周期钩子 + `_editor_hook_launcher.py`；CLI；编辑器内由 editor-guard 快速跳过）
├── scripts/            # 工具脚本（sync / check / fix 等，见下文）
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

**详细维护说明**（同步策略、editor-guard、`fix.ps1` 行为）：见 [`scripts/README.md`](scripts/README.md）。

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

### 已配置服务器（19，以 `~/.claude/.mcp.json` 为准）

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

99 个专业领域 AI 代理，覆盖软件开发全流程。

### 按领域分类

| 领域            | 智能体                                                                            |
| --------------- | --------------------------------------------------------------------------------- |
| **前端开发**    | frontend-developer, mobile-developer, react-reviewer, ui-designer, typescript-pro   |
| **后端开发**    | backend-developer, nodejs-reviewer, python-pro, python-reviewer                   |
| **数据库**      | database-architect, sql-pro, data-engineer                                        |
| **测试质量**    | qa-engineer, api-tester, code-quality-checker, code-reviewer                      |
| **安全性能**    | security-scanner, performance-analyzer                                            |
| **架构设计**    | software-architect, component-architect                                           |
| **运维 DevOps** | devops-engineer, observability-engineer, terraform-specialist, incident-responder |
| **工程效能**    | git-expert, refactoring-expert, legacy-modernizer                                 |
| **AI/数据**     | ai-engineer, prompt-engineer, business-analyst                                    |
| **文档沟通**    | doc-generator, meeting-notes, ppt-creator, email-writer, weekly-report            |
| **专项领域**    | payment-integration, project-manager, mermaid-expert, debugger                    |

### 使用方法

```
使用 [agent-name] agent 来 [任务描述]
```

示例：

- `使用 frontend-developer agent 创建用户管理页面`
- `使用 code-reviewer agent 审查这个 PR`
- `使用 debugger agent 排查接口 500 错误`

---

## 技能库 Skills

157 个独立、可复用的技能模块，AI 可直接调用处理特定任务。

### 后端开发 (12)

| 技能                   | 触发场景       | 核心能力                                   |
| ---------------------- | -------------- | ------------------------------------------ |
| **api-development**    | 构建 REST API  | URL 规范、统一响应格式、入参验证、安全基线 |
| **api-mock**           | Mock 数据生成  | Mock.js、Faker.js、MSW 模拟服务            |
| **db-migration**       | 数据库迁移     | Knex.js、Prisma、TypeORM 迁移              |
| **middleware**         | Express 中间件 | 认证、日志、限流、错误处理                 |
| **mcp-builder**        | MCP 服务器开发 | FastMCP/MCP SDK 实现、工具命名规范         |
| **nodejs-backend**     | Node.js 后端   | Express/Koa/Fastify/NestJS 最佳实践        |
| **python-backend**     | Python 后端    | FastAPI/Flask/Django 最佳实践              |
| **scheduled-task**     | 定时任务       | node-cron、node-schedule、Bull 队列        |
| **socket-event**       | WebSocket 通信 | Socket.io 事件定义、房间管理               |
| **sql-database**       | SQL 数据库     | MySQL/PostgreSQL/SQLite 查询优化、索引设计 |
| **message-queue**      | 消息队列       | RabbitMQ、Kafka、Redis 队列                |
| **websocket-realtime** | 实时通信       | WebSocket、Socket.io、实时数据推送         |

### 前端开发 (10)

| 技能                      | 触发场景      | 核心能力                           |
| ------------------------- | ------------- | ---------------------------------- |
| **frontend-design**       | UI 界面设计   | 生产级界面、避免 AI 审美           |
| **icon-search**           | 图标搜索导入  | Iconify、IconPark、FontAwesome     |
| **react-component**       | React 组件    | Hooks、状态管理、性能优化          |
| **theme-config**          | 主题配置      | Ant Design、Element Plus、Tailwind |
| **typescript**            | TypeScript    | 高级类型、工具类型、类型安全       |
| **uniapp-development**    | UniApp 开发   | Vue 3 语法、多端适配               |
| **vue-development**       | Vue 开发      | SFC、Composable、Pinia             |
| **web-artifacts-builder** | 复杂 Web 制品 | React + Tailwind + shadcn/ui       |
| **state-management**      | 状态管理      | Redux、Pinia、Zustand、Jotai       |
| **i18n-support**          | 国际化        | i18next、react-intl、多语言支持    |

### 测试与质量 (11)

| 技能                         | 触发场景   | 核心能力                       |
| ---------------------------- | ---------- | ------------------------------ |
| **code-review**              | 代码审查   | 5 维度审查、标准反馈格式       |
| **code-refactor**            | 代码重构   | 函数提取、类重构、设计模式     |
| **code-standards**           | 代码规范   | 命名规范、目录结构、代码风格   |
| **error-handling**           | 错误处理   | 异常捕获、错误分类、日志记录   |
| **performance-optimization** | 性能优化   | 前端渲染、后端处理、数据库查询 |
| **regex-helper**             | 正则表达式 | 常用模式、性能优化             |
| **security-best-practices**  | 安全实践   | OWASP、SQL 注入、XSS、CSRF     |
| **testing-standards**        | 测试规范   | 单元测试、集成测试、E2E        |
| **web-testing**              | Web 测试   | Playwright 脚本、自动化浏览器  |
| **data-validation**          | 数据验证   | Zod、Yup、Joi 校验库           |
| **rate-limiting**            | 限流控制   | 请求限流、防刷、Token 桶算法   |

### 运维部署 (6)

| 技能                   | 触发场景      | 核心能力                   |
| ---------------------- | ------------- | -------------------------- |
| **deploy-script**      | 部署脚本      | PM2、systemd、Docker、K8s  |
| **docker-devops**      | Docker DevOps | Dockerfile、Compose、CI/CD |
| **nginx-config**       | Nginx 配置    | 反向代理、负载均衡、SSL    |
| **cicd-pipeline**      | CI/CD 流水线  | GitHub Actions、Jenkins    |
| **env-config**         | 环境配置      | dotenv、配置管理、密钥安全 |
| **logging-monitoring** | 日志监控      | Winston、Pino、ELK 栈      |

### 文档办公 (6)

| 技能                 | 触发场景   | 核心能力                   |
| -------------------- | ---------- | -------------------------- |
| **doc-coauthoring**  | 协同写作   | 三阶段工作流、文档结构     |
| **docx**             | Word 文档  | OOXML、修订追踪、文本提取  |
| **pdf**              | PDF 处理   | 文本提取、创建、合并、表单 |
| **pptx**             | PPT 演示   | python-pptx、XML 操作      |
| **report-generator** | 报告生成   | Markdown、PDF、Word、HTML  |
| **xlsx**             | Excel 表格 | openpyxl、公式、图表       |

### 创意设计 (4)

| 技能                  | 触发场景  | 核心能力                     |
| --------------------- | --------- | ---------------------------- |
| **algorithmic-art**   | 算法艺术  | p5.js、种子随机、生成艺术    |
| **canvas-design**     | 视觉设计  | 海报、平面设计、PNG/PDF 输出 |
| **slack-gif-creator** | Slack GIF | 动画 GIF、尺寸优化           |
| **theme-factory**     | 主题样式  | 10 套预设主题、即时生成      |

### 架构与设计 (5)

| 技能                    | 触发场景   | 核心能力                   |
| ----------------------- | ---------- | -------------------------- |
| **database-design**     | 数据库设计 | 范式、索引、分库分表       |
| **caching-strategy**    | 缓存策略   | Redis、CDN、本地缓存设计   |
| **fullstack-auth**      | 全栈认证   | JWT、OAuth、Session、SSO   |
| **monorepo-management** | monorepo   | pnpm workspace、Turborepo  |
| **search-engine**       | 搜索引擎   | Elasticsearch、Meilisearch |

### 工具与工作流 (3)

| 技能              | 触发场景   | 核心能力                     |
| ----------------- | ---------- | ---------------------------- |
| **git-workflow**  | Git 工作流 | 分支策略、提交规范、版本管理 |
| **skill-creator** | 技能创建   | 文件结构、description 编写   |
| **file-upload**   | 文件上传   | 分片上传、OSS、断点续传      |

> 遗留迁移、大规模重构等场景请使用 **agents**：`legacy-modernizer`、`refactoring-expert`（见上表「智能体」），二者不在 `skills/` 目录。

---

## 规则规范 Rules

12 个核心规则文件，AI 编码时自动生效：

| 规则文件              | 作用范围 | 主要内容                           |
| --------------------- | -------- | ---------------------------------- |
| **RULES_CORE.md**     | 全局通用 | 最佳实践、Clean Code、注释规范     |
| **RULES_FRONTEND.md** | 前端场景 | React/Vue 组件、状态管理、CSS 规范 |
| **RULES_BACKEND.md**  | 后端场景 | RESTful API、数据库、错误处理      |
| **RULES_DATABASE.md** | 数据库   | 数据库设计、索引优化、迁移管理     |
| **RULES_DEVOPS.md**   | 运维     | CI/CD、容器化、监控告警             |
| **RULES_GIT.md**      | 版本控制 | Git 工作流、提交规范、分支管理      |
| **RULES_MOBILE.md**   | 移动端   | iOS/Android 开发规范               |
| **RULES_PYTHON.md**   | Python   | Python 最佳实践、类型注解          |
| **RULES_SECURITY.md** | 安全     | 安全最佳实践、漏洞防护              |
| **RULES_TESTING.md**  | 测试     | 测试策略、覆盖率、TDD               |
| **RULES_TYPESCRIPT.md**| TypeScript | 类型安全、高级类型、泛型         |
| **RULES_AI.md**       | AI 开发  | LLM 应用开发、Prompt 工程          |

### 核心规则摘要

- **简单至上**：最小可行方案，拒绝过度设计
- **DRY + 单一职责**：避免重复代码
- **默认防御**：XSS、CSRF、SQL 注入防护
- **错误处理**：覆盖所有边界情况
- **注释规范**：JSDoc/Python docstring，中文优先

---

## 生命周期钩子 Hooks

`hooks/` 目录共 **15** 个 `.py` 文件：**14** 个生命周期钩子脚本 + **`_editor_hook_launcher.py`**（编辑器侧启动/桥接，非业务钩子）。任务执行前后由业务钩子触发（**与编辑器兼容性、editor-guard 细节见** `scripts/README.md`）。

### 编辑后钩子 (PostEdit)

| 脚本                        | 功能           |
| --------------------------- | -------------- |
| **post-edit-format.py**     | 自动代码格式化 |
| **post-edit-lint.py**       | Lint 检查      |
| **post-secret-detector.py** | 敏感信息检测   |
| **post-operation-log.py**   | 操作日志记录   |
| **post-doc-reminder.py**    | 文档更新提醒   |
| **post-test-runner.py**     | 自动运行测试   |
| **post-auto-commit.py**     | 自动提交（若启用） |

> **说明**：钩子由 `~/.claude/settings.json` 引用；`sync.ps1` 不向各编辑器目录同步 `hooks/`。在 Cursor 等编辑器中应配合 `fix.ps1 -Fix` 的 editor-guard，避免阻塞。

### 执行前钩子 (PreToolUse)

| 脚本                        | 功能              |
| --------------------------- | ----------------- |
| **pre-task-planner.py**     | 任务计划生成      |
| **pre-bash-guard.py**       | Bash 命令安全检查 |
| **pre-dep-checker.py**      | 依赖检查          |
| **pre-context-injector.py** | 上下文注入        |

### 停止钩子 (Stop)

| 脚本                       | 功能            |
| -------------------------- | --------------- |
| **stop-daily-summary.py**  | 每日总结生成    |
| **stop-readme-updater.py** | README 自动更新 |
| **stop-notify.py**         | 任务完成通知    |

---

## 同步脚本 Scripts（`~/.claude/scripts/`）

当前为 **PowerShell** 脚本：

| 脚本                        | 版本 | 用途                                                                                                                                               |
| --------------------------- | ---- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **sync.ps1**                | v8.3 | **仅同步 4 项**：`skills/`、`agents/`、`rules/`（软链接）+ `CLAUDE.md`（复制）到各编辑器；自动清理旧版遗留的 `hooks/`、`scripts/` 软链接；写入 `CLAUDE_IN_EDITOR` 环境哨兵 |
| **check.ps1**               | v3.0 | 环境与健康检查（目录、配置安全、软链接、钩子、运行时、MCP 依赖、工具箱统计），报告写入 `logs/check-YYYYMMDD.md`                                    |
| **fix.ps1**                 | v3.0 | **修复编辑器僵死/死循环**：为所有 `.py` hooks 注入 editor-guard（基于环境变量、`TERM_PROGRAM`、stdin 负载联合识别编辑器环境并自动跳过）；支持 `-Fix` / `-Restore` |
| **search-github-tools.ps1** | v1.0 | GitHub 热门工具检索与本地技能库对比                                                                                                                |
| **collect-experience.ps1**  | v1.0 | 从日志/Git 等整理经验到 `experiences/`                                                                                                             |

---

## 使用指南

### 1. 修复 Hooks（防止编辑器僵死）

编辑器（Cursor/Windsurf/Trae）与 Claude CLI 共用 `~/.claude/settings.json`。因此在编辑器日志中看到 `C:\Users\DELL\.claude\hooks\*.py` 是正常现象，不代表 `sync.ps1` 同步了 `hooks/`。Hooks 在编辑器中执行会导致**阻塞/死循环**。

**解决方案**：为每个 `.py` hook 文件添加 editor-guard，使其在编辑器环境中自动退出，CLI 环境中正常执行。

```powershell
# 诊断（仅检查，不修改）
powershell -ExecutionPolicy Bypass -File .claude\scripts\fix.ps1

# 修复：给所有 .py hooks 添加 editor-guard
powershell -ExecutionPolicy Bypass -File .claude\scripts\fix.ps1 -Fix

# 如需撤销修复（恢复原始 .py 文件）
powershell -ExecutionPolicy Bypass -File .claude\scripts\fix.ps1 -Restore
```

修复后建议**重启编辑器**，并结合 `check.ps1 -Quick` 与 `~/.claude/logs/operations.log` 验证不再僵死。

### 2. 同步到编辑器（仅 4 项）

```powershell
# 同步到所有支持的编辑器 (Cursor, Trae, Qoder, Windsurf)
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

## 统计（与仓库实际文件同步，请随增减更新）

| 类别          | 数量 |
| ------------- | ---- |
| MCP 服务器    | 19   |
| 智能体 Agents | 99   |
| 技能 Skills   | 157  |
| 规则文件      | 12   |
| 钩子脚本（.py） | 48（包含启动器、业务钩子及备份文件） |
| 维护脚本      | 5    |

---
