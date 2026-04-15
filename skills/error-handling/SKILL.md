---
name: error-handling
description: 处理程序错误
triggers: [处理程序错误, 实现异常捕获, 设计错误处理策略, 编写错误日志]
---

# 错误处理

## 错误处理原则

```
🛡️ 防御式编程 - 假设一切都会出错
📊 错误分类 - 区分业务错误和系统错误
📝 完整日志 - 记录足够的问题诊断信息
💬 友好提示 - 用户能理解的错误信息
🔄 优雅降级 - 部分失败不影响整体
```

## 错误分类体系

### 错误类型定义

```typescript
// types/errors.ts

// 基础错误类
class AppError extends Error {
  constructor(
    public code: number,
    message: string,
    public statusCode = 400
  ) {
    super(message)
    this.name = 'AppError'
  }
}

// 验证错误
class ValidationError extends AppError {
  constructor(message: string, public field?: string) {
    super(40001, message, 400)
    this.name = 'ValidationError'
  }
}

// 认证错误
class AuthError extends AppError {
  constructor(message = '未授权') {
    super(40101, message, 401)
    this.name = 'AuthError'
  }
}

// 权限错误
class ForbiddenError extends AppError {
  constructor(message = '无权限') {
    super(40301, message, 403)
    this.name = 'ForbiddenError'
  }
}

// 资源不存在
class NotFoundError extends AppError {
  constructor(resource = '资源') {
    super(40401, `${resource}不存在`, 404)
    this.name = 'NotFoundError'
  }
}

// 业务逻辑错误
class BusinessError extends AppError {
  constructor(code: number, message: string) {
    super(code, message, 400)
    this.name = 'BusinessError'
  }
}

// 外部服务错误
class ExternalServiceError extends AppError {
  constructor(service: string) {
    super(50301, `${service}服务暂时不可用`, 503)
    this.name = 'ExternalServiceError'
  }
}
```

### 错误码规范

```
格式：XXYYZ
XX: 模块代码（00=通用，01=用户，02=订单...）
YY: 错误类型（01=参数，02=认证，03=权限，04=资源，05=业务）
Z: 具体错误序号

示例：
40001 - 通用参数错误
40101 - 通用认证错误
10101 - 用户参数错误
10201 - 用户认证错误
10501 - 用户业务错误（如余额不足）
```

## 后端错误处理

### Express 中间件

```typescript
// middlewares/errorHandler.ts
import { Request, Response, NextFunction } from 'express'
import { AppError, ValidationError, AuthError } from '../types/errors'
import logger from '../utils/logger'

export function errorHandler(
  err: Error,
  req: Request,
  res: Response,
  _next: NextFunction
) {
  // 已知错误
  if (err instanceof AppError) {
    logger.warn('业务错误', {
      code: err.code,
      message: err.message,
      path: req.path,
      method: req.method
    })

    return res.status(err.statusCode).json({
      code: err.code,
      msg: err.message,
      data: null
    })
  }

  // 参数验证错误（express-validator）
  if (err.name === 'ValidationError') {
    return res.status(400).json({
      code: 40001,
      msg: err.message,
      data: null
    })
  }

  // 未知错误
  logger.error('未处理的错误', {
    error: err.message,
    stack: err.stack,
    path: req.path,
    method: req.method,
    body: req.body
  })

  res.status(500).json({
    code: 50000,
    msg: process.env.NODE_ENV === 'production'
      ? '服务器内部错误'
      : err.message,
    data: null
  })
}

// 异步错误包装器
export function asyncHandler(
  fn: (req: Request, res: Response, next: NextFunction) => Promise<any>
) {
  return (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve(fn(req, res, next)).catch(next)
  }
}
```

### 路由使用

