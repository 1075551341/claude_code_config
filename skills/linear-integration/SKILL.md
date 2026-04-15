---
name: linear-integration
description: 集成 Linear 项目管理和 Issue 跟踪
triggers: [集成 Linear 项目管理和 Issue 跟踪]
---

# Linear 集成

## 核心功能

```
📋 Issue 管理 - 创建、更新、查询、关闭
🔄 工作流自动化 - 状态转换、标签、优先级
📊 项目跟踪 - 里程碑、迭代、进度
👥 团队协作 - 分配、评论、附件
```

## API 配置

### API Key 配置

```bash
LINEAR_API_KEY=your-linear-api-key
```

### GraphQL 客户端

```typescript
import { LinearClient } from '@linear/sdk';

const linear = new LinearClient({
  apiKey: process.env.LINEAR_API_KEY,
});
```

## 常用操作

### 创建 Issue

```typescript
// 创建新 Issue
const issue = await linear.createIssue({
  title: '修复登录页面 500 错误',
  description: `
## 问题描述
登录接口返回 500 错误

## 复现步骤
1. 访问 /login
2. 输入用户名密码
3. 点击登录

## 期望结果
成功登录并跳转到首页
  `,
  teamId: 'team-uuid',
  priority: 1, // 0=No priority, 1=Urgent, 2=High, 3=Normal, 4=Low
  labelIds: ['label-uuid'],
});

console.log(`Created issue: ${issue.identifier}`);
```

### 查询 Issues

```typescript
// 查询团队的 Issues
const issues = await linear.issues({
  filter: {
    team: { id: { eq: 'team-uuid' } },
    state: { type: { eq: 'started' } },
  },
  orderBy: 'createdAt',
  first: 20,
});

for (const issue of issues.nodes) {
  console.log(`${issue.identifier}: ${issue.title}`);
  console.log(`  Status: ${await issue.state.then(s => s?.name)}`);
  console.log(`  Assignee: ${await issue.assignee.then(a => a?.name)}`);
}
```

### 更新 Issue

```typescript
// 更新状态
await linear.updateIssue('issue-id', {
  stateId: 'done-state-id',
});

// 分配给用户
await linear.updateIssue('issue-id', {
  assigneeId: 'user-id',
});

// 添加标签
await linear.updateIssue('issue-id', {
  labelIds: ['bug-label-id', 'urgent-label-id'],
});

// 添加评论
await linear.createComment({
  issueId: 'issue-id',
  body: '已修复，请验证',
});
```

## 高级查询

### GraphQL 查询

```typescript
const result = await linear.client.rawRequest(`
  query ($teamId: String!, $priority: Int!) {
    issues(
      filter: {
        team: { id: { eq: $teamId } }
        priority: { eq: $priority }
      }
    ) {
      nodes {
        id
        identifier
        title
        priority
        state { name type }
        assignee { name }
        labels { nodes { name } }
      }
    }
  }
`, {
  teamId: 'team-uuid',
  priority: 1,
});
```

### 搜索 Issue

```typescript
const results = await linear.searchIssues('登录错误', {
  filter: {
    team: { id: { eq: 'team-uuid' } },
  },
  first: 10,
});
```

## 工作流自动化

### 状态转换

```typescript
// 获取工作流状态
const team = await linear.team('team-uuid');
const states = await team.states();

// 获取特定状态
const todoState = states.nodes.find(s => s.name === 'Todo');
const inProgressState = states.nodes.find(s => s.name === 'In Progress');
const doneState = states.nodes.find(s => s.name === 'Done');

// 更新状态
await linear.updateIssue('issue-id', {
  stateId: inProgressState?.id,
});
```

### 批量操作

```typescript
// 批量更新优先级
const urgentIssues = await linear.issues({
  filter: {
    priority: { eq: 1 },
    state: { type: { neq: 'completed' } },
  },
});

for (const issue of urgentIssues.nodes) {
  // 发送通知
  await notifyTeam(`紧急 Issue: ${issue.identifier} - ${issue.title}`);
}
```

## Webhook 集成

```typescript
import express from 'express';

const app = express();

app.post('/linear-webhook', express.json(), async (req, res) => {
  const { type, data } = req.body;

  switch (type) {
    case 'Issue.create':
      console.log(`新 Issue: ${data.identifier}`);
      // 自动分配或通知
      break;

    case 'Issue.update':
      if (data.state?.type === 'completed') {
        console.log(`Issue 完成: ${data.identifier}`);
        // 更新其他系统
      }
      break;

    case 'Comment.create':
      console.log(`新评论: ${data.body}`);
      break;
  }

  res.status(200).send('OK');
});

app.listen(3000);
```

## 与其他工具集成

### GitHub 关联

```typescript
// 关联 GitHub PR
await linear.updateIssue('issue-id', {
  description: issue.description + `\n\n**PR:** #123`,
});

// 或使用 Linear 的 GitHub 集成自动关联
```

### Slack 通知

```typescript
async function notifyNewIssue(issue: any) {
  const slack = new WebClient(process.env.SLACK_BOT_TOKEN);

  await slack.chat.postMessage({
    channel: '#engineering',
    blocks: [
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: `*New Issue Created*\n<${issue.url}|${issue.identifier}: ${issue.title}>`,
        },
      },
      {
        type: 'section',
        fields: [
          { type: 'mrkdwn', text: `*Priority:* ${getPriorityLabel(issue.priority)}` },
          { type: 'mrkdwn', text: `*Team:* ${issue.team.name}` },
        ],
      },
    ],
  });
}
```

## 最佳实践

```markdown
1. 使用标签系统分类 Issue（bug, feature, improvement）
2. 设置合理的优先级：Urgent → High → Normal → Low
3. 使用项目/里程碑跟踪大型功能
4. 定期清理过期 Issue
5. 关联相关 Issue 和 PR
6. 使用模板统一 Issue 描述格式
```