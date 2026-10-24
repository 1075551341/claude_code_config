# 推荐开发流程（v13：模型无关 · 一次通过 · 独立审查门）

> 唯一调度面：`config/workflow.yaml`。本文件中 `<!-- spine:* -->` 块由 `python scripts/workflow.py render` 生成，勿手改；其余为说明。

## 1. 本包管什么、不管什么

| 管（写在 `config/workflow.yaml`） | 不管（由调用方决定） |
| --- | --- |
| 阶段、进入/退出门、轨道 | 用哪个模型（会话 `/model`、`settings.json`、编辑器模型选择器、Task 传参） |
| 完成定义：独立审查 PASS 才算完成 | 推理强度 / effort / thinking（被调用模型自身的设置） |
| 审查路由、七维、轮次上限 | 子 Agent 用哪个模型（不传 = 继承会话） |
| 就绪定义与交审自检 | 上下文窗口大小（模型名后缀 `[1M]`、`autoCompactWindow` 或本机登记表） |

`python scripts/workflow.py check` 做三件事：校验配置（每条轨道都含 ④验证、完成定义覆盖全部轨道、轮次 ≤3、七维与 `hooks/_lib/r20_replay.py` 一致、无孤儿 agent）、检测派生块漂移、跑 **model-agnostic lint**（全仓命中模型 ID / 厂商档位别名 / effort 键，或 agents/commands/skills（含 catalog）frontmatter 带 `model:`/`effort:` 即失败；豁免：CHANGELOG、docs/archive|research|ADR、plugins/、hooks/tests/、scripts/workflow.py 自身）。`validate_config.py` V21 调用它。

### 用户如何选模型

- **Claude Code**：`/model`，或 `settings.json` 的 `model`（网关/第三方后端用其自身的环境变量）。agent 没有 `model:` 键，自动继承。
- **Cursor**：编辑器模型选择器；派发 `Task` 时可传 `model`，不传即继承。
- **跨模型审查**：调用方给 `cross-model-reviewer` 选一个与实现者不同的模型；选不出就不派。
- **推理强度**：只在模型自身的设置里调（会话/编辑器），本包不写。

## 2. 阶段、轨道与完成定义

<!-- spine:flow -->
| 阶段 | 命令 | skill | 角色 | 退出门 |
| --- | --- | --- | --- | --- |
| ⓪分类 | — | task-triage | session | 输出分类契约：大类 \| 需改文件 \| verify_tier \| 置信度 \| 成功标准 |
| ⓑ根因 | — | systematic-debugging | session | 根因证据一行（失败日志 / 断点 / 最小复现）；修复点与回归验证命令写入影响清单 |
| ⓡ调研 | — | deep-research | session | 关键结论 ≥2 个独立来源交叉验证，标注时效与可信度 |
| ①规划 | /discuss | brainstorming | session | grill ≤5 问收敛，验收标准可量化；HARD-GATE：用户批准设计 |
| ②规格 | /plan | writing-plans | planner | spec-validation 通过，无静默缩 scope；就绪定义（quality.definition_of_ready）全部满足 |
| ③执行 | /execute | executing-plans | change-implementer | 清单内文件一次改齐（含文档/注释/INDEX/版本戳）；构建/类型/Lint 通过；R16 无静默吞异常；交审前自检（quality.self_check）通过 |
| ④验证 | /verify | verification-before-completion | session | verify_tier 对应清单全部附命令证据；审查前刷图（last_edit 之后）；本轮全新独立审查全部 PASS（completion + review.routing） |
| ⑤学习 | /compact | memory-compression | session | claude-mem 记录模式/决策（R18） |
| ⓢ交付 | /ship | ship | session | 用户要求的交付物完成（commit / PR / 发布），CI 绿 |

- **simple**：⓪分类 → ③执行 → ④验证
- **bug**：⓪分类 → ⓑ根因 → ③执行 → ④验证
- **non_simple**：⓪分类 → ①规划 → ②规格 → ③执行 → ④验证 → ⑤学习
- **research**：⓪分类 → ⓡ调研 → ④验证
- **按需**：ⓢ交付（不在轨道内；任务完成且用户明确要求时进入，R19）
- **模型 / effort**：不在本包配置；由调用方（会话、settings、编辑器、Task 传参）决定，agent 一律继承。

**完成定义**（派生自 config/workflow.yaml，改配置后 `python scripts/workflow.py render`，勿手改）：没有独立审查 PASS ⇒ 任务未完成；适用全部轨道（simple, bug, non_simple, research），简单/只读/文档任务同样适用。

- verify_tier 清单全部附观察到的命令输出
- 本轮全新独立审查者（非实现者、未 resume）给出 PASS，七维齐全，且 review.pass_requires 两道门（符合预期要求 + 原功能保持）均附证据通过
- **PASS = 两道门同时满足**（任一不满足即 NEEDS-CHANGES）：
  1. **符合预期要求**：每项改动都对应原始要求 / 验收标准；逐条无遗漏；无破坏要求的范围外改动（满足 + 遗漏 + 错改 维）。证据：原始要求逐条 → 对应改动或明确的反驳/弃权理由。
  2. **原功能保持**：起点 tip 上既有的预期行为全部保持，无静默回归；有意的行为变更逐条显式列出并对应原始要求（原功能 维）。证据：相关测试 / validate / check 脚本的观察输出 + 相对起点 tip 的行为差异说明。
