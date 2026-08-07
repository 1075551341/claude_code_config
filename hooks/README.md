# Hooks 钩子系统 v5.3

> Claude Code 专用，不同步编辑器。17 注册激活 hooks + `_archive/` 非激活资产库（36）
> 五阶段×三层矩阵：骨架层(always-on) + 执行层(reactive) + 横切层(cross-cutting)
> **v5.3 变更（v10.14.0）**：① 完成验证门升级硬阻断——新增 `stop-verification-gate.py`（Stop exit 2 回灌，吸收 stop-quality-gate 全部职责并归档之）；新增 `post-edit-verify-tracker.py`（PostToolUse 状态追踪）；`pre-userprompt-verify-gate.py` 加状态触发修复关键词盲区；`config/quality_gates.json` 新增 `verification_gate` 节为硬门配置 SSOT；② 引入 code-review-graph MCP（审查/验证专用层，与 codegraph 互补）；③ Cursor Guard 同步 `verify_tracker.py` + verification_gate.py 状态触发 + guard-config.json 扩展。

## 目录结构

| 目录                 | 数量        | 用途                                                                                                                                         |
| -------------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `hooks/`             | 17 注册激活 | standard profile（settings.json 已注册）                                                                                                     |
| `hooks/`（未注册 4） | 4           | pre-tmux-reminder / pre-loop-guard / pre-suggest-compact / stop-context-monitor — 文件保留未注册：Claude Code 原生机制或 Cursor Guard 已覆盖 |
| `hooks/_lib/`        | 2           | 共享库：context_thresholds.py + gate_messages.md（门控文本 SSOT）                                                                            |
| `hooks/_archive/`    | 36          | 非激活资产库（含 stop-quality-gate.py，v10.14 职责并入 stop-verification-gate.py）                                                          |
| `hooks/_deprecated/` | 4           | 禁止启用（pre-task-planner + 3 个 stub）                                                                                                     |

---

## 17 注册激活 Hook 清单（v10.14.0 对齐运行态）

### SessionStart (1)

| Hook                         | 功能                                                          | 层   |
| ---------------------------- | ------------------------------------------------------------- | ---- |
| `session-start-bootstrap.py` | codegraph 索引检测 + **P0 分类门注入**（读 gate_messages.md） | 骨架 |

> 插件（superpowers/claude-mem）注入与本地 bootstrap 为 additive 叠加，不冲突。

### UserPromptSubmit (1)

| Hook                            | 功能                                                                                                          | 层   |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------- | ---- |
| `pre-userprompt-verify-gate.py` | **完成验证门**：prompt 命中完成类关键词 **或** 状态显示本轮有未验证编辑 → 注入 verification-before-completion 强制指令（修复关键词盲区） | 骨架 |

### PreToolUse (6)

| Hook                        | 触发                 | 功能                                                                                                                       | 层   |
| --------------------------- | -------------------- | -------------------------------------------------------------------------------------------------------------------------- | ---- |
| `pre-edit-impact-nudge.py`  | Edit/Write/MultiEdit | **变更影响门**：本会话首次编辑注入 change-impact-analysis 强制指令（状态 `~/.claude/.state/impact-nudge.json`，永不 deny） | 骨架 |
| `pre-read-before-edit.py`   | Edit/Write/MultiEdit | GSD read-before-edit 强制                                                                                                  | 执行 |
| `pre-context-injector.py`   | Task/Bash/Write/Edit | 项目 CLAUDE.md 上下文注入（每会话一次）                                                                                    | 骨架 |
| `pre-rtk-rewrite.py`        | Bash                 | RTK Shell 命令压缩改写                                                                                                     | 横切 |
| `pre-bash-guard.py`         | Bash                 | 危险命令拦截 + git --no-verify 阻止 + dep check                                                                            | 骨架 |
| `pre-manifest-validator.py` | Skill/Task           | MANIFEST 归属校验防互博                                                                                                    | 横切 |

### PostToolUse (4)

