---
name: api-mock
description: 当需要生成Mock数据、模拟API响应、创建测试数据、使用Faker.js/Mock.js时调用此技能。触发词：Mock数据、模拟数据、Mock API、Faker.js、Mock.js、MSW、测试数据生成、假数据、数据模拟。
---

# API Mock 开发

## Mock.js 快速入门

### 基础语法

```javascript
import Mock from 'mockjs'

const data = Mock.mock({
  // 字符串
  'string|3': 'ab',        // 重复3次: 'ababab'
  'string|1-3': 'ab',      // 随机重复1-3次

  // 数字
  'number|1-100': 1,       // 1-100随机整数
  'float|1-100.1-2': 1,    // 1-100随机浮点数，1-2位小数
  'integer': '@integer',    // 大整数

  // 布尔
  'boolean': '@boolean',    // 随机布尔值
  'bool|1-3': true,        // 1/4概率为true

  // 数组
  'array|3': ['a', 'b'],    // 重复3次
  'array|1-3': ['a', 'b'],  // 随机重复1-3次
  'list|10': [{ id: '@id', name: '@cname' }],  // 生成10个对象

  // 对象
  'object|2': { a: 1, b: 2, c: 3 },  // 随机选2个属性
})

console.log(JSON.stringify(data, null, 2))
```

### 占位符

```javascript
Mock.mock({
  // 基础
  id: '@id',                    // 随机ID
  guid: '@guid',                // GUID
  uuid: '@uuid',                // UUID

  // 文本
  title: '@title',              // 标题
  sentence: '@sentence',        // 句子
  paragraph: '@paragraph',      // 段落
  word: '@word',                // 单词
  cparagraph: '@cparagraph',    // 中文段落
  csentence: '@csentence',      // 中文句子
  cname: '@cname',              // 中文名

  // 日期时间
  date: '@date',                // 日期
  time: '@time',                // 时间
  datetime: '@datetime',        // 日期时间
  now: '@now',                  // 当前时间

  // 图片
  image: '@image("200x100", "#4A7BF7", "Hello")',  // 图片URL
  img: '@img',                  // 随机图片

  // 网络
  url: '@url',                  // URL
  domain: '@domain',            // 域名
  email: '@email',              // 邮箱
  ip: '@ip',                    // IP地址

  // 地理
  region: '@region',            // 区域
  province: '@province',        // 省
  city: '@city',                // 市
  county: '@county',            // 县
  address: '@county(true)',     // 完整地址

  // 其他
  color: '@color',              // 颜色
  rgb: '@rgb',                  // RGB颜色
  pick: '@pick(["a", "b", "c"])',  // 从数组中随机选
})
```

## Faker.js (推荐)

### 安装

```bash
pnpm add @faker-js/faker -D
```

### 基础使用

```typescript
import { faker } from '@faker-js/faker/locale/zh_CN'

// 人物
faker.person.firstName()        // 名
faker.person.lastName()         // 姓
faker.person.fullName()         // 全名
faker.person.sex()              // 性别

// 联系方式
faker.phone.number()            // 电话
faker.internet.email()          // 邮箱
faker.internet.username()       // 用户名
faker.internet.password()       // 密码
faker.internet.url()            // URL
faker.internet.avatar()         // 头像URL

// 地址
faker.location.city()           // 城市
faker.location.streetAddress()  // 街道地址
faker.location.zipCode()        // 邮编
faker.location.country()        // 国家

// 公司
faker.company.name()            // 公司名
faker.company.catchPhrase()     // 口号

// 金融
faker.finance.accountNumber()   // 账号
faker.finance.creditCardNumber() // 信用卡号
faker.finance.amount()          // 金额

// 日期
faker.date.past()               // 过去日期
faker.date.future()             // 未来日期
faker.date.recent()             // 最近日期
faker.date.birthdate()          // 生日

// 图片
faker.image.url()               // 图片URL
faker.image.avatar()            // 头像
faker.image.urlLoremFlickr({ category: 'nature' })  // 分类图片

// 随机
faker.datatype.uuid()           // UUID
faker.datatype.boolean()        // 布尔
faker.datatype.number()         // 数字
faker.helpers.arrayElement(['a', 'b', 'c'])  // 随机选择
```

### 自定义种子（可重复）

```typescript
// 设置种子，每次生成相同数据
faker.seed(123)
console.log(faker.person.fullName())  // 总是相同的结果
```

## MSW (Mock Service Worker)

### 安装

```bash
pnpm add msw -D
pnpm exec msw init public/ --save
```

### 定义 Handlers

```typescript
// src/mocks/handlers.ts
import { http, HttpResponse, delay } from 'msw'

export const handlers = [
  // GET 请求
  http.get('/api/users', async () => {
    await delay(200)  // 模拟延迟

    return HttpResponse.json({
      code: 0,
      data: [
        { id: 1, name: '张三', email: 'zhang@example.com' },
        { id: 2, name: '李四', email: 'li@example.com' },
      ],
      meta: { total: 2 }
    })
  }),

  // 动态参数
  http.get('/api/users/:id', ({ params }) => {
    const { id } = params

    return HttpResponse.json({
      code: 0,
      data: { id, name: '张三', email: 'zhang@example.com' }
    })
  }),

  // POST 请求
  http.post('/api/users', async ({ request }) => {
    const body = await request.json()

    return HttpResponse.json({
      code: 0,
      data: { id: Date.now(), ...body }
    }, { status: 201 })
  }),

  // 错误响应
  http.get('/api/error', () => {
    return HttpResponse.json({
      code: 50000,
      msg: '服务器错误'
    }, { status: 500 })
  }),
]
```

### 浏览器启动

```typescript
// src/mocks/browser.ts
import { setupWorker } from 'msw/browser'
import { handlers } from './handlers'

export const worker = setupWorker(...handlers)

// main.ts
if (import.meta.env.DEV) {
  const { worker } = await import('./mocks/browser')
  await worker.start()
}
```

### Node 测试启动

```typescript
// src/mocks/node.ts
import { setupServer } from 'msw/node'
import { handlers } from './handlers'

export const server = setupServer(...handlers)

// vitest.setup.ts
import { server } from './mocks/node'

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

## 实用场景

### 生成测试数据

```typescript
// scripts/generate-mock-data.ts
import { faker } from '@faker-js/faker/locale/zh_CN'

function generateUsers(count: number) {
  return Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    name: faker.person.fullName(),
    email: faker.internet.email(),
    phone: faker.phone.number(),
    avatar: faker.image.avatar(),
    address: faker.location.streetAddress(),
    createdAt: faker.date.past().toISOString(),
  }))
}

console.log(JSON.stringify(generateUsers(10), null, 2))
```

### API 响应类型安全

```typescript
// types/api.ts
interface User {
  id: number
  name: string
  email: string
}

interface ApiResponse<T> {
  code: number
  data: T
  msg: string
}

// mock/handlers.ts
import { faker } from '@faker-js/faker/locale/zh_CN'

function createMockUser(): User {
  return {
    id: faker.number.int(),
    name: faker.person.fullName(),
    email: faker.internet.email(),
  }
}

export const handlers = [
  http.get('/api/user', () => {
    const response: ApiResponse<User> = {
      code: 0,
      data: createMockUser(),
      msg: 'ok'
    }
    return HttpResponse.json(response)
  }),
]
```