---
name: redis-cache
description: 当需要使用Redis缓存、配置Redis服务、实现缓存策略、操作Redis数据结构时调用此技能。触发词：Redis、缓存、Redis命令、Redis配置、缓存策略、分布式缓存、内存数据库。
---

# Redis 缓存

## 核心能力

**Redis操作、缓存策略、数据结构使用。**

---

## 适用场景

- 数据缓存
- 会话存储
- 消息队列
- 分布式锁

---

## 基本数据类型

| 类型 | 说明 | 使用场景 |
|------|------|----------|
| String | 字符串 | 缓存、计数器 |
| Hash | 哈希表 | 对象存储 |
| List | 列表 | 队列、栈 |
| Set | 集合 | 去重、标签 |
| ZSet | 有序集合 | 排行榜 |

---

## 常用命令

### String 操作

```bash
# 设置
SET key value
SET key value EX 3600    # 设置过期时间(秒)
SET key value PX 3600000 # 设置过期时间(毫秒)
SETNX key value          # 不存在才设置

# 获取
GET key

# 计数
INCR counter
INCRBY counter 10
DECR counter

# 批量
MSET key1 val1 key2 val2
MGET key1 key2
```

### Hash 操作

```bash
# 设置
HSET user:1 name "John"
HSET user:1 age 30
HMSET user:1 name "John" age 30

# 获取
HGET user:1 name
HGETALL user:1

# 删除
HDEL user:1 age
```

### List 操作

```bash
# 推入
LPUSH queue item1 item2
RPUSH queue item3

# 弹出
LPOP queue
RPOP queue

# 范围
LRANGE queue 0 -1

# 阻塞弹出
BLPOP queue 5  # 等待5秒
```

### Set 操作

```bash
# 添加
SADD tags tag1 tag2

# 获取
SMEMBERS tags
SISMEMBER tags tag1

# 运算
SINTER set1 set2    # 交集
SUNION set1 set2    # 并集
SDIFF set1 set2     # 差集
```

### ZSet 操作

```bash
# 添加
ZADD leaderboard 100 user1
ZADD leaderboard 95 user2

# 获取
ZRANGE leaderboard 0 -1 WITHSCORES
ZREVRANGE leaderboard 0 9  # 前10名

# 分数操作
ZINCRBY leaderboard 10 user1
```

---

## 缓存策略

### 缓存穿透

```python
# 布隆过滤器 或 空值缓存
def get_data(key):
    data = redis.get(key)
    if data is None:
        data = db.query(key)
        if data is None:
            redis.setex(key, 60, "NULL")  # 空值缓存短时间
        else:
            redis.setex(key, 3600, data)
    elif data == "NULL":
        return None
    return data
```

### 缓存击穿

```python
# 互斥锁
def get_data_with_lock(key):
    data = redis.get(key)
    if data is None:
        lock_key = f"lock:{key}"
        if redis.setnx(lock_key, 1):
            redis.expire(lock_key, 10)
            try:
                data = db.query(key)
                redis.setex(key, 3600, data)
            finally:
                redis.delete(lock_key)
    return data
```

### 缓存雪崩

```python
# 随机过期时间
import random

def set_cache(key, value, base_ttl=3600):
    ttl = base_ttl + random.randint(0, 300)  # 添加随机值
    redis.setex(key, ttl, value)
```

---

## Node.js 使用

```typescript
import Redis from 'ioredis';

const redis = new Redis({
  host: 'localhost',
  port: 6379,
  password: 'password',
  db: 0
});

// 基础操作
await redis.set('key', 'value', 'EX', 3600);
const value = await redis.get('key');

// Hash
await redis.hset('user:1', 'name', 'John');
const user = await redis.hgetall('user:1');

// 发布订阅
redis.subscribe('channel', (err, count) => {});
redis.on('message', (channel, message) => {
  console.log(message);
});

// 发布
const publisher = new Redis();
publisher.publish('channel', 'message');
```

---

## Python 使用

```python
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

# 基础操作
r.set('key', 'value', ex=3600)
value = r.get('key')

# Hash
r.hset('user:1', mapping={'name': 'John', 'age': 30})
user = r.hgetall('user:1')

# Pipeline (批量操作)
pipe = r.pipeline()
pipe.set('key1', 'value1')
pipe.set('key2', 'value2')
pipe.execute()
```

---

## 分布式锁

```python
import uuid

def acquire_lock(lock_name, timeout=10):
    identifier = str(uuid.uuid4())
    lock_key = f"lock:{lock_name}"
    
    if r.setnx(lock_key, identifier):
        r.expire(lock_key, timeout)
        return identifier
    return None

def release_lock(lock_name, identifier):
    lock_key = f"lock:{lock_name}"
    
    pipe = r.pipeline()
    while True:
        try:
            pipe.watch(lock_key)
            if pipe.get(lock_key) == identifier.encode():
                pipe.multi()
                pipe.delete(lock_key)
                pipe.execute()
                return True
            pipe.unwatch()
            break
        except redis.WatchError:
            pass
    return False
```

---

## 注意事项

```
必须:
- 设置合理过期时间
- 处理缓存穿透/击穿/雪崩
- 使用连接池
- 监控内存使用

避免:
- 大Key存储
- 无限制过期时间
- 不处理序列化
- 忽略持久化配置
```

---

## 相关技能

- `caching-strategy` - 缓存策略
- `nodejs-backend` - Node.js 后端
- `python-backend` - Python 后端