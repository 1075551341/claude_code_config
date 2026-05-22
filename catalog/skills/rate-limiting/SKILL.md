---
name: rate-limiting
description: 实现API限流
triggers: [实现API限流, 防止接口被恶意刷取, 配置请求频率控制]
---

# 限流防护

## 描述
API 限流与防刷方案，涵盖令牌桶、滑动窗口、分布式限流等策略

## 触发条件
当用户提到：限流、Rate Limit、令牌桶、滑动窗口、漏桶、防刷、API 频率限制、429、throttle、并发控制、分布式限流 时使用此技能

## 方案选型

| 场景 | 推荐方案 | 适用范围 |
|------|----------|----------|
| Express 单实例 | express-rate-limit | 快速接入、小型项目 |
| 分布式限流 | Redis + 滑动窗口/令牌桶 | 多实例部署 |
| Nginx 层限流 | limit_req_zone | 网关层防护 |
| FastAPI | slowapi（基于 limits） | Python API |
| 精细控制 | 自定义 Lua 脚本 + Redis | 多维度/动态限流 |
| 网关层 | Kong / APISIX 限流插件 | 微服务架构 |

## 核心代码示例

### TypeScript - Redis 滑动窗口限流
```typescript
import Redis from 'ioredis';

const redis = new Redis(process.env.REDIS_URL);

/**
 * @描述 滑动窗口限流器
 * @参数 key - 限流标识（如 IP、用户 ID）
 * @参数 windowMs - 窗口大小（毫秒）
 * @参数 maxRequests - 窗口内最大请求数
 * @返回 { allowed, remaining, retryAfter }
 */
async function slidingWindowRateLimit(
  key: string,
  windowMs: number,
  maxRequests: number
): Promise<{ allowed: boolean; remaining: number; retryAfter: number }> {
  const now = Date.now();
  const windowStart = now - windowMs;

  const multi = redis.multi();
  multi.zremrangebyscore(key, 0, windowStart);
  multi.zcard(key);
  multi.zadd(key, now.toString(), `${now}:${Math.random()}`);
  multi.pexpire(key, windowMs);

  const results = await multi.exec();
  const count = (results?.[1]?.[1] as number) || 0;

  if (count >= maxRequests) {
    const oldest = await redis.zrange(key, 0, 0, 'WITHSCORES');
    const retryAfter = oldest.length > 1
      ? Math.ceil((parseInt(oldest[1]) + windowMs - now) / 1000)
      : Math.ceil(windowMs / 1000);
    return { allowed: false, remaining: 0, retryAfter };
  }

  return { allowed: true, remaining: maxRequests - count - 1, retryAfter: 0 };
}

// Express 中间件
function rateLimit(windowMs: number, max: number) {
  return async (req: Request, res: Response, next: NextFunction) => {
    const key = `rl:${req.ip}:${req.route?.path || req.path}`;
    const result = await slidingWindowRateLimit(key, windowMs, max);

    res.set('X-RateLimit-Limit', max.toString());
    res.set('X-RateLimit-Remaining', result.remaining.toString());

    if (!result.allowed) {
      res.set('Retry-After', result.retryAfter.toString());
      return res.status(429).json({ code: 429, msg: '请求过于频繁，请稍后再试' });
    }
    next();
  };
}

// 不同接口不同限流策略
app.post('/auth/login', rateLimit(60_000, 5));        // 登录：1 分钟 5 次
app.post('/auth/sms', rateLimit(60_000, 1));           // 短信：1 分钟 1 次
app.use('/api', rateLimit(60_000, 100));               // 通用：1 分钟 100 次
```

### TypeScript - Redis 令牌桶（Lua 脚本）
```typescript
const tokenBucketScript = `
  local key = KEYS[1]
  local capacity = tonumber(ARGV[1])
  local refillRate = tonumber(ARGV[2])
  local now = tonumber(ARGV[3])

  local data = redis.call('HMGET', key, 'tokens', 'lastRefill')
  local tokens = tonumber(data[1]) or capacity
  local lastRefill = tonumber(data[2]) or now

  local elapsed = (now - lastRefill) / 1000
  tokens = math.min(capacity, tokens + elapsed * refillRate)

  if tokens < 1 then
    return {0, 0}
  end

  tokens = tokens - 1
  redis.call('HMSET', key, 'tokens', tokens, 'lastRefill', now)
  redis.call('PEXPIRE', key, math.ceil(capacity / refillRate) * 1000 + 1000)
  return {1, math.floor(tokens)}
`;

async function tokenBucket(key: string, capacity: number, refillPerSec: number) {
  const [allowed, remaining] = await redis.eval(
    tokenBucketScript, 1, key, capacity, refillPerSec, Date.now()
  ) as [number, number];
  return { allowed: allowed === 1, remaining };
}
```

### Python - FastAPI 限流
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379/2",
    default_limits=["100/minute"],
)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request):
    """描述：登录接口，限制每分钟 5 次"""
    return {"code": 0, "msg": "ok"}

@app.post("/auth/sms")
@limiter.limit("1/minute;5/hour")
async def send_sms(request: Request):
    """描述：短信发送接口，1 分钟 1 次，1 小时 5 次"""
    return {"code": 0, "msg": "ok"}
```

### Nginx 层限流
```nginx
http {
    # 基于 IP 的请求频率限制
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

    server {
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            limit_req_status 429;
            proxy_pass http://backend;
        }
        location /auth/login {
            limit_req zone=login burst=3;
            limit_req_status 429;
            proxy_pass http://backend;
        }
    }
}
```

## 最佳实践

1. **多层防护** → Nginx 粗粒度 + 应用层细粒度 + 业务层自定义
2. **标识维度** → IP / 用户 ID / API Key，按业务选择组合
3. **响应头** → 返回 `X-RateLimit-Limit` / `Remaining` / `Retry-After`
4. **白名单** → 内部服务/管理员/压测 IP 加入白名单
5. **动态调整** → 根据负载自动调整限流阈值（降级策略）
6. **分级限流** → 核心接口（登录/支付）严格限流，普通查询宽松
7. **攻击应对** → 异常流量触发熔断，自动封禁恶意 IP（fail2ban）
