---
name: ionic-app
description: 当需要使用Ionic框架开发混合应用、结合Angular/React/Vue开发移动应用时调用此技能。触发词：Ionic、Ionic框架、Ionic开发、Ionic Angular、Ionic React、Ionic Vue、混合应用、Ionic Capacitor。
---

# Ionic 应用开发

## 核心能力

**Ionic框架开发、跨平台混合应用、Capacitor集成。**

---

## 适用场景

- Ionic 混合应用开发
- Angular/React/Vue 集成
- 跨平台移动应用
- 企业级应用开发

---

## 项目创建

```bash
# 安装CLI
npm install -g @ionic/cli

# 创建项目
ionic start myApp tabs --type=angular
ionic start myApp tabs --type=react
ionic start myApp tabs --type=vue

# 运行
ionic serve

# 添加平台
ionic cap add android
ionic cap add ios
```

---

## 项目结构 (Angular)

```
src/
├── app/
│   ├── home/
│   │   ├── home.module.ts
│   │   ├── home.page.html
│   │   ├── home.page.scss
│   │   └── home.page.ts
│   ├── app-routing.module.ts
│   ├── app.component.html
│   ├── app.component.ts
│   └── app.module.ts
├── assets/
├── environments/
├── theme/
├── global.scss
└── index.html
```

---

## 核心组件

### 导航

```html
<!-- Tabs导航 -->
<ion-tabs>
  <ion-tab-bar slot="bottom">
    <ion-tab-button tab="home">
      <ion-icon name="home"></ion-icon>
      <ion-label>首页</ion-label>
    </ion-tab-button>
    <ion-tab-button tab="settings">
      <ion-icon name="settings"></ion-icon>
      <ion-label>设置</ion-label>
    </ion-tab-button>
  </ion-tab-bar>
</ion-tabs>

<!-- 侧边栏 -->
<ion-menu side="start" contentId="main">
  <ion-header>
    <ion-toolbar>
      <ion-title>菜单</ion-title>
    </ion-toolbar>
  </ion-header>
  <ion-content>
    <ion-list>
      <ion-item>选项1</ion-item>
      <ion-item>选项2</ion-item>
    </ion-list>
  </ion-content>
</ion-menu>
```

### 常用UI组件

```html
<!-- 卡片 -->
<ion-card>
  <ion-card-header>
    <ion-card-title>卡片标题</ion-card-title>
    <ion-card-subtitle>副标题</ion-card-subtitle>
  </ion-card-header>
  <ion-card-content>
    卡片内容
  </ion-card-content>
</ion-card>

<!-- 列表 -->
<ion-list>
  <ion-item>
    <ion-label>项目1</ion-label>
  </ion-item>
  <ion-item>
    <ion-label>项目2</ion-label>
  </ion-item>
</ion-list>

<!-- 按钮 -->
<ion-button>默认按钮</ion-button>
<ion-button color="primary">主要按钮</ion-button>
<ion-button color="danger" fill="outline">危险按钮</ion-button>

<!-- 表单 -->
<ion-item>
  <ion-label position="floating">用户名</ion-label>
  <ion-input [(ngModel)]="username"></ion-input>
</ion-item>

<!-- 加载 -->
<ion-loading [isOpen]="loading" message="加载中..."></ion-loading>
```

---

## React 版本

### 组件使用

```tsx
import { IonContent, IonHeader, IonPage, IonTitle, IonToolbar, IonButton, IonCard, IonCardHeader, IonCardTitle, IonCardContent } from '@ionic/react';

const Home: React.FC = () => {
  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonTitle>首页</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent fullscreen>
        <IonCard>
          <IonCardHeader>
            <IonCardTitle>欢迎</IonCardTitle>
          </IonCardHeader>
          <IonCardContent>
            <IonButton routerLink="/detail">查看详情</IonButton>
          </IonCardContent>
        </IonCard>
      </IonContent>
    </IonPage>
  );
};

export default Home;
```

### 路由

```tsx
import { IonReactRouter } from '@ionic/react-router';
import { Route, Redirect } from 'react-router';

<IonReactRouter>
  <IonRouterOutlet>
    <Route path="/home" component={Home} exact />
    <Route path="/detail/:id" component={Detail} />
    <Redirect exact from="/" to="/home" />
  </IonRouterOutlet>
</IonReactRouter>
```

---

## Vue 版本

### 组件

```vue
<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-title>首页</ion-title>
      </ion-toolbar>
    </ion-header>
    <ion-content>
      <ion-card>
        <ion-card-header>
          <ion-card-title>卡片</ion-card-title>
        </ion-card-header>
        <ion-card-content>
          <ion-button @click="handleClick">点击</ion-button>
        </ion-card-content>
      </ion-card>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const count = ref(0)

const handleClick = () => {
  count.value++
}
</script>
```

---

## Native 功能

### 使用Capacitor插件

```typescript
import { Camera, CameraResultType } from '@capacitor/camera';
import { Geolocation } from '@capacitor/geolocation';
import { Haptics, ImpactStyle } from '@capacitor/haptics';

// 相机
const takePhoto = async () => {
  const image = await Camera.getPhoto({
    quality: 90,
    allowEditing: true,
    resultType: CameraResultType.Uri
  });
  return image.webPath;
};

// 定位
const getLocation = async () => {
  const position = await Geolocation.getCurrentPosition();
  return position.coords;
};

// 触觉反馈
const vibrate = async () => {
  await Haptics.impact({ style: ImpactStyle.Medium });
};
```

---

## 主题定制

```scss
// variables.scss
:root {
  --ion-color-primary: #3880ff;
  --ion-color-secondary: #3dc2ff;
  --ion-color-success: #2dd36f;
  --ion-color-warning: #ffc409;
  --ion-color-danger: #eb445a;
  
  --ion-background-color: #ffffff;
  --ion-text-color: #000000;
}

// 暗色模式
@media (prefers-color-scheme: dark) {
  :root {
    --ion-background-color: #1a1a1a;
    --ion-text-color: #ffffff;
  }
}
```

---

## 构建发布

```bash
# 构建
ionic build

# 同步到原生
ionic cap sync

# 打开IDE
ionic cap open android
ionic cap open ios

# 发布到应用商店
# Android: 上传AAB到Google Play
# iOS: 上传到App Store Connect
```

---

## 注意事项

```
必须:
- 使用Ionic组件而非HTML元素
- 处理平台差异
- 优化首屏加载
- 测试真机效果

避免:
- 混用Web和Ionic组件
- 忽略移动端适配
- 过大包体积
- 忽略权限处理
```

---

## 相关技能

- `capacitor-app` - Capacitor原生
- `angular` - Angular框架
- `mobile-deployment` - 应用发布