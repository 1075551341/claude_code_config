---
description: TypeScript 代码开发时启用
alwaysApply: false
---

# TypeScript 规则（专用）

> 配合核心规则使用，仅在 TypeScript 场景加载

## 配置规范

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "exactOptionalPropertyTypes": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

## 类型系统

### 禁止 any

```typescript
// ❌ 禁止
function process(data: any) {
  return data.value;
}

// ✅ 使用 unknown + 类型守卫
function process(data: unknown) {
  if (typeof data === 'object' && data !== null && 'value' in data) {
    return (data as { value: string }).value;
  }
  throw new Error('Invalid data');
}

// ✅ 使用泛型
function process<T extends { value: string }>(data: T): string {
  return data.value;
}
```

### 类型定义

```typescript
// 对象类型：优先 type
type User = {
  id: number;
  name: string;
  email: string;
};

// 可扩展/实现：使用 interface
interface Repository<T> {
  findById(id: number): Promise<T | null>;
  save(entity: T): Promise<void>;
}

// 联合类型
type Status = 'pending' | 'approved' | 'rejected';
type Result<T> = Success<T> | Failure;

// 工具类型
type PartialUser = Partial<User>;
type RequiredUser = Required<User>;
type UserKeys = keyof User;
type UserValues = User[keyof User];
```

### 泛型约束

```typescript
// 基础泛型
function identity<T>(value: T): T {
  return value;
}

// 约束泛型
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

// 条件类型
type NonNullable<T> = T extends null | undefined ? never : T;

// 映射类型
type Readonly<T> = {
  readonly [K in keyof T]: T[K];
};

// 模板字面量类型
type EventName = `on${Capitalize<string>}`;
```

## 函数规范

### 函数签名

```typescript
// 显式返回类型
function fetchUser(id: number): Promise<User> {
  return api.get<User>(`/users/${id}`);
}

// 函数重载
function format(value: string): string;
function format(value: number): string;
function format(value: string | number): string {
  return String(value);
}

// 参数默认值
function createUrl(
  path: string,
  baseUrl: string = 'https://api.example.com'
): string {
  return `${baseUrl}${path}`;
}
```

### 箭头函数

```typescript
// 单行简洁
const double = (n: number): number => n * 2;

// 多行使用常规形式
const process = (data: string[]): number => {
  const filtered = data.filter(Boolean);
  return filtered.length;
};

// 回调函数类型
type Callback<T> = (value: T, index: number) => void;
```

## 异步编程

### Promise

```typescript
// async/await
async function fetchData(url: string): Promise<Response> {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return response;
  } catch (error) {
    if (error instanceof Error) {
      throw new ApiError(error.message, { cause: error });
    }
    throw error;
  }
}

// Promise.all 并行
const [users, posts] = await Promise.all([
  fetchUsers(),
  fetchPosts()
]);

// Promise.allSettled 容错
const results = await Promise.allSettled([
  fetchUser(1),
  fetchUser(2),
]);
const succeeded = results
  .filter((r): r is PromiseFulfilledResult<User> => r.status === 'fulfilled')
  .map(r => r.value);
```

### 错误处理

```typescript
// Result 模式
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };

async function safeFetch<T>(url: string): Promise<Result<T>> {
  try {
    const response = await fetch(url);
    const data = await response.json() as T;
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error as Error };
  }
}

// 使用
const result = await safeFetch<User>('/api/user/1');
if (result.success) {
  console.log(result.data);
} else {
  console.error(result.error);
}
```

## React/前端规范

### 组件类型

```typescript
// 函数组件
interface ButtonProps {
  variant?: 'primary' | 'secondary';
  onClick?: () => void;
  children: React.ReactNode;
}

export function Button({ variant = 'primary', onClick, children }: ButtonProps) {
  return (
    <button className={`btn btn-${variant}`} onClick={onClick}>
      {children}
    </button>
  );
}

// 泛型组件
interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
}

export function List<T>({ items, renderItem }: ListProps<T>) {
  return <ul>{items.map(renderItem)}</ul>;
}
```

### Hooks 规范

```typescript
// 自定义 Hook 以 use 开头
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

// 返回类型明确
interface UseFetchResult<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

function useFetch<T>(url: string): UseFetchResult<T> {
  // ...
}
```

## 模块规范

### 导入导出

```typescript
// 命名导出
export { User, UserService };
export type { UserDTO, CreateUserDTO };

// 默认导出（仅一个时）
export default class UserService { }

// 重新导出
export { UserService } from './user.service';
export type { User } from './user.types';

// 命名空间导入
import * as Utils from './utils';
```

### 模块解析

```typescript
// 使用路径别名
import { UserService } from '@/services';
import type { User } from '@/types';

// 避免 ../../ 相对路径
import { Button } from '../../../components/Button'; // ❌
import { Button } from '@/components/Button'; // ✅
```

## 工具类型库

```typescript
// 常用工具类型
type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
type Required<T, K extends keyof T> = Omit<T, K> & Required<Pick<T, K>>;
type Mutable<T> = { -readonly [K in keyof T]: T[K] };
type DeepPartial<T> = { [K in keyof T]?: DeepPartial<T[K]> };

// 类型守卫
function isString(value: unknown): value is string {
  return typeof value === 'string';
}

function isUser(value: unknown): value is User {
  return typeof value === 'object' && value !== null && 'id' in value;
}
```