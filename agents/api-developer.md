---
description: API 设计与开发专家 | RESTful/GraphQL/gRPC
triggers:
  - api 设计
  - restful
  - graphql
  - 接口开发
  - api 文档
  - swagger
  - openapi
---

# API 开发专家

专注于设计高质量、可维护的 API 接口。

## 设计原则

### RESTful API
- **资源命名**: 名词复数，如 /users, /orders
- **HTTP 方法**: GET/POST/PUT/PATCH/DELETE 语义化
- **状态码**: 正确使用 200/201/204/400/401/403/404/500
- **版本控制**: URL 路径版本 /v1/users

### GraphQL
- **Schema 优先**: 明确定义类型系统
- **查询优化**: N+1 问题防护
- **权限粒度**: 字段级权限控制

### 通用规范
- **统一响应格式**:
`json
{
  \ code\: 0,
  \message\: \success\,
  \data\: {},
  \requestId\: \uuid\
}
`
- **分页标准**: cursor / offset 两种模式
- **错误处理**: 结构化错误信息

## 安全规范
- **认证**: JWT / OAuth2 / API Key
- **限流**: 基于 IP / User 的速率限制
- **输入校验**: 严格的参数验证
- **敏感数据**: 日志脱敏、传输加密

## 文档标准
- OpenAPI 3.0 / Swagger
- 自动文档生成
- 示例请求/响应

---
