# CHANGELOG — 配置变更史

> v11 起变更摘要自 `SPEC.md` 外置到本文件；SPEC 只保留现行法典。新版本在顶部追加。

## v11.4.13 场景路由 YAML + 审前双图 + inherit 并行审查（2026-09-03）

- **配置驱动**：新增 `config/scenario-router.yaml`（场景→load.skills/agents + quality）与 `config/harness-capabilities.yaml`（capability → 当前端 provider/fallback/interrupt）。分类后只按 YAML 加载；缺能力走声明降级，禁止假装调用。
- **独立审查**：审前强制双图 ensure（codegraph init|sync + CRG build|update）。只读 + 维度不重叠 + 子代理 `model=inherit`（禁止 max/xhigh/thinking-max 倍率档）时允许并行多审查（最多 3）；否则串行。日常 `review_max_rounds=3` 不变。
- **Harness 适配**：`sync-manifest.json` 增 `harnesses`（DSH / OpenCode）。`editors.opencode.enabled` 仍 false，禁止 CLAUDE.md 覆盖 AGENTS.md。`check.ps1` 在 home 存在时断言便携 CLI 且 AGENTS.md 非 CLAUDE.md 软链。
- **漂移清零**：SPEC MCP 常驻 4；hooks 19 注册；Superpowers 6.3.0；INDEX 版本对齐；插件表 hud/exa/context7/firecrawl/playwright/github 与 v11.4.5 一致；workbuddy `enabled=true`（home 缺席跳过）；`validate_config.py` BASE=`CLAUDE_HOME`/仓根回退 + `change-implementer` + V20 校验两份 YAML。
- **文档**：SYNC_GUIDE 补 DSH 适配层；TOOL_MATCHING_GUIDE / using-superpowers 改为指针。不精简 skill/agent/rule/catalog。
- **多端**：DSH 2.12 / OpenCode 1.12 映射到 11.4.13。Guard 仍 1.2.11。

## v11.4.12 一次找齐再集中改 + 每轮全新开审（2026-09-01）

- **一次找齐**：独立审查必须扫完影响面后再给结论；禁止发现一条就停审/立刻改。完整清单到位后再派**一次** `change-implementer` 集中改齐。
- **每轮全新开审**：下一轮独立审查必须新开 Task/Agent（禁止 `resume` 上一轮审查者）；对照原始要求全量重扫，上轮清单仅参考、不得限定范围。避免把上轮遗漏/误判带进下一轮、耗尽 3 轮后仍有未扫项。
- **机械门**：`is_resumed_subagent`；带 `resume` 的审查委派不计入 `reviews`（Claude tracker 注入提醒；Cursor `verify_tracker` 跳过记账）。Cursor Guard **1.2.11**。
- **多端**：DSH 2.12 / OpenCode 1.12 手工对齐。

## v11.4.11 审查只找问题 + 修改者分角色（2026-09-01）

- **R20**：配置/修改必须与文档、注释、版本戳同步；不一致不得声称完成。
- **双审角色分离**：`eng-reviewer`（及审查角色：ceo/designer/dx/qa/security）只对照原始要求找问题；`tools` 仅 Read/Grep/Glob；禁止改文件、禁止提交补丁。落实修改必须 `Task` `change-implementer`（Cursor 无该类型则 `generalPurpose` 且 prompt 声明修改者）。禁止同一 agent 既审又改。
- **结论不一致**：验证与独立审查不一致（含 PASS 夹带必须修项 / 须同步）→ 立即再派修改者，禁止只汇报等用户。`apply_review_verdict` 将 PASS+须同步视为不干净。
- **多端**：DSH 2.10 / OpenCode 1.10 手工对齐。Guard 仍 1.2.10（完成门不 followup）。

## v11.4.10 Cursor 完成门不再 followup（2026-09-01）

- **根因**：Cursor Stop 不能 `permission: deny`；`followup_message` 变成假用户回合刷会话面板；`loop_count` 随 generation 重置，会话级 `edited_files` 使 Agent「本轮零编辑」无法停 hook。
- **Cursor Guard 1.2.10**：`verification_stop` 只做图谱 refresh / 全绿 `sync.ps1`，**禁止** `followup_message`。`verification_gate` 不再注入完成门 `additional_context`。`context_stop` 不再为验证 followup 让位。`enforce_mode=off`（旧 followup/soft 部署值映射为 off）。完成验证改由规则驱动：修改→验证→独立审查；PASS 即停；仅结论不一致才再开一轮，最多 3 轮。
- **不改**：Claude Stop `exit 2`；`first_edit_verify`；图谱 deny；用户显式「提取上下文」followup。
- **多端**：DSH 2.9 / OpenCode 1.9 手工对齐（禁止把 followup_message 搬过去）。`sync.ps1` 仍不覆盖 AGENTS.md。

## v11.4.9 计划等待零注入 + 有改动即双审 + 双图起止（2026-09-01）

- **P0 计划等待**：Cursor `CreatePlan` 走 `CallDynamicTool` 时 `verify_tracker` 必须记账；写 `.cursor/plans/*.plan.md` 不得清除 `awaiting_plan_approval`、不计完成门。`verification_stop` 在 awaiting 时硬 return（可静默 refresh 图谱）。生产链单测覆盖 CallDynamicTool + 写 plan.md。
- **双图**：Windows `/d:/` 与 `file:///d:` 路径规范化；已有图时 CLI `update` 失败记警告不阻断（避免 CRG expansion cap 把整仓编辑锁死）。Cursor `sessionEnd` 调 `refresh_incremental`（timeout 45s）。Guard **1.2.9**。
- **双审**：`require_reviewer_min_files` 3→1；有代码/配置改动须独立审查一次。**PASS/符合预期即停**（禁止再审浪费 token）；仅审查与修改/验证结论不一致（NEEDS-CHANGES）才再改再验再审，最多 3 轮。只读与计划制品 skip。
- **多端**：DSH 2.8 / OpenCode 1.8 手工对齐（`sync.ps1` 仍不覆盖 AGENTS.md）。OpenCode `verify-gate` 计划等待不注入 R20 完成令。

## v11.4.8 双审循环=修改→验证→审查（2026-08-31）

- **语义**：非简单双审不是「只审查最多 3 次」，而是 **修改 → 验证（对照原始要求）→ 独立审查全部修改** 循环，直到符合预期或满 3 轮。`NEEDS-CHANGES` 后无新修改不得再审（禁止只连审不改）。
- **机械门**：`dual_pass_phase` = modify | verify | review | capped | done。Cursor/Claude Stop 按相位注入。`review_cycle: modify-verify-review`。`review_rounds` 仅在 last_edit > last_rev 时 +1（同轮连派不耗轮次）。`apply_review_verdict`：PASS 须已有 reviews，禁止自报。已部署 `guard-config` 若仍含裸词「完成」，deploy 跟模板对齐。
- **多端**：DSH 2.7 / OpenCode 1.7 手工对齐。Cursor Guard **1.2.8**。
- **不改**：计划未批准禁止 followup、短 R20 六字段、`require_reviewer_min_files=3`、sync 不覆盖 AGENTS.md。

## v11.4.7 计划未批准不终审 + 短 R20 + 非简单双审（2026-08-31）

- **根因**：Cursor `CreatePlan` 后用户未点 Build，`stop` 仍写 `followup_message`（完成验证门），把计划等待当成任务完成。
- **Cursor Guard 1.2.7**：计划未批准 / CreatePlan / SwitchMode→plan / 本轮零编辑 / 无 session id → **禁止 followup**；禁止把 session 写成 `"unknown"`。完成门不再用裸词「完成」（避免「所有都完成后」回灌）。短 followup；审查满 3 次仍无 PASS → `DONE_WITH_CONCERNS`，禁止第 4 次空转。
- **短 R20**：`gate_messages.md` 完成验证门收成约 6 行；技能模板六行字段不变（满足/遗漏/错改/漏改/原功能/影响范围），机械检测仍走 `r20_replay.py`。
- **非简单双审**：执行者做完后 fresh `eng-reviewer` 审 diff+影响面；`NEEDS-CHANGES` 则执行→再审；**审查最多 3 次**（含首次）。简单任务仍一轮。`require_reviewer_min_files` 保持 3。
- **多端**：DSH AGENTS **2.6**、OpenCode AGENTS **1.6** 手工对齐（独立视角再审最多 3 次；禁止把 Cursor `followup_message` 搬过去）。`sync.ps1` **不覆盖** 两端 `AGENTS.md`。OpenCode `verify-gate.ts` 仅在有未验编辑时注入短 R20。
- **不改**：图谱保鲜硬门；R5 同方案 ≤2；不启用 ralph-loop。

