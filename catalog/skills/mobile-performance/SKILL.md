---
name: mobile-performance
description: 优化移动端应用性能
triggers: [优化移动端应用性能, 减少包体积, 优化启动速度, 降低内存占用]
---

# 移动端性能优化

## 核心能力

**包体积优化、启动加速、内存管理、流畅度提升。**

---

## 适用场景

- 包体积优化
- 启动速度优化
- 内存占用优化
- 滑动卡顿解决

---

## 包体积优化

### 资源压缩

```markdown
1. 图片压缩
   - WebP格式替代PNG/JPG
   - 使用tinypng/pngquant压缩
   - 按需加载不同分辨率

2. 代码压缩
   - Tree Shaking
   - 代码混淆
   - 压缩工具 (terser/uglify)

3. 资源清理
   - 删除无用图片
   - 清理废弃代码
   - 合并重复资源
```

### 分析工具

```bash
# Android
./gradlew assembleRelease --analyze

# iOS
# Xcode → Product → Archive → Distribute → Size Report

# Web/混合应用
npx source-map-explorer dist/*.js
```

### Android 包体积

```groovy
// build.gradle
android {
    buildTypes {
        release {
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }
    }
    
    // 分包
    packagingOptions {
        exclude 'META-INF/*.kotlin_module'
    }
}
```

### iOS 包体积

```
1. Strip Debug Symbols
2. Remove unused code
3. Compress PNG files
4. Use asset catalogs
5. Optimize images
```

---

## 启动优化

### 冷启动流程

```
App启动 → 进程创建 → Application初始化 → Activity创建
→ UI渲染 → 用户可交互
```

### Android 启动优化

```kotlin
// 延迟初始化
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        
        // 必要的同步初始化
        
        // 非必要异步初始化
        GlobalScope.launch {
            initAnalytics()
            initCrashlytics()
        }
        
        // 或使用启动器
        AppInitializer.getInstance(this)
            .initializeComponent(AnalyticsInitializer::class.java)
    }
}

// 使用Startup库
class AnalyticsInitializer : Initializer<Unit> {
    override fun create(context: Context) {
        // 初始化代码
    }
    
    override fun dependencies(): List<Class<out Initializer<*>>> {
        return emptyList()
    }
}
```

### iOS 启动优化

```swift
// AppDelegate
func application(_ application: UIApplication, 
                 didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    
    // 关键初始化
    
    // 延迟非关键任务
    DispatchQueue.global().async {
        self.setupAnalytics()
        self.setupCrashReporting()
    }
    
    return true
}

// 使用后台任务
func beginBackgroundTask()
func endBackgroundTask(_ identifier: UIBackgroundTaskIdentifier)
```

### 首屏优化

```markdown
1. 骨架屏
   - 立即显示占位UI
   - 减少用户等待感

2. 预加载
   - 提前加载关键数据
   - 缓存首页内容

3. 懒加载
   - 非首屏内容延迟加载
   - 分块渲染
```

---

## 内存优化

### 内存泄漏检测

```markdown
Android:
- LeakCanary
- Android Profiler

iOS:
- Instruments (Leaks, Allocations)
- Xcode Memory Graph

Web/Hybrid:
- Chrome DevTools Memory
- heap snapshot
```

### 常见内存问题

```markdown
1. 图片内存
   - 按需加载尺寸
   - 及时回收bitmap
   - 使用缓存策略

2. 列表优化
   - ViewHolder复用
   - 图片复用
   - 分页加载

3. 单例持有
   - 避免Context泄露
   - 使用WeakReference
```

### Android 内存优化

```kotlin
// 图片加载配置
Glide.with(context)
    .load(url)
    .override(targetWidth, targetHeight)
    .into(imageView)

// Bitmap复用
val options = BitmapFactory.Options()
options.inBitmap = reusableBitmap
options.inSampleSize = calculateInSampleSize()

// 及时回收
override fun onDestroy() {
    binding.unbind()
    compositeDisposable.clear()
}
```

### iOS 内存优化

```swift
// 图片内存
let image = UIImage(contentsOfFile: path)  // 不缓存
let image = UIImage(named: "image")        // 系统缓存

// 及时释放
deinit {
    // 清理资源
}

// 内存警告处理
override func didReceiveMemoryWarning() {
    super.didReceiveMemoryWarning()
    // 释放可重建的资源
}
```

---

## 滑动优化

### 列表优化

```kotlin
// Android RecyclerView
class MyAdapter : RecyclerView.Adapter<MyViewHolder>() {
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): MyViewHolder {
        // 使用ViewHolder
    }
    
    override fun onBindViewHolder(holder: MyViewHolder, position: Int) {
        // 避免复杂计算
        // 使用DiffUtil
    }
}

// 使用DiffUtil
val diffResult = DiffUtil.calculateDiff(MyDiffCallback(oldList, newList))
adapter.submitList(newList)
diffResult.dispatchUpdatesTo(adapter)
```

### iOS 列表

```swift
// UITableView优化
func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
    let cell = tableView.dequeueReusableCell(withIdentifier: "Cell", for: indexPath)
    // 快速绑定数据
    return cell
}

// 预计算高度
func tableView(_ tableView: UITableView, estimatedHeightForRowAt indexPath: IndexPath) -> CGFloat {
    return cachedHeights[indexPath] ?? 44
}
```

### Web滚动优化

```javascript
// 虚拟列表
import { VirtualList } from 'react-window'

const Row = ({ index, style }) => (
  <div style={style}>Row {index}</div>
)

<VirtualList
  height={600}
  itemCount={10000}
  itemSize={50}
  width="100%"
>
  {Row}
</VirtualList>

// 防抖节流
const handleScroll = throttle(() => {
  // 滚动处理
}, 100)
```

---

## 性能监控

### 指标监控

```markdown
关键指标:
- 冷启动时间 < 3秒
- 热启动时间 < 1秒
- 页面切换 < 300ms
- 列表滚动 FPS > 55
- 内存峰值 < 150MB
- 包体积 < 50MB
```

### 监控工具

| 平台 | 工具 |
|------|------|
| Android | Android Profiler, Perfetto |
| iOS | Instruments, MetricKit |
| Flutter | DevTools, Firebase Performance |
| React Native | Flipper, Hermes |
| Web | Lighthouse, WebPageTest |

---

## 注意事项

```
必须:
- 定期监控性能指标
- 测试低端设备
- 关注内存使用
- 分析启动时间

避免:
- 过度优化
- 忽略低端设备
- 频繁GC
- 主线程阻塞
```

---

## 相关技能

- `performance-optimization` - 通用性能优化
- `mobile-deployment` - 应用发布
- `react-native` - React Native开发