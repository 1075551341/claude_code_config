# Claude Code 全栈开发工具中心

> 统一管理 Claude Code 的 Skills、Agents、MCP、Hooks、Plugins、Scripts 等工具，
> 通过软链接同步到 Cursor、Trae、Qoder、Windsurf 等编辑器，一处维护，多处共享。

---

## 目录结构

```
~/.claude/
├── CLAUDE.md              # 全局行为规范（核心配置）
├── settings.json          # 设置（插件、钩子、权限、MCP）
├── .mcp.json              # MCP 服务器配置
├── skills/                # 技能库（57 个）
├── agents/                # 智能体（39 个）
├── rules/                 # 开发规则（3 个）
├── hooks/                 # 钩子脚本（14 个）
│   ├── pre-*.py           #   前置钩子（安全拦截/任务规划）
│   ├── post-*.py          #   后置钩子（格式化/lint/测试/提交）
│   └── stop-*.py          #   停止钩子（日报/README/通知）
├── scripts/               # 运维脚本（9 个）
│   ├── sync-tools.ps1     #   多编辑器同步
│   ├── update-toolbox.ps1 #   工具库检查更新
│   ├── health-check.ps1   #   环境健康检查
│   ├── search-github-tools.ps1  # GitHub 热门工具搜索
│   └── collect-experience.ps1   # 开发经验收集
├── plugins/               # 已安装插件（16 个）
├── backups/               # 自动备份
├── daily_summary/         # 每日工作摘要
├── experiences/           # 开发经验积累
├── logs/                  # 操作日志
└── plans/                 # 任务计划
```

---

## 核心设计理念

| 原则 | 说明 |
|------|------|
| **零中断执行** | `Bash(*)` 全量放行 + `bypassPermissions` 模式，deny 列表兜底安全 |
| **先计划后开发** | 复杂任务自动生成 plan.md → 分步开发 → 全面测试 → 更新 README |
| **自动测试** | 代码修改后自动运行测试，失败时反馈给 AI 自动修复 |
| **一处维护** | ~/.claude 为唯一数据源，软链接同步到所有编辑器 |
| **中文优先** | 工具描述、文档、注释使用中文，代码和 commit 使用英文 |
| **持续积累** | 开发经验自动收集，工具库定期更新 |

---

## MCP 服务器（9 个）

| 名称 | 功能 | 用途 |
|------|------|------|
| **redis** | Redis 数据库 | 缓存、队列、会话、键值存储 |
| **postgres** | PostgreSQL 数据库 | SQL 查询、数据管理、事务 |
| **sqlite** | SQLite 数据库 | 轻量数据库、本地存储 |
| **filesystem** | 文件系统 | 读写 D:\apdms 项目目录 |
| **memory** | 持久化记忆 | 跨会话知识图谱、经验记忆 |
| **brave-search** | 网页搜索 | Brave 搜索引擎 |
| **fetch** | HTTP 请求 | 获取网页和 API 数据 |
| **puppeteer** | 浏览器自动化 | 截图、爬虫、E2E 测试 |
| **sequential-thinking** | 结构化推理 | 复杂问题逐步分解 |

---

## Skills 技能库（57 个）

### 后端开发（10）

| 技能 | 描述 |
|------|------|
| `api-development` | RESTful API 设计与实现 |
| `api-mock` | Mock.js/Faker.js/MSW 模拟服务 |
| `db-migration` | 数据库迁移（Knex/Prisma/TypeORM） |
| `middleware` | Express 中间件（认证/日志/限流） |
| `mcp-builder` | MCP 服务器构建 |
| `nodejs-backend` | Node.js 后端最佳实践 |
| `python-backend` | Python 后端最佳实践 |
| `scheduled-task` | 定时任务（cron/BullMQ） |
| `socket-event` | Socket.io 事件处理 |
| `sql-database` | SQL 数据库开发优化 |

### 前端开发（8）

| 技能 | 描述 |
|------|------|
| `frontend-design` | 生产级前端界面设计 |
| `react-component` | React 组件 + Hooks 最佳实践 |
| `vue-development` | Vue 3 Composition API 开发 |
| `typescript` | TypeScript 类型安全 |
| `uniapp-development` | UniApp 跨平台开发 |
| `icon-search` | 图标搜索（Iconify/IconPark） |
| `theme-config` | 主题配置（Ant Design/Tailwind） |
| `web-artifacts-builder` | 复杂 Web 制品构建 |

### 全栈通用（7）

