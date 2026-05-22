---
name: claude-api
description: Claude API / Anthropic SDK 开发指南。触发：使用 Claude API、Anthropic SDK、构建 AI 应用、Managed Agents
triggers: [使用 Claude API、Anthropic SDK、构建 AI 应用、Managed Agents]
---

# Claude API / SDK 开发指南

## 模型选择

| 场景 | 推荐模型 | 理由 |
|------|---------|------|
| 复杂推理/代码 | claude-sonnet-4-20250514 | 最佳性价比 |
| 快速/简单任务 | claude-haiku-3-5-20241022 | 最低成本/延迟 |
| 最高质量 | claude-opus-4-20250514 | 最强能力 |

## 核心模式

### 1. 基础调用
```python
import anthropic
client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "..."}]
)
```

### 2. 流式响应
```python
with client.messages.stream(...) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

### 3. 工具使用（Function Calling）
- 定义 tools 数组（name, description, input_schema）
- 处理 tool_use 停止原因
- 返回 tool_result 内容块
- 循环直到 end_turn

### 4. Prompt 缓存
- 标记 `cache_control: {"type": "ephemeral"}` 
- 系统提示和长上下文优先缓存
- 缓存 TTL：5 分钟

### 5. 结构化输出
- 使用 JSON Schema 约束输出
- `response_format` 或工具定义中指定 schema

### 6. 批处理
- 大量独立请求用 Message Batches API
- 异步提交 → 轮询结果

## 最佳实践

1. **Prompt 设计**：具体指令 > 模糊描述，示例 > 规则
2. **错误处理**：重试 429/529，指数退避
3. **Token 管理**：监控 usage 字段，设置合理 max_tokens
4. **安全**：不暴露 API Key，服务端代理请求
5. **成本控制**：Haiku 处理简单任务，Sonnet 处理复杂任务