## v11.4.6 图谱保鲜硬门（2026-08-29）

- **会话先建图**：SessionStart 对 eligible git 仓执行 `codegraph init\|sync` 与 `code-review-graph build\|update`（不是仅提示）。超时：SessionStart 120s、PreToolUse 90s、Stop 刷新 30s。`_editor_hook_launcher` 子进程超时 55s→180s，避免截断 ensure。
- **无图不准后续**：PreToolUse deny 查询 MCP / Grep / Glob / 写工具；建图类 CLI/MCP 放行。取消「无图 Grep 兜底」主路径。
- **验绿后 sync.ps1**：Stop 增量刷新双图；仅验证门全绿（非跳过、非 max_blocks）才 `pwsh sync.ps1 -Scope rules`。
- **多端**：Claude + Cursor Guard hook；TRAE/Qoder 用 `scripts/deploy-editor-graph-hooks.ps1` 合并注册（不经 launcher）；workbuddy 仅 CLAUDE/CORE 硬性规则。**DSH 2.3 / OpenCode 1.3**：提取便携 CLI `templates/editor-graph-hooks/graph_freshness_cli.py`（ensure/refresh）到 `~/.dsh/tools` 与 `~/.config/opencode/scripts`；OpenCode `plugins/graph-freshness.ts` 会话开始 ensure、idle refresh；DSH 无 Stop，总纲+verification 强制同一 CLI。仍不经 `sync.ps1` 覆盖各端 AGENTS.md。
- **不恢复** 每次编辑 kg sync hook（codegraph watcher 仍管日常改动）。
- **cwd 回退（重启复验）**：SessionStart/PreToolUse 用 `resolve_cwd`（`cwd` → `workspace_roots` → `VSCODE_CWD` → 进程 cwd），避免 Cursor 不传 cwd 时把 eligible 仓当成非 git 跳过 ensure。Cursor matcher 含 `CallDynamicTool` / `MCP:.*`，并挂 `beforeMCPExecution`。
- **cwd 优先级补漏**：用户级 Cursor hook 进程 cwd / payload.cwd 常为 `~/.cursor`（本机联接 `D:\cursor`，非 git）。`resolve_cwd` 改为**先选 git-eligible 的 `workspace_roots`**，不再让 hook-home cwd 抢先；仍无 git 根时读 `projects/*/.workspace-trusted`（viewed files 不得压过已信任工作区）。显式非 git 的 `workspace_roots` **或 payload `cwd`** 禁止 infer 到另一仓。Stop 无编辑也增量刷新双图，且 **保留 SessionStart 的 `session_id`、不因 CLI 超时把 `ok` 打成 False**。sessionStart 成功 ensure 后写入 `env.CURSOR_PROJECT_DIR` 供后续 hook。
- **Cursor Guard 1.2.6**：SessionStart `user_message` 展示双图同步成功/失败（非仅 additional_context）；Stop 刷新同样 `user_message`（失败必显、成功每会话一次）。子项目 depth-1 封顶，禁止无穷嵌套同步。
- **R20 影响范围**：终验必填「影响范围」并对照 CRG/IMPACT/blast；便携 `r20_check.py` 提取到 DSH `tools/` 与 OpenCode `scripts/`；OpenCode `verify-gate.ts` 机械门对齐。DSH 2.5 / OpenCode 1.5。不经 `sync.ps1` 覆盖各端 AGENTS.md。
- **DSH 2.4 / OpenCode 1.4**：对齐「禁止重复调用/注入」——ensure 每会话一次；OpenCode `GRAPH_RULE`/`R20` 每会话注入一次，idle refresh 60s 冷却，加急每空闲周期一次。不经 `sync.ps1` 覆盖 AGENTS.md。
- **Cursor Guard 1.2.4 防乒乓**：`context_stop` 的「上下文≥90%」`followup_message` 每会话只发一次（`loop_limit=1` 不能跨「followup 当新用户消息」生效）。工具侧 90% `additional_context`/`agent_message` 同样只注入一次。`/summarize` 与「压缩上下文」重置工具计数并清除陈旧 preCompact 百分比，避免估算永远卡在 FORCE。

## v11.4.5 MCP 分工 + 门控六维纠错（2026-08-29）

- **工具优先级**：编辑器内置 > 同名 plugin > MCP > 按需中断启用。常驻 MCP 仍为 codegraph / CRG / serena / grep。Firecrawl：Claude 走 plugin（不写 `.mcp.json`）。
- **CRG 扩权**：精准上下文（`get_minimal_context`）+ 变更影响（`get_impact_radius`）+ 风险/审查/开 PR（`detect_changes` / `get_review_context`）。codegraph 仍为 R17「怎么运作」。chrome-devtools / postgres 默认关，需要时**中断请用户手动启用**（禁止自动 merge debug/ops）。
- **门控续轮**：追踪器记 `crg_calls`；有 `.code-review-graph/` 且最后一次代码编辑后未调 CRG → Stop/followup 阻断。续轮文案六维：影响面/需求未达/错改/漏改/原功能/文档。`max_blocks=3` 不变。
- **R20 满足行三态**：对指纹关键词承认/反驳/弃权（GSD honest-verifier）；硬门仍用 `coverage_ok`。
- **不吸收**：竞品 code-graph plugin；ralph-loop / 独立 `/loop`；实验性 agent-Stop hook；caveman 2.x；claude-mem ≥13.14；OpenSpec 1.10。
- **多端**：Cursor/qoder/trae 经 sync 规则通道。DSH AGENTS 2.2 + skills；OpenCode AGENTS 1.2 + oc-\* skills；`verify-gate.ts` **仅改注入文案**。各端 plugin/MCP 开关不动。
- **复核补漏**：OpenCode `oc-using-superpowers` 去掉过时「未挂 CRG」；SPEC 页脚 / fsaccess / GOVERNANCE / TOOL_MATCHING 的「常驻 9」与 Firecrawl-MCP 措辞对齐；有图判定须存在 `graph.db`（避免把空的 `~/.code-review-graph` 登记目录当项目图）；Cursor Guard 测试覆盖「有图无 crg_calls → followup」。

## 2026-08-29 MCP 裁剪

- **删除常驻**：全部编辑器去掉 `aider-repo-map`、`sequential-thinking`（不要加回）。
- **chrome-devtools 默认关**：Claude plugin=`false`；OpenCode/DSH/Qoder 条目保留但 disabled；Cursor 为 Plugin，须在面板 Disabled。
- 权威：`.mcp.json` 仅 codegraph / CRG / serena / grep。

## v11.4.4 出站切断（2026-08-27）opencode / DSH 不再耦合 Claude 配置

- **sync 切断**：`config/sync-manifest.json` 将 `opencode.enabled` 置 `false`；`sync.ps1`/`check.ps1` fallback 对齐。不再把 `CLAUDE.md` 覆盖 `~/.config/opencode/AGENTS.md`。`enabled=false` 仅反向扫残留软链，OpenCode 自管的实体 `AGENTS.md` 保留。
- **范围**：不改 Claude 本体 `settings.json` / hooks / skills / `.mcp.json`。OpenCode 与 DSH 各自拥有独立总纲、P0 技能、MCP 启动脚本与验证门。

## v11.4.3 配置一致性修复（2026-08-26）全量审计 + 触发词去重 + 权限对齐

- **审计**：validate_config 19 项 PASS 基础上清零遗留漂移——MANIFEST 版本串滞后（头注释 11.4.0/version 11.4.1 → 对齐全局）、SPEC plugins 计数失实（enabledPlugins 实为启用7/禁用9，claude-hud/exa 未显式登记）、hooks/README `_lib` 计数 8→10（v11.4 新增 gate_cli.py/req_fingerprint.py 漏更）、gate_messages.md 头部版本标记停 v11.3.5
- **触发词去重（V1 归零）**：`重构` 唯一归属 code-refactoring；change-impact-analysis 与 improve-codebase-architecture frontmatter triggers 移除裸词（路由无损：前者 P0 表强制触发、后者保留 架构改进/refactor/技术债务）
- **策略对齐**：settings.local.json 删 `Bash(powershell *)` allow（与 R9 + pre-bash-guard PS5.1 警告一致）；opencode.json chrome-devtools → enabled:false（debug 按需，与 Claude 侧 mcp-configs/debug.json 同语义）
- **插件登记**：enabledPlugins 显式补齐 claude-hud@jarrodwatts=true / exa@claude-plugins-official=false（exa 已由 .mcp.json 常驻挂载，禁双挂）
- **残留清理**：删 ~/.config/opencode/plugins/.load-probe-marker + zz-load-probe.ts（v11.4.1 插件加载诊断探针使命完成）

