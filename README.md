# Claude Code 全局配置文件库 (Claude Code Config)

这个仓库包含了 `Claude Code` / `Trae` 等 AI 编程助手的全局配置，旨在通过统一的代理 (Agents)、技能 (Skills)、规则 (Rules)、模型上下文协议 (MCP) 和生命周期脚本，打造一个高度自动化、规范化和高效的 AI 辅助开发环境。

## 目录结构

```text
.claude/
├── agents/      # 自定义 AI 代理角色
├── skills/      # 可复用的特定领域技能库
├── rules/       # 代码和行为规范（前端/后端/核心）
├── hooks/       # 生命周期钩子脚本
├── scripts/     # 实用同步和检查脚本
├── .mcp.json    # 模型上下文协议 (MCP) 配置
├── CLAUDE.md    # 全局行为规范
├── config.json  # Claude 核心配置
└── .gitignore   # Git 忽略配置
```

---

## 🔌 模型上下文协议 (MCP - `.mcp.json`)

MCP (Model Context Protocol) 为 AI 助手提供了丰富的外部环境和数据交互能力。当前配置了以下服务器：

- **`redis`**: 交互 Redis 数据库，支持缓存、队列。
- **`filesystem`**: 本地文件系统操作，允许 AI 读写指定目录。
- **`memory`**: 持久化记忆存储，支持知识图谱和会话记忆。
- **`brave-search`**: Brave 搜索引擎，提供网页搜索能力。
- **`fetch`**: HTTP 请求工具，获取网页内容和 API 数据。
- **`sqlite` & `postgres`**: 关系型数据库操作，支持直接进行 SQL 查询和数据管理。
- **`puppeteer` & `playwright`**: 现代浏览器自动化，支持网页截图、动态内容爬虫和 E2E 测试辅助。
- **`sequential-thinking`**: 辅助 AI 进行复杂问题的逐步推理。
- **`context7`**: 技术文档实时查询，支持各大流行库文档检索。
- **`github`**: GitHub 集成，支持 PR、Issue 和仓库操作。

---

## 🤖 代理角色 (Agents)

`agents/` 目录定义了不同的 AI 角色，帮助在不同场景下提供高度定制化的专家辅助：

- **开发与架构**: `frontend-developer.md`, `backend-developer.md`, `mobile-developer.md`, `software-architect.md`
- **质量与测试**: `code-reviewer.md`, `code-quality-checker.md`, `qa-engineer.md`, `api-tester.md`
- **运维与数据**: `devops-engineer.md`, `database-architect.md`, `data-engineer.md`, `sql-pro.md`
- **产品与管理**: `project-manager.md`, `business-analyst.md`, `ui-designer.md`
- **专用领域**: `security-scanner.md`, `performance-analyzer.md`, `mermaid-expert.md`, `ppt-creator.md`

---

## 🛠️ 核心技能 (Skills)

`skills/` 目录包含了大量独立、可复用的技能模块，AI 可以直接调用这些技能处理特定任务：

- **全栈开发**: `api-development`, `react-component`, `vue-development`, `nodejs-backend`, `python-backend`
- **系统与部署**: `docker-devops`, `deploy-script`, `nginx-config`, `cicd-pipeline`
- **文档与报告**: `docx`, `pptx`, `xlsx`, `pdf`, `report-generator`
- **设计与UI**: `canvas-design`, `theme-factory`, `frontend-design`
- **质量与安全**: `code-refactor`, `error-handling`, `security-best-practices`, `testing-standards`

---

## 📜 规则规范 (Rules)

`rules/` 目录包含了多维度的开发规范，在 AI 编写代码时自动生效：

- **`RULES_CORE.md`**: 全局通用的最佳实践、代码整洁道 (Clean Code)、注释规范和通用响应格式。
- **`RULES_FRONTEND.md`**: 针对前端场景（React/Vue等），包括组件结构、状态管理、Tailwind/CSS 规范及性能优化。
- **`RULES_BACKEND.md`**: 针对后端场景，涵盖 RESTful API 设计、数据库查询规范、错误处理、安全基线等。

---

## 🔗 生命周期钩子 (Hooks)

`hooks/` 包含了在任务执行前后触发的 Python 脚本，以增强自动化流程：

- **执行前 (`pre-*`)**: 依赖检查 (`pre-dep-checker.py`)、上下文注入 (`pre-context-injector.py`)、Bash 防护 (`pre-bash-guard.py`)。
- **编辑后 (`post-edit-*`)**: 自动格式化 (`post-edit-format.py`)、Lint 检查 (`post-edit-lint.py`)、敏感信息检测 (`post-secret-detector.py`)。
- **停止/完成 (`stop-*`)**: 每日总结生成 (`stop-daily-summary.py`)、README 自动更新 (`stop-readme-updater.py`)。

---

## ⚙️ 版本控制与 Gitignore 优化

为了保持配置仓库的纯净，我们优化了 `.gitignore`，**只保留关键配置，忽略运行产生的临时文件和状态**：

- 忽略运行时日志、历史记录、Telemetry 数据：`logs/`, `history/`, `daily_summary/`
- 忽略 AI 执行的具体任务、会话和内存状态：`tasks/`, `sessions/`, `ide/`, `projects/`
- 忽略本地插件缓存、依赖缓存：`plugins/cache/`, `cache/`, `context_cache.json`
- 忽略各种 `.lock` 和 Python 的 `__pycache__`

这样可以确保即使跨设备克隆仓库，也能只拉取纯净、无状态的核心配置环境。
