---
name: workflow
description: 五阶段工作流与 DAG 编排。触发：工作流、deer-flow、阶段编排。
triggers: [工作流, deer-flow, DAG, 阶段]
layer: supplement
source: local
loading_tier: L3
disable-model-invocation: true
---

# 工作流规则

## 阶段定义

> **计划唯一入口**：skill/writing-plans + /plan（禁用 hook/pre-task-planner）
> **五阶段骨架 SSOT → `CLAUDE.md`「五阶段流程」**（目标/产出/门控全量；v11.3.6 修正迁移指针并删除本文件重复骨架）。

### Learn 阶段扩展（gstack /learn）

- 跨会话学习：项目特定模式、陷阱、偏好决策 → claude-mem observations（R18；原 `experiences/` 文件体系已归档至 `docs/archive/experiences/`）
- `/learn`：查看/搜索/修剪跨会话学习内容

## 质量门

> 三门定义与阻断条件（名称见该节）SSOT → `skills/verification-before-completion/SKILL.md`「质量门」节（v11.3.6 收敛，消除「警告vs强制」漂移）。

## 上下文腐烂治理

> **三级阈值已迁至 `rules/CORE.md`**。此处保留预防措施。

## 最小可工作切片

- 每阶段产出最小可工作增量
- 每阶段可独立合并，降低大PR的review难度
- 优先交付最高价值切片

## 命令规范（来自 open-gsd/gsd-core，原 get-shit-done）

| 命令 | 阶段 | 作用 |
|------|------|------|
| `/discuss` | Discuss | 明确需求、识别约束、对齐期望 |
| `/plan` | Plan | 设计实现方案、分解任务、识别依赖 |
| `/execute` | Execute | 按计划实现、遵循简洁优先和安全默认 |
| `/verify` | Verify | 交叉验证、质量门检查、回归测试 |
| `/ship` | Ship | 合并、部署、监控 |
| `/compact` / `/summarize` | 全局 | 战略压缩：Claude Code 用 `/compact`；Cursor 用 `/summarize` 或「压缩上下文」 |
| `/status` | 全局 | 查看当前工作流状态和进度 |
| `/deer-flow` | 执行 | 委托 deer-flow 外部编排引擎（flash/standard/pro/ultra 四模式） |

## Phase 工作流（来自 open-gsd/gsd-core）

```
Phase 1: Minimum Viable — 最小可工作切片
Phase 2: Core Experience — 完整快乐路径
Phase 3: Edge Cases — 错误处理、边界情况、打磨
Phase 4: Optimization — 性能、监控
```

## 上下文腐烂预防

> 三级阈值 → `rules/CORE.md`（唯一 SSOT）。

- 长任务（>30分钟）拆分为独立子Agent
- 每完成一个子目标输出状态摘要
- 工作流切换时保存/恢复规划上下文

## 子Agent编排（deer-flow 2.0 + DAG 四阶段）

> **deer-flow 2.0**: bytedance/deer-flow | LangGraph-based ground-up rewrite | Python 73.5%
> **执行模式**: flash（快速）/ standard（标准）/ pro（planning）/ ultra（sub-agents 并行 fan-out）
> **桥接**: `skills/claude-to-deerflow`（v12 由 catalog 迁入，低频 disable-model-invocation）| 环境变量 `DEERFLOW_URL` 自定义端点
> **状态机** (→ `rules/CORE.md`): DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED

### DAG 依赖图规则

```
无依赖子目标 → 并行派发（同一批次内共享三态制品快照）
有依赖子目标 → 等待前置完成 + 制品写入后派发
冲突检测：同一制品路径禁止并行写入
```

### 编排四阶段

```
Phase 1: 拆解 → 识别独立子目标 + 依赖关系 → DAG 任务图
Phase 2: 调度 → 无依赖并行派发 | 有依赖等待前置完成 | fresh context
Phase 3: 整合 → 收集结果 → 冲突检测 → 合并
Phase 4: 验证 → 子目标独立验证 + 整体集成验证
```

### 变更影响分析三阶段（强制执行）

> 门控与触发条件 → `rules/CORE.md`；三阶段详情 → `skills/governance/SKILL.md`。

### 无冲突原则 + 跨会话制品

- 子Agent边界清晰，不重叠执行范围；工具调用不相互覆盖
- 子Agent 结果写入三态制品；新会话优先加载制品
- 压缩前 `pre-compact-state` 保留决策与制品指针
