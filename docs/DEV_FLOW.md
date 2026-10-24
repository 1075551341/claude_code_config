# 推荐开发流程（v12 配置驱动）

> 唯一调度面：`config/workflow.yaml`。本文件中 `<!-- spine:* -->` 块由 `python scripts/workflow.py render` 生成，勿手改；其余为说明。

## 1. 一个文件驱动整条链路

| 想改什么 | 改 `config/workflow.yaml` 的哪一节 | 生效方式 |
| --- | --- | --- |
| 换后端 / 换模型（Anthropic、Kimi、DeepSeek、任意单模型网关） | `models.active_profile`，或在 `models.profiles` 新增一个 profile | `render` + `apply-settings --write` |
| 某个角色用哪一档、多大 effort | `roles.<agent>` | `render`（写 agent frontmatter `model` / `effort`） |
| 阶段、进入/退出门 | `stages` / `tracks` | `render`（写 commands 门控块、CLAUDE.md 流程表） |
| 一次通过契约 | `quality.definition_of_ready` / `quality.self_check` | `render`（写 change-implementer / planner 契约块） |
| 审查轮次、阻断次数、审查者路由、七维 | `review` | `render`（写 `quality_gates.json`、guard-config、审查者契约块、AGENTS.md 路由） |
| 分类所需档位、子任务优先级档位 | `triage` | `render`（写 task-triage / SDD 档位表） |

`python scripts/workflow.py check` 会校验配置（档位齐全、角色覆盖全部 agent、审查者档位不低于修改者、七维与 `hooks/_lib/r20_replay.py` 机械门一致），并检测派生内容是否漂移；`validate_config.py` V21 调用它。

### 切换模型（示例：换到 DeepSeek）

```bash
# 1. config/workflow.yaml: models.active_profile: deepseek
python scripts/workflow.py show                    # 预览：每个角色将用什么模型
python scripts/workflow.py render                  # 写回派生内容
python scripts/workflow.py apply-settings          # dry-run：看 settings.json 将改哪些键
python scripts/workflow.py apply-settings --write  # 合并 model / effortLevel / ANTHROPIC_DEFAULT_*_MODEL，并清掉上一 profile 的残留键（备份 settings.json.bak_<时间戳>，已 gitignore）
python scripts/sync-compact-window.py              # 按新模型上下文重算 autoCompactWindow
```

原理：agent frontmatter 只写档位别名（`opus` / `sonnet` / `haiku`）；profile 通过 `ANTHROPIC_DEFAULT_{OPUS,SONNET,HAIKU}_MODEL` 把别名重定向到具体模型，所以换后端不改任何 agent 文件。`apply-settings` 会移除 `CLAUDE_CODE_SUBAGENT_MODEL`（它会覆盖全部 agent 的路由）。`single` profile 让所有 agent `inherit` 会话模型，适合只有一个模型的网关。

Cursor 侧：Cursor 也会读取 `~/.claude/agents/`，但它的 frontmatter `model` 只认 `inherit` 或 Cursor 模型 ID；`opus` / `sonnet` / `haiku` 别名在 Cursor 中不保证生效。因此 Cursor 的路由以 `CURSOR-EDITOR.mdc` 派生表为准：主会话派发 `Task` 时显式传 slug，覆盖 frontmatter。只用 Cursor、不想依赖派发时传参的用户可切到 `single` profile（全部 `inherit`）。

<!-- spine:models -->
当前 profile：**anthropic** — Anthropic API / Claude Platform（默认）

| 档位 | Claude Code 别名 → 模型 | Cursor slug | 上下文 |
| --- | --- | --- | --- |
| frontier | `opus` → `claude-opus-5-5` | `claude-opus-5-5-high` | 1000000 |
| mid | `sonnet` → `claude-sonnet-5-5` | `claude-sonnet-5-5-medium` | 1000000 |
| light | `haiku` → `claude-haiku-5-5` | `composer-2.5-fast` | 200000 |
<!-- /spine:models -->

## 2. 角色路由

