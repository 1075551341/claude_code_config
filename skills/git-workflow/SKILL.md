---
name: git-workflow
description: Git 提交与安全规范。触发：commit、提交、git commit、保存更改。
triggers: [commit, 提交, git commit, 创建提交, 保存更改]
layer: supplement
disable-model-invocation: true
loading_tier: L3
source: user-rules-migration
---

# Git 提交流程

> **L3**：用户显式要求 commit 或「提交」时 Read 全文。

## 安全协议

- **禁止**修改 git config
- **禁止**破坏性命令（`push --force`、`hard reset` 等），除非用户明确要求
- **禁止**跳过 hooks（`--no-verify`、`--no-gpg-sign` 等），除非用户明确要求
- **禁止**对 main/master force push；用户要求时须警告
- **避免** `git commit --amend`，仅当以下**全部**满足：
  1. 用户明确要求 amend，或 pre-commit hook 自动改文件需纳入
  2. HEAD 由本会话创建（`git log -1 --format='%an %ae'`）
  3. 提交**未** push 到 remote
- hook **失败**时：修复后**新建** commit，**不要** amend
- 已 push 的提交：**不要** amend（除非用户明确要求且接受 force push）
- **禁止**提交含密钥的文件（`.env`、`credentials.json` 等）；用户要求时警告

## 提交流程

1. **并行**执行：
   - `git status`（含 untracked）
   - `git diff`（staged + unstaged）
   - `git log`（近期 message 风格）
2. 分析变更，起草 1–2 句 commit message（强调 why）
3. **顺序**执行：
   - `git add` 相关文件
   - `git commit`（HEREDOC 传 message）
   - `git status` 验证成功
4. hook 失败 → 修复 → **新** commit

## Commit message 格式

```bash
git commit -m "$(cat <<'EOF'
<type>: <why-focused summary>

EOF
)"
```

遵循仓库既有风格；无约定时用 conventional commits。

## 禁止

- 无变更时 empty commit
- 用户未要求时不主动 commit
- `git` 带 `-i` 交互标志
