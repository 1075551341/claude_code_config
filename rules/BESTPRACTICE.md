---
name: bestpractice
description: 综合最佳实践规则（错误处理、提示词设计、代码精炼）
alwaysApply: true
layer: skeleton
source: shanraisshan/claude-code-best-practice + x1xhlol/system-prompts-and-models-of-ai-tools + Chalarangelo/30-seconds-of-code
---

# 综合最佳实践

> 来源：shanraisshan/claude-code-best-practice + x1xhlol/system-prompts + Chalarangelo/30-seconds-of-code

## 错误处理最佳实践

- 每层显式处理，永不静默吞错
- 错误信息包含上下文（操作名、输入摘要、原始错误）
- 自定义错误类携带机器可读 code
- 已知错误 → 业务码 + 友好提示；未知错误 → 完整日志 + 通用错误码
- 异步操作必须 try/catch，禁止裸 await

## 提示词设计原则

- 明确角色定位和职责边界
- 结构化输出格式（JSON Schema / Markdown Template）
- Few-shot 示例优于长描述
- 约束条件用否定式（禁止X 优于 建议不X）
- 分步推理优于一次性输出

## 代码精炼理念

- 优先使用语言内置方法而非手写算法
- 函数名即文档，减少注释依赖
- 数据结构选择决定代码复杂度
- 不可变数据流优于可变状态
- 组合优于继承，函数优于类

## API 设计

- RESTful 资源命名用名词复数
- 版本化：`/v1/resources`
- 幂等设计：PUT/DELETE 天然幂等，POST 需显式保证
- 分页、过滤、排序参数统一格式
- 响应包含自我描述（_links / _meta）

## 日志规范

- 结构化日志（JSON 格式），禁止纯文本拼接
- 级别语义：DEBUG < INFO < WARN < ERROR < FATAL
- 敏感字段脱敏：password/token/secret/card_number
- 请求链路追踪：request_id 贯穿全链路
