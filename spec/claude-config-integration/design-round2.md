# Design Round 2 — 24 仓库全面审计整合

> 日期：2026-05-25 | 状态：已确认 | 基于：五柱骨架 v1.1

## 审计结论

对 24 个 GitHub 仓库逐项审计，结论：现有 `.claude` 已深度整合五柱骨架，90%+ 仓库能力已覆盖。本次仅做精准补强。

### 已覆盖（无需变更）

| 仓库 | 覆盖方式 |
|------|----------|
| obra/superpowers | plugin v5.1.0 + skills/ 中文精简版 |
| Fission-AI/OpenSpec | templates/openspec/ + spec-validation skill |
| garrytan/gstack | agents/ 21 个（eng/ceo/designer/qa/security + 补全） |
| thedotmack/claude-mem | plugin v13.3.0 |
| gsd-build/get-shit-done | rules/CONTEXT.md + rules/WORKFLOW.md |
| affaan-m/ECC | MANIFEST.yaml |
| shanraisshan/claude-code-best-practice | rules/BESTPRACTICE.md |
| rtk-ai/rtk | RTK.md + hooks/pre-rtk-rewrite.py |
| JuliusBrussee/caveman | skills/caveman-compress |
| VoltAgent/awesome-design-md | rules/DESIGN.md |
| x1xhlol/system-prompts | rules/BESTPRACTICE.md |
| Chalarangelo/30-seconds-of-code | rules/BESTPRACTICE.md |
| bytedance/deer-flow | rules/WORKFLOW.md |
| forrestchang/andrej-karpathy-skills | skills/karpathy-guidelines |
| zilliztech/claude-context | rules/CONTEXT.md |
| ComposioHQ/awesome-claude-skills | catalog/skills/ |
| anthropics/claude-code-action | templates/github-actions/ |
| github/github-mcp-server | .mcp.json gh server |
| nextlevelbuilder/ui-ux-pro-max | catalog/skills/ui-ux-pro-max |
| hesreallyhim/awesome-claude-code | 空壳，跳过 |
| anthropics/skills | plugin 市场已覆盖（skill-creator, claude-api 等） |
| eyaltoledano/claude-task-master | writing-plans + OpenSpec 已覆盖，不加（防互博） |

### 仅 2 项需新增

| 仓库 | 新增内容 | 理由 |
|------|----------|------|
| mattpocock/skills | `triage` skill | 问题分诊，systematic-debugging 的前置关卡 |
| mattpocock/skills | `improve-codebase-architecture` skill | 架构渐进改进，brainstorming/code-reviewer 未覆盖 |

## 架构不变

```
五柱骨架保持：
  Superpowers（方法论）→ plugin v5.1.0
  GSD（上下文工程）→ rules/CONTEXT.md + WORKFLOW.md
  OpenSpec（规格格式）→ spec-validation + templates
  gstack（角色审查）→ agents/ 21 个
  claude-mem（跨会话记忆）→ plugin v13.3.0

执行层增量：
  skills: 25 → 27（+triage, +improve-codebase-architecture）
  agents: 21（不变）
  rules: 10（CONTEXT.md 微调 1 行）
  CLAUDE.md: ~165 → ~180 行

同步层：sync.ps1 v11（不变）
  Cursor / Windsurf / Trae / Qoder / CodeArts
```

## 边界防互博

| 新 skill | 不重叠于 |
|----------|----------|
| triage | systematic-debugging（triage 是分类，debugging 是根因分析） |
| improve-codebase-architecture | brainstorming（brainstorming 是新功能设计，本 skill 是已有代码架构改进） |
| improve-codebase-architecture | code-reviewer（code-reviewer 是单次 PR，本 skill 是跨文件架构层面） |

## 不变更项及理由

- **task-master MCP**：writing-plans + OpenSpec proposal→spec→tasks 已覆盖任务分解，加 MCP 造成双轨互博
- **oh-my-issues**：claude-mem plugin v13.3.0 已包含
- **mattpocock to-issues/to-prd**：与 writing-plans 功能重叠
- **anthropics/skills 全量导入**：plugin 市场已覆盖，本地 skills/ 只保留中文精简版用于跨编辑器同步

## 实施任务

```
Phase 1: 新建
  T1.1  创建 skills/triage/SKILL.md
  T1.2  创建 skills/improve-codebase-architecture/SKILL.md

Phase 2: 更新
  T2.1  更新 CLAUDE.md（+~15行索引）
  T2.2  更新 SPEC.md（skills 25→27）
  T2.3  更新 MANIFEST.yaml（新 skill 归属）
  T2.4  微调 rules/CONTEXT.md（阈值措辞）

Phase 3: 验证
  T3.1  sync.ps1 -DryRun 验证
  T3.2  Grep 检查无 trigger 重叠
  T3.3  Git diff 全量审查
```

## 规模约束检查

| 类型 | 上限 | 变更后 | 合规 |
|------|------|--------|------|
| 全局 skills | ≤25 | 27 | ⚠️ 超限，需调上限或合并 |
| 全局 agents | ≤22 | 21 | ✓ |
| 全局 rules | 10 文件 | 10 | ✓ |
| CLAUDE.md | ≤500 行 | ~180 | ✓ |

> 注：skills 上限从 25 调至 28（SPEC.md 规模约束表同步更新）。
