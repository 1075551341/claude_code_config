# 多端图谱保鲜（v11.4.10）

便携 CLI SSOT：`graph_freshness_cli.py`（ensure / refresh / status）+ `r20_check.py`（R20 机械门，含影响范围）。
部署：`pwsh -ExecutionPolicy Bypass -File scripts/deploy-editor-graph-hooks.ps1`（TRAE/Qoder 合并 hook **并**复制 CLI / R20 检查器到 DSH/OpenCode；复制 `graph-freshness.ts` 与 `verify-gate.ts`）。
v11.4.10：Cursor 完成门不再 followup。OpenCode `verify-gate` 审查 PASS 后不再催完成令。
v11.4.9：Windows `/X:/` 路径规范化；已有图 CLI 失败不阻断；OpenCode `verify-gate` 计划文件不注入完成令；独立审查 PASS 即停。

| Harness | 开始 | 结束 | 配置 |
|---|---|---|---|
| Claude / Cursor | SessionStart hook | Stop hook | `config/quality_gates.json` `graph_freshness` |
| TRAE / Qoder | 下表 hook | Stop hook | 同上（命令指向 `~/.claude/hooks`） |
| OpenCode | plugin `ensure` **每会话一次**；`GRAPH_RULE` 注入一次 | idle `refresh` **60s 冷却** | `~/.config/opencode/graph-freshness.json` |
| DSH | agent CLI `ensure` **每会话一次**（无 hook） | 完成前 CLI `refresh` **一次** | `~/.dsh/config/graph-freshness.json` |

OpenCode / DSH **不**经 `sync.ps1` 覆盖 AGENTS.md；CLI 为各自 home 副本。

# TRAE / Qoder 图谱保鲜 hook 注册

禁止经 `_editor_hook_launcher`：launcher 在编辑器内会 skip。
命令指向 `~/.claude/hooks` 源文件，**不复制**图谱逻辑进 AppData。

部署：

```powershell
pwsh -ExecutionPolicy Bypass -File scripts/deploy-editor-graph-hooks.ps1
```

- TRAE timeout 单位：**秒**。SessionStart 退出码 2 不阻断会话 → 靠 PreToolUse deny。
- Qoder SessionStart 不可阻断 → 同样靠 PreToolUse deny。
- `~/.qoder-cn/settings.json` 若过大或是 JSONC，脚本会 **skip** 以免整文件重写。请把下面片段手工合并进 `hooks` 段。

## TRAE `~/.trae-cn/hooks.json`（追加，勿覆盖已有 bash-guard）

```json
{
  "SessionStart": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "python \"%USERPROFILE%/.claude/hooks/session-start-bootstrap.py\"",
          "timeout": 120
        }
      ]
    }
  ],
  "PreToolUse": [
    {
      "matcher": "Grep|Glob|Write|Edit|RunCommand|mcp__.*",
      "hooks": [
        {
          "type": "command",
          "command": "python \"%USERPROFILE%/.claude/hooks/pre-graph-freshness.py\"",
          "timeout": 90
        }
      ]
    }
  ],
  "Stop": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "python \"%USERPROFILE%/.claude/hooks/stop-graph-freshness.py\"",
          "timeout": 150
        }
      ]
    }
  ]
}
```

路径按本机 `~/.claude` 替换。R19 bash-guard 仍走 AppData 副本；图谱 hook **不要**复制进 AppData。

## Qoder `settings.json` 的 `hooks` 段

与上表相同事件名（SessionStart / PreToolUse / Stop），PreToolUse matcher 用 `Grep|Glob|Write|Edit|Bash|mcp__.*`。timeout 能配则配 120/90/150。
