---
name: vercel-deploy
description: Vercel 部署和托管配置。触发词：Vercel、部署、托管、Edge Functions、前端部署。
---

# Vercel 部署

## 核心功能

```
🚀 自动部署 - Git 集成、PR 预览
⚡ Edge Functions - Serverless API
🌍 CDN - 全球加速、边缘缓存
📊 分析 - 性能监控、访问统计
🔧 环境变量 - 多环境配置
```

## 项目配置

### vercel.json

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    { "source": "/api/(.*)", "destination": "/api" }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" }
      ]
    }
  ]
}
```

## 部署流程

### CLI 部署

```bash
# 安装 CLI
npm i -g vercel

# 登录
vercel login

# 部署
vercel

# 生产部署
vercel --prod
```

### Git 集成

```markdown
1. 在 Vercel Dashboard 导入 GitHub 仓库
2. 配置构建命令和输出目录
3. 推送代码自动触发部署
4. PR 自动创建预览环境
```

## Edge Functions

### API 路由

```
api/
├── users.ts
├── posts/
│   └── [id].ts
└── health.ts
```

```typescript
// api/users.ts
import type { VercelRequest, VercelResponse } from '@vercel/node';

export default async function handler(
  req: VercelRequest,
  res: VercelResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const users = await fetchUsers();

  return res.status(200).json({ users });
}
```

### 动态路由

```typescript
// api/posts/[id].ts
export default async function handler(
  req: VercelRequest,
  res: VercelResponse
) {
  const { id } = req.query;

  const post = await getPost(id as string);

  if (!post) {
    return res.status(404).json({ error: 'Not found' });
  }

  return res.status(200).json(post);
}
```

### Edge Runtime

```typescript
export const config = {
  runtime: 'edge',
};

export default async function handler(request: Request) {
  const url = new URL(request.url);

  return new Response(JSON.stringify({
    message: 'Hello from Edge!',
    url: url.pathname,
  }), {
    headers: { 'Content-Type': 'application/json' },
  });
}
```

## 环境变量

### CLI 设置

```bash
# 添加环境变量
vercel env add DATABASE_URL

# 设置值
vercel env rm DATABASE_URL production
```

### .env 文件

```bash
# .env.local
DATABASE_URL=postgresql://...
JWT_SECRET=your-secret
```

### 代码访问

```typescript
const databaseUrl = process.env.DATABASE_URL;
const jwtSecret = process.env.JWT_SECRET;
```

## 性能优化

### 缓存配置

```typescript
// 静态资源缓存
export const config = {
  headers: [
    {
      source: '/static/(.*)',
      headers: [
        {
          key: 'Cache-Control',
          value: 'public, max-age=31536000, immutable',
        },
      ],
    },
  ],
};
```

### ISR (增量静态生成)

```typescript
// Next.js getStaticProps
export async function getStaticProps() {
  const posts = await getPosts();

  return {
    props: { posts },
    revalidate: 60, // 60秒后重新生成
  };
}
```

## 域名配置

### 自定义域名

```bash
# 添加域名
vercel domains add example.com

# 配置 DNS
# 添加 CNAME 记录指向 cname.vercel-dns.com
```

### 多域名重定向

```json
{
  "redirects": [
    {
      "source": "/blog",
      "destination": "https://blog.example.com",
      "permanent": true
    }
  ]
}
```

## 监控与分析

### Web Analytics

```typescript
// _document.tsx 或 layout.tsx
import { Analytics } from '@vercel/analytics/react';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  );
}
```

### Speed Insights

```typescript
import { SpeedInsights } from '@vercel/speed-insights/next';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <SpeedInsights />
      </body>
    </html>
  );
}
```

## 常见问题排查

### 构建失败

```bash
# 本地测试构建
vercel build

# 查看构建日志
vercel logs <deployment-url>
```

### 函数超时

```json
{
  "functions": {
    "api/**/*.ts": {
      "memory": 1024,
      "maxDuration": 30
    }
  }
}
```

### 地区限制

```json
{
  "functions": {
    "api/**/*.ts": {
      "regions": ["hkg1", "sin1"]  // 香港、新加坡
    }
  }
}
```

## 最佳实践

```markdown
1. 使用 Edge Runtime 提升响应速度
2. 合理设置缓存策略
3. 敏感操作使用 Edge Functions
4. 配置合理的超时和内存
5. 使用预览环境测试变更
6. 监控性能指标及时优化
```