| 技能 | 描述 |
|------|------|
| `fullstack-auth` | JWT/OAuth2.0 认证授权 + RBAC |
| `state-management` | 状态管理（Zustand/Pinia/Redux） |
| `websocket-realtime` | WebSocket 实时通信 |
| `i18n-support` | 国际化（i18next/vue-i18n） |
| `env-config` | 环境配置管理 |
| `monorepo-management` | Monorepo 管理（Turborepo/pnpm） |
| `database-design` | 数据库表结构设计 |

### 架构与性能（7）

| 技能 | 描述 |
|------|------|
| `caching-strategy` | 缓存策略（Redis/内存/CDN/HTTP） |
| `rate-limiting` | 限流防护（令牌桶/滑动窗口） |
| `message-queue` | 消息队列（BullMQ/Redis Streams） |
| `search-engine` | 搜索实现（MeiliSearch/ES） |
| `data-validation` | 数据校验（Zod/Pydantic） |
| `file-upload` | 文件上传（分片/OSS/图片处理） |
| `logging-monitoring` | 日志监控（Pino/Prometheus） |

### 测试与质量（9）

| 技能 | 描述 |
|------|------|
| `code-review` | 代码审查 |
| `code-refactor` | 代码重构 |
| `code-standards` | 代码规范 |
| `error-handling` | 错误处理 |
| `performance-optimization` | 性能优化 |
| `regex-helper` | 正则表达式助手 |
| `security-best-practices` | 安全最佳实践 |
| `testing-standards` | 测试规范（单元/集成/E2E） |
| `web-testing` | Playwright Web 测试 |

### 运维部署（4）

| 技能 | 描述 |
|------|------|
| `deploy-script` | 部署脚本（PM2/Docker/K8s） |
| `docker-devops` | Docker 容器化与 CI/CD |
| `nginx-config` | Nginx 配置生成 |
| `cicd-pipeline` | CI/CD 流水线配置 |

### 文档办公（6）

| 技能 | 描述 |
|------|------|
| `doc-coauthoring` | 协同文档撰写 |
| `docx` | Word 文档处理 |
| `pdf` | PDF 文档处理 |
| `pptx` | PPT 演示文稿 |
| `report-generator` | 报告文档生成 |
| `xlsx` | Excel 电子表格 |

### 创意设计（4）

| 技能 | 描述 |
|------|------|
| `algorithmic-art` | p5.js 算法艺术生成 |
| `canvas-design` | 视觉设计创作 |
| `slack-gif-creator` | Slack 动画 GIF 制作 |
| `theme-factory` | 制品主题样式套件 |

### 工具链（2）

| 技能 | 描述 |
|------|------|
| `git-workflow` | Git 工作流最佳实践 |
| `skill-creator` | 技能创建与管理 |

---

## Agents 智能体（39 个）

| 智能体 | 角色 | 职责 |
|--------|------|------|
| `ai-engineer` | AI 开发工程师 | LLM 集成、RAG、Prompt 工程 |
| `api-tester` | API 测试专家 | 接口测试、验证、报告 |
| `backend-developer` | 后端工程师 | API、业务逻辑、数据库 |
| `business-analyst` | 业务分析师 | 数据分析、KPI、运营报告 |
| `code-quality-checker` | 质量检查员 | 代码规范、静态分析 |
| `code-reviewer` | 审查专家 | 全面代码审查、PR 评审 |
| `component-architect` | 组件架构师 | 组件设计、拆分建议 |
| `data-engineer` | 数据工程师 | ETL、数据仓库、BI |
| `database-architect` | 数据库架构师 | DB 设计、选型、优化 |
| `debugger` | 调试专家 | 错误排查、崩溃分析 |
| `devops-engineer` | DevOps 工程师 | CI/CD、容器化、监控 |
| `doc-generator` | 文档工程师 | API 文档、技术说明 |
| `email-writer` | 邮件撰写 | 商务邮件、信函 |
| `frontend-developer` | 前端工程师 | UI 组件、交互、性能 |
| `git-expert` | Git 专家 | 分支管理、冲突解决 |
| `incident-responder` | 故障响应 | 生产故障、应急处理 |
| `legacy-modernizer` | 现代化专家 | 技术迁移、框架升级 |
| `meeting-notes` | 会议记录 | 纪要、行动项整理 |
| `mermaid-expert` | 图表专家 | 流程图、架构图 |
| `mobile-developer` | 移动端工程师 | RN、Flutter、小程序 |
| `nodejs-reviewer` | Node.js 审查 | TS 后端代码审查 |
| `observability-engineer` | 可观测性 | 监控、链路追踪 |
| `payment-integration` | 支付集成 | 微信/支付宝/Stripe |
| `performance-analyzer` | 性能分析 | 瓶颈分析、优化 |
| `ppt-creator` | PPT 专家 | 汇报材料制作 |
| `project-manager` | 项目经理 | 需求、进度、风险 |
| `prompt-engineer` | Prompt 工程师 | 提示词设计优化 |
| `python-pro` | Python 专家 | 脚本、算法、自动化 |
| `python-reviewer` | Python 审查 | FastAPI/Flask 审查 |
| `qa-engineer` | 测试工程师 | 测试用例、自动化 |
| `react-reviewer` | React 审查 | 组件、Hooks 审查 |
| `refactoring-expert` | 重构专家 | 代码重构、消除技术债 |
| `security-scanner` | 安全扫描 | 漏洞检测、安全审计 |
| `software-architect` | 架构师 | 架构设计、技术选型 |
| `sql-pro` | SQL 专家 | 复杂查询、性能优化 |
| `terraform-specialist` | Terraform | IaC、云资源编排 |
| `typescript-pro` | TS 专家 | 类型系统、泛型 |
| `ui-designer` | UI 设计师 | 界面设计、交互设计 |
| `weekly-report` | 周报撰写 | 工作总结、汇报 |