## v11.4.2 防乱码约束（2026-08-26）编码守卫双阶段 + 格式化保行尾 + 命令误用警告

- **编码守卫（hooks 16→18）**：新增 `pre-encoding-snapshot.py` + `post-encoding-check.py`（共享库 `_lib/encoding_guard.py`）——Pre 快照目标文件 BOM/EOL 签名（`.state/encoding-snapshots.json`），Post 比对差异 + 绝对检查（非法 UTF-8/U+FFFD 替换符/GBK 双重编码特征串/游离 BOM/json+py 带 BOM/严重 mixed EOL）；检出经 additionalContext 警告注入永不阻断，提示立即回滚、禁止在损坏内容上叠加修改；注册于 Edit/Write/MultiEdit + serena/fs MCP 双组（PostToolUse 顺序=格式化→编码校验→密钥扫描→验证追踪）
- **格式化治本**：`post-edit-format.py` prettier 三处调用补 `--end-of-line auto`——此前 npx prettier 兜底按默认 LF 输出，会把 CRLF 配置文件静默改写行尾，是 AI 编辑配置仓反复出现异常的最大来源
- **命令误用警告**：`pre-bash-guard.py` 新增编码误用警告组——echo/tee/Set-Content/Add-Content/Out-File/heredoc 重定向写文件内容（PS5.1 默认 ANSI 是乱码重灾区）、powershell.exe(PS5.1)（落实 R9）、sed -i → 一律警告注入并给出稳定替代（Edit/Write 工具/pwsh）
- **规则层**：`rules/CORE.md` 新增「文件编码与写入约束」小节：默认 UTF-8 无 BOM、保留目标文件既有编码/BOM/EOL、文件内容写入一律用 Edit/Write 工具禁 shell 重定向、Windows 中文输出先设 UTF-8、检测到乱码立即回滚禁叠加、二进制禁 Read/Edit
- **登记链**：settings.json（Pre/Post 各 +2 注册位，共 24 hook 条目）+ hooks.snippet.json 快照刷新 + hooks/README v5.9（18 注册激活）+ MANIFEST.yaml core 清单 + TRAE AppData pre-bash-guard 副本同步

## v11.4.1 同日热修（2026-08-25，opencode 插件活性 + 观测性）

- **目录净化（去耦合）**：删除跨编辑器误生成残留 `~/.claude/.cursor/`、`.trae/`（openspec init 于 .claude cwd 误产物；用户手删）+ `.git/opencode`（watcher projectID 标记）+ `__pycache__`×5（406KB）+ `.ruff_cache` + `debug.log`（搜狗输入法误落）+ `last_summary_date.txt`（零引用已证）+ tray 诊断残留；`openspec/` 含全局 config.yaml **改判保留**。**设计内耦合清单声明**（保留勿清）：`templates/cursor-guard/`、`docs/CURSOR_*.md`、sync-manifest editors 段、sync/check/fix.ps1 多端逻辑、`plugins/marketplaces/*`（claude-mem 插件源码含 .windsurf 子树）、`mcp-configs/`。配套：.gitignore UTF-8 重写（修乱码注释 + 删 .cursor 白名单×3 + 增 `/.ruff_cache/`）、package.json version → 11.4.1、README/SYNC_GUIDE「永不同步」清单措辞更新

- **插件未触发根因修复**：全局插件目录单数 `plugin/` → 官方约定复数 `plugins/`（autoload 不加载单数目录）；插件导出形态改为仅命名导出 `VerifyGate`（去除 default 双导出疑似注册冲突）
- **观测性**：插件接 `client.app.log`（service=verify-gate）——加载/捕获/追踪/idle 全链路可于 opencode.log 审计；gate_cli 非零退出/spawn 失败显式上报
- **健壮性**：python 路径 `Bun.which` 解析；`message.updated(role=user)` 事件流兜底 capture-req（chat.message 未触发时仍建档，会话级去重）
- **指纹条目时间戳**：`req_fingerprint.save_requirements` 建档补 `started_ts/ts`（修验证探针盲区：纯指纹条目原无时间戳，新鲜度过滤误判为不存在）
- **关闭防误触**：新增 `~/.config/opencode/tui.json`——`app_exit` 收敛为 `<leader>q`；ctrl+c 走双按退出守卫（上游 PR #12733 内联确认）；原生退出确认弹窗无配置项（#40510 开放中），此为当前最接近方案
- **托盘伴侣 v3**：桌面版 close-to-tray 上游未实现（#35775 assigned 未发布；源码 window-all-closed→quit）。**用户定义行为语义**：点 X=隐藏到托盘（等效实现：看门狗检测退出→800ms 确认→自动重启→新窗口绘制后自动隐藏，会话持久化恢复）；托盘「退出 OpenCode」=正式退出（AutoRelaunch 让位）；托盘左键唤回。v2 的 SC_CLOSE 灰化已回退（用户要 X 可点而非死按钮）。**OpenCode 开机自启审计：零条目**（HKCU/HKLM Run+RunOnce、WOW6432Node、双启动文件夹、计划任务全查无命中）；伴侣亦有意不自启（用户决策）。**插件加载诊断探针**：`plugins/zz-load-probe.ts` 顶层写 marker——下次重启判别「目录未扫描 vs 钩子未注册」

## v11.4.0 变更摘要（2026-08-25，多端验证精细化 + opencode 接入 + 上游矩阵）

- **主诉**：「解决后验证不够精细」（不符合预期要求 / 漏改 / 错改 / 破坏原功能）。路线 C=混合分层（brainstorming 访谈确认）：机械层全任务常开 + 独立审查分层触发。
- **G3 错改硬证据自动化**：`post-edit-verify-tracker.py` 增 `append_impact_record()`——追踪到的编辑路径自动写项目 `.claude/state/impact-manifest.log`，方案A清单差集不再依赖模型自觉落盘；`IMPACT_REMINDER` 降级为写失败兜底。测试 `hooks/tests/test_impact_autolog.py`（含 e2e git 仓库场景）
- **G2 需求指纹实质比对**：新增 `_lib/req_fingerprint.py`（复用 `issue_state.extract_features` strong/weak 分层，零新算法）；捕获点=`pre-userprompt-issue-tracker.py`（与问题指纹同点）；`r20_replay.replay_ok(text, requirements=None)` 可选参——「满足」行须命中 strong 指纹（<5 全命中，≥5 允许 ≥80%），weak-only 不启用防误伤；Stop 门经 `requirement_fingerprint` 开关传入。Cursor 端 import_claude_lib 同源自动继承
- **W3 审查结论机械检测**：`r20_replay.review_verdict_ok()`（PASS / NEEDS-CHANGES 大写标记）；≥3 文件已委派但回复缺结论 → 阻断；blocks≥2（持续处理代理信号）即使 <3 文件也触发审查委派要求。开关 `require_review_verdict` / 触发线 `verdict_trigger_min_blocks`
- **G1 opencode 接入**：sync-manifest editors 增 `opencode`（special=`agents_md`，CLAUDE.md 改名副本落 `~/.config/opencode/AGENTS.md`；sync.ps1/check.ps1 各增分支，fix.ps1 有意不纳——无 launcher）；新增 opencode 插件 `~/.config/opencode/plugins/verify-gate.ts`（chat.message 存指纹 / tool.execute.after 追踪 / system.transform 注入 R20 完成令 / idle 未验加急提醒）+ 薄入口 `_lib/gate_cli.py`（判定 SSOT 仍居 \_lib，禁复制实现）。平台限制：opencode 无 Stop exit-2 硬阻断，硬阻断二期评估。**修正（同日复查）**：全局插件目录须为复数 `plugins/`（官方 autoload 约定），单数目录不会被加载
- **G4 上游矩阵（详证 → `docs/research/45-upstream-stability-v11.4.md`）**：superpowers cherry-pick 分级仪式（spike/bounded/architectural，HARD-GATE 不减）；OpenSpec 升 1.10.0（changelog 无破坏+init 冒烟门）；gsd-core 版本串 1.11.0（Node≥24 不适用：概念集成）；ECC 2.1.0 参考串；rtk 0.45.0；CRG pin 2.3.8（明示 no breaking）；caveman 条件升级（diff 门）；**claude-mem 维持 13.13.1 钉扎**（13.14+ 为 CMEM Pro 推销专版，运行态核查未越线）；gstack vendored 维持
- **版本一致性**：CLAUDE.md / SPEC.md / MANIFEST.yaml / rules-CORE.md / verification SKILL.md / sync-manifest.json / scripts-README / SYNC_GUIDE 全量 v11.4.0
- **SSOT**：验证链判定唯一居于 `hooks/_lib/*.py`；多端（Claude/Cursor 直载、opencode 子进程）共享同一份实现

