---
name: ios-simulator
description: 当需要测试iOS应用、使用iOS模拟器、调试iOS界面、测试iPhone/iPad应用时调用此技能。触发词：iOS模拟器、iPhone模拟器、iPad模拟器、iOS测试、Xcode模拟器、Simulator、iOS调试。
---

# iOS 模拟器操作

## 核心能力

**iOS模拟器控制、应用测试、界面调试。**

---

## 适用场景

- iOS 应用测试
- 模拟器控制
- 界面调试
- 设备模拟

---

## 基本命令

### 启动模拟器

```bash
# 列出可用设备
xcrun simctl list devices

# 启动模拟器
open -a Simulator

# 启动指定设备
xcrun simctl boot "iPhone 15 Pro"
```

### 应用管理

```bash
# 安装应用
xcrun simctl install booted /path/to/App.app

# 启动应用
xcrun simctl launch booted com.example.app

# 终止应用
xcrun simctl terminate booted com.example.app

# 卸载应用
xcrun simctl uninstall booted com.example.app
```

---

## 设备控制

### 屏幕操作

```bash
# 截图
xcrun simctl io booted screenshot screenshot.png

# 录屏
xcrun simctl io booted recordVideo video.mov

# 设置状态栏
xcrun simctl status_bar booted override --time "12:00" --dataNetwork wifi --wifiMode active
```

### 位置模拟

```bash
# 设置位置
xcrun simctl location booted set 37.7749,-122.4194
```

### 推送通知

```bash
# 发送推送通知
xcrun simctl push booted com.example.app notification.json
```

---

## 设备配置

### 设备类型

```bash
# 创建新设备
xcrun simctl create "My iPhone" "iPhone 15 Pro" iOS17.0

# 删除设备
xcrun simctl delete <device-id>

# 重置设备
xcrun simctl erase <device-id>
```

### 环境设置

```bash
# 设置外观
xcrun simctl ui booted appearance dark

# 设置语言
xcrun simctl ui booted locale zh_CN
```

---

## 常用操作

### 清理重置

```bash
# 关闭所有模拟器
xcrun simctl shutdown all

# 重置所有内容和设置
xcrun simctl erase all

# 清理不可用设备
xcrun simctl delete unavailable
```

### 日志查看

```bash
# 实时日志
xcrun simctl spawn booted log stream

# 过滤日志
xcrun simctl spawn booted log stream --predicate 'process == "myapp"'
```

---

## 快捷键

| 操作 | 快捷键 |
|------|--------|
| 切换设备 | Cmd + Shift + K |
| 截图 | Cmd + S |
| 录屏 | Cmd + R |
| 旋转 | Cmd + 左/右箭头 |
| 缩放 | Cmd + 1/2/3 |
| Shake | Cmd + Ctrl + Z |

---

## 测试场景

### 网络条件

```bash
# 网络状态
xcrun simctl status_bar booted override --dataNetwork 3g

# 或通过 Network Link Conditioner
```

### 内存警告

```bash
# 触发内存警告
xcrun simctl simulate_memory_warning booted
```

### 权限测试

```
Settings > Privacy & Security
- 相机权限
- 相册权限
- 位置权限
- 通知权限
```

---

## 调试技巧

### Safari 开发工具

```
1. Safari > 开发 > 模拟器
2. 选择要调试的页面
3. 使用 Web Inspector 调试
```

### 控制台输出

```bash
# 实时控制台
xcrun simctl spawn booted log stream --level debug
```

---

## 注意事项

```
必须：
- 定期清理旧设备
- 验证真机表现
- 测试多种设备尺寸

避免：
- 只测试模拟器
- 忽略性能差异
- 不清理缓存数据
```

---

## 相关技能

- `web-testing` - Web 测试
- `uniapp-development` - UniApp 开发
- `mobile-developer` agent - 移动端开发