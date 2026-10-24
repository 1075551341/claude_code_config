---
description: Claude 配置总纲 — 路由 + 工作流主干 + 完成定义（多端 L0 必加载）
alwaysApply: true
layer: router
---

# Claude 全局配置

> **v13.0.1** — 模型无关 · 一次通过 · 独立审查门。主干 `config/workflow.yaml` | 铁律 `rules/CORE.md` | 归属 `MANIFEST.yaml` | 法典 `SPEC.md` | 史 `CHANGELOG.md`

**五柱**：Superpowers v6.3.0(方法论) | GSD(上下文) | OpenSpec(规格) | gstack(审查) | claude-mem v13.13.1(记忆，钉扎 <13.14)
**三横切**：L1 ECC+deer-flow | L2 RTK+caveman+阈值 | L3 codegraph+Firecrawl/Exa（codebase-memory 已禁用）

## 优先级与入口

```
用户显式指令 > CLAUDE.md > 激活skill > lazy规则 > alwaysApply > 默认
工具路由: codegraph →（双图就绪后）Grep；本机文件名 → everything | 为什么/偏好 → claude-mem（R17-R18）
```

任务入口：疑似重复 → `claude-mem search`（R18）→ Read `skills/task-triage/SKILL.md`（Phase0 + 分类契约）→ 按轨道走。按需 Read：`skills-INDEX.md` | `agents-INDEX.md` | `rules-INDEX.md`。

| 必读 skill（P0） | 何时 |
| --- | --- |
| using-superpowers / task-triage | 会话开始、新任务 |
| change-impact-analysis | 任何修改意图 |
| brainstorming | 非简单 ①规划（HARD-GATE） |
| verification-before-completion | ④验证（审查政策 + R20 七维 SSOT） |
| systematic-debugging | Bug / 调试 |

**简单 = Phase0 已盘点 + 关联需改≤2 + 白名单 + 五维全低 + attempt=1**（判定正文只在 task-triage）。简单只缩短流程，**不豁免独立审查**。持续处理（attempt≥2）→ 执行升档非简单 + verify_tier=全量。

## 工作流主干（SSOT = `config/workflow.yaml`，下方为派生块）

> 改阶段 / 门控 / 完成定义 / 审查 → 只改 `config/workflow.yaml` → `python scripts/workflow.py render`。说明 → `docs/DEV_FLOW.md`。

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

<HARD-GATE>用户批准设计前禁止实现 → Read skills/brainstorming/SKILL.md</HARD-GATE>

**状态机**：DONE（独立审查 PASS）/ DONE_WITH_CONCERNS（仅用户显式豁免审查）/ NEEDS_CONTEXT / BLOCKED（含审查轮次用尽）。计划未批准 / 仅 `*.plan.md` / 纯澄清问答不进入完成态。TDD 与 SDD 仅用户明确要求时启用。

## 模型与推理强度

本包不指定任何模型或 effort。主会话模型由用户在会话 / settings / 编辑器中选择；子 Agent 不传即继承；推理强度只由被调用模型自身的设置决定。`cross-model-reviewer` 由调用方选一个与实现者不同的模型。`workflow.py check` 的 lint 拦截任何模型 ID / 档位别名 / effort 键回流。

## 铁律

R1 完成（验证证据 + 独立审查 PASS）| R3 Bug 全修 | R4 配置 Grep 引用 | R5 同方案≤2 | R8 高危确认 | R9 pwsh 7.5+ | R11 安全默认 | R12 子 Agent 隔离 | R13 制品存活 | R14 版本克制 | R15 pnpm | R16 错误暴露（禁裸 except:pass）| R17 codegraph 优先 | R18 claude-mem 记忆 | R19 禁自动 commit/stash | R20 会话终验（漏改 / 原功能 / 文档/注释 同步 / 问题是否解决）。**正文唯一在 `rules/CORE.md`**。

## 工具门控

**禁止**：eligible git 仓无双图时 Grep/Glob/everything/编辑/查询 MCP；未 `codegraph_explore` 直接做结构探索；未 Firecrawl+Exa 做深度调研；上下文 >70% 未评估压缩（Cursor `/summarize`，Claude Code `/compact`）。

## 审查路由

路由 = `config/workflow.yaml` `review.routing`（派生到 `rules/AGENTS.md`）。必派 eng-reviewer；无依赖并行 Task；审查者只读；修改只走 `change-implementer`；每轮全新开审。

## 命令

`/discuss` `/plan` `/execute` `/verify` `/ship` `/compact`（阶段）| `/review`（派发独立审查）| `/deep-research` | `/workstream` | `/adr` | OPSX：`/propose` → `/apply` → `/sync` → `/archive`。全集 → `commands/`。

## 指针

| 内容 | 位置 |
| --- | --- |
| 主干 / 流程说明 | config/workflow.yaml + docs/DEV_FLOW.md |
| 铁律 / 习惯 / 工具优先级 / 阈值 | rules/CORE.md |
| Agent / MCP / Git / 安全 / 规格 | rules/AGENTS.md / MCP.md / GIT.md / SECURITY.md / OPENSPEC.md |
| 工具链地板 | config/toolchain.yaml |
| 同步 | docs/SYNC_GUIDE.md（`scripts/sync.ps1`；不碰 settings.json / .mcp.json / hooks/） |
| 插件 | plugins/installed_plugins.json |

**业务仓库**：SessionStart ensure 双图；每轮开审前 last_edit 之后增量 refresh；Stop refresh。无图 deny。验绿后 `scripts/sync.ps1`。**RTK** → `RTK.md`。