## v11.3.5 变更摘要（2026-08-20，验证准则分解评分 = llm-as-a-verifier）

- **优点来源**：github.com/llm-as-a-verifier/llm-as-a-verifier（通用验证框架，agentic benchmarks SOTA）。提取 9 项优点，与 Claude 配置自身优点盘点对比后融合缺失 5 项；完整对比矩阵与决策记录 → `docs/LLM_AS_A_VERIFIER_SYNC.md`
- **verification skill 新增「验证准则分解评分」小节**（SSOT）：①观察输出优先——证据=命令 stdout/stderr、测试结果、文件内容，**禁止以 agent 叙述代替证据**（Trust observed output — NOT narration）；②准则分解≥2 条（正确性/根因/验证确认三问）逐条核验；③关键结论 1–20 细粒度评分（<10 不声称完成，禁二值模糊）；④关键验证项重复评估≥2 次（独立视角/反向验证）；⑤方案选择/审查候选成对比较 + A/B 交换复评消位置偏差（多候选与参照基线比较，O(Nk) 控成本）；⑥长任务每原子任务自评进度分，连续 2 次 <10 → 上报止损/换方案
- **L0 同步**：CLAUDE.md 版本行 + R20 行「验证证据须观察输出（命令/测试/文件），不信叙述」；rules/CORE.md R20 会话终验段同句；hooks/\_lib/gate_messages.md 版本行 + 软性短句（**不动硬门字段**）
- **hooks 零变更**：R20 模板字段（满足/遗漏/错改/漏改/原功能）原样保留，r20_replay.py / stop-verification-gate.py 无需改动；hooks v5.8 保持
- **未纳入项及理由**（防回潮）：logprob 分布期望（模型层无 logprob API，理念≈重复评估）、Best-of-N 自验证（审查路由/codex 跨模型复核已覆盖）、prefix-cache+记账（工程实现细节非方法论）
- **版本一致性**：CLAUDE.md / SPEC.md / MANIFEST / README / docs-README / SYNC_GUIDE / hooks-README / gate_messages 全量 v11.3.5
- **DSH 同步（手工对齐协议）**：`~/.dsh/AGENTS.md` v1.3.2→v1.3.3（合并源指针 v11.3.2→**v11.3.5**，顺带修复 v11.3.3/11.3.4 滞后；④验证行 + 铁律 R7/R20 行 + 会话终验模板证据行）+ `~/.dsh/skills/verification-before-completion/SKILL.md`（同源小节，DSH 简化版）；SYNC_GUIDE DSH 适配层登记 v1.3.3↔v11.3.5
- **SSOT**：`skills/verification-before-completion/SKILL.md`（融合正文）+ `docs/LLM_AS_A_VERIFIER_SYNC.md`（决策记录）+ `CLAUDE.md`（R20 行）+ `rules/CORE.md`（R20 段）

## v11.3.4 变更摘要（2026-08-19，门控强化 + 初次修改验收）

- **全局加载**：`hooks/_lib/gate_messages.md` 四段改为短指针（完整清单只在 skill），降低会话注入体积。L0 R20 缩为指针；Cursor `CURSOR-EDITOR.mdc` 写明 Stop 用 `followup_message` 等效硬门。
- **初次修改验收门**：每个文件首次成功编辑后注入五维核对。核对范围 = 该文件 + blast-radius **全部相关项**（禁止只验当前文件）。Claude 并入 `post-edit-verify-tracker.py`；Cursor `first_edit_verify.py`。`maintenance_hints` 扩展到业务仓库。
- **R20 反空模板**：共享 `hooks/_lib/r20_replay.py`。漏改须含文档/无文档影响/路径；原功能须含证据/测试/冒烟；满足不可为省略号。Claude Stop 与 Cursor stop 共用。
- **Cursor Stop 对齐**：`verification_stop.py` 在未验证或 R20 不合格时 `followup_message` 续轮；`loop_limit` 对齐 `max_blocks`；`r20_capture.py` 在 afterAgentResponse 记录合格终验。`guard-config` `enforce_mode=followup`；已部署的 `soft` 自动映射为 `followup`（仅 `off` 关闭）。
- **SSOT**：`hooks/_lib/gate_messages.md` + `r20_replay.py` + `skills/verification-before-completion`（场景 G）+ `config/quality_gates.json`
- **核对范围**：五维/R20 覆盖 blast-radius **全部相关项**（文档/INDEX/命令/测试/同类引用），禁止只验已编辑文件；门控文案、场景 G、CORE 反模式、`/verify`、GOVERNANCE R20 口径已对齐。

## v11.3.3 变更摘要（2026-08-16，R20 文档一致 + 加载口径对齐）

- **铁律 R20**：完成后「漏改」显式包含——修改后文件/配置必须与文档/备注保持一致（README/SPEC/CHANGELOG/INDEX/MANIFEST/frontmatter/注释）。不新增 Stop 硬门字段（仍检满足/遗漏/错改/漏改/原功能）；模板增场景 F。L0：`CLAUDE.md` + `rules/CORE.md`；模板 SSOT：`skills/verification-before-completion`；详参：`rules/GOVERNANCE.md`；双端注入：`hooks/_lib/gate_messages.md`
- **全局加载**：统一 L0–L3。SPEC 加载表去掉历史 L4 行，L2 不再误列 `subagent-driven-development`（v10.15 起为 L3 显式触发）；`using-superpowers` 去掉「CLAUDE.md 细分 L4」过时口径并补全 L1 四技能；`validate_config.py` V15 文案 L0–L3，V4 增检关键词 `文档/备注`
- **同步**：sync.ps1 刷新 Cursor plugin / qoder-cn / trae-cn / workbuddy；DSH 无工具链变更，映射仍 v1.2.x↔v11.3.2（不强制手工对齐）
- **SSOT**：`CLAUDE.md`（R20 + L2 列）+ `rules/CORE.md` + `SPEC.md`（加载表）+ `MANIFEST.yaml` loading_tiers

## v11.3.2 变更摘要（2026-08-15，R20 逐条回放强化）

- **铁律 R20 强化（A 方案）**：改前优先成熟方案或已有全局通用处理（禁止为单编辑器/单场景发明特例）；完成后按原始要求**逐条回放**（禁止把实现重做一遍），清单扩为满足/遗漏/错改/漏改/原功能。非功能变更「原功能」必须写「保持」并指向测试或冒烟证据。L0：`CLAUDE.md`（workbuddy 短句自洽）+ `rules/CORE.md` 两段正文；模板 SSOT：`skills/verification-before-completion`；详参指针：`rules/GOVERNANCE.md`；双端注入：`hooks/_lib/gate_messages.md`；Claude Stop 硬门增检 `漏改`+`原功能`（`test_r20_replay.py`）。不新建规则文件、不写入 CURSOR-EDITOR.mdc
- **校验**：`validate_config.py` V4 断言 CLAUDE.md 与 CORE/verification 含 `漏改`/`原功能`，防缩回三字段
- **同步**：sync.ps1 刷新 Cursor plugin / qoder-cn / trae-cn / workbuddy；DSH 映射 v1.2.x↔v11.3.2（手工，非 sync）
- **SSOT**：`CLAUDE.md`（R20）+ `rules/CORE.md` + `skills/verification-before-completion/SKILL.md`（模板）+ `hooks/stop-verification-gate.py`

## v11.3.1 变更摘要（2026-08-14，多端一致性修复）

