# colbymchenry/codegraph v1.0.1

> 层: L3 洞察 | 置信度: 高 | 刷新: 2026-06-16

## 核心价值

- 静态代码索引；~47% token 减少
- codegraph_explore / codegraph_impact / trace 符号级快查
- R17 探索首选（先于 Grep/Read）
- MCP 集成；mandate init 策略

## 证据

- [GitHub colbymchenry/codegraph](https://github.com/colbymchenry/codegraph)
- validate_config V16 校验

## 本地映射

| MANIFEST concern | 路径 |
|------------------|------|
| codegraph | `MANIFEST.yaml` → `policy: mandate_init` |
| R17 | `rules/CORE.md`, `rules/CURSOR-EDITOR.mdc` |
| MCP | `.mcp.json` user-codegraph |
|  playbook | `docs/RUNTIME_PLAYBOOK.md` |

## 吸收决策

**采纳** — 全局 `~/.claude` index + 业务项目 mandate init。

## 互博检查

- vs UA：codegraph 主；UA disabled
- vs Grep：codegraph 首选，Grep fallback

## v10.1 增量

- v1.0.0 major：配置值脱敏、symlink 安全、R 语言索引
- v1.0.1：`codegraph daemon` 交互管理器、MCP watchdog 自愈
