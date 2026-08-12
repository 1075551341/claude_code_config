# Lum1104/Understand-Anything — 归档卡

> 层: 已归档 | 刷新: 2026-07-31 | 决策: removed (v10.5.1 Q4) | 不重新集成 (P13)
> 现状(2026-07-31 双源验证): 已迁移至 [Egonex-AI/Understand-Anything](https://github.com/Egonex-AI/Understand-Anything)，76.9K★，活跃维护（pushed 2026-07-29）

## 能力（调研期存档 + 2026-07-31 复核）

- 知识图谱：多 agent pipeline 将代码库/知识库/文档转为可交互知识图（structural + domain 双视图）
- 语义图/understand-graph：类/函数/依赖级节点 + 自然语言问答 + diff 影响分析
- 多平台插件：Claude Code/Cursor/Codex/Copilot/Gemini CLI 等 17 平台；Tree-sitter + LLM 混合
- 数据目录：.ua/knowledge-graph.json（增量更新，可提交分享）

## 移除理由（v10.5.1 Q4，维持）

- 与 colbymchenry/codegraph（R17 常驻，符号级）功能重叠
- 与 DeusData/codebase-memory-mcp（L4 架构/ADR/变更）重叠
- 双引擎替代：codegraph + cbm 覆盖全部场景，UA 冗余；R14 版本克制不重新评估

## 决策引用

- 30-repo-deep-research-v10.md v10.5 delta（Q4: UA removed）
- v10.5 设计 P13 判定：不重新集成（设计文档已清理，结论见 `SPEC.md` 变更日志）
- COVERAGE.md 冗余/互博 #1：codegraph vs UA

## 跟踪

- 无跟踪动作（removed 决策维持；活跃度提升不改变冗余结论）
- 重新集成触发条件：codegraph/cbm 能力缺口出现（当前无）
