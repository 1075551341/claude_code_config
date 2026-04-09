---
name: subagent-driven-development
description: 用于子代理驱动开发模式，每个任务由新子代理执行并经过两阶段审查。当有实施计划需要执行、需要将任务分发给子代理、复杂功能需要分步实现时使用。触发词：子代理开发、subagent、subagent-driven、任务分发、并行开发、代理协调、执行计划、任务拆解、子代理审查、多代理协作。
---

# 子代理驱动开发

## 核心理念

将复杂任务拆分为独立子任务，分发给专门的子代理并行处理，最后整合结果。

```
┌─────────────┐
│   主代理    │ ← 协调和整合
└──────┬──────┘
       │
  ┌────┼────┬────────┐
  ↓    ↓    ↓        ↓
┌───┐┌───┐┌───┐  ┌───┐
│子1││子2││子3│  │子4│  ← 并行执行
└───┘└───┘└───┘  └───┘
```

## 工作流程

### 第一阶段：规范制定

主代理定义清晰的接口规范：

```markdown
## 任务规范

### 目标

[明确的任务目标]

### 输入

- 参数1：类型、说明
- 参数2：类型、说明

### 输出

- 返回值：类型、说明
- 格式要求：JSON Schema / 文件格式

### 约束

- 性能要求
- 兼容性要求
- 安全要求

### 验收标准

- [ ] 标准1
- [ ] 标准2
```

### 第二阶段：任务分发

```typescript
// 将大任务拆分为独立子任务
const tasks = [
  {
    id: "auth",
    agent: "backend-developer",
    spec: "实现用户认证模块，包含登录、注册、Token 刷新",
    dependencies: [],
    output: "auth-module/",
  },
  {
    id: "user-ui",
    agent: "frontend-developer",
    spec: "实现用户登录注册页面，对接 auth API",
    dependencies: ["auth"], // 依赖认证模块的 API 文档
    output: "src/pages/auth/",
  },
  {
    id: "db",
    agent: "database-architect",
    spec: "设计用户表结构，支持多种登录方式",
    dependencies: [],
    output: "migrations/",
  },
];

// 并行启动无依赖的任务
await Promise.all([
  runAgent(
    "backend-developer",
    tasks.find((t) => t.id === "auth"),
  ),
  runAgent(
    "database-architect",
    tasks.find((t) => t.id === "db"),
  ),
]);

// 等待依赖完成后启动后续任务
await runAgent(
  "frontend-developer",
  tasks.find((t) => t.id === "user-ui"),
);
```

### 第三阶段：质量审查

```markdown
## 审查清单

### 规范符合性

- [ ] 输出格式符合规范
- [ ] 接口定义一致
- [ ] 命名规范一致

### 代码质量

- [ ] 无明显 bug
- [ ] 错误处理完善
- [ ] 代码可读性好

### 集成检查

- [ ] 模块间接口正确
- [ ] 依赖关系正确
- [ ] 无循环依赖
```

## 子代理类型

### 按职责划分

| 代理类型           | 适用任务          | 输出                |
| ------------------ | ----------------- | ------------------- |
| frontend-developer | UI 组件、页面开发 | Vue/React 组件      |
| backend-developer  | API、服务开发     | Express/NestJS 代码 |
| database-architect | 数据库设计        | Migration 脚本      |
| tester             | 测试用例编写      | 测试文件            |
| doc-writer         | 文档编写          | Markdown 文档       |

### 按领域划分

| 代理类型        | 适用场景           |
| --------------- | ------------------ |
| auth-expert     | 认证授权相关       |
| payment-expert  | 支付相关           |
| search-expert   | 搜索功能           |
| realtime-expert | WebSocket/实时通信 |

## 通信协议

### 任务分配消息

```json
{
  "taskId": "auth-001",
  "agentType": "backend-developer",
  "spec": {
    "goal": "实现 JWT 认证中间件",
    "input": {
      "userSchema": "参考 models/user.ts"
    },
    "output": {
      "format": "TypeScript 文件",
      "path": "src/middlewares/auth.ts"
    },
    "constraints": ["Token 有效期 15 分钟", "支持刷新 Token"]
  }
}
```

### 结果反馈消息

```json
{
  "taskId": "auth-001",
  "status": "completed",
  "output": {
    "files": ["src/middlewares/auth.ts"],
    "exports": ["authMiddleware", "refreshToken"],
    "usage": "参考 README.md"
  },
  "issues": []
}
```

## 最佳实践

### 1. 任务粒度

```
✅ 合适：一个子任务 1-4 小时完成
❌ 过大：一个子任务需要几天
❌ 过小：一个子任务几分钟
```

### 2. 接口先行

```typescript
// 先定义接口，再分发任务
interface AuthService {
  login(email: string, password: string): Promise<LoginResult>;
  register(data: RegisterData): Promise<User>;
  refresh(token: string): Promise<TokenPair>;
}

// 前端代理基于接口开发
// 后端代理基于接口实现
```

### 3. 隔离原则

- 每个子代理在独立目录工作
- 共享代码通过接口访问
- 避免直接修改其他模块代码

### 4. 增量集成

```
完成一个 → 集成一个 → 验证一个
而不是全部完成再集成
```

## 错误处理

### 子任务失败

```typescript
try {
  await runSubAgent(task);
} catch (error) {
  // 1. 记录失败原因
  logger.error("Subtask failed", { task, error });

  // 2. 决定处理策略
  if (task.critical) {
    // 关键任务失败，停止整个流程
    throw error;
  } else {
    // 非关键任务，跳过并记录
    skippedTasks.push(task);
  }

  // 3. 尝试替代方案
  if (task.fallback) {
    await runSubAgent(task.fallback);
  }
}
```

### 冲突解决

```markdown
当多个子代理修改同一文件时：

1. 预防：通过任务划分避免冲突
2. 检测：使用 git diff 检查冲突
3. 解决：主代理协调合并
```
