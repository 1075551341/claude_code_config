# 仓库覆盖矩阵（v10.5.2）

> 日期: 2026-07-28 | SSOT: 28 active + 1 removed ↔ 卡片 ↔ MANIFEST concern ↔ 集成决策
> 前版: v10.5.1（2026-07-17）→ **v10.5.2 工具调用门控优化**

## 覆盖率

| 指标         | 值                                |
| ------------ | --------------------------------- |
| 目标仓库     | 28                                |
| Active       | **28**                            |
| Removed      | **0**                             |
| 独立卡片     | 28（均含 v10.5.1 delta）          |
| 运行配置目标 | **v10.5.2**（工具调用门控优化后） |

## 五柱

| 仓库                  | 卡片                                                    | 最新（gh 2026-07-17） | 状态                                        |
| --------------------- | ------------------------------------------------------- | --------------------- | ------------------------------------------- |
| obra/superpowers      | [obra-superpowers](repos/obra-superpowers.md)           | v6.1.1 / 256K★        | integrated（钉 v6.0.x 本地；升 6.1 待评估） |
| open-gsd/gsd-core     | [open-gsd-gsd-core](repos/open-gsd-gsd-core.md)         | v1.7.0 / 6.7K★        | integrated（钉 1.4.5；1.7 待评估）          |
| Fission-AI/OpenSpec   | [fission-ai-openspec](repos/fission-ai-openspec.md)     | v1.6.0 / 61K★         | integrated（钉 1.4.1；1.6 待评估）          |
| garrytan/gstack       | [garrytan-gstack](repos/garrytan-gstack.md)             | no GH release / 122K★ | integrated                                  |
| thedotmack/claude-mem | [thedotmack-claude-mem](repos/thedotmack-claude-mem.md) | v13.11.0 / 87K★       | integrated（钉 13.8.x；13.11 待评估）       |

## L1 治理

| 仓库                | 卡片                                                | 状态           |
| ------------------- | --------------------------------------------------- | -------------- |
| affaan-m/ECC        | [affaan-m-ecc](repos/affaan-m-ecc.md)               | cherry_pick    |
| bytedance/deer-flow | [bytedance-deer-flow](repos/bytedance-deer-flow.md) | L3 optional    |
| ruvnet/ruflo        | [ruvnet-ruflo](repos/ruvnet-ruflo.md)               | reference_only |

## L2 优化

| 仓库                  | 卡片                                                    | 最新          | 状态               |
| --------------------- | ------------------------------------------------------- | ------------- | ------------------ |
| rtk-ai/rtk            | [rtk-ai-rtk](repos/rtk-ai-rtk.md)                       | ~0.43/0.44-rc | integrated (hook)  |
| JuliusBrussee/caveman | [juliusbrussee-caveman](repos/juliusbrussee-caveman.md) | v1.9.1        | integrated (skill) |

## L3 洞察

| 仓库                         | 卡片                                                                  | 最新              | 状态                   |
| ---------------------------- | --------------------------------------------------------------------- | ----------------- | ---------------------- |
| colbymchenry/codegraph       | [colbymchenry-codegraph](repos/colbymchenry-codegraph.md)             | **v1.4.1** / 60K★ | mandate R17 常驻       |
| DeusData/codebase-memory-mcp | [deusdata-codebase-memory-mcp](repos/deusdata-codebase-memory-mcp.md) | **v0.9.0** / 32K★ | L4_on_demand（双引擎） |
| Firecrawl + Exa              | deep-research                                                         | —                 | L3 调研双源            |

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

## 工具 / 集成

| 仓库                               | 卡片                                                       | 状态                    |
| ---------------------------------- | ---------------------------------------------------------- | ----------------------- |
| anthropics/claude-plugins-official | [anthropics…](repos/anthropics-claude-plugins-official.md) | plugin source           |
| eyaltoledano/claude-task-master    | [eyaltoledano…](repos/eyaltoledano-claude-task-master.md)  | L4 optional             |
| github/github-mcp-server           | [github…](repos/github-github-mcp-server.md)               | Cursor gh plugin        |
| anthropics/claude-code-action      | [anthropics…](repos/anthropics-claude-code-action.md)      | CI reference            |
| zilliztech/claude-context          | [zilliztech…](repos/zilliztech-claude-context.md)          | archived_redirect → cbm |

## 五柱评分（原 REPO_ANALYSIS v2.4，v10.6.0 并入）

| 柱 | 评分 | 核心价值 | 本地 |
| --------------------- | ------ | -------------------------------------- | ------------------------------ |
| obra/superpowers | ⭐⭐⭐⭐⭐ | SDD+TDD、HARD-GATE、两阶段审查、原子任务 | P0 路由集 5；插件+本地优先 |
| open-gsd/gsd-core | ⭐⭐⭐⭐⭐ | 制品优先、DAG、Trust-But-Verify、workstreams | workstream/adr/context-engineering |
| Fission-AI/OpenSpec | ⭐⭐⭐⭐ | OPSX、delta specs、brownfield | core CLI；verify 走本地 commands |
| garrytan/gstack | ⭐⭐⭐⭐⭐ | 25 agents、审查路由、品味记忆、ML 防御 | dx-reviewer、taste-memory 等 |
| thedotmack/claude-mem | ⭐⭐⭐⭐⭐ | 渐进式披露、Chroma、平台隔离 | R18；Endless 默认关 |

## 冗余/互博（已解决）

1. codegraph vs UA — **UA removed v10.5**；双引擎 = codegraph + cbm
2. codegraph vs codebase-memory — 互补（R17 符号级 vs L4 架构/ADR/变更）
3. claude-context vs codebase-memory — context archived_redirect → cbm
4. deer-flow vs workstream — MANIFEST excludes
5. gstack vs compound-engineering — 插件禁用
6. RTK vs caveman — 输入压缩 vs 输出压缩

## 归档 lineage

| 仓库                    | 卡片                                    | 说明                             |
| ----------------------- | --------------------------------------- | -------------------------------- |
| gsd-build/get-shit-done | [open-gsd…](repos/open-gsd-gsd-core.md) | archived；后继 open-gsd/gsd-core |

## v10.5.1 决策（访谈锁定 Q1–Q8）

| #   | 决策                | 结论                               |
| --- | ------------------- | ---------------------------------- |
| Q1  | 交付边界            | 分层 delta；不推翻骨架             |
| Q2  | 版本                | 钉现状；上游文档「待评估」         |
| Q3  | 调研深度            | Tier-1 双源；Tier-2 gh             |
| Q5  | cbm                 | 场景强制；Claude L4；Cursor P0     |
| Q6  | sync                | 多编辑器；修 CONTEXT/CORE/MCP 过期 |
| Q7  | 波次                | 三波串行                           |
| Q8  | 版本号              | **v10.5.1** patch                  |

**无架构重开提案**（五柱边界 / ECC cherry_pick / ruflo reference_only 不变）。版本钉扎遵循 R14：不自动升 OpenSpec 1.6 / GSD 1.7 / codegraph 1.4 / cbm 0.9 / superpowers 6.1 / claude-mem 13.11。

## SSOT 链

```
repos/*.md → 30-repo-deep-research-v10.md（唯一全量）→ COVERAGE.md（含原 REPO_ANALYSIS 评分/互博）→ MANIFEST.yaml → SPEC.md
计划: plans/2026-07-29-v10.6-optimization.md（合并 v10.5/v10.5.1/v10.6 决策脉络）
诊断: docs/diagnostic-v10.5.2.md（v10.5.2 工具调用门控）
```
