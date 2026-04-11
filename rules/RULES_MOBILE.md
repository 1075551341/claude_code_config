---
description: 移动端开发规则（Flutter/RN/UniApp/原生）
alwaysApply: false
globs: ["*.dart", "pubspec.yaml", "*.rn.*", "uniapp.json", "*.swift", "*.kt", "*.xcodeproj", "AndroidManifest.xml"]
---

# 移动端开发规则（专用）

> 配合核心规则使用，仅在移动端开发场景加载

## 技术选型

```markdown
场景               →  推荐方案
───────────────────────────────────
跨平台应用         →  Flutter / React Native / UniApp
iOS 原生           →  Swift / SwiftUI
Android 原生       →  Kotlin / Jetpack Compose
小程序             →  UniApp / Taro / 原生小程序
混合应用           →  Ionic / Capacitor
```

## Flutter 开发规范

### 项目结构

```
lib/
├── main.dart              # 应用入口
├── app/                   # 应用级配置
│   ├── app.dart           # MaterialApp 配置
│   └── routes.dart        # 路由配置
├── features/              # 功能模块
│   ├── auth/
│   │   ├── data/          # 数据层
│   │   ├── domain/        # 领域层
│   │   └── presentation/  # 展示层
│   └── home/
├── core/                  # 核心功能
│   ├── theme/
│   ├── constants/
│   └── utils/
└── shared/                # 共享组件
    ├── widgets/
    └── models/
```

### 状态管理

```dart
// Riverpod 推荐
final counterProvider = StateProvider<int>((ref) => 0);

// 使用
class CounterWidget extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final count = ref.watch(counterProvider);
    return Text('$count');
  }
}

// Bloc 模式
class CounterCubit extends Cubit<int> {
  CounterCubit() : super(0);
  void increment() => emit(state + 1);
}
```

### 性能优化

```dart
// 使用 const 构造函数
const Text('Hello');  // ✅
Text('Hello');        // ❌ 每次重建

// ListView 优化
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) => ItemWidget(items[index]),
);

// 图片缓存
CachedNetworkImage(
  imageUrl: url,
  placeholder: (context, url) => CircularProgressIndicator(),
  errorWidget: (context, url, error) => Icon(Icons.error),
);
```

## React Native 开发规范

### 项目结构

```
src/
├── App.tsx                # 应用入口
├── navigation/            # 导航配置
├── screens/               # 页面组件
├── components/            # 共享组件
├── hooks/                 # 自定义 Hooks
├── services/              # API 服务
├── store/                 # 状态管理
├── utils/                 # 工具函数
└── types/                 # TypeScript 类型
```

### 样式规范

```typescript
// 使用 StyleSheet.create
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

// 或使用 styled-components
const Container = styled.View`
  flex: 1;
  background-color: #fff;
  padding: 16px;
`;
```

### 性能优化

```typescript
// 使用 memo 避免不必要渲染
const Item = memo(({ data }) => (
  <View>
    <Text>{data.title}</Text>
  </View>
));

// 使用 useCallback 缓存回调
const handlePress = useCallback(() => {
  navigation.navigate('Detail');
}, [navigation]);

// FlatList 优化
<FlatList
  data={items}
  renderItem={renderItem}
  keyExtractor={(item) => item.id}
  removeClippedSubviews={true}
  maxToRenderPerBatch={10}
  windowSize={5}
/>
```

## UniApp 开发规范

### 项目结构

```
src/
├── pages/                 # 页面
│   ├── index/
│   │   └── index.vue
│   └── user/
│       └── index.vue
├── components/            # 组件
├── static/                # 静态资源
├── store/                 # Vuex/Pinia
├── utils/                 # 工具函数
├── api/                   # 接口定义
├── App.vue                # 应用入口
├── main.ts                # 主入口
└── manifest.json          # 应用配置
```

### 条件编译

```vue
<template>
  <view>
    <!-- #ifdef MP-WEIXIN -->
    <button open-type="getPhoneNumber">微信授权</button>
    <!-- #endif -->

    <!-- #ifdef APP-PLUS -->
    <button @click="nativeLogin">原生登录</button>
    <!-- #endif -->

    <!-- #ifdef H5 -->
    <button @click="h5Login">H5登录</button>
    <!-- #endif -->
  </view>
</template>
```

### API 封装

```typescript
// utils/request.ts
export const request = <T>(options: RequestOptions): Promise<T> => {
  return new Promise((resolve, reject) => {
    uni.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'Authorization': getToken(),
        'Content-Type': 'application/json',
      },
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data as T);
        } else {
          reject(new Error(`HTTP ${res.statusCode}`));
        }
      },
      fail: reject,
    });
  });
};
```

