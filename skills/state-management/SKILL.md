# 状态管理最佳实践

## 描述
前端状态管理技能，涵盖 React（Zustand/Redux/Jotai）和 Vue（Pinia）的状态设计、
Store 拆分、异步状态处理、持久化和性能优化。

## 触发条件
当需要设计或实现前端状态管理方案时使用，包括全局状态、跨组件通信、缓存策略等场景。

## 技术方案选型

| 场景 | 推荐方案 | 理由 |
|------|----------|------|
| React 轻量状态 | Zustand | API 简洁，无 Provider，按需渲染 |
| React 复杂状态 | Redux Toolkit | 中间件生态完整，DevTools 强大 |
| React 原子状态 | Jotai | 细粒度更新，适合表单/编辑器 |
| React 服务端状态 | TanStack Query | 缓存/重试/乐观更新一站式 |
| Vue 状态管理 | Pinia | Vue 官方推荐，TypeScript 友好 |

## Zustand 模板

```typescript
import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

interface AppState {
  count: number
  loading: boolean
  increment: () => void
  fetchData: () => Promise<void>
}

export const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set, get) => ({
        count: 0,
        loading: false,
        increment: () => set((state) => ({ count: state.count + 1 })),
        fetchData: async () => {
          set({ loading: true })
          try {
            const data = await api.getData()
            set({ count: data.count, loading: false })
          } catch {
            set({ loading: false })
          }
        },
      }),
      { name: 'app-storage' }
    )
  )
)
```

## Pinia 模板

```typescript
import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', () => {
  const count = ref(0)
  const loading = ref(false)

  const doubleCount = computed(() => count.value * 2)

  async function fetchData() {
    loading.value = true
    try {
      const data = await api.getData()
      count.value = data.count
    } finally {
      loading.value = false
    }
  }

  return { count, loading, doubleCount, fetchData }
})
```

## 最佳实践

1. **Store 拆分**：按业务领域拆分（user/product/cart），禁止单一巨大 Store
2. **选择器优化**：使用 selector 精确订阅，避免不必要重渲染
3. **异步状态**：分离 loading/error/data 三态
4. **持久化**：仅持久化必要数据（Token/偏好），避免缓存过期数据
5. **不可变更新**：使用 Immer 或展开运算符，禁止直接修改 state
