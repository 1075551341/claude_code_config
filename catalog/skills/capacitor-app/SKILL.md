---
name: capacitor-app
description: 开发混合移动应用、使用Capacitor/Ionic框架、将Web应用打包为移动应用
triggers: [Capacitor, Ionic, 混合应用, Web转原生, Ionic Capacitor, 原生插件, Capacitor插件, 混合开发, Ionic框架, Ionic Angular, Ionic React, Ionic Vue]
---

# Capacitor 混合应用

## 核心能力

**Web应用打包原生、原生API调用、跨平台混合开发。**

---

## 适用场景

- Web应用打包移动端
- 混合应用开发
- 原生功能调用
- 跨平台应用

---

## 项目初始化

```bash
# 安装Capacitor
npm install @capacitor/core @capacitor/cli

# 初始化
npx cap init

# 添加平台
npm install @capacitor/android
npm install @capacitor/ios

npx cap add android
npx cap add ios
```

---

## 项目结构

```
project/
├── src/                    # Web源码
│   ├── index.html
│   └── ...
├── android/                # Android项目
│   └── app/
├── ios/                    # iOS项目
│   └── App/
├── capacitor.config.ts     # 配置文件
└── package.json
```

---

## 配置文件

```typescript
import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.example.app',
  appName: 'My App',
  webDir: 'dist',
  bundledWebRuntime: false,
  
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: '#ffffff',
      showSpinner: false
    },
    StatusBar: {
      style: 'dark',
      backgroundColor: '#ffffff'
    }
  },
  
  server: {
    androidScheme: 'https'
  }
};

export default config;
```

---

## 常用插件

### 官方插件

```typescript
// 安装
npm install @capacitor/camera
npm install @capacitor/geolocation
npm install @capacitor/storage
npm install @capacitor/push-notifications

// 使用
import { Camera, CameraResultType } from '@capacitor/camera';

const takePicture = async () => {
  const image = await Camera.getPhoto({
    quality: 90,
    allowEditing: true,
    resultType: CameraResultType.Uri
  });
  
  const imageUrl = image.webPath;
};

// 地理位置定位
import { Geolocation } from '@capacitor/geolocation';

const getCurrentPosition = async () => {
  const coordinates = await Geolocation.getCurrentPosition();
  console.log('Position:', coordinates.coords);
};

// 本地存储
import { Preferences } from '@capacitor/preferences';

await Preferences.set({ key: 'name', value: 'Max' });
const { value } = await Preferences.get({ key: 'name' });

// 推送通知
import { PushNotifications } from '@capacitor/push-notifications';

await PushNotifications.requestPermissions();
await PushNotifications.register();

PushNotifications.addListener('pushNotificationReceived', (notification) => {
  console.log('Push received:', notification);
});
```

---

## 原生功能调用

### 设备信息

```typescript
import { Device } from '@capacitor/device';

const info = await Device.getInfo();
console.log(info.platform);  // 'ios' | 'android' | 'web'
console.log(info.model);
console.log(info.osVersion);
```

### 文件系统

```typescript
import { Filesystem, Directory } from '@capacitor/filesystem';

// 写入文件
await Filesystem.writeFile({
  path: 'myFile.txt',
  data: 'Hello World',
  directory: Directory.Documents
});

// 读取文件
const result = await Filesystem.readFile({
  path: 'myFile.txt',
  directory: Directory.Documents
});
```

### 应用信息

```typescript
import { App } from '@capacitor/app';

// 获取应用信息
const info = await App.getInfo();
console.log(info.version);

// 监听应用状态
App.addListener('appStateChange', ({ isActive }) => {
  console.log('App is active:', isActive);
});

// 监听返回按钮
App.addListener('backButton', () => {
  // 处理返回
});
```

---

## 开发流程

### 开发调试

```bash
# 运行Web开发服务器
npm run dev

# 同步到原生项目
npx cap sync

# 打开原生IDE
npx cap open android
npx cap open ios

# 在设备运行
npx cap run android
npx cap run ios
```

### 热重载

```typescript
// capacitor.config.ts
import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  // ...
  server: {
    url: 'http://192.168.1.100:5173',  // 开发机IP
    cleartext: true  // Android需要
  }
};
```

---

## 自定义插件

### 定义接口

```typescript
// src/plugins/definitions.ts
export interface MyPlugin {
  echo(options: { value: string }): Promise<{ value: string }>;
}

declare module '@capacitor/core' {
  interface PluginRegistry {
    MyPlugin: MyPlugin;
  }
}
```

### Android实现

```java
// android/app/src/main/java/com/example/MyPlugin.java
package com.example;

import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.annotation.CapacitorPlugin;

@CapacitorPlugin(name = "MyPlugin")
public class MyPlugin extends Plugin {
    @PluginMethod
    public void echo(PluginCall call) {
        String value = call.getString("value");
        JSObject ret = new JSObject();
        ret.put("value", value);
        call.resolve(ret);
    }
}
```

### iOS实现

```swift
// ios/App/App/MyPlugin.swift
import Capacitor

@objc(MyPlugin)
public class MyPlugin: CAPPlugin {
    @objc func echo(_ call: CAPPluginCall) {
        let value = call.getString("value") ?? ""
        call.success([
            "value": value
        ])
    }
}
```

---

## 构建发布

```bash
# 构建
npm run build

# 同步
npx cap sync

# Android发布
cd android
./gradlew assembleRelease

# iOS发布
# 打开Xcode → Archive → Distribute
```

---

## 注意事项

```
必须:
- 测试真机运行
- 处理权限请求
- 适配不同平台
- 优化首屏加载

避免:
- 依赖Web特有API
- 忽略原生权限
- 过大的包体积
- 阻塞UI线程
```

---

## 相关技能

- `ionic-app` - Ionic开发
- `electron-app` - Electron桌面应用
- `mobile-deployment` - 应用发布
