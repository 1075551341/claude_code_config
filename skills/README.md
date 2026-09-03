# Skills 技能库

> **全局 36 个**（L1×4 + L2 门控×5 + L3×27；以 [skills-INDEX.md](../skills-INDEX.md) 为准）+ **catalog/** 领域库（按需复制）｜Superpowers 插件 v6.3.0；本地同名 skill 为权威

完整索引 → [skills-INDEX.md](../skills-INDEX.md)

---

## P0 路由集（6）

L1: using-superpowers, task-triage, change-impact-analysis, brainstorming  
L2 门控: verification-before-completion, systematic-debugging

## Superpowers Workflow（12，本地深度定制版）

writing-plans | executing-plans | test-driven-development | subagent-driven-development | using-git-worktrees | requesting-code-review | receiving-code-review | finishing-a-development-branch | brainstorming | systematic-debugging | verification-before-completion | using-superpowers

> 与插件 superpowers v6.3.0 同名但**非副本**：本地版为中文重写 + 五阶段/门控/verify_tier 集成（相似度 <10%），本地为权威。

## 调研 / Git / 记忆

deep-research | git-workflow | pr-workflow | claude-mem-maintenance | memory-compression

## Meta

spec-validation | karpathy-guidelines | caveman-compress | skill-creator | skill-reviewer

## 扩展

autoplan | design-pipeline（含原 design-engineer Phase 2）| ship（含原 release-engineer）| structured-artifacts

## 重构与前端

code-refactoring（含前端提案模式）| frontend-library-advisor | frontend-design-pattern-applier | test-edge-case-analyzer

## 其他

triage | improve-codebase-architecture | workstream-management | adr-management | change-impact-analysis | task-triage

---

## v11 变更

- 降级 catalog：office-hours / instinct-learning / onboarding-guide / claude-to-deerflow / browser-qa / taste-memory
- 删除：context-engineering（正文并入 rules/CONTEXT.md）
- 并入：frontend-refactor-proposer → code-refactoring 子文档；writing-skills → skill-creator 前言

Catalog 复制：`python ~/.claude/scripts/migrate-from-legacy.py --project <path> --skill <name>`
