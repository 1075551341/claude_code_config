---
name: caveman-compress
description: 压缩 agent 长输出与冗余解释。触发词：压缩输出、精简回复、caveman、token 浪费。
layer: supplement
source: JuliusBrussee/caveman
---

# Caveman Compress

## 触发条件

- 手动：`压缩输出` / `精简回复` / `caveman` / `token 浪费`
- 自动：输出 >500字 或 上下文使用率 >50%

## 压缩规则

1. 结论先行，细节按需
2. 删除寒暄与重复确认
3. 代码引用用路径+行号，不贴全文
4. 多步骤用 checklist 替代长段落
5. 去冗余→去解释→保留关键信息→保留代码

## 安全阀

压缩后信息不可推导→回退原文。禁止过度压缩导致丢失关键约束/铁律/触发词。

## 模式

- **lite**：删除冗余句（默认 SessionStart 激活）
- **full**：结构化摘要 + 指针
- **ultra**：仅结论 + 下一步
- **wenyan**：文言文式极简（中文项目推荐，最短表达）

### wenyan 示例
- 原："你需要使用 useMemo 来避免不必要的重新渲染"
- wenyan："重渲染→useMemo"

切换：`/caveman wenyan` 或 `caveman=wenyan`

与 RTK（shell 输出压缩）正交。来源：JuliusBrussee/caveman
