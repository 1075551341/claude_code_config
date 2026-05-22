---
description: TypeScript 代码开发时启用
alwaysApply: false
---

# TypeScript 规则（专用）

> 配合核心规则使用，仅在 TypeScript 场景加载

## 配置规范

### tsconfig.json 关键项

```json
{
  "compilerOptions": {
    "target": "ES2022", "module": "ESNext", "moduleResolution": "bundler",
    "strict": true, "noEmit": true, "esModuleInterop": true, "skipLibCheck": true,
    "noUncheckedIndexedAccess": true, "noImplicitReturns": true, "noFallthroughCasesInSwitch": true,
    "baseUrl": ".", "paths": { "@/*": ["./src/*"] }
  },
  "include": ["src/**/*"], "exclude": ["node_modules", "dist"]
}
```

## 类型系统

### 禁止 any

```typescript
// ❌ function process(data: any)
// ✅ 使用 unknown + 类型守卫 或 泛型
function process<T extends { value: string }>(data: T): string { return data.value; }
```

### 类型定义优先级

```typescript
// 对象类型：优先 type；可扩展/实现：使用 interface
type User = { id: number; name: string; email: string };
interface Repository<T> { findById(id: number): Promise<T | null>; save(entity: T): Promise<void>; }

// 联合类型 + 工具类型
type Status = 'pending' | 'approved' | 'rejected';
type Result<T> = Success<T> | Failure;
type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
```

### 类型守卫

```typescript
function isString(value: unknown): value is string { return typeof value === 'string'; }
function isUser(value: unknown): value is User { return typeof value === 'object' && value !== null && 'id' in value; }
```

## 函数规范

```typescript
// 显式返回类型 + 函数重载 + 参数默认值
function format(value: string): string;
function format(value: number): string;
function format(value: string | number): string { return String(value); }

// 箭头函数：单行简洁，多行常规
const double = (n: number): number => n * 2;
```

## 异步编程

```typescript
// async/await + 错误处理
async function fetchData(url: string): Promise<Response> {
  try { const response = await fetch(url); if (!response.ok) throw new Error(`HTTP ${response.status}`); return response; }
  catch (error) { throw new ApiError((error as Error).message, { cause: error }); }
}

// Promise.all 并行 / Promise.allSettled 容错
const [users, posts] = await Promise.all([fetchUsers(), fetchPosts()]);

// Result 模式（无异常）
type Result<T, E = Error> = { success: true; data: T } | { success: false; error: E };
```

## React/前端规范

```typescript
// 函数组件 + 泛型组件
interface ButtonProps { variant?: 'primary' | 'secondary'; onClick?: () => void; children: React.ReactNode; }
export function Button({ variant = 'primary', onClick, children }: ButtonProps) { return <button className={`btn btn-${variant}`} onClick={onClick}>{children}</button>; }

// 自定义 Hook 以 use 开头，返回类型明确
function useDebounce<T>(value: T, delay: number): T { /* ... */ }
```

## 时间处理

### 禁止 `new Date()` / `Date.now()`，使用 dayjs / date-fns

`new Date()` 不可变性问题、API 反人类、时区处理困难。必须使用时间库。

```typescript
// ❌ 禁止
const now = new Date();
const ts = new Date().toISOString();
const formatted = new Date().toLocaleDateString();
const stamp = Date.now();

// ✅ dayjs（首选，2KB、不可变、链式）
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';
dayjs.extend(utc); dayjs.extend(timezone);

const now = dayjs();
const ts = dayjs().toISOString();
const formatted = dayjs().format('YYYY-MM-DD HH:mm:ss');
const inShanghai = dayjs().tz('Asia/Shanghai');

// ✅ date-fns（函数式风格项目）
import { format, addDays, isAfter } from 'date-fns';
const formatted = format(new Date(), 'yyyy-MM-dd');
const tomorrow = addDays(new Date(), 1);

// ❌ 避免 moment（已弃用、体积 67KB、可变对象）
// import moment from 'moment';  // 除非维护旧项目
```

### 时间库选型

| 场景 | 推荐 | 理由 |
|------|------|------|
| 通用项目 | dayjs | 轻量 2KB、moment 兼容 API、不可变 |
| 函数式项目 | date-fns | tree-shakeable、纯函数 |
| 维护旧项目 | moment | 仅限已有依赖，不新引入 |

### 依赖注入（业务逻辑）

```typescript
import dayjs from 'dayjs';
type Clock = () => dayjs.Dayjs;
const defaultClock: Clock = () => dayjs();

function createService(clock: Clock = defaultClock) {
  const now = clock();
}

// ✅ 测试中注入固定时间
const service = createService(() => dayjs('2025-01-01T00:00:00Z'));
```

例外：纯 UI 展示当前时间（如时钟组件）

## 模块规范

```typescript
// 命名导出优先 / 路径别名避免 ../../
export { User, UserService };
export type { UserDTO, CreateUserDTO };
import { UserService } from '@/services';  // ✅
import { Button } from '../../../components/Button';  // ❌
```
