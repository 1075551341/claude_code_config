---
name: mobile-ui
description: 开发移动端UI界面
triggers: [开发移动端UI界面, 使用移动UI组件库, 实现移动端交互效果]
---

# 移动端 UI 组件

## 核心能力

**移动端UI设计、组件库使用、手势交互实现。**

---

## 适用场景

- 移动端UI开发
- 组件库使用
- 手势交互
- 响应式适配

---

## 主流组件库

### Vue 生态

| 库 | 特点 |
|------|------|
| Vant | 轻量、组件丰富 |
| NutUI | 京东出品 |
| Cube UI | 滴滴出品 |
| Ant Design Vue Mobile | 企业级 |

### React 生态

| 库 | 特点 |
|------|------|
| Ant Design Mobile | 企业级 |
| React Vant | Vant React版 |
| NutUI React | 京东出品 |
| Ionic React | 跨平台UI |

---

## Vant 使用

### 安装配置

```bash
npm install vant
# 或
npm install @vant/auto-import-resolver unplugin-vue-components -D
```

### 按需引入

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import Components from 'unplugin-vue-components/vite'
import { VantResolver } from '@vant/auto-import-resolver'

export default defineConfig({
  plugins: [
    vue(),
    Components({
      resolvers: [VantResolver()]
    })
  ]
})
```

### 常用组件

```vue
<template>
  <!-- 按钮 -->
  <van-button type="primary">主要按钮</van-button>
  <van-button type="success">成功按钮</van-button>
  
  <!-- 表单 -->
  <van-field v-model="value" label="用户名" placeholder="请输入用户名" />
  <van-field v-model="password" type="password" label="密码" />
  
  <!-- 列表 -->
  <van-list
    v-model:loading="loading"
    :finished="finished"
    finished-text="没有更多了"
    @load="onLoad"
  >
    <van-cell v-for="item in list" :key="item" :title="item" />
  </van-list>
  
  <!-- 弹窗 -->
  <van-popup v-model:show="show" position="bottom">
    <van-picker :columns="columns" @confirm="onConfirm" />
  </van-popup>
  
  <!-- 导航 -->
  <van-tabbar v-model="active">
    <van-tabbar-item icon="home-o">首页</van-tabbar-item>
    <van-tabbar-item icon="user-o">我的</van-tabbar-item>
  </van-tabbar>
</template>
```

---

## Ant Design Mobile

### 使用

```tsx
import { Button, Input, List, Modal } from 'antd-mobile'
import { useState } from 'react'

export default function App() {
  const [visible, setVisible] = useState(false)
  
  return (
    <div className="app">
      <Button color="primary" onClick={() => setVisible(true)}>
        打开弹窗
      </Button>
      
      <Modal
        visible={visible}
        onClose={() => setVisible(false)}
        content="这是弹窗内容"
      />
      
      <List header="列表标题">
        <List.Item>内容1</List.Item>
        <List.Item>内容2</List.Item>
      </List>
    </div>
  )
}
```

---

## 移动端适配

### rem 方案

```javascript
// lib-flexible
(function(win, doc) {
  const docEl = doc.documentElement
  const resizeEvt = 'orientationchange' in win ? 'orientationchange' : 'resize'
  
  function recalc() {
    const clientWidth = docEl.clientWidth
    if (!clientWidth) return
    docEl.style.fontSize = 100 * (clientWidth / 750) + 'px'  // 设计稿750px
  }
  
  recalc()
  win.addEventListener(resizeEvt, recalc, false)
})(window, document)

// postcss-pxtorem
// postcss.config.js
module.exports = {
  plugins: {
    'postcss-pxtorem': {
      rootValue: 100,
      propList: ['*']
    }
  }
}
```

### viewport 方案

```css
/* 使用vw单位 */
.container {
  width: 100vw;
  padding: 4vw;
  font-size: 3.2vw;
}

/* postcss-px-to-viewport */
/* postcss.config.js */
module.exports = {
  plugins: {
    'postcss-px-to-viewport': {
      viewportWidth: 375,
      viewportHeight: 667,
      unitPrecision: 5,
      viewportUnit: 'vw',
      selectorBlackList: [],
      minPixelValue: 1,
      mediaQuery: false
    }
  }
}
```

---

## 手势交互

### Touch 事件

```typescript
// 触摸开始
element.addEventListener('touchstart', (e) => {
  const touch = e.touches[0]
  startX = touch.clientX
  startY = touch.clientY
})

// 触摸移动
element.addEventListener('touchmove', (e) => {
  const touch = e.touches[0]
  const deltaX = touch.clientX - startX
  const deltaY = touch.clientY - startY
})

// 触摸结束
element.addEventListener('touchend', (e) => {
  const touch = e.changedTouches[0]
})
```

### 手势库

```typescript
// Hammer.js
import Hammer from 'hammerjs'

const mc = new Hammer(element)

mc.on('panleft panright swipe', (e) => {
  console.log(e.type)
})

mc.get('swipe').set({ direction: Hammer.DIRECTION_ALL })
```

---

## 常见交互模式

### 下拉刷新

```vue
<van-pull-refresh v-model="refreshing" @refresh="onRefresh">
  <van-list>
    <!-- 列表内容 -->
  </van-list>
</van-pull-refresh>

<script>
export default {
  data() {
    return {
      refreshing: false
    }
  },
  methods: {
    async onRefresh() {
      await this.loadData()
      this.refreshing = false
    }
  }
}
</script>
```

### 无限滚动

```vue
<van-list
  v-model:loading="loading"
  :finished="finished"
  @load="onLoad"
>
  <van-cell v-for="item in list" :key="item.id" :title="item.title" />
</van-list>
```

### 左滑删除

```vue
<van-swipe-cell>
  <van-cell title="单元格" value="内容" />
  <template #right>
    <van-button square type="danger" text="删除" />
  </template>
</van-swipe-cell>
```

---

## 注意事项

```
必须:
- 适配不同屏幕尺寸
- 处理触摸事件
- 优化滚动性能
- 考虑安全区域

避免:
- 使用hover效果
- 固定像素尺寸
- 阻塞主线程
- 忽略刘海屏适配
```

---

## 相关技能

- `vue-development` - Vue开发
- `react-component` - React组件
- `mobile-performance` - 移动端性能