---
name: uniapp-development
description: 开发UniApp跨平台应用
triggers: [开发UniApp跨平台应用, 编写微信小程序, 实现多端适配]
---

# UniApp 开发

## 项目结构

```
src/
├── pages/              # 页面
│   ├── index/
│   │   └── index.vue
│   └── user/
│       └── profile.vue
├── components/         # 组件
├── static/             # 静态资源
├── store/              # 状态管理
├── api/                # API 封装
├── utils/              # 工具函数
├── pages.json          # 页面配置
├── manifest.json       # 应用配置
└── uni.scss            # 全局样式变量
```

## 页面配置

```json
// pages.json
{
  "pages": [
    {
      "path": "pages/index/index",
      "style": {
        "navigationBarTitleText": "首页",
        "navigationBarBackgroundColor": "#ffffff",
        "enablePullDownRefresh": true
      }
    }
  ],
  "globalStyle": {
    "navigationBarTextStyle": "black",
    "navigationBarTitleText": "App",
    "navigationBarBackgroundColor": "#ffffff",
    "backgroundColor": "#f8f8f8"
  },
  "tabBar": {
    "color": "#999999",
    "selectedColor": "#007AFF",
    "list": [
      { "pagePath": "pages/index/index", "text": "首页", "iconPath": "static/tab/home.png", "selectedIconPath": "static/tab/home-active.png" },
      { "pagePath": "pages/user/profile", "text": "我的", "iconPath": "static/tab/user.png", "selectedIconPath": "static/tab/user-active.png" }
    ]
  }
}
```

## Vue 3 语法

### 页面组件
```vue
<!-- pages/index/index.vue -->
<template>
  <view class="container">
    <view class="header">
      <text class="title">{{ title }}</text>
    </view>

    <!-- 列表 -->
    <scroll-view
      scroll-y
      :style="{ height: scrollHeight + 'px' }"
      @scrolltolower="loadMore"
    >
      <view v-for="item in list" :key="item.id" class="item">
        {{ item.name }}
      </view>
      <uni-load-more :status="loadStatus" />
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onPullDownRefresh, onReachBottom } from '@dcloudio/uni-app'

// 状态
const title = ref('首页')
const list = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const hasMore = ref(true)

// 计算属性
const loadStatus = computed(() => {
  if (loading.value) return 'loading'
  if (!hasMore.value) return 'noMore'
  return 'more'
})

const scrollHeight = computed(() => {
  const info = uni.getSystemInfoSync()
  return info.windowHeight - 44 // 减去导航栏高度
})

// 生命周期
onMounted(() => {
  loadData()
})

// 下拉刷新
onPullDownRefresh(async () => {
  page.value = 1
  hasMore.value = true
  await loadData()
  uni.stopPullDownRefresh()
})

// 上拉加载
onReachBottom(() => {
  if (!loading.value && hasMore.value) {
    page.value++
    loadData()
  }
})

// 方法
const loadData = async () => {
  loading.value = true
  try {
    const res = await api.getList({ page: page.value })
    if (page.value === 1) {
      list.value = res.data
    } else {
      list.value.push(...res.data)
    }
    hasMore.value = res.data.length > 0
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.container {
  padding: 20rpx;
}
.item {
  padding: 20rpx;
  background: #fff;
  margin-bottom: 20rpx;
  border-radius: 8rpx;
}
</style>
```

### 组件定义
```vue
<!-- components/UserCard/UserCard.vue -->
<template>
  <view class="user-card" @click="handleClick">
    <image class="avatar" :src="user.avatar" mode="aspectFill" />
    <view class="info">
      <text class="name">{{ user.name }}</text>
      <text class="desc">{{ user.desc }}</text>
    </view>
    <slot />
  </view>
</template>

<script setup lang="ts">
interface Props {
  user: {
    id: string
    name: string
    avatar: string
    desc?: string
  }
}

const props = defineProps<Props>()
const emit = defineEmits<{
  click: [id: string]
}>()

const handleClick = () => {
  emit('click', props.user.id)
}
</script>

<style lang="scss" scoped>
.user-card {
  display: flex;
  align-items: center;
  padding: 24rpx;
  background: #fff;
  border-radius: 12rpx;
}
.avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
}
</style>
```

## API 封装

```typescript
// api/request.ts
const BASE_URL = import.meta.env.VITE_API_BASE_URL

interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  header?: Record<string, string>
}

export function request<T>(options: RequestOptions): Promise<T> {
  const token = uni.getStorageSync('token')

  return new Promise((resolve, reject) => {
    uni.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        ...options.header
      },
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data as T)
        } else if (res.statusCode === 401) {
          // 跳转登录
          uni.navigateTo({ url: '/pages/login/login' })
          reject(new Error('未授权'))
        } else {
          uni.showToast({ title: '请求失败', icon: 'none' })
          reject(new Error(res.data?.msg || '请求失败'))
        }
      },
      fail: (err) => {
        uni.showToast({ title: '网络错误', icon: 'none' })
        reject(err)
      }
    })
  })
}

// api/user.ts
export const userApi = {
  getList: (params) => request({ url: '/users', data: params }),
  getDetail: (id: string) => request({ url: `/users/${id}` }),
  create: (data) => request({ url: '/users', method: 'POST', data })
}
```

## 多端适配

### 条件编译
```vue
<template>
  <view>
    <!-- #ifdef H5 -->
    <view>H5 专属内容</view>
    <!-- #endif -->

    <!-- #ifdef MP-WEIXIN -->
    <button open-type="getUserInfo" @getuserinfo="onGetUserInfo">微信授权</button>
    <!-- #endif -->

    <!-- #ifdef APP-PLUS -->
    <view>App 专属功能</view>
    <!-- #endif -->
  </view>
</template>

<script setup lang="ts">
// 条件编译函数
// #ifdef H5
const shareToWechat = () => {
  // H5 分享逻辑
}
// #endif

// #ifdef MP-WEIXIN
const shareToWechat = () => {
  uni.share({
    provider: 'weixin',
    scene: 'WXSceneSession',
    type: 0,
    success: () => console.log('分享成功')
  })
}
// #endif
</script>
```

### 单位适配
```scss
// uni.scss
$uni-color-primary: #007AFF;

// 使用 rpx（推荐）
.card {
  width: 750rpx;  // 全屏宽度
  padding: 32rpx;
  font-size: 28rpx;
}
```

## 性能优化

| 优化项 | 方案 |
|--------|------|
| 图片懒加载 | `<image lazy-load />` |
| 长列表 | 使用 `<scroll-view>` + 分页 |
| 避免频繁 setData | 合并数据更新 |
| 组件按需加载 | `easycom` 自动导入 |
| 减少 DOM 层级 | 扁平化视图结构 |
| 预加载 | `uni.preloadPage()` |

## 常用 API

```typescript
// 路由
uni.navigateTo({ url: '/pages/detail/detail?id=1' })
uni.redirectTo({ url: '/pages/login/login' })
uni.switchTab({ url: '/pages/index/index' })
uni.navigateBack({ delta: 1 })

// 存储
uni.setStorageSync('key', value)
const value = uni.getStorageSync('key')

// 提示
uni.showToast({ title: '成功', icon: 'success' })
uni.showLoading({ title: '加载中' })
uni.hideLoading()
uni.showModal({ title: '提示', content: '确认删除？' })

// 图片
uni.chooseImage({ count: 9, success: (res) => console.log(res.tempFilePaths) })
uni.previewImage({ urls: ['url1', 'url2'] })

// 扫码
uni.scanCode({ success: (res) => console.log(res.result) })
```