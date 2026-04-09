# Claude Code 全局行为规范

<!--
  ⚠️ 本文件对所有模型（Claude / GLM / Qwen / 其他）强制生效
  模型必须在每次响应前完整读取"强制规则速查"部分
-->

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

**不需要显式说明工具名称。根据任务场景，自动选择并调用最合适的工具。**

### 场景 → 工具映射（自动触发，无需用户指定）

| 触发场景                                 | 自动调用                      |
| ---------------------------------------- | ----------------------------- |
| 需要查找最新技术文档、库的用法、版本信息 | ctx7（优先）→ brave（备选）   |
| 需要在网络上搜索解决方案、错误原因       | brave → fetch                 |
| 需要访问某个具体 URL 获取内容            | fetch                         |
| 需要爬取网页批量提取内容                 | crawl                         |
| 需要操作本地文件系统（项目目录外）       | fs                            |
| 需要执行 Redis 缓存/队列操作             | redis                         |
| 需要查询或操作 SQLite 数据库             | sqlite                        |
| 需要查询或操作 PostgreSQL 数据库         | postgres                      |
| 需要执行 git 操作（不涉及 GitHub API）   | git                           |
| 需要操作 GitHub PR/Issue/仓库/Actions    | gh                            |
| 需要截图、测试网页、E2E 自动化           | pw（优先）→ puppeteer（备选） |
| 需要 Docker 容器/镜像/服务管理           | docker                        |
| 需要获取当前时间、时区转换               | time                          |
| 复杂推理、多步骤规划、连续/分支思考       | thinking（Sequential Thinking MCP） |
| 需要在会话间记住重要信息、上下文         | memory                        |
| 需要 Slack 消息发送/频道管理             | slack                         |
| 需要 Exa AI 语义搜索                     | exa                           |
| 需要 Linear 项目管理/Issue 跟踪          | linear                        |

### Agent 自动匹配规则

| 任务类型 | 自动调用 Agent |
|----------|----------------|
| AI/LLM 应用开发 | ai-engineer |
| 前端 UI 开发 | frontend-developer |
| 后端 API 开发 | backend-developer |
| 数据库设计/优化 | database-architect |
| 代码审查 | code-reviewer |
| 安全审计 | security-scanner |
| 性能分析 | performance-analyzer |
| 测试编写 | qa-engineer |
| 故障排查 | debugger |
| 文档生成 | doc-generator |
| DevOps/部署 | devops-engineer |
| 机器学习开发 | ml-engineer |
| 游戏开发 | game-developer |
| 嵌入式/物联网 | embedded-engineer |
| 构建错误排查 | build-validator |
| E2E 测试 | e2e-runner |
| 安全审查 | security-reviewer |
| 规格文档编写 | spec-writer |

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
