---
name: typescript
description: 编写TypeScript类型、解决类型错误、使用泛型/高级类型、实现类型安全
triggers: [TypeScript, TS类型, 泛型, 类型定义, 类型安全, TypeScript配置, 类型推断, 类型体操, interface, type]
---

# TypeScript 高级模式

> 聚焦高级模式和易错点，基础类型略过

## 高级类型

### 辨别联合（Discriminated Union）
```typescript
type Result<T> =
  | { status: 'ok'; data: T }
  | { status: 'error'; error: string }

function handle<T>(r: Result<T>) {
  if (r.status === 'ok') console.log(r.data)  // 自动收窄
  else console.error(r.error)
}
```

### 条件类型 + infer
```typescript
type Awaited<T> = T extends Promise<infer U> ? U : T
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : never
type Flatten<T> = T extends Array<infer Item> ? Item : T
```

### 模板字面量类型
```typescript
type EventName<T extends string> = `on${Capitalize<T>}`
type HttpVerb = 'GET' | 'POST' | 'PUT' | 'DELETE'
type ApiPath = `/${string}`
```

## 泛型

### 约束与默认值
```typescript
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key]
}

interface ApiResponse<T = unknown> { data: T; code: number }

function merge<T extends object, U extends object>(a: T, b: U): T & U {
  return { ...a, ...b }
}
```

## 工具类型速查
```
Partial<T>              所有属性可选
Required<T>             所有属性必选
Readonly<T>             所有属性只读
Pick<T, K>              选取属性子集
Omit<T, K>              排除属性子集
Record<K, V>            键值对类型
Exclude<T, U>           联合类型排除
Extract<T, U>           联合类型提取
NonNullable<T>          排除 null/undefined
Parameters<F>           函数参数类型元组
ReturnType<F>           函数返回类型
```

## 类型守卫
```typescript
function isUser(obj: unknown): obj is User {
  return typeof obj === 'object' && obj !== null && 'id' in obj
}

function assertDefined<T>(val: T | null | undefined): asserts val is T {
  if (val == null) throw new Error('值不应为空')
}
```

## 常见陷阱
```typescript
// ❌ any 扩散丢失类型安全 → ✅ unknown + 类型守卫
// ❌ as 强转掩盖问题 → ✅ 用 zod/valibot 运行时验证
// ❌ 数字枚举可反向映射 → ✅ 字符串联合 type Dir = 'up'|'down'
// ❌ 函数重载：具体类型必须放在宽泛类型前面
```

## tsconfig 关键配置
```json
{
  "strict": true,
  "noUncheckedIndexedAccess": true,
  "exactOptionalPropertyTypes": true,
  "noImplicitReturns": true,
  "noFallthroughCasesInSwitch": true
}
```
