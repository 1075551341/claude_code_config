# 仓库覆盖矩阵（v10.14.0）

> 日期: 2026-08-07 | SSOT: 46（29 已集成 + 15 新卡 + 2 v10.14 新增）↔ 卡片 ↔ MANIFEST concern ↔ 集成决策
> 前版: v10.11.0（2026-08-01）→ **v10.14.0** 新增 code-review-graph（integrated）+ CodeGraphContext（评估未引入）

## 覆盖率

| 指标         | 值                                                             |
| ------------ | -------------------------------------------------------------- |
| 目标仓库     | 46（44 + 2 v10.14 新增）                                       |
| Active       | **30**（28 active + 1 removed + CRG 新增 integrated）          |
| Removed      | **1**（Lum1104/Understand-Anything）                           |
| 新增卡片     | **17**（15 + CRG + CGC）                                       |
| 独立卡片     | 46                                                             |
| 运行配置目标 | **v10.14.0**（+code-review-graph MCP 审查/验证专用层）         |

## 五柱

| 仓库                  | 卡片                                                    | 最新（2026-08-01 核实）         | 状态                                         |
| --------------------- | ------------------------------------------------------- | ------------------------------- | -------------------------------------------- |
| obra/superpowers      | [obra-superpowers](repos/obra-superpowers.md)           | **6.2.0**（插件运行态）/ 256K★  | integrated（对齐运行态；本地 override 生效） |
| open-gsd/gsd-core     | [open-gsd-gsd-core](repos/open-gsd-gsd-core.md)         | 上游 v1.7.0 / 6.7K★             | integrated（钉 1.4.5；1.7 待评估）           |
| Fission-AI/OpenSpec   | [fission-ai-openspec](repos/fission-ai-openspec.md)     | 上游 v1.6.0 / 61K★              | integrated（钉 1.4.1；1.6 待评估）           |
| garrytan/gstack       | [garrytan-gstack](repos/garrytan-gstack.md)             | v0.19 / 122K★                   | integrated                                   |
| thedotmack/claude-mem | [thedotmack-claude-mem](repos/thedotmack-claude-mem.md) | **13.12.4**（插件运行态）/ 87K★ | integrated（对齐运行态）                     |

## L1 治理

| 仓库                | 卡片                                                | 状态           |
| ------------------- | --------------------------------------------------- | -------------- |
| affaan-m/ECC        | [affaan-m-ecc](repos/affaan-m-ecc.md)               | cherry_pick    |
| bytedance/deer-flow | [bytedance-deer-flow](repos/bytedance-deer-flow.md) | L3 optional    |
| ruvnet/ruflo        | [ruvnet-ruflo](repos/ruvnet-ruflo.md)               | reference_only |

## L2 优化

| 仓库                  | 卡片                                                    | 最新                   | 状态               |
| --------------------- | ------------------------------------------------------- | ---------------------- | ------------------ |
| rtk-ai/rtk            | [rtk-ai-rtk](repos/rtk-ai-rtk.md)                       | **0.44.1**（本机核实） | integrated (hook)  |
| JuliusBrussee/caveman | [juliusbrussee-caveman](repos/juliusbrussee-caveman.md) | v1.9.1                 | integrated (skill) |

## L3 洞察

| 仓库                         | 卡片                                                                  | 最新                             | 状态                                |
| ---------------------------- | --------------------------------------------------------------------- | -------------------------------- | ----------------------------------- |
| colbymchenry/codegraph       | [colbymchenry-codegraph](repos/colbymchenry-codegraph.md)             | **MCP 1.5.0 / CLI 0.9.7** / 60K★ | mandate R17 常驻                    |
| tirth8205/code-review-graph  | [tirth8205-code-review-graph](repos/tirth8205-code-review-graph.md)   | **v2.3.6** / 8.5K★               | **v10.14 integrated**（审查/验证专用层，与 codegraph 互补） |
| CodeGraphContext/CodeGraphContext | [codegraphcontext-cgc](repos/codegraphcontext-cgc.md)            | v0.5.5 / 3.2K★                   | 评估未引入（与 codegraph 重叠；备选） |
| DeusData/codebase-memory-mcp | [deusdata-codebase-memory-mcp](repos/deusdata-codebase-memory-mcp.md) | 上游 **v0.9.0** / 32K★           | **永久禁用**（全盘索引爆 CPU/内存） |
| Firecrawl + Exa              | deep-research                                                         | —                                | L3 调研双源                         |

