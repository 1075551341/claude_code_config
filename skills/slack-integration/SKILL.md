---
name: slack-integration
description: 集成 Slack 消息发送、频道管理、用户操作。触发词：Slack、Slack API、消息通知、频道管理、Slack Bot。
---

# Slack 集成

## 核心功能

```
📨 消息发送 - 文本、富文本、附件、Block Kit
👥 频道管理 - 创建、归档、成员管理
🤖 Bot 操作 - 命令处理、事件订阅、交互组件
📊 消息查询 - 历史、搜索、线程
```

## API 配置

### Bot Token 权限

```json
{
  "scopes": [
    "chat:write",
    "channels:read",
    "channels:history",
    "users:read",
    "files:write"
  ]
}
```

### 环境变量

```bash
SLACK_BOT_TOKEN=xoxb-xxx
SLACK_APP_TOKEN=xapp-xxx
SLACK_SIGNING_SECRET=xxx
```

## 常用操作

### 发送消息

```typescript
import { WebClient } from '@slack/web-api';

const client = new WebClient(process.env.SLACK_BOT_TOKEN);

// 简单文本消息
await client.chat.postMessage({
  channel: '#general',
  text: 'Hello from Claude!',
});

// Block Kit 富消息
await client.chat.postMessage({
  channel: '#alerts',
  blocks: [
    {
      type: 'header',
      text: {
        type: 'plain_text',
        text: '🚨 系统告警',
      },
    },
    {
      type: 'section',
      text: {
        type: 'mrkdwn',
        text: '*服务:* API Server\n*状态:* 🔴 Down\n*时间:* 2024-01-01 12:00:00',
      },
    },
    {
      type: 'actions',
      elements: [
        {
          type: 'button',
          text: { type: 'plain_text', text: '查看详情' },
          url: 'https://example.com/alerts/123',
        },
      ],
    },
  ],
});
```

### 频道操作

```typescript
// 创建频道
const channel = await client.conversations.create({
  name: 'project-alpha',
  is_private: false,
});

// 邀请成员
await client.conversations.invite({
  channel: channel.id,
  users: 'U12345,U67890',
});

// 获取频道列表
const { channels } = await client.conversations.list({
  types: 'public_channel,private_channel',
});
```

### 文件上传

```typescript
import { createReadStream } from 'fs';

await client.files.uploadV2({
  channel: '#reports',
  file: createReadStream('./report.pdf'),
  filename: 'monthly-report.pdf',
  title: '月度报告',
  initial_comment: '请查收本月报告',
});
```

## Webhook 接收

```typescript
import { createEventAdapter } from '@slack/events-api';

const slackEvents = createEventAdapter(process.env.SLACK_SIGNING_SECRET);

// 监听消息事件
slackEvents.on('message', async (event) => {
  if (event.bot_id) return; // 忽略机器人消息

  console.log(`Received: ${event.text} from ${event.user}`);

  // 自动回复
  if (event.text.includes('help')) {
    await client.chat.postMessage({
      channel: event.channel,
      thread_ts: event.ts,
      text: '需要什么帮助？',
    });
  }
});

// 启动服务
slackEvents.start(3000);
```

## 交互组件

```typescript
import { createMessageAdapter } from '@slack/interactive-messages';

const slackInteractions = createMessageAdapter(process.env.SLACK_SIGNING_SECRET);

// 处理按钮点击
slackInteractions.action({ type: 'button' }, async (payload, respond) => {
  const { actions, user, channel } = payload;

  if (actions[0].action_id === 'approve') {
    await respond({
      text: `✅ ${user.name} 已批准`,
      replace_original: false,
    });
  }
});

slackInteractions.start(3001);
```

## 最佳实践

```markdown
1. 使用线程回复减少频道噪音
2. 限制消息频率，避免刷屏
3. 使用 Block Kit 创建丰富的交互界面
4. 敏感操作需要二次确认
5. 错误时提供清晰的错误信息
```

## 错误处理

```typescript
import { WebAPICallError } from '@slack/web-api';

async function safePostMessage(channel: string, text: string) {
  try {
    return await client.chat.postMessage({ channel, text });
  } catch (error) {
    const apiError = error as WebAPICallError;

    if (apiError.data?.error === 'channel_not_found') {
      console.error('频道不存在，请检查频道名称');
    } else if (apiError.data?.error === 'not_in_channel') {
      // 自动加入频道后重试
      await client.conversations.join({ channel });
      return await client.chat.postMessage({ channel, text });
    }

    throw error;
  }
}
```