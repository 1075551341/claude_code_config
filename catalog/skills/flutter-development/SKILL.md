---
name: flutter-development
description: 开发Flutter跨平台移动应用、编写Dart代码、实现iOS/Android双端应用
triggers: [Flutter, Flutter开发, Dart, 移动应用, 跨平台开发, Flutter UI, Widget, iOS Android双端]
---

# Flutter 跨平台开发

## 核心能力

**Flutter应用开发、Widget构建、状态管理、跨平台适配。**

---

## 适用场景

- Flutter 应用开发
- iOS/Android 双端开发
- Widget 组件开发
- 状态管理实现

---

## 项目结构

```
lib/
├── main.dart           # 应用入口
├── app.dart            # App配置
├── screens/            # 页面
│   ├── home/
│   │   ├── home_screen.dart
│   │   └── home_controller.dart
├── widgets/            # 通用组件
│   ├── buttons/
│   └── cards/
├── models/             # 数据模型
├── services/           # 服务层
│   ├── api_service.dart
│   └── storage_service.dart
├── providers/          # 状态管理
└── utils/              # 工具函数
```

---

## 常用Widget

### 基础布局

```dart
// 容器
Container(
  padding: EdgeInsets.all(16),
  decoration: BoxDecoration(
    color: Colors.white,
    borderRadius: BorderRadius.circular(8),
  ),
  child: Text('内容'),
)

// 行/列布局
Row(
  mainAxisAlignment: MainAxisAlignment.spaceBetween,
  children: [Widget1(), Widget2()],
)

Column(
  children: [Widget1(), Widget2()],
)

// 列表
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) => ListTile(
    title: Text(items[index]),
  ),
)
```

### 常用组件

```dart
// 文本
Text('Hello', style: TextStyle(fontSize: 16))

// 按钮
ElevatedButton(
  onPressed: () {},
  child: Text('按钮'),
)

// 输入框
TextField(
  decoration: InputDecoration(
    labelText: '用户名',
    border: OutlineInputBorder(),
  ),
  onChanged: (value) {},
)

// 图片
Image.network('url')
Image.asset('assets/image.png')
```

---

## 状态管理

### Provider

```dart
// 定义
class Counter extends ChangeNotifier {
  int _count = 0;
  int get count => _count;
  
  void increment() {
    _count++;
    notifyListeners();
  }
}

// 使用
Consumer<Counter>(
  builder: (context, counter, child) {
    return Text('${counter.count}');
  },
)
```

### Riverpod

```dart
// 定义
final counterProvider = StateProvider<int>((ref) => 0);

// 使用
class MyWidget extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final count = ref.watch(counterProvider);
    return Text('$count');
  }
}
```

---

## 网络请求

### Dio

```dart
import 'package:dio/dio.dart';

final dio = Dio();

// GET
final response = await dio.get('https://api.example.com/data');

// POST
final response = await dio.post(
  'https://api.example.com/data',
  data: {'key': 'value'},
);
```

---

## 本地存储

### SharedPreferences

```dart
final prefs = await SharedPreferences.getInstance();

// 存储
await prefs.setString('token', 'xxx');
await prefs.setInt('count', 10);

// 读取
final token = prefs.getString('token');
final count = prefs.getInt('count');
```

### Hive

```dart
var box = await Hive.openBox('myBox');

// 存储
await box.put('key', 'value');

// 读取
final value = box.get('key');
```

---

## 导航路由

```dart
// 跳转
Navigator.push(
  context,
  MaterialPageRoute(builder: (context) => DetailScreen()),
);

// 返回
Navigator.pop(context);

// 命名路由
Navigator.pushNamed(context, '/detail');
```

---

## 常用命令

```bash
# 创建项目
flutter create my_app

# 运行
flutter run

# 构建
flutter build apk      # Android
flutter build ios      # iOS

# 清理
flutter clean

# 依赖
flutter pub get
flutter pub upgrade
```

---

## 注意事项

```
必须：
- 区分StatelessWidget和StatefulWidget
- 使用const优化性能
- 处理异步操作
- 适配不同屏幕尺寸

避免：
- 过深嵌套
- 忽略生命周期
- 硬编码颜色/尺寸
- 阻塞主线程
```

---

## 相关技能

- `react-native` - React Native 开发
- `uniapp-development` - UniApp 开发
- `mobile-developer` agent - 移动端开发
