---
name: websocket-server
description: WebSocket 服务端开发与实时通信
triggers: [WebSocket 服务端开发与实时通信]
---

# WebSocket 服务端

## 核心功能

```
🔌 连接管理 - 建立、心跳、断开
📤 消息推送 - 广播、单播、房间
🔄 重连机制 - 自动重连、状态恢复
📊 状态同步 - 实时数据、在线状态
```

## Node.js + Socket.io

### 服务端配置

```typescript
import { Server } from 'socket.io';

const io = new Server(3000, {
  cors: {
    origin: ['https://example.com'],
    credentials: true,
  },
  pingTimeout: 60000,
  pingInterval: 25000,
});

// 中间件：认证
io.use(async (socket, next) => {
  const token = socket.handshake.auth.token;
  try {
    const user = await verifyToken(token);
    socket.data.user = user;
    next();
  } catch (err) {
    next(new Error('Authentication failed'));
  }
});

// 连接处理
io.on('connection', (socket) => {
  console.log(`User ${socket.data.user.id} connected`);

  // 加入用户专属房间
  socket.join(`user:${socket.data.user.id}`);

  // 处理断开
  socket.on('disconnect', (reason) => {
    console.log(`Disconnected: ${reason}`);
  });
});
```

### 房间管理

```typescript
// 加入房间
io.on('connection', (socket) => {
  socket.on('join-room', async (roomId) => {
    await socket.join(roomId);
    socket.to(roomId).emit('user-joined', {
      userId: socket.data.user.id,
      timestamp: Date.now(),
    });
  });

  socket.on('leave-room', async (roomId) => {
    await socket.leave(roomId);
    socket.to(roomId).emit('user-left', {
      userId: socket.data.user.id,
    });
  });
});

// 广播到房间
io.to('room-123').emit('message', { content: 'Hello!' });

// 排除发送者
socket.to('room-123').emit('message', { content: 'Hello!' });

// 发送给特定用户
io.to('user:123').emit('notification', { message: 'New message' });
```

### 消息处理

```typescript
interface ChatMessage {
  id: string;
  roomId: string;
  senderId: string;
  content: string;
  timestamp: number;
}

io.on('connection', (socket) => {
  socket.on('chat-message', async (data: Omit<ChatMessage, 'id' | 'timestamp'>) => {
    const message: ChatMessage = {
      id: generateId(),
      ...data,
      senderId: socket.data.user.id,
      timestamp: Date.now(),
    };

    // 保存到数据库
    await saveMessage(message);

    // 广播到房间
    io.to(data.roomId).emit('chat-message', message);

    // 发送确认
    socket.emit('chat-message:ack', { id: message.id });
  });
});
```

### 心跳与重连

```typescript
// 服务端心跳配置
const io = new Server({
  pingTimeout: 60000,   // 60秒无响应断开
  pingInterval: 25000,  // 每25秒发送心跳
});

// 客户端重连
import { io } from 'socket.io-client';

const socket = io('ws://localhost:3000', {
  reconnection: true,
  reconnectionAttempts: 10,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 5000,
});

socket.on('reconnect', (attemptNumber) => {
  console.log(`Reconnected after ${attemptNumber} attempts`);
  // 重新订阅
  socket.emit('resubscribe', lastMessageId);
});

socket.on('reconnect_failed', () => {
  console.log('Reconnection failed');
  // 显示离线提示
});
```

## 原生 WebSocket

### 服务端

```typescript
import { WebSocketServer, WebSocket } from 'ws';

const wss = new WebSocketServer({ port: 3000 });

const clients = new Map<string, WebSocket>();

wss.on('connection', (ws, req) => {
  const userId = extractUserId(req);

  clients.set(userId, ws);

  ws.on('message', (data) => {
    const message = JSON.parse(data.toString());

    switch (message.type) {
      case 'chat':
        handleChat(ws, message.payload);
        break;
      case 'ping':
        ws.send(JSON.stringify({ type: 'pong' }));
        break;
    }
  });

  ws.on('close', () => {
    clients.delete(userId);
  });

  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
  });
});

// 广播
function broadcast(message: object) {
  const data = JSON.stringify(message);
  clients.forEach((ws) => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(data);
    }
  });
}
```

### 心跳实现

```typescript
const heartbeatInterval = 30000;

wss.on('connection', (ws) => {
  let isAlive = true;

  const heartbeat = () => {
    if (!isAlive) {
      return ws.terminate();
    }

    isAlive = false;
    ws.ping();
  };

  const interval = setInterval(heartbeat, heartbeatInterval);

  ws.on('pong', () => {
    isAlive = true;
  });

  ws.on('close', () => {
    clearInterval(interval);
  });
});
```

## 集群模式

### Redis 适配器

```typescript
import { createAdapter } from '@socket.io/redis-adapter';
import { createClient } from 'redis';

const pubClient = createClient({ url: 'redis://localhost:6379' });
const subClient = pubClient.duplicate();

await Promise.all([
  pubClient.connect(),
  subClient.connect(),
]);

io.adapter(createAdapter(pubClient, subClient));

// 多实例间消息同步
io.to('room-123').emit('message', data);  // 所有实例都能收到
```

### 粘性会话

```typescript
// 使用 nginx 配置 ip_hash
upstream websocket {
    ip_hash;
    server ws1:3000;
    server ws2:3000;
}

server {
    location /socket.io/ {
        proxy_pass http://websocket;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 最佳实践

```markdown
1. 使用心跳保持连接活跃
2. 实现消息确认机制
3. 处理重连和状态恢复
4. 限制消息大小防止滥用
5. 使用 Redis 适配器支持集群
6. 记录连接日志便于排查
7. 实现优雅关闭避免消息丢失
```