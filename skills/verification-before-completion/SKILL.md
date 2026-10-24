---
name: verification-before-completion
description: ★强制执行★ 完成前验证 + 独立审查门：无观察证据不声称完成，无独立审查 PASS 不算完成
triggers: [完成, 声称完成, 验证, check, 确认完成, done, 修好了, 测试通过]
layer: skeleton
disable-model-invocation: true
loading_tier: L2
source: obra/superpowers
---

# 完成前验证 + 独立审查门

> **L2 门控**：④验证阶段 Read 全文。本文件 = 审查政策 SSOT；数字/维度/路由/完成定义 → `config/workflow.yaml`（下方派生块）。升档触发 → `skills/task-triage/SKILL.md`。机械门 → `hooks/stop-verification-gate.py` + `hooks/_lib/r20_replay.py`。

## 完成定义

<!-- spine:completion -->
**完成定义**（派生自 config/workflow.yaml，改配置后 `python scripts/workflow.py render`，勿手改）：没有独立审查 PASS ⇒ 任务未完成；适用全部轨道（simple, bug, non_simple, research），简单/只读/文档任务同样适用。

- verify_tier 清单全部附观察到的命令输出
- 本轮全新独立审查者（非实现者、未 resume）给出 PASS，七维齐全，且 review.pass_requires 两道门（符合预期要求 + 原功能保持）均附证据通过
- **PASS = 两道门同时满足**（任一不满足即 NEEDS-CHANGES）：
  1. **符合预期要求**：每项改动都对应原始要求 / 验收标准；逐条无遗漏；无破坏要求的范围外改动（满足 + 遗漏 + 错改 维）。证据：原始要求逐条 → 对应改动或明确的反驳/弃权理由。
  2. **原功能保持**：起点 tip 上既有的预期行为全部保持，无静默回归；有意的行为变更逐条显式列出并对应原始要求（原功能 维）。证据：相关测试 / validate / check 脚本的观察输出 + 相对起点 tip 的行为差异说明。
- 一轮 = 改 → 验 → 刷图 → 并行全新审查（一次找齐）；目标第 1 轮 PASS，上限 **3** 轮。
- 3 轮仍未 PASS ⇒ **BLOCKED**（未完成），不得声称完成，也不得改为「跳过审查」。
- 自检、实现者自签、验证命令全绿都不能替代独立审查；仅用户显式豁免时放行，状态记 `DONE_WITH_CONCERNS`。
<!-- /spine:completion -->

适用范围：任何将声称完成或产生交付物的工作——代码、配置、**文档**、调研结论、计划/规格、架构建议。唯一不进入完成态的是：计划未批准 / 仅 `*.plan.md` / 纯澄清问答（这不是免审旁路，而是还没到完成）。

## verify_tier

| 档 | 何时 | 必须项 |
| --- | --- | --- |
| **比例** | 初判简单且 attempt=1 且未持续处理 | 构建/类型/Lint（适用项）+ 功能核验 + 关联文件；贴命令输出 |
| **全量** | 非简单；或持续处理；或已升档 | 比例全部 + 交叉验证（反向构造失败场景、需求回溯、同类遗漏扫描、MANIFEST 一致性）+ 残留引用 = 0 |

证据只认**观察输出**（命令 stdout/stderr、测试结果、文件内容），不认叙述。

## 必做核对（两档同强制）

- 修改文件已重读确认生效；无调试残留
- 改名/删除/移动/改签名：Grep 旧名 → 0；行为变更：逐个消费者走查
- 非功能变更（重构/格式/配置/重命名/文档）：跑既有测试或冒烟，写入「原功能」证据
- 配置/修改与文档、注释、INDEX、MANIFEST、版本戳同步；不一致 = 未完成（计入「漏改」）
- 安全：无硬编码密钥；边界输入已校验

## 独立审查

**一轮** = 改 → 验 → **刷图** → 并行全新审查（一次找齐）。目标第 1 轮 PASS。

