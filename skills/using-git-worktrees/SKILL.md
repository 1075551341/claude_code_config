---
name: using-git-worktrees
description: 使用 Git Worktree 进行并行开发、隔离分支
triggers: [Git Worktree, 并行开发, 分支隔离, 多分支, worktree]
layer: supplement
source: obra/superpowers
disable-model-invocation: true
loading_tier: L3
---

# Git Worktree 并行开发

## @Examples

```
用户: "需要在另一个分支上工作，但不想丢失当前更改"
Claude: /using-git-worktrees → git worktree add（禁止 git stash；未提交改动留在当前工作区或由用户本地处理）

用户: "想并行开发两个功能"
Claude: /using-git-worktrees → 创建多个 worktree → 并行开发
```

## 为什么用 Worktree

| 方式         | 优点                                          | 缺点               |
| ------------ | --------------------------------------------- | ------------------ |
| git checkout | 简单                                          | 需要切换，丢失更改 |
| git stash    | **禁止**（R19）；改用 worktree 或用户本地处理 | 堆栈管理复杂       |
| git worktree | 并行，保留状态                                | 需要管理多个目录   |

## 基础操作

### 创建 Worktree

```bash
# 从现有分支创建 worktree（不新建分支）
git worktree add ../feature-x feature-branch

# 若需同时新建分支：由用户本地执行 git worktree add -b …（Agent 禁止，R19）
```

### 列出 Worktrees

```bash
git worktree list
# 输出：
# /path/main           abc1234 [main]
# /path/feature-x      def5678 [feature-x]
# /path/hotfix         ghi9012 [hotfix]
```

### 移除 Worktree

```bash
# 安全移除（会提示是否删除分支）
git worktree remove ../feature-x

# 强制移除（不检查分支）
git worktree remove --force ../feature-x
```

## 使用场景

### 场景 1: 切换分支开发

```bash
# 当前在 feature-a 工作，想同时看 feature-b
# 有未提交更改时禁止 git stash（R19）；用 worktree 并行，或请用户本地处理

git worktree add ../feature-b feature-b  # 须用户本条消息显式要求建/切分支或 worktree
# 在 ../feature-b 继续工作
```

### 场景 2: 并行 Code Review

```bash
# PR 需要 review，但还想继续开发
git worktree add ../review-PR pr/123-review
# 在 review-PR 目录进行 review
# 主目录继续开发
```

### 场景 3: 隔离测试环境

```bash
# 需要在干净环境测试
git worktree add ../test-clean main
# 在 test-clean 运行测试
```

## 最佳实践

1. **命名规范**: 使用有意义的目录名

   ```bash
   git worktree add ../wt-feature-user-auth feature/user-auth
   ```

2. **定期清理**: 完成工作后移除不需要的 worktree

   ```bash
   git worktree prune  # 清理已失效的 worktree
   ```

3. **注意共享状态**: .git 是共享的，commit 会影响主仓库

## 限制

- 一个分支只能有一个 worktree（除非使用 `allow dusty`）
- 工作目录不能是当前 worktree 的子目录
- 删除分支前必须先移除所有关联的 worktree
