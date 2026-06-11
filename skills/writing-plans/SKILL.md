---
name: writing-plans
description: 编写原子级实施计划（2-5分钟/任务），含精确路径+代码+验证命令。与 executing-plans 配对。
triggers: [写计划, 实施计划, 任务分解, 项目规划, 原子任务]
layer: supplement
source: obra/superpowers
disable-model-invocation: true
loading_tier: L2
---

# 编写实施计划

## 核心原则

**原子任务** — 每个任务 2-5 分钟完成，子Agent 无需额外上下文即可执行。

## 规格三轨（互斥）

| 场景 | 路径 | 入口 |
|------|------|------|
| 功能变更/brownfield | `openspec/changes/<id>/` | `/propose` |
| 大功能多阶段 | `.planning/phases/` | `/plan` |
| ≤3文件小功能 | `spec/<project>/` | `/plan` |

## 原子任务模板

每个任务必须包含三个必填字段：

```markdown
### Task N: [名称] [P0/P1/P2]

**文件**: `src/path/to/file.ts` (精确路径)

**操作**: [具体到代码行的操作描述]

**验证**: `npm test -- path/to/test.ts` (可执行的验证命令)
```

## 计划结构

```markdown
# [功能名] 实施计划

## DAG 依赖图
[注：无依赖任务并行，有依赖串行，同制品路径禁止并行写入]

## Wave1: [波次名] (无依赖，并行)
- [ ] Task 1.1: [标题]
- [ ] Task 1.2: [标题]

## Wave2: [波次名] (依赖 Wave1)
- [ ] Task 2.1: [标题]
...

## 验收
- [ ] 标准1：可量化条件
- [ ] 标准2：可量化条件
```

## 反模式（禁止）

| 禁止 | 原因 |
|------|------|
| "实现用户认证" 作为单步 | 太大，应该拆分为 5+ 原子任务 |
| "改一下 auth 模块" | 无文件路径，子Agent 不知道从哪里下手 |
| "测试全部通过" 作为验证 | 不可执行，需指定测试文件或命令 |
| 占位符如 `TODO: fill later` | 原子任务不留空白 |
| 1-3天粒度的步骤 | 子Agent 无法独立执行 |

## 计划自审清单

- [ ] 每个任务 ≤5 分钟完成
- [ ] 每个任务有精确文件路径
- [ ] 每个任务有可执行验证命令
- [ ] 无占位符/TODO
- [ ] DAG 依赖图明确（无依赖 = 可并行）
- [ ] 覆盖完整功能范围，无遗漏
- [ ] 同一制品路径无并行写入冲突

## 执行握手

```
writing-plans 输出计划后:
├─ 选择一: 派发给 subagent-driven-development（推荐，复杂计划）
│   └─ 子Agent 按波次执行，两阶段审查
└─ 选择二: 内联执行（简单计划，≤3原子任务）
    └─ 主会话直接按顺序执行
```

## 示例

```markdown
# 用户登录 实施计划

## Wave1 (并行)
- [ ] Task 1.1: 创建 User model [P0]
  文件: `src/models/User.ts`
  操作: 定义 User 接口 + Mongoose schema (email, passwordHash, createdAt)
  验证: `npx ts-node -e "import User from './src/models/User'; console.log('OK')"`

- [ ] Task 1.2: 创建 auth middleware [P0]
  文件: `src/middleware/auth.ts`
  操作: JWT verify 中间件，解码后注入 req.userId
  验证: `npm test -- src/middleware/auth.test.ts`

## Wave2 (依赖 Wave1)
- [ ] Task 2.1: 实现 POST /login [P0]
  文件: `src/routes/auth.ts`
  操作: 接收 email+password，验证后返回 { token, user }
  验证: `curl -X POST localhost:3000/login -H 'Content-Type: application/json' -d '{"email":"test@test.com","password":"123456"}'`

## 验收
- [ ] 登录成功返回 JWT token
- [ ] 错误密码返回 401
- [ ] 不存在用户返回 401
```
