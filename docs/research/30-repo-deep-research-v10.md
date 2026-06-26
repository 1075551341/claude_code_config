# 28 仓库深度调研报告 v10.3

> 日期: 2026-06-24（v10.3）/ 2026-06-26（v10.3.1 delta） | 方法: Exa + Firecrawl/官方源 交叉验证 | 28 张卡片
> 状态: **已完成** | 运行配置: **v10.3.1** | 历史 v7/v8 → `archive/`
> Per-repo 卡片: [`repos/`](repos/) | 五柱卡片 + codegraph + plugins-official 已刷新（2026-06-24）；4 张高变化卡片 delta 刷新（2026-06-26）

---

## 摘要

五柱企业级骨架（v10.0→v10.1 增量：GSD 版本对齐 + 27 张 repo 卡片）：

```
RUNTIME = Superpowers(方法论) + GSD(上下文) + OpenSpec(规格) + gstack(审查) + claude-mem(记忆)
横切    = ECC(cherry-pick) + RTK/caveman + codegraph + Exa/Firecrawl（UA l3_on_demand）
探索    = codegraph → Grep → Read
执行    = SDD+TDD → verify → learn(pattern+mem)
```

> **codegraph 指标补全（v10.2.1）**：官方 current-build 均值（7 仓库/Opus 4.8/2026-06-02）= **~16% 更便宜 · ~47% 更少 token · ~58% 更少工具调用 · ~22% 更快**。旧文「~47% token」**正确但片面**，补全四元组即可。MCP 默认仅 4 工具，`codegraph_impact` 需 `CODEGRAPH_MCP_TOOLS` 显式启用（见 [codegraph 卡 F1/F2](repos/colbymchenry-codegraph.md)）。

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
| Lum1104/Understand-Anything v2.7.5 | [lum1104-understand-anything](repos/lum1104-understand-anything.md) | **l3_on_demand**（插件 disabled + catalog 保留） |
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
| anthropics/claude-plugins-official | [anthropics-claude-plugins-official](repos/anthropics-claude-plugins-official.md) |
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

## v10.1 → v10.2 变更日志

> 设计文档: [`docs/superpowers/specs/2026-06-17-v10.2-config-optimization-design.md`](../superpowers/specs/2026-06-17-v10.2-config-optimization-design.md)
> 访谈轮次: 8 项决策逐一确认 | 状态: **设计已批准**

| 项 | v10.1 | v10.2 | 决策理由 |
|----|-------|-------|---------|
| superpowers | v5.1.0 | **v6.0.0** | 简化审查（两阶段→单 task-reviewer）+ dispatching-parallel-agents + writing-skills |
| 加载分级 | L0-L4 五级 | **L0+L1+L2+L3 三级** | L3/L4 合并为 on-demand，减少认知负担 |
| UA | disabled | **L3 按需**（catalog 保留） | onboarding/领域分析场景 codegraph 无法替代 |
| GSD | v1.4.5 | v1.4.5（**锁定**） | v1.5.0-rc forensics/resume 在 P2 刻意不实现 |
| 去重 | MANIFEST conflict 基础 | **+6 组 excludes** + rule supplement_only | 温和不删，优先级明确 |
| 同步 | L0 rules only | **+`--skills` 可选 flag** | 按需初始化，不全量同步 |
| Gap 补全 | 识别但未排期 | **P0(3)/P1(3)/P2(3)** | /learn↔mem 管道 + 描述精简 + snippets |

### v10.2 P0 补全

| # | 项 | 来源 | 动作 |
|---|----|------|------|
| P0.1 | gstack /learn ↔ claude-mem 管道 | garrytan/gstack + thedotmack/claude-mem | learn skill 增加写 mem observation 步骤 |
| P0.2 | 工具描述密度精简 | x1xhlol/system-prompts | 移除冗余工具描述，保留原则 |
| P0.3 | snippets/ 初始化 | Chalarangelo/30-seconds-of-code | 5 个模板文件（py/js/shell） |

### v10.2 架构决策更新

| 决策 | 来源 | v10.2 状态 |
|------|------|-----------|
| superpowers v6.0.0 升级 | obra/superpowers | ✅ 升级，本地覆盖兼容 |
| UA L3 按需启用 | Lum1104/Understand-Anything | ADR 更新: disabled→l3_on_demand |
| 三级加载精简 | x1xhlol 工具密度研究 | L0 alwaysApply + L1 session + L2 gate + L3 on-demand |
| gstack /learn 深度集成 | garrytan/gstack | taste_memory concern → claude-mem observation 管道 |
| ECC 互斥增强 | affaan-m/ECC | +6 组 excludes，防 subagent 互博 |

---

---

## v10.2 → v10.2.1 变更日志

> 日期: 2026-06-19 | 方法: Exa + Firecrawl/官方源 双源重新核验 16+ 仓库 | 不改架构拓扑

### 版本核验表（双源）

