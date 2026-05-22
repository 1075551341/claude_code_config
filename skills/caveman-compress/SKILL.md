---
name: caveman-compress
description: 压缩 agent 长输出与冗余解释。触发词：压缩输出、精简回复、caveman、token 浪费。
---

# Caveman Compress

## 适用

- 回复超过必要长度
- 重复已说内容
- 列表/日志可摘要

## 规则

1. 结论先行，细节按需
2. 删除寒暄与重复确认
3. 代码引用用路径+行号，不贴全文
4. 多步骤用 checklist 替代长段落

## 模式

- **lite**：删除冗余句（默认 SessionStart 激活）
- **full**：结构化摘要 + 指针
- **ultra**：仅结论 + 下一步

与 RTK（shell 输出压缩）正交。来源：JuliusBrussee/caveman
