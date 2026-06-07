# 深度调研索引

> 日期: 2026-06-07 | 五柱 × 29 仓库 | 最新配置: v8.1 | 调研版本: v8.0

## 核心文档

| 文档 | 版本 | 说明 |
|------|------|------|
| [29-repo-deep-research-v8.md](29-repo-deep-research-v8.md) | v8.0 | **最新** — 29 仓库全量调研 + ECC 2.0/deer-flow/ruflo 深度分析 |
| [28-repo-deep-research-v7.md](28-repo-deep-research-v7.md) | v7.0 | 28 仓库全量 README 分析 |
| [five-pillars-v7.md](five-pillars-v7.md) | v7.0 | 五柱骨架深度分析 |
| [comparative-analysis-v7.md](comparative-analysis-v7.md) | v7.0 | 仓库对比分析 & 集成建议 |
| [repo-analysis-gstack-v7.md](repo-analysis-gstack-v7.md) | v7.0 | gstack v0.19 23 角色详细分析 |
| [repo-analysis-codegraph-v7.md](repo-analysis-codegraph-v7.md) | v7.0 | codegraph 使用分析 |
| [26-repo-research-summary.md](26-repo-research-summary.md) | v6 | 26 仓库早期调研 |
| [27-repo-research-v6.md](27-repo-research-v6.md) | v6 | 27 仓库中期调研 |

## 仓库分组

| 分组 | 仓库 | 定位 |
|------|------|------|
| **五柱** | superpowers, GSD, OpenSpec, gstack, claude-mem | 企业级架构核心 |
| **治理** | ECC, deer-flow, ruflo | 防互博 + 编排 |
| **优化** | RTK, caveman, codegraph, UA | Token 节省 + 洞察 |
| **技能** | best-practice, mattpocock/skills, anthropics/skills, karpathy, vibe-coding-cn, awesome-claude-skills | 方法论 + 格式 |
| **工具** | task-master, claude-code-action, github-mcp, claude-context | CI/CD + 集成 |
| **参考** | awesome-design-md, system-prompts, 30-seconds-of-code, awesome-claude-code | 设计 + 实证 |

## 五柱声明

```
Superpowers → 方法论 (HOW): 14 skill 完整开发链 + HARD-GATE
GSD         → 上下文 (CONTEXT): 三级阈值 + 三态制品 + DAG
OpenSpec    → 规格 (WHAT): fluid + brownfield-first + opsx
gstack      → 审查 (WHO): 23 角色虚拟团队
claude-mem  → 记忆 (MEMORY): 渐进式披露 + SSOT
```

## 关键变更（v7.0 → v8.0）

| 仓库 | 深度补充 |
|------|----------|
| affaan-m/ECC | v2.0 架构: Module Resolver → Target Adapter → Operation Planner → Install-State |
| bytedance/deer-flow | 9 层 Middleware、Sandbox 隔离、claude-to-deerflow bridge |
| ruvnet/ruflo | 蜂群拓扑 (hierarchical/mesh/adaptive)、HNSW 向量记忆、SONA 自学习 |
| eyaltoledano/claude-task-master | 选择性工具加载 (core/standard/all)、~70% token 减少 |
