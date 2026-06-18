# .claude — Claude Code 全局配置

> 五柱 × 五阶段 × 三横切 | **v10.1** | 归属: `MANIFEST.yaml` | 运行时: `docs/RUNTIME_PLAYBOOK.md`

## 快速导航

| 文件 | 用途 |
|------|------|
| `CLAUDE.md` | 入口 — 优先级链 + 铁律 R1-R18 + 路由 |
| `SPEC.md` | 配置法典（v10.1） |
| `MANIFEST.yaml` | 组件唯一归属 + 防互博 |
| `agent.yaml` | harness 组件清单 |
| `.mcp.json` | MCP 常驻 5（codegraph+crawl+git+fs+time）；ops 见 `mcp-configs/` |
| `settings.json` | 运行时配置 |

## 目录

| 目录 | 内容 |
|------|------|
| `skills/` | 38 技能（→ [skills-INDEX.md](skills-INDEX.md)） |
| `agents/` | 25 智能体（→ [agents-INDEX.md](agents-INDEX.md)） |
| `rules/` | 10 规则（→ [rules-INDEX.md](rules-INDEX.md)） |
| `hooks/` | 20 生命周期钩子（含 GateGuard + codegraph sync） |
| `plugins/` | 18 已安装插件（15 启用 + 3 禁用） |
| `commands/` | 斜杠命令入口 |
| `docs/` | RUNTIME_PLAYBOOK + SYNC_GUIDE + CURSOR_MCP_PROFILE + TOOL_MATCHING_GUIDE |
| `scripts/` | sync.ps1、validate_config.py、check.ps1、test-sync-dedup.ps1 |
| `spec/` | 设计文档 + 任务计划 |
| `templates/` | OpenSpec/GSD/DESIGN 模板 |
| `catalog/` | 按需技能/智能体/规则库 |

## 五柱骨架

Superpowers(方法论) | GSD(上下文) | OpenSpec(规格) | gstack(审查) | claude-mem(记忆)

## 同步到编辑器

```powershell
powershell -ExecutionPolicy Bypass -File scripts/sync.ps1              # 索引模式
powershell -ExecutionPolicy Bypass -File scripts/sync.ps1 -Full -Force # 全量模式
```

```bash
./scripts/sync.sh sync    # Linux/macOS 索引模式
```

- 索引：7 总纲软链接 + `skills/` `agents/` 联接 + `rules/` 单文件链接
- 全量：+ `rules/*.mdc` + `skills-native/` 格式转换（Windows sync.ps1 -Full）
- 详见 [`docs/SYNC_GUIDE.md`](docs/SYNC_GUIDE.md)
- **去重策略**：同类型同名先删后写（`Remove-ScopedSameTypeTarget`）；回归 `scripts/test-sync-dedup.ps1`

hooks/commands/MCP/plugins/settings.json **不同步**（Claude Code 专用）

## v10.1

- 调研：`docs/research/repos/` 27 张卡片 + SSOT v10.1
- MANIFEST 10.1；GSD open-gsd/gsd-core **1.4.1**

## v10.0 结案

- 调研 SSOT：`docs/research/30-repo-deep-research-v10.md`
- 验证：`python scripts/validate_config.py`（16/16）
- **同步去重**：`sync.ps1` 先删同类型同名再链接/写入；回归 `scripts/test-sync-dedup.ps1`
- **体检**：`scripts/check.ps1 -Quick`
