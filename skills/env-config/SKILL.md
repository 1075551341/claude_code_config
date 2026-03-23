# 环境变量与配置管理最佳实践

## 描述
环境变量和应用配置管理技能，涵盖 .env 文件规范、多环境配置、
密钥安全存储、配置校验和 12-Factor App 原则。

## 触发条件
当需要管理项目环境变量、配置多环境部署、处理密钥存储时使用。

## 文件命名规范

```
.env                # 默认配置（提交到 Git，不含密钥）
.env.local          # 本地覆盖（不提交，gitignore）
.env.development    # 开发环境
.env.staging        # 预发布环境
.env.production     # 生产环境（不提交到 Git）
.env.test           # 测试环境
.env.example        # 配置模板（提交到 Git，不含真实值）
```

## 配置校验模板（Zod）

```typescript
import { z } from 'zod'

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'staging', 'production', 'test']),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
  REDIS_URL: z.string().url().optional(),
  JWT_SECRET: z.string().min(32),
  CORS_ORIGIN: z.string().default('http://localhost:3000'),
  LOG_LEVEL: z.enum(['debug', 'info', 'warn', 'error']).default('info'),
})

export const env = envSchema.parse(process.env)
export type Env = z.infer<typeof envSchema>
```

## Python 配置校验（Pydantic）

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """应用配置（通过环境变量注入）"""
    app_name: str = "myapp"
    debug: bool = False
    database_url: str
    redis_url: str = "redis://localhost:6379"
    jwt_secret: str
    cors_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"

settings = Settings()
```

## .gitignore 配置

```gitignore
.env.local
.env.*.local
.env.production
.env.staging
*.pem
*.key
```

## 最佳实践

1. **分层配置**：基础值放 .env，环境覆盖放 .env.[环境名]
2. **模板文件**：维护 .env.example，新成员复制后填值
3. **类型校验**：启动时校验所有必需变量，缺少则立即报错退出
4. **密钥隔离**：密钥仅存在于 .env.local 和 CI/CD 密钥管理中
5. **禁止硬编码**：所有可变配置必须通过环境变量注入
6. **前端安全**：前端仅暴露 `VITE_*` 或 `NEXT_PUBLIC_*` 前缀的变量
