---
name: react-component
description: 当需要开发React组件、使用React Hooks、管理React状态、优化React性能时调用此技能。触发词：React组件、React开发、React Hooks、useState、useEffect、React状态管理、JSX、组件开发、React性能优化。
---

# React 组件开发

## 组件标准结构

```typescript
// components/UserCard/UserCard.tsx
import { memo, useState, useCallback } from 'react'
import type { FC, ReactNode } from 'react'
import styles from './UserCard.module.css'

// 类型定义
interface UserCardProps {
  id: string
  name: string
  email: string
  avatar?: string
  onEdit?: (id: string) => void
  children?: ReactNode
}

// 组件
export const UserCard: FC<UserCardProps> = memo(({
  id,
  name,
  email,
  avatar,
  onEdit,
  children
}) => {
  const [loading, setLoading] = useState(false)

  const handleEdit = useCallback(() => {
    onEdit?.(id)
  }, [id, onEdit])

  return (
    <div className={styles.card}>
      {avatar && <img src={avatar} alt={name} className={styles.avatar} />}
      <div className={styles.info}>
        <h3 className={styles.name}>{name}</h3>
        <p className={styles.email}>{email}</p>
      </div>
      {onEdit && (
        <button onClick={handleEdit} disabled={loading}>
          编辑
        </button>
      )}
      {children}
    </div>
  )
})

UserCard.displayName = 'UserCard'
```

## Hooks 最佳实践

### useState - 状态管理
```typescript
// 基础类型
const [count, setCount] = useState(0)

// 对象类型（使用函数式更新避免覆盖）
const [user, setUser] = useState<User | null>(null)
setUser(prev => ({ ...prev, name: 'new' }))

// 惰性初始化（避免每次渲染都执行）
const [data, setData] = useState(() => expensiveInit())
```

### useEffect - 副作用
```typescript
// 1. 组件挂载时执行
useEffect(() => {
  fetchData()
}, [])

// 2. 依赖变化时执行
useEffect(() => {
  fetchUserDetail(userId)
}, [userId])

// 3. 清理副作用
useEffect(() => {
  const timer = setInterval(tick, 1000)
  return () => clearInterval(timer)
}, [])

// 4. 异步操作
useEffect(() => {
  let cancelled = false
  async function load() {
    const data = await fetchData()
    if (!cancelled) setData(data)
  }
  load()
  return () => { cancelled = true }
}, [])
```

### useMemo / useCallback - 性能优化
```typescript
// useMemo: 缓存计算结果
const sortedList = useMemo(() => {
  return [...list].sort((a, b) => a.name.localeCompare(b.name))
}, [list])

// useCallback: 缓存函数引用
const handleClick = useCallback((id: string) => {
  setSelected(id)
}, []) // 依赖为空，函数引用稳定

// 子组件配合 memo 使用
const Child = memo(({ onClick }: { onClick: (id: string) => void }) => {
  // 只有 props 变化才重新渲染
})
```

### useRef - 引用保持
```typescript
// DOM 引用
const inputRef = useRef<HTMLInputElement>(null)
inputRef.current?.focus()

// 保持可变值（不触发重渲染）
const prevValue = useRef(value)
useEffect(() => {
  prevValue.current = value
}, [value])
```

### 自定义 Hook
```typescript
// hooks/useAsync.ts
export function useAsync<T>(fn: () => Promise<T>) {
  const [state, setState] = useState<{
    loading: boolean
    error: Error | null
    data: T | null
  }>({ loading: false, error: null, data: null })

  const execute = useCallback(async () => {
    setState({ loading: true, error: null, data: null })
    try {
      const data = await fn()
      setState({ loading: false, error: null, data })
    } catch (error) {
      setState({ loading: false, error: error as Error, data: null })
    }
  }, [fn])

  return { ...state, execute }
}

// 使用
const { loading, error, data, execute } = useAsync(() => fetchUser(id))
useEffect(() => { execute() }, [execute])
```

## 状态管理

### Zustand（推荐）
```typescript
// stores/userStore.ts
import { create } from 'zustand'

interface UserState {
  user: User | null
  isLoggedIn: boolean
  login: (credentials: Credentials) => Promise<void>
  logout: () => void
}

export const useUserStore = create<UserState>((set) => ({
  user: null,
  isLoggedIn: false,
  login: async (credentials) => {
    const user = await authApi.login(credentials)
    set({ user, isLoggedIn: true })
  },
  logout: () => {
    authApi.logout()
    set({ user: null, isLoggedIn: false })
  }
}))
```

### Context + useReducer
```typescript
// contexts/AppContext.tsx
import { createContext, useContext, useReducer, FC } from 'react'

type State = { count: number }
type Action = { type: 'increment' } | { type: 'decrement' }

const AppContext = createContext<{
  state: State
  dispatch: React.Dispatch<Action>
} | null>(null)

const reducer = (state: State, action: Action): State => {
  switch (action.type) {
    case 'increment': return { count: state.count + 1 }
    case 'decrement': return { count: state.count - 1 }
  }
}

export const AppProvider: FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(reducer, { count: 0 })
  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  )
}

export const useAppContext = () => {
  const context = useContext(AppContext)
  if (!context) throw new Error('useAppContext must be used within AppProvider')
  return context
}
```

## 性能优化

```typescript
// 1. 列表虚拟滚动
import { FixedSizeList } from 'react-window'
<FixedSizeList height={600} itemCount={1000} itemSize={50}>
  {({ index, style }) => <div style={style}>{items[index].name}</div>}
</FixedSizeList>

// 2. 懒加载组件
const HeavyComponent = lazy(() => import('./HeavyComponent'))
<Suspense fallback={<Loading />}>
  <HeavyComponent />
</Suspense>

// 3. 避免不必要的重渲染
const MemoChild = memo(Child)
const handleClick = useCallback(() => {}, [])

// 4. useTransition 处理大列表更新
const [isPending, startTransition] = useTransition()
startTransition(() => {
  setFilteredItems(filterLargeList(items))
})
```

## TypeScript 类型安全

```typescript
// Props 类型
interface Props {
  required: string
  optional?: number
  callback: (id: string) => void
  children: ReactNode
}

// 泛型组件
interface ListProps<T> {
  items: T[]
  renderItem: (item: T) => ReactNode
}
function List<T>({ items, renderItem }: ListProps<T>) {
  return <ul>{items.map(renderItem)}</ul>
}

// 事件类型
const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  setValue(e.target.value)
}
const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault()
}
```

## 检查清单

- [ ] 组件使用 TypeScript 类型定义
- [ ] 使用 `memo` 优化不必要的重渲染
- [ ] 列表使用稳定的 `key`（不用 index）
- [ ] `useEffect` 正确声明依赖数组
- [ ] 异步操作有清理逻辑
- [ ] 错误边界处理