| 仓库 | MANIFEST | 双源实测 | 动作 |
|------|----------|----------|------|
| superpowers | 6.0.0 | v6.0.0 (06-16)；插件装 5.1.0 | 升级插件 |
| gsd-core | 1.4.5 | **v1.5.0 stable** (06-05) | Phase E ADR 评估 |
| OpenSpec | 1.4.1 | v1.4.1 (06-03) 最新 | 已对齐 |
| gstack | 0.19 | **包 1.58.1.0** (06-14) | 版本号体系修正 |
| claude-mem | 13.6.1 | v13.6.1 (06-15) | 已对齐 |
| rtk | 0.42.4 | v0.42.4 stable | 已对齐 |
| caveman | 1.9.0 | v1.9.0 (06-12) | 已对齐 |
| codegraph | 1.0.1 | v1.0.1 (06-13) | 指标+工具集纠偏 |
| ECC | 2.0.0 | v2.0.0 stable (06-10) | 已对齐 |

### 三项可执行新发现

| # | 发现 | 动作 |
|---|------|------|
| F1 | codegraph MCP 默认仅 4 工具，`codegraph_impact` 需 env 启用 | CORE 变更彻底性纠偏：explore blast-radius 优先 |
| F2 | codegraph 官方四元组 ~16%成本/~47%token/~58%工具调用/~22%更快（47% **是官方数字**，原 premise 误判） | 补全为官方四元组（不删 47%） |
| F3 | caveman-shrink MCP 中间件压缩工具描述 | catalog 记录，不默认接入 |

### 其他增量

- 新增 `anthropics/claude-plugins-official` 卡片（插件分发 SSOT；card 总数 27→28）
- superpowers #1773：brainstorming AskUserQuestion 回归 → 本地守卫（仅 brainstorming）
- gstack：Codex 审查默认开启 + 5 重技能懒加载
- UA：全文统一 l3_on_demand（删除 disabled 残留）

### 去重决策矩阵 +1

| 重叠领域 | 涉及 | 决策 |
|----------|------|------|
| 插件分发 | claude-plugins-official vs 本地 agents/skills | feature-dev 三 agent 本地主（MANIFEST excludes）；LSP 族按需 |

---

## v10.2.1 → v10.3 变更日志

> 日期: 2026-06-24 | 方法: WebSearch + GitHub + 社区三源 delta 刷新 17 张 stale 卡片 | 骨架不变,深化集成

### 变更总表

| 项 | v10.2.1 | v10.3 | 决策理由 |
|----|---------|-------|----------|
| codegraph F1 | impact 默认隐藏,explore blast-radius 优先 | `.mcp.json` env `CODEGRAPH_MCP_TOOLS` 显式启用 `codegraph_impact` | R6 变更彻底性保障:impact 工具恢复,满足铁律 |
| sync.ps1 | 5 编辑器(cursor/devin/qoder/trae/codearts) | 7 编辑器(+qoder-cn, +trae-cn) | 用户要求 7 编辑器同步;-cn 变体独立配置目录 |
| stale 卡片 | 28 张(部分 2026-06-19) | 17 张 delta 刷新到 2026-06-24 | 3 源交叉验证;版本/Stars/架构变更记录 |
| 验证 | validate_config 16/16 | + plugin grep + R16 grep + R17/R18 grep + sync --DryRun | 防互博 + 铁律强制执行验证 |
| 版本 | 10.2.1 | 10.3 | 版本号对齐(MANIFEST/CLAUDE/SPEC) |
| 语言 | 中英混合 | 文档/注释优先中文,代码保持原样 | 用户要求 |

### Delta 刷新卡片清单(17 张)

| 卡片 | 关键变更 |
|------|----------|
| bytedance-deer-flow | v2.0→v3.1;50K+ Stars;中间件 9→11 层;五模式(+fast);AIO Sandbox |
| github-github-mcp-server | v1.2.0;54K+ Stars;21 toolsets;MCP Apps;GitHub MCP Registry |
| lum1104-understand-anything | 组织迁移→Egonex-AI;26.5K+ Stars;Tree-sitter+LLM;5 Agent 流水线;多语言 |
| forrestchang-andrej-karpathy-skills | Stars 92K→176K(3 月翻倍);四原则已吸收 CORE R1-R4 |
| zilliztech-claude-context | Stars 9.9K→11.4K;实测 -40% token/-36% 工具调用;+Ollama 本地嵌入 |
| nextlevelbuilder-ui-ux-pro-max-skill | v2.2.1;53.7K+ Stars;50+ 风格/161 色板/57 字体;双模式 |
| anthropics-claude-code-action | v1.0.146 |
| anthropics-skills | ~151K+ Stars;开放标准跨平台采纳;渐进式披露 3 层 |
| 2025emma-vibe-coding-cn | 维持中文社区最佳实践 |
| composiohq-awesome-claude-skills | 21.7K+ Stars |
| chalarangelo-30-seconds-of-code | 128K+ Stars |
| hesreallyhim-awesome-claude-code | 36.8K+ Stars |
| mattpocock-skills | 135K+ Stars |
| ruvnet-ruflo | v3.6.30;蜂群拓扑持续演进 |
| shanraisshan-claude-code-best-practice | 51.3K+ Stars |
| voltagent-awesome-design-md | 91K+ Stars |
| x1xhlol-system-prompts-and-models | 140K+ Stars |

