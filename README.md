# .claude — Claude Code 全局配置

> 五柱 × 五阶段 × 三横切 | **v11.4.20** | 归属: `MANIFEST.yaml` | 法典: `SPEC.md`（变更史: `CHANGELOG.md`）

## 快速导航

| 文件            | 用途                                                                                |
| --------------- | ----------------------------------------------------------------------------------- |
| `CLAUDE.md`     | 唯一 L0 入口 — 路由链 + P0 路由集 + L0–L3 + 五阶段 + 铁律 R1-R20（v11 并入 ROUTER） |
| `SPEC.md`       | 配置法典（v11.4.20）                                                                 |
| `MANIFEST.yaml` | 组件唯一归属 + 防互博                                                               |
| `.mcp.json`     | MCP 常驻配置；ops/optional 见 `mcp-configs/`                                        |
| `settings.json` | 运行时配置                                                                          |

## 目录

| 目录         | 内容                                                                                 |
| ------------ | ------------------------------------------------------------------------------------ |
| `skills/`    | 36 技能（→ [skills-INDEX.md](skills-INDEX.md)）                                      |
| `agents/`    | 17 智能体（→ [agents-INDEX.md](agents-INDEX.md)）                                    |
| `rules/`     | 10 规则（→ [rules-INDEX.md](rules-INDEX.md)）                                        |
| `hooks/`     | 生命周期钩子（19 注册激活 + `_lib/` 共享库；归档/弃用目录已于 v11 删除）             |
| `commands/`  | 斜杠命令入口（五阶段 + OpenSpec）                                                    |
| `docs/`      | SYNC_GUIDE + research/（调研 SSOT）+ ADR/（RUNTIME_PLAYBOOK 已并入 CLAUDE.md/rules） |
| `scripts/`   | sync.ps1、validate_config.py、check.ps1                                              |
| `templates/` | OpenSpec/GSD/DESIGN 模板                                                             |
| `catalog/`   | 按需变体库 107+48+15（→ [catalog/INDEX.md](catalog/INDEX.md)，含同名项消歧）         |

## 五柱骨架

Superpowers(方法论) | GSD(上下文) | OpenSpec(规格) | gstack(审查) | claude-mem(记忆)

## 同步（v11.1 多编辑器 1+N）

Claude Code 原生读 `~/.claude`（零同步）；编辑器侧 = Cursor + qoder-cn + trae-cn + workbuddy（qoder/trae/codearts 定义保留待装，home 缺席自动跳过）。**云端 Agent 不能写本机 `C:\Users\DELL\.claude`**（仓根即该目录）。优化合入后在本机拉取**当前优化分支**（不必等 merge 进 main），再同步编辑器：

```powershell
cd C:\Users\DELL\.claude
git fetch origin
git checkout cursor/v11-config-alignment-04a6
git pull origin cursor/v11-config-alignment-04a6
pwsh -ExecutionPolicy Bypass -File scripts/sync.ps1
pwsh -ExecutionPolicy Bypass -File scripts/deploy-editor-graph-hooks.ps1   # TRAE/Qoder hook 合并；DSH/OpenCode 便携件 sync 也会复制
python scripts/validate_config.py
pwsh -ExecutionPolicy Bypass -File scripts/check.ps1
```

若该分支已合入 `main`，可改为 `git checkout main` 后 `git pull`。

本机脱敏核验（不要把密钥贴进对话）：`settings.json` 的 `enabledPlugins` 对照 SPEC 插件表；`~/.config/opencode/AGENTS.md` 若存在则不得为指向 `CLAUDE.md` 的软链；`python scripts/validate_config.py` 与 `pwsh -ExecutionPolicy Bypass -File scripts/check.ps1`。

- 根文件 6 项软链到 cursor/qoder-cn/trae-cn；规则：Cursor=local plugin `.mdc`（唯一通道），qoder-cn=`rules/*.mdc`，trae-cn=`user_rules/*.md`（实体+台账）；workbuddy 仅 `CLAUDE.md`+`skills/` 联接
- **常量单源**：`config/sync-manifest.json`（root_files + editors + harnesses）；**去重策略**：同类型同名先删后写 + 台账孤儿清除；回归 `scripts/test-sync-dedup.ps1`
- 详见 [`docs/SYNC_GUIDE.md`](docs/SYNC_GUIDE.md)

hooks/commands/MCP/plugins/settings.json **不同步**（Claude Code 专用）

## 验证

```powershell
python scripts/validate_config.py   # 配置校验（含 R16 裸 except 扫描）
pwsh -ExecutionPolicy Bypass -File scripts/check.ps1        # 一致性体检
```

## 版本

