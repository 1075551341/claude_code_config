# .claude — Claude Code 全局配置

> 五柱 × 五阶段 × 三横切 | **v10.12.0** | 归属: `MANIFEST.yaml` | 法典: `SPEC.md` | 运行时: `docs/RUNTIME_PLAYBOOK.md`

## 快速导航

| 文件                | 用途                                         |
| ------------------- | -------------------------------------------- |
| `CLAUDE.md`         | 入口 — 优先级链 + 铁律 R1-R19 + 路由         |
| `CLAUDE-ROUTER.mdc` | Tool-First 路由 — P0 路由集 + L0–L3 加载等级 |
| `SPEC.md`           | 配置法典（v10.12.0）                         |
| `MANIFEST.yaml`     | 组件唯一归属 + 防互博                        |
| `.mcp.json`         | MCP 常驻配置；ops/optional 见 `mcp-configs/` |
| `settings.json`     | 运行时配置                                   |

## 目录

| 目录         | 内容                                                                 |
| ------------ | -------------------------------------------------------------------- |
| `skills/`    | 45 技能（→ [skills-INDEX.md](skills-INDEX.md)）                      |
| `agents/`    | 25 智能体（→ [agents-INDEX.md](agents-INDEX.md)）                    |
| `rules/`     | 12 规则（→ [rules-INDEX.md](rules-INDEX.md)）                        |
| `hooks/`     | 生命周期钩子（激活核心 + `_archive/` 非激活资产库 + `_deprecated/`） |
| `commands/`  | 斜杠命令入口（五阶段 + OpenSpec）                                    |
| `docs/`      | RUNTIME_PLAYBOOK + SYNC_GUIDE + research/（调研 SSOT）+ ADR/         |
| `scripts/`   | sync.ps1、validate_config.py、check.ps1                              |
| `templates/` | OpenSpec/GSD/DESIGN 模板                                             |
| `catalog/`   | 按需技能/智能体/规则库                                               |

## 五柱骨架

Superpowers(方法论) | GSD(上下文) | OpenSpec(规格) | gstack(审查) | claude-mem(记忆)

## 同步到编辑器

```powershell
powershell -ExecutionPolicy Bypass -File scripts/sync.ps1          # L0 入口（推荐）
powershell -ExecutionPolicy Bypass -File scripts/sync.ps1 -Skills  # + skills/
powershell -ExecutionPolicy Bypass -File scripts/sync.ps1 -All     # + 全部 rules + agents
```

- L0：CLAUDE.md + CORE + ROUTER 链接/复制到各编辑器全局目录（Cursor 规则为实体副本）
- **去重策略**：同类型同名先删后写；回归 `scripts/test-sync-dedup.ps1`
- 详见 [`docs/SYNC_GUIDE.md`](docs/SYNC_GUIDE.md)

hooks/commands/MCP/plugins/settings.json **不同步**（Claude Code 专用）

## 验证

```powershell
python _validate_config.py        # 配置校验（含 R16 裸 except 扫描）
powershell scripts/check.ps1      # 一致性体检
```

## 版本

- 当前：**v10.12.0**（2026-08-01）— 任务判定：关联需改≤2 + 六维/模型匹配 + 全任务验证（持续处理升全量）
- 变更史：`SPEC.md` 末尾 changelog 链
- 调研 SSOT：`docs/research/44-repo-deep-research-v10.11.md` + `COVERAGE.md`
