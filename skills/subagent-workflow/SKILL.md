---
name: subagent-workflow
description: 多 Agent 协作工作流编排。触发词：多agent、Agent协作、子代理、并行开发、工作流编排。
---

# 子代理协作工作流

## 核心概念

```
🎯 主代理 - 任务分解、协调、整合
🤖 子代理 - 专业执行、独立上下文
🔄 工作流 - 顺序/并行/条件分支
```

## 协作模式

### 1. 顺序执行

```markdown
任务 → AgentA → AgentB → AgentC → 结果

示例：
需求分析 → 设计师 → 开发者 → 测试工程师
```

### 2. 并行执行

```markdown
          ┌→ AgentA →┐
任务 → 主代理 → AgentB → 整合 → 结果
          └→ AgentC →┘

示例：
前端开发者 ─┐
后端开发者 ─┼→ 集成测试
数据库设计师 ┘
```

### 3. 条件分支

```markdown
任务
  ├─ 条件A → AgentA
  ├─ 条件B → AgentB
  └─ 默认   → AgentC
```

## 任务分解规则

### 分解粒度

```markdown
✅ 合适的分解：
- 单一职责：每个子任务有明确目标
- 独立上下文：子任务之间最小依赖
- 可验证：每个子任务有验收标准

❌ 避免的分解：
- 过于细碎：导致协调开销过大
- 高度耦合：子任务需要频繁通信
- 边界模糊：责任不清晰
```

### 分解模板

```markdown
## 任务：[任务名称]

### 子任务 1：[子任务名]
- 负责 Agent：[agent-name]
- 输入：[需要什么]
- 输出：[产出什么]
- 验收标准：[如何验证]
- 预计时间：[时间估算]

### 子任务 2：...
```

## Agent 选择策略

```markdown
| 任务类型 | 推荐 Agent |
|----------|------------|
| API 设计 | backend-developer |
| UI 实现 | frontend-developer |
| 数据库设计 | database-architect |
| 代码审查 | code-reviewer |
| 安全审计 | security-scanner |
| 测试编写 | qa-engineer |
| 文档编写 | doc-generator |
| 性能优化 | performance-analyzer |
```

## 通信协议

### 输入输出格式

```typescript
// 子任务输入
interface SubTaskInput {
  taskId: string;
  description: string;
  context: Record<string, unknown>;
  constraints: string[];
  expectedOutput: string;
}

// 子任务输出
interface SubTaskOutput {
  taskId: string;
  status: 'success' | 'failed' | 'blocked';
  result: Record<string, unknown>;
  issues: string[];
  suggestions: string[];
}
```

### 进度汇报

```markdown
## 进度更新 [timestamp]

### 已完成
- ✅ 子任务 A：完成
- ✅ 子任务 B：完成

### 进行中
- 🔄 子任务 C：50%

### 等待中
- ⏳ 子任务 D：等待子任务 C

### 阻塞
- ❌ 子任务 E：缺少依赖
```

## 错误处理

```markdown
## 错误恢复策略

1. 重试：同一 Agent 重试（最多 2 次）
2. 切换：换另一个同类 Agent
3. 人工介入：报告用户请求指导
4. 降级：跳过非关键步骤
5. 回滚：恢复到上一个稳定状态
```

## 最佳实践

```markdown
1. 明确每个 Agent 的职责边界
2. 减少子任务间的依赖
3. 设置合理的超时和重试
4. 保持主代理的上下文精简
5. 记录协作日志便于调试
6. 定期同步进度避免偏离
```