- **版本串/计数/残留引用对齐 SSOT**：MANIFEST/SPEC/CLAUDE/README/docs-README/package.json 统一 v11.3.1（docs-README 原错标 v11.1.0、package.json 原 11.1.1）；README catalog 计数 101+43+15 → 107+48+15（对齐 `catalog/INDEX.md`）；编辑器口径统一 `config/sync-manifest.json` 7 编辑器（qoder/trae/codearts 保留待装、home 缺席自动跳过）
- **残留引用修复**：settings.json 注释删除失效 sync-tools.ps1 说明（settings.json 永不同步编辑器）；`scripts/search-github-tools.ps1` → sync.ps1；settings.json env 移除 `CLAUDE_CODE_AUTO_COMPACT_WINDOW`（validate_config V17；`autoCompactWindow` 已等效）
- **安全清理**：`settings.json.bak_20260812_231253`（含 API token）移出 git 跟踪 → `backups/`；`.gitignore` 增 `settings.json.bak_*` 锚定；git 历史保留（提醒轮换 kimi key）
- **遗留清理**：移除已并入 main 的 worktree `.claude/worktrees/mcp-configs-sync` 及其分支（未提交 diff 快照备份至 `backups/`）
- **DSH 消费方登记**：`docs/SYNC_GUIDE.md` 增「DSH 适配层」小节 + `MANIFEST.yaml` sync_targets 注记；`~/.dsh/AGENTS.md` 对齐 v11.3.1（v1.0.0 → v1.1.0）
- **同步**：sync.ps1 -All 重同步四编辑器（Cursor plugin / qoder-cn / trae-cn / workbuddy 漂移清零），check.ps1 复检
- **SSOT**：`config/sync-manifest.json`（编辑器清单）+ `catalog/INDEX.md`（catalog 计数）+ 本文件

## v11.3.0 变更摘要（2026-08-14，会话终验 R20 + Python MCP 修复）

- **铁律 R20 会话终验**：全部任务完成后必须对照用户原始请求输出满足/遗漏/错改清单（不是把任务重做一遍）。L0：`CLAUDE.md` + `rules/CORE.md`；L2：`verification-before-completion`；Cursor 软提醒：`hooks/_lib/gate_messages.md` 第 8 条；Claude Stop 硬门：`stop-verification-gate.py` 检测标记（含纯文档编辑）。`quality_gates.json` 增 `require_requirements_replay`
- **AGENTS.md 缺口补全**：CORE 工程原则点名 KISS + SOLID 思想；GOVERNANCE 操作化 2–3 句。不新建规则文件（`global_rules_max: 10`），不覆盖 `rules/AGENTS.md`
- **Python 系 MCP 修复（不同步 mcp.json）**：根因是 uv 的 CPython 3.13.11 安装残缺（无 `Lib/encodings`），导致 serena / uvx CRG / aider-repo-map 全部 `encodings` 崩溃。已重装完整 3.13、serena 改钉 3.12、RepoMapper venv 重建；新增 `scripts/python-mcp.ps1` 清 PYTHONHOME。Cursor / Claude / Qoder 的 `mcp.json` **手工**对齐（github 保持本地 stdio；Qoder 去掉常驻 chrome-devtools/fs）。`sync.ps1` 仍永不同步 MCP；`check.ps1` 增加断言
- **SSOT**：`CLAUDE.md`（R20）+ `rules/CORE.md` + `hooks/stop-verification-gate.py` + 各编辑器自有 `mcp.json`

## v11.2.0 变更摘要（2026-08-14，工程原则整合 + pwsh 7 优先）

- **AGENTS.md 工程原则整合**：`d:\download\AGENTS.md` 18 规则去重后 6 条增量（第一性原理/YAGNI/删除过时优先于兼容层/依赖克制三件套/长期可维护优先/简单方案不主动升级）分层注入 —— 骨架进 `rules/CORE.md` 新增「工程原则」节 + 优先级第 5 条（L0 alwaysApply），详参进 `rules/GOVERNANCE.md` 最佳实践详参章新增「工程决策原则」小节；不新建规则文件（守 `global_rules_max: 10`），不覆盖 `rules/AGENTS.md`（同名不同义：现有=多Agent编排路由）
- **PowerShell 7 优先规则**：CLAUDE.md R9 从纯负面禁令升级为「Windows 终端优先 pwsh（PS7+ 稳定版，避免 PS5.1 异常）」；CORE.md 工作原则节同步；脚本注释示例 pwsh 化（sync.ps1/scripts/README.md/docs/SYNC_GUIDE.md/check.ps1），保留 `#Requires -Version 5.1` 兼容与 powershell 回退说明；Qoder MCP 启动脚本（chrome-devtools/playwright/context7-mcp.ps1）powershell.exe 用法为刻意兼容修复，明确豁免
- **SSOT**：`CLAUDE.md`（R9）+ `rules/CORE.md`（工程原则节）+ `rules/GOVERNANCE.md`（工程决策原则详参）

## v11.1.1 变更摘要（2026-08-13，问题指纹判定重构）

- **`hooks/_lib/issue_state.py` 重构（hooks v5.7）**：原「同问题重复修改」判定为特征集 SHA1 精确匹配，粗糙/不准——六个根因：①精确哈希无相似度概念（换措辞即漏检）②中文无分词、整段连续中文当单 token（中文漏报主因）③「还是不行」类零信息追问独立成桶且同 cwd 共桶（跨问题误报主因）④cwd 大小写/斜杠形态不归一（CC↔Cursor 跨端识别失效）⑤top-8 词频在短 prompt 下按字典序截断致指纹抖动 ⑥resolved 终态化、回归不升级。重构为：**分层特征**（strong=归一化路径/异常名/错误码/代码符号/反引号片段，weak=英文词+**中文字符 bigram**）+ **加权相似匹配**（strong=overlap 系数 0.6 + weak=Jaccard 0.4，`similarity_threshold` 默认 0.5，纯弱信号自动抬至 ≥0.6）+ 精确 key 短路；**泛化追问续接**（短+含错误词+无强信号 → 续接同会话 2h 内最近条目，不建新桶）；**cwd 归一化**（小写/正斜杠/去尾分隔符）；**resolved 回归升级**（解决后连续命中 ≥2 → 撤销 resolved + 回归硬提醒 build_regression_message）；状态条目新增 features/cwd/resolved_hits 字段（旧条目兼容，仅精确匹配 30 天老化；条目上限 300 防扫描膨胀）。消费者 API 零改动（CC/Cursor/stop-verification-gate 三方签名不变；Cursor 经 import_claude_lib 直读源 lib 即时生效，无需重部署）。配置 `similarity_threshold` 三处显式化（quality_gates.json / guard-config 模板+部署）。**验证**：新增 `hooks/tests/test_issue_state.py` 21 用例全过（六根因逐项覆盖 + 旧格式兼容 + 防抖 + compact 轻提示）；双端 e2e 实跑（CC launcher 链路 + Cursor 部署 hook 链路，中文改写跨会话均正确命中）；状态文件清理测试残渣后重置

## v11.1.0 变更摘要（2026-08-13，多编辑器恢复 + 全局去重）

- **多编辑器同步恢复（sync v20.0，1+N）**：按用户决策（2026-08-13）在 v19 架构上恢复 qoder-cn / trae-cn / workbuddy 落点——**未回滚** v18.4 旧脚本；编辑器清单入 `config/sync-manifest.json` **editors 段**（home/rules_channel/rules_ext/root_index/special，home 缺席自动跳过，qoder/trae/codearts 定义保留待装）；`sync.ps1` 新增通用编辑器循环 + 参数化 `Deploy-EditorRules`（实体复制 + **`.claude-managed` 台账**孤儿清除——只删自己管理过的条目，编辑器目录内用户自有规则免疫）；落点 = qoder-cn 根 6 软链 + `rules/*.mdc`、trae-cn 根 6 软链 + `user_rules/*.md`、workbuddy 仅 `CLAUDE.md`+`skills/` 联接（SOUL/USER/IDENTITY/BOOTSTRAP 禁触，跳根索引）；`check.ps1` S3 **反转**为 managed 白名单校验（缺失落点才告警，`enabled=false` 反向扫残留）；`impact_sync.py` 规则漂移检测覆盖多编辑器（`_editor_rule_channels()` 读 manifest）；`fix.ps1 $ALL_EDITORS` 与 `test-sync-dedup.ps1`（+编辑器通道去重与用户自有规则存活断言）同步扩展；TRAE R19 守卫（AppData hooks_env 副本，2026-08-13 核验与源逐字一致）独立于同步链保留，`hooks/README.md` 修正其真实路径
- **全局去重（零行为变更）**：计数/分级漂移清零——README 目录表 45/25/12→36/16/10、`skills/SKILL.md` 重写为指针壳（原 P0/Workflow/扩展表与 INDEX 双写且含 7 个已降级技能、总计 39 等漂移）、`skills-INDEX.md` L2 (7)→(5) 且 TDD/SDD 按 frontmatter L3 归位、L3 (25)→(27)、`rules/AGENTS.md`「补全 3」→「补全 2 + 跨模型 1」；断链修复——deep-research skill/命令的 `user-crawl`→`firecrawl`、Exa「optional-dev 按需」→「常驻 .mcp.json」、`hooks/README.md` `_deprecated/` 路径改已删注记；**四命令薄壳化**（路由不变）——`/review`（51 行审查路由收敛指针 `rules/AGENTS.md`）、`/execute`（→`skills/executing-plans`）、`/propose`（目录结构收敛 `rules/OPENSPEC.md`，保留独有 proposal 模板）、`/deep-research`（三档分级表收敛 skill）；低风险项——`rules/MCP.md` 标注 collab.json 仅声明无 merge 体、`validate_config.py` V11 补漏登记 `pre-userprompt-issue-tracker` 并把 4 个保留未注册 hook 拆为 optional 存在性检查（16 注册 + 4 保留精确对齐 settings.json）、SPEC GSD 行 context-engineering 消歧（能力名非已删 skill）
- **SSOT**：`config/sync-manifest.json`（root_files + plugin_rule_sources + **editors**）；技能清单 SSOT = `skills-INDEX.md`（`skills/SKILL.md` 降为指针壳）

