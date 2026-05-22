---
name: performance-optimization
description: 优化系统性能
triggers: [优化系统性能, 解决性能瓶颈, 优化前端渲染, 优化数据库查询]
---

# 性能优化

## 性能优化原则

```
📏 先测量，后优化 - 用数据说话
🎯 抓重点 - 关注核心路径和瓶颈
🔄 持续优化 - 性能是持续的过程
⚖️ 权衡取舍 - 时间换空间，空间换时间
```

## 前端性能优化

### 1. 加载性能

```typescript
// ✅ 代码分割
const HeavyComponent = lazy(() => import('./HeavyComponent'))

// ✅ 路由懒加载
const routes = [
  { path: '/dashboard', component: () => import('@/views/Dashboard.vue') }
]

// ✅ 第三方库按需导入
import { Button, Input } from 'ant-design-vue'
// 而不是 import antd from 'ant-design-vue'

// ✅ 预加载关键资源
<link rel="preload" href="/fonts/main.woff2" as="font" crossorigin>

// ✅ 图片优化
<img src="image.webp" loading="lazy" decoding="async" />
```

### 2. 渲染性能

```typescript
// ✅ 使用虚拟列表处理大数据
import { useVirtualList } from '@vueuse/core'
const { list, containerProps, wrapperProps } = useVirtualList(largeList, { itemHeight: 50 })

// ✅ 计算属性缓存（Vue）
const filteredList = computed(() =>
  list.value.filter(item => item.status === 'active')
)

// ✅ useMemo 缓存计算（React）
const filteredList = useMemo(() =>
  list.filter(item => item.status === 'active'),
  [list]
)

// ✅ 防抖/节流高频操作
import { useDebounceFn, useThrottleFn } from '@vueuse/core'

const handleSearch = useDebounceFn((query) => {
  fetchResults(query)
}, 300)

const handleScroll = useThrottleFn(() => {
  updatePosition()
}, 100)

// ✅ 避免 layout thrashing
// ❌ 错误：循环中读写交替
for (let i = 0; i < elements.length; i++) {
  elements[i].style.width = elements[i].offsetWidth + 10 + 'px'
}

// ✅ 正确：批量读取后批量写入
const widths = elements.map(el => el.offsetWidth)
elements.forEach((el, i) => {
  el.style.width = widths[i] + 10 + 'px'
})
```

### 3. 网络优化

```typescript
// ✅ 请求合并
// ❌ 多次请求
const users = await fetchUsers()
const orders = await fetchOrders()

// ✅ 并行请求
const [users, orders] = await Promise.all([
  fetchUsers(),
  fetchOrders()
])

// ✅ 请求缓存
const cache = new Map()

async function fetchWithCache(key: string, fetcher: () => Promise<any>, ttl = 60000) {
  if (cache.has(key)) {
    const { data, timestamp } = cache.get(key)
    if (Date.now() - timestamp < ttl) {
      return data
    }
  }
  const data = await fetcher()
  cache.set(key, { data, timestamp: Date.now() })
  return data
}

// ✅ 取消重复请求
const pendingRequests = new Map()

async function fetchUnique(url: string) {
  if (pendingRequests.has(url)) {
    return pendingRequests.get(url)
  }
  const promise = fetch(url).finally(() => {
    pendingRequests.delete(url)
  })
  pendingRequests.set(url, promise)
  return promise
}
```

## 后端性能优化

### 1. 数据库优化

```sql
-- ✅ 索引优化
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_order_user_status ON orders(user_id, status);

-- ✅ 分页优化
-- ❌ OFFSET 分页
SELECT * FROM orders ORDER BY id LIMIT 100000, 20;

-- ✅ 游标分页
SELECT * FROM orders WHERE id > 100000 ORDER BY id LIMIT 20;

-- ✅ 只查询需要的字段
SELECT id, name, email FROM users WHERE status = 'active';

-- ✅ 避免 SELECT *
SELECT id, title FROM articles LIMIT 10;
```

