# .claude — Claude Code 全局配置

> 五柱 × 五阶段 × 三横切 | 设计: `spec/claude-config-integration/design-v6.md` | 归属: `MANIFEST.yaml`

## 快速导航

| 文件 | 用途 |
|------|------|
| `CLAUDE.md` | 入口 — 优先级链 + 铁律 + 路由 |
| `SPEC.md` | 配置法典（v7.2） |
| `MANIFEST.yaml` | 组件唯一归属 + 防互博 |
| `agent.yaml` | harness 组件清单 |
| `.mcp.json` | MCP 服务器权威源 |
| `settings.json` | 运行时配置 |

## 目录

| 目录 | 内容 |
|------|------|
| `skills/` | 28 技能（→ [skills-INDEX.md](skills-INDEX.md)） |
| `agents/` | 22 智能体（→ [agents-INDEX.md](agents-INDEX.md)） |
| `rules/` | 10 规则（→ [rules-INDEX.md](rules-INDEX.md)） |
| `hooks/` | 18 生命周期钩子 |
| `plugins/` | 18 已安装插件（15 启用 + 3 禁用） |
| `commands/` | 斜杠命令入口 |
| `docs/` | 调研 + 同步指南 |
| `scripts/` | sync.ps1 + validate_config.py |
| `spec/` | 设计文档 + 任务计划 |
| `templates/` | OpenSpec/GSD/DESIGN 模板 |
| `catalog/` | 按需技能/智能体/规则库 |

## 同步到编辑器

```powershell
powershell -ExecutionPolicy Bypass -File scripts/sync.ps1              # 索引：7总纲 + skills/agents联接 + rules单文件链接
powershell -ExecutionPolicy Bypass -File scripts/sync.ps1 -Full -Force # 全量：+ rules/skills 格式转换
```

- 索引模式：7 总纲软链接 + `skills/` `agents/` 联接 + 编辑器侧 `rules/` 单文件链接
- 全量模式：+ `rules/*.mdc` + `skills-native/` 原生副本
- 详见 [`docs/SYNC_GUIDE.md`](docs/SYNC_GUIDE.md) v14
