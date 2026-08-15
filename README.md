# .claude — Claude Code 全局配置

> 五柱 × 五阶段 × 三横切 | **v11.3.2** | 归属: `MANIFEST.yaml` | 法典: `SPEC.md`（变更史: `CHANGELOG.md`）

## 快速导航

| 文件            | 用途                                                                                |
| --------------- | ----------------------------------------------------------------------------------- |
| `CLAUDE.md`     | 唯一 L0 入口 — 路由链 + P0 路由集 + L0–L3 + 五阶段 + 铁律 R1-R20（v11 并入 ROUTER） |
| `SPEC.md`       | 配置法典（v11.3.2）                                                                 |
| `MANIFEST.yaml` | 组件唯一归属 + 防互博                                                               |
| `.mcp.json`     | MCP 常驻配置；ops/optional 见 `mcp-configs/`                                        |
| `settings.json` | 运行时配置                                                                          |

## 目录

| 目录         | 内容                                                                                 |
| ------------ | ------------------------------------------------------------------------------------ |
| `skills/`    | 36 技能（→ [skills-INDEX.md](skills-INDEX.md)）                                      |
| `agents/`    | 16 智能体（→ [agents-INDEX.md](agents-INDEX.md)）                                    |
| `rules/`     | 10 规则（→ [rules-INDEX.md](rules-INDEX.md)）                                        |
| `hooks/`     | 生命周期钩子（16 注册激活 + `_lib/` 共享库；归档/弃用目录已于 v11 删除）             |
| `commands/`  | 斜杠命令入口（五阶段 + OpenSpec）                                                    |
| `docs/`      | SYNC_GUIDE + research/（调研 SSOT）+ ADR/（RUNTIME_PLAYBOOK 已并入 CLAUDE.md/rules） |
| `scripts/`   | sync.ps1、validate_config.py、check.ps1                                              |
| `templates/` | OpenSpec/GSD/DESIGN 模板                                                             |
| `catalog/`   | 按需变体库 107+48+15（→ [catalog/INDEX.md](catalog/INDEX.md)，含同名项消歧）         |

## 五柱骨架

Superpowers(方法论) | GSD(上下文) | OpenSpec(规格) | gstack(审查) | claude-mem(记忆)

## 同步（v11.1 多编辑器 1+N）

Claude Code 原生读 `~/.claude`（零同步）；编辑器侧 = Cursor + qoder-cn + trae-cn + workbuddy（qoder/trae/codearts 定义保留待装，home 缺席自动跳过）：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/sync.ps1          # 根文件 + 各编辑器规则（推荐）
powershell -ExecutionPolicy Bypass -File scripts/sync.ps1 -Skills  # + skills/
powershell -ExecutionPolicy Bypass -File scripts/sync.ps1 -All     # + agents/
```

- 根文件 6 项软链到 cursor/qoder-cn/trae-cn；规则：Cursor=local plugin `.mdc`（唯一通道），qoder-cn=`rules/*.mdc`，trae-cn=`user_rules/*.md`（实体+台账）；workbuddy 仅 `CLAUDE.md`+`skills/` 联接
- **DSH 适配层**：`~/.dsh/AGENTS.md` 静态快照（合并源=本仓 + `D:\download\AGENTS.md`，非 sync 目标，升版后手工对齐版本串；见 SYNC_GUIDE「DSH 适配层」）
- **常量单源**：`config/sync-manifest.json`（root_files + editors）；**去重策略**：同类型同名先删后写 + 台账孤儿清除；回归 `scripts/test-sync-dedup.ps1`
- 详见 [`docs/SYNC_GUIDE.md`](docs/SYNC_GUIDE.md)

hooks/commands/MCP/plugins/settings.json **不同步**（Claude Code 专用）

## 验证

```powershell
python scripts/validate_config.py   # 配置校验（含 R16 裸 except 扫描）
powershell scripts/check.ps1        # 一致性体检
```

## 版本

- 当前：**v11.3.2**（2026-08-15）— R20 逐条回放强化（改前成熟/全局 + 满足/遗漏/错改/漏改/原功能；非功能变更必须保持原功能）
- 前版：v11.3.1（2026-08-14）— 多端一致性修复（版本串/计数/残留引用对齐 SSOT + 四编辑器重同步 + DSH 消费方登记 + 遗留清理）
- 前版：v11.3.0（2026-08-14）— 铁律 R20 会话终验 + Python 系 MCP 修复（uv CPython 3.13 encodings；mcp.json 手工维护、sync 永不复制）
- 前版：v11.2.0（2026-08-14）— AGENTS.md 工程原则整合（CORE 工程原则节 + GOVERNANCE 工程决策详参）+ Windows 终端优先 pwsh 7+（R9 升级，Qoder MCP 脚本例外）
- 前版：v11.1.1（2026-08-13）— 问题指纹判定重构（相似匹配 + 中文 bigram + 泛化追问续接 + resolved 回归升级，单测 21 用例）
- 前版：v11.1.0（2026-08-13）— 多编辑器同步恢复 1+N（sync v20.0：Cursor + qoder-cn/trae-cn/workbuddy，清单单源 sync-manifest editors 段）+ 全局去重（计数/分级漂移、断链、四命令薄壳化）
- 前版：v11.0.0（2026-08-12，深度重构）— 治理文档 8→6 根文件 + skills 45→36 / agents 25→16 / rules 12→10 + codegraph v1.5 自动同步接管 + 变更史外置 CHANGELOG.md
- 变更史：`CHANGELOG.md`
- 调研 SSOT：`docs/research/44-repo-deep-research-v10.11.md` + `COVERAGE.md`
