---
description: Git 版本控制、分支管理、提交规范相关任务时启用
alwaysApply: false
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

| 类型 | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 文档更新 |
| `style` | 代码格式（不影响逻辑） |
| `refactor` | 重构 |
| `perf` | 性能优化 |
| `test` | 测试相关 |
| `chore` | 构建/工具相关 |
| `ci` | CI 配置 |
| `revert` | 回滚 |

## PR 规范

### 标题格式

```
[<type>] <scope>: <description>
示例：[feat] auth: add SSO support
```

### Code Review 检查项

```markdown
代码质量：□ 风格一致 □ 无重复 □ 命名清晰
安全性：  □ 无敏感泄露 □ 输入验证 □ 权限检查
性能：    □ 无 N+1 □ 无内存泄漏 □ 异步正确
测试：    □ 覆盖充分 □ 边界条件 □ 错误处理
```

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
git branch backup-branch            # 创建备份
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
