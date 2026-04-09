# Claude Code 全局行为规范

<!--
  ⚠️ 本文件对所有模型（Claude / GLM / Qwen / 其他）强制生效
  模型必须在每次响应前完整读取"强制规则速查"部分
-->

> **跨编辑器说明**：本文件通过软链接在 Claude Code、Cursor、Windsurf、Trae、VS Code 等编辑器间共享。
> 标记 `[Claude Code Only]` 的章节仅适用于 Claude Code CLI，其他编辑器会安全忽略。
> **工具自动匹配**：未明确指定工具时，根据任务场景自动匹配最合适的工具（详见"工具自动调用规则"）。

---

## 快速导航

| 需求 | 跳转 |
|------|------|
| 工具自动匹配规则 | [工具自动调用规则](#工具自动调用规则) |
| Agent 自动委托 | [Agent 路由](#agent-路由) |
| 强制规则清单 | [★ 强制规则速查](#强制规则速查) |
| 跨编辑器兼容 | [跨编辑器工具映射](#跨编辑器工具映射) |
| MCP 服务器列表 | [MCP 工具映射](#mcp-工具映射) |

---

## 跨编辑器工具映射 [Claude Code Only]

本配置通过软链接同步到多个编辑器，各编辑器工具名称映射如下：

| 功能 | Claude Code | Cursor | Windsurf | Gemini CLI | Copilot CLI |
|------|-------------|--------|----------|--------------|-------------|
| 读取文件 | `Read` | `read_file` | `read_file` | `view` | `view` |
| 编辑文件 | `Edit` | `apply_diff` | `edit_file` | `replace` | `edit` |
| 创建文件 | `Write` | `write_file` | `write_file` | `create` | `write` |
| 搜索代码 | `Grep` | `search_files` | `search` | `grep` | `search` |
| 查找文件 | `Glob` | `list_dir` | `glob` | `ls` | `glob` |
| 执行命令 | `Bash` | `run_terminal_cmd` | `run_command` | `bash` | `bash` |
| 调用 Agent | `Task` | `agent` | `agent` | N/A | `agent` |

**编辑器检测**：Hooks 通过以下方式自动检测编辑器环境并安全跳过：
- 环境变量：`VSCODE_PID`, `CURSOR_CHANNEL`, `WINDSURF_APP_VERSION`
- 控制台检测：`GetConsoleWindow() == 0` (Windows), `!isatty(0)` (Unix)
- 路径特征：`.cursor/`, `.windsurf/`, `.trae/` 等

---

## 工具选择指南 [Claude Code Only]

使用**最具体的工具**。有结构化工具时，不要默认使用 Bash。

| 任务            | 首选工具             |
| --------------- | -------------------- |
| 读取单个文件    | `Read`               |
| 按模式查找文件  | `Glob`               |
| 搜索文件内容    | `Grep`               |
| 编写或修补代码  | `Edit` / `MultiEdit` |
| 创建新文件      | `Write`              |
| 运行 shell 命令 | `Bash`（限定范围）   |
| 获取网页内容    | `WebFetch`           |
| 网络搜索        | `WebSearch`          |
| 浏览 UI         | `Computer`           |
| 生成专业子代理  | `Task`               |

**代理委托规则**：任务隔离且范围明确时（代码审查、安全扫描、文档更新）委托给子代理。单个文件读取或简单问题**不生成**代理。

---

## Agent 路由 [Claude Code Only]

根据上下文自动调用正确的子代理：

| 提示中的信号                                         | 委托给代理          |
| ---------------------------------------------------- | ------------------- |
| "review", "check quality", "PR feedback"             | `code-reviewer`     |
| "plan", "design feature", "how should I implement"   | `planner`           |
| "architecture", "design system", "scalability"       | `architect`         |
| "security", "vulnerability", "CVE", "audit"          | `security-reviewer` |
| "write docs", "update README", "JSDoc"               | `doc-writer`        |
| "debug", "why is this failing", "trace error"        | `debugger`          |
| "refactor", "clean up", "dead code"                  | `refactor-cleaner`  |
| "test", "coverage", "TDD"                            | `tdd-guide`         |
| "search codebase", "find implementation", "where is" | `codebase-search`   |

---

## ★ 强制规则速查（每次响应前必须遵守）

> 无论使用何种底层模型，以下规则不可跳过、不可简化、不可遗忘。

```text
[MUST-1]  任务未完成前禁止停止，直到所有步骤全部验证通过
[MUST-2]  修改文件后必须重新读取确认修改已生效，不能假设成功
[MUST-3]  同一问题修复后，必须检查所有关联文件是否存在相同问题
[MUST-4]  执行测试/构建失败后，必须分析根本原因再重试，不能重复同一操作
[MUST-5]  每个功能完成后输出验收清单，逐项确认后才算完成
[NEVER-1] 禁止在未验证的情况下汇报"已完成"
[NEVER-2] 禁止重复同一个失败的方案超过2次
[NEVER-3] 禁止在不可逆操作前不确认（删生产数据/强推主分支/删远端分支）
[NEVER-4] 禁止 cd + 重定向组合：cd /path && cmd 2>/dev/null
[NEVER-5] 禁止 powershell -Command 包裹原生 PowerShell 命令
```

---

## 工具自动调用规则

**核心原则：不需要显式说明工具名称。根据任务描述的自然语言，自动匹配并调用最合适的工具。**

### MCP 工具自然语言匹配矩阵

**匹配优先级**：精确关键词 > 场景语义 > 工具组合

| 自然语言关键词 | 首选工具 | 备用方案 | 典型场景 | 工具前缀 |
|--------------|---------|---------|---------|---------|
| **GitHub 文档** | | | | |
| "github.com/xxx、仓库文档、项目文档" | mcp0_ask_question | mcp1_web_search_exa | 查询 GitHub 仓库 Wiki | `mcp0_*` |
| **语义搜索** | | | | |
| "搜索、查找、找资料、semantic search" | mcp1_web_search_exa | brave | AI 语义搜索相似内容 | `mcp1_*` |
| **URL 获取** | | | | |
| "https://...、网页内容、URL、获取页面" | mcp2_fetch | - | 直接获取指定 URL | `mcp2_*` |
| **设计稿** | | | | |
| "figma.com、figma、设计稿、UI 设计" | mcp3_get_design_context | - | 设计稿转代码 | `mcp3_*` |
| **文件操作** | | | | |
| "读取文件、文件操作、目录结构" | Read / mcp4_* | - | 项目内文件操作 | `mcp4_*` |
| **Git 操作** | | | | |
| "git 状态、提交历史、分支" | mcp5_git_status/log | gh | 本地 Git 操作 | `mcp5_*` |
| **浏览器自动化** | | | | |
| "截图、网页测试、E2E、表单填写" | mcp6_browser_* | mcp8_puppeteer | Playwright 测试 | `mcp6_*` |
| **记忆存储** | | | | |
| "记住、保存上下文、跨会话记忆" | mcp7_create_memory | - | 持久化重要信息 | `mcp7_*` |
| **Puppeteer** | | | | |
| "PDF 生成、打印页面" | mcp8_puppeteer_screenshot | mcp6 | Chrome 自动化 | `mcp8_*` |
| **数据库/其他** | | | | |
| Redis、缓存 | redis | - | 缓存操作 | - |
| SQLite、本地数据库 | sqlite | - | 轻量数据库 | - |
| PostgreSQL、PG | postgres | - | 生产数据库 | - |
| Docker、容器 | docker | - | 容器管理 | - |
| 时间、时区 | time | - | 时间计算 | - |
| 复杂推理、架构设计 | thinking | - | 多方案比较 | - |
| Slack、通知 | slack | - | 消息发送 | - |
| Linear、项目管理 | linear | - | 任务跟踪 | - |

### 自然语言工具匹配规则

**匹配优先级**：精确关键词 > 场景语义 > 工具组合

```
触发条件识别：
├─ 文档/知识查询 → ctx7 (优先) / brave (备选)
│   └─ 关键词：文档、API、用法、示例、reference、手册
├─ 问题/错误排查 → brave (优先) / fetch (备选)
│   └─ 关键词：报错、错误、怎么解决、为什么、如何
├─ URL/网页内容 → fetch (直接访问)
│   └─ 关键词：https://、网址、网页、网站、页面
├─ 批量采集/爬取 → crawl
│   └─ 关键词：爬取、采集、批量、所有页面、sitemap
├─ 数据库操作 → redis/sqlite/postgres (根据上下文识别)
│   └─ 关键词：数据库、查询、表、SQL、缓存
├─ 浏览器操作 → pw (优先) / puppeteer (备选)
│   └─ 关键词：截图、测试、点击、填写、E2E、页面
└─ 推理/规划 → thinking
    └─ 关键词：分析、设计、规划、对比、选择、决策
```

### 工具降级策略

当首选工具不可用时，自动降级到备选方案：

```
ctx7 (技术文档) → brave (网页搜索) → fetch (直接访问)
pw (Playwright) → puppeteer (备选浏览器)
git (本地操作) → gh (GitHub API)
redis/sqlite/postgres → fs (本地文件备选)
```

### Agent 自动匹配规则

| 任务类型        | 自动调用 Agent       |
| --------------- | -------------------- |
| AI/LLM 应用开发 | ai-engineer          |
| 前端 UI 开发    | frontend-developer   |
| 后端 API 开发   | backend-developer    |
| 数据库设计/优化 | database-architect   |
| 代码审查        | code-reviewer        |
| 安全审计        | security-scanner     |
| 性能分析        | performance-analyzer |
| 测试编写        | qa-engineer          |
| 故障排查        | debugger             |
| 文档生成        | doc-generator        |
| DevOps/部署     | devops-engineer      |
| 机器学习开发    | ml-engineer          |
| 游戏开发        | game-developer       |
| 嵌入式/物联网   | embedded-engineer    |
| 构建错误排查    | build-validator      |
| E2E 测试        | e2e-runner           |
| 安全审查        | security-reviewer    |
| 规格文档编写    | spec-writer          |

### 工具调用原则

1. **调用工具**：调用所有可用工具时说明调用的工具("我将使用XX工具")，并给出结果
2. **组合调用**：复杂任务可同时调用多个工具，ctx7 + brave + fetch 组合查找问题
3. **降级策略**：首选工具失败时自动切换备选工具，不询问用户
4. **结果优先**：工具返回结果后直接整合进回答，不逐条展示原始 API 输出

---

## 执行风格

**最大自主权执行，零中断开发。**

- 明确任务直接执行，完成后汇报结果
- 遇到多方案时，自动选最优方案执行，完成后说明理由
- 文件读写、代码修改、安装依赖、运行测试 → 直接做
- 任务链多步操作 → 一次性完成全部步骤
- 权限弹窗/MCP 调用 → 全部自动允许

**唯一需要停下确认的情况：**

- 删除生产数据库数据
- 强制推送到 main/master 分支
- 删除远端分支
- 不可逆的基础设施变更（terraform destroy 等）

---

## 修改彻底性规范（针对三方模型的关键规则）

> 此节专门解决"同一问题多次说明才修改彻底"的问题。

### 修改前：影响面分析

在修改任何代码/配置前，必须先执行：

```bash
1. 搜索所有相同模式：grep -r "问题关键词" --include="*.ts" --include="*.js"
2. 列出所有受影响文件
3. 确认修改范围后一次性全部修改
```

### 修改中：逐文件验证

```markdown
每修改一个文件后：
□ 重新读取该文件确认修改已写入
□ 检查同目录是否有相同问题的兄弟文件
□ 检查是否有引用该文件的上层文件需要同步修改
```

### 修改后：交叉验证清单

```markdown
□ 运行构建/类型检查确认无新错误
□ 搜索是否还有遗漏的相同模式
□ 检查测试文件是否需要同步更新
□ 确认功能端到端可以正常运行
□ 输出"已修改文件列表"供用户核对
```

---

## 计划优先工作流

满足以下任一条件时，必须先出计划再开发：

- 新建项目或模块
- 功能涉及 3 个以上文件
- 涉及架构/数据库/API 设计
- 包含前后端联调
- 任务含"开发"、"实现"、"重构"、"迁移"

### 计划存储路径规则

| 计划类型                                    | 存储位置                      | 示例                           |
| ------------------------------------------- | ----------------------------- | ------------------------------ |
| **全局计划**（Claude 配置优化、工具链管理） | `~/.claude/plans/`            | Claude Code 配置优化           |
| **项目计划**（功能开发、重构、项目级架构）  | `<项目根目录>/.claude/plans/` | `D:/apdms/pdms/.claude/plans/` |

**判断依据：**

- 计划内容涉及特定项目代码 → 项目目录
- 计划内容涉及 Claude Code 工具本身、全局配置 → 全局目录
- 不确定时优先放项目目录（计划跟随项目走）

**执行步骤：**

1. 根据计划类型确定存储路径，创建 `<路径>/plan.md`（任务分析 + 分步计划 + 风险 + 验收标准）
2. 按计划逐步执行，每步验证后继续
3. 开发完成后运行全量测试
4. 生成/更新 `README.md`

**免计划场景：** 修 bug、改配置、加注释、格式化代码

---

## 自动测试规范

每次功能开发完成后必须执行测试：

```markdown
优先级顺序：

1. vitest/jest/pytest 等框架 → 运行对应测试命令
2. TypeScript 项目 → tsc --noEmit 类型检查
3. ESLint/Ruff → 代码规范检查
4. API 开发 → curl/httpie 验证关键接口
5. 前端组件 → 确认编译通过，无运行时错误
```

---

## ⚠️ Bash 命令硬性规范

### 绝对禁止

```bash
# ❌ 禁止：cd + 重定向
cd /path && command 2>/dev/null
cd /path && command > output.txt

# ❌ 禁止：powershell -Command 包裹
powershell -Command "Get-Service '*redis*' 2>$null"
```

### 安全替代

```bash
# ✅ 目录操作
npm --prefix D:/apdms/backend run dev
git -C D:/apdms status
Get-ChildItem D:/apdms

# ✅ 服务检查
Get-Service -Name redis
sc query Redis

# ✅ 后台启动
Start-Process node -WorkingDirectory D:/apdms/backend -ArgumentList "app.js"
```

| 需求           | ❌ 禁止                     | ✅ 安全                      |
| -------------- | --------------------------- | ---------------------------- |
| 目录内执行命令 | `cd /path && npm run dev`   | `npm --prefix /path run dev` |
| 检查目录       | `cd /path && ls`            | `Get-ChildItem /path`        |
| 检查服务       | `powershell -Command "..."` | `Get-Service redis`          |
| Git 操作       | `cd /path && git status`    | `git -C /path status`        |

---

## 代码风格

- 语言：TypeScript 优先，Python 3.11+
- 缩进：2 空格（JS/TS），4 空格（Python）
- 引号：单引号（JS/TS），双引号（Python）
- 文件名：kebab-case（前端），snake_case（Python）
- 命名：组件 PascalCase / 变量函数 camelCase / 常量 UPPER_SNAKE_CASE
- TypeScript 禁止 `any`，Python 函数必须有类型注解

---

## 全栈开发规范

### 前端

- React/Vue + TypeScript，禁止 `any`
- CSS Modules 或 Tailwind，禁止全局样式污染
- 单文件不超过 300 行
- 列表 > 500 项时使用虚拟滚动

### 后端

- 统一响应：`{ "code": 0, "msg": "ok", "data": {} }`
- 参数化查询，禁止拼接 SQL
- JWT 中间件统一鉴权
- 所有异步必须 try/catch，禁止裸 await

### 数据库

- 查询走索引，禁止 `SELECT *`
- Migration 脚本必须可回滚
- 敏感字段加密存储

---

## Git 规范

```text
commit message 格式：<type>(<scope>): <描述>
type: feat | fix | refactor | perf | test | docs | chore | ci
```

**未经确认绝对不执行：**

- `git push origin main/master`
- `git push --force` / `git push -f`
- `git branch -D`
- `git push origin --delete`

---

## Windows 环境规范

```powershell
# 服务管理
sc query Redis
Get-Service -Name redis
net start Redis / net stop Redis

# 端口检查
netstat -ano | findstr :3000
Get-NetTCPConnection -LocalPort 3000

# 进程管理
Get-Process node
Stop-Process -Name node -Force

# 路径检查
Test-Path D:/apdms/frontend
Get-ChildItem D:/apdms/backend
```

---

## 错误处理

- 先分析根本原因，不修表面症状
- 修复后说明：原因 + 修复方式 + 如何避免
- 同一方法失败不超过 2 次，立即换思路
- EPERM 先检查文件是否被进程占用

---

## 工具库维护

- 新发现实用工具 → 添加到 `~/.claude/skills/`
- 工具库变更后 → 运行 `sync.ps1` 同步到编辑器
- **同步脚本仅同步** `rules/`、`agents/`、`skills/` **与** `CLAUDE.md` **副本**；`settings.json` / MCP / hooks 仍以 `~/.claude` 与各编辑器自身配置为准，不覆盖编辑器模型
- 经验教训 → 记录到 `~/.claude/experiences/`
- 定期运行 `sync.ps1` 同步工具库
- 插件缓存过大或异常时 → 可清空 `~/.claude/plugins/cache/`（停止相关进程后操作，下次使用会重新下载）

---

## 输出格式

- 沟通语言：中文
- 代码块必须标注语言类型
- 较长步骤用编号列表
- 重要警告用 ⚠️ 标注
- 成功完成用 ✅ 确认
- **任务完成时必须输出：已修改文件列表 + 验收清单**

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

_版本：v3.0 | 更新：2026-04-09_
