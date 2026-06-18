# 28 仓库深度调研报告 v10.2-rc

> 日期: 2026-06-17 | 方法: Exa + Firecrawl 交叉验证 + 5 Agent 并行 WebSearch/WebFetch 增强 | 28+ 仓库
> 状态: **Phase 1 完成** | 运行配置: **v10.1 → v10.2 规划中** | 历史 v7/v8 → `archive/`
> Per-repo 卡片: [`repos/`](repos/) | 五柱卡片已 Agent 增强（2026-06-17）

---

## 摘要

五柱企业级骨架（v10.0→v10.1 增量：GSD 版本对齐 + 27 张 repo 卡片）：

```
RUNTIME = Superpowers(方法论) + GSD(上下文) + OpenSpec(规格) + gstack(审查) + claude-mem(记忆)
横切    = ECC(cherry-pick) + RTK/caveman + codegraph + Exa/Firecrawl（UA disabled）
探索    = codegraph → Grep → Read
执行    = SDD+TDD → verify → learn(pattern+mem)
```

**v10.1 访谈共识**（15 项锁定）：见 [design-v10.1.md](../../spec/claude-config-integration/design-v10.1.md)

---

## 五柱骨架

| 柱 | 仓库 | 卡片 |
|----|------|------|
| 方法论 | obra/superpowers v5.1.0 | [obra-superpowers](repos/obra-superpowers.md) |
| 上下文 | open-gsd/gsd-core v1.4.5 | [open-gsd-gsd-core](repos/open-gsd-gsd-core.md) |
| 规格 | Fission-AI/OpenSpec v1.4.1 | [fission-ai-openspec](repos/fission-ai-openspec.md) |
| 审查 | garrytan/gstack v0.19 | [garrytan-gstack](repos/garrytan-gstack.md) |
| 记忆 | thedotmack/claude-mem v13.6.1 | [thedotmack-claude-mem](repos/thedotmack-claude-mem.md) |

**Superpowers 工作流链**：

```
brainstorming (HARD-GATE) → using-git-worktrees → writing-plans
→ subagent-driven-development → TDD → requesting-code-review → finishing-a-development-branch
```

**GSD 阈值双轨**：

| 平台/场景 | 阈值 | 行动 |
|-----------|------|------|
| Cursor/编辑器 | <70% / 70% / 90% | 正常 / `/summarize` / 强制压缩或子 Agent |
| GSD 逻辑 | 70% | 任务边界 / 子 Agent 切换（非强制压缩） |

---

## L1 治理横切

| 仓库 | 卡片 | 决策 |
|------|------|------|
| affaan-m/ECC v2.0-rc.1 | [affaan-m-ecc](repos/affaan-m-ecc.md) | cherry-pick，无插件 |
| bytedance/deer-flow v2.0 | [bytedance-deer-flow](repos/bytedance-deer-flow.md) | L3 可选，>30min |
| ruvnet/ruflo | [ruvnet-ruflo](repos/ruvnet-ruflo.md) | reference_only |

---

## L2 优化横切

| 仓库 | 卡片 |
|------|------|
| rtk-ai/rtk v0.42.1 | [rtk-ai-rtk](repos/rtk-ai-rtk.md) |
| JuliusBrussee/caveman v1.8.2 | [juliusbrussee-caveman](repos/juliusbrussee-caveman.md) |
| 内部阈值 | rules/CORE.md + CONTEXT.md |

---

## L3 洞察横切

| 仓库 | 卡片 | 决策 |
|------|------|------|
| colbymchenry/codegraph v1.0.1 | [colbymchenry-codegraph](repos/colbymchenry-codegraph.md) | mandate init |
| Lum1104/Understand-Anything v2.7.5 | [lum1104-understand-anything](repos/lum1104-understand-anything.md) | **disabled** |
| Firecrawl + Exa | deep-research L3 | 双源，Exa 兜底 |

---

## 技能与最佳实践（12 仓库）

