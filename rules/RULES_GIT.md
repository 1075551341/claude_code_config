---
description: Git 版本控制、分支管理、提交规范相关任务时启用
alwaysApply: false
---

# Git 规则（专用）

> 配合核心规则使用，仅在 Git 相关场景加载

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

### Trunk Based

```
main (主干)
  ├── 短期分支 (< 1天)
  └── feature flags 控制功能
```

### 分支命名规范

```markdown
功能开发：feature/ISSUE-123-user-auth
缺陷修复：fix/ISSUE-456-login-error
紧急修复：hotfix/ISSUE-789-security-patch
发布分支：release/1.2.0
文档更新：docs/api-documentation
重构：refactor/user-service
```

## Commit 规范

### Commit Message 格式

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Type 类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | feat(auth): add OAuth2 login |
| `fix` | Bug 修复 | fix(api): resolve null pointer in user service |
| `docs` | 文档更新 | docs: update API documentation |
| `style` | 代码格式（不影响逻辑） | style: format code with prettier |
| `refactor` | 重构 | refactor(user): extract validation logic |
| `perf` | 性能优化 | perf(db): optimize user query |
| `test` | 测试相关 | test(user): add unit tests for auth |
| `chore` | 构建/工具相关 | chore: update dependencies |
| `ci` | CI 配置 | ci: add GitHub Actions workflow |
| `revert` | 回滚 | revert: feat(auth): add OAuth2 login |

### Commit 示例

```
feat(order): add order cancellation feature

- Add cancel endpoint to order API
- Implement cancellation logic in order service
- Add unit tests for cancellation scenarios

Closes #123
```

## Merge/Pull Request 规范

### PR 标题格式

```
[<type>] <scope>: <description>

示例：
[feat] auth: add SSO support
[fix] api: resolve timeout issue
```

### PR 描述模板

```markdown
## 变更概述
<!-- 简述本次变更的目的和内容 -->

## 变更类型
- [ ] 新功能 (feat)
- [ ] Bug 修复 (fix)
- [ ] 重构 (refactor)
- [ ] 文档 (docs)
- [ ] 其他

## 测试清单
- [ ] 单元测试已通过
- [ ] 集成测试已通过
- [ ] 手动测试完成

## 影响范围
<!-- 列出受影响的模块或接口 -->

## 截图/演示
<!-- 如有 UI 变更，附上截图 -->

## 相关 Issue
Closes #xxx
```

### Code Review 检查项

```markdown
代码质量：
□ 代码风格一致
□ 无重复代码
□ 命名清晰
□ 注释充分

安全性：
□ 无敏感信息泄露
□ 输入验证完整
□ 权限检查正确

性能：
□ 无 N+1 查询
□ 无内存泄漏风险
□ 异步操作正确

测试：
□ 测试覆盖充分
□ 边界条件测试
□ 错误处理测试
```

## 危险操作防护

### 禁止操作（需确认）

```bash
# 强制推送到保护分支
git push --force origin main
git push -f origin master

# 删除远程分支
git push origin --delete <branch>

# 重写历史
git push --force-with-lease origin main
git rebase -i HEAD~10  # 交互式变基

# 硬重置
git reset --hard HEAD~5
git checkout -- .
```

### 安全操作

```bash
# 创建备份分支
git branch backup-branch

# 查看变更
git log --oneline -10
git diff HEAD~5

# 安全变基
git rebase -i --autosquash HEAD~5

# 撤销提交（保留变更）
git reset --soft HEAD~1
```

## 常用命令速查

### 分支操作

```bash
# 创建并切换分支
git checkout -b feature/new-feature

# 删除已合并分支
git branch -d feature/old-feature

# 查看所有分支
git branch -a

# 同步远程分支
git fetch --prune
```

### 提交操作

```bash
# 增量提交
git add -p

# 修改最后一次提交
git commit --amend

# 交互式暂存
git stash push -m "work in progress"
git stash pop

# 查看提交历史
git log --graph --oneline --all
```

### 合并操作

```bash
# 合并分支（保留历史）
git merge --no-ff feature/xxx

# 变基合并
git rebase feature/xxx

# 解决冲突后继续
git add .
git rebase --continue

# 放弃变基
git rebase --abort
```

### 撤销操作

```bash
# 撤销工作区修改
git restore <file>

# 撤销暂存
git restore --staged <file>

# 撤销提交（保留变更）
git reset --soft HEAD~1

# 撤销提交（丢弃变更）
git reset --hard HEAD~1

# 创建撤销提交
git revert <commit-hash>
```

## .gitignore 规范

```gitignore
# 依赖
node_modules/
vendor/
__pycache__/

# 构建输出
dist/
build/
*.o

# 环境配置
.env
.env.local
.env.*.local

# IDE
.idea/
.vscode/
*.swp

# 系统文件
.DS_Store
Thumbs.db

# 日志
*.log
logs/

# 临时文件
*.tmp
*.temp
.cache/
```

## Git Hooks

### pre-commit

```bash
#!/bin/sh
# 运行 lint 和格式检查
npm run lint
npm run format:check

# 检查敏感信息
if git diff --cached | grep -E "(password|secret|api_key)"; then
  echo "发现敏感信息，请移除后再提交"
  exit 1
fi
```

### commit-msg

```bash
#!/bin/sh
# 验证 commit message 格式
commit_msg=$(cat "$1")
pattern="^(feat|fix|docs|style|refactor|perf|test|chore|ci|revert)(\(.+\))?: .{1,50}"

if ! echo "$commit_msg" | grep -qE "$pattern"; then
  echo "Commit message 格式错误"
  echo "正确格式: type(scope): subject"
  echo "示例: feat(auth): add login feature"
  exit 1
fi
```

## Git 工作流最佳实践

```markdown
提交前：
□ 拉取最新代码
□ 运行测试
□ 代码格式化
□ 检查敏感信息

提交时：
□ 原子提交（一个功能一个提交）
□ 清晰的 commit message
□ 关联 Issue

合并前：
□ 解决冲突
□ Code Review
□ 测试通过

合并后：
□ 删除功能分支
□ 更新本地分支
```