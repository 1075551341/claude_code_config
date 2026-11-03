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
5. 全部完成后：有交付物编辑先走双审（修改者与审查者分角色；政策 → verification skill），再交叉验证 + 短 R20

## 双审（修改→验证→刷图→审查；角色分离）

> 政策 SSOT → `skills/verification-before-completion/SKILL.md`。轮次 → `config/workflow.yaml` `review.max_rounds`。

一轮 = **修改** → **验证**（贴观察输出）→ **审查前增量刷图** → **独立七维审查**。

**角色（禁止混用）**：
- **修改** → `Task` `change-implementer`（fresh）。Cursor 无该 `subagent_type` 时用 `generalPurpose`，prompt 必须声明「你是修改者，禁止审查」。禁止审查者改文件。
- **审查** → `Task` `eng-reviewer`（及 AGENTS.md 并行路由）。**每轮全新开审**，禁止 `resume`。只对照原始要求找问题；禁止改文件。上轮清单不得限定本轮范围。prompt 须含：本轮已刷新、CRG `get_impact_radius` / `get_review_context` + `codegraph_explore` blast-radius。
- **主会话**：编排 + 跑验证命令 + R20；不在审查回合自己改代码。

**提前结束**：独立审查干净 `PASS`（七维齐全、无必须修项）且与验证结论一致 → **立即结束**。
**再开一轮**：审查给出完整未满足清单后，派**一次** `change-implementer` 集中改齐。改完再验证后全新派审。满 `review.max_rounds` 仍未 PASS → `BLOCKED`（未完成）；只有用户显式豁免才记 `DONE_WITH_CONCERNS`。禁止边审边改、禁止只连审不改。

计划未批准 / 仅计划文件 / 纯澄清问答（无交付）→ 不进入完成态，不走本循环。

1. `change-implementer` 按批准设计改完（含文档/注释同步）；主会话贴观察证据
2. 审查前增量刷新双图；再派本批审查者（七维一次找齐）
3. 干净 `PASS` → 主会话输出短 R20；**禁止再派审查**
4. `NEEDS-CHANGES` / 七维缺项 → 一次 `change-implementer` 集中改齐；再验证后全新开审
5. 计划未批准 / CreatePlan 等待用户 → 禁止启动审查或声称完成

## 原则
- 遵循 R11 安全默认；最小改动集（CORE 开发习惯）
- 每个子任务有明确成功标准
- 执行过程中发现计划缺陷，返回 plan 阶段修正

<!-- spine:concurrency -->
**执行并发**（派生自 config/workflow.yaml，改配置后 `python scripts/workflow.py render`，勿手改）：无依赖且可后台的命令/操作不得阻塞会话，优先并行。有依赖或下一步需要其输出的仍按序、禁止后台。长驻服务器 / watcher 保持后台。不是第三道 PASS 门，不另建 Stop hook，不改 `browser_ui_tests`。

- 无依赖且可后台的命令/操作不得阻塞会话，优先并行
- 有依赖或下一步需要其输出的步骤仍按序执行，禁止后台
- 长驻服务器 / watcher 保持后台
<!-- /spine:concurrency -->

## 进度追踪（task-master 风格）

- Checkbox 可视化：`- [ ] 待办` / `- [x] 完成`
- 阶段进度：`Phase 1/3 — ██████░░░░ 60%`
- 依赖状态标记：`→ T2（pending）` / `✓ T2（completed）`
- 每完成一个任务输出进度更新
