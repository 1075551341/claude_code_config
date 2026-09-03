# Hooks 钩子系统 v5.16

> Claude Code 专用，不同步编辑器。19 注册激活 hooks
> 五阶段×三层矩阵：骨架层(always-on) + 执行层(reactive) + 横切层(cross-cutting)
> **v5.16 变更（v11.4.13）**：R19 禁自动新建/切换分支（`git_r19.py` + pre-bash-guard deny）；R15 包管理器混用警告。Cursor Guard 1.2.12。改本守卫后须刷新 TRAE AppData 副本。
> **v5.15 变更（v11.4.12）**：每轮独立审查必须全新开审；带 `resume` 的审查委派不计入 `reviews`。Cursor Guard 1.2.11。
> **v5.14 变更（v11.4.10）**：Cursor Guard 1.2.10 — 完成门不再 `followup_message`（规则驱动双审）；`verification_gate` 关闭完成门注入。Claude Stop exit 2 不变。
> **v5.13 变更（v11.4.9）**：有改动即双审；独立审查 PASS 即停，仅结论不一致才再开一轮（最多 3 轮）。计划未批准零注入（CallDynamicTool/CreatePlan）；写 plan.md 不计完成门。Windows `/X:/` 路径规范化；已有图 CLI 失败不阻断。Cursor Guard 1.2.9（sessionEnd 刷双图 timeout 45s）。
> **v5.12 变更（v11.4.8）**：非简单双审=修改→验证→审查循环最多 3 轮；`dual_pass_phase`；禁止只连审不改。`review_rounds` 仅 last_edit>last_rev 时 +1；PASS 须已有 reviews。Cursor Guard 1.2.8。
> **v5.11 变更（v11.4.7）**：Stop 完成门——计划未批准/零编辑不阻断；短 R20；非简单审查最多 3 次。Cursor Guard 1.2.7 对齐。图谱保鲜仍为 v5.10。
> **v5.10 变更（v11.4.6）**：图谱保鲜硬门——SessionStart 真正 `codegraph init|sync` + `code-review-graph build|update`（120s）；新 `pre-graph-freshness.py` PreToolUse deny 无图查询/Grep/写工具；Stop 增量刷新双图，验证全绿后 `sync.ps1 -Scope rules`；launcher 子进程超时 180s。TRAE/Qoder 用 `stop-graph-freshness.py`（未在 CC settings 注册）+ `scripts/deploy-editor-graph-hooks.ps1`。不恢复每次编辑 kg sync hook。
> **v5.9 变更（v11.4.2）**：① 新增**编码守卫双阶段** `pre-encoding-snapshot.py` + `post-encoding-check.py`（共享库 `_lib/encoding_guard.py`）——Pre 快照 BOM/EOL 签名，Post 比对差异 + 绝对检查（非法 UTF-8/U+FFFD/GBK 特征串/游离 BOM/json+py 带 BOM/严重 mixed EOL），警告注入永不阻断，注册 16→18；② `post-edit-format.py` prettier 调用补 `--end-of-line auto` 保留既有行尾（防止 prettier 默认 LF 静默改写 CRLF 配置文件）；③ `pre-bash-guard.py` 新增编码误用警告组（echo/tee/Set-Content/Out-File/heredoc 重定向写内容、powershell.exe、sed -i → 提示稳定替代）。
> **v11.3.5 注记**：无 hooks 变更（v5.8 保持）——验证准则分解评分（llm-as-a-verifier）只改 `skills/verification-before-completion` 模板正文与 `_lib/gate_messages.md` 软性短句，R20 硬门字段（满足/遗漏/错改/漏改/原功能）不变，`r20_replay.py`/`stop-verification-gate.py` 无需改动。
> **v5.8 变更（v11.3.4）**：① `post-edit-verify-tracker.py` 在记账后对每个文件首次成功编辑注入五维迷你验收（`_lib/first_edit_verify.py`）；② Stop 硬门 R20 反空模板抽到 `_lib/r20_replay.py`（漏改须含文档/无文档影响/路径，原功能须含证据/测试/冒烟）；③ 门控文本经 `_lib/gate_reader.py` 读短指针；④ Cursor Guard v1.2.1 增 `first_edit_verify` / `verification_stop`（followup）/ `r20_capture`。
> **v5.7 变更（v11.1.1）**：`_lib/issue_state.py` 判定重构——原特征集 SHA1 精确匹配粗糙/不准（中文整段单 token、泛化追问共桶误报、cwd 形态不归一跨端失效）。改为分层特征（strong=路径/错误码/异常名/符号，weak=英文词+中文 bigram）+ 加权相似度阈值（`similarity_threshold` 默认 0.5，纯弱信号自动抬高）；泛化追问（「还是不行」等）续接同会话最近条目不再独立成桶；resolved 后连续命中 ≥2 判回归自动恢复硬提醒；消费者 API 不变（record/merge_config/min_prompt_len/mark_session_resolved），Cursor 经 import_claude_lib 直读本 lib 即时生效。单测 `tests/test_issue_state.py`（21 用例）。
> **v5.6 变更（v11.0.0 Phase 5）**：退役 `post-codegraph-sync.py` 与 `stop-knowledge-graph-sync.py`（及共享库 `_lib/knowledge_graph_sync.py`、Cursor Guard `knowledge_graph_sync_hook.py`）——codegraph v1.5 MCP server 自带原生文件监听自动同步（300ms 静默窗 + 连接时追赶），本地 sync hook 冗余；注册 18→16。
> **v5.5 变更（v11.0.0）**：`_archive/`（36）与 `_deprecated/`（4）目录整体删除——非激活资产不再随仓携带，需要时从 git 历史恢复（tag `v10.17-baseline` 前）。
> **v5.4 变更（v10.17.0）**：① 补登记 `pre-userprompt-issue-tracker.py`（UserPromptSubmit 第 2 个 hook，此前漏登记）；② PostToolUse/PreToolUse matcher 增加 `mcp__serena__.*` / `mcp__fs__.*` 分组——MCP 写工具此前完全绕过验证追踪器，Stop 门因此误判「本会话没改过代码」；③ 新增共享库 `_lib/issue_state.py`（指纹与状态双端共用）与 `_lib/tool_paths.py`（写工具识别与路径解析）；④ 影响门从「每会话一次」改为「每文件首次编辑」；⑤ Stop 门新增工作树交叉核查与非功能变更回归证据校验。
> **v5.3 变更（v10.14.0）**：① 完成验证门升级硬阻断——新增 `stop-verification-gate.py`（Stop exit 2 回灌，吸收 stop-quality-gate 全部职责并归档之）；新增 `post-edit-verify-tracker.py`（PostToolUse 状态追踪）；`pre-userprompt-verify-gate.py` 加状态触发修复关键词盲区；`config/quality_gates.json` 新增 `verification_gate` 节为硬门配置 SSOT；② 引入 code-review-graph MCP（审查/验证专用层，与 codegraph 互补）；③ Cursor Guard 同步 `verify_tracker.py` + verification_gate.py 状态触发 + guard-config.json 扩展。
> **注册可复现性**：`settings.json` 含 API token 被 `.gitignore` 排除，hook 注册与 matcher 无法随仓库恢复。可跟踪快照见 `templates/claude-settings/hooks.snippet.json`（仅 hooks 段，路径占位 `{{CLAUDE_HOME}}`），恢复步骤见 `scripts/README.md`；**改动 settings.json 的 hooks 段后须同步刷新该快照**。
> **TRAE 侧**：R19 bash-guard 仍经 AppData 副本。图谱保鲜经 `~/.trae-cn/hooks.json` 直接调用 `~/.claude/hooks/*.py`（`deploy-editor-graph-hooks.ps1`），不经 launcher、不复制图谱逻辑进 AppData。