## 性能优化规范

### 启动优化

```markdown
优化项               →  方案
───────────────────────────────────
首屏渲染             →  懒加载非关键组件
图片加载             →  预加载关键图片，使用 WebP
代码分割             →  动态 import，按需加载
原生模块             →  延迟初始化非必要 SDK
```

### 内存管理

```typescript
// 及时清理资源
useEffect(() => {
  const subscription = eventEmitter.addListener('event', handler);
  return () => subscription.remove();  // 清理订阅
}, []);

// 图片内存优化
<Image
  source={{ uri: url, cache: 'reload' }}
  resizeMode="contain"
  style={{ width: 200, height: 200 }}
/>
```

### 包体积优化

```markdown
优化项               →  方案
───────────────────────────────────
资源压缩             →  图片 WebP 格式，音频压缩
代码压缩             →  ProGuard/R8 (Android)，Strip (iOS)
动态库               →  合并相似库，移除未使用依赖
资源分级             →  按 dpi 分层，使用矢量图
```

## 发布流程规范

### iOS 发布

```markdown
1. 代码审查 & 测试
2. 更新版本号（Info.plist）
3. 构建 Archive（Xcode）
4. 上传 App Store Connect
5. 填写发布说明
6. 提交审核
7. 审核通过后发布

注意事项：
- 隐私政策 URL 必须有效
- 权限使用说明完整
- 内购必须使用 IAP
- 不允许热更原生代码
```

### Android 发布

```markdown
1. 代码审查 & 测试
2. 更新版本号（build.gradle）
3. 签名打包（AAB/APK）
4. 上传 Google Play Console
5. 填写发布说明
6. 提交审核
7. 审核通过后发布

注意事项：
- 目标 API 级别符合要求
- 权限声明合规
- 隐私政策完整
- 64 位支持
```

### 小程序发布

```markdown
1. 代码审查 & 测试
2. 更新版本号（manifest.json）
3. 上传代码（开发者工具）
4. 提交审核
5. 审核通过后发布

注意事项：
- 用户隐私合规
- 内容安全审查
- 虚拟支付限制（iOS）
- 类目资质完备
```

## 安全规范

### 数据存储

```typescript
// 敏感数据加密存储
import SecureStorage from 'react-native-encrypted-storage';

// ✅ 安全存储
await SecureStorage.setItem('token', token);
const token = await SecureStorage.getItem('token');

// ❌ 不安全存储
await AsyncStorage.setItem('token', token);  // 明文存储
```

### 网络安全

```typescript
// SSL Pinning
const agent = new https.Agent({
  ca: fs.readFileSync('./cert.pem'),
});

// 证书校验（Android）
<certificates src="system" />
<certificates src="user" />
```

### 权限管理

```typescript
// 动态权限请求
import { PermissionsAndroid } from 'react-native';

async function requestCameraPermission() {
  const granted = await PermissionsAndroid.request(
    PermissionsAndroid.PERMISSIONS.CAMERA,
    {
      title: '相机权限',
      message: '需要相机权限以拍摄照片',
      buttonNeutral: '稍后询问',
      buttonNegative: '取消',
      buttonPositive: '允许',
    }
  );
  return granted === PermissionsAndroid.RESULTS.GRANTED;
}
```

### 代码混淆

```gradle
// Android (build.gradle)
android {
  buildTypes {
    release {
      minifyEnabled true
      shrinkResources true
      proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
    }
  }
}
```

## 测试规范

### 单元测试

```dart
// Flutter 单元测试
void main() {
  group('Counter', () {
    test('should increment', () {
      final counter = Counter(0);
      counter.increment();
      expect(counter.value, 1);
    });
  });
}
```

### 集成测试

```typescript
// React Native Detox
describe('Login', () => {
  beforeAll(async () => {
    await device.launchApp();
  });

  it('should login successfully', async () => {
    await element(by.id('email')).typeText('test@example.com');
    await element(by.id('password')).typeText('password');
    await element(by.id('login-button')).tap();
    await expect(element(by.id('home-screen'))).toBeVisible();
  });
});
```

## 调试技巧

```markdown
调试工具：
- Flutter: DevTools, Observatory
- React Native: Flipper, Reactotron
- UniApp: 内置调试器, HBuilderX 调试

常见问题排查：
- 白屏：检查 JS 错误，查看控制台日志
- 闪退：检查原生崩溃日志（Xcode/Logcat）
- 内存泄漏：使用 Profiler 分析
- 性能问题：使用性能分析工具定位
```

---

_最后更新：2026-04-08_