---

## Hooks 钩子脚本（14 个）

### PreToolUse 前置钩子

| 钩子 | 触发条件 | 功能 |
|------|----------|------|
| `pre-bash-guard.py` | Bash | 危险命令拦截（rm -rf、格式化、强推等） |
| `pre-task-planner.py` | Task/Bash/Write | 复杂任务自动生成计划文档 |
| `pre-context-injector.py` | Task/Write/Edit/Bash | 项目上下文注入 |
| `pre-dep-checker.py` | Bash | npm/pip 包名安全检查 |

### PostToolUse 后置钩子

| 钩子 | 触发条件 | 功能 |
|------|----------|------|
| `post-edit-format.py` | Edit/Write/MultiEdit | 自动格式化（Prettier/Ruff/Black） |
| `post-edit-lint.py` | Edit/Write/MultiEdit | ESLint + TypeScript 类型检查 |
| `post-secret-detector.py` | Edit/Write/MultiEdit | 密钥/Token/密码泄露检测 |
| `post-doc-reminder.py` | Edit/Write/MultiEdit | 无注释函数提醒 |
| `post-operation-log.py` | 所有工具 | 操作日志记录 |
| `post-auto-commit.py` | Edit/Write/MultiEdit | 累计 3+ 变更自动 git commit |
| `post-test-runner.py` | Edit/Write/MultiEdit | 自动运行测试，失败反馈修复 |

### Stop 停止钩子

| 钩子 | 功能 |
|------|------|
| `stop-daily-summary.py` | 生成每日工作摘要（方便写周报） |
| `stop-readme-updater.py` | 有计划的任务完成后自动更新 README |
| `stop-notify.py` | Windows 桌面通知（任务完成提醒） |

---

## Scripts 运维脚本（9 个）

| 脚本 | 功能 | 用法 |
|------|------|------|
| `sync-tools.ps1` | 软链接同步到 Cursor/Trae/Qoder/Windsurf | 管理员运行 |
| `sync-tools.bat` | BAT 入口（双击运行） | 双击即可 |
| `sync-tools.sh` | Bash 版同步（Git Bash/WSL） | `bash sync-tools.sh` |
| `sync-rules.bat` | 规则文件同步 | 双击即可 |
| `sync-rules.sh` | Bash 版规则同步 | `bash sync-rules.sh` |
| `update-toolbox.ps1` | 工具库完整性检查 + 缺失提醒 | 定期运行 |
| `health-check.ps1` | 环境健康检查（Python/Node/Git/MCP） | 排障时运行 |
| `search-github-tools.ps1` | GitHub 热门工具搜索与安全评估 | 定期运行 |
| `collect-experience.ps1` | 从 Git/日志收集开发经验 | 周报时运行 |

---

## Plugins 插件（16 个）

| 插件 | 描述 |
|------|------|
| `chrome-devtools-mcp` | Chrome DevTools 浏览器调试 |
| `claude-code-setup` | Claude Code 配置推荐 |
| `claude-md-management` | CLAUDE.md 管理优化 |
| `code-review` | 代码审查 |
| `commit-commands` | Git 提交和 PR 管理 |
| `context7` | 第三方库文档查询 |
| `feature-dev` | 功能开发辅助 |
| `firecrawl` | 网页爬取和数据提取 |
| `frontend-design` | 前端设计辅助 |
| `github` | GitHub 集成 |
| `playwright` | Playwright 浏览器自动化 |
| `ralph-loop` | 循环任务调度 |
| `security-guidance` | 安全指导 |
| `skill-creator` | 技能创建工具 |
| `superpowers` | 增强功能 |
| `typescript-lsp` | TypeScript LSP 支持 |