<!-- spine:roles -->
| 角色 | 档位 | effort | Claude Code `model` | Cursor Task `model` |
| --- | --- | --- | --- | --- |
| session | frontier | high | `opus`（claude-opus-5-5） | `claude-opus-5-5-high` |
| planner | frontier | high | `opus`（claude-opus-5-5） | `claude-opus-5-5-high` |
| architect | frontier | high | `opus`（claude-opus-5-5） | `claude-opus-5-5-high` |
| agentic-orchestrator | frontier | high | `opus`（claude-opus-5-5） | `claude-opus-5-5-high` |
| change-implementer | mid | high | `sonnet`（claude-sonnet-5-5） | `claude-sonnet-5-5-medium` |
| build-error-resolver | mid | medium | `sonnet`（claude-sonnet-5-5） | `claude-sonnet-5-5-medium` |
| spec-reviewer | mid | high | `sonnet`（claude-sonnet-5-5） | `claude-sonnet-5-5-medium` |
| sre | mid | medium | `sonnet`（claude-sonnet-5-5） | `claude-sonnet-5-5-medium` |
| code-explorer | light | low | `haiku`（claude-haiku-5-5） | `composer-2.5-fast` |
| doc-writer | light | medium | `haiku`（claude-haiku-5-5） | `composer-2.5-fast` |
| eng-reviewer | frontier | high | `opus`（claude-opus-5-5） | `claude-opus-5-5-high` |
| security-reviewer | frontier | high | `opus`（claude-opus-5-5） | `claude-opus-5-5-high` |
| codex-reviewer | frontier | high | `opus`（claude-opus-5-5） | `claude-opus-5-5-high` |
| ceo-reviewer | mid | medium | `sonnet`（claude-sonnet-5-5） | `claude-sonnet-5-5-medium` |
| designer | mid | medium | `sonnet`（claude-sonnet-5-5） | `claude-sonnet-5-5-medium` |
| dx-reviewer | mid | medium | `sonnet`（claude-sonnet-5-5） | `claude-sonnet-5-5-medium` |
| qa | mid | high | `sonnet`（claude-sonnet-5-5） | `claude-sonnet-5-5-medium` |

> effort 只作用于 Claude Code；Cursor slug 按档位固定（effort / fast 已编码在 slug 中）。
<!-- /spine:roles -->

## 3. 阶段与轨道

<!-- spine:flow -->
| 阶段 | 命令 | skill | 角色（档/effort） | 退出门 |
| --- | --- | --- | --- | --- |
| ⓪分类 | — | task-triage | session（frontier / high） | 输出分类契约：大类 \| 需改文件 \| 模型档(当前≥所需) \| verify_tier \| 置信度 \| 成功标准 |
| ⓑ根因 | — | systematic-debugging | session（frontier / high） | 根因证据一行（失败日志 / 断点 / 最小复现）；修复点与回归验证命令写入影响清单 |
| ⓡ调研 | — | deep-research | session（frontier / high） | 关键结论 ≥2 个独立来源交叉验证，标注时效与可信度 |
| ①规划 | /discuss | brainstorming | session（frontier / high） | grill ≤5 问收敛，验收标准可量化；HARD-GATE：用户批准设计 |
| ②规格 | /plan | writing-plans | planner（frontier / high） | spec-validation 通过，无静默缩 scope；就绪定义（quality.definition_of_ready）全部满足 |
| ③执行 | /execute | executing-plans | change-implementer（mid / high） | 清单内文件一次改齐（含文档/注释/INDEX/版本戳）；构建/类型/Lint 通过；R16 无静默吞异常；提交审查前自检（quality.self_check）通过 |
| ④验证 | /verify | verification-before-completion | session（frontier / high） | verify_tier 对应清单全部附命令证据；审查前刷图（last_edit 之后）；本轮全新审查批次全部 PASS（review.routing） |
| ⑤学习 | /compact | memory-compression | session（frontier / high） | claude-mem 记录模式/决策（R18） |
| ⓢ交付 | /ship | ship | session（frontier / high） | 用户要求的交付物完成（commit / PR / 发布），CI 绿 |

- **simple**：⓪分类 → ③执行 → ④验证
- **bug**：⓪分类 → ⓑ根因 → ③执行 → ④验证
- **non_simple**：⓪分类 → ①规划 → ②规格 → ③执行 → ④验证 → ⑤学习
- **research**：⓪分类 → ⓡ调研 → ④验证
- **按需**：ⓢ交付（不在轨道内；用户明确要求时进入，R19）
- **审查**：一轮 = 改 → 验 → 刷图 → 并行全新审查；上限 5 轮（Stop 阻断 3 次）；必派 eng-reviewer。
<!-- /spine:flow -->

## 4. 一次通过（不靠返工达标）

返工通常来自三处：开工时验收标准不清、影响清单漏项（文档/INDEX/版本戳）、审查清单与实现者自检清单不一致。v12 用配置把这三处在开工前和交审前堵住：

1. **就绪定义**（`quality.definition_of_ready`）：③执行前必须有可验证的验收标准、完整影响清单、预选验证命令、预选审查者。缺一项不开工。这一段渲染进 `planner` 与 `change-implementer`。
2. **交审前自检**（`quality.self_check`）：修改者用与审查者 **同一份** 七维逐条自检，并确认残留引用为 0、派生块已 render。
3. **同源审查契约**：每个审查者 agent 的契约块与 verification skill 的七维都从 `review.dimensions` 渲染，hooks 的机械门（`r20_replay.py`）由 V21 对齐校验，所以「实现者以为做完了」和「审查者认为做完了」用的是同一把尺。

