---
name: claude-api-integration
description: 当需要集成Claude API、使用Anthropic SDK开发AI应用、构建Claude Agent时调用此技能。触发词：Claude API、Anthropic SDK、Claude集成、AI应用开发、Claude Agent、大模型API、Claude开发。
---

# Claude API 集成

## 核心能力

**Claude API调用、Anthropic SDK使用、AI应用开发。**

---

## 适用场景

- Claude API 集成
- AI 应用开发
- Agent 构建
- 对话系统开发

---

## 快速开始

### 安装 SDK

```bash
# Python
pip install anthropic

# Node.js
npm install @anthropic-ai/sdk
```

### 基本调用

```python
# Python
import anthropic

client = anthropic.Anthropic(api_key="your-api-key")

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello, Claude"}
    ]
)

print(message.content[0].text)
```

```javascript
// Node.js
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

const message = await client.messages.create({
  model: 'claude-sonnet-4-6',
  max_tokens: 1024,
  messages: [{ role: 'user', content: 'Hello, Claude' }]
});

console.log(message.content[0].text);
```

---

## 模型选择

| 模型 | 用途 | 特点 |
|------|------|------|
| claude-opus-4-6 | 复杂推理 | 最强能力 |
| claude-sonnet-4-6 | 平衡性能 | 推荐使用 |
| claude-haiku-4-5 | 快速响应 | 轻量高效 |

---

## 高级功能

### 流式响应

```python
with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "讲一个故事"}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

### System Prompt

```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system="你是一个专业的代码审查专家",
    messages=[
        {"role": "user", "content": "审查这段代码..."}
    ]
)
```

### 多模态输入

```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": base64_image
                    }
                },
                {"type": "text", "text": "描述这张图片"}
            ]
        }
    ]
)
```

---

## Tool Use (Function Calling)

### 定义工具

```python
tools = [
    {
        "name": "get_weather",
        "description": "获取指定城市的天气信息",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称"
                }
            },
            "required": ["city"]
        }
    }
]
```

### 处理工具调用

```python
def process_tool_use(tool_name, tool_input):
    if tool_name == "get_weather":
        return get_weather(tool_input["city"])
    return None

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    tools=tools,
    messages=messages
)

if response.stop_reason == "tool_use":
    for block in response.content:
        if block.type == "tool_use":
            result = process_tool_use(block.name, block.input)
            # 继续对话...
```

---

## 最佳实践

### Token 管理

```python
# 估算token数量
def count_tokens(text):
    return len(text) // 4  # 粗略估算

# 控制输出长度
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=500,  # 限制输出
    messages=messages
)
```

### 错误处理

```python
from anthropic import APIError, RateLimitError

try:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=messages
    )
except RateLimitError:
    print("达到速率限制，稍后重试")
except APIError as e:
    print(f"API错误: {e}")
```

### 对话历史管理

```python
def chat(messages, user_input):
    messages.append({"role": "user", "content": user_input})
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=messages
    )
    
    messages.append({
        "role": "assistant",
        "content": response.content[0].text
    })
    
    return messages
```

---

## 注意事项

```
必须：
- 安全存储API密钥
- 处理速率限制
- 监控Token使用
- 记录请求日志

避免：
- 硬编码API密钥
- 无限重试
- 忽略错误处理
- 发送敏感信息
```

---

## 相关技能

- `prompt-engineering` - Prompt设计
- `mcp-builder` - MCP服务器构建
- `ai-engineer` agent - AI功能开发