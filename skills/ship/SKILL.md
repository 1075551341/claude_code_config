---
name: ship
description: 交付管线（分支完成 → 测试/覆盖 → 推送 → 开 PR → 合并策略 → 可选部署）。触发词：发布 | ship | 开 PR | pull request | 合并分支 | 分支完成
triggers: [发布, ship, 推送开PR, 部署验证, 开 PR, pull request, 提交 PR, gh pr, 分支完成, 合并分支, 分支清理]
layer: supplement
source: garrytan/gstack + obra/superpowers
disable-model-invocation: true
loading_tier: L3
---

# Ship（交付唯一正文）

> v12：原 `skills/pr-workflow`（开 PR）与 `skills/finishing-a-development-branch`（分支完成/合并策略）并入本技能；后者保留为指向本文件的薄壳。阶段门控 → `config/workflow.yaml` `stages.ship`（`/ship` 命令派生块）。
> Git 安全（禁自动 commit/stash、禁改 git config）→ `skills/git-workflow/SKILL.md`。用户未要求时不 push、不开 PR。

## 前置（④验证已通过）

- verification-before-completion 全绿，本轮审查批次 PASS
- 文档/CHANGELOG/版本戳/派生块已同步（改过 `config/workflow.yaml` → `python scripts/workflow.py check` 通过）

## 管线

1. **同步基线**：`git fetch` 目标分支；有冲突先解决（merge 或 rebase，按仓库惯例）
2. **全量测试 + 构建/类型/Lint**；无测试框架则说明并引导
3. **覆盖审计**：覆盖率不低于基线；新逻辑有测试
4. **准备 PR（并行）**：`git status`；`git diff`（staged + unstaged）；分支是否 track remote；`git log` + `git diff <base>...HEAD`（覆盖本分支**全部** commits，非仅最新一条）
5. **推送**：需要时 `git push -u origin HEAD`
6. **开 PR**：`gh pr create`（HEREDOC body，格式见下）；完成后返回 **PR URL**
7. **合并策略**（用户要求合并时）：单一特性/提交杂 → squash；提交已整洁且需保留历史 → rebase/merge；合并后清理本地与远程分支
8. **可选部署**：完整闭环（approved PR → verified production）→ `catalog/agents/land-and-deploy.md`；CI 模板 → `templates/github-actions/`（claude-code-action，4 后端，结构化 JSON 输出）

## PR 格式

```bash
gh pr create --title "<type>(<scope>): <description>" --body "$(cat <<'EOF'
## Summary
- 变更点

## Test plan
- [x] 构建 / 测试 / lint 命令与结果

## 验证清单
- [x] eng-reviewer PASS（+ 按路由触发的审查者）
- [x] 文档 / CHANGELOG 已同步
EOF
)"
```

## 预发布检查清单

```
□ 构建通过（无错误、无新 warning）
□ 测试通过（单元 + 集成，覆盖率不低于基线）
□ 审查批次 PASS（eng-reviewer 必派；安全敏感 +security-reviewer）
□ 文档更新（README / API docs / CHANGELOG）
□ 无硬编码密钥 / .env 泄露（R11）
□ 依赖无已知漏洞（pnpm audit / uv pip audit 等）
□ 无回滚风险；CI 全绿
```

## 约束

- 禁止修改 git config；禁止用 TodoWrite / Task 替代本流程
- 强推 main / 删除远程分支前须用户确认（R8）