- 一轮 = 改 → 验 → 刷图 → 并行全新审查（一次找齐）；目标第 1 轮 PASS，上限 **3** 轮。
- 3 轮仍未 PASS ⇒ **BLOCKED**（未完成），不得声称完成，也不得改为「跳过审查」。
- 自检、实现者自签、验证命令全绿都不能替代独立审查；仅用户显式豁免时放行，状态记 `DONE_WITH_CONCERNS`。
<!-- /spine:flow -->

## 3. 一次通过，独立审查兜底

预期路径是第 1 轮审查就 PASS。返工通常来自三处：验收标准不清、影响清单漏项（文档/INDEX/版本戳）、审查清单与自检清单不一致。v13 在开工前和交审前堵住这三处：

1. **就绪定义**（`quality.definition_of_ready`）：③执行前必须有可验证的验收标准、完整影响清单、预选验证命令、预选审查者。渲染进 `planner` 与 `change-implementer`。
2. **交审前自检**（`quality.self_check`）：修改者用与审查者 **同一份** 七维逐条自检。自检通过 ≠ 完成。
3. **同源审查契约**：审查者契约块与 verification skill 七维都从 `review.dimensions` 渲染；hooks 机械门（`r20_replay.py`）由 V21 对齐校验。

**轮次**：一轮 = 改 → 验 → 刷图 → 并行全新审查（一次找齐）。上限 `review.max_rounds`（默认 3，校验器不允许超过 3）。第 3 轮仍未 PASS ⇒ 状态 **BLOCKED**：任务未完成，向用户报告剩余问题；不得降级为「跳过审查」或「完成但有顾虑」。唯一放行是用户显式豁免（`skip_keywords`），状态记 `DONE_WITH_CONCERNS`，仍不是 DONE。

**机械门 vs 规则门**：Claude Code Stop hook 在有交付编辑时强制本流程（最多阻断 `max_blocks` 次防死循环，放行时打印 BLOCKED 状态）；无编辑的任务（调研/问答交付物）与 Cursor（Stop 不能阻断）由规则强制：同样要独立审查交付物，PASS 才能声称完成。

## 4. 派生清单

<!-- spine:derived -->
| 目标 | 内容（来源节） |
| --- | --- |
| agents/*.md frontmatter | 无 `model` / `effort` 键（render 剥离，lint 拦截） |
| 审查者 agents `spine:review-contract` | 七维 + 结论 + 只读规则（review） |
| change-implementer / planner `spine:ready-contract` | 就绪定义 + 交审自检（quality） |
| commands/{discuss,plan,execute,verify,ship,compact}.md `spine:stage-gate` | 阶段门；verify 含完成定义 |
| CLAUDE.md / docs/DEV_FLOW.md `spine:flow` | 阶段表 + 轨道 + 完成定义 |
| rules/AGENTS.md `spine:review-routing` | 审查路由（review.routing） |
| skills/verification-before-completion `spine:dimensions` / `spine:completion` | 七维 + 完成定义 |
| templates/cursor-guard/rules/CURSOR-EDITOR.mdc `spine:completion` | Cursor 完成定义 |
| config/quality_gates.json verification_gate | 轮次 / 阻断 / 最少文件 / 审查者 / 刷图 / 完成状态 |
| templates/cursor-guard/guard-config.json verification.reviewer_agents | Cursor 审查者名单 |
| templates/editor-graph-hooks/verify-gate.ts | `review_max_rounds=<n>` 文案 |
<!-- /spine:derived -->

## 5. 从 v12 迁移

| v12 | v13 |
| --- | --- |
| `models` 多厂商 profiles、`roles` 档位 + effort、`triage` 档位 | 删除。模型与 effort 由调用方决定；agent frontmatter 不再有 `model` / `effort` |
| `workflow.py show --profile` / `apply-settings` / `templates/claude-settings/model.snippet.json` | 删除。`settings.json` 由用户自己管理 |
| `config/model-context-windows.json` 登记各厂商模型 | 出厂为空表；窗口来自模型名后缀、`autoCompactWindow` 或本机 `model-context-windows.local.json`（gitignore） |
| 审查上限 5 轮；用尽后 DONE_WITH_CONCERNS 放行 | 上限 3 轮；用尽 = BLOCKED（未完成）；每条轨道含审查门 |
| 16 agents / 35 skills / 12 rules / 18 commands | 9 / 26 / 6 / 14（去向见 CHANGELOG v13.0.0） |
| v12 跨模型审查者（名含厂商） | `cross-model-reviewer`（去厂商化） |
| `review.legacy_reviewer_names`：hooks 仍把旧名子代理（v12 前 code-reviewer、v12 跨模型审查者）计为审查者 | 删除：只认现行 7 个审查者名；旧名子代理的输出不再计入独立审查 |

已部署用户：

1. `git pull` → `python scripts/workflow.py check`。
2. 若 v12 `apply-settings --write` 曾写入 `settings.json`：按需删除其中的推理强度键与模型别名重定向环境变量，自己选会话模型。
3. 若 `settings.json` 的 `autoCompactWindow` 之前依赖登记表：保持现值即可（未知模型时以显式值为准），或在模型名后加 `[1M]` 等后缀。
4. `pwsh -File scripts/sync.ps1 -All`（Cursor 侧再跑 `deploy-cursor-guard.ps1`）。
