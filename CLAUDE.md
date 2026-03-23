# Claude Code 全局行为规范

## 执行风格

**最大自主权执行，零中断开发。所有操作自动完成，不等待人工确认。**

- 对于明确的任务，直接执行，**绝不**反复确认细节
- 文件读写、代码修改、运行测试、安装依赖 —— 直接做，完成后汇报结果
- 遇到多个可行方案时，自动比较选择最优方案执行，完成后说明选择理由
- **绝不**在每个小步骤前问"我可以继续吗？"
- 权限弹窗/工具授权/MCP 调用 → **全部自动允许**，不等待手动操作
- Shell/Bash 命令 → 直接执行，不逐条确认（deny 列表中的除外）
- 只在涉及**不可逆操作**（删除生产数据、强制推送到主分支、删除远端分支）时才停下来确认
- 任务链中的多步操作 → 一次性完成全部步骤，中间不暂停

---

## 计划优先工作流

**复杂功能/组件/项目开发时，必须遵循「先计划 → 再开发 → 后测试」流程。**

### 触发条件（满足任一）

- 新建项目或模块
- 功能涉及 3 个以上文件
- 涉及架构设计、数据库设计、API 设计
- 包含前后端联调
- 任务描述含"开发"、"实现"、"重构"、"迁移"等关键词

### 执行步骤

1. **生成计划**：在项目 `.claude/plans/` 下创建 `plan.md`，包含：
   - 任务分析与技术方案
   - 分步实施计划（每步可独立验证）
   - 风险点与应对措施
   - 完成验收标准
2. **分步开发**：按计划逐步执行，每完成一步验证后继续
3. **全面测试**：开发完成后运行所有相关测试，确保功能和接口正常
4. **更新文档**：生成或更新 `README.md`，记录架构、用法、API 等

### 简单任务（免计划）

- 修复单个 bug
- 修改配置文件
- 添加注释或文档
- 格式化代码

---

## 自动测试规范

**每次功能开发完成后，必须执行测试确保正常。**

```
测试执行优先级：
1. 如有 vitest/jest/pytest 等测试框架 → 运行对应测试
2. 如有 TypeScript → 运行 tsc --noEmit 类型检查
3. 如有 ESLint/Ruff → 运行代码检查
4. 如为 API 开发 → 使用 curl/httpie 验证接口
5. 如为前端组件 → 确认编译通过，无运行时错误
```

---

## ⚠️ Bash 命令硬性规范

### 禁止：cd + 重定向组合

```bash
# ❌ 永远禁止
cd /path && command 2>/dev/null
cd /path && command > output.txt

# ✅ 正确替代
ls -la D:/apdms/frontend
npm --prefix D:/apdms/backend run dev
git -C D:/apdms status
```

### 禁止：powershell -Command 包裹

```bash
# ❌ 禁止
powershell -Command "Get-Service '*redis*' 2>$null"

# ✅ 正确替代
Get-Service -Name redis
sc query Redis
```

### 安全写法速查表

| 需求 | ❌ 禁止 | ✅ 安全 |
|------|---------|---------|
| 进入目录执行 | `cd /path && npm run dev` | `npm --prefix /path run dev` |
| 检查目录 | `cd /path && ls 2>/dev/null` | `Get-ChildItem /path` |
| 检查服务 | `powershell -Command "..."` | `Get-Service redis` |
| 后台启动 | `cd /path && node app.js &` | `Start-Process node -WorkingDirectory /path` |
| Git 操作 | `cd /path && git status` | `git -C /path status` |

---

## 代码风格

- 语言：TypeScript 优先，Python 使用 3.11+
- 缩进：2 空格（JS/TS），4 空格（Python）
- 引号：单引号（JS/TS），双引号（Python）
- 文件名：kebab-case（前端），snake_case（Python）
- 组件命名：PascalCase；变量/函数：camelCase；常量：UPPER_SNAKE_CASE
- TypeScript 禁止 `any`，Python 函数必须有类型注解

---

## 工作流程

1. **先读再写**：修改前先读取相关文件，理解现有代码结构
2. **小步提交**：完成一个功能点即可提交，commit message 遵循 Conventional Commits
3. **测试先行**：写代码同时补充对应测试
4. **路径操作**：优先使用 `--prefix`、`-C`、`--workdir` 参数
5. **工具优先**：优先使用 `.claude/skills/` 和 `.claude/agents/` 中的工具

---

## 全栈开发规范

### 前端

- React/Vue + TypeScript，禁止 `any`
- CSS Modules 或 Tailwind，避免全局样式污染
- 组件拆分：单文件不超过 300 行
- 性能：图片懒加载、代码分割、虚拟滚动（列表 > 500 项）

### 后端

- RESTful API 统一响应格式：`{ "code": 0, "msg": "ok", "data": {} }`
- 参数化查询，禁止拼接 SQL
- JWT 鉴权中间件统一处理
- 所有异步必须 try/catch，禁止裸 await

### 数据库

- 查询走索引，禁止 `SELECT *`
- Migration 脚本必须可回滚
- 敏感字段加密存储

---

## 工具库维护

**定期搜索并更新开发工具，保持工具链最新。**

- 新发现的实用工具添加到 `~/.claude/skills/`
- 通过 `~/.claude/scripts/sync-tools.ps1` 同步到所有编辑器（Cursor/Trae/Qoder/Windsurf）
- 优先使用本地工具库中的方案，避免重复造轮子
- 工具描述、文档、README 统一使用中文（代码除外）
- 开发中遇到的好用工具和经验教训 → 记录到 `~/.claude/experiences/`
- 定期运行 `~/.claude/scripts/update-toolbox.ps1` 检查工具缺失和更新
- 搜索 GitHub/npm/PyPI 热门仓库时，评估安全性和实用性后再引入

---

## Git 规范

```
commit message 格式：<type>(<scope>): <描述>
type: feat | fix | refactor | perf | test | docs | chore | ci
```

**绝对不要**在未经确认的情况下执行：

- `git push origin main/master`
- `git push --force` 或 `git push -f`
- `git branch -D`
- `git push origin --delete`

---

## Windows 环境规范

```bash
# 检查服务
sc query Redis
Get-Service -Name redis

# 检查端口
netstat -ano | findstr :3000
Get-NetTCPConnection -LocalPort 3000

# 检查进程
Get-Process node
tasklist | findstr node

# 启停服务
net start Redis
net stop Redis

# 检查路径
Test-Path D:/apdms/frontend
Get-ChildItem D:/apdms/backend
```

---

## 错误处理

- 先分析根本原因，不修表面症状
- 修复后说明：问题原因 + 修复方式 + 如何避免
- 同一方法失败不超过 2 次，换思路
- EPERM 权限错误先检查文件是否被进程占用

---

## 输出格式

- 沟通语言：中文
- 代码块必须标注语言类型
- 较长步骤用编号列表
- 重要警告用 ⚠️ 标注
- 成功完成用 ✅ 确认

---

## 经验积累

**开发过程中不断总结，持续改进。**

- 遇到的坑和解决方案 → 简要记录到 `~/.claude/experiences/`
- 发现的高效工具/库 → 评估后添加到 skills
- 项目完成后 → 自动生成经验总结
- 定期回顾经验库，避免重复踩坑
