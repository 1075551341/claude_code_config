---
name: executing-plans
description: 计划执行技能，与writing-plans配对，按计划逐步执行任务
triggers:
  - 执行计划
  - 实施计划
  - 执行任务
  - 按计划执行
priority: P1
layer: supplement
source: obra/superpowers
disable-model-invocation: true
loading_tier: L2
---
# 计划执行

## 流程
1. 读取 writing-plans 生成的计划文档
2. 按依赖顺序执行每个任务
3. 每个任务完成后独立验证
4. 任务失败时隔离问题，不污染其他任务
5. 全部完成后：非简单任务先委派独立审查者（见下），再交叉验证 + 短 R20

## 非简单双审（修改→验证→审查，最多 3 轮）

一轮 = **修改** → **验证**（对照原始要求，贴观察输出）→ **独立审查全部修改**。
不合格则再开一轮，直到符合预期或满 3 轮。禁止只连审不改。

1. 执行者按批准设计改完并贴观察证据
2. `Task` `eng-reviewer`（fresh，只读）对照原始要求审全部 diff + IMPACT/blast，结论 `PASS` 或 `NEEDS-CHANGES`（列出未满足项）
3. `PASS` → 主会话输出短 R20 后才可声称完成
4. `NEEDS-CHANGES` → 执行者按未满足项**修改并验证**（同方案 ≤R5），再开一轮新审查（计数 +1）
5. 满 3 轮仍不符合预期 → `BLOCKED` / `DONE_WITH_CONCERNS`，禁止第 4 轮、禁止空转
6. 计划未批准 / CreatePlan 等待用户 → 禁止启动审查或完成门 followup

简单任务不走本循环。

## 原则
- 遵循 R10 简洁优先 + R11 安全默认
- 每个子任务有明确成功标准
- 无依赖的子任务可并行
- 执行过程中发现计划缺陷，返回 plan 阶段修正

## 进度追踪（task-master 风格）

- Checkbox 可视化：`- [ ] 待办` / `- [x] 完成`
- 阶段进度：`Phase 1/3 — ██████░░░░ 60%`
- 依赖状态标记：`→ T2（pending）` / `✓ T2（completed）`
- 每完成一个任务输出进度更新