## 目录结构

| 目录                 | 数量                       | 用途                                                                                                                      |
| -------------------- | -------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `hooks/`             | 19 注册激活                | standard profile（settings.json 已注册）                                                                                  |
| `hooks/`（未注册 5） | 5                          | pre-tmux-reminder / pre-loop-guard / pre-suggest-compact / stop-context-monitor / stop-graph-freshness（TRAE/Qoder Stop） |
| `hooks/_lib/`        | 11 py + `gate_messages.md` | 上列 + `graph_freshness.py`（双图 ensure / deny / 验绿后 sync.ps1）                                                       |

---

## 19 注册激活 Hook 清单（v11.4.6 对齐运行态）

### SessionStart (1)

| Hook                         | 功能                                                                                        | 层   |
| ---------------------------- | ------------------------------------------------------------------------------------------- | ---- |
| `session-start-bootstrap.py` | **双图 ensure**（init/update）+ P0 分类门注入（读 gate_messages.md）；无图写入 blocked 状态 | 骨架 |

> 插件（superpowers/claude-mem）注入与本地 bootstrap 为 additive 叠加，不冲突。

### UserPromptSubmit (2)

| Hook                              | 功能                                                                                                                                                  | 层   |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ---- |
| `pre-userprompt-issue-tracker.py` | **重复问题追踪**：prompt 指纹命中历史记录时注入「先查上轮结论、禁止从头重做」（状态 `~/.claude/.state/issue-tracker.json`，与 Cursor 共用，永不阻断） | 横切 |
| `pre-userprompt-verify-gate.py`   | **完成验证门**：prompt 命中完成类关键词 **或** 状态显示本轮有未验证编辑 → 注入 verification-before-completion 强制指令（修复关键词盲区）              | 骨架 |