### 决策不变项

- 骨架:五柱×五阶段×三横切(不变)
- deer-flow:L3 可选(不变)
- UA:disabled + catalog 保留(不变)
- ruflo:reference_only(不变)
- zilliztech-claude-context:L4 按需(不变)
- 所有 catalog 引用:按需,不膨胀 L1(不变)

### 计划依据

5 轮访谈 20 问(见 [plans/2026-06-24-v10.3-optimization.md](../superpowers/plans/2026-06-24-v10.3-optimization.md))

---

## v10.3 → v10.3.1 变更日志

> 日期: 2026-06-26 | 方法: npm registry + GitHub Releases + Tags 三源 delta 刷新高变化仓库 | patch 级修正

### 变更总表

| 项 | v10.3 | v10.3.1 | 决策理由 |
|----|-------|---------|----------|
| 高变化卡片 | 17 张刷新到 2026-06-24 | 4 张高变化卡片 delta 刷新到 2026-06-26 | 仅刷新核心五柱 + L2 仓库,避免全量刷新浪费 token |
| claude-mem 版本 | v13.6.1 | v13.8.1 | npm registry 实际版本;GitHub Releases 不完整(仅至 v13.3.0) |
| rtk 版本 | v0.42.4(错误) | v0.41.0 | GitHub Releases 纠正:v0.42.x 从未发布稳定版;原记录混淆 npm dev tag |
| superpowers 版本 | v6.0.0 | v6.0.3 | patch 级升级;SDD scratch 路径变更(.git/ → .superpowers/sdd/) |
| gsd-core 版本 | v1.5.0(评估 Stay 1.4.5) | v1.6.0(ADR-1244 完整落地) | capability registry + context_guard_mode 需独立 ADR 评估 |
| lint 模板 | 无 | prettier + eslint 9 flat config | 用户要求:prettier 管格式,eslint 管质量,互不混淆;HTML/Vue/JSX 多属性每行一个,标签独立成行 |
| 项目模板 | 无 | templates/project-init/ | 用户要求:跨项目迭代优化 |
| sync.ps1 | 7 编辑器 | + -Lint / -InitProject flag | 分发 lint 模板 + 项目初始化 |

### Delta 刷新卡片清单(4 张)

| 卡片 | 关键变更 |
|------|----------|
| obra-superpowers | v6.0.0→v6.0.3;SDD scratch 路径 .git/→.superpowers/sdd/;evals 子模块移除 |
| thedotmack-claude-mem | v13.6.1→v13.8.1;npm registry 三源验证;GitHub Releases 不完整 |
| open-gsd-gsd-core | v1.5.0→v1.6.0;ADR-1244 五阶段完整落地;capability registry + context_guard_mode |
| rtk-ai-rtk | 版本纠正 v0.42.4→v0.41.0;v0.42.x 从未发布稳定版;根因:混淆 dev tag |

### 决策不变项

- 骨架:五柱×五阶段×三横切(不变)
- gsd-core:维持 Stay 1.4.5 推荐(v1.6.0 需独立 ADR 评估)
- rtk:hook 接线不变(版本纠正不影响功能)
- claude-mem:R14 锁定 major v13.x 维持
- superpowers:升级 6.0.0→6.0.3 可推进(patch 级,无 breaking)

### 计划依据

3 轮访谈 22 问(见 [plans/2026-06-24-v10.3-optimization.md](../superpowers/plans/2026-06-24-v10.3-optimization.md) + 本轮访谈决策)

---

## 信息源

| 来源 | 日期 | 可信度 |
|------|------|--------|
| Exa: superpowers v5.1.0/v6.0.0, OpenSpec v1.4.1 | 2026-06 | 高 |
| Exa: open-gsd/gsd-core v1.4.1 | 2026-06 | 高 |
| Firecrawl: gstack v0.19 | 2026-06 | 高 |
| 本地 MANIFEST + installed_plugins | 2026-06-17 | 高 |
| 访谈 15 项共识 (v10.1) + 8 项决策 (v10.2) | 2026-06-17 | 高 |
| superpowers v6.0.0 CHANGELOG | 2026-06-16 | 高 |
| design doc: 2026-06-17-v10.2-config-optimization-design.md | 2026-06-17 | 高 |
| Exa+Firecrawl 双源核验 16+ 仓库 (v10.2.1) | 2026-06-19 | 高 |
| codegraph v1.0 CHANGELOG (F1/F2) + 官网 | 2026-06-19 | 高 |
| gsd-core v1.5.0 stable releases | 2026-06-19 | 高 |
| superpowers #1773 issue | 2026-06-19 | 高 |
| WebSearch + GitHub + 社区三源 delta 刷新 17 张 stale 卡片 (v10.3) | 2026-06-24 | 高 |
| v10.3 计划: plans/2026-06-24-v10.3-optimization.md (5 轮访谈 20 问) | 2026-06-24 | 高 |