## v11.0.0 变更摘要（2026-08-12，深度重构）

> 计划：`claude_配置_v11_深度重构.plan`（Phase 0–6）；基线 commit 382a5ee。

- **Phase 1 无损清理**：删临时脚本/日志/test-results、`hooks/_archive` + `hooks/_deprecated`、`scripts/cbm-index.ps1`；`experiences/` 归档至 `docs/archive/experiences/`（学习产物统一 claude-mem observation）；版本串/INDEX 漂移修复
- **Phase 2 技能与 Agent 收敛**：skills 45→36（office-hours / instinct-learning / onboarding-guide / claude-to-deerflow / browser-qa / taste-memory 降级 catalog；context-engineering 删除并入 rules/CONTEXT；frontend-refactor-proposer 并入 code-refactoring；writing-skills 并入 skill-creator）；agents 25→16（cso→security-reviewer 深度模式；release-engineer→skills/ship；product-manager 六问→catalog office-hours；design-engineer→skills/design-pipeline；design-shotgun / pair-agent / ios-specialist / land-and-deploy / performance-engineer 降级 catalog）；superpowers 系 13 技能确认本地深度定制（相似度<10%）保留权威
- **Phase 3 治理文档重构**：`CLAUDE-ROUTER.mdc` + `docs/RUNTIME_PLAYBOOK.md` + `agent.yaml` 三文件并入 —— 路由/决策树进 `CLAUDE.md`（唯一 L0 入口）、harness 清单进 `MANIFEST.yaml`、auto-compact 表进 `rules/CONTEXT.md`、双平台工具对照进 `rules/MCP.md`；根文件 8→6；rules 12→10（DESIGN 并入 FRONTEND 设计系统节、BESTPRACTICE 并入 GOVERNANCE 最佳实践详参章）；命令薄壳化（/verify /compact /ship /autoplan 正文迁对应 skill）；SPEC 变更史外置本文件；Cursor 插件 L0 承载改 `00-CLAUDE.mdc`
- **Phase 4 同步链双端重构（sync v19.0）**：目标收敛为仅 Cursor（Claude Code 原生读 `~/.claude` 零同步）——删除 qoder/trae(-cn)/codearts/workbuddy 分支、`sync.sh`（Linux/macOS，v2.3 止）、`templates/cursor-claude-config-plugin/` 镜像层（规则三重持有→双份：SSOT + plugin 实体副本，插件直接从 SSOT 生成含孤儿清除）；**常量单源** `config/sync-manifest.json`（root_files + plugin_rule_sources，`sync.ps1`/`check.ps1`/`impact_sync.py` 三消费方统一，impact_sync 带内置回退）；`check.ps1` S3 重写为 Cursor 专项校验 + 旧编辑器残留链扫描（WorkBuddy/CodeArts 检查段与 `Get-EditorSettingsPath` 移除）；`fix.ps1 $ALL_EDITORS` 收敛为 cursor（launcher 内嵌探测串属运行时防御保留）；`test-sync-dedup.ps1` 由三落点改两落点；`docs/SYNC_GUIDE.md` 重写为 v19.0 双端版；旧编辑器 39 条残留软链/联接（qoder-cn/trae-cn/workbuddy）经用户确认全量清除
- **Phase 5 codegraph v1.5 自动同步接管 + hooks 退役（hooks v5.6，guard 1.2.0）**：确认 v1.5 三层保鲜（原生 OS watcher 300ms 静默窗 / 陈旧标注 / connect-time 对账）后**双侧退役 kg sync hook**——CC 侧 `post-codegraph-sync`（PostToolUse ×2 组）+ `stop-knowledge-graph-sync`（Stop）注册与脚本删除（settings.json 23→20 注册、hooks 18→16 激活，快照 `hooks.snippet.json` 同步刷新）；Guard 侧 `knowledge_graph_sync_hook.py`（afterFileEdit + stop）与 `_lib/knowledge_graph_sync.py` 共享库删除，`guard-config.json` knowledge_graph 配置节裁撤；`sync.ps1` 尾部图谱刷新块移除；**实测**：删除 4 文件后 `codegraph sync` 一次对账清净（Removed 4 / 638ms），watcher 管改动、删除靠重连对账（研究卡已记录）；**余下 16 hook 原生化审计**：三门控（分类/影响/验证）、bash-guard、RTK、secret-detector、issue-tracker 等均无 Claude Code 原生替身，全部保留；4 个未注册 hook（tmux/loop/suggest-compact/context-monitor）维持文件保留不注册
- **SSOT**：`CLAUDE.md`（路由+五阶段+铁律）+ `MANIFEST.yaml`（归属+harness）+ `config/sync-manifest.json`（同步常量）+ `skills/task-triage/SKILL.md`（判定）+ 本文件（变更史）

## v10.17.0 变更摘要（2026-08-12）

配置精简去重 + 执行层硬化。三个长期症状（同问题重复处理 / 关联文件遗漏 / 改完影响其他功能）此前只有文字提示、没有机械拦截，本版把它们逐条落到 hook 上。

- **MCP 收敛 9 项三层**：本地代码（codegraph / code-review-graph / aider-repo-map / serena）+ 远端探索（github / grep）+ Web 文档（exa / context7 / firecrawl）。`chrome-devtools`、`fs` 从常驻降级为按需 profile（`mcp-configs/debug.json`、`mcp-configs/fsaccess.json`）——`fs` 全盘可写正是绕过验证追踪的通道之一。codegraph 1.5.0 / firecrawl 3.23.9 / exa 3.4.0 补版本钉扎（R14）。新增本地代码四工具分工表（`rules/MCP.md`、`docs/TOOL_MATCHING_GUIDE.md`）
- **判定逻辑单源化**：SSOT 唯一在 `skills/task-triage/SKILL.md`；下游（CLAUDE-ROUTER / skills-INDEX / RUNTIME_PLAYBOOK / using-superpowers）要么写全六条判定条件，要么只写指针，消除「两条缩写」漂移；非简单路径补回被整条跳过的 grill；五阶段图改 TDD/SDD 显式触发
- **C1 重复处理**：指纹算法与状态双端共用 `hooks/_lib/issue_state.py`，单一状态文件 `~/.claude/.state/issue-tracker.json`（此前 Claude 与 Cursor 各写各的，跨编辑器互不可见）；`stop-verification-gate` 验证通过时置 `resolved=true`，激活此前无人写入的轻提示死分支
- **C2 遗漏**：影响门从「每会话一次」改为「每文件首次编辑」双端注入；Stop 门新增 `git status --porcelain` 与 `edited_files` 交叉核查，堵住 MCP / Bash 重定向写入的绕过通道
- **C3 回归**：`settings.json` 与 Cursor `hooks.json` 的 matcher 补 `mcp__serena__.`_ / `mcp**fs**._`（必须带 `.\*`，裸名永不触发）；写工具识别与路径解析统一到 `hooks/\_lib/tool_paths.py`；Stop 门新增非功能变更的回归测试证据校验
- **同步链修复（sync v18.4）**：`$L0_ROOT_ITEMS` 补齐 SPEC / MANIFEST / 三个 INDEX / agent.yaml / CLAUDE-ROUTER.mdc，并从「仅 Cursor」放开到**除 workbuddy 外的所有编辑器**——总纲链要求 Agent 按编辑器相对路径 Read 这些文件，v18.3 的收窄让 qoder / trae / codearts 断链；集合在 `sync.ps1` / `sync.sh`(v2.3) / `check.ps1` / `impact_sync.SYNC_FILES` 四处统一（`agent.yaml` 此前只在其中两处）。`impact_sync.rules_out_of_sync()` 改查 plugin 路径并比对内容哈希（此前查 `~/.cursor/rules/` 且比 mtime，是每次会话「过期规则」误报的根因，实测规则无漂移）；guard 1.1.9
- **结构整备**：MANIFEST excludes 中的已移除组件加注说明；`deep-research` split-brain 消歧为「skills/ 权威、catalog/ 变体」；新增 `catalog/INDEX.md`（101 skills + 43 agents + 15 rules 一页式清单 + 7 个同名项消歧表）；agent.yaml 补注册 issue-tracker hook 与 `/sync` 命令；`templates/claude-settings/hooks.snippet.json` 让被 gitignore 的 hook 注册可复现；版本串统一 v10.17.0 / sync v18.4
- **仓库瘦身与 .gitignore 归位**：过程制品（`spec/`、`docs/superpowers/plans/`）移出版本库只留本地最近一次；删除 v10.5/v10.5.1 设计、v10.10 计划、`usage-audit-v10.6.md`、`research/archive/` 与 3 个一次性脚本（`migrate-from-legacy.py` 经核查是 catalog 安装工具、被 10 处文档引用，保留）。`.gitignore` 修三处误伤：`.cursor/` 整目录忽略曾吞掉 5 个 opsx 命令与 5 个 openspec 技能、`*.txt` 曾吞掉 8 份 `skills/*/LICENSE.txt` 与 `templates/cursor-user-rules-snippet.txt`、`config.json` 无锚点会命中任意层级
- **SSOT**：`.mcp.json`（MCP）+ `skills/task-triage/SKILL.md`（判定）+ `hooks/_lib/issue_state.py`（重复追踪）+ `hooks/_lib/tool_paths.py`（写工具识别）+ `hooks/_lib/gate_messages.md`（门控文本）+ `config/quality_gates.json`（门控配置）