| Hook                            | 触发           | 功能                                                 | 层   |
| ------------------------------- | -------------- | ---------------------------------------------------- | ---- |
| `post-edit-format.py`           | Edit/Write     | 代码格式化 + Lint                                    | 执行 |
| `post-secret-detector.py`       | Edit/Write     | 密钥/Token/密码泄露扫描                              | 横切 |
| `post-codegraph-sync.py`        | Edit/Write     | codegraph + codebase-memory 增量同步（90s debounce） | 横切 |
| `post-edit-verify-tracker.py`   | Edit/Write/Bash/Task | 完成验证追踪器：记录编辑文件/验证命令/审查委派到状态文件，供 Stop 硬门核查 | 骨架 |

### PreCompact (1)

| Hook                   | 功能           | 层   |
| ---------------------- | -------------- | ---- |
| `pre-compact-state.py` | 压缩前状态快照 | 横切 |

### Stop (4)

| Hook                           | 功能                                                                                                          | 层   |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------- | ---- |
| `stop-verification-gate.py`    | **完成验证硬门**：变更范围轻量自动检查 + 测试证据 + 预期符合性 + eng-reviewer 委派核查 + R16 裸 except 扫描 + plan 提醒 | 骨架 |
| `stop-session-summary.py`      | 会话摘要                                                                                                      | 执行 |
| `stop-readme-updater.py`       | README 自动更新                                                                                               | 执行 |
| `stop-knowledge-graph-sync.py` | 强制刷新 codegraph + codebase-memory（忽略 debounce）                                                         | 横切 |

共享库：`hooks/_lib/knowledge_graph_sync.py`（Claude PostToolUse/Stop、Cursor Guard、`sync.ps1` 共用）。

---

## 精简说明（v2.4 → v3.0）

| 移除的 hook                    | 去向                        | 原因                       |
| ------------------------------ | --------------------------- | -------------------------- |
| `pre-dep-checker.py`           | 合并到 pre-bash-guard       | 功能重叠                   |
| `pre-git-hook-bypass-block.py` | 合并到 pre-bash-guard       | 功能重叠                   |
| `post-edit-lint.py`            | 合并到 post-edit-format     | 合并减少调用               |
| `post-test-runner.py`          | \_archive/                  | 60s 太重，改为验证阶段手动 |
| `post-doc-reminder.py`         | 合并到 stop-readme-updater  | 功能重叠                   |
| `stop-notify.py`               | \_archive/                  | 桌面通知与核心流程无关     |
| `stop-debug-checker.py`        | 合并到 stop-verification-gate（经 stop-quality-gate 中转） | 功能重叠                   |
| `stop-daily-summary.py`        | 合并到 stop-session-summary | 功能重叠                   |

**v5.1 除名（stub，48B 空操作，名实不符）**
| `post-operation-log.py` | \_deprecated/ | 空操作 stub，settings.json 注册已移除 |
| `pre-config-protection.py` | \_deprecated/ | 空操作 stub，settings.json 注册已移除 |
| `stop-pattern-extraction.py` | \_deprecated/ | 空操作 stub，未注册 |

---

## Profile 配置（ECC cherry-pick → 本地映射）

> **不安装 ECC 插件**。`LOCAL_HOOK_PROFILE` 映射本地 hook 子集（等同 ECC 概念）。

```bash
LOCAL_HOOK_PROFILE=minimal   # 仅生命周期+安全 (5 hooks)
LOCAL_HOOK_PROFILE=standard  # 默认：16 注册激活 (当前)
LOCAL_HOOK_PROFILE=strict    # 16核心 + _archive/ 安全扫描（需人工迁移注册）
```

兼容别名：`ECC_HOOK_PROFILE` 同义。

**strict 候选（位于 `_archive/`，启用前先迁移+注册）**：

- `_archive/pre-userprompt-secret-scan.py` (dwarvesf/claude-guardrails)
- `_archive/post-prompt-injection-scan.py` (lasso-security/claude-hooks)

---

## Cursor 编辑器

Claude Code hooks **不在 Cursor 内执行**（`_editor_hook_launcher.py` 快速跳过）。
Cursor Guard v1.1（`templates/cursor-guard/` + `deploy-cursor-guard.ps1`）：同步、70%/90% 压缩、codegraph 路由、shell/密钥守卫、维护提示。详见 `docs/CURSOR_EDITOR_SETUP.md` 与 `docs/SYNC_GUIDE.md` §Cursor Guard。

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

_版本：5.1 | 12 激活核心 + 35 \_archive + 4 \_deprecated_