### 2. 缓存策略

```typescript
// ✅ Redis 缓存
import Redis from 'ioredis'
const redis = new Redis()

async function getUser(id: string) {
  // 1. 查缓存
  const cached = await redis.get(`user:${id}`)
  if (cached) return JSON.parse(cached)

  // 2. 查数据库
  const user = await db.user.findUnique({ where: { id } })

  // 3. 写缓存
  if (user) {
    await redis.setex(`user:${id}`, 3600, JSON.stringify(user))
  }

  return user
}

// ✅ 缓存穿透防护
async function getUserWithProtection(id: string) {
  const cached = await redis.get(`user:${id}`)
  if (cached === 'NULL') return null // 缓存空值
  if (cached) return JSON.parse(cached)

  const user = await db.user.findUnique({ where: { id } })

  if (user) {
    await redis.setex(`user:${id}`, 3600, JSON.stringify(user))
  } else {
    await redis.setex(`user:${id}`, 60, 'NULL') // 短时间缓存空值
  }

  return user
}

// ✅ 缓存预热
async function warmupCache() {
  const hotUsers = await db.user.findMany({
    where: { lastLogin: { gte: subDays(new Date(), 7) } }
  })
  const pipeline = redis.pipeline()
  hotUsers.forEach(user => {
    pipeline.setex(`user:${user.id}`, 3600, JSON.stringify(user))
  })
  await pipeline.exec()
}
```

### 3. 异步处理

```typescript
// ✅ 消息队列处理耗时任务
import { Queue, Worker } from 'bullmq'

const emailQueue = new Queue('email')

// 生产者
async function sendEmailAsync(to: string, subject: string, body: string) {
  await emailQueue.add('send', { to, subject, body })
}

// 消费者
const worker = new Worker('email', async job => {
  await sendEmail(job.data.to, job.data.subject, job.data.body)
})

// ✅ 批量处理
async function processBatch<T>(
  items: T[],
  processor: (batch: T[]) => Promise<void>,
  batchSize = 100
) {
  for (let i = 0; i < items.length; i += batchSize) {
    const batch = items.slice(i, i + batchSize)
    await processor(batch)
  }
}
```

### 4. 连接池配置

```typescript
// ✅ 数据库连接池
import { Pool } from 'pg'

const pool = new Pool({
  max: 20,              // 最大连接数
  min: 5,               // 最小连接数
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000
})

// ✅ HTTP 连接池（axios）
import axios from 'axios'

const http = axios.create({
  timeout: 5000,
  maxRedirects: 3,
  httpAgent: new http.Agent({ keepAlive: true, maxSockets: 50 }),
  httpsAgent: new https.Agent({ keepAlive: true, maxSockets: 50 })
})
```

## 性能监控

### 关键指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| LCP | < 2.5s | 最大内容绘制时间 |
| FID | < 100ms | 首次输入延迟 |
| CLS | < 0.1 | 累积布局偏移 |
| TTFB | < 200ms | 首字节时间 |
| API 响应 | < 200ms | P95 响应时间 |

### 性能分析工具

```bash
# 前端性能分析
pnpm add -D vite-plugin-bundle-analyzer

# 后端性能分析
node --prof app.js
node --prof-process isolate-*.log

# 数据库慢查询分析
# PostgreSQL
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;

# MySQL
SHOW PROFILE FOR QUERY 1;
```

## 性能优化检查清单

### 前端

- [ ] 代码分割和懒加载
- [ ] 图片压缩和懒加载
- [ ] 使用虚拟列表处理大数据
- [ ] 防抖/节流高频操作
- [ ] 缓存计算结果
- [ ] 预加载关键资源

### 后端

- [ ] 数据库索引优化
- [ ] 查询只选需要的字段
- [ ] 缓存热点数据
- [ ] 异步处理耗时任务
- [ ] 连接池合理配置
- [ ] 响应压缩