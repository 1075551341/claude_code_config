---
name: electron-app
description: 当需要开发Electron桌面应用、使用Web技术开发桌面软件、Windows/macOS/Linux跨平台桌面应用时调用此技能。触发词：Electron、桌面应用、桌面软件开发、Electron开发、跨平台桌面、Windows应用、macOS应用。
---

# Electron 桌面应用开发

## 核心能力

**Electron桌面应用开发、主进程与渲染进程、原生API集成。**

---

## 适用场景

- 桌面应用开发
- 跨平台桌面软件
- 原生API集成
- 系统托盘应用

---

## 项目结构

```
electron-app/
├── package.json
├── main.js              # 主进程
├── preload.js           # 预加载脚本
├── src/                 # 渲染进程
│   ├── index.html
│   ├── renderer.js
│   └── styles.css
└── build/               # 打包配置
```

---

## 主进程

```javascript
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  mainWindow.loadFile('src/index.html');
  
  // 开发模式打开DevTools
  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools();
  }
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
```

---

## IPC 通信

### 预加载脚本

```javascript
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  send: (channel, data) => ipcRenderer.send(channel, data),
  receive: (channel, callback) => {
    ipcRenderer.on(channel, (event, ...args) => callback(...args));
  },
  invoke: (channel, data) => ipcRenderer.invoke(channel, data),
});
```

### 主进程处理

```javascript
// 同步消息
ipcMain.on('message', (event, data) => {
  event.reply('reply', '收到: ' + data);
});

// 异步消息
ipcMain.handle('async-message', async (event, data) => {
  const result = await processData(data);
  return result;
});
```

### 渲染进程调用

```javascript
// 发送消息
window.electronAPI.send('message', 'Hello');

// 接收消息
window.electronAPI.receive('reply', (data) => {
  console.log(data);
});

// 调用异步方法
const result = await window.electronAPI.invoke('async-message', data);
```

---

## 原生功能

### 系统托盘

```javascript
const { Tray, Menu, nativeImage } = require('electron');

const tray = new Tray(nativeImage.createFromPath('icon.png'));

const contextMenu = Menu.buildFromTemplate([
  { label: '显示窗口', click: () => mainWindow.show() },
  { label: '退出', click: () => app.quit() },
]);

tray.setContextMenu(contextMenu);
```

### 文件对话框

```javascript
const { dialog } = require('electron');

// 打开文件
const result = await dialog.showOpenDialog({
  properties: ['openFile', 'multiSelections'],
  filters: [{ name: 'Images', extensions: ['jpg', 'png'] }],
});

// 保存文件
const result = await dialog.showSaveDialog({
  defaultPath: 'untitled.txt',
});
```

### 通知

```javascript
const { Notification } = require('electron');

new Notification({
  title: '标题',
  body: '内容',
}).show();
```

---

## 打包发布

### electron-builder

```json
{
  "build": {
    "appId": "com.example.app",
    "productName": "MyApp",
    "mac": {
      "target": "dmg",
      "category": "public.app-category.utilities"
    },
    "win": {
      "target": "nsis"
    },
    "linux": {
      "target": "AppImage"
    }
  }
}
```

```bash
# 构建
npm run build

# 打包
npx electron-builder --mac
npx electron-builder --win
npx electron-builder --linux
```

---

## 常用命令

```bash
# 安装
npm install electron --save-dev

# 运行
npx electron .

# 开发热重载
npx electron . --reload
```

---

## 注意事项

```
必须：
- 启用contextIsolation
- 使用preload脚本
- 验证IPC消息
- 签名发布应用

避免：
- 直接暴露Node API
- 硬编码路径
- 阻塞主进程
- 忽略平台差异
```

---

## 相关技能

- `desktop-app` - 桌面应用通用
- `nodejs-backend` - Node.js 后端
- `frontend-design` - 前端设计