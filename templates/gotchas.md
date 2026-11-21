# Gotchas 记录模板

重要且可复用的错误教训按需外化，优先复用项目已有文档，不要求每次小修都新建记录。

## 条目格式

```markdown
### [简短标题]

- **日期**：YYYY-MM-DD
- **症状**：[用户/系统观察到的现象]
- **根因**：[直接原因 → 根本原因（5-Why 链）]
- **修复**：[采取的修复措施]
- **预防**：[防止复现的措施：测试/lint 规则/文档]
- **标签**：[分类标签，如 auth, build, typescript, async]
```

## 示例

```markdown
### TypeScript 路径别名构建失败

- **日期**：2026-05-20
- **症状**：`tsc` 编译通过但运行时 `Cannot find module '@/utils'`
- **根因**：tsconfig paths 仅影响类型检查，运行时需要 tsconfig-paths 或打包器处理
- **修复**：添加 `tsconfig-paths` 到 `ts-node` 配置
- **预防**：CI 增加 `node -e "require('@/utils')"` 冒烟测试
- **标签**：typescript, build, paths
```

## 使用说明

- 调试或实现过程中遇到有复用价值的教训时追加条目
- 调试时先查 gotchas.md 检查是否为已知问题
- 如有可用记忆工具，则同步关键 gotchas 到跨会话记忆