- 当前：**v11.4.20**（2026-09-03）— 场景 load 注入 + capability 解析 + 本机优化分支落地。Guard 1.2.13；DSH 2.12 / OpenCode 1.12
- 前版：v11.4.19（2026-09-03）— L0/Stop 轮次句与规范括号句同形。Guard 1.2.13；DSH 2.12 / OpenCode 1.12
- 前版：v11.4.18（2026-09-03）— 现行操作句与 L0 轮次口径对齐（日常最多 3 轮（单任务覆盖须用户显式声明））。Guard 1.2.13；DSH 2.12 / OpenCode 1.12
- 前版：v11.4.17（2026-09-03）— 版本映射/L0 MCP 注释/本机落地 Bypass 与云端 home。Guard 1.2.13；DSH 2.12 / OpenCode 1.12
- 前版：v11.4.16（2026-09-03）— MCP 分组/调研薄壳对齐 harness；check Expand-UserHome；Guard inherit 消费并行审查者。Guard 1.2.13；DSH 2.12 / OpenCode 1.12
- 前版：v11.4.15（2026-09-03）— 审查清单闭环：harness 文案、加载器可执行、inherit 机械门。Guard 1.2.12；DSH 2.12 / OpenCode 1.12
- 前版：v11.4.14（2026-09-03）— 场景路由加载器闭环；Stop/Guard 消费审前双图与 inherit 并行门；sync.ps1 复制 harness 便携件。Guard 1.2.12；DSH 2.12 / OpenCode 1.12
- 前版：v11.4.13（2026-09-03）— 场景路由 YAML SSOT + harness 能力图；独立审前双图；inherit 并行审查（禁倍率档）。Guard 1.2.11；DSH 2.12 / OpenCode 1.12
- 前版：v11.4.12（2026-09-01）— 审查一次找齐再集中改；每轮独立审查必须全新开审（禁止 resume 上轮审查者）。Guard 1.2.11；DSH 2.12 / OpenCode 1.12
- 前版：v11.4.11（2026-09-01）— 独立审查只找问题；修改走 `change-implementer`；配置/文档/注释必须同步；验证与审查不一致立即派修改者。Guard 1.2.10；DSH 2.10 / OpenCode 1.10
- 前版：v11.4.10（2026-09-01）— Cursor 完成门不再 followup（规则驱动双审）；Claude Stop exit 2 保留；Guard 1.2.10；DSH 2.9 / OpenCode 1.9
- 前版：v11.4.9（2026-09-01）— 有改动即双审（PASS 即停，仅结论不一致才再开一轮、最多 3 轮）；计划未批准零注入（CallDynamicTool/CreatePlan）；Windows `/X:/` 路径规范化；会话起止双图 ensure/refresh；已有图 CLI 失败不阻断；Guard 1.2.9；DSH 2.8 / OpenCode 1.8
- 前版：v11.4.8（2026-08-31）— 非简单双审=修改→验证→审查循环最多 3 轮（禁止只连审不改）；Guard 1.2.8；DSH 2.7 / OpenCode 1.7
- 前版：v11.4.7（2026-08-31）— 计划未批准 / CreatePlan / 零编辑禁止 followup；短 R20；非简单双审最多 3 次；Cursor Guard 1.2.7；DSH 2.6 / OpenCode 1.6 手工对齐（sync.ps1 不覆盖 AGENTS.md）
- 前版：v11.4.6（2026-08-29）— 图谱保鲜硬门（会话 ensure 双图、无图 deny、验绿后 sync.ps1）；Guard 1.2.6；DSH 2.5 / OpenCode 1.5
- 前版：v11.4.5（2026-08-29）— MCP 分工（内置>plugin>MCP；CRG=上下文/影响面/风险/审查/PR）+ Stop 六维纠错续轮 + R20 满足行三态；DevTools/Postgres 中断启用；DSH/OpenCode 手工对齐且不改其 plugin/MCP 开关
- 前版：v11.4.3（2026-08-26）— 配置一致性修复：版本/计数漂移清零 + 触发词去重（V1 归零，`重构` 唯一归属 code-refactoring）+ 权限对齐（删 powershell allow；opencode chrome-devtools 转按需）+ 插件显式登记（claude-hud=true/exa=false 禁双挂）+ opencode 诊断探针残留清理
- 前版：v11.4.2（2026-08-26）— 防乱码编码守卫双阶段（快照+校验）+ prettier 保行尾 + 命令误用警告组
- 前版：v11.4.1（2026-08-25）— opencode 验证门修复与可观测性
- 前版：v11.4.0（2026-08-25）— IMPACT 自动登记 + 需求指纹 R20 实质比对 + 审查结论机械检测 + opencode 接入（AGENTS.md+验证门插件）+ 上游矩阵 docs/research/45 + DSH 同步 v1.3.4
- 前版：v11.3.5（2026-08-20）— 验证准则分解评分（llm-as-a-verifier：观察输出优先/准则三问/1-20 评分/重复评估/成对比较消偏/进度止损）+ DSH 同步 v1.3.3
- 前版：v11.3.4（2026-08-19）— 门控短指针 + 初次修改五维验收 + R20 反空模板 + Cursor stop followup
- 前版：v11.3.2（2026-08-15）— R20 逐条回放强化（改前成熟/全局 + 满足/遗漏/错改/漏改/原功能；非功能变更必须保持原功能）
- 前版：v11.3.1（2026-08-14）— 多端一致性修复（版本串/计数/残留引用对齐 SSOT + 四编辑器重同步 + DSH 消费方登记 + 遗留清理）
- 前版：v11.3.0（2026-08-14）— 铁律 R20 会话终验 + Python 系 MCP 修复（uv CPython 3.13 encodings；mcp.json 手工维护、sync 永不复制）
- 前版：v11.2.0（2026-08-14）— AGENTS.md 工程原则整合（CORE 工程原则节 + GOVERNANCE 工程决策详参）+ Windows 终端优先 pwsh 7+（R9 升级，Qoder MCP 脚本例外）
- 前版：v11.1.1（2026-08-13）— 问题指纹判定重构（相似匹配 + 中文 bigram + 泛化追问续接 + resolved 回归升级，单测 21 用例）
- 前版：v11.1.0（2026-08-13）— 多编辑器同步恢复 1+N（sync v20.0：Cursor + qoder-cn/trae-cn/workbuddy，清单单源 sync-manifest editors 段）+ 全局去重（计数/分级漂移、断链、四命令薄壳化）
- 前版：v11.0.0（2026-08-12，深度重构）— 治理文档 8→6 根文件 + skills 45→36 / agents 25→16 / rules 12→10 + codegraph v1.5 自动同步接管 + 变更史外置 CHANGELOG.md
- 变更史：`CHANGELOG.md`
- 调研 SSOT：`docs/research/44-repo-deep-research-v10.11.md` + `COVERAGE.md`
