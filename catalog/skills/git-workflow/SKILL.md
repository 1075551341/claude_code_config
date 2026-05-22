---
name: git-workflow
description: 管理Git分支
triggers: [管理Git分支, 规范提交信息, 处理Git冲突, 设计Git工作流]
---

# Git 工作流

## 分支命名规范

```
main/master      # 生产分支，受保护
develop          # 开发分支
feature/*        # 功能分支：feature/user-auth
bugfix/*         # Bug 修复：bugfix/login-error
hotfix/*         # 紧急修复：hotfix/security-patch
release/*        # 发布分支：release/v1.2.0
```

## 工作流程

### Git Flow
```
feature → develop → release → main
                   ↓
                 hotfix → main
```

### GitHub Flow（简化版）
```
feature → main（通过 PR 合并）
```

## 提交规范

### Commit Message 格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型
| 类型 | 说明 | 示例 |
|------|------|------|
| feat | 新功能 | feat(user): 添加用户登录功能 |
| fix | Bug 修复 | fix(api): 修复请求超时问题 |
| docs | 文档更新 | docs: 更新 README |
| style | 代码格式 | style: 格式化代码 |
| refactor | 重构 | refactor(utils): 优化日期处理函数 |
| perf | 性能优化 | perf(list): 虚拟滚动优化 |
| test | 测试 | test(user): 添加登录单元测试 |
| chore | 构建/工具 | chore: 更新依赖版本 |
| ci | CI 配置 | ci: 添加自动部署配置 |

### 完整示例
```
feat(user): 添加用户注册功能

- 实现邮箱验证
- 添加密码强度校验
- 发送欢迎邮件

Closes #123
```

## 常用命令

### 分支操作
```bash
# 创建并切换分支
git checkout -b feature/user-auth

# 切换分支
git checkout develop

# 合并分支（先切换到目标分支）
git checkout main
git merge --no-ff feature/user-auth

# 删除已合并的分支
git branch -d feature/user-auth

# 删除远程分支
git push origin --delete feature/user-auth
```

### 撤销操作
```bash
# 撤销工作区修改
git checkout -- <file>

# 撤销暂存
git reset HEAD <file>

# 撤销最近一次提交（保留修改）
git reset --soft HEAD~1

# 撤销最近一次提交（丢弃修改）
git reset --hard HEAD~1

# 修改最后一次提交信息
git commit --amend -m "新的提交信息"
```

### 暂存工作
```bash
# 暂存当前修改
git stash save "描述信息"

# 查看暂存列表
git stash list

# 恢复最近暂存
git stash pop

# 恢复指定暂存
git stash pop stash@{1}
```

### 查看历史
```bash
# 查看提交历史
git log --oneline --graph --all

# 查看文件修改历史
git log -p <file>

# 查看某次提交详情
git show <commit-hash>

# 查看谁修改了某行
git blame <file>
```

### 远程操作
```bash
# 查看远程仓库
git remote -v

# 添加远程仓库
git remote add upstream <url>

# 拉取远程更新
git fetch origin

# 拉取并合并
git pull origin develop

# 推送分支
git push origin feature/user-auth

# 推送并设置上游
git push -u origin feature/user-auth
```

## Code Review 检查项

### 代码质量
- [ ] 代码是否符合项目规范
- [ ] 是否有重复代码可以抽取
- [ ] 是否有未使用的代码/变量
- [ ] 错误处理是否完善

### 安全性
- [ ] 是否有硬编码的敏感信息
- [ ] 输入验证是否完善
- [ ] 权限检查是否正确

### 性能
- [ ] 是否有 N+1 查询
- [ ] 大数据量处理是否合理
- [ ] 是否有不必要的计算

### 测试
- [ ] 是否有对应的测试用例
- [ ] 边界条件是否覆盖
- [ ] 测试是否通过

## 常见问题处理

### 合并冲突
```bash
# 1. 拉取最新代码
git fetch origin
git checkout feature/user-auth
git rebase origin/develop

# 2. 解决冲突后
git add <解决冲突的文件>
git rebase --continue

# 3. 如果想放弃 rebase
git rebase --abort
```

### 错误提交到 main
```bash
# 1. 创建新分支保存修改
git checkout -b feature/saved-work

# 2. 回退 main 分支
git checkout main
git reset --hard origin/main

# 3. 继续在新分支工作
git checkout feature/saved-work
```

### 提交信息写错
```bash
# 修改最后一次提交信息
git commit --amend

# 修改历史提交信息（交互式）
git rebase -i HEAD~3
# 将 pick 改为 reword
```

### 大文件误提交
```bash
# 从历史中彻底删除
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch path/to/large-file' \
  --prune-empty --tag-name-filter cat -- --all

# 强制推送
git push origin --force --all

# 清理本地仓库
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

## Git Hooks

### pre-commit
```bash
#!/bin/sh
# .git/hooks/pre-commit

# 运行 lint
npm run lint

# 运行测试
npm run test

# 检查是否有敏感信息
if git diff --cached | grep -E "(password|secret|token)"; then
  echo "发现敏感信息，请检查"
  exit 1
fi
```

### commit-msg
```bash
#!/bin/sh
# .git/hooks/commit-msg

# 检查提交信息格式
pattern="^(feat|fix|docs|style|refactor|perf|test|chore)(\(.+\))?: .{1,50}"
if ! grep -qE "$pattern" "$1"; then
  echo "提交信息格式错误"
  echo "格式: type(scope): subject"
  echo "示例: feat(user): 添加登录功能"
  exit 1
fi
```

## 最佳实践

1. **频繁提交**：小步快跑，每个逻辑变更一次提交
2. **有意义的提交信息**：描述做了什么，为什么做
3. **提交前检查**：确保代码可运行，测试通过
4. **保持分支整洁**：定期 rebase develop，避免过多 merge commit
5. **Code Review**：所有代码合并前必须经过审查
6. **保护主分支**：禁止直接推送到 main/develop