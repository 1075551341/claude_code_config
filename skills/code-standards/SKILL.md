---
name: code-standards
description: 制定代码规范
triggers: [制定代码规范, 检查命名规范, 统一代码风格, 编写代码规范文档]
---

# 代码规范

## 核心原则

```
📦 组件化 - 单一职责，高内聚低耦合
🔧 可扩展 - 开闭原则，易扩展不易修改
🛡️ 安全性 - 输入验证，防御式编程
📝 可读性 - 命名清晰，注释恰当
🧪 可测试 - 依赖注入，便于 Mock
```

## 命名规范

### 通用规则

| 类型 | 规范 | 示例 |
|------|------|------|
| 变量 | camelCase | `userName`, `isLoading` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| 函数 | camelCase + 动词开头 | `getUserById`, `handleSubmit` |
| 类/组件 | PascalCase | `UserService`, `UserCard` |
| 文件名 | kebab-case | `user-service.ts`, `user-card.vue` |
| 目录名 | kebab-case | `user-profile/`, `api-client/` |
| 接口 | I 前缀或无前缀 | `IUser` 或 `User` |
| 类型 | PascalCase | `UserType`, `ApiResponse` |
| 枚举 | PascalCase + 单数 | `UserStatus` |

### 布尔变量命名

```typescript
// ✅ 推荐 - is/has/can/should 前缀
const isVisible = true
const hasPermission = false
const canEdit = true
const shouldRender = false
const isLoading = true
const hasError = false

// ❌ 避免
const visible = true
const permission = false
const edit = true
```

### 函数命名

```typescript
// ✅ 动词开头，语义清晰
function getUserById(id: string) { }      // 获取
function createUser(data: UserData) { }   // 创建
function updateUser(id: string) { }       // 更新
function deleteUser(id: string) { }       // 删除
function validateEmail(email: string) { } // 验证
function formatPrice(price: number) { }   // 格式化
function parseResponse(data: string) { }  // 解析
function calculateTotal(items: Item[]) { }// 计算
function handleButtonClick() { }          // 处理事件
function onInputChange() { }              // 事件回调

// ❌ 避免
function user() { }
function data() { }
function process() { }
```

### 事件处理命名

```typescript
// ✅ 推荐 - handle + 事件源 + 动作
const handleFormSubmit = () => { }
const handleUserDelete = (id: string) => { }
const handleModalClose = () => { }

// Props 传递时 - on + 事件名
interface Props {
  onSubmit: () => void
  onCancel: () => void
  onUserSelect: (user: User) => void
}
```

## 目录结构规范

### 前端项目（推荐）

```
src/
├── api/                 # API 接口封装
│   ├── index.ts
│   ├── request.ts       # Axios 实例配置
│   └── modules/         # 按模块划分
│       ├── user.ts
│       └── product.ts
├── assets/              # 静态资源
│   ├── images/
│   └── styles/
├── components/          # 通用组件
│   ├── common/          # 基础组件
│   │   ├── Button/
│   │   │   ├── index.ts
│   │   │   ├── Button.vue
│   │   │   └── Button.test.ts
│   │   └── Input/
│   └── business/        # 业务组件
│       └── UserCard/
├── composables/         # 组合式函数 (Vue)
│   └── useAuth.ts
├── hooks/               # 自定义 Hooks (React)
│   └── useAuth.ts
├── layouts/             # 布局组件
├── router/              # 路由配置
├── stores/              # 状态管理
│   └── modules/
├── types/               # 类型定义
│   └── index.ts
├── utils/               # 工具函数
│   ├── format.ts
│   └── validate.ts
├── views/               # 页面组件
│   └── user/
│       ├── index.vue
│       └── components/  # 页面私有组件
└── App.vue
```

### 后端项目（推荐）

