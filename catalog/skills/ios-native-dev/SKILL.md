---
name: ios-native-dev
description: 开发iOS原生应用、使用Swift/Objective-C开发iPhone/iPad应用、实现iOS UI界面
triggers: [iOS开发, iOS原生, Swift开发, Objective-C, iPhone开发, iPad开发, UIKit, SwiftUI, 声明式UI, SwiftUI组件, SwiftUI布局, Xcode, CocoaPods, Swift Package]
---

# iOS 原生开发

## 核心能力

**iOS原生应用开发、Swift编程、SwiftUI/UIKit界面。**

---

## 适用场景

- iOS 原生应用开发
- Swift/Objective-C 编程
- SwiftUI/UIKit 界面开发
- iPhone/iPad 应用

---

## 项目结构

```
MyApp/
├── App/
│   ├── MyAppApp.swift          # App入口
│   ├── ContentView.swift       # 主视图
│   └── Assets.xcassets/        # 资源
├── Models/                     # 数据模型
├── Views/                      # 视图
│   ├── Screens/
│   └── Components/
├── ViewModels/                 # 视图模型
├── Services/                   # 服务层
│   ├── APIService.swift
│   └── DataService.swift
├── Utils/                      # 工具类
├── Info.plist                  # 配置
└── AppDelegate.swift           # 应用代理
```

---

## SwiftUI 基础

### 视图定义

```swift
struct ContentView: View {
    @State private var text = ""
    
    var body: some View {
        VStack {
            Text("Hello, iOS!")
                .font(.title)
                .foregroundColor(.primary)
            
            TextField("输入文字", text: $text)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .padding()
            
            Button("点击") {
                print("Button tapped")
            }
            .buttonStyle(.borderedProminent)
        }
        .padding()
    }
}
```

### 列表

```swift
struct ListView: View {
    let items = ["Item 1", "Item 2", "Item 3"]
    
    var body: some View {
        List(items, id: \.self) { item in
            HStack {
                Image(systemName: "star")
                Text(item)
            }
        }
        .listStyle(.insetGrouped)
    }
}
```

### 导航

```swift
struct NavigationView: View {
    var body: some View {
        NavigationStack {
            List {
                NavigationLink("详情页") {
                    DetailView()
                }
            }
            .navigationTitle("首页")
            .navigationBarTitleDisplayMode(.large)
        }
    }
}
```

---

## 状态管理

### @State

```swift
@State private var count = 0

Button("Count: \(count)") {
    count += 1
}
```

### @ObservedObject / @StateObject

```swift
class ViewModel: ObservableObject {
    @Published var data: [String] = []
    
    func loadData() {
        // 加载数据
    }
}

struct MyView: View {
    @StateObject private var viewModel = ViewModel()
    
    var body: some View {
        List(viewModel.data, id: \.self) { item in
            Text(item)
        }
        .onAppear {
            viewModel.loadData()
        }
    }
}
```

### @EnvironmentObject

```swift
// 定义
class AppState: ObservableObject {
    @Published var isLoggedIn = false
}

// 注入
@main
struct MyApp: App {
    @StateObject var appState = AppState()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
        }
    }
}

// 使用
struct MyView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        Text(appState.isLoggedIn ? "已登录" : "未登录")
    }
}
```

---

## 网络请求

### URLSession

```swift
func fetchData() async throws -> [User] {
    let url = URL(string: "https://api.example.com/users")!
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode([User].self, from: data)
}

// 使用
Task {
    do {
        let users = try await fetchData()
        await MainActor.run {
            self.users = users
        }
    } catch {
        print("Error: \(error)")
    }
}
```

### Combine

```swift
import Combine

class ViewModel: ObservableObject {
    @Published var users: [User] = []
    private var cancellables = Set<AnyCancellable>()
    
    func loadUsers() {
        URLSession.shared.dataTaskPublisher(for: URL(string: "https://api.example.com/users")!)
            .map(\.data)
            .decode(type: [User].self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { _ in },
                receiveValue: { [weak self] users in
                    self?.users = users
                }
            )
            .store(in: &cancellables)
    }
}
```

---

## 数据持久化

### UserDefaults

```swift
// 存储
UserDefaults.standard.set("value", forKey: "key")

// 读取
let value = UserDefaults.standard.string(forKey: "key")
```

### SwiftData

```swift
@Model
class User {
    var id: UUID
    var name: String
    var createdAt: Date
    
    init(name: String) {
        self.id = UUID()
        self.name = name
        self.createdAt = Date()
    }
}

// 使用
struct ContentView: View {
    @Environment(\.modelContext) private var context
    
    var body: some View {
        List {
            ForEach(users) { user in
                Text(user.name)
            }
        }
    }
}
```

---

## CocoaPods 配置

```ruby
# Podfile
platform :ios, '15.0'
use_frameworks!

target 'MyApp' do
  pod 'Alamofire', '~> 5.8'
  pod 'Kingfisher', '~> 7.10'
  pod 'SnapKit', '~> 5.6'
end
```

---

## 常用命令

```bash
# 构建
xcodebuild -scheme MyApp -configuration Debug build

# 测试
xcodebuild test -scheme MyApp -destination 'platform=iOS Simulator,name=iPhone 15'

# 归档
xcodebuild archive -scheme MyApp -archivePath build/MyApp.xcarchive

# 导出IPA
xcodebuild -exportArchive -archivePath build/MyApp.xcarchive -exportPath build/ipa -exportOptionsPlist ExportOptions.plist

# CocoaPods
pod install
pod update
```

---

## 注意事项

```
必须:
- 使用SwiftUI优先
- 遵循Human Interface Guidelines
- 适配不同设备尺寸
- 处理深色模式

避免:
- 主线程网络请求
- 强引用循环
- 硬编码字符串
- 忽略内存警告
```

---

## 相关技能

- `swift-ui` - SwiftUI开发
- `ios-simulator` - iOS模拟器
- `mobile-deployment` - 应用发布
