# Claude Code — 全局配置

> 版本：v1.0 | 更新：见 memory/index.md

## 快速导航

- 规范 → `rules/` | 角色 → `agents/` | Skill → `skills/`
- 记忆 → `memory/index.md` | 计划 → `docs/plans/`
- Spec → `openspec/` | 命令 → `/help`

---

## 工作规范

### 非简单任务必须先计划

| 触发条件 | 动作 |
|---------|------|
| 需求模糊 | `/brainstorm` → 设计文档 |
| 涉及 ≥3 文件修改 | `/spec` → delta spec，再 `/plan` |
| 架构/接口变更 | `/spec` + 架构师 agent 确认 |
| 简单 bug fix | 直接 `/fix` |

### 上下文管理（GSD 原则）
- 主会话只编排，实现交给子 agent
- 目标：主会话上下文 <40%
- 长任务中途 `/clear` 重置，从 memory/index.md 恢复

### 工具优先
1. 先查 `skills/` 有无匹配 skill → 调用
2. 先查 `agents/` 有无对应角色 → 路由
3. 都没有再自行处理

### 输出原则
- 言简意赅，无废话，无重复
- 代码修改聚焦变更，不重写无关部分
- 不确定时问，不猜测不假设

---

## Agent 路由

| 场景 | Agent |
|------|-------|
| 系统设计、架构选型 | `agents/architect.md` |
| 代码质量审查 | `agents/eng-reviewer.md` |
| 产品/业务决策 | `agents/ceo-reviewer.md` |
| UI/交互/视觉 | `agents/designer.md` |
| 测试、质量保证 | `agents/qa.md` |
| 报错、根因分析 | `agents/debugger.md` |
| 技术调研 | `agents/researcher.md` |
| 安全审计 | `agents/security.md` |

---

## 上下文加载规则

会话开始时自动加载：
```
@memory/index.md          # 项目记忆索引（始终加载）
```

按需加载（任务触发）：
```
@rules/01-core.md         # 所有任务
@rules/02-code.md         # 代码任务
@rules/04-testing.md      # 涉及测试
@agents/<role>.md         # 路由到对应 agent
@skills/<category>/<skill>.md  # 执行对应 skill
```

---

## 禁止事项

- 不在没有 spec/plan 的情况下修改核心逻辑
- 不忽略已有 skill 自己重新实现
- 不在一个会话里同时做设计、实现、审查（上下文污染）
- 不在代码里保留调试用 console.log / print
- 不跨 agent 职责边界主动执行
