---
name: mobile-deployment
description: 当需要发布移动应用、上架应用商店、配置应用签名、实现应用更新时调用此技能。触发词：应用发布、App发布、应用商店、上架App Store、上架Google Play、应用签名、OTA更新、热更新。
---

# 移动应用发布

## 核心能力

**应用签名配置、应用商店上架、OTA热更新。**

---

## 适用场景

- 应用签名配置
- 应用商店上架
- OTA 热更新
- 版本更新管理

---

## Android 发布

### 签名配置

```groovy
// build.gradle
android {
    signingConfigs {
        release {
            storeFile file('release.keystore')
            storePassword 'password'
            keyAlias 'alias'
            keyPassword 'password'
        }
    }
    
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }
    }
}
```

### 生成签名文件

```bash
# 创建keystore
keytool -genkey -v -keystore release.keystore \
  -alias my-alias \
  -keyalg RSA -keysize 2048 -validity 10000

# 查看签名信息
keytool -list -v -keystore release.keystore

# 签名APK
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 \
  -keystore release.keystore app-release-unsigned.apk my-alias

# 或使用apksigner
apksigner sign --ks release.keystore --out app-release.apk app-release-unsigned.apk
```

### 构建发布版本

```bash
# Gradle构建
./gradlew assembleRelease

# 或使用bundle (推荐)
./gradlew bundleRelease

# 输出位置
# APK: app/build/outputs/apk/release/
# AAB: app/build/outputs/bundle/release/
```

### Google Play 上架

```markdown
1. 创建开发者账号 ($25一次性费用)
2. 创建应用
3. 填写商店信息:
   - 应用名称、描述
   - 图标、截图
   - 分类、内容评级
4. 上传AAB文件
5. 设置定价和分发
6. 提交审核 (通常1-3天)
```

### 国内应用商店

```markdown
主流商店:
- 华为应用市场
- 小米应用商店
- OPPO软件商店
- vivo应用商店
- 应用宝(腾讯)
- 百度手机助手

注意事项:
- 需要软件著作权
- 部分需要ICP备案
- 首次上架审核较严
```

---

## iOS 发布

### 证书配置

```markdown
1. Apple开发者账号 ($99/年)
2. 创建证书:
   - Development证书
   - Distribution证书
3. 创建App ID
4. 创建Provisioning Profile
5. 配置Xcode
```

### Xcode 配置

```xml
<!-- Info.plist -->
<key>CFBundleIdentifier</key>
<string>com.example.app</string>
<key>CFBundleVersion</key>
<string>1</string>
<key>CFBundleShortVersionString</key>
<string>1.0.0</string>
```

### 构建发布

```bash
# 命令行构建
xcodebuild -workspace MyApp.xcworkspace \
  -scheme MyApp \
  -configuration Release \
  -archivePath build/MyApp.xcarchive \
  archive

# 导出IPA
xcodebuild -exportArchive \
  -archivePath build/MyApp.xcarchive \
  -exportPath build/ipa \
  -exportOptionsPlist ExportOptions.plist
```

### App Store 上架

```markdown
1. 在App Store Connect创建应用
2. 填写应用信息:
   - 名称、描述
   - 关键词、分类
   - 图标、截图
   - 隐私政策URL
3. 上传构建版本
   - Xcode → Product → Archive → Distribute
   - 或使用Transporter应用
4. 提交审核 (通常1-3天)
5. 审核通过后发布
```

---

## 热更新

### React Native CodePush

```bash
# 安装
npm install react-native-code-push

# 配置
code-push app add MyApp-Android android react-native
code-push app add MyApp-iOS ios react-native

# 发布更新
code-push release-react MyApp-Android android
code-push release-react MyApp-iOS ios

# 强制更新
code-push release-react MyApp-Android android --mandatory
```

### Flutter OTA

```yaml
# 使用 shorebird
# 安装
flutter pub global activate shorebird_cli

# 初始化
shorebird init

# 发布
shorebird release android
shorebird release ios

# 补丁发布
shorebird patch android 1.0.0+1
```

### 原生应用更新

```kotlin
// Android 应用内更新
val appUpdateManager = AppUpdateManagerFactory.create(context)

val appUpdateInfo = appUpdateManager.appUpdateInfo.await()

if (appUpdateInfo.updateAvailability() == UpdateAvailability.UPDATE_AVAILABLE) {
    appUpdateManager.startUpdateFlowForResult(
        appUpdateInfo,
        AppUpdateType.FLEXIBLE,
        this,
        UPDATE_REQUEST_CODE
    )
}
```

---

## 版本管理

### 版本号规则

```
版本号: Major.Minor.Patch
例: 1.2.3

Major: 重大更新/不兼容变更
Minor: 新功能/向后兼容
Patch: Bug修复

Build号: 递增整数，每次构建+1
```

### 更新检查

```javascript
// 版本比较
function compareVersion(v1, v2) {
  const parts1 = v1.split('.').map(Number)
  const parts2 = v2.split('.').map(Number)
  
  for (let i = 0; i < 3; i++) {
    if (parts1[i] > parts2[i]) return 1
    if (parts1[i] < parts2[i]) return -1
  }
  return 0
}

// 检查更新
async function checkUpdate() {
  const response = await fetch('/api/version')
  const { latestVersion, forceUpdate } = await response.json()
  
  if (compareVersion(latestVersion, currentVersion) > 0) {
    showUpdateDialog(forceUpdate)
  }
}
```

---

## 注意事项

```
必须:
- 备份签名文件
- 测试发布版本
- 准备审核材料
- 遵守平台规范

避免:
- 丢失签名密钥
- 频繁提交审核
- 违反平台政策
- 无更新说明
```

---

## 相关技能

- `android-development` - Android开发
- `ios-native-dev` - iOS开发
- `mobile-performance` - 性能优化