---
name: mcp-builder
description: 创建高质量 MCP（Model Context Protocol）服务器，使 LLM 通过设计良好的工具与外部服务交互。构建 MCP 服务器或集成外部 API 时使用。
---

# MCP Server Development

## 核心原则
- **工具粒度**：每个工具做一件明确的事，名称用 `{service}_{action}` 格式（如 `github_create_issue`）
- **描述优先**：工具描述是 LLM 的导航地图，必须清晰说明"何时用"和"会做什么"
- **错误可操作**：错误信息告诉 LLM 如何修复，而不只是报错

## Python (FastMCP) 快速实现
```python
from fastmcp import FastMCP

mcp = FastMCP("service-name")

@mcp.tool()
async def service_get_item(item_id: str) -> dict:
    """获取指定 ID 的条目详情。
    
    Args:
        item_id: 条目唯一标识符
    Returns:
        包含 id、name、status 的条目对象
    """
    try:
        result = await api_client.get(f"/items/{item_id}")
        return result
    except NotFoundError:
        raise ValueError(f"条目 {item_id} 不存在，请先用 service_list_items 确认 ID")
    except ApiError as e:
        raise RuntimeError(f"API 调用失败：{e.message}")

if __name__ == "__main__":
    mcp.run()
```

## TypeScript (MCP SDK) 快速实现
```typescript
import { Server } from '@modelcontextprotocol/sdk/server/index.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'

const server = new Server({ name: 'service-name', version: '1.0.0' })

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [{
    name: 'service_get_item',
    description: '获取指定条目详情',
    inputSchema: {
      type: 'object',
      properties: { item_id: { type: 'string', description: '条目 ID' } },
      required: ['item_id']
    }
  }]
}))

server.setRequestHandler(CallToolRequestSchema, async (req) => {
  const { name, arguments: args } = req.params
  if (name === 'service_get_item') {
    const item = await getItem(args.item_id as string)
    return { content: [{ type: 'text', text: JSON.stringify(item) }] }
  }
  throw new Error(`未知工具：${name}`)
})

const transport = new StdioServerTransport()
await server.connect(transport)
```

## 工具设计检查清单
- [ ] 名称：`{service}_{verb}_{noun}`，动词用 get/list/create/update/delete/search
- [ ] 描述：说明用途、关键参数含义、返回结构
- [ ] 参数：用枚举限制有效值；可选参数给默认值
- [ ] 返回：结构化 JSON，字段名自描述
- [ ] 错误：区分"用户错误"（4xx，告知修复方法）和"系统错误"（5xx）
- [ ] 分页：列表工具支持 `limit`/`cursor`，避免一次返回全量

## 认证处理
```python
# 从环境变量读取，不硬编码
import os
api_key = os.environ.get("SERVICE_API_KEY")
if not api_key:
    raise RuntimeError("缺少 SERVICE_API_KEY 环境变量")
```
