# .claude — Claude Code 全局配置

> 五柱 × 五阶段 × 三横切 | **v12.0.1** | 归属: `MANIFEST.yaml` | 法典: `SPEC.md`（变更史: `CHANGELOG.md`）

## 快速导航

| 文件            | 用途                                                              |
| --------------- | ----------------------------------------------------------------- |
| `CLAUDE.md`     | L0 纯路由（≤120 行）                                              |
| `SPEC.md`       | 精简法典（计数引用 MANIFEST）                                     |
| `MANIFEST.yaml` | 组件归属 + harness + 计数/版本单源                                |
| `.mcp.json`     | MCP 常驻配置                                                      |
| `settings.json` | 无密钥骨架（hooks 由 snippet 生成）；密钥在 `settings.local.json` |

## 目录

| 目录         | 内容                                                  |
| ------------ | ----------------------------------------------------- |
| `skills/`    | 按需技能（→ [skills-INDEX.md](skills-INDEX.md)）      |
| `agents/`    | 智能体（→ [agents-INDEX.md](agents-INDEX.md)）        |
| `rules/`     | CORE + FRONTEND（→ [rules-INDEX.md](rules-INDEX.md)） |
| `hooks/`     | 生命周期钩子（snippet 注册 + `_lib/`）                |
| `commands/`  | 斜杠命令薄壳                                          |
| `docs/`      | SYNC_GUIDE + research/COVERAGE + ADR                  |
| `scripts/`   | sync.ps1、validate_config.py、check.ps1               |
| `templates/` | cursor-guard / claude-settings / 项目脚手架           |

## 同步（1+N）

Claude Code 原生读 `~/.claude`。编辑器：cursor / qoder-cn / trae-cn / trae。

```powershell
pwsh -ExecutionPolicy Bypass -File scripts/sync.ps1
pwsh -ExecutionPolicy Bypass -File scripts/sync.ps1 -All -DryRun
```
