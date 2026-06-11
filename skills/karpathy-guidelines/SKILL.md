---
name: karpathy-guidelines
description: Karpathy 编码四原则及实施规则。触发词：简洁代码、过度设计、surgical changes、think before coding。
layer: supplement
source: forrestchang/andrej-karpathy-skills
disable-model-invocation: true
loading_tier: L3
---

# Karpathy Guidelines

## 原则一：Think Before Coding

先陈述假设再编码。遇到歧义呈现多种解读而非静默选择一个。发现更简单方案主动指出。

**实施规则**：
- 有 2+ 种解读时，列出所有并请用户选择
- 发现需求矛盾立即指出，不继续
- 方案讨论前禁止写任何代码

## 原则二：Simplicity First

能 50 行不写 200 行。禁止推测性通用化。

**实施规则**：
- 写完自问：资深工程师会说"过度设计"？→ 重写
- 能删一半行数且不丢功能？→ 做
- 不为"未来可能需要"加抽象层
- 三个相似行 > 一个过早抽象

## 原则三：Surgical Changes

只改必须改的。匹配现有风格。每条改动可追踪到用户请求。

**实施规则**：
- 只清理自己改动导致的孤儿代码（无引用的 import、死变量），不删既存死代码
- 遵守文件行数上限 800 行，超过时拆分为最小改动
- 变更前检查现有模式，新代码风格与周围一致

## 原则四：Goal-Driven

弱命令转强声明式标准。任务完成 = 验证通过。

**实施规则**：

| 弱命令 | 强声明式 |
|--------|---------|
| "加验证" | "先写无效输入测试，再使其通过" |
| "修 bug" | "先写复现测试，确认失败，再修，确认通过" |
| "优化性能" | "先测量基线，再设定目标，优化后验证达标" |
| "改一下" | "读文件→定位行→Edit→验证→确认" |

**多步验证计划**：
1. 描述完成后的预期行为
2. 列出验证步骤（命令 + 预期输出）
3. 执行验证，报告结果

## 铁律关联

R1–R11 → `CLAUDE.md` | R12(子Agent隔离) R13(制品存活) R14(版本克制) R15(pnpm优先) → `rules/CORE.md`

## 效果指标

1. 新增代码 < 目标的 2 倍行数
2. 改动文件数 = 必须修改的最小数
3. 无推测性抽象
4. PR 描述可逐行追溯到用户需求

来源：forrestchang/andrej-karpathy-skills