## v10.15.0 变更摘要（2026-08-12）

- **MCP 11 项三层架构**：github 启用官方远端（Bearer `GITHUB_TOKEN`）；fs 启用全盘符（C:/D:/E:）；exa 补 `EXA_API_KEY`；chrome-devtools 保持 `@latest`（R14 例外，用户决策）；`_comment` 重写如实描述
- **TDD/SDD 显式触发**：`CLAUDE.md` SDD+TDD 行改为「仅用户明确要求时启用」；task-triage / skills-INDEX / SPEC / gate_messages 同步
- **问题指纹追踪（新 hook）**：`pre-userprompt-issue-tracker.py`（UserPromptSubmit，永不阻断）— 同问题重复出现时注入「先查上轮结论禁止重做」；推翻 v10.13「不做计数器」决策；状态 `~/.claude/.state/issue-tracker.json`；Cursor 端 `issue_tracker.py`（guard 1.1.8）
- **验证门补强**：残留引用检测从全量档专属移为任何修改必须（两档同强制）；新增「非功能变更回归保持」核验；疑难项 grill 前置在分类门/影响门文本中醒目标注
- **配置文档一致性**：`.mcp.json` 为唯一事实源；mcp/servers.json、mcp/README.md、docs/TOOL_MATCHING_GUIDE.md、docs/CURSOR_MCP_PROFILE.md、rules/MCP.md、mcp-configs/\*、templates/cursor-guard/mcp-recommended.json 全量同步至 v10.15
- **SSOT**：`.mcp.json`（MCP）+ `hooks/pre-userprompt-issue-tracker.py`（重复追踪）+ `hooks/_lib/gate_messages.md`（门控文本）+ `config/quality_gates.json`（issue_tracker 配置节）

## v10.13.0 变更摘要（2026-08-01）

- **Phase0 前置盘点**：分类前强制盘点已知文件/工具/记忆/成功标准；未盘点不得宣称简单
- **持续处理 = 执行升档**：attempt≥2 / 首轮未解决 → verify_tier=全量 **且** 执行升档非简单（不再停留简单旁路）
- **一次改完**：简单路径仅 attempt=1；清单膨胀>2 立即执行升档；禁止多轮简单旁路
- **模型档映射表**：frontier/mid/light 典型模型对照，防虚报；设计 doc → `spec/task-difficulty-precision/design.md`
- **SSOT**：`skills/task-triage`；verification / gate_messages / CLAUDE / ROUTER / using-superpowers 短引用对齐

## v10.12.0 变更摘要（2026-08-01）

- **简单判定放宽计数**：关联需改文件 ≤2（仅 Edit 逻辑源；只读/sync 镜像不计）+ 白名单 + 六维全低 + 模型匹配低
- **六维**：原五维 + ⑥模型匹配（frontier/mid/light 自报，防预期过高/过低）
- **全任务强制验证**：删除「轻量验证」旁路措辞；verify_tier=比例|全量；持续处理同一问题 → 验证升全量
- **分类输出契约**：大类 | 需改列表 | 模型档 | verify_tier | 置信度 | 成功标准
- **SSOT**：`skills/task-triage` + `verification-before-completion`；gate_messages / CLAUDE / ROUTER / using-superpowers 短引用对齐

## v10.11.0 变更摘要（2026-08-01）

- **44 仓库全量调研**：SSOT 30-repo → `44-repo-deep-research-v10.11.md`（四分类：29 已集成 + 15 新卡 + 2 不集成）；COVERAGE 矩阵 44；repos/ 新增 15 张浅层卡（anthropics-claude-code / musistudio-claude-code-router / openai-codex-plugin-cc / VoltAgent-subagents 等）
- **版本对齐运行态（非升级）**：superpowers 6.2.0 / claude-mem 13.12.4 / codegraph MCP 1.5.0（插件 autoUpdater 自动更新，installed_plugins.json 为事实源）；rtk 0.44.1 确认
- **0 新增组件**：45 skills / 25 agents / 5 MCP 常驻 保持；新仓库全部卡片/文档级记录（CCR/codex-plugin-cc/claude-code-best/SuperClaude 评估=不集成，MANIFEST reference concern）
- **agent.yaml 漂移修复**：v9.0 → v10.11.0；p0 补 task-triage（6）；mcp_loading 对齐 .mcp.json 常驻 5；global_skills_max 45
- **清理（保留最全最新一次）**：删 v10.6/v10.7 计划 + diagnostic-v10.5.2 + 7 空 backups 子目录；保留 v10.10 计划 + 44-repo SSOT
- **可选变更（用户确认）**：feature-dev 插件停用（MANIFEST 冲突落地）；codegraph CLI 0.9.7 → 1.5.0（版本分裂消除）；autoCompactWindow 按模型窗口计算=1M 保持不变；fs MCP 未选
- **validate_config warn 收敛**：V17 env 显式化（70/70/90）+ V9 deny 补 3 条 + V1 触发词消歧（9 → 1 warn）

## v10.10.0 变更摘要（2026-07-31）

- **同步链路修复**：sync.ps1 v18.2 新增 `-Scope rules|indexes|all` + `-Force`（对齐 Cursor Guard sync_runner 契约，修复自动同步必失败）；变更检测（hash 跳过）；结尾图谱刷新去 force；Guard hooks.json 移除 postToolUse 双注册；Cursor 规则通道 = local plugin 永久方案（`~/.cursor/rules` 实测不生效，不做其他通道尝试）
- **安全**：settings.json 密钥外置（环境变量）+ gitignore + 取消跟踪；sync-mode.json 删除
- **cbm 永久禁用**：全盘索引爆 CPU/内存（用户确认）；SPEC/MANIFEST/CORE/plugin 模板统一口径，codegraph 全权替代；validate_config V18 改为禁用断言
- **重复合并**：CLAUDE.md -9 行（R17 收敛 CORE SSOT 指针、场景映射表单点化、@RTK.md 指针化、/deer-flow 命令对齐）；版本/计数全串对齐 v10.10.0（skills 45、hooks 16、global_skills_max 45）
- **MCP 分层**：crawl 移 optional-dev.json 按需，常驻 5（codegraph+fetch+git+fs+time）
- **可测量性**：stop-session-summary 追加 skill/agent 真实触发日志（logs/skill-triggers.jsonl），下一轮 usage-audit 数据源

## v10.9.0 变更摘要（2026-07-31）

> ⚠️ 以下 v10.9 判定口径**已废止**（历史记录，勿据此执行）：现行为 **六维** + **关联需改≤2**，见 `skills/task-triage/SKILL.md`。

