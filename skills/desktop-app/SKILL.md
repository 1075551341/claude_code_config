---
name: desktop-app
description: 当需要开发桌面应用程序、选择桌面技术栈、实现桌面应用功能时调用此技能。触发词：桌面应用、桌面软件开发、Tauri、Electron、WPF、Qt、桌面GUI、Windows应用、macOS应用、Linux应用。
---

# 桌面应用开发

## 核心能力

**桌面应用技术选型、跨平台开发、系统集成。**

---

## 适用场景

- 桌面应用开发
- 技术栈选型
- 系统集成
- 跨平台适配

---

## 技术栈对比

| 技术 | 语言 | 优势 | 适用场景 |
|------|------|------|----------|
| Electron | JS/TS | Web技术、生态丰富 | 跨平台应用 |
| Tauri | Rust+Web | 性能好、体积小 | 轻量级应用 |
| Qt | C++/Python | 性能优秀、原生体验 | 专业软件 |
| Flutter | Dart | 统一UI、跨平台 | 移动+桌面 |
| WPF | C# | Windows原生 | Windows应用 |
| SwiftUI | Swift | macOS/iOS原生 | 苹果生态 |

---

## Tauri 开发

### 项目创建

```bash
# 创建项目
npm create tauri-app@latest

# 开发
npm run tauri dev

# 构建
npm run tauri build
```

### Rust 后端

```rust
// src-tauri/src/main.rs
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![greet])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

### 前端调用

```typescript
import { invoke } from '@tauri-apps/api/tauri';

const result = await invoke('greet', { name: 'World' });
```

---

## 系统集成

### 文件系统

```javascript
// Electron
const fs = require('fs').promises;
const data = await fs.readFile('path/to/file');

// Tauri
import { readTextFile } from '@tauri-apps/api/fs';
const data = await readTextFile('path/to/file');
```

### 窗口管理

```javascript
// Electron
const { BrowserWindow } = require('electron');
const win = new BrowserWindow({ width: 800, height: 600 });

// Tauri
import { appWindow } from '@tauri-apps/api/window';
await appWindow.setSize({ width: 800, height: 600 });
```

### 系统对话框

```javascript
// Electron
const { dialog } = require('electron');
const result = await dialog.showOpenDialog();

// Tauri
import { open } from '@tauri-apps/api/dialog';
const result = await open({ multiple: true });
```

---

## 自动更新

### Electron

```javascript
const { autoUpdater } = require('electron-updater');

autoUpdater.checkForUpdatesAndNotify();

autoUpdater.on('update-downloaded', () => {
  autoUpdater.quitAndInstall();
});
```

### Tauri

```rust
use tauri::updater::Updater;

let updater = Updater::new(app_handle);
updater.check().await?;
```

---

## 性能优化

### 启动优化

```markdown
1. 延迟加载模块
2. 预加载关键资源
3. 优化启动画面
4. 减少初始化任务
```

### 内存优化

```markdown
1. 及时释放资源
2. 避免内存泄漏
3. 使用对象池
4. 图片懒加载
```

---

## 打包签名

### Windows

```bash
# 代码签名
signcode /spc cert.spc /key key.pvk /t timestamp app.exe

# NSIS安装包
makensis installer.nsi
```

### macOS

```bash
# 签名
codesign --deep --force --verify --verbose --sign "Developer ID" app.app

# 公证
xcrun notarytool submit app.zip --wait
```

---

## 注意事项

```
必须：
- 选择合适技术栈
- 处理跨平台差异
- 实现自动更新
- 签名发布应用

避免：
- 过大安装包
- 阻塞主线程
- 忽略权限请求
- 硬编码路径
```

---

## 相关技能

- `electron-app` - Electron 开发
- `performance-optimization` - 性能优化
- `deploy-script` - 部署脚本