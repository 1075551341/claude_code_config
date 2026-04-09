---
name: n8n-automation
description: 当需要配置n8n工作流自动化、创建自动化节点、集成第三方服务自动化时调用此技能。触发词：n8n、自动化工作流、工作流自动化、n8n节点、自动化集成、n8n配置、流程自动化、工作流节点。
---

# n8n 工作流自动化

## 核心能力

**n8n 工作流配置、节点创建、自动化流程设计。**

---

## 适用场景

- 自动化工作流创建
- 第三方服务集成
- 数据同步自动化
- 定时任务配置
- 通知自动化

---

## 基本概念

### 节点类型

| 类型 | 用途 |
|------|------|
| Trigger | 启动工作流 |
| Action | 执行操作 |
| Logic | 流程控制 |
| Transform | 数据转换 |

### 常用触发器

```
- Manual Trigger（手动）
- Schedule Trigger（定时）
- Webhook（HTTP触发）
- Email Trigger（邮件触发）
- File Trigger（文件触发）
```

---

## 工作流创建

### 1. 定义触发

```json
{
  "nodes": [
    {
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "position": [250, 300],
      "parameters": {
        "mode": "everyDay",
        "hour": 9
      }
    }
  ]
}
```

### 2. 添加操作

```json
{
  "name": "HTTP Request",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "GET",
    "url": "https://api.example.com/data"
  }
}
```

### 3. 数据转换

```json
{
  "name": "Set",
  "type": "n8n-nodes-base.set",
  "parameters": {
    "values": {
      "string": [
        {
          "name": "processedData",
          "value": "={{$json.field}}"
        }
      ]
    }
  }
}
```

### 4. 输出结果

```json
{
  "name": "Email Send",
  "type": "n8n-nodes-base.emailSend",
  "parameters": {
    "fromEmail": "automation@example.com",
    "toEmail": "user@example.com",
    "subject": "Daily Report",
    "text": "={{$json.report}}"
  }
}
```

---

## 表达式语法

### 数据引用

```
{{ $json.field }}           # 当前节点数据
{{ $node["NodeName"].json }} # 其他节点数据
{{ $now }}                   # 当前时间
{{ $env.VAR_NAME }}          # 环境变量
```

### 函数调用

```
{{ $json.date.toDate() }}
{{ $json.text.toUpperCase() }}
{{ $json.items.length }}
```

---

## 常用集成示例

### Slack 通知

```json
{
  "name": "Slack",
  "type": "n8n-nodes-base.slack",
  "parameters": {
    "channel": "#general",
    "text": "={{$json.message}}"
  }
}
```

### Google Sheets

```json
{
  "name": "Google Sheets",
  "type": "n8n-nodes-base.googleSheets",
  "parameters": {
    "operation": "append",
    "sheetId": "sheet_id",
    "range": "A1:D1"
  }
}
```

### GitHub

```json
{
  "name": "GitHub",
  "type": "n8n-nodes-base.github",
  "parameters": {
    "operation": "createIssue",
    "repo": "owner/repo",
    "title": "={{$json.title}}"
  }
}
```

---

## 流程控制

### 条件分支

```json
{
  "name": "IF",
  "type": "n8n-nodes-base.if",
  "parameters": {
    "conditions": {
      "string": [
        {
          "value1": "={{$json.status}}",
          "operation": "equals",
          "value2": "success"
        }
      ]
    }
  }
}
```

### 循环处理

```json
{
  "name": "Split In Batches",
  "type": "n8n-nodes-base.splitInBatches",
  "parameters": {
    "batchSize": 10
  }
}
```

---

## 注意事项

```
必须：
- 使用表达式而非硬编码
- 添加错误处理节点
- 配置重试策略
- 测试边界情况

避免：
- 无限循环设计
- 敏感数据硬编码
- 节点依赖顺序问题
- 未设置超时
```

---

## 相关技能

- `scheduled-task` - 定时任务
- `api-development` - API 开发
- `deploy-script` - 部署配置