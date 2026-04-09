---
name: api-development
description: 当需要设计RESTful API、实现API端点、编写后端接口、处理HTTP请求响应时调用此技能。触发词：API开发、REST API、接口设计、端点实现、后端接口、HTTP接口、API端点、路由设计、API文档。
---

# API 开发

## URL 结构
```
GET    /api/v1/{resource}       # 列表（支持分页/过滤）
GET    /api/v1/{resource}/:id   # 详情
POST   /api/v1/{resource}       # 创建
PUT    /api/v1/{resource}/:id   # 全量更新
PATCH  /api/v1/{resource}/:id   # 部分更新
DELETE /api/v1/{resource}/:id   # 删除
```
规则：名词复数、嵌套不超过 2 层、版本前缀 `/v1`

## 统一响应格式
```json
{ "code": 0, "msg": "ok", "data": {}, "meta": { "page": 1, "total": 100 } }
{ "code": 40001, "msg": "参数错误：email 格式无效", "data": null }
```
错误码：`4xxYY`=客户端错误，`5xxYY`=服务端错误，项目初始化时统一定义。

## 核心实现

### 入参验证（必做）
```typescript
// Zod
const schema = z.object({ email: z.string().email(), age: z.number().int().min(0).optional() })
const data = schema.parse(req.body) // 自动抛出验证错误
```

### 统一错误中间件
```typescript
app.use((err, req, res, next) => {
  if (err instanceof ValidationError)
    return res.status(400).json({ code: err.code, msg: err.message })
  logger.error(err) // 记录完整堆栈，响应不暴露
  res.status(500).json({ code: 50000, msg: '服务器内部错误' })
})
```

### 分页（大数据集用游标，非 offset）
```
GET /users?cursor=eyJpZCI6MTAwfQ&limit=20
响应：{ data: [...], nextCursor: "eyJpZCI6MTIwfQ" }
```

## 安全基线
| 风险 | 措施 |
|------|------|
| 未授权访问 | JWT/Session 统一鉴权中间件 |
| 参数注入 | 参数化查询，禁止拼接 SQL |
| 请求滥用 | 核心接口 Rate Limit |
| 数据泄露 | 错误不暴露堆栈；敏感字段加密 |
| CORS | 明确域名白名单，生产禁 `*` |

## 性能要点
- N+1：用 `include`/`JOIN` 或 DataLoader
- 禁 `SELECT *`，查询必须走索引
- 幂等 GET 加 Redis 缓存 + TTL
- 外部依赖：timeout + retry + fallback

## OpenAPI 文档示例
```yaml
/users/{id}:
  get:
    summary: 获取用户详情
    parameters:
      - { name: id, in: path, required: true, schema: { type: integer } }
    responses:
      200: { description: 成功 }
      404: { description: 用户不存在 }
```
