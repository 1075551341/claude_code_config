---
name: config-management
description: 配置文件管理规范，统一管理环境变量、配置文件、敏感信息。触发词：配置管理、环境变量、env文件、配置文件、敏感信息、密钥管理、环境配置、dotenv。
---

# 配置管理

## 配置层级

```
优先级（从高到低）：
1. 命令行参数
2. 环境变量
3. 配置文件
4. 默认值

原则：
- 环境相关 → 环境变量
- 业务相关 → 配置文件
- 运行时参数 → 命令行
- 常量 → 代码默认值
```

## 环境变量管理

### .env 文件规范

```bash
# .env.example（提交到仓库）
NODE_ENV=development
PORT=3000
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-key
API_KEY=your-api-key

# .env（不提交，敏感信息）
DATABASE_URL=postgresql://real_user:real_pass@prod-host:5432/prod_db
JWT_SECRET=actual-production-secret-32chars
API_KEY=sk-prod-xxxxxxxxxxxx
```

### 环境变量命名

```bash
# 好的命名
DATABASE_URL          # 服务名 + 属性
JWT_SECRET            # 功能名 + 属性
REDIS_HOST            # 服务名 + 属性
MAX_CONNECTIONS       # 全局配置

# 不好的命名
DB                    # 太简短
SECRET                # 不明确
redis_url             # 不统一（应大写）
my_database_password  # 太冗长
```

### 加载环境变量

```typescript
// Node.js
import dotenv from 'dotenv';
dotenv.config();

// 或使用 dotenv-flow 支持多环境
import dotenvFlow from 'dotenv-flow';
dotenvFlow.config();

// Python
from dotenv import load_dotenv
load_dotenv()

import os
db_url = os.getenv('DATABASE_URL')
```

## 配置文件结构

### 多环境配置

```
config/
├── default.json       # 默认配置
├── development.json   # 开发环境
├── test.json          # 测试环境
├── production.json    # 生产环境
└── custom.json        # 用户自定义（可选）
```

### 配置文件格式

```json
{
  "app": {
    "name": "MyApp",
    "version": "1.0.0"
  },
  "server": {
    "port": 3000,
    "host": "localhost",
    "cors": {
      "enabled": true,
      "origins": ["http://localhost:8080"]
    }
  },
  "database": {
    "pool": {
      "min": 2,
      "max": 10
    },
    "timeout": 30000
  },
  "logging": {
    "level": "info",
    "format": "json"
  }
}
```

### 配置加载代码

```typescript
import config from "config";

// 获取配置
const dbConfig = config.get("database");
const port = config.get("server.port");

// 带默认值
const timeout = config.get("database.timeout") ?? 5000;
```

## 敏感信息处理

### 禁止硬编码

```typescript
// ❌ 错误
const apiKey = "sk-prod-xxxxxxxxxxxx";
const dbPassword = "password123";

// ✅ 正确
const apiKey = process.env.API_KEY;
const dbPassword = process.env.DB_PASSWORD;
```

### 密钥存储方案

```
开发环境:
  → .env 文件（不提交）

测试环境:
  → CI/CD 密钥管理（GitHub Secrets）

生产环境:
  → 密钥管理服务（AWS Secrets Manager / Vault）
```

### Secrets Manager 示例

```typescript
// AWS Secrets Manager
import { SecretsManager } from "@aws-sdk/client-secrets-manager";

async function getSecret(secretId: string) {
  const client = new SecretsManager();
  const response = await client.getSecretValue({ SecretId: secretId });
  return JSON.parse(response.SecretString);
}

// HashiCorp Vault
import vault from "node-vault";

async function getVaultSecret(path: string) {
  const client = vault({
    endpoint: process.env.VAULT_ADDR,
    token: process.env.VAULT_TOKEN,
  });
  const result = await client.read(path);
  return result.data;
}
```

## 配置验证

### 启动时验证

```typescript
import { z } from "zod";

const configSchema = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]),
  PORT: z.string().transform(Number).default("3000"),
  DATABASE_URL: z.string().min(1),
  JWT_SECRET: z.string().min(32),
});

function validateConfig() {
  const result = configSchema.safeParse(process.env);
  if (!result.success) {
    console.error("配置验证失败:", result.error.flatten());
    process.exit(1);
  }
  return result.data;
}

const config = validateConfig();
```

### Python 配置验证

```python
from pydantic import BaseSettings, Field, validator

class Settings(BaseSettings):
    NODE_ENV: str = 'development'
    PORT: int = 3000
    DATABASE_URL: str = Field(..., min_length=1)
    JWT_SECRET: str = Field(..., min_length=32)

    @validator('NODE_ENV')
    def validate_env(cls, v):
        if v not in ['development', 'test', 'production']:
            raise ValueError('Invalid NODE_ENV')
        return v

    class Config:
        env_file = '.env'

settings = Settings()
```

## 配置变更管理

### 变更检查清单

```markdown
## 配置变更检查

- [ ] 是否影响现有功能
- [ ] 是否需要迁移脚本
- [ ] 是否需要更新文档
- [ ] 是否需要通知下游服务
- [ ] 生产环境验证方案
- [ ] 回滚方案
```

### 变更记录

```markdown
## 配置变更日志

### 2024-01-15 - 数据库连接池调整

- 变更人：张三
- 变更内容：
  - pool.max: 10 → 20
  - pool.timeout: 30000 → 60000
- 变更原因：高并发场景连接不足
- 影响范围：所有数据库操作
- 验证结果：连接等待时间下降 80%
```

## 最佳实践

1. **敏感信息不入库** — .env 文件加入 .gitignore
2. **提供示例文件** — .env.example 说明必需变量
3. **启动时验证** — 缺少必要配置时报错退出
4. **配置集中管理** — 统一配置加载入口
5. **文档配置项** — README 中列出所有配置项说明
6. **生产隔离** — 生产配置与开发分离管理