```typescript
// routes/user.ts
import { Router } from 'express'
import { asyncHandler } from '../middlewares/errorHandler'
import { NotFoundError, ValidationError } from '../types/errors'

const router = Router()

router.get('/:id', asyncHandler(async (req, res) => {
  const { id } = req.params

  // 参数验证
  if (!id || !/^\d+$/.test(id)) {
    throw new ValidationError('无效的用户ID')
  }

  // 查询用户
  const user = await userService.getById(id)
  if (!user) {
    throw new NotFoundError('用户')
  }

  res.json({ code: 0, data: user })
}))

export default router
```

## 前端错误处理

### API 请求封装

```typescript
// api/request.ts
import axios from 'axios'
import { message } from 'ant-design-vue'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000
})

// 响应拦截
request.interceptors.response.use(
  (response) => {
    const { data } = response

    // 业务错误
    if (data.code !== 0) {
      handleBusinessError(data.code, data.msg)
      return Promise.reject(new Error(data.msg))
    }

    return data.data
  },
  (error) => {
    // HTTP 错误
    if (error.response) {
      const { status, data } = error.response
      handleHttpError(status, data?.msg)
    } else if (error.code === 'ECONNABORTED') {
      message.error('请求超时，请稍后重试')
    } else {
      message.error('网络错误，请检查网络连接')
    }

    return Promise.reject(error)
  }
)

function handleBusinessError(code: number, msg: string) {
  // 特殊错误码处理
  if (code === 40101) {
    // 未授权，跳转登录
    localStorage.removeItem('token')
    window.location.href = '/login'
    return
  }

  if (code === 40301) {
    message.error('您没有权限执行此操作')
    return
  }

  // 显示错误信息
  message.error(msg || '操作失败')
}

function handleHttpError(status: number, msg?: string) {
  const errorMap: Record<number, string> = {
    400: '请求参数错误',
    401: '未授权，请重新登录',
    403: '拒绝访问',
    404: '请求的资源不存在',
    500: '服务器内部错误',
    502: '网关错误',
    503: '服务暂不可用',
    504: '网关超时'
  }

  message.error(msg || errorMap[status] || '请求失败')
}

export default request
```

### 组件错误边界（React）

```typescript
// components/ErrorBoundary.tsx
import { Component, ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('组件错误:', error, errorInfo)
    // 上报错误
    // reportError(error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="error-fallback">
          <h2>出错了</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => window.location.reload()}>
            刷新页面
          </button>
        </div>
      )
    }

    return this.props.children
  }
}

// 使用
<ErrorBoundary>
  <App />
</ErrorBoundary>
```

### Vue 错误处理

```typescript
// main.ts
import { createApp } from 'vue'

const app = createApp(App)

// 全局错误处理
app.config.errorHandler = (err, instance, info) => {
  console.error('Vue 错误:', err)
  console.error('组件:', instance?.$options?.name)
  console.error('错误信息:', info)

  // 上报错误
  // reportError(err, info)
}

// 全局警告处理（开发环境）
if (import.meta.env.DEV) {
  app.config.warnHandler = (msg, instance, trace) => {
    console.warn('Vue 警告:', msg)
    console.warn('组件:', instance?.$options?.name)
    console.warn('追踪:', trace)
  }
}
```

## 日志记录

### 结构化日志

```typescript
// utils/logger.ts
import winston from 'winston'

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
    new winston.transports.File({ filename: 'logs/combined.log' })
  ]
})

// 开发环境输出到控制台
if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple()
  }))
}

export default logger

// 使用示例
logger.info('用户登录', { userId: '123', ip: '192.168.1.1' })
logger.error('支付失败', { orderId: '456', error: '余额不足' })
```

## 错误处理检查清单

- [ ] 所有已知错误都有明确的错误码和消息
- [ ] 错误信息对用户友好
- [ ] 敏感信息不在错误响应中暴露
- [ ] 错误日志包含足够的诊断信息
- [ ] 异步错误被正确捕获
- [ ] 前端有错误边界/全局错误处理
- [ ] 网络错误有友好的提示和重试机制