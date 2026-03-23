---
name: vue-development
description: 使用 Vue 3 Composition API、状态管理和性能优化构建 Vue.js 应用。开发 Vue 组件或应用时使用。
---

# Vue.js Development (Vue 3)

## 组件标准结构
```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// Props
const props = defineProps<{ title: string; count?: number }>()
const emit = defineEmits<{ update: [value: number]; close: [] }>()

// 状态
const loading = ref(false)
const items = ref<string[]>([])
const total = computed(() => items.value.length)

// 生命周期
onMounted(() => { /* 初始化 */ })
</script>

<template>
  <div>
    <slot name="header" :total="total" />
    <ul v-if="!loading">
      <li v-for="item in items" :key="item">{{ item }}</li>
    </ul>
  </div>
</template>

<style scoped>/* 局部样式，避免全局污染 */</style>
```

## ref vs reactive 选择
```typescript
const count = ref(0)        // 基础类型用 ref
const user = reactive({})   // 对象用 reactive（注意：解构会丢失响应性）
const { name } = toRefs(user) // 解构需用 toRefs
```

## Composable 模式（逻辑复用）
```typescript
// useAsync.ts
export function useAsync<T>(fn: () => Promise<T>) {
  const data = ref<T | null>(null)
  const loading = ref(false)
  const error = ref<Error | null>(null)

  async function execute() {
    loading.value = true; error.value = null
    try { data.value = await fn() }
    catch (e) { error.value = e as Error }
    finally { loading.value = false }
  }
  return { data, loading, error, execute }
}

// 使用
const { data, loading, execute } = useAsync(() => fetchUsers())
onMounted(execute)
```

## 状态管理（Pinia）
```typescript
export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const isLoggedIn = computed(() => !!user.value)

  async function login(credentials: Credentials) {
    user.value = await authApi.login(credentials)
  }
  return { user, isLoggedIn, login }
})
```

## v-model 双向绑定（自定义组件）
```typescript
// 子组件
const model = defineModel<string>() // Vue 3.4+
// 或 props: ['modelValue'] + emit('update:modelValue', val)
```

## 性能优化
```typescript
// 大列表虚拟滚动
import { useVirtualList } from '@vueuse/core'

// 计算属性缓存（避免模板中直接调用函数）
const sortedList = computed(() => [...list.value].sort())

// 组件懒加载
const HeavyChart = defineAsyncComponent(() => import('./HeavyChart.vue'))

// v-memo 跳过不变子树
<li v-for="item in list" :key="item.id" v-memo="[item.selected]">
```

## 关键规则
- `:key` 在 `v-for` 中必须唯一且稳定（用 ID，不用 index）
- `v-if` vs `v-show`：条件不常变用 `v-if`，频繁切换用 `v-show`
- 避免 `v-if` 和 `v-for` 同级（用 `computed` 先过滤）
- Props 单向数据流，子组件不直接修改 props
