# Design Round 3 — 24 仓库 + P3 安全补强

> 日期：2026-05-26 | 状态：已实施 | 基于：五柱骨架 v2.4

## 审计结论

| 类别 | 结论 |
|------|------|
| 五柱骨架 | 不变；Superpowers / GSD / OpenSpec / gstack / claude-mem |
| 24 用户仓库 | 90%+ 已覆盖；mattpocock 全局 2 已落地 |
| P3 安全补强 | cherry-pick 入 rules/hooks/settings，非第六柱 |
| ruflo | 参考排除；制品持久化吸收至 WORKFLOW.md |
| compound-engineering | Cursor plugin 已有；Claude Code 侧 instinct-learning + experiences/ |

## P3 仓库来源索引

| 仓库 | source | 落地 | 互斥 |
|------|--------|------|------|
| trailofbits/claude-code-config | main | rules/SECURITY.md §11, settings.json deny | pre-bash-guard owner 不变 |
| trailofbits/claude-code-devcontainer | main | templates/devcontainer/README.md | 非全局 hook |
| dwarvesf/claude-guardrails | main | hooks/_optional/pre-userprompt-secret-scan.py | post-secret-detector 职责分离 |
| lasso-security/claude-hooks | main | hooks/_optional/post-prompt-injection-scan.py | warn 不 block |
| efij/awesome-claude-code-security | main | SPEC.md 外链索引 | 仅索引 |
| EveryInc/compound-engineering-plugin | main | SPEC.md 注明 Cursor plugin | 不导入 37 skill |
| kumaran-is/claude-code-guide | main | rules/CONTEXT.md 3 条 | 参考 |
| domengabrovsek/claude | main | agents/README routing | 参考 |
| marc-shade/claude-code-security | main | rules/SECURITY.md checklist | 参考 |
| disler/claude-code-hooks-mastery | main | hooks/tests/fixtures/ | 本地测试 |
| ruvnet/ruflo | main | 排除；WORKFLOW 制品持久化 | orchestrator + claude-mem |

## 来源三处同步规范

每个 P3 concern 必须在以下三处标注 `source:`：

1. `design.md` §15.6
2. `MANIFEST.yaml` concerns
3. `SPEC.md` 溯源表

## 实施 Phase

```
Phase 10: design/spec/compliance/tasks v2.4 + design-round3.md
Phase 11: validate_config + settings + SECURITY + hooks + runtime
Phase 12: validate + sync DryRun + 互博 grep
```

## 规模（v2.4）

| 类型 | 上限 | 当前 |
|------|------|------|
| 全局 skills | ≤28 | 27 |
| 全局 agents | ≤22 | 20 |
| 全局 rules | 10 | 9 |
| CLAUDE.md | ≤500 | ~167 |
