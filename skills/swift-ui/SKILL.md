---
name: swift-ui
description: 当需要使用SwiftUI开发iOS界面、编写声明式SwiftUI代码、实现iOS原生UI时调用此技能。触发词：SwiftUI、SwiftUI开发、声明式UI、Swift UI、iOS UI、SwiftUI组件、SwiftUI布局。
---

# SwiftUI 开发

## 核心能力

**SwiftUI声明式UI、组件开发、状态管理。**

---

## 适用场景

- SwiftUI 界面开发
- iOS/macOS 原生UI
- 声明式UI编写
- 状态管理

---

## 基础视图

### 文本与图片

```swift
// 文本
Text("Hello, SwiftUI!")
    .font(.title)
    .foregroundColor(.blue)
    .multilineTextAlignment(.center)

// 图片
Image("photo")
    .resizable()
    .aspectRatio(contentMode: .fill)
    .frame(width: 100, height: 100)
    .clipShape(Circle())

// SF Symbols
Image(systemName: "star.fill")
    .foregroundColor(.yellow)
```

### 布局容器

```swift
// VStack - 垂直
VStack(alignment: .leading, spacing: 10) {
    Text("Title")
    Text("Subtitle")
}

// HStack - 水平
HStack {
    Text("Left")
    Spacer()
    Text("Right")
}

// ZStack - 叠加
ZStack {
    Image("background")
    Text("Overlay")
}

// Grid (iOS 16+)
Grid {
    GridRow {
        Text("1,1")
        Text("1,2")
    }
    GridRow {
        Text("2,1")
        Text("2,2")
    }
}
```

---

## 常用控件

### 按钮

```swift
// 基础按钮
Button("点击") {
    print("tapped")
}

// 自定义按钮
Button(action: {
    // 动作
}) {
    HStack {
        Image(systemName: "play")
        Text("播放")
    }
}
.buttonStyle(.borderedProminent)

// 图片按钮
Button {
    // 动作
} label: {
    Image(systemName: "plus")
}
```

### 输入控件

```swift
// 文本框
@State private var text = ""

TextField("输入文字", text: $text)
    .textFieldStyle(.roundedBorder)
    .padding()

SecureField("密码", text: $password)

// 开关
@State private var isOn = true

Toggle("开关", isOn: $isOn)

// 滑块
@State private var value = 0.0

Slider(value: $value, in: 0...100)

// 选择器
@State private var selection = 0

Picker("选项", selection: $selection) {
    Text("选项1").tag(0)
    Text("选项2").tag(1)
}
.pickerStyle(.segmented)
```

---

## 列表与导航

### 列表

```swift
// 基础列表
List {
    Text("项目1")
    Text("项目2")
}

// 动态列表
struct Item: Identifiable {
    let id = UUID()
    let name: String
}

List(items) { item in
    Text(item.name)
}

// 分组列表
List {
    Section("水果") {
        Text("苹果")
        Text("香蕉")
    }
    Section("蔬菜") {
        Text("胡萝卜")
    }
}

// 编辑列表
List {
    ForEach(items) { item in
        Text(item.name)
    }
    .onDelete { indexSet in
        items.remove(atOffsets: indexSet)
    }
    .onMove { indices, newOffset in
        items.move(fromOffsets: indices, toOffset: newOffset)
    }
}
```

### 导航

```swift
// NavigationStack (iOS 16+)
NavigationStack {
    List {
        NavigationLink("详情") {
            DetailView()
        }
    }
    .navigationTitle("首页")
}

// 带数据传递
NavigationLink(value: item) {
    Text(item.name)
}
.navigationDestination(for: Item.self) { item in
    DetailView(item: item)
}

// Sheet弹出
@State private var showSheet = false

Button("弹出") {
    showSheet = true
}
.sheet(isPresented: $showSheet) {
    SheetView()
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

### @Binding

```swift
struct ChildView: View {
    @Binding var value: Int
    
    var body: some View {
        Button("Add") {
            value += 1
        }
    }
}

// 使用
ChildView(value: $count)
```

### @Observable (iOS 17+)

```swift
@Observable
class ViewModel {
    var count = 0
    var items: [Item] = []
    
    func increment() {
        count += 1
    }
}

struct ContentView: View {
    @State private var viewModel = ViewModel()
    
    var body: some View {
        Text("Count: \(viewModel.count)")
        Button("Add") {
            viewModel.increment()
        }
    }
}
```

### @EnvironmentObject

```swift
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

## 动画

### 基础动画

```swift
@State private var scale = 1.0

Button("动画") {
    withAnimation(.spring()) {
        scale = 2.0
    }
}
.scaleEffect(scale)

// 隐式动画
Circle()
    .frame(width: isLarge ? 200 : 100)
    .animation(.easeInOut, value: isLarge)
```

### 过渡动画

```swift
if showDetail {
    DetailView()
        .transition(.slide)
        .animation(.default, value: showDetail)
}
```

---

## 自定义视图修饰符

```swift
extension View {
    func cardStyle() -> some View {
        self
            .padding()
            .background(Color.white)
            .cornerRadius(10)
            .shadow(radius: 5)
    }
}

// 使用
Text("内容")
    .cardStyle()
```

---

## 注意事项

```
必须:
- 使用@State管理本地状态
- 遵循单一数据源原则
- 使用预览加速开发
- 适配不同设备尺寸

避免:
- 过深嵌套视图
- 不必要的状态
- 忽略性能问题
- 硬编码尺寸
```

---

## 相关技能

- `ios-native-dev` - iOS原生开发
- `mobile-ui` - 移动端UI
- `swift-language` - Swift语言