## 技能 / 最佳实践（catalog）

| 仓库                                   | 卡片                                                               | 状态           |
| -------------------------------------- | ------------------------------------------------------------------ | -------------- |
| shanraisshan/claude-code-best-practice | [shanraisshan…](repos/shanraisshan-claude-code-best-practice.md)   | catalog        |
| mattpocock/skills                      | [mattpocock-skills](repos/mattpocock-skills.md)                    | integrated (2) |
| anthropics/skills                      | [anthropics-skills](repos/anthropics-skills.md)                    | format ref     |
| forrestchang/andrej-karpathy-skills    | [forrestchang…](repos/forrestchang-andrej-karpathy-skills.md)      | integrated     |
| 2025Emma/vibe-coding-cn                | [2025emma…](repos/2025emma-vibe-coding-cn.md)                      | CORE 吸收      |
| ComposioHQ/awesome-claude-skills       | [composiohq…](repos/composiohq-awesome-claude-skills.md)           | catalog        |
| hesreallyhim/awesome-claude-code       | [hesreallyhim…](repos/hesreallyhim-awesome-claude-code.md)         | catalog        |
| x1xhlol/system-prompts…                | [x1xhlol…](repos/x1xhlol-system-prompts-and-models.md)             | reference      |
| VoltAgent/awesome-design-md            | [voltagent…](repos/voltagent-awesome-design-md.md)                 | catalog        |
| nextlevelbuilder/ui-ux-pro-max-skill   | [nextlevelbuilder…](repos/nextlevelbuilder-ui-ux-pro-max-skill.md) | catalog        |
| Chalarangelo/30-seconds-of-code        | [chalarangelo…](repos/chalarangelo-30-seconds-of-code.md)          | catalog        |

## v10.11 新增（15 卡片）

| 仓库                                    | 卡片                                                                                        | 状态                         |
| --------------------------------------- | ------------------------------------------------------------------------------------------- | ---------------------------- |
| anthropics/claude-code                  | [anthropics-claude-code](repos/anthropics-claude-code.md)                                   | reference（官方安装路径）    |
| travisvn/awesome-claude-skills          | [travisvn-awesome-claude-skills](repos/travisvn-awesome-claude-skills.md)                   | marketplace 源（不注册）     |
| VoltAgent/awesome-claude-code-subagents | [voltagent-awesome-claude-code-subagents](repos/voltagent-awesome-claude-code-subagents.md) | catalog（勿全量装）          |
| Piebald-AI/claude-code-system-prompts   | [piebald-ai-claude-code-system-prompts](repos/piebald-ai-claude-code-system-prompts.md)     | reference                    |
| wasp-lang/open-saas                     | [wasp-lang-open-saas](repos/wasp-lang-open-saas.md)                                         | pattern ref                  |
| claude-code-best/claude-code            | [claude-code-best-claude-code](repos/claude-code-best-claude-code.md)                       | reference（**不集成**）      |
| SuperClaude-Org/SuperClaude_Framework   | [superclaude-org-superclaude-framework](repos/superclaude-org-superclaude-framework.md)     | reference（**不集成**）      |
| alirezarezvani/claude-skills            | [alirezarezvani-claude-skills](repos/alirezarezvani-claude-skills.md)                       | catalog（按需单包）          |
| Jeffallan/claude-skills                 | [jeffallan-claude-skills](repos/jeffallan-claude-skills.md)                                 | catalog（本地等价）          |
| luongnv89/claude-howto                  | [luongnv89-claude-howto](repos/luongnv89-claude-howto.md)                                   | reference                    |
| Yeachan-Heo/oh-my-claudecode            | [yeachan-heo-oh-my-claudecode](repos/yeachan-heo-oh-my-claudecode.md)                       | reference                    |
| davila7/claude-code-templates           | [davila7-claude-code-templates](repos/davila7-claude-code-templates.md)                     | reference                    |
| musistudio/claude-code-router           | [musistudio-claude-code-router](repos/musistudio-claude-code-router.md)                     | reference（**评估=不集成**） |
| openai/codex-plugin-cc                  | [openai-codex-plugin-cc](repos/openai-codex-plugin-cc.md)                                   | reference（**评估=不集成**） |
| jarrodwatts/claude-hud                  | [jarrodwatts-claude-hud](repos/jarrodwatts-claude-hud.md)                                   | reference（本地已装 v0.1.1） |

