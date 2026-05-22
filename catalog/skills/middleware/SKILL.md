---
name: middleware
description: 编写Express中间件
triggers: [编写Express中间件, 实现认证日志限流等中间件功能]
---

# Express 中间件创建

生成符合 Express 规范的中间件代码

## 使用方式

```
/middleware <type> [options]
```

**类型说明：**
- `auth` - 认证中间件
- `logger` - 日志中间件
- `error` - 错误处理中间件
- `rate-limit` - 限流中间件
- `cors` - CORS 中间件
- `validate` - 参数校验中间件

## 认证中间件

```typescript
// middlewares/auth.ts
import { Request, Response, NextFunction } from 'express'
import { verifyToken } from '../utils/jwt'
import { error } from '../utils/response'

// 扩展 Request 类型
declare global {
  namespace Express {
    interface Request {
      user?: {
        id: string
        username: string
        role: string
      }
    }
  }
}

/**
 * JWT 认证中间件
 */
export function authenticate(req: Request, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization

  if (!authHeader?.startsWith('Bearer ')) {
    return error(res, '未提供认证令牌', 401)
  }

  const token = authHeader.slice(7)

  try {
    const payload = verifyToken(token)
    req.user = payload
    next()
  } catch (err) {
    return error(res, '令牌无效或已过期', 401)
  }
}

/**
 * 角色权限中间件
 */
export function requireRole(...roles: string[]) {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user) {
      return error(res, '未认证', 401)
    }

    if (!roles.includes(req.user.role)) {
      return error(res, '权限不足', 403)
    }

    next()
  }
}

/**
 * 可选认证中间件（不强制要求登录）
 */
export function optionalAuth(req: Request, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization

  if (authHeader?.startsWith('Bearer ')) {
    const token = authHeader.slice(7)
    try {
      const payload = verifyToken(token)
      req.user = payload
    } catch {
      // 忽略错误，继续执行
    }
  }

  next()
}
```

## 日志中间件

```typescript
// middlewares/logger.ts
import { Request, Response, NextFunction } from 'express'
import logger from '../utils/logger'

export function requestLogger(req: Request, res: Response, next: NextFunction) {
  const start = Date.now()

  // 响应完成后记录日志
  res.on('finish', () => {
    const duration = Date.now() - start
    const logData = {
      method: req.method,
      url: req.originalUrl,
      status: res.statusCode,
      duration: `${duration}ms`,
      ip: req.ip,
      userAgent: req.get('user-agent'),
    }

    if (res.statusCode >= 400) {
      logger.warn('请求失败', logData)
    } else {
      logger.info('请求完成', logData)
    }
  })

  next()
}
```

## 错误处理中间件

```typescript
// middlewares/errorHandler.ts
import { Request, Response, NextFunction } from 'express'
import logger from '../utils/logger'

interface AppError extends Error {
  status?: number
  code?: string
}

export function errorHandler(
  err: AppError,
  req: Request,
  res: Response,
  next: NextFunction
) {
  const status = err.status || 500
  const message = err.message || '服务器内部错误'

  // 记录错误日志
  logger.error('未捕获的错误', {
    error: err.message,
    stack: err.stack,
    url: req.originalUrl,
    method: req.method,
    body: req.body,
  })

  // 生产环境不暴露堆栈
  const response: any = {
    code: status,
    msg: message,
  }

  if (process.env.NODE_ENV === 'development') {
    response.stack = err.stack
  }

  res.status(status).json(response)
}

// 404 处理
export function notFoundHandler(req: Request, res: Response) {
  res.status(404).json({
    code: 404,
    msg: `路由不存在: ${req.method} ${req.originalUrl}`,
  })
}

// 异步错误包装器
export function asyncHandler(fn: Function) {
  return (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve(fn(req, res, next)).catch(next)
  }
}
```

## 限流中间件

```typescript
// middlewares/rateLimit.ts
import rateLimit from 'express-rate-limit'
import RedisStore from 'rate-limit-redis'
import { redis } from '../utils/redis'

// 通用限流
export const generalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 分钟
  max: 100, // 每个 IP 最多 100 次请求
  message: {
    code: 429,
    msg: '请求过于频繁，请稍后再试',
  },
  standardHeaders: true,
  legacyHeaders: false,
})

// 登录限流（更严格）
export const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5, // 每个 IP 最多 5 次尝试
  message: {
    code: 429,
    msg: '登录尝试过多，请 15 分钟后再试',
  },
})

// API 限流
export const apiLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 分钟
  max: 60, // 每个 IP 最多 60 次请求
  message: {
    code: 429,
    msg: 'API 调用过于频繁',
  },
})

// 使用 Redis 存储（分布式限流）
export const distributedLimiter = rateLimit({
  store: new RedisStore({
    sendCommand: (...args: string[]) => redis.call(...args),
  }),
  windowMs: 60 * 1000,
  max: 100,
})
```

## 参数校验中间件

```typescript
// middlewares/validate.ts
import { Request, Response, NextFunction } from 'express'
import { z } from 'zod'
import { error } from '../utils/response'

/**
 * Zod 校验中间件工厂
 */
export function validate(schema: z.ZodSchema, source: 'body' | 'query' | 'params' = 'body') {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      const data = await schema.parseAsync(req[source])
      req[source] = data
      next()
    } catch (err) {
      if (err instanceof z.ZodError) {
        const messages = err.errors.map(e => `${e.path.join('.')}: ${e.message}`)
        return error(res, messages.join(', '), 400)
      }
      next(err)
    }
  }
}

// 使用示例
const createUserSchema = z.object({
  username: z.string().min(3).max(20),
  email: z.string().email(),
  password: z.string().min(8),
})

router.post('/users', validate(createUserSchema), handler)
```

## CORS 中间件

```typescript
// middlewares/cors.ts
import cors from 'cors'

// 开发环境配置
export const devCors = cors({
  origin: true, // 允许所有来源
  credentials: true,
})

// 生产环境配置
export const prodCors = cors({
  origin: ['https://example.com', 'https://api.example.com'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
})
```

## 中间件组合

```typescript
// 组合多个中间件
export const protectedRoute = [authenticate, apiLimiter]
export const adminRoute = [authenticate, requireRole('admin')]
export const publicApi = [apiLimiter]
```