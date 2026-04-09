---
name: caching-strategy
description: 当需要设计缓存策略、使用Redis缓存、配置CDN缓存、解决缓存穿透/雪崩/击穿问题时调用此技能。触发词：缓存策略、Redis缓存、CDN缓存、HTTP缓存、缓存穿透、缓存雪崩、缓存击穿、TTL、LRU、Cache-Control。
---

# 缓存策略

## 描述
缓存策略设计与实现，涵盖 Redis、内存缓存、CDN、HTTP 缓存等多层缓存方案。

## 触发条件
当用户提到：缓存、Redis、内存缓存、CDN、HTTP Cache、Cache-Control、ETag、缓存穿透、缓存雪崩、缓存击穿、TTL、LRU、缓存失效策略 时使用此技能。

## 方案选型

| 场景 | 推荐方案 | 适用范围 |
|------|----------|----------|
| 进程内热数据 | node-cache / lru-cache | 单实例、低延迟 |
| 分布式缓存 | Redis / Memcached | 多实例共享、高可用 |
| HTTP 静态资源 | CDN + Cache-Control | 前端资源、图片 |
| API 响应缓存 | ETag + 条件请求 | GET 接口幂等数据 |
| 数据库查询缓存 | Redis + Cache-Aside | 读多写少场景 |

## 核心代码示例

### TypeScript - Redis Cache-Aside 模式
```typescript
import Redis from 'ioredis';

const redis = new Redis(process.env.REDIS_URL);

/**
 * @描述 Cache-Aside 通用缓存封装
 * @参数 key - 缓存键
 * @参数 fetcher - 数据源获取函数
 * @参数 ttl - 过期时间（秒），默认 300
 * @返回 缓存或数据源的数据
 */
async function cacheAside<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttl = 300
): Promise<T> {
  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);

  const data = await fetcher();
  // 随机抖动防止缓存雪崩
  const jitter = Math.floor(Math.random() * 60);
  await redis.setex(key, ttl + jitter, JSON.stringify(data));
  return data;
}

// 批量缓存失效
async function invalidatePattern(pattern: string): Promise<void> {
  const keys = await redis.keys(pattern);
  if (keys.length > 0) await redis.del(...keys);
}

// 使用示例
const user = await cacheAside(
  `user:${id}`,
  () => db.user.findUnique({ where: { id } }),
  600
);
```

### TypeScript - LRU 内存缓存
```typescript
import { LRUCache } from 'lru-cache';

const cache = new LRUCache<string, unknown>({
  max: 500,
  ttl: 1000 * 60 * 5,
  allowStale: false,
});

function memoize<T>(key: string, fn: () => T, ttlMs = 300_000): T {
  if (cache.has(key)) return cache.get(key) as T;
  const result = fn();
  cache.set(key, result, { ttl: ttlMs });
  return result;
}
```

### Python - Redis 缓存装饰器
```python
import json, functools, random
from redis import Redis

redis_client = Redis.from_url("redis://localhost:6379/0")

def cached(prefix: str, ttl: int = 300):
    """
    描述：Redis 缓存装饰器，支持 TTL 抖动
    参数：
        prefix (str): 缓存键前缀
        ttl (int): 过期时间（秒）
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{prefix}:{hash(str(args) + str(kwargs))}"
            data = redis_client.get(key)
            if data:
                return json.loads(data)
            result = await func(*args, **kwargs)
            jitter = random.randint(0, 60)
            redis_client.setex(key, ttl + jitter, json.dumps(result, default=str))
            return result
        return wrapper
    return decorator

@cached("user", ttl=600)
async def get_user(user_id: int) -> dict:
    return await db.fetch_one("SELECT id, name FROM users WHERE id = $1", user_id)
```

## 最佳实践

1. **缓存穿透** → 空值也缓存（短 TTL），或布隆过滤器拦截
2. **缓存雪崩** → TTL 加随机抖动，热 key 预加载
3. **缓存击穿** → 互斥锁（Redis SETNX）防止并发回源
4. **一致性** → 写操作先更新 DB 再删缓存（延迟双删更可靠）
5. **监控** → 关注缓存命中率，低于 80% 需优化策略
6. **序列化** → JSON 通用，MessagePack/Protobuf 性能更好
7. **分层** → L1 内存 + L2 Redis，兼顾速度和容量