> multica-ai/andrej-karpathy-skills：forrestchang 组织迁移（同仓库双名），更新 [forrestchang 卡](repos/forrestchang-andrej-karpathy-skills.md) 指针，不新建卡。

## 工具 / 集成

| 仓库                               | 卡片                                                       | 状态                    |
| ---------------------------------- | ---------------------------------------------------------- | ----------------------- |
| anthropics/claude-plugins-official | [anthropics…](repos/anthropics-claude-plugins-official.md) | plugin source           |
| eyaltoledano/claude-task-master    | [eyaltoledano…](repos/eyaltoledano-claude-task-master.md)  | L4 optional             |
| github/github-mcp-server           | [github…](repos/github-github-mcp-server.md)               | Cursor gh plugin        |
| anthropics/claude-code-action      | [anthropics…](repos/anthropics-claude-code-action.md)      | CI reference            |
| zilliztech/claude-context          | [zilliztech…](repos/zilliztech-claude-context.md)          | archived_redirect → cbm |

## 五柱评分（原 REPO_ANALYSIS v2.4，v10.6.0 并入）

| 柱                    | 评分       | 核心价值                                     | 本地                               |
| --------------------- | ---------- | -------------------------------------------- | ---------------------------------- |
| obra/superpowers      | ⭐⭐⭐⭐⭐ | SDD+TDD、HARD-GATE、两阶段审查、原子任务     | P0 路由集 6；插件+本地优先         |
| open-gsd/gsd-core     | ⭐⭐⭐⭐⭐ | 制品优先、DAG、Trust-But-Verify、workstreams | workstream/adr/context-engineering |
| Fission-AI/OpenSpec   | ⭐⭐⭐⭐   | OPSX、delta specs、brownfield                | core CLI；verify 走本地 commands   |
| garrytan/gstack       | ⭐⭐⭐⭐⭐ | 25 agents、审查路由、品味记忆、ML 防御       | dx-reviewer、taste-memory 等       |
| thedotmack/claude-mem | ⭐⭐⭐⭐⭐ | 渐进式披露、Chroma、平台隔离                 | R18；Endless 默认关                |

## 冗余/互博（已解决）

1. codegraph vs UA — **UA removed v10.5**；双引擎 = codegraph + cbm（cbm 已禁用 v10.10）
2. codegraph vs codebase-memory — 互补（R17 符号级 vs L4 架构/ADR/变更）→ **v10.10 永久禁用 cbm**（全盘索引爆 CPU/内存）
3. claude-context vs codebase-memory — context archived_redirect → cbm
4. deer-flow vs workstream — MANIFEST excludes
5. gstack vs compound-engineering — 插件禁用
6. RTK vs caveman — 输入压缩 vs 输出压缩
7. CCR vs Kimi 直连 — v10.11 评估=不集成（常驻进程 vs 单供应商）
8. codex-plugin-cc vs codex-reviewer — 本地 codex-reviewer 主，plugin 不集成（双倍计费）
9. claude-code-best/SuperClaude vs 五柱 — 架构重叠，不集成

