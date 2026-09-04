# Hooks 钩子系统 v12

> Claude Code 专用。注册集合 SSOT = `templates/claude-settings/hooks.snippet.json`，由 `python scripts/apply-settings.py` 写入 `settings.json`。计数以 MANIFEST `harness.hooks.core` 为准。

## 机械门控

| Hook | 作用 |
| --- | --- |
| session-start-bootstrap | 双图 ensure |
| pre-graph-freshness | 无图 deny |
| pre-explore-router | R17 软门（`CLAUDE_R17_MODE=deny` 可升级） |
| pre-bash-guard / post-secret-detector | 危险命令与密钥（模式表 `_lib/shell_patterns.py` / `secret_patterns.py`） |
| pre-encoding-snapshot / post-encoding-check | 编码守卫 |
| post-edit-verify-tracker | 验证与审查记账 |
| stop-verification-gate | 有写入无新鲜独立审查 → exit 2 |
| stop-graph-freshness | 仅 TRAE/Qoder 未在 CC 注册 |

Launcher：CLI 缺失目标 hook → exit 2（`CLAUDE_HOOK_ALLOW_MISSING=1` 可放行）。Profile 变量统一 `CLAUDE_HOOK_PROFILE`。

共享库：`hooks/_lib/`（r20_replay、graph_freshness、encoding_guard、issue_state）。Cursor Guard 经 `import_claude_lib` 引用，禁止再拷贝分叉。
