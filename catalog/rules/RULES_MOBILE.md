---
description: 移动端开发规则（Flutter/RN/UniApp/原生）
alwaysApply: false
globs: ["*.dart", "pubspec.yaml", "*.rn.*", "uniapp.json", "*.swift", "*.kt", "*.xcodeproj", "AndroidManifest.xml"]
---

# 移动端开发规则

## 技术选型

```
跨平台应用  → Flutter / React Native / UniApp
iOS 原生    → Swift / SwiftUI
Android 原生 → Kotlin / Jetpack Compose
小程序      → UniApp / Taro / 原生小程序
```

## Flutter 开发规范

> Flutter/Dart 语言规范详见 `RULES_DART.md`

```
lib/
├── main.dart              # 应用入口
├── app/                   # 应用级配置
├── features/              # 功能模块（data/domain/presentation）
├── core/                  # 核心功能（theme/constants/utils）
└── shared/                # 共享组件（widgets/models）
```

## React Native 开发规范

```
src/
├── App.tsx        # 应用入口
├── navigation/    # 导航配置
├── screens/       # 页面组件
├── components/    # 共享组件
├── hooks/         # 自定义 Hooks
├── services/      # API 服务
├── store/         # 状态管理
└── types/         # TypeScript 类型
```

性能优化：memo + useCallback + FlatList（removeClippedSubviews, maxToRenderPerBatch, windowSize）

## UniApp 开发规范

```vue
<!-- 条件编译 -->
<!-- #ifdef MP-WEIXIN --><button open-type="getPhoneNumber">微信授权</button><!-- #endif -->
<!-- #ifdef APP-PLUS --><button @click="nativeLogin">原生登录</button><!-- #endif -->
```

## 性能优化

```
启动：懒加载非关键组件 + 预加载关键图片 + 动态 import
内存：及时清理订阅/监听 + 图片适当分辨率
包体积：WebP格式 + ProGuard/R8 + 移除未使用依赖 + 按dpi分层
```

## 发布流程

```
iOS：代码审查→更新版本号→构建Archive→上传App Store Connect→提交审核
  注意：隐私政策URL有效 + 权限说明完整 + 内购必须IAP + 不允许热更原生代码
Android：代码审查→更新版本号→签名打包(AAB)→上传Google Play→提交审核
  注意：目标API级别合规 + 权限声明合规 + 64位支持
小程序：代码审查→更新版本号→上传代码→提交审核
  注意：用户隐私合规 + 内容安全审查 + 虚拟支付限制(iOS)
```

## 安全规范

```typescript
await SecureStorage.setItem('token', token);  // 敏感数据加密存储（不用 AsyncStorage 明文存 token）
const agent = new https.Agent({ ca: fs.readFileSync('./cert.pem') });  // SSL Pinning
const granted = await PermissionsAndroid.request(PermissionsAndroid.PERMISSIONS.CAMERA);  // 动态权限
```

## 调试

```
Flutter: DevTools | React Native: Flipper/Reactotron | UniApp: 内置调试器
白屏→查JS错误 | 闪退→查原生崩溃日志 | 内存泄漏→Profiler | 性能→性能分析工具
```
