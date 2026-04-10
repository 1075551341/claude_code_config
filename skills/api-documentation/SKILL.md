---
name: api-documentation
description: API文档编写规范，编写清晰、完整的RESTful API文档。触发词：API文档、接口文档、RESTful文档、API说明、接口说明、Swagger、OpenAPI、API规范。
---

# API 文档编写

## 文档结构

### 标准模板

````markdown
# API 文档

## 概述

- 基础URL: `https://api.example.com/v1`
- 认证方式: Bearer Token
- 响应格式: JSON

## 接口列表

### [接口名称]

**基本信息**

- 路径: `/resources`
- 方法: `GET`
- 认证: 需要

**请求参数**
| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| page | int | 否 | 页码 | 1 |

**响应示例**

```json
{ "code": 0, "msg": "ok", "data": {...} }
```
````

```

## 接口规范

### RESTful 路径设计

```

GET /users # 列表
GET /users/:id # 详情
POST /users # 创建
PUT /users/:id # 全量更新
PATCH /users/:id # 部分更新
DELETE /users/:id # 删除

````

### 统一响应格式

```json
// 成功
{ "code": 0, "msg": "ok", "data": {...} }

// 错误
{ "code": 1001, "msg": "参数错误", "data": null }

// 分页
{ "code": 0, "msg": "ok", "data": { "items": [], "pagination": { "total": 100, "page": 1 } } }
````

### HTTP 状态码

```
200 OK              # 成功
201 Created         # 创建成功
204 No Content      # 删除成功
400 Bad Request     # 参数错误
401 Unauthorized    # 未认证
403 Forbidden       # 无权限
404 Not Found       # 资源不存在
500 Server Error    # 服务器错误
```

## 认证方式

### Bearer Token

```
Authorization: Bearer <token>
```

### API Key

```
X-API-Key: your-api-key
```

### OAuth 2.0

1. 获取授权码
2. 交换 access_token
3. 使用 token 请求

## OpenAPI/Swagger

```yaml
openapi: 3.0.0
info:
  title: API 文档
  version: 1.0.0

paths:
  /users:
    get:
      summary: 获取用户列表
      parameters:
        - name: page
          in: query
          schema:
            type: integer
      responses:
        "200":
          description: 成功
```

## 参数类型说明

- `string` - 字符串
- `int` - 整数
- `float` - 浮点数
- `bool` - 布尔值
- `enum` - 枚举
- `array` - 数组
- `object` - 对象
- `date` - 日期（ISO8601）
