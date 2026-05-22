---
description: Dart / Flutter 开发规则
globs: ["*.dart", "pubspec.yaml"]
---

# Dart / Flutter 开发规则

## 空安全

- 启用 Sound Null Safety
- `!` 操作符需注释非空保证
- `late` 仅用于确定会初始化的字段
- 优先用 `?.` / `??` / `?.[]` 处理可空值
- 集合用 `List<T>?` 而非 `List<T?>`

## Widget 设计

- StatelessWidget 优先，状态提升到最近公共祖先
- const 构造函数尽可能标记
- 列表项必须提供 Key
- 单一职责：每个 Widget 做一件事
- 拆分 > 200 行的 Widget

## 状态管理

- Provider（简单）/ Riverpod（推荐）/ BLoC（复杂）
- 精确订阅：Selector 优于 Consumer 优于 watch 整个对象
- 避免全局状态过度刷新
- 异步状态：loading / error / data 三态处理

## 异步

- await 必须在 async 函数内
- Stream 订阅必须取消（StreamSubscription.dispose）
- FutureBuilder 的 ConnectionState 处理
- 避免在 build 中创建 Future（缓存到字段）

## 性能

- ListView.builder 替代 Column+map（长列表）
- RepaintBoundary 隔离重绘区域
- const Widget 减少重建
- 图片用 cached_network_image + 适当分辨率
- 避免在 build 中做耗时计算

## 测试

- Widget 测试：finders + matchers + actions
- 单元测试：纯逻辑用 test()，Widget 用 testWidgets()
- Mock：mockito 代码生成
- Golden 测试：跨平台字体处理
