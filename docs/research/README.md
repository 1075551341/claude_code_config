# 调研文档索引

> 快照日期: 2026-08-01（调研快照仍为 **v10.11.0**，未重新调研） | 运行配置目标: v10.17.0

**SSOT**：[`44-repo-deep-research-v10.11.md`](44-repo-deep-research-v10.11.md)（原 30-repo 已并入）
**覆盖矩阵**：[`COVERAGE.md`](COVERAGE.md)（44 仓库；含原 REPO_ANALYSIS 五柱评分，v10.6.0 已合并）
**优化计划**：[`../superpowers/plans/2026-08-01-v10.11-44repo.md`](../superpowers/plans/2026-08-01-v10.11-44repo.md)（最近一次执行记录；计划为本地制品，不入版本库）

| 文档                                                               | 说明                                  |
| ------------------------------------------------------------------ | ------------------------------------- |
| [44-repo-deep-research-v10.11.md](44-repo-deep-research-v10.11.md) | 深度调研 SSOT（唯一全量，44 仓库）    |
| [COVERAGE.md](COVERAGE.md)                                         | 44 覆盖矩阵 + 五柱评分 + 升级评估记录 |
| [repos/](repos/)                                                   | per-repo 卡片（46）                   |

### 五柱

- [obra-superpowers](repos/obra-superpowers.md) · [open-gsd-gsd-core](repos/open-gsd-gsd-core.md) · [fission-ai-openspec](repos/fission-ai-openspec.md) · [garrytan-gstack](repos/garrytan-gstack.md) · [thedotmack-claude-mem](repos/thedotmack-claude-mem.md)

### L1 / L2 / L3

- [affaan-m-ecc](repos/affaan-m-ecc.md) · [bytedance-deer-flow](repos/bytedance-deer-flow.md) · [ruvnet-ruflo](repos/ruvnet-ruflo.md)
- [rtk-ai-rtk](repos/rtk-ai-rtk.md) · [juliusbrussee-caveman](repos/juliusbrussee-caveman.md)
- [colbymchenry-codegraph](repos/colbymchenry-codegraph.md) · [deusdata-codebase-memory-mcp](repos/deusdata-codebase-memory-mcp.md)

### 技能 / 工具

见 `repos/` 其余卡片；claude-context → archived_redirect。

**配置真相源链**：

```
repos/*.md → 44-repo-deep-research-v10.11.md → COVERAGE.md → MANIFEST.yaml → SPEC.md
```

## 维护规则（v10.11.0）

- 缺口仓库才双源深研（Firecrawl+Exa，L2 档）；已覆盖仓库 gh 轻复核（1-2K tokens，gh 凭证可用时）
- 卡片 delta 单段制：历史段直接删除（v10.17 起不再保留 `archive/`，历史由 git 承担）
- 主文档 `44-repo-deep-research-v10.11.md` 只更新顶部摘要+版本号，不追加段落（v10.11.0 Delta 节 ≤15 行）
- 44 仓库覆盖后新增仓库：先建卡片 → COVERAGE +1 行 → 主文档 Delta 节更新
