---
name: mini-program
description: 当需要开发微信小程序、支付宝小程序、抖音小程序、百度小程序等平台小程序时调用此技能。触发词：小程序开发、微信小程序、支付宝小程序、抖音小程序、百度小程序、小程序框架、Taro、小程序组件。
---

# 小程序开发

## 核心能力

**多平台小程序开发、小程序框架使用、跨平台适配。**

---

## 适用场景

- 微信小程序开发
- 支付宝小程序开发
- 抖音/百度小程序
- 小程序跨平台开发

---

## 平台对比

| 平台 | 开发语言 | UI框架 | 特点 |
|------|----------|--------|------|
| 微信 | WXML/WXSS/JS | WeUI | 生态最完善 |
| 支付宝 | AXML/ACSS/JS | AntUI | 金融场景 |
| 抖音 | TTMXL/TTSS/JS | - | 视频生态 |
| 百度 | SWAN/CSS/JS | - | 搜索入口 |

---

## 微信小程序

### 项目结构

```
miniprogram/
├── pages/
│   ├── index/
│   │   ├── index.js
│   │   ├── index.json
│   │   ├── index.wxml
│   │   └── index.wxss
│   └── detail/
├── components/
│   └── card/
├── utils/
├── app.js
├── app.json
├── app.wxss
└── project.config.json
```

### 页面定义

```javascript
// pages/index/index.js
Page({
  data: {
    message: 'Hello World',
    list: []
  },
  
  onLoad() {
    this.loadData()
  },
  
  async loadData() {
    const res = await wx.request({
      url: 'https://api.example.com/data'
    })
    this.setData({ list: res.data })
  },
  
  handleTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/detail/detail?id=${id}`
    })
  }
})
```

### WXML 模板

```xml
<view class="container">
  <text>{{message}}</text>
  
  <view wx:for="{{list}}" wx:key="id" 
        class="item" 
        data-id="{{item.id}}"
        bindtap="handleTap">
    <image src="{{item.image}}" mode="aspectFill" />
    <text>{{item.title}}</text>
  </view>
  
  <button bindtap="onSubmit">提交</button>
</view>
```

### WXSS 样式

```css
.container {
  padding: 20rpx;
  background-color: #f5f5f5;
}

.item {
  display: flex;
  align-items: center;
  padding: 20rpx;
  background: #fff;
  border-radius: 8rpx;
  margin-bottom: 20rpx;
}

.item image {
  width: 120rpx;
  height: 120rpx;
  border-radius: 8rpx;
}
```

### 常用 API

```javascript
// 导航
wx.navigateTo({ url: '/pages/detail/detail' })
wx.redirectTo({ url: '/pages/index/index' })
wx.switchTab({ url: '/pages/home/home' })
wx.navigateBack({ delta: 1 })

// 提示
wx.showToast({ title: '成功', icon: 'success' })
wx.showLoading({ title: '加载中' })
wx.hideLoading()
wx.showModal({
  title: '提示',
  content: '确定删除？',
  success(res) {
    if (res.confirm) { }
  }
})

// 存储
wx.setStorageSync('key', 'value')
wx.getStorageSync('key')

// 用户信息
wx.getUserProfile({
  desc: '用于展示用户信息',
  success(res) {
    console.log(res.userInfo)
  }
})

// 支付
wx.requestPayment({
  timeStamp: '',
  nonceStr: '',
  package: '',
  signType: 'MD5',
  paySign: '',
  success(res) { }
})
```

---

## Taro 跨平台

### 项目结构

```
src/
├── pages/
│   ├── index/
│   │   └── index.tsx
│   └── detail/
├── components/
├── services/
├── store/
├── app.config.ts
├── app.tsx
└── index.html
```

### 页面组件

```tsx
import { View, Text, Button } from '@tarojs/components'
import { useLoad, useDidShow } from '@tarojs/taro'
import { useState } from 'react'

export default function Index() {
  const [list, setList] = useState([])
  
  useLoad(() => {
    console.log('Page loaded.')
  })
  
  useDidShow(() => {
    loadData()
  })
  
  const loadData = async () => {
    const res = await Taro.request({
      url: 'https://api.example.com/data'
    })
    setList(res.data)
  }
  
  return (
    <View className="container">
      {list.map(item => (
        <View key={item.id} className="item">
          <Text>{item.title}</Text>
        </View>
      ))}
    </View>
  )
}
```

### 页面配置

```typescript
// app.config.ts
export default defineAppConfig({
  pages: [
    'pages/index/index',
    'pages/detail/detail'
  ],
  window: {
    backgroundTextStyle: 'light',
    navigationBarBackgroundColor: '#fff',
    navigationBarTitleText: 'WeChat',
    navigationBarTextStyle: 'black'
  },
  tabBar: {
    list: [{
      pagePath: 'pages/index/index',
      text: '首页',
      iconPath: 'assets/home.png',
      selectedIconPath: 'assets/home-active.png'
    }, {
      pagePath: 'pages/user/index',
      text: '我的',
      iconPath: 'assets/user.png',
      selectedIconPath: 'assets/user-active.png'
    }]
  }
})
```

---

## uni-app 开发

```vue
<template>
  <view class="container">
    <text>{{ message }}</text>
    <button @click="handleTap">点击</button>
    
    <view v-for="item in list" :key="item.id">
      {{ item.title }}
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      message: 'Hello',
      list: []
    }
  },
  onLoad() {
    this.loadData()
  },
  methods: {
    async loadData() {
      const res = await uni.request({
        url: 'https://api.example.com/data'
      })
      this.list = res.data
    },
    handleTap() {
      uni.navigateTo({ url: '/pages/detail/detail' })
    }
  }
}
</script>

<style>
.container {
  padding: 20rpx;
}
</style>
```

---

## 发布流程

### 微信小程序

```bash
# 上传代码
# 使用微信开发者工具 → 上传

# 或使用 CLI
# npm install -g miniprogram-ci

miniprogram-ci upload \
  --pp ./dist \
  --pkp ./private.key \
  --appid wxAPPID \
  -r 1 \
  --uv 1.0.0 \
  -d "上传描述"
```

### 版本发布

```
开发版 → 体验版 → 审核版 → 线上版

1. 开发版：开发调试
2. 体验版：内部测试
3. 审核版：提交审核
4. 线上版：正式发布
```

---

## 注意事项

```
必须:
- 遵循各平台规范
- 处理授权登录流程
- 优化包体积
- 适配不同平台差异

避免:
- 使用不支持的ES特性
- 过大的包体积
- 频繁setData
- 忽略平台审核规则
```

---

## 相关技能

- `uniapp-development` - UniApp开发
- `vue-development` - Vue开发
- `mobile-deployment` - 移动应用发布