## 归档 lineage

| 仓库                        | 卡片                                                                | 说明                                         |
| --------------------------- | ------------------------------------------------------------------- | -------------------------------------------- |
| gsd-build/get-shit-done     | [open-gsd…](repos/open-gsd-gsd-core.md)                             | archived；后继 open-gsd/gsd-core             |
| Lum1104/Understand-Anything | [lum1104-understand-anything](repos/lum1104-understand-anything.md) | removed v10.5.1 Q4；codegraph+cbm 双引擎替代 |

## v10.5.1 决策（访谈锁定 Q1–Q8）

| #   | 决策     | 结论                               |
| --- | -------- | ---------------------------------- |
| Q1  | 交付边界 | 分层 delta；不推翻骨架             |
| Q2  | 版本     | 钉现状；上游文档「待评估」         |
| Q3  | 调研深度 | Tier-1 双源；Tier-2 gh             |
| Q5  | cbm      | 场景强制；Claude L4；Cursor P0     |
| Q6  | sync     | 多编辑器；修 CONTEXT/CORE/MCP 过期 |
| Q7  | 波次     | 三波串行                           |
| Q8  | 版本号   | **v10.5.1** patch                  |

## v10.11 决策（2026-08-01）

| #   | 决策       | 结论                                                                                               |
| --- | ---------- | -------------------------------------------------------------------------------------------------- |
| D1  | 新增集成   | **0 新增** skill/agent/MCP/plugin；全部 44 仓库走卡片/文档级记录                                   |
| D2  | 版本口径   | 插件随上游自动更新（superpowers 6.2.0 / claude-mem 13.12.4 / codegraph MCP 1.5.0），文档对齐运行态 |
| D3  | 维持钉扎   | OpenSpec 1.4.1 / GSD 1.4.5 / ECC 2.0 cherry_pick（R14，评估记录见下）                              |
| D4  | 不集成评估 | CCR（常驻进程）、codex-plugin-cc（双倍计费）、claude-code-best/SuperClaude（架构重叠）             |
| D5  | 清理       | 删旧计划 v10.6/v10.7 + diagnostic-v10.5.2 + 7 空 backups；保留 v10.10 计划 + 44-repo SSOT          |
| D6  | token      | settings.json 硬编码 token **跳过**（不修改/不记录/不同步）                                        |

## 升级评估记录（v10.11 不落地，供后续确认）

| 组件          | 上游最新 | 升级步骤                                                       | 风险                                |
| ------------- | -------- | -------------------------------------------------------------- | ----------------------------------- |
| gsd-core      | v1.7.0   | 待独立 ADR（capability registry/context_guard_mode）           | EoS/ADR 影响面大                    |
| OpenSpec      | v1.6.0   | `openspec update` 重生成 agent 指令 + 波及 sync 7 编辑器       | /opsx:explore/Stores 新特性验证     |
| ECC           | v2.1+    | 插件安装（勿复制 hooks 进 settings.json，README 警告重复执行） | 现有 cherry_pick 体系已覆盖核心能力 |
| codegraph CLI | 1.5.0    | `codegraph upgrade`（可选 V1，先备份 .codegraph/）             | R17 依赖链，需验证索引兼容          |

**无架构重开提案**（五柱边界 / ECC cherry_pick / ruflo reference_only 不变）。版本钉扎遵循 R14；插件类组件（superpowers/claude-mem）随 autoUpdater 自动更新，文档以 installed_plugins.json 为事实源。

## SSOT 链

```
repos/*.md → 44-repo-deep-research-v10.11.md（唯一全量）→ COVERAGE.md（含原 REPO_ANALYSIS 评分/互博）→ MANIFEST.yaml → SPEC.md
计划: plans/2026-07-31-v10.10-optimization.md（最新执行记录）+ plans/2026-08-01-v10.11-44repo.md
诊断: docs/diagnostic-v10.5.2.md（已删除 v10.11；内容并入 CLAUDE.md 工具调用门控）
```
