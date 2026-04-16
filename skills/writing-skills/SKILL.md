---
name: writing-skills
description: 技能编写元技能，将TDD应用于技能文档本身
triggers:
  - 编写技能
  - 创建技能
  - 技能设计
  - skill writing
priority: P2
---
# 技能编写

## 核心理念
Writing skills IS Test-Driven Development applied to process documentation.

## 技能类型
| 类型 | 说明 | 示例 |
|------|------|------|
| Technique | 可重复的操作步骤 | brainstorming, systematic-debugging |
| Pattern | 可识别的问题-解决方案对 | context-rot-guard, quality-gate |
| Reference | 查阅型知识 | api-documentation, code-standards |

## 编写流程
1. 识别触发场景（什么时候需要这个技能）
2. 定义期望输出（技能执行后产生什么）
3. 编写指令体（步骤+约束+示例）
4. 验证技能可被正确触发和执行
5. 迭代精炼（基于使用反馈）

## 格式
YAML frontmatter（name+description+triggers+priority）+ Markdown指令体
