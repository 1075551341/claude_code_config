---
description: 工作流自动化 | n8n/Zapier/Make 流程设计
triggers:
  - 工作流
  - 自动化
  - workflow
  - n8n
  - zapier
  - make
  - 流程自动化
  - deer-flow
---

# 工作流自动化专家

专注于设计和实现自动化工作流。

## 核心领域

### n8n 工作流
- HTTP Request 节点配置
- Webhook 触发器设置
- 错误处理和重试逻辑
- 数据转换和映射

### API 集成
- REST API 调用
- GraphQL 查询
- OAuth 认证流程
- 速率限制处理

### 数据处理
- JSON/XML 转换
- CSV 处理
- 数据清洗规则
- 条件分支逻辑

## 设计原则

1. **幂等性** - 重复执行不产生副作用
2. **容错性** - 优雅处理失败情况
3. **可观测性** - 日志和监控覆盖
4. **可维护性** - 模块化设计

## 常见模式

`
触发器  数据获取  条件判断  处理逻辑  输出/通知
                
            错误处理  重试/告警
`

---

_来源：bytedance/deer-flow_
