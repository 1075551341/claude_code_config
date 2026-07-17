# 仓库覆盖矩阵（v10.5.1）

> 日期: 2026-07-17 | SSOT: 28 active + 1 removed ↔ 卡片 ↔ MANIFEST concern ↔ 集成决策
> 前版: v10.5（同日）→ **v10.5.1 分层 delta**

## 覆盖率

| 指标         | 值                               |
| ------------ | -------------------------------- |
| 目标仓库     | 29（含 UA 审计卡）               |
| Active       | **28**                           |
| Removed      | **1**（Understand-Anything，Q4） |
| 独立卡片     | 29（均含 v10.5.1 delta）         |
| 运行配置目标 | **v10.5.1**（Wave3 落地后）      |

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

## Removed（Q5）

| 仓库                                        | 卡片                                                                | 状态                                       |
| ------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------ |
| Egonex-AI/Understand-Anything（原 Lum1104） | [lum1104-understand-anything](repos/lum1104-understand-anything.md) | **removed** — 审计保留；替代 cbm+codegraph |

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
| Q4  | Understand-Anything | **removed**                        |
| Q5  | cbm                 | 场景强制；Claude L4；Cursor P0     |
| Q6  | sync                | 多编辑器；修 CONTEXT/CORE/MCP 过期 |
| Q7  | 波次                | 三波串行                           |
| Q8  | 版本号              | **v10.5.1** patch                  |

**无架构重开提案**（五柱边界 / ECC cherry_pick / ruflo reference_only 不变）。版本钉扎遵循 R14：不自动升 OpenSpec 1.6 / GSD 1.7 / codegraph 1.4 / cbm 0.9 / superpowers 6.1 / claude-mem 13.11。

## SSOT 链

```
repos/*.md → 30-repo-deep-research-v10.md（v10.5.1 唯一全量）→ COVERAGE.md → REPO_ANALYSIS.md → MANIFEST.yaml → SPEC.md
计划/设计: plans/2026-07-17-v10.5.1-optimization.md · design-v10.5.1.md
（v10.5 计划/设计保留交叉链接）
```
