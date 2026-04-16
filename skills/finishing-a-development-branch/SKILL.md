---
name: finishing-a-development-branch
description: 开发分支完成时检查、清理、创建PR、合并策略
triggers: [分支完成, PR创建, 合并分支, 分支清理, 开发完成, 当开发分支工作完成, 需要决定合并策略, 准备创建PR, 执行合并前检查]
---

# 分支完成

## @Examples

```
用户: "功能开发完了，怎么合并？"
Claude: /finishing-a-development-branch → 检查清单 → 创建PR → 合并策略

用户: "这个分支可以合并了吗？"
Claude: /finishing-a-development-branch → 运行检查 → 确认可合并 → 准备合并
```

## 检查清单

### 1. 代码质量检查

```bash
# 运行所有检查
□ 测试通过（npm test / pytest）
□ Lint 通过（npm run lint / ruff check）
□ 类型检查通过（tsc --noEmit / mypy）
□ 构建成功（npm run build）
```

### 2. Git 状态检查

```bash
# 分支状态
□ 所有变更已提交
□ 提交信息符合规范
□ 无敏感信息提交
□ 提交数量合理（可考虑 squash）

# 同步状态
□ 已拉取最新主分支
□ 已解决所有冲突
□ 分支历史整洁
□ 分支已推送到远程
```

### 3. 审查状态

- [ ] Code Review 通过
- [ ] 所有讨论已解决

### 4. 文档检查

```bash
# 必要文档
□ README 已更新（如有新功能）
□ API 文档已更新（如有接口变更）
□ CHANGELOG 已更新
□ 注释充分
```

---

## 合并策略选择

### 根据场景选择策略

| 场景 | 推荐策略 | 原因 |
|------|----------|------|
| 功能分支 → develop | Squash Merge | 保持历史整洁 |
| Release 分支 → main | Merge Commit | 保留发布记录 |
| Hotfix 分支 → main | Merge Commit | 追踪紧急修复 |
| 小改进 | Squash Merge | 减少噪音 |
| 大功能（多人协作） | Rebase + Merge | 保留细节历史 |

### 合并命令参考

```bash
# Squash Merge
git checkout develop
git merge --squash feature/xxx
git commit -m "feat(xxx): add feature description"

# Merge Commit（保留历史）
git checkout main
git merge --no-ff release/1.2.0

# Rebase 后合并
git checkout feature/xxx
git rebase develop
git checkout develop
git merge feature/xxx
```

---

## 完成流程

### 步骤 1：最终验证

```markdown
## 分支完成验证

### 基本信息
- 分支名称：feature/xxx
- 目标分支：develop
- 变更文件：X 个
- 提交数量：X 个

### 质量检查
- [ ] 测试覆盖率 > 80%
- [ ] 无 Lint 错误
- [ ] 无类型错误
- [ ] 构建成功

### 文档检查
- [ ] README 已更新
- [ ] 必要注释已添加
```

### 步骤 2：决定合并方式

```markdown
## 合并决策

当前分支：feature/user-auth
提交数量：5 个
变更范围：适中

推荐策略：Squash Merge

原因：
- 单一功能特性
- 提交数量适中
- 保持主分支历史整洁
```

### 步骤 3：执行合并

```bash
# 1. 切换到目标分支
git checkout develop

# 2. 拉取最新代码
git pull origin develop

# 3. 执行合并
git merge --squash feature/user-auth

# 4. 编写合并提交
git commit -m "feat(auth): add user authentication

- Add login/logout functionality
- Add JWT token validation
- Add user session management

Closes #123"

# 5. 推送
git push origin develop
```

### 步骤 4：清理分支

```bash
# 删除本地分支
git branch -d feature/user-auth

# 删除远程分支（如已推送）
git push origin --delete feature/user-auth

# 清理已合并的分支
git fetch -p && git branch -vv | grep ': gone]' | awk '{print $1}' | xargs -r git branch -d
```

---

## PR 准备模板

```markdown
## [类型] 简短描述

### 变更内容
- 具体变更1
- 具体变更2

### 变更类型
- [ ] 新功能 (feat)
- [ ] Bug 修复 (fix)
- [ ] 重构 (refactor)
- [ ] 文档 (docs)
- [ ] 其他

### 测试验证
- [ ] 单元测试已添加/更新
- [ ] 集成测试已通过
- [ ] 手动测试完成

### 影响范围
<!-- 列出可能受影响的模块 -->

### 截图（如有UI变更）
<!-- 添加截图 -->

### 相关问题
Closes #xxx
```

---

## 决策树

```
开发完成
    │
    ├─ 测试通过？ ─否─→ 修复测试
    │
    └─ 是
        │
        ├─ 冲突？ ─是─→ 解决冲突
        │
        └─ 否
            │
            ├─ 需要 PR？ ─是─→ 创建 PR
            │
            └─ 否（直接合并）
                │
                ├─ 选择合并策略
                │
                └─ 执行合并 → 清理分支
```

---

## 相关技能

- `git-workflow` - Git 工作流管理
- `git-worktrees` - 并行开发隔离
- `code-review-workflow` - 代码审查工作流
- `verification-checklist` - 完成验证
