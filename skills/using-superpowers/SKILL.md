---
name: using-superpowers
description: 技能发现与使用规则。触发：开始任何对话时、不确定是否有可用技能时
---

# 技能发现与使用规则

## 核心规则

> 即使只有 1% 的可能性技能适用，也必须调用。

## 优先级

1. **用户显式指令** — 最高优先级
2. **Superpowers 技能** — 工作流技能（brainstorming, tdd, systematic-debugging 等）
3. **领域技能** — 语言/框架特定（python-patterns, react-component 等）
4. **默认系统提示** — 最低优先级

## 技能匹配信号

| 信号 | 技能 |
|------|------|
| "创建功能"、"构建组件"、"添加特性" | brainstorming |
| "写测试"、"TDD"、"先写测试" | test-driven-development |
| "debug"、"为什么失败"、"报错" | systematic-debugging |
| "审查代码"、"code review" | requesting-code-review |
| "写计划"、"实现方案" | writing-plans |
| "完成了"、"修复了"、"测试通过" | verification-before-completion |
| "深度研究"、"调研"、"技术选型" | deep-research |
| "写文档"、"RFC"、"技术规范" | doc-coauthoring |

## 技能调用原则

1. **不跳过**：技能存在就必须完整执行，不走捷径
2. **不替代**：不用自己的逻辑替代技能定义的工作流
3. **不省略**：技能的每个步骤都必须执行，不因"显而易见"而跳过
4. **铁律优先**：技能中的 Iron Law / 铁律不可违反
