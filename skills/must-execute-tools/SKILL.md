---
name: must-execute-tools
description: 强制使用的核心工具链，必须按规范调用
triggers: [必须工具, 核心工具, 工具链, 规范调用, 强制执行]
---

# 必须执行工具集

## @Examples

```
用户: "修这个bug"
Claude: /must-execute-tools → Grep同类 → 全部修复 → 再Grep确认

用户: "改配置"
Claude: /must-execute-tools → Grep引用方 → 全部同步 → 构建验证
```

## 必须工具链

| 场景 | 工具序列 |
|------|---------|
| Bug修复 | Grep同类 → 修复 → Grep确认 |
| 配置变更 | Grep引用 → 同步 → 构建验证 |
| 文件修改 | Read → Edit → Read确认 |
| 危险操作 | 确认 → 记录日志 |
| 任务完成 | verification-before-completion |

## 强制执行规则

1. Bug修复后必须 Grep 确认零遗漏
2. 配置变更后必须 Grep 所有引用方
3. 文件修改后必须 Read 确认
4. 危险操作前必须用户确认
