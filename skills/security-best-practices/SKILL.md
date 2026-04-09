---
name: security-best-practices
description: 当需要进行安全开发、防护常见漏洞、处理敏感数据、实现安全认证时调用此技能。触发词：安全开发、安全防护、OWASP、XSS防护、SQL注入防护、CSRF防护、安全审计、漏洞防护、敏感数据加密。
---

# 安全最佳实践

## 安全开发原则

```
🛡️ 最小权限原则 - 只授予必要的权限
🔒 纵深防御 - 多层安全措施
🔐 默认安全 - 安全是默认配置
🔍 输入验证 - 永不信任用户输入
📊 审计日志 - 记录关键操作
```

## OWASP Top 10 防护

### 1. SQL 注入

```typescript
// ❌ 危险：字符串拼接
const query = `SELECT * FROM users WHERE id = ${userId}`

// ✅ 安全：参数化查询
const query = 'SELECT * FROM users WHERE id = ?'
const result = await db.query(query, [userId])

// ✅ 安全：ORM 查询
const user = await prisma.user.findFirst({ where: { id: userId } })
```

### 2. XSS（跨站脚本攻击）

```typescript
// ❌ 危险：直接插入 HTML
element.innerHTML = userInput

// ✅ 安全：文本内容
element.textContent = userInput

// ✅ 安全：使用框架自动转义
<div>{userInput}</div>

// ✅ 安全：使用 DOMPurify 清理
import DOMPurify from 'dompurify'
const clean = DOMPurify.sanitize(userInput)
```

### 3. CSRF（跨站请求伪造）

```typescript
// 后端：生成 CSRF Token
import csrf from 'csurf'
const csrfProtection = csrf({ cookie: true })

// 前端：携带 Token
fetch('/api/user', {
  method: 'POST',
  headers: {
    'X-CSRF-Token': csrfToken
  }
})

// 或者使用 SameSite Cookie
app.use(session({
  cookie: { sameSite: 'strict' }
}))
```

### 4. 认证与会话安全

```typescript
// ✅ JWT 安全配置
const token = jwt.sign(
  { userId: user.id, role: user.role },
  process.env.JWT_SECRET,
  {
    expiresIn: '1h',           // 短过期时间
    issuer: 'your-app',
    audience: 'your-app'
  }
)

// ✅ 安全的密码存储
import bcrypt from 'bcrypt'
const hashedPassword = await bcrypt.hash(password, 12) // 高 cost factor

// ✅ 登录失败限制
import rateLimit from 'express-rate-limit'
const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5, // 15 分钟内最多 5 次
  message: '登录失败次数过多，请稍后再试'
})
```

### 5. 敏感数据保护

```typescript
// ✅ 环境变量管理敏感配置
import dotenv from 'dotenv'
dotenv.config()

const config = {
  dbPassword: process.env.DB_PASSWORD,
  jwtSecret: process.env.JWT_SECRET,
  apiKey: process.env.API_KEY
}

// ✅ 日志脱敏
function sanitizeLog(data: any) {
  const sensitiveFields = ['password', 'token', 'creditCard', 'ssn']
  return Object.keys(data).reduce((acc, key) => {
    if (sensitiveFields.includes(key)) {
      acc[key] = '***REDACTED***'
    } else {
      acc[key] = data[key]
    }
    return acc
  }, {} as any)
}

// ✅ 响应过滤
function toPublicUser(user: User) {
  const { password, salt, ...publicUser } = user
  return publicUser
}
```

### 6. 文件上传安全

```typescript
// ✅ 文件上传安全检查
import path from 'path'
import fs from 'fs'

const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/gif']
const MAX_SIZE = 5 * 1024 * 1024 // 5MB

async function handleUpload(file: File) {
  // 1. 检查文件类型
  if (!ALLOWED_TYPES.includes(file.mimetype)) {
    throw new Error('不支持的文件类型')
  }

  // 2. 检查文件大小
  if (file.size > MAX_SIZE) {
    throw new Error('文件过大')
  }

  // 3. 生成安全的文件名
  const ext = path.extname(file.name)
  const safeName = `${Date.now()}-${crypto.randomUUID()}${ext}`

  // 4. 存储到安全目录
  const uploadDir = path.join(process.cwd(), 'uploads')
  // 确保不会路径遍历
  const safePath = path.resolve(uploadDir, safeName)
  if (!safePath.startsWith(uploadDir)) {
    throw new Error('非法路径')
  }

  // 5. 可选：重新处理图片去除恶意代码
  // await sharp(file.buffer).toFile(safePath)
}
```

### 7. API 安全

```typescript
// ✅ 完整的 API 安全中间件配置
import helmet from 'helmet'
import cors from 'cors'
import rateLimit from 'express-rate-limit'
import mongoSanitize from 'express-mongo-sanitize'

const app = express()

// 安全 Headers
app.use(helmet())

// CORS 配置
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || [],
  credentials: true
}))

// 请求限流
app.use('/api', rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100
}))

// MongoDB 注入防护
app.use(mongoSanitize())

// 参数验证
import { body, validationResult } from 'express-validator'
app.post('/api/users',
  body('email').isEmail().normalizeEmail(),
  body('password').isLength({ min: 8 }),
  (req, res) => {
    const errors = validationResult(req)
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() })
    }
    // 处理请求...
  }
)
```

### 8. 依赖安全

```bash
# 定期检查依赖漏洞
pnpm audit

# 自动修复
pnpm audit --fix

# 使用 pnpm 的安全特性
# package.json
{
  "pnpm": {
    "overrides": {
      "vulnerable-package": "^2.0.0"
    }
  }
}
```

## 安全检查清单

### 代码层面

- [ ] 所有用户输入都经过验证和清理
- [ ] SQL 使用参数化查询
- [ ] 敏感数据加密存储
- [ ] 密码使用强哈希算法
- [ ] JWT/Session 配置安全
- [ ] 文件上传有类型和大小限制
- [ ] 错误信息不暴露系统细节
- [ ] 日志不记录敏感信息

### 配置层面

- [ ] HTTPS 强制使用
- [ ] CORS 正确配置
- [ ] 安全 Headers 设置（helmet）
- [ ] 请求限流配置
- [ ] 依赖定期审计

### 运维层面

- [ ] 环境变量管理
- [ ] 密钥定期轮换
- [ ] 访问日志记录
- [ ] 异常行为监控
- [ ] 备份和恢复方案