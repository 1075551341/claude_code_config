---
description: 同步 OpenSpec delta specs 到主规格（core profile + /opsx:sync）
---

# /sync — OpenSpec delta 同步

> **正文**：`rules/OPENSPEC.md` | CLI：`/opsx:sync` 或 `openspec sync`

将 `openspec/changes/<id>/specs/` 中的 delta 合并到项目主 spec。

## 前置

- core profile（`openspec init --tools cursor`）已配置
- `apply` 完成且 `verify` 通过

## 流程

1. 确认 delta 制品完整
2. 运行 `/opsx:sync`（或 `openspec sync`）
3. 检查主 spec 无冲突
4. 继续 `/archive` 归档变更