```
src/
├── config/              # 配置
│   ├── index.ts
│   └── defaults.ts
├── controllers/         # 控制器
├── middlewares/         # 中间件
│   ├── auth.ts
│   ├── errorHandler.ts
│   └── validator.ts
├── models/              # 数据模型
├── routes/              # 路由
│   ├── index.ts
│   └── modules/
├── services/            # 服务层
├── repositories/        # 数据访问层
├── utils/               # 工具
├── types/               # 类型定义
└── validators/          # 参数验证
```

## 代码风格

### 函数设计原则

```typescript
// ✅ 单一职责 - 一个函数只做一件事
function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

function sendEmail(to: string, subject: string, body: string): Promise<void> {
  // 发送邮件逻辑
}

// ❌ 避免 - 函数职责过多
function validateAndSendEmail(email: string, content: string) {
  if (!validateEmail(email)) return false
  // 发送邮件...
}
```

### 参数设计

```typescript
// ✅ 参数对象化 - 超过 3 个参数使用对象
interface CreateOrderParams {
  userId: string
  productId: string
  quantity: number
  address?: string
}

function createOrder(params: CreateOrderParams): Promise<Order> { }

// ❌ 避免 - 参数过多
function createOrder(userId: string, productId: string, quantity: number, address?: string) { }

// ✅ 使用解构设置默认值
function createUser({ name, age = 18, role = 'user' }: CreateUserParams) { }
```

### 返回值设计

```typescript
// ✅ 返回类型明确
function getUser(id: string): Promise<User | null> { }
function getUsers(): Promise<User[]> { }

// ✅ 操作结果明确
interface Result<T> {
  success: boolean
  data?: T
  error?: string
}

function deleteUser(id: string): Promise<Result<void>> {
  try {
    await db.user.delete(id)
    return { success: true }
  } catch (error) {
    return { success: false, error: error.message }
  }
}
```

## 注释规范

### 文件头注释

```typescript
/**
 * 用户服务
 *
 * 提供用户相关的 CRUD 操作和业务逻辑
 *
 * @module services/user
 * @author Your Name
 * @created 2024-03-19
 */
```

### 函数注释

```typescript
/**
 * 根据条件查询用户列表
 *
 * @param params - 查询参数
 * @param params.page - 页码，从 1 开始
 * @param params.pageSize - 每页数量，默认 20
 * @param params.keyword - 搜索关键词
 * @returns 用户列表和分页信息
 * @throws {ValidationError} 参数验证失败
 * @example
 * ```ts
 * const result = await getUserList({ page: 1, keyword: '张' })
 * console.log(result.data) // User[]
 * ```
 */
async function getUserList(params: GetUsersParams): Promise<PaginatedResult<User>> { }
```

### 复杂逻辑注释

```typescript
// 计算用户等级积分
// 规则：基础积分 × 活跃系数 × VIP 加成
// 活跃系数：连续登录天数 / 30，上限 1.5
// VIP 加成：普通用户 1，VIP 1.2，SVIP 1.5
const score = baseScore * Math.min(loginDays / 30, 1.5) * vipMultiplier
```

### TODO/FIXME 规范

```typescript
// TODO: 添加缓存支持，预计 Q2 完成
// FIXME: 并发情况下可能重复创建，需要加锁
// HACK: 临时方案，等待后端接口更新后移除
// NOTE: 这里不能用 async，会影响事件循环
```

## 代码质量检查清单

### 每次提交前

- [ ] 代码格式化（Prettier/ESLint）
- [ ] 无 TypeScript 类型错误
- [ ] 无 console.log 调试代码
- [ ] 无硬编码的敏感信息
- [ ] 注释准确且必要
- [ ] 测试用例通过

### 代码审查时

- [ ] 命名语义清晰
- [ ] 函数职责单一
- [ ] 无重复代码
- [ ] 错误处理完善
- [ ] 边界条件考虑
- [ ] 性能无明显问题

### 重构时

- [ ] 有测试覆盖
- [ ] 小步提交
- [ ] 行为不变
- [ ] 代码更易理解