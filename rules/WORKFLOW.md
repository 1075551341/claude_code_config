---
name: workflow
description: 阶段式工作流规则，定义从讨论到发布的完整开发生命周期
alwaysApply: false
layer: supplement
source: open-gsd/get-shit-done-redux + bytedance/deer-flow + obra/superpowers + garrytan/gstack
triggers:
  - 工作流
  - 阶段式开发
  - GSD
  - phase workflow
---

# 工作流规则

## 阶段定义

> **计划唯一入口**：skill/writing-plans + /plan（禁用 hook/pre-task-planner）
> **骨架内容已迁至 `rules/CORE.md`**：五阶段流程、状态机、门控。

### 1. Discuss 阶段
- 目标：明确需求、识别约束、对齐期望
- 产出：需求文档、验收标准、技术约束清单
- 门控：需求无歧义、验收标准可量化

### 2. Plan 阶段
- 目标：设计实现方案、分解任务、识别依赖
- 产出：实施计划、任务分解、依赖图
- 门控：方案经过头脑风暴评估、任务有明确成功标准

### 3. Execute 阶段
- 目标：按计划实现、遵循简洁优先和安全默认
- 产出：代码变更、测试用例
- 门控：每个子任务独立验证通过、遵循 R10+R11

### 4. Verify 阶段
- 目标：交叉验证、质量门检查、回归测试
- 产出：验证报告、问题清单
- 门控：交叉验证清单全部通过、质量门无告警

### 5. Ship 阶段
- 目标：合并、部署、监控
- 产出：合并PR、部署记录
- 门控：CI通过、无回滚风险

### 6. Learn 阶段（gstack /learn）
> **来源**: garrytan/gstack | 跨会话学习管理

- 目标：提取可复用模式，跨会话积累项目知识
- 产出：`experiences/patterns/` + `experiences/rejected/`
- `/learn`：查看/搜索/修剪跨会话学习内容
- 与 claude-mem 互补：/learn 管项目级经验，claude-mem 管会话级记忆
- 学习内容：项目特定模式、陷阱、偏好决策

## 质量门

| 门 | 检查项 | 阻断条件 |
|----|--------|---------|
| Schema Drift | ORM变更缺migration | 阻断 |
| Security Anchor | 验证绑定威胁模型 | 阻断 |
| Scope Reduction | planner静默丢弃需求 | 警告 |

## 上下文腐烂治理

> **三级阈值已迁至 `rules/CORE.md`**。此处保留预防措施。

## 最小可工作切片

- 每阶段产出最小可工作增量
- 每阶段可独立合并，降低大PR的review难度
- 优先交付最高价值切片

## 命令规范（来自 get-shit-done）

| 命令 | 阶段 | 作用 |
|------|------|------|
| `/discuss` | Discuss | 明确需求、识别约束、对齐期望 |
| `/plan` | Plan | 设计实现方案、分解任务、识别依赖 |
| `/execute` | Execute | 按计划实现、遵循简洁优先和安全默认 |
| `/verify` | Verify | 交叉验证、质量门检查、回归测试 |
| `/ship` | Ship | 合并、部署、监控 |
| `/compact` | 全局 | 战略压缩：在逻辑断点主动压缩上下文 |
| `/status` | 全局 | 查看当前工作流状态和进度 |

## Phase 工作流（来自 get-shit-done）

```
Phase 1: Minimum Viable — 最小可工作切片
Phase 2: Core Experience — 完整快乐路径
Phase 3: Edge Cases — 错误处理、边界情况、打磨
Phase 4: Optimization — 性能、监控
```

## 上下文腐烂预防

- 长任务（>30分钟）拆分为独立子Agent
- 每完成一个子目标输出状态摘要
- 遵循三级阈值：<40% 正常 / 50% compact / 70% 强制压缩
- 工作流切换时保存/恢复规划上下文

## 子Agent编排（deer-flow 2.0 + ruflo）

> **deer-flow 2.0**: bytedance/deer-flow | LangGraph-based ground-up rewrite | Python 73.5%
> **执行模式**: flash（快速）/ standard（标准）/ pro（planning）/ ultra（sub-agents 并行 fan-out）
> **桥接**: claude-to-deerflow skill (`npx skills add`) | 环境变量 `DEERFLOW_URL` 自定义端点
> **状态机** (→ `rules/CORE.md`): DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED

### 编排四阶段 (DAG)

```
Phase 1: 拆解 → 识别独立子目标 + 依赖关系 → DAG 任务图
Phase 2: 调度 → 无依赖并行派发 | 有依赖等待前置完成 | fresh context
Phase 3: 整合 → 收集结果 → 冲突检测 → 合并
Phase 4: 验证 → 子目标独立验证 + 整体集成验证
```

### ruflo 蜂群概念（不落地）

> **source**: ruvnet/ruflo v3.10.34 — 参考排除
> HNSW向量记忆(~1.9x快) + 3共识(Raft/Byzantine/Gossip) + 100+ agents 蜂群拓扑
> 适用于多机多团队协作。单用户场景由 agentic-orchestrator 覆盖。

### 无冲突原则 + 跨会话制品

- 子Agent边界清晰，不重叠执行范围；工具调用不相互覆盖
- 子Agent 结果写入三态制品；新会话优先加载制品
- 压缩前 `pre-compact-state` 保留决策与制品指针
