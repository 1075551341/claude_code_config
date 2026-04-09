---
name: api-documentation
description: API文档编写规范，编写清晰、完整的RESTful API文档。触发词：API文档、接口文档、RESTful文档、API说明、接口说明、Swagger、OpenAPI、API规范。
---

# API 文档编写

## 文档结构

### 标准模板
```markdown
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
| limit | int | 否 | 每页数量 | 20 |

**请求示例**
```bash
curl -X GET "https://api.example.com/v1/resources?page=1" \
  -H "Authorization: Bearer <token>"
```

**响应示例**
```json
{
  "code": 0,
  "msg": "ok",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1
  }
}
```

**错误码**
| 错误码 | 说明 |
|--------|------|
| 401 | 未授权 |
| 403 | 权限不足 |
| 500 | 服务器错误 |
```

## 接口规范

### RESTful 路径设计
```
GET    /users           # 用户列表
GET    /users/:id       # 用户详情
POST   /users           # 创建用户
PUT    /users/:id       # 全量更新
PATCH  /users/:id       # 部分更新
DELETE /users/:id       # 删除用户

GET    /users/:id/orders    # 用户订单列表
POST   /users/:id/orders    # 创建订单
```

### 统一响应格式
```json
// 成功响应
{
  "code": 0,
  "msg": "ok",
  "data": {
    // 业务数据
  }
}

// 错误响应
{
  "code": 1001,
  "msg": "参数错误",
  "data": {
    "errors": [
      {"field": "email", "message": "邮箱格式不正确"}
    ]
  }
}

// 分页响应
{
  "code": 0,
  "msg": "ok",
  "data": {
    "items": [],
    "pagination": {
      "total": 100,
      "page": 1,
      "limit": 20,
      "pages": 5
    }
  }
}
```

### HTTP 状态码规范
```
200 OK              # 成功
201 Created         # 创建成功
204 No Content      # 删除成功（无返回体）
400 Bad Request     # 参数错误
401 Unauthorized    # 未认证
403 Forbidden       # 无权限
404 Not Found       # 资源不存在
409 Conflict        # 资源冲突
422 Unprocessable   # 验证失败
500 Server Error    # 服务器错误
```

## 文档元素详解

### 参数说明格式
```markdown
| 参数名 | 类型 | 必填 | 位置 | 说明 | 默认值 | 示例 |
|--------|------|------|------|------|--------|------|
| id | string | 是 | path | 用户ID | - | "abc123" |
| name | string | 否 | query | 搜索名称 | "" | "张三" |
| role | enum | 否 | body | 用户角色 | "user" | "admin" |
```

**类型说明**
- `string` - 字符串
- `int` - 整数
- `float` - 浮点数
- `bool` - 布尔值
- `enum` - 枚举（列出可选值）
- `array` - 数组
- `object` - 对象
- `date` - 日期（ISO8601格式）

### 认证说明
```markdown
## 认证方式

### Bearer Token
请求头携带 JWT Token：
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### API Key
请求头携带 API Key：
```
X-API-Key: your-api-key
```

### OAuth 2.0
1. 获取授权码
2. 交换 access_token
3. 使用 token 请求
```

### 错误码表
```markdown
## 错误码定义

### 系统错误 (1xxx)
| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 1001 | 参数错误 | 检查请求参数 |
| 1002 | 参数缺失 | 补充必填参数 |
| 1003 | 参数格式错误 | 按文档格式调整 |

### 业务错误 (2xxx)
| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 2001 | 用户不存在 | 检查用户ID |
| 2002 | 密码错误 | 重新输入 |
| 2003 | 账户已禁用 | 联系管理员 |

### 权限错误 (3xxx)
| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 3001 | 未登录 | 先登录 |
| 3002 | 权限不足 | 申请权限 |
| 3003 | Token过期 | 刷新Token |
```

## 文档生成工具

### OpenAPI/Swagger
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
            default: 1
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserList'
```

### 从代码生成
```typescript
// 使用 tsoa 生成 Swagger
@Route("users")
export class UserController {
  @Get()
  @SuccessResponse(200, "OK")
  @Response(400, "参数错误")
  public async getUsers(
    @Query() page?: number,
    @Query() limit?: number
  ): Promise<UserListResponse> {
    // ...
  }
}
```

## 完整示例

```markdown
# 用户管理 API

## 创建用户

**POST** `/users`

### 请求体
```json
{
  "name": "张三",
  "email": "zhangsan@example.com",
  "password": "securePassword123",
  "role": "user"
}
```

### 参数说明
| 字段 | 类型 | 必填 | 说明 | 约束 |
|------|------|------|------|------|
| name | string | 是 | 用户名 | 2-50字符 |
| email | string | 是 | 邮箱 | 有效邮箱格式 |
| password | string | 是 | 密码 | 8-32字符，含大小写和数字 |
| role | enum | 否 | 角色 | user/admin，默认user |

### 成功响应 (201)
```json
{
  "code": 0,
  "msg": "ok",
  "data": {
    "id": "abc123",
    "name": "张三",
    "email": "zhangsan@example.com",
    "role": "user",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### 错误响应
- 400: 参数验证失败
- 409: 邓箱已存在
- 500: 服务器错误
```