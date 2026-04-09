---
name: socket-event
description: 当需要定义Socket.io事件、实现WebSocket事件处理、设计实时通信协议时调用此技能。触发词：Socket.io事件、WebSocket事件、Socket事件定义、实时通信、Socket.io开发、事件处理、房间管理。
---

# Socket.io 事件处理生成

生成类型安全的 Socket.io 事件处理代码。

## 使用方式

```
/socket-event <action> [options]
```

**操作类型：**
- `define` - 定义事件类型
- `handler` - 生成事件处理器
- `client` - 生成客户端封装

## 事件类型定义

### 服务端类型

```typescript
// types/socket.ts
import { Socket } from 'socket.io'

// 客户端 -> 服务端 事件
interface ClientToServerEvents {
  // 任务相关
  'task:create': (data: { type: string; input: string }) => void
  'task:cancel': (taskId: string) => void
  'task:subscribe': (taskId: string) => void
  'task:unsubscribe': (taskId: string) => void

  // 进度查询
  'progress:get': (taskId: string) => void

  // 房间管理
  'room:join': (roomId: string) => void
  'room:leave': (roomId: string) => void
}

// 服务端 -> 客户端 事件
interface ServerToClientEvents {
  // 任务事件
  'task:created': (task: Task) => void
  'task:updated': (task: Task) => void
  'task:completed': (task: Task) => void
  'task:failed': (task: Task) => void

  // 进度事件
  'progress:update': (data: { taskId: string; progress: number; status: string }) => void

  // 系统事件
  'system:notification': (data: { type: string; message: string }) => void
  'system:error': (error: { code: string; message: string }) => void
}

// 中间件数据
interface SocketData {
  userId: string
  username: string
  rooms: string[]
}

// 完整类型
export type TypedSocket = Socket<
  ClientToServerEvents,
  ServerToClientEvents,
  DefaultEventsMap,
  SocketData
>
```

### 客户端类型

```typescript
// types/socket-client.ts
import type { Manager, Socket } from 'socket.io-client'

type EmittedEvents<T> = {
  [K in keyof T]: T[K] extends (...args: infer A) => void ? A : never
}

type OnEvents<T> = {
  [K in keyof T]: T[K] extends (...args: infer A) => void
    ? (...args: A) => void
    : never
}

export type ClientSocket = Socket<ServerToClientEvents, ClientToServerEvents>
```

## 服务端实现

### Socket 服务初始化

```typescript
// socket/index.ts
import { Server } from 'socket.io'
import type {
  ClientToServerEvents,
  ServerToClientEvents,
  SocketData,
} from '../types/socket'

export function setupSocket(httpServer: HttpServer) {
  const io = new Server<
    ClientToServerEvents,
    ServerToClientEvents,
    DefaultEventsMap,
    SocketData
  >(httpServer, {
    cors: {
      origin: process.env.FRONTEND_URL || 'http://localhost:5173',
      credentials: true,
    },
  })

  // 认证中间件
  io.use(async (socket, next) => {
    try {
      const token = socket.handshake.auth.token
      const payload = verifyToken(token)

      socket.data.userId = payload.userId
      socket.data.username = payload.username
      socket.data.rooms = []

      next()
    } catch (err) {
      next(new Error('Authentication failed'))
    }
  })

  io.on('connection', (socket) => {
    console.log(`用户连接: ${socket.data.username}`)

    // 注册事件处理器
    registerTaskHandlers(io, socket)
    registerRoomHandlers(io, socket)

    socket.on('disconnect', () => {
      console.log(`用户断开: ${socket.data.username}`)
    })
  })

  return io
}
```

### 任务事件处理器

```typescript
// socket/handlers/task.ts
import type { TypedSocket } from '../../types/socket'

export function registerTaskHandlers(
  io: Server,
  socket: TypedSocket
) {
  // 创建任务
  socket.on('task:create', async (data) => {
    try {
      const task = await TaskService.create({
        userId: socket.data.userId,
        type: data.type,
        input: data.input,
      })

      // 通知创建者
      socket.emit('task:created', task)

      // 广播到管理员房间
      io.to('admin').emit('task:created', task)
    } catch (err) {
      socket.emit('system:error', {
        code: 'TASK_CREATE_FAILED',
        message: (err as Error).message,
      })
    }
  })

  // 取消任务
  socket.on('task:cancel', async (taskId) => {
    const task = await TaskService.getById(taskId)

    if (task.userId !== socket.data.userId) {
      return socket.emit('system:error', {
        code: 'FORBIDDEN',
        message: '无权操作此任务',
      })
    }

    await TaskService.cancel(taskId)
    socket.emit('task:updated', { ...task, status: 'cancelled' })
  })

  // 订阅任务进度
  socket.on('task:subscribe', (taskId) => {
    socket.join(`task:${taskId}`)
    socket.data.rooms.push(`task:${taskId}`)
  })

  // 取消订阅
  socket.on('task:unsubscribe', (taskId) => {
    socket.leave(`task:${taskId}`)
    socket.data.rooms = socket.data.rooms.filter(r => r !== `task:${taskId}`)
  })
}
```

