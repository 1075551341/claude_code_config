# Skills 索引

> 源：`skills/` | 分级来自 MANIFEST loading_tiers | v13.0.4（26 全量 = L1×4 + L2×5 + L3×17；流程/审查 SSOT → `config/workflow.yaml`；本包不绑定模型与推理强度；catalog 变体见 `catalog/INDEX.md`）

## L1 — 会话常驻 (4)

- [using-superpowers](skills/using-superpowers/SKILL.md) — 技能发现与 Tool-First 路由
- [change-impact-analysis](skills/change-impact-analysis/SKILL.md) — 变更影响分析，改前必执行
- [brainstorming](skills/brainstorming/SKILL.md) — HARD-GATE 方案设计（非简单任务必加载）
- [task-triage](skills/task-triage/SKILL.md) — 分类 SSOT：Phase0 盘点；简单=关联需改≤2+白名单+五维全低+attempt=1；简单不豁免独立审查

## L2 — 阶段门控 (5)

| 阶段  | Skill                                                                            | 触发               |
| ----- | -------------------------------------------------------------------------------- | ------------------ |
| 2规格 | [writing-plans](skills/writing-plans/SKILL.md)                                   | 原子级实施计划     |
| 2规格 | [spec-validation](skills/spec-validation/SKILL.md)                               | spec可验证验收标准 |
| 3执行 | [executing-plans](skills/executing-plans/SKILL.md)                               | 按计划逐步执行     |
| 3调试 | [systematic-debugging](skills/systematic-debugging/SKILL.md)                     | 根因分析（含原 triage 分级） |
| 4验证 | [verification-before-completion](skills/verification-before-completion/SKILL.md) | 验证 + 独立审查（两道关）+ 完成定义 |

## L3 — 信号触发 (17)

### 显式触发工作流（仅用户明确要求时启用）

- [test-driven-development](skills/test-driven-development/SKILL.md) — RED-GREEN-REFACTOR
- [subagent-driven-development](skills/subagent-driven-development/SKILL.md) — 子Agent派发 + 两阶段审查

### 调研与决策

- [deep-research](skills/deep-research/SKILL.md) — 深度调研（Firecrawl+Exa+交叉验证）
- [adr-management](skills/adr-management/SKILL.md) — 架构决策记录管理

### 审查（薄壳，覆盖上游同名技能 → verification-before-completion）

- [requesting-code-review](skills/requesting-code-review/SKILL.md) — 薄壳 → 独立审查契约
- [receiving-code-review](skills/receiving-code-review/SKILL.md) — 薄壳 → 集中改齐流程

### 设计与UI

- [design-pipeline](skills/design-pipeline/SKILL.md) — 设计管线（探索-对比板-HTML）

### 上下文与记忆

- [memory-compression](skills/memory-compression/SKILL.md) — 上下文压缩与跨会话记忆
- [claude-mem-maintenance](skills/claude-mem-maintenance/SKILL.md) — claude-mem 记忆维护
- [caveman-compress](skills/caveman-compress/SKILL.md) — 输出压缩（caveman模式）

### 技能治理

- [skill-creator](skills/skill-creator/SKILL.md) — 创建/更新有效技能指南
- [skill-reviewer](skills/skill-reviewer/SKILL.md) — skill 合规性审查

### 执行与编排

- [workstream-management](skills/workstream-management/SKILL.md) — 并行任务流管理（git worktree）
- [using-git-worktrees](skills/using-git-worktrees/SKILL.md) — Git Worktree 并行开发

### Git与发布

- [git-workflow](skills/git-workflow/SKILL.md) — Git 工作流
- [ship](skills/ship/SKILL.md) — 交付管线唯一正文（前置：独立审查 PASS）
- [finishing-a-development-branch](skills/finishing-a-development-branch/SKILL.md) — 薄壳 → ship（覆盖上游同名技能）

## v13 变更（原全局 → 去向）

| 原 skill | 去向 |
| --- | --- |
| karpathy-guidelines | 删除；四原则并入 `rules/CORE.md` 开发习惯 |
| triage | 删除；P0-P3 分级并入 `systematic-debugging` / `task-triage` |
| autoplan | 删除；审查路由 → `config/workflow.yaml` review.routing |
| structured-artifacts | 删除；制品约定 → `rules/CORE.md` R13 |
| improve-codebase-architecture / code-refactoring | 删除；行为保持靠 R20「原功能保持」审查关 |
| frontend-library-advisor / frontend-design-pattern-applier / test-edge-case-analyzer | 删除；领域知识按需 → `catalog/` |

> superpowers 同名技能为本地定制版或薄壳，**本地权威**；删除同名本地技能会让上游插件版生效，故审查/分支完成类保留薄壳。
