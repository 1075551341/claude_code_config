---
name: finishing-a-development-branch
description: 开发分支完成时检查、清理、创建PR、合并策略
triggers: [分支完成, PR创建, 合并分支, 分支清理, 开发完成]
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

### 1. 代码状态
- [ ] 测试全部通过
- [ ] Lint 无错误
- [ ] 构建成功

### 2. Git 状态
- [ ] 提交信息规范
- [ ] 无未提交的更改
- [ ] 分支已推送到远程

### 3. 审查状态
- [ ] Code Review 通过
- [ ] 所有讨论已解决

### 4. 文档更新
- [ ] README 已更新（如需要）
- [ ] API 文档已更新
- [ ] 变更日志已记录

## PR 创建

```markdown
## [类型] 简短描述

### 变更内容
- 具体变更1
- 具体变更2

### 测试验证
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 手动验证完成

### 相关问题
Closes #123
```

## 合并策略

| 场景 | 策略 |
|------|------|
| 小改动 | Squash Merge |
| 多提交逻辑 | Rebase + Merge |
| 紧急修复 | Fast-Forward Merge |
| 需要保留历史 | Merge Commit |

## 分支清理

```bash
# 合并后删除本地分支
git branch -d feature-branch

# 删除远程分支
git push origin --delete feature-branch

# 清理已合并的分支
git fetch -p && git branch -vv | grep ': gone]' | awk '{print $1}' | xargs -r git branch -d
```