- **全新**：新开 `Task`，禁止 `resume`；对照原始要求 + 当前 diff + 本轮新鲜图谱全量重扫，上轮清单不得限定范围；审查者只读；修改只走 `change-implementer`；禁止边审边改。
- **审查前刷图**：`last_edit` 之后增量刷新双图（`graph_freshness` `refresh_incremental`），`last_pre_review_graph_ts > last_edit_ts` 才能派审；SessionStart ensure / Stop refresh 不算；失败禁止开审。同轮并行审查者共享这一次刷新。
- **路由**：`rules/AGENTS.md`（必派 eng-reviewer）。无依赖审查者同一消息并行。
- **派发 prompt 必带**：原始要求原文；起点 tip 与变更清单；主会话已观察到的验证输出原文（测试 / validate / check）及相对起点的行为差异（审查者多为只读工具，须凭此核对「原功能保持」）；本轮已刷新；CRG `get_impact_radius` / `get_review_context`（有图）+ `codegraph_explore` blast-radius；按七维输出。
- **整轮判定**：任一审查者 `NEEDS-CHANGES` / 七维缺项 / 「PASS 但列必须修项」→ 整轮不通过 → 汇总完整清单派一次 `change-implementer` 集中改齐 → 验证 → 刷图 → 全新开审。
- **干净 PASS**（全部审查者 PASS、七维有效、与验证证据一致）→ 任务完成，不再派审。
- **轮次用尽仍未 PASS** → `BLOCKED`：向用户报告剩余问题与证据；不得声称完成，不得改记「跳过审查」。

### 七维（独立审查与主会话 R20 同一清单）

<!-- spine:dimensions -->
> 派生自 config/workflow.yaml，改配置后 `python scripts/workflow.py render`，勿手改。缺任一项视为本轮无效、不计 PASS。

1. 满足（承认/反驳/弃权 + 证据）
2. 遗漏（原始要求逐条对照）
3. 错改（改了不该改的）
4. 漏改（含文档/注释/版本戳/派生块，或「无文档影响」）
5. 原功能（相对起点 tip 保持 + 测试/validate/冒烟观察输出；有意行为变更逐条列出）
6. 影响范围（CRG get_impact_radius / IMPACT / blast-radius）
7. **问题是否解决**（已解决 | 未解决 | 部分解决 + 观察证据，禁止「看起来好了」）
<!-- /spine:dimensions -->

```
## 独立审查 / 会话终验（R20）
原始要求：<逐条关键词，禁止复述实现>
- 满足：<各点承认/反驳/弃权>
- 遗漏：无
- 错改：无
- 漏改：无文档影响 | 已同步 <paths>
- 原功能：保持（证据：<命令>）
- 影响范围：CRG / IMPACT / blast-radius
- 问题是否解决：已解决（证据：命令输出原文）
- 符合预期要求：通过（证据：原始要求逐条 → 对应改动）
- 原功能保持：通过（证据：测试/validate/check 观察输出 + 相对起点的行为差异）
结论：PASS   （主会话终验状态：DONE 仅当独立审查 PASS；否则 BLOCKED。不通过时结论写 NEEDS-CHANGES，两道门写「不通过」+ 证据。禁止照抄「通过 | 不通过」或尖括号槽。）
```

Stop 硬门（`r20_replay.py`）要求：含 `会话终验` 或 `R20`，且同时含 `遗漏`、`错改`、`漏改`、`原功能`、`影响范围`、`问题是否解决`；「满足」非空且每个需求指纹关键词须承认/反驳/弃权；「漏改」含 `文档`/`注释`/`无文档影响`/路径；「原功能」含 `证据`/`测试`/`冒烟`；「影响范围」含 `CRG`/`get_impact_radius`/`IMPACT`/`blast-radius`/`影响面`；「问题是否解决」含三态之一与观察证据。审查者 PASS 另须两道门行（`review_bars_ok`）：「符合预期要求」「原功能保持」各一行、以「通过」开头、同一行写非空真实证据；`证据：<…>` / 尖括号槽 / 空证据 / 「基本通过」都不算。DSH / OpenCode 用便携 `r20_check.py`。

## 质量门（`config/quality_gates.json`，Stop 门消费）

Schema Drift（ORM 变更缺 migration）· Security Anchor（auth 变更绑定威胁模型）· Scope Reduction（活跃 plan/spec 须对照 tasks）· Impact Manifest（脏集 − 基线 ⊆ 声明清单）。

## 失败与升级

- 验证失败 → 不声称完成；同方案 ≤2 次（R5），再失败换方案或 NEEDS_CONTEXT。
- 初判简单但继续处理 → `verify_tier=全量` + 执行升档非简单（task-triage）。
- Claude Stop 达 `max_blocks` 或审查轮次用尽 → 放行停机，状态 = `BLOCKED`（未完成）。通知写到 stdout（`systemMessage` + `additionalContext`），不只 stderr。Cursor Stop 不能阻断，同一状态经 `user_message`/`agent_message` 露出。
- 用户显式说出 `skip_keywords` 才可豁免审查，状态记 `DONE_WITH_CONCERNS`，不是 DONE。否定句（「不要跳过验证」「don't skip verify」）不是豁免。

## 输出

通过 → 验证报告（verify_tier + 命令输出）+ 独立审查结论 + 已修改文件。未通过 → 失败项 + 下一步，**不声称完成**。
