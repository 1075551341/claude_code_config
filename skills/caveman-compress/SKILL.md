---
name: caveman-compress
description: 输出压缩（caveman 模式）。触发词：caveman | 压缩输出 | 精简回复 | 言简意赅
layer: supplement
source: JuliusBrussee/caveman
disable-model-invocation: true
loading_tier: L3
---

# Caveman Compress

## 触发条件

- 手动：`压缩输出` / `精简回复` / `caveman` / `token 浪费`
- 自动：输出 >300字 或 上下文使用率 >40% 或 工具调用 >20次
- ⛔ 上下文 >50% 时必须启用 L2 full 或 L3 ultra 模式

## 压缩规则

1. 结论先行，细节按需
2. 删除寒暄与重复确认
3. 代码引用用路径+行号，不贴全文
4. 多步骤用 checklist 替代长段落
5. 去冗余→去解释→保留关键信息→保留代码

## 安全阀

压缩后信息不可推导→回退原文。禁止过度压缩导致丢失关键约束/铁律/触发词。

## 模式

## 四级压缩（确认）

- **L1 lite**：删除冗余句（默认 SessionStart 激活）
- **L2 full**：结构化摘要 + 指针
- **L3 ultra**：仅结论 + 下一步
- **L4 wenyan**：文言文式极简（中文项目推荐，最短表达）

### wenyan 示例
- 原："你需要使用 useMemo 来避免不必要的重新渲染"
- wenyan："重渲染→useMemo"

切换：`/caveman wenyan` 或 `caveman=wenyan`

与 RTK（shell 输出压缩）正交。来源：JuliusBrussee/caveman
