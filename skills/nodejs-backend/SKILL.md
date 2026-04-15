---
name: nodejs-backend
description: 开发Node.js后端应用、使用Express/Koa/NestJS框架、编写后端API服务
triggers: [Node.js后端, Express开发, Koa开发, NestJS, 后端开发, Node服务, JavaScript后端, TypeScript后端]
---

# Node.js 后端开发

## 项目结构标准

```
src/
├── app.ts              # 应用入口
├── config/             # 配置管理
│   ├── index.ts
│   └── defaults.ts
├── routes/             # 路由层（只负责路由定义）
│   ├── index.ts
│   └── user.ts
├── controllers/        # 控制器（处理请求响应）
├── services/           # 服务层（核心业务逻辑）
├── middlewares/        # 中间件
│   ├── auth.ts
│   ├── errorHandler.ts
│   └── validator.ts
├── models/             # 数据模型
├── utils/              # 工具函数
│   ├── logger.ts
│   └── response.ts
└── types/              # TypeScript 类型定义
```

## Express 标准模板

```typescript
// app.ts
import express from 'express'
import { errorHandler } from './middlewares/errorHandler'
import routes from './routes'

const app = express()

// 中间件
app.use(express.json({ limit: '10mb' }))
app.use(express.urlencoded({ extended: true }))

// 路由
app.use('/api/v1', routes)

// 错误处理（必须放最后）
app.use(errorHandler)

export default app
```

## 分层职责

### Routes 层
```typescript
// routes/user.ts - 只负责路由定义，不写业务逻辑
import { Router } from 'express'
import { UserController } from '../controllers/user'
import { auth } from '../middlewares/auth'
import { validate } from '../middlewares/validator'
import { userSchema } from '../validators/user'

const router = Router()
const controller = new UserController()

router.get('/', auth, controller.list)
router.post('/', validate(userSchema), controller.create)
router.get('/:id', controller.detail)
router.put('/:id', auth, validate(userSchema), controller.update)
router.delete('/:id', auth, controller.delete)

export default router
```

### Controller 层
```typescript
// controllers/user.ts - 处理请求响应，调用 service
import { UserService } from '../services/user'
import { success, fail } from '../utils/response'

export class UserController {
  private service = new UserService()

  list = async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { page, pageSize } = req.query
      const result = await this.service.list({ page, pageSize })
      res.json(success(result))
    } catch (err) {
      next(err)
    }
  }
}
```

### Service 层
```typescript
// services/user.ts - 核心业务逻辑，可复用
export class UserService {
  async list(params: ListParams) {
    const { page = 1, pageSize = 20 } = params
    const [data, total] = await Promise.all([
      this.model.findMany({ skip: (page - 1) * pageSize, take: pageSize }),
      this.model.count()
    ])
    return { data, total, page, pageSize }
  }
}
```

## 错误处理

```typescript
// middlewares/errorHandler.ts
import { AppError, ValidationError, AuthError } from '../types/errors'

export const errorHandler = (err, req, res, next) => {
  // 已知错误
  if (err instanceof ValidationError) {
    return res.status(400).json({ code: 40001, msg: err.message })
  }
  if (err instanceof AuthError) {
    return res.status(401).json({ code: 40101, msg: '未授权' })
  }

  // 未知错误
  logger.error('Unhandled error:', err)
  res.status(500).json({ code: 50000, msg: '服务器内部错误' })
}
```

## 常用中间件

### 请求日志
```typescript
app.use((req, res, next) => {
  const start = Date.now()
  res.on('finish', () => {
    logger.info(`${req.method} ${req.path} ${res.statusCode} ${Date.now() - start}ms`)
  })
  next()
})
```

### 请求限流
```typescript
import rateLimit from 'express-rate-limit'

app.use('/api', rateLimit({
  windowMs: 15 * 60 * 1000,  // 15分钟
  max: 100,                   // 最多100次请求
  message: { code: 42901, msg: '请求过于频繁' }
}))
```

### CORS
```typescript
import cors from 'cors'

app.use(cors({
  origin: config.corsOrigins,  // 生产环境必须配置白名单
  credentials: true
}))
```

## 性能优化

| 场景 | 方案 |
|------|------|
| 数据库查询 | 索引优化 + 分页 + 避免 N+1 |
| 大文件上传 | 流式处理 + 分片上传 |
| 高并发 | 集群模式 + Redis 缓存 |
| 慢接口 | 异步队列（Bull/BullMQ） |
| 内存泄漏 | 监控 + 及时释放引用 |

## 安全检查清单

- [ ] 输入验证（使用 Zod/Joi）
- [ ] SQL 注入防护（参数化查询）
- [ ] XSS 防护（helmet 中间件）
- [ ] CSRF 防护
- [ ] 敏感数据加密存储
- [ ] JWT/Session 安全校验
- [ ] 环境变量管理（dotenv）
- [ ] 日志脱敏（不记录密码/token）
