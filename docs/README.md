# Docs 文档索引

> 最后更新: 2026-09-03 | **当前配置: v11.4.13**

---

## 配置与决策

| 文档 | 描述 |
| ---- | ---- |

<!-- v11: RUNTIME_PLAYBOOK 已并入 CLAUDE.md（决策树）/ rules/CONTEXT.md（auto-compact）/ rules/MCP.md（双平台工具） -->

| [CURSOR_MCP_PROFILE.md](CURSOR_MCP_PROFILE.md) | Cursor 插件/MCP 边界 |
| [CURSOR_EDITOR_SETUP.md](CURSOR_EDITOR_SETUP.md) | Cursor 编辑器专有设置 |
| [LLM_AS_A_VERIFIER_SYNC.md](LLM_AS_A_VERIFIER_SYNC.md) | llm-as-a-verifier 优点提取 + Claude 优点盘点 + 对比矩阵与融合决策（v11.3.5） |
| [ADR/](ADR/) | 架构决策记录 |
| [SYNC_GUIDE.md](SYNC_GUIDE.md) | 多编辑器同步 1+N（Claude Code 零同步 + Cursor/qoder-cn/trae-cn/workbuddy，qoder/trae/codearts 待装自动跳过） |
| [TOOL_MATCHING_GUIDE.md](TOOL_MATCHING_GUIDE.md) | MCP / R17/R18 路由 |
| [superpowers/plans/2026-08-01-v10.11-44repo.md](superpowers/plans/2026-08-01-v10.11-44repo.md) | 最近一次优化计划（本地制品，不入版本库） |

## 深度调研 (research/)

| 文档                                                                        | 描述                                      |
| --------------------------------------------------------------------------- | ----------------------------------------- |
| [44-repo-deep-research-v10.11.md](research/44-repo-deep-research-v10.11.md) | **调研 SSOT（唯一全量，44 仓库）**        |
| [COVERAGE.md](research/COVERAGE.md)                                         | 覆盖矩阵 + 五柱评分（含原 REPO_ANALYSIS） |
| [research/README.md](research/README.md)                                    | 调研索引                                  |
| [research/repos/](research/repos/)                                          | per-repo 卡片（46）                       |

**SSOT 链**：`research/repos/*.md` → `44-*` → `COVERAGE.md` → `MANIFEST.yaml` → `SPEC.md`
