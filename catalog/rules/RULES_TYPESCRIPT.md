---
description: TypeScript 代码开发时启用
---

# TypeScript 规则（专用）

> 配合核心规则使用，仅在 TypeScript 场景加载
> 运行时、版本和包管理器遵循项目清单、锁文件及 CI；本资料不设置全局地板。

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

优先复用项目现有依赖；时间戳、ISO 输出和基本展示可使用 `Date` / `Intl`。明确日期、时间点和时区的不同语义；复杂日历计算或时区需求超出标准能力时，再评估已有 dayjs / date-fns 等库，不为此规则新增或替换依赖。

```typescript
type Clock = () => Date;
const systemClock: Clock = () => new Date();

function createService(clock: Clock = systemClock) {
  return clock().toISOString();
}

const fixed = new Date('2025-01-01T00:00:00Z');
const service = createService(() => fixed);
const display = new Intl.DateTimeFormat('zh-CN', {
  timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit',
}).format(fixed);
```

时间影响业务判断时注入时钟便于测试；一次性脚本和简单显示无需为了该模式增加抽象。维护旧项目时尊重现有时间库，迁移需有实际需求和验证。

## 模块规范

```typescript
// 命名导出优先 / 路径别名避免 ../../
export { User, UserService };
export type { UserDTO, CreateUserDTO };
import { UserService } from '@/services';  // ✅
import { Button } from '../../../components/Button';  // ❌
```
