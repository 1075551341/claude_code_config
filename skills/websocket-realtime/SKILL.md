# WebSocket 实时通信最佳实践

## 描述
WebSocket 和实时通信技能，涵盖 Socket.io、原生 WebSocket、SSE 的选型、
房间管理、消息协议设计、断线重连和安全防护。

## 触发条件
当需要实现实时推送、聊天、协同编辑、实时数据看板等功能时使用。

## 技术选型

| 场景 | 推荐方案 | 理由 |
|------|----------|------|
| 通用实时通信 | Socket.io | 自动降级、房间、命名空间、生态完整 |
| 高性能场景 | ws / uWebSockets | 零依赖，吞吐量高 |
| 单向推送 | SSE (EventSource) | HTTP 兼容，简单易用，自动重连 |
| 全栈类型安全 | tRPC subscriptions | 与 tRPC 生态无缝集成 |

## Socket.io 服务端模板

```typescript
import { Server } from 'socket.io'

const io = new Server(httpServer, {
  cors: { origin: process.env.CLIENT_URL, credentials: true },
  pingInterval: 25000,
  pingTimeout: 20000,
})

// JWT 鉴权中间件
io.use(async (socket, next) => {
  const token = socket.handshake.auth.token
  try {
    const user = await verifyToken(token)
    socket.data.user = user
    next()
  } catch {
    next(new Error('认证失败'))
  }
})

io.on('connection', (socket) => {
  const userId = socket.data.user.id
  socket.join(`user:${userId}`)

  socket.on('message:send', async (data) => {
    const message = await saveMessage(data)
    io.to(`room:${data.roomId}`).emit('message:new', message)
  })

  socket.on('disconnect', (reason) => {
    console.log(`用户 ${userId} 断开: ${reason}`)
  })
})
```

## 客户端模板

```typescript
import { io, Socket } from 'socket.io-client'

class SocketClient {
  private socket: Socket

  constructor(url: string, token: string) {
    this.socket = io(url, {
      auth: { token },
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 10,
    })

    this.socket.on('connect', () => console.log('已连接'))
    this.socket.on('connect_error', (err) => console.error('连接失败:', err.message))
  }

  send(event: string, data: unknown) {
    this.socket.emit(event, data)
  }

  on(event: string, handler: (...args: unknown[]) => void) {
    this.socket.on(event, handler)
  }

  disconnect() {
    this.socket.disconnect()
  }
}
```

## 最佳实践

1. **鉴权**：连接握手时验证 JWT，拒绝未授权连接
2. **房间管理**：使用命名空间隔离业务模块，房间隔离会话
3. **消息协议**：统一格式 `{ type, payload, timestamp }`
4. **断线重连**：指数退避重试，重连后同步丢失消息
5. **限流**：单用户消息频率限制，防止 DDoS
6. **心跳检测**：定期 ping/pong 检测假死连接
