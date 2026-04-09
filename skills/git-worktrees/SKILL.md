---
name: git-worktrees
description: 当需要并行开发多个功能、隔离开发环境、同时处理多个分支时调用此技能。触发词：git worktree、worktree、并行开发、隔离分支、多分支开发、独立工作树、分支隔离。
---

# Git Worktrees 使用

## 核心能力

**创建隔离的Git工作树，支持多分支并行开发。**

---

## 适用场景

- 并行开发多个功能
- 紧急修复与功能开发并行
- 需要隔离的开发环境
- 避免频繁切换分支

---

## 基本概念

```
主仓库：~/project/main
├── .git/worktrees/feature-a
├── .git/worktrees/hotfix-b
└── .git/worktrees/feature-c

Worktree 是独立的工作目录，共享同一个 Git 仓库。
```

---

## 常用命令

### 创建 Worktree

```bash
# 基于现有分支
git worktree add ../project-feature-a feature-a

# 基于新分支
git worktree add -b new-feature ../project-new-feature main

# 基于远程分支
git worktree add ../project-upstream upstream/main
```

### 列出 Worktrees

```bash
git worktree list
# 输出示例：
# /home/user/project/main      abc123 [main]
# /home/user/project/feature-a def456 [feature-a]
```

### 删除 Worktree

```bash
# 先清理
cd ../project-feature-a
git worktree remove .

# 或从任意位置
git worktree remove ../project-feature-a

# 强制删除（有未提交更改）
git worktree remove --force ../project-feature-a
```

### 清理过期 Worktree

```bash
# 清理已删除目录的worktree记录
git worktree prune
```

---

## 工作流程

### 并行功能开发

```bash
# 主仓库开发功能A
cd ~/project/main
# ... 开发功能A

# 需要紧急修复？创建独立worktree
git worktree add -b hotfix-123 ../project-hotfix main
cd ../project-hotfix
# ... 修复问题
git commit -m "fix: ..."
git push origin hotfix-123

# 回到主开发继续
cd ../main
# 继续功能A开发
```

### 多版本测试

```bash
# 测试不同版本
git worktree add ../project-v1.0 v1.0
git worktree add ../project-v2.0 v2.0
git worktree add ../project-main main

# 同时运行不同版本
cd ../project-v1.0 && npm start &
cd ../project-v2.0 && npm start &
```

---

## 最佳实践

### 目录命名规范

```
project/
├── main          # 主分支
├── feature-xxx   # 功能分支
├── hotfix-xxx    # 紧急修复
└── experiment    # 实验性分支
```

### 环境隔离

```bash
# 每个worktree可以有独立的依赖
cd ../project-feature-a
npm install  # 独立的node_modules
```

### 清理策略

```bash
# 定期清理已完成的worktree
git worktree list | grep -v "main" | xargs -I {} git worktree remove {}

# 或使用别名
git config --global alias.wclean '!git worktree list | grep -v main | cut -d" " -f1 | xargs -I {} git worktree remove {}'
```

---

## 注意事项

```
必须：
- 完成后及时删除
- 不同分支使用不同目录名
- 定期prune清理

避免：
- 同一分支多处checkout
- 忘记删除导致分支锁定
- 在worktree中删除分支
```

---

## 相关技能

- `git-workflow` - Git 工作流
- `code-review-workflow` - PR 审查流程