### PreToolUse (8)

| Hook                        | 触发                                                     | 功能                                                                                                                                                                                                                                                              | 层   |
| --------------------------- | -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---- |
| `pre-graph-freshness.py`    | codegraph/CRG MCP + Grep/Glob/Edit/Write/Bash            | **图谱保鲜硬门**：无图则 ensure，仍失败 deny；建图类放行                                                                                                                                                                                                          | 骨架 |
| `pre-edit-impact-nudge.py`  | Edit/Write/MultiEdit + `mcp__serena__.*` / `mcp__fs__.*` | **变更影响门**：**每个文件首次编辑**注入 change-impact-analysis 强制指令（状态 `~/.claude/.state/impact-nudge.json` 记已注入文件集，永不 deny）                                                                                                                   | 骨架 |
| `pre-read-before-edit.py`   | Edit/Write/MultiEdit                                     | GSD read-before-edit 强制                                                                                                                                                                                                                                         | 执行 |
| `pre-encoding-snapshot.py`  | Edit/Write/MultiEdit + `mcp__serena__.*` / `mcp__fs__.*` | **编码快照**（v11.4.2）：编辑前记录目标文件 BOM/EOL/大小签名 → `.state/encoding-snapshots.json`，供 Post 侧比对，永不阻断                                                                                                                                         | 横切 |
| `pre-context-injector.py`   | Task/Bash/Write/Edit                                     | 项目 CLAUDE.md 上下文注入（每会话一次）                                                                                                                                                                                                                           | 骨架 |
| `pre-rtk-rewrite.py`        | Bash                                                     | RTK Shell 命令压缩改写                                                                                                                                                                                                                                            | 横切 |
| `pre-bash-guard.py`         | Bash                                                     | 危险命令拦截 + git --no-verify 阻止 + **stash exit2 硬拦截 + commit WARN 注入**（`-C/--git-dir/--work-tree/-c` 变体防绕过）+ dep check + **编码误用警告组**（echo/tee/Set-Content/Out-File/heredoc 重定向写内容、powershell.exe、sed -i → 提示稳定替代，v11.4.2） | 骨架 |
| `pre-manifest-validator.py` | Skill/Task                                               | MANIFEST 归属校验防互博                                                                                                                                                                                                                                           | 横切 |

### PostToolUse (5)

