# /ship — 合并、部署

验证全部通过后，执行合并和部署。

## 流程

1. 确认所有验证通过
2. 检查 Git 状态（无未提交变更、分支最新）
3. 创建 PR / 合并到目标分支
4. 触发部署（如适用）
5. 清理工作分支

## PR 格式

```
[type] scope: description

## Summary
- 变更点 1
- 变更点 2

## Test plan
- [x] 测试项 1
- [x] 测试项 2

## 验证清单
- [x] 构建通过
- [x] 测试通过
- [x] 安全审查通过

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

## 门控

- CI 全部通过 ✓
- Code Review 通过 ✓
- 无回滚风险 ✓