### 进度推送

```typescript
// socket/progress.ts
import type { Server } from 'socket.io'

export class ProgressNotifier {
  private io: Server

  constructor(io: Server) {
    this.io = io
  }

  // 推送进度更新
  notify(taskId: string, progress: number, status: string) {
    this.io.to(`task:${taskId}`).emit('progress:update', {
      taskId,
      progress,
      status,
    })
  }

  // 任务完成
  complete(taskId: string, task: Task) {
    this.io.to(`task:${taskId}`).emit('task:completed', task)
  }

  // 任务失败
  fail(taskId: string, task: Task) {
    this.io.to(`task:${taskId}`).emit('task:failed', task)
  }

  // 广播给所有用户
  broadcast(type: string, message: string) {
    this.io.emit('system:notification', { type, message })
  }
}
```

## 客户端封装

### Vue 3 Composable

```typescript
// composables/useSocket.ts
import { ref, onMounted, onUnmounted } from 'vue'
import { io, Socket } from 'socket.io-client'
import type { ServerToClientEvents, ClientToServerEvents } from '@/types/socket'

export function useSocket() {
  const socket = ref<Socket<ServerToClientEvents, ClientToServerEvents> | null>(null)
  const connected = ref(false)

  const connect = (token: string) => {
    socket.value = io(import.meta.env.VITE_WS_URL, {
      auth: { token },
      transports: ['websocket'],
    })

    socket.value.on('connect', () => {
      connected.value = true
      console.log('Socket 连接成功')
    })

    socket.value.on('disconnect', () => {
      connected.value = false
      console.log('Socket 断开连接')
    })
  }

  const disconnect = () => {
    socket.value?.disconnect()
    socket.value = null
  }

  // 事件监听
  const on = <K extends keyof ServerToClientEvents>(
    event: K,
    callback: ServerToClientEvents[K]
  ) => {
    socket.value?.on(event, callback)
  }

  const off = <K extends keyof ServerToClientEvents>(
    event: K,
    callback: ServerToClientEvents[K]
  ) => {
    socket.value?.off(event, callback)
  }

  // 发送事件
  const emit = <K extends keyof ClientToServerEvents>(
    event: K,
    ...args: Parameters<ClientToServerEvents[K]>
  ) => {
    socket.value?.emit(event, ...args)
  }

  return {
    socket,
    connected,
    connect,
    disconnect,
    on,
    off,
    emit,
  }
}
```

### 任务订阅 Composable

```typescript
// composables/useTaskProgress.ts
import { ref, onMounted, onUnmounted } from 'vue'
import { useSocket } from './useSocket'

export function useTaskProgress(taskId: string) {
  const progress = ref(0)
  const status = ref('pending')
  const { on, off, emit } = useSocket()

  const handleProgress = (data: { taskId: string; progress: number; status: string }) => {
    if (data.taskId === taskId) {
      progress.value = data.progress
      status.value = data.status
    }
  }

  onMounted(() => {
    emit('task:subscribe', taskId)
    on('progress:update', handleProgress)
  })

  onUnmounted(() => {
    emit('task:unsubscribe', taskId)
    off('progress:update', handleProgress)
  })

  return { progress, status }
}
```

### 在组件中使用

```vue
<script setup lang="ts">
import { useTaskProgress } from '@/composables/useTaskProgress'

const props = defineProps<{ taskId: string }>()
const { progress, status } = useTaskProgress(props.taskId)
</script>

<template>
  <div class="task-progress">
    <a-progress :percent="progress" :status="status" />
    <span>状态: {{ status }}</span>
  </div>
</template>
```

## Redis 适配器（集群支持）

```typescript
// socket/adapter.ts
import { createAdapter } from '@socket.io/redis-adapter'
import { pubClient, subClient } from '../utils/redis'

export function setupRedisAdapter(io: Server) {
  io.adapter(createAdapter(pubClient, subClient))
}
```