---

## Rules 开发规则（3 个）

| 规则 | 启用条件 | 描述 |
|------|----------|------|
| `RULES_CORE.md` | 始终启用 | 核心规则：角色定位、代码规范、注释模板 |
| `RULES_BACKEND.md` | 后端开发时 | API 设计、数据库规范、安全基线 |
| `RULES_FRONTEND.md` | 前端开发时 | 组件规范、样式、性能检查清单 |

---

## 多编辑器同步

### 软链接架构

```
~/.claude/skills/  ← 唯一数据源
    ├── ~/.cursor/skills/     (软链接)
    ├── ~/.trae/skills/       (软链接)
    ├── ~/.qoder/skills/      (软链接)
    └── ~/.windsurf/skills/   (软链接)

~/.claude/agents/  ← 唯一数据源
    ├── ~/.cursor/agents/     (软链接)
    ├── ~/.trae/agents/       (软链接)
    ├── ~/.qoder/agents/      (软链接)
    └── ~/.windsurf/agents/   (软链接)

~/.claude/rules/   ← 唯一数据源
    ├── ~/.cursor/rules/      (软链接)
    └── ...
```

### 一键同步

```powershell
# PowerShell（推荐，需管理员权限）
powershell -ExecutionPolicy Bypass -File ~/.claude/scripts/sync-tools.ps1

# 或双击 BAT 文件
~/.claude/scripts/sync-tools.bat

# 或 Git Bash
bash ~/.claude/scripts/sync-tools.sh
```

---

## 日常运维

```powershell
# 环境健康检查
powershell -ExecutionPolicy Bypass -File ~/.claude/scripts/health-check.ps1

# 工具库完整性检查
powershell -ExecutionPolicy Bypass -File ~/.claude/scripts/update-toolbox.ps1

# 搜索 GitHub 热门工具
powershell -ExecutionPolicy Bypass -File ~/.claude/scripts/search-github-tools.ps1

# 收集开发经验
powershell -ExecutionPolicy Bypass -File ~/.claude/scripts/collect-experience.ps1 D:\apdms
```

---

## 权限安全策略

### 允许（自动执行，不中断）

- 所有文件读写操作（Read/Write/Edit/MultiEdit）
- 所有 Bash 命令（`Bash(*)`）
- 所有 MCP 工具调用（`mcp__*`）
- 网络搜索和抓取

### 禁止（deny 列表拦截）

- `rm -rf /`、`format`、`mkfs` 等破坏性系统命令
- `git push --force` 到 main/master 分支
- `npm publish` 发布包
- `terraform destroy` 销毁基础设施
- `redis-cli FLUSHALL/FLUSHDB` 清空数据
- 读取生产环境密钥文件（.pem/.key/.pfx）

---

## 统计总览

| 类别 | 数量 | 说明 |
|------|------|------|
| Skills | 57 | 覆盖前后端、测试、运维、文档、设计 |
| Agents | 39 | 覆盖全栈开发各角色 |
| MCP 服务器 | 9 | 数据库 + 搜索 + 文件 + 浏览器 |
| Plugins | 16 | 官方增强插件 |
| Hooks | 14 | 安全拦截 + 自动格式化/测试/提交 |
| Rules | 3 | 核心 + 前端 + 后端 |
| Scripts | 9 | 同步 + 检查 + 搜索 + 经验收集 |
| **总计** | **147** | |

---

## 更新记录

### 2026-03-21 - 全面优化升级

- **权限**：`Bash(*)` + `bypassPermissions` 模式，彻底消除执行中断
- **Hooks**：新增 `post-test-runner.py` 自动测试运行器（14 个）
- **Skills**：新增 7 个全栈技能（缓存/上传/日志/校验/搜索/队列/限流），总计 57 个
- **Scripts**：新增 `health-check.ps1`、`search-github-tools.ps1`，总计 9 个
- **MCP**：settings.json 同步 postgres 服务器，总计 9 个
- **CLAUDE.md**：增强自主执行策略、测试规范、工具库维护、经验积累
- **安全**：deny 列表增加 DROP DATABASE/TABLE、rm -rf C:/D: 等防护
- **文档**：README.md 全面重写，中文描述

### 2026-03-20 - 初始版本

- Skills 43 个、Agents 39 个、Hooks 13 个
- 基础同步脚本和工具库

---

_最后更新：2026-03-21_
