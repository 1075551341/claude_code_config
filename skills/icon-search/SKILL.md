---
name: icon-search
description: 当需要查找图标、搜索图标库、使用Iconify/FontAwesome图标时调用此技能。触发词：图标搜索、Iconify、FontAwesome、图标查找、IconPark、前端图标、SVG图标、图标导入、icon组件。
---

# 图标搜索和导入

搜索和导入前端图标。

## 使用方式

```
/icon-search <keyword> [options]
```

**参数说明：**
- `<keyword>`: 搜索关键词
- `--lib`: 图标库 - `iconify` | `iconpark` | `fontawesome` | `heroicons`

## Iconify 集成

### 安装

```bash
# Vue 3
pnpm add @iconify/vue

# React
pnpm add @iconify/react
```

### 使用方式

```vue
<script setup lang="ts">
import { Icon } from '@iconify/vue'
</script>

<template>
  <!-- 基础使用 -->
  <Icon icon="mdi:home" />

  <!-- 设置大小 -->
  <Icon icon="mdi:account" width="24" />
  <Icon icon="mdi:account" width="2rem" />

  <!-- 设置颜色 -->
  <Icon icon="mdi:heart" color="red" />
  <Icon icon="mdi:star" style="color: #f59e0b" />

  <!-- 内联模式 -->
  <Icon icon="mdi:check" inline />
</template>
```

### 常用图标集

| 图标集 | 前缀 | 说明 |
|--------|------|------|
| Material Design | `mdi:` | Google Material 图标 |
| Font Awesome | `fa:` | FontAwesome 图标 |
| Heroicons | `heroicons:` | Tailwind 团队图标 |
| Carbon | `carbon:` | IBM Carbon 图标 |
| Tabler | `tabler:` | Tabler Icons |
| Lucide | `lucide:` | Lucide Icons |
| Remix Icon | `ri:` | Remix 图标 |
| Ant Design | `ant-design:` | Ant Design 图标 |

### 按需加载图标集

```typescript
// 安装特定图标集
pnpm add @iconify/json  // 全部图标
pnpm add @iconify-json/mdi  // 仅 Material Design
pnpm add @iconify-json/fa  // 仅 FontAwesome
```

### 离线使用

```typescript
// 预加载图标数据
import { addCollection } from '@iconify/vue'
import mdiIcons from '@iconify-json/mdi/icons.json'

addCollection(mdiIcons)
```

## IconPark 图标

### 安装

```bash
# Vue 3
pnpm add @icon-park/vue-next

# React
pnpm add @icon-park/react
```

### 使用方式

```vue
<script setup lang="ts">
import { Home, Setting, User } from '@icon-park/vue-next'
</script>

<template>
  <Home />
  <Setting theme="outline" size="24" fill="#333" />
  <User theme="filled" size="32" />
</template>
```

### 主题类型

- `outline` - 线性
- `filled` - 填充
- `two-tone` - 双色
- `multi-color` - 多色

## 自定义图标组件

### Vue 3 封装

```vue
<!-- components/SvgIcon/index.vue -->
<script setup lang="ts">
import { computed } from 'vue'
import { Icon } from '@iconify/vue'

interface Props {
  name: string
  size?: number | string
  color?: string
  className?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 16,
})

// 判断是否为 Iconify 图标
const isIconify = computed(() => props.name.includes(':'))

// 本地 SVG 图标
const localIcon = computed(() => {
  if (isIconify.value) return null
  return () => import(`./icons/${props.name}.svg?component`)
})
</script>

<template>
  <Icon
    v-if="isIconify"
    :icon="name"
    :width="size"
    :color="color"
    :class="className"
  />
  <component
    v-else
    :is="localIcon"
    :width="size"
    :height="size"
    :class="className"
  />
</template>
```

### 图标选择器组件

```vue
<!-- components/IconPicker/index.vue -->
<script setup lang="ts">
import { ref, computed } from 'vue'
import { Icon } from '@iconify/vue'

const props = defineProps<{
  modelValue?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const search = ref('')
const selected = ref(props.modelValue || '')

// 常用图标列表
const popularIcons = [
  'mdi:home', 'mdi:account', 'mdi:cog', 'mdi:bell',
  'mdi:email', 'mdi:heart', 'mdi:star', 'mdi:search',
  'mdi:plus', 'mdi:close', 'mdi:check', 'mdi:edit',
  'mdi:delete', 'mdi:download', 'mdi:upload', 'mdi:share',
]

const filteredIcons = computed(() => {
  if (!search.value) return popularIcons
  return popularIcons.filter(icon =>
    icon.toLowerCase().includes(search.value.toLowerCase())
  )
})

const selectIcon = (icon: string) => {
  selected.value = icon
  emit('update:modelValue', icon)
}
</script>

<template>
  <a-input v-model:value="search" placeholder="搜索图标..." />

  <div class="icon-grid">
    <div
      v-for="icon in filteredIcons"
      :key="icon"
      class="icon-item"
      :class="{ active: selected === icon }"
      @click="selectIcon(icon)"
    >
      <Icon :icon="icon" width="24" />
      <span>{{ icon.split(':')[1] }}</span>
    </div>
  </div>
</template>

<style scoped>
.icon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 8px;
  margin-top: 12px;
}

.icon-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
}

.icon-item:hover {
  background: #f5f5f5;
}

.icon-item.active {
  background: #e6f4ff;
  border: 1px solid #1890ff;
}

.icon-item span {
  font-size: 12px;
  margin-top: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}
</style>
```

## 图标搜索 API

### Iconify API

```typescript
// 搜索图标
const searchIcons = async (query: string) => {
  const response = await fetch(
    `https://api.iconify.design/search?query=${encodeURIComponent(query)}&limit=50`
  )
  return response.json()
}

// 获取图标 SVG
const getIconSvg = async (icon: string) => {
  const [prefix, name] = icon.split(':')
  const response = await fetch(
    `https://api.iconify.design/${prefix}/${name}.svg`
  )
  return response.text()
}
```

### 离线搜索

```typescript
// 本地图标索引
const iconIndex = {
  'mdi:home': { name: 'home', category: 'navigation' },
  'mdi:account': { name: 'account', category: 'user' },
  'mdi:cog': { name: 'settings', category: 'system' },
  // ...
}

const searchLocal = (query: string) => {
  const q = query.toLowerCase()
  return Object.entries(iconIndex)
    .filter(([key, meta]) =>
      key.includes(q) || meta.name.includes(q) || meta.category.includes(q)
    )
    .map(([key]) => key)
}
```

## 常用图标分类

### 导航类
```
mdi:home, mdi:menu, mdi:arrow-left, mdi:arrow-right
mdi:chevron-left, mdi:chevron-right, mdi:close, mdi:backburger
```

### 用户类
```
mdi:account, mdi:account-circle, mdi:account-group
mdi:login, mdi:logout, mdi:shield-account
```

### 操作类
```
mdi:plus, mdi:minus, mdi:pencil, mdi:delete
mdi:check, mdi:close, mdi:refresh, mdi:download
```

### 状态类
```
mdi:check-circle, mdi:alert-circle, mdi:information
mdi:warning, mdi:error, mdi:success
```

### 文件类
```
mdi:file, mdi:folder, mdi:file-document
mdi:file-image, mdi:file-video, mdi:file-music
```

### 通信类
```
mdi:email, mdi:message, mdi:bell
mdi:phone, mdi:chat, mdi:send
```