| 仓库 | 卡片 |
|------|------|
| shanraisshan/claude-code-best-practice | [shanraisshan-claude-code-best-practice](repos/shanraisshan-claude-code-best-practice.md) |
| mattpocock/skills | [mattpocock-skills](repos/mattpocock-skills.md) |
| anthropics/skills | [anthropics-skills](repos/anthropics-skills.md) |
| forrestchang/andrej-karpathy-skills | [forrestchang-andrej-karpathy-skills](repos/forrestchang-andrej-karpathy-skills.md) |
| 2025Emma/vibe-coding-cn | [2025emma-vibe-coding-cn](repos/2025emma-vibe-coding-cn.md) |
| ComposioHQ/awesome-claude-skills | [composiohq-awesome-claude-skills](repos/composiohq-awesome-claude-skills.md) |
| hesreallyhim/awesome-claude-code | [hesreallyhim-awesome-claude-code](repos/hesreallyhim-awesome-claude-code.md) |
| x1xhlol/system-prompts-and-models | [x1xhlol-system-prompts-and-models](repos/x1xhlol-system-prompts-and-models.md) |
| VoltAgent/awesome-design-md | [voltagent-awesome-design-md](repos/voltagent-awesome-design-md.md) |
| nextlevelbuilder/ui-ux-pro-max-skill | [nextlevelbuilder-ui-ux-pro-max-skill](repos/nextlevelbuilder-ui-ux-pro-max-skill.md) |
| Chalarangelo/30-seconds-of-code | [chalarangelo-30-seconds-of-code](repos/chalarangelo-30-seconds-of-code.md) |
| anthropics/claude-code-action | [anthropics-claude-code-action](repos/anthropics-claude-code-action.md) |

---

## 工具与集成

| 仓库 | 卡片 |
|------|------|
| eyaltoledano/claude-task-master | [eyaltoledano-claude-task-master](repos/eyaltoledano-claude-task-master.md) |
| github/github-mcp-server | [github-github-mcp-server](repos/github-github-mcp-server.md) |
| zilliztech/claude-context | [zilliztech-claude-context](repos/zilliztech-claude-context.md) |

---

## 去重决策矩阵（v10.1）

| 重叠领域 | 涉及 | 决策 |
|----------|------|------|
| 任务规划 | superpowers vs task-master | superpowers 主；task-master L4 PRD |
| 编排 | subagent vs deer-flow vs ruflo | 内部 / L3 长时 / 仅文档 |
| 代码探索 | codegraph vs UA vs Grep | codegraph → Grep（UA disabled） |
| UI 设计 | gstack vs ui-ux-pro-max | gstack 流程；uupm catalog |
| 记忆 | claude-mem vs claude-context | mem SSOT；context L4 按需 |
| 规格 | OpenSpec vs GSD .planning | 三轨互斥 |
| 审查 | gstack vs compound-engineering | 禁用 plugin；本地 agents |
| 压缩 | RTK vs caveman | 输入 vs 输出 |
| Superpowers | 插件 vs 本地 skills | 后加载本地覆盖 |
| 加载 | L0 四入口 vs 全量 rules | sync 索引 L0 only；P0 五技能 L1 |

---

## 吸收优先级

### P0（Phase B）

1. MANIFEST v10.1 + GSD 版本 1.4.1 对齐
2. SSOT 链 + 27 repo 卡片
3. validate_config 16/16 + sync.ps1

### P1 — 已完成

- Firecrawl 双源、Endless Mode 评估、OpenSpec core CLI

### P2 — 刻意不实现

- GSD forensics/resume、[gsd-gaps-v10.md](gsd-gaps-v10.md)
- ECC install-state、ruflo 集成、UA 启用

---

## v10 → v10.1 变更日志

| 项 | v10.0 | v10.1 |
|----|-------|-------|
| 文档结构 | 单文件摘要 | +27 张 [repos/](repos/) 卡片 |
| GSD 版本 | 1.42.3（旧编号） | **1.4.5** stable（1.5.0-rc 仅跟踪） |
| codegraph | 0.9.9 | **1.0.1**（v1.0 配置值脱敏 breaking） |
| RTK / caveman | 0.42.1 / 1.8.2 | **0.42.4** / **1.9.0** |
| claude-mem | 13.6.0 | **13.6.1** |
| ECC | 2.0-rc | **2.0.0** 正式（仍 cherry-pick） |
| gstack | v0.19 CLI | package **1.58.1.0**（无 GitHub Release） |
| 探索链 | codegraph → UA → Grep | codegraph → Grep（UA disabled 明示） |
| 加载策略 | 已述 | P0 五技能 L1 + L0 四入口访谈锁定 |
| OpenSpec | v1.4.1 | v1.4.1 双源确认；sync 默认与 core 一致 |

---

## 信息源

| 来源 | 日期 | 可信度 |
|------|------|--------|
| Exa: superpowers v5.1.0, OpenSpec v1.4.1 | 2026-06 | 高 |
| Exa: open-gsd/gsd-core v1.4.1 | 2026-06 | 高 |
| Firecrawl: gstack v0.19 | 2026-06 | 高 |
| 本地 MANIFEST + installed_plugins | 2026-06-16 | 高 |
| 访谈 15 项共识 | 2026-06-16 | 高 |
