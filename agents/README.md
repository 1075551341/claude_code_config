# Agents 智能体库

> **全局 8 个**薄编排 + **catalog/agents/** 领域库（38）

---

## 核心 8（全局）

| Agent | 预加载 skill | 职责 |
|-------|-------------|------|
| planner | writing-plans | 仅计划，不实现 |
| code-explorer | — | 只读探索 |
| code-reviewer | requesting/receiving-code-review | 审查不改代码 |
| build-error-resolver | systematic-debugging | 构建错误 |
| architect | brainstorming | 架构决策 |
| spec-reviewer | spec-validation | spec 审查 |
| context-manager | memory-compression, caveman-compress | 上下文/压缩 |
| agentic-orchestrator | subagent-driven-development | 多 Agent 并行 |

---

## 调用原则

1. 子 Agent **不继承**会话历史，只注入必要上下文
2. 同一模块 **单一负责**（MANIFEST.yaml 查 owner）
3. 无依赖任务 **并行**；失败隔离，不污染其他子目标

---

## Catalog（按需）

```powershell
python ~/.claude/scripts/migrate-from-legacy.py --project <path> --agent python-reviewer
```

示例：frontend-developer, security-reviewer, database-expert …

---

## 互斥

| 场景 | 用 | 不用 |
|------|-----|------|
| 写计划 | agent/planner + writing-plans | planning-expert, pre-task-planner |
| 并行编排 | agentic-orchestrator | planner 并行派发 |
| 跨会话记忆 | claude-mem plugin | context-manager 重复存储 |

---

## 来源

superpowers + ECC（cherry-pick）
