---
name: pr-workflow
description: PR工作流（L3）。触发词：PR | pull request | 拉取请求 | 代码合并 | 创建PR | 提交审查
triggers: [开 PR, create PR, pull request, 提交 PR, gh pr]
layer: supplement
disable-model-invocation: true
loading_tier: L3
source: user-rules-migration
---

# GitHub Pull Request 流程

> **L3**：用户显式要求创建 PR 时 Read 全文。使用 `gh` CLI（Shell）。

## 准备（并行）

- `git status`
- `git diff`（staged + unstaged）
- 检查分支是否 track remote、是否与 remote 同步
- `git log` + `git diff [base]...HEAD`（本分支相对 base 的**全部** commits）

## 分析

- 覆盖 PR 将包含的**所有** commits，非仅最新一条
- 起草 Summary + Test plan

## 创建（顺序）

1. 需要时 `git push -u origin HEAD`
2. `gh pr create`（HEREDOC body）：

```bash
gh pr create --title "title" --body "$(cat <<'EOF'
## Summary
- ...

## Test plan
- [ ] ...

EOF
)"
```

## 约束

- **禁止**修改 git config
- **禁止**用 TodoWrite / Task 工具替代本流程
- 完成后返回 **PR URL**
- 用户未要求时不 push
