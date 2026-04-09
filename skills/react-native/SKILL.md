---
name: react-native
description: 当需要开发React Native跨平台移动应用、使用JavaScript/TypeScript开发移动端时调用此技能。触发词：React Native、RN开发、移动端开发、React Native CLI、Expo、移动应用开发、iOS Android开发。
---

# React Native 跨平台开发

## 核心能力

**React Native应用开发、跨平台组件、原生模块集成。**

---

## 适用场景

- React Native 应用开发
- iOS/Android 双端开发
- 原生模块集成
- Expo 快速开发

---

## 项目结构

```
src/
├── App.tsx             # 应用入口
├── navigation/         # 导航配置
│   └── AppNavigator.tsx
├── screens/            # 页面
│   ├── HomeScreen.tsx
│   └── DetailScreen.tsx
├── components/         # 组件
│   ├── Button.tsx
│   └── Card.tsx
├── hooks/              # 自定义Hook
├── services/           # 服务层
├── store/              # 状态管理
├── types/              # 类型定义
└── utils/              # 工具函数
```

---

## 核心组件

```tsx
import { View, Text, TouchableOpacity, FlatList } from 'react-native';

// 基础布局
<View style={styles.container}>
  <Text style={styles.title}>Hello</Text>
  <TouchableOpacity onPress={handlePress}>
    <Text>按钮</Text>
  </TouchableOpacity>
</View>

// 列表
<FlatList
  data={items}
  keyExtractor={(item) => item.id}
  renderItem={({ item }) => (
    <Text>{item.name}</Text>
  )}
/>
```

---

## 样式处理

```tsx
import { StyleSheet } from 'react-native';

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 16,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
});

// 条件样式
<View style={[styles.container, isActive && styles.active]} />
```

---

## 导航

### React Navigation

```tsx
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';

const Stack = createStackNavigator();

function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Detail" component={DetailScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

// 页面跳转
navigation.navigate('Detail', { id: 1 });
navigation.goBack();
```

---

## 网络请求

```tsx
// Fetch
const fetchData = async () => {
  const response = await fetch('https://api.example.com/data');
  const data = await response.json();
  return data;
};

// Axios
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://api.example.com',
  timeout: 10000,
});

const response = await api.get('/data');
```

---

## 原生模块

```tsx
// iOS (Objective-C)
RCT_EXPORT_METHOD(showToast:(NSString *)message) {
  // 原生实现
}

// Android (Kotlin)
@ReactMethod
fun showToast(message: String) {
  // 原生实现
}

// JS调用
import { NativeModules } from 'react-native';
NativeModules.MyModule.showToast('Hello');
```

---

## Expo 开发

```bash
# 创建项目
npx create-expo-app my-app

# 启动
npx expo start

# 构建
npx expo build:android
npx expo build:ios

# 发布
npx expo publish
```

---

## 常用命令

```bash
# 创建项目
npx react-native init MyProject

# iOS
cd ios && pod install
npx react-native run-ios

# Android
npx react-native run-android

# 调试
npx react-native start --reset-cache
```

---

## 注意事项

```
必须：
- 处理平台差异
- 优化列表性能
- 管理内存泄漏
- 测试双端表现

避免：
- 频繁重新渲染
- 阻塞JS线程
- 忽略安全区域
- 硬编码尺寸
```

---

## 相关技能

- `flutter-development` - Flutter 开发
- `react-component` - React 组件
- `mobile-developer` agent - 移动端开发