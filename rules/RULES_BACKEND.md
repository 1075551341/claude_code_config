---
description: 后端相关功能开发时启用
alwaysApply: false
---

# 后端规则（专用）

> 配合核心规则使用，仅在后端场景加载

## 技术选型

```
场景               →  推荐方案
───────────────────────────────────
RESTful API        →  Express / FastAPI / Gin
实时 / WebSocket   →  Socket.io / uWebSockets
高并发微服务       →  Go / Rust（有充分理由时）
脚本 / 工具链      →  Python / Node.js
```

不为技术栈而技术栈，选最熟悉且够用的。

## API 设计

### 路由规范

```
GET    /resources          # 列表
GET    /resources/:id      # 详情
POST   /resources          # 创建
PUT    /resources/:id      # 全量更新
PATCH  /resources/:id      # 部分更新
DELETE /resources/:id      # 删除
```

### 响应格式（统一）

```json
{ "code": 0, "msg": "ok", "data": {} }
```

错误码项目初始化时统一定义，禁止魔法数字散落。

## 函数注释模板

```python
def function_name(param_a: str, param_b: int = 0) -> dict:
    """
    描述：[一句话说明功能]
    参数：
        param_a (str): 说明
        param_b (int): 说明，默认 0
    返回：
        dict: 返回值结构说明
    异常：
        ValueError: 触发条件
    注意：
        [副作用 / 外部依赖 / 性能注意事项]
    """
```

## 数据库规范

- 查询必须走索引，禁止 `SELECT *`
- 事务操作加超时限制
- 敏感字段（密码 / Token）加密存储，日志中脱敏
- Migration 脚本必须可回滚

## 安全基线

| 风险     | 措施                            |
| -------- | ------------------------------- |
| SQL 注入 | 参数化查询，禁止拼接 SQL        |
| 认证绕过 | JWT 验证中间件统一处理          |
| 权限越权 | 每个接口显式校验角色 / 资源归属 |
| 敏感泄露 | 错误不暴露堆栈，统一错误格式    |
| 请求滥用 | 核心接口接入 Rate Limit         |

## 错误处理原则

```
1. 已知错误  → 业务码 + 友好提示（不暴露内部）
2. 未知错误  → 记录完整日志 + 返回通用错误码
3. 外部依赖  → timeout + fallback，避免雪崩
4. 所有异步  → 必须 try/catch 或 .catch()，禁止裸 await
```

## 项目结构（参考）

```
src/
  ├── routes/       # 路由注册
  ├── controllers/  # 入参校验 + 调用 service
  ├── services/     # 核心业务逻辑
  ├── models/       # 数据模型 / ORM
  ├── middlewares/  # 鉴权、限流、日志
  ├── utils/        # 通用工具
  └── config/       # 环境配置（禁止硬编码）
```

## 何时必须写文档注释

```
① 业务流程 > 3 步
② 涉及外部服务调用（标注超时 / 重试策略）
③ 定时任务 / 后台 Worker
④ 数据库 Migration 脚本

最小内容：目的 + 入参/出参 + 异常处理 + 依赖说明
```