审查轮次上限（`review.max_rounds`）只是兜底，不是预期路径。预期是第一轮审查就 PASS。

## 5. 派生清单

<!-- spine:derived -->
| 目标 | 内容（来源节） |
| --- | --- |
| agents/*.md frontmatter | `model` / `effort`（roles × active profile） |
| 审查者 agents `spine:review-contract` | 七维 + 结论 + 只读规则（review） |
| change-implementer / planner `spine:ready-contract` | 就绪定义 + 交审自检（quality） |
| commands/{discuss,plan,execute,verify,ship,compact}.md `spine:stage-gate` | 阶段进入/退出门（stages） |
| CLAUDE.md / docs/DEV_FLOW.md `spine:flow` | 阶段表 + 轨道 + 审查轮次 |
| rules/AGENTS.md `spine:review-routing` | 审查路由（review.routing） |
| skills/task-triage `spine:tier-map` | ⑥模型匹配档位（triage + profile） |
| skills/subagent-driven-development `spine:priority-tiers` | 子任务优先级 → 档位 |
| skills/verification-before-completion `spine:dimensions` | 七维清单 |
| templates/cursor-guard/rules/CURSOR-EDITOR.mdc `spine:cursor-models` | Cursor Task model slug 表 |
| config/quality_gates.json verification_gate | 轮次 / 阻断 / 最少文件 / 审查者名单 / 刷图 |
| templates/cursor-guard/guard-config.json verification.reviewer_agents | Cursor 审查者名单 |
| config/model-context-windows.json model_tokens | 全部 profile 模型上下文 |
| templates/claude-settings/model.snippet.json | settings.json 模型键（apply-settings 合并） |
| templates/editor-graph-hooks/verify-gate.ts | `review_max_rounds=<n>` 文案（review.max_rounds） |
<!-- /spine:derived -->

## 6. 从 v11 迁移

| v11 | v12 |
| --- | --- |
| 轮次/阻断写在 `config/quality_gates.json`，校验器硬编码 5/3 | 只改 `config/workflow.yaml` `review`；`quality_gates.json` 由 render 同步（hooks 读取方式不变） |
| `agents/code-reviewer.md` 与 `eng-reviewer` 并存 | 并入 `eng-reviewer`；`code-reviewer` 仍列在 `legacy_reviewer_names`，hooks 照常识别旧名委派 |
| `skills/pr-workflow` + `skills/finishing-a-development-branch` + `skills/ship` 三处讲发布 | 正文只在 `skills/ship`；`finishing-a-development-branch` 保留为指向 ship 的薄壳（防止上游 superpowers 同名技能回填） |
| 模型档位散落在 task-triage（frontier/mid/light）与 SDD（Opus/Sonnet/Haiku）两张表 | 只在 `models` + `roles` + `triage`；两张表改为派生块 |
| catalog 内有全局 agent/skill 的同名副本 | 删除；全局为唯一权威 |
| 未注册 hooks（tmux/loop-guard/suggest-compact/context-monitor） | 删除（原生机制与 Cursor Guard 已覆盖；git 历史可回溯） |

已部署用户：

1. `git pull`。
2. **先选后端**：v12 默认 `active_profile: anthropic`，agent frontmatter 已改写为 `opus` / `sonnet` / `haiku`（v11 多为 `inherit`）。Kimi / DeepSeek / 网关用户先把 `models.active_profile` 改成 `kimi` / `deepseek` / `single`，再 `python scripts/workflow.py render`。不要用 `anthropic` 跑 `apply-settings`，否则会把 `ANTHROPIC_DEFAULT_*_MODEL` 写成 Claude 模型 ID。
3. `python scripts/workflow.py check` → `python scripts/workflow.py apply-settings`（先 dry-run 看 diff）→ `apply-settings --write`。
4. `python scripts/sync-compact-window.py` → `pwsh -File scripts/sync.ps1 -All`（Cursor 侧再跑 `deploy-cursor-guard.ps1`，`reviewer_agents` 会跟随模板）。

`active_profile` 是本机选择但写在受版本控制的文件里：切换后约 22–28 个派生文件会变脏（视前后 profile 而定）。只在本机用时，把这些改动留在本地分支；`git update-index --skip-worktree` 也可以，但上游改到同一文件时 `git pull` 会失败，需先 `--no-skip-worktree`。要团队共享就提交。若 `settings.json` 的 hooks 仍注册了已删的 4 个 hook，按 `templates/claude-settings/hooks.snippet.json` 清理。
