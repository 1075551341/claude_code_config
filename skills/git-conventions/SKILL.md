---
name: git-conventions
description: Git 分支/提交/PR 规范（与 git-workflow 安全协议互补）。触发：分支策略、commit 规范、PR 流程。
triggers: [分支策略, commit 规范, PR 流程]
layer: supplement
source: local
loading_tier: L3
disable-model-invocation: true
---

# Git 规则

## 分支策略

### Git Flow

```
main (生产)
  └── develop (开发)
        ├── feature/xxx (功能)
        ├── bugfix/xxx (修复)
        └── release/x.x.x (发布)
              └── hotfix/xxx (紧急修复)
```

### 分支命名

```
功能：feature/ISSUE-123-user-auth
修复：fix/ISSUE-456-login-error
紧急：hotfix/ISSUE-789-security-patch
发布：release/1.2.0
文档：docs/api-documentation
重构：refactor/user-service
```

## Commit 规范

### 格式

```
<type>(<scope>): <subject>

[optional body]
[optional footer]
```

### Type 类型

| 类型       | 说明                   |
| ---------- | ---------------------- |
| `feat`     | 新功能                 |
| `fix`      | Bug 修复               |
| `docs`     | 文档更新               |
| `style`    | 代码格式（不影响逻辑） |
| `refactor` | 重构                   |
| `perf`     | 性能优化               |
| `test`     | 测试相关               |
| `chore`    | 构建/工具相关          |
| `ci`       | CI 配置                |
| `revert`   | 回滚                   |

## PR 规范

### 标题格式

```
[<type>] <scope>: <description>
示例：[feat] auth: add SSO support
```

### Code Review 检查项

```markdown
代码质量：□ 风格一致 □ 无重复 □ 命名清晰
安全性： □ 无敏感泄露 □ 输入验证 □ 权限检查
性能： □ 无 N+1 □ 无内存泄漏 □ 异步正确
测试： □ 覆盖充分 □ 边界条件 □ 错误处理
```

## Agent Git 禁令（v10）

| 操作          | Agent                                                                                        | 用户本地 |
| ------------- | -------------------------------------------------------------------------------------------- | -------- |
| `git stash`   | **禁止**（shell deny）                                                                       | 允许     |
| `git commit`  | **禁止自动**；仅显式要求 + Guard 确认                                                        | 允许     |
| `git push`    | **禁止自动**（shell deny）                                                                   | 允许     |
| 新建/切换分支 | **禁止自动**（`checkout -b` / `switch` / `branch <name>` / `worktree add -b` / `branch -c`） | 允许     |

**配置**：`~/.cursor/guard-config.json` → `git.forbid_auto_commit` / `git.forbid_stash`；Claude Code → `hooks/pre-bash-guard.py`。

> **R19 铁律**：详见 `rules/CORE.md`。`git stash` 一律禁止；`git commit`/`git push` 仅用户显式指令 + Guard 确认后执行；**禁止自动新增/改动分支**。Pre-bash-guard 拦截 stash/commit/push/建切分支（`GIT_OPTS` 覆盖 `-C/--git-dir/--work-tree/-c` 变体）。

## 危险操作防护

### 禁止操作（需确认）

```bash
git push --force origin main        # 强制推保护分支
git push origin --delete <branch>   # 删除远程分支
git rebase -i HEAD~10               # 交互式变基
git reset --hard HEAD~5             # 硬重置
```

### 安全替代

```bash
git branch backup-branch            # 用户本地创建备份（Agent 禁止执行，R19）
git reset --soft HEAD~1             # 撤销提交（保留变更）
git revert <commit-hash>            # 创建撤销提交
```

## Git Hooks

### pre-commit

```bash
#!/bin/sh
npm run lint && npm run format:check
if git diff --cached | grep -E "(password|secret|api_key)"; then
  echo "发现敏感信息，请移除后再提交"; exit 1
fi
```

### commit-msg

```bash
#!/bin/sh
commit_msg=$(cat "$1")
pattern="^(feat|fix|docs|style|refactor|perf|test|chore|ci|revert)(\(.+\))?: .{1,50}"
if ! echo "$commit_msg" | grep -qE "$pattern"; then
  echo "格式错误，正确: type(scope): subject"; exit 1
fi
```

## .gitignore 规范

```gitignore
node_modules/ vendor/ __pycache__/   # 依赖
dist/ build/ *.o                     # 构建输出
.env .env.local .env.*.local         # 环境配置
.idea/ .vscode/ *.swp                # IDE
.DS_Store Thumbs.db                  # 系统文件
*.log logs/                          # 日志
*.tmp *.temp .cache/                 # 临时文件
```