| Hook                          | 触发                                                     | 功能                                                                                                                                                                | 层   |
| ----------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---- |
| `post-edit-format.py`         | Edit/Write                                               | 代码格式化 + Lint（prettier 补 `--end-of-line auto` 保留既有行尾）                                                                                                  | 执行 |
| `post-encoding-check.py`      | Edit/Write/MultiEdit + `mcp__serena__.*` / `mcp__fs__.*` | **编码校验**（v11.4.2）：绝对检查（非法 UTF-8/U+FFFD/GBK 特征串/游离 BOM/json+py 带 BOM/严重 mixed EOL）+ 快照比对（BOM 增删/EOL 翻转），警告注入回滚指引，永不阻断 | 横切 |
| `post-secret-detector.py`     | Edit/Write + `mcp__serena__.*` / `mcp__fs__.*`           | 密钥/Token/密码泄露扫描                                                                                                                                             | 横切 |
| `post-edit-verify-tracker.py` | Edit/Write/Bash/Task + `mcp__serena__.*` / `mcp__fs__.*` | 完成验证追踪器：记录编辑/验证/审查/**CRG 调用（crg_calls）**；**每个文件首次成功编辑后注入五维迷你验收**；MCP 写路径经 `_lib/tool_paths.py`                         | 骨架 |

> codegraph 索引同步不再走 hook：v1.5 起 MCP server 原生监听自动同步（v11 退役 `post-codegraph-sync.py`）。

### PreCompact (1)

| Hook                   | 功能           | 层   |
| ---------------------- | -------------- | ---- |
| `pre-compact-state.py` | 压缩前状态快照 | 横切 |

### Stop (3)

| Hook                        | 功能                                                                                                                   | 层   |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ---- |
| `stop-verification-gate.py` | **完成验证硬门** + 双图增量刷新 + **验证全绿后 sync.ps1**；轻量自动检查 + 测试证据 + R20 + 有图必调 CRG + 六维纠错续轮 | 骨架 |
| `stop-session-summary.py`   | 会话摘要                                                                                                               | 执行 |
| `stop-readme-updater.py`    | README 自动更新                                                                                                        | 执行 |

共享库（双端共用，Cursor Guard 经 `hook_io.import_claude_lib()` 动态导入）：

| 模块                         | 职责                                                    | 使用方                                                                                                                             |
| ---------------------------- | ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `_lib/issue_state.py`        | 问题指纹算法 + 单一状态文件 + `mark_session_resolved()` | `pre-userprompt-issue-tracker.py`、Cursor `issue_tracker.py`、`stop-verification-gate.py`                                          |
| `_lib/tool_paths.py`         | 写工具识别（原生 + MCP）与入参文件路径解析              | `post-edit-verify-tracker.py`、`pre-edit-impact-nudge.py`、Cursor `verify_tracker.py` / `impact_nudge.py` / `first_edit_verify.py` |
| `_lib/context_thresholds.py` | 70%/90% 阈值解析                                        | 压缩相关 hook                                                                                                                      |
| `_lib/gate_messages.md`      | 四门控短指针 SSOT（完整清单在 skill）                   | bootstrap / verify-gate / impact-nudge / first-edit                                                                                |
| `_lib/gate_reader.py`        | 分段读取 gate_messages.md                               | 上列注入 hook + Cursor `gate_messages.py`                                                                                          |
| `_lib/r20_replay.py`         | R20 反空模板（双端共用，禁止再复制正则）                | `stop-verification-gate.py`、Cursor `verification_stop.py` / `r20_capture.py`                                                      |
| `_lib/crg_track.py`          | CRG 工具识别、crg_calls、有图检测、六维续轮文案         | `post-edit-verify-tracker.py`、`stop-verification-gate.py`、Cursor `verify_tracker.py` / `verification_stop.py`                    |
| `_lib/graph_freshness.py`    | 双图 ensure / 工具分类 / 验绿后 sync.ps1                | bootstrap、pre-graph-freshness、stop-verification-gate、Cursor Guard、TRAE/Qoder                                                   |
| `_lib/first_edit_verify.py`  | 每文件首次编辑后五维验收（first_edit_nudged）           | `post-edit-verify-tracker.py`、Cursor `first_edit_verify.py`                                                                       |
| `_lib/encoding_guard.py`     | 编码守卫核心：快照签名/比对 + 绝对损坏检查              | `pre-encoding-snapshot.py`、`post-encoding-check.py`                                                                               |

---

## 精简说明（v2.4 → v3.0；历史记录）

> 下表「\_archive/ / \_deprecated/」目录已于 v11.0.0 删除，文件仅存于 git 历史。

| 移除的 hook                    | 去向                                                       | 原因                       |
| ------------------------------ | ---------------------------------------------------------- | -------------------------- |
| `pre-dep-checker.py`           | 合并到 pre-bash-guard                                      | 功能重叠                   |
| `pre-git-hook-bypass-block.py` | 合并到 pre-bash-guard                                      | 功能重叠                   |
| `post-edit-lint.py`            | 合并到 post-edit-format                                    | 合并减少调用               |
| `post-test-runner.py`          | \_archive/                                                 | 60s 太重，改为验证阶段手动 |
| `post-doc-reminder.py`         | 合并到 stop-readme-updater                                 | 功能重叠                   |
| `stop-notify.py`               | \_archive/                                                 | 桌面通知与核心流程无关     |
| `stop-debug-checker.py`        | 合并到 stop-verification-gate（经 stop-quality-gate 中转） | 功能重叠                   |
| `stop-daily-summary.py`        | 合并到 stop-session-summary                                | 功能重叠                   |

**v5.1 除名（stub，48B 空操作，名实不符；`_deprecated/` 目录已于 v11 删除，文件仅存 git 历史 tag `v10.17-baseline` 前）**
| `post-operation-log.py` | 已删（原 \_deprecated/） | 空操作 stub，settings.json 注册已移除 |
| `pre-config-protection.py` | 已删（原 \_deprecated/） | 空操作 stub，settings.json 注册已移除 |
| `stop-pattern-extraction.py` | 已删（原 \_deprecated/） | 空操作 stub，未注册 |

---

## Profile 配置（ECC cherry-pick → 本地映射）

> **不安装 ECC 插件**。`LOCAL_HOOK_PROFILE` 映射本地 hook 子集（等同 ECC 概念）。

```bash
LOCAL_HOOK_PROFILE=minimal   # 仅生命周期+安全 (5 hooks)
LOCAL_HOOK_PROFILE=standard  # 默认：19 注册激活 (当前)
LOCAL_HOOK_PROFILE=strict    # 16 核心 + 扩展安全扫描（v11 起归档库已删，需从 git 历史恢复后注册）
```

兼容别名：`ECC_HOOK_PROFILE` 同义。

**strict 候选（原 `_archive/`，v11 已删，git 历史可恢复）**：`pre-userprompt-secret-scan.py`（dwarvesf/claude-guardrails）、`post-prompt-injection-scan.py`（lasso-security/claude-hooks）。

---

## Cursor 编辑器

Claude Code hooks **不在 Cursor 内执行**（`_editor_hook_launcher.py` 快速跳过）。
Cursor Guard v1.2.12（`templates/cursor-guard/` + `deploy-cursor-guard.ps1`，23 hooks）：同步、70%/90% 压缩（90% 用 `additional_context` 一次、不 followup 续轮）、codegraph 路由、图谱保鲜、shell/密钥守卫、维护提示（含业务仓）、初次修改五维验收、Stop `verification_stop` **不** followup（完成门改规则驱动双审；仅图谱 refresh / 全绿 sync）；R19 `forbid_auto_branch`（ask）+ R15 包管理器混用警告；`verify_tracker` 对 resume 审查不记账。stdin 解析见 `hook_io.parse_hook_json`。详见 `docs/CURSOR_EDITOR_SETUP.md` 与 `docs/SYNC_GUIDE.md` §Cursor Guard。

## 上下文压缩（Claude Code）

| 层                    | 配置                                              | 窗口           | 阈值                    |
| --------------------- | ------------------------------------------------- | -------------- | ----------------------- |
| **模型解析**          | `config/model-context-windows.json` + `[1M]` 后缀 | 按模型动态     | —                       |
| **原生 auto-compact** | `autoCompactWindow`（SessionStart 同步）          | ≤ 模型最大     | **70%** 自动 `/compact` |
| **Hook 建议**         | `hooks/_lib/context_thresholds.py`                | 同上（封顶）   | 70% 建议 / **90% 强制** |
| **HUD 状态条**        | claude-hud plugin                                 | API 实测       | 与模型一致              |
| **Cursor Guard**      | `guard-config.json`                               | 200K（Cursor） | 70/90                   |

换模型：`python scripts/sync-compact-window.py` 或新开 Claude Code 会话。

⛔ `autoCompactWindow` 不得超过 `resolve_model_context_tokens()`；勿写死 `CLAUDE_CODE_AUTO_COMPACT_WINDOW`。

## 设计原则

1. **事件驱动**：PreToolUse(守卫) → Tool executes → PostToolUse(审计)
2. **Profile 控制**：环境变量切换，无需改配置文件
3. **平台自适应**：\_editor_hook_launcher.py 检测 Claude Code/Cursor/Devin
4. **Python 3**：跨平台 Windows/macOS/Linux

## 退出码

| 码  | 含义     |
| --- | -------- |
| 0   | 允许继续 |
| 2   | 阻止执行 |

---

_版本：5.16（v11.4.13）| 19 注册激活 + 5 未注册；R19 禁自动建/切分支；R15 包管理器混用警告；每轮独立审查必须全新开审；Cursor 完成门不 followup；Claude Stop exit 2；图谱保鲜硬门_