- **任务分类重构**：两大类（简单/非简单）→ 使用类型细分（文档/实现/配置值/Bug / Bug/功能/架构/配置/删除/调研），`skills/task-triage/SKILL.md` 为唯一 SSOT
- ~~**简单判定严格收窄**：单文件(=1) + 白名单 + 五维全低~~（v10.13 起改为六维 + ≤2，本行仅存档）
- ~~**Bug 归属**：可复现+根因明确+单文件 → 简单~~（现行：关联需改≤2）；其余 → triage(P0-P3)→systematic-debugging
- **双端同步**：gate_messages P0 段/CLAUDE/ROUTER/using-superpowers/MANIFEST/索引三文件/Cursor 插件副本统一 v10.9.0

## v10.7.0 变更摘要（2026-07-30）

- **配置驱动门控**：分类路由/完成验证/变更影响从模型自觉升级为 hook 强制注入（双端）。文本 SSOT `hooks/_lib/gate_messages.md`；Claude Code 新增 SessionStart/UserPromptSubmit 注册 + `pre-userprompt-verify-gate` + `pre-edit-impact-nudge`；Cursor Guard 新增 `verification_gate`/`impact_nudge`，`session_bootstrap` 注入 P0 门
- **变更影响门**：首编辑注入提醒，**永不 deny**（用户决策）；状态 `~/.claude/.state/impact-nudge.json` / Guard state，7 天清理
- **hooks 对齐**：settings.json 注册 7→15（补注册历史遗漏 5：pre-read-before-edit/pre-manifest-validator/pre-compact-state/stop-quality-gate/stop-session-summary，与 README v5.1 文档口径对齐）；Cursor Guard 15→17
- **stdin UTF-8 修复**：Windows cp936 致中文 prompt 乱码，三个新 Claude hook 与 Guard `hook_io.read_stdin` 显式 UTF-8 解码
- **Cursor 全量同步**：`sync.ps1 -All` 12 rules verbatim 部署为 .mdc + skills 44 + agents 25
- **agent.yaml 漂移清理**：mcp_loading 去 figma/puppeteer/glif 对齐 `.mcp.json`；limits 对齐实际（rules 12/skills 44/agents 25）；hooks.core 对齐注册态 15
- 详图：`docs/superpowers/plans/2026-07-30-v10.7-gate-enforcement.md`

## v10.6.0 变更摘要（2026-07-29）

- **版本对齐**：SPEC/README/skills-INDEX/MANIFEST/research-README 版本串统一（修复 10.1/10.4.0/10.5.1 漂移）
- **文档精简**：旧优化 plan（v10.5/v10.5.1）合并为 `docs/superpowers/plans/2026-07-29-v10.6-optimization.md` 后删除原件；`gsd-gaps-v10.md` 删除（已被 v10.5.2 调研吸收）；`REPO_ANALYSIS.md` 并入 `COVERAGE.md` 后删除；`reference/task-master-integration.md` 归档至 `docs/research/archive/`
- **常驻瘦身**：`rules/CORE.md` 316→≤150 行，治理详情迁 `rules/GOVERNANCE.md`（model_decision 触发）；CONTEXT/BESTPRACTICE/WORKFLOW 去除与 CORE 重复段
- **索引补全**：skills-INDEX 补登 7 技能（44 全量）；修复 2 个 SKILL.md 重复 frontmatter
- **hooks 治理**：3 个 stub 移 `_deprecated/`；`_optional/` → `_archive/`（非激活资产库）
- **使用率审计**：`docs/research/usage-audit-v10.6.md`（零触发项降级/废弃候选）
- **OpenSpec**：三处表面职责边界文档化
- 访谈决策记录：见 v10.6 优化计划文档

## v10.5.1 变更摘要（2026-07-17）

- **调研**：分层 delta 刷新 29 卡 + SSOT；上游漂移仅文档「待评估」（R14）
- **cbm**：架构/ADR/变更/跨服务 **场景强制**；未调用 → `DONE_WITH_CONCERNS`；Claude 仍不进常驻 5
- **同步**：`sync.ps1 -All` 修 CONTEXT/CORE/MCP 过期
- 详图：`spec/claude-config-integration/design-v10.5.1.md` + plan（已合并入 `docs/superpowers/plans/2026-07-29-v10.6-optimization.md`）

## v10.5 变更摘要（2026-07-17）

- **探索链**：codegraph → codebase-memory(L4) → Grep → Read
- **Cursor Guard**：`explore.enforce_mode=soft_block`（Grep/Glob）
- **MCP 常驻**：纠偏为 5（chrome-devtools 回 optional-dev）
- **调研**：28 active；上游版本漂移仅文档跟踪（R14）

## v10.2.1 变更摘要（2026-06-19 双源刷新）

- **28 repo 卡片**：+`anthropics-claude-plugins-official`（插件分发 SSOT；27→28）
- **superpowers**：本地 override 已落地（#1773 守卫 + 单 task-reviewer 对齐）；插件二进制 5.1.0 → **6.0.0** 待 Claude Code `/plugin update`（Cursor 无法下载）
- **codegraph**：F1（MCP 默认 4 工具，`codegraph_impact` 需 `CODEGRAPH_MCP_TOOLS`）+ F2（官方四元组 ~16%成本/~47%token/~58%工具调用/~22%更快；47% 为官方数字，仅补全）
- **gsd-core**：v1.5.0 stable 走 ADR 评估（暂锁 1.4.5）
- **探索链**：codegraph → Grep → Read（impact 优先 explore blast-radius）

## v10.1 变更摘要

- **27 repo 卡片**：`docs/research/repos/{slug}.md`
- **GSD 版本**：open-gsd/gsd-core **1.4.1**（MANIFEST 对齐）
- **探索链**：codegraph → Grep → Read
- **加载**：L0 四入口 + P0 五技能 L1；sync 索引模式
- **调研 SSOT**：44-repo-deep-research-v10.11.md（v10.11 内容）+ repos/

## v10.0 变更摘要

- **MANIFEST v10**：ecc_integration cherry_pick、module_resolver、thresholds 双轨、ruflo reference_only
- **OpenSpec CLI** 1.4.1 **core**（含 sync）；本地 commands 权威；`openspec init --tools cursor`
- **codegraph mandate**：V16 校验 + `codegraph index`；UA 当时 **disabled**（v10.5 已 **removed**，见 ADR-2026-07-17）
- **调研 SSOT**：仅 `docs/research/44-repo-deep-research-v10.11.md`（历史多版本已清理）
- **Firecrawl**：`scripts/firecrawl-mcp.ps1` 包装启动
- **Git 禁令**：禁止 Agent auto commit / stash（Guard v1.1.6）
- **阈值**：Cursor/Claude 70/90 + GSD 70% 逻辑断点
- **Claude Code auto-compact SSOT**：`config/model-context-windows.json` + `hooks/_lib/context_thresholds.py`；详 `rules/CONTEXT.md` §auto-compact（v11：原 RUNTIME_PLAYBOOK 已并入）

## v9.2 变更摘要

- **MCP 分层**：Claude Code `.mcp.json` 常驻 5；ops/optional-dev 迁入 `mcp-configs/`
- **Cursor 文档化**：CURSOR_MCP_PROFILE 反映用户精简后的插件/MCP 清单
- **CORE 去重**：缩短时间 API 示例；工作原则改指针
- **V15 校验**：`validate_config.py` loading_tier + disable-model-invocation
- **RUNTIME_PLAYBOOK**：五阶段 + 调研三档 + 上下文 + R16 单页 SSOT（v11 已并入 CLAUDE.md / rules）

## v9.1 变更摘要

- **L0–L4 分级加载**：P0 改称「路由集」；L1 混合（using-superpowers + change-impact 常驻）
- **slash-only**：除 L1 外全部 skills 加 `disable-model-invocation`（Cursor token 减负）
- **调研三档**：L1 Context7/Exa → L2 Exa+Firecrawl → L3 deep-research
- **User Rules 迁出**：git-workflow / pr-workflow / claude-mem-maintenance（L3）
- **spec-validation**：仅②门控；④ exclusively verification-before-completion
- **插件边界**：禁用 compound-engineering；审查走 `~/.claude/agents/` gstack
- 详图：`spec/claude-config-integration/design-v10.5.md` + plan（已合并入 `docs/superpowers/plans/2026-07-29-v10.6-optimization.md`）

## v9.0 变更摘要

- R17-R18：codegraph 探索优先 + claude-mem 记忆优先
- 新增：workstream-management / adr-management / onboarding-guide skills
- 新增：dx-reviewer agent + rules/OPENSPEC.md
- Hook 增强：GateGuard(stop-context-monitor) + codegraph 增量同步 + PreCompact 状态持久化
- P3：taste-memory / claude-to-deerflow skills + workstreams ADR-002
- 文档：`docs/REPO_ANALYSIS.md` | `spec/claude-config-integration/design-v9.md`
