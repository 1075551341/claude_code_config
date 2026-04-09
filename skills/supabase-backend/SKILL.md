---
name: supabase-backend
description: 使用 Supabase 构建 BaaS 后端服务。触发词：Supabase、BaaS、实时数据库、PostgreSQL托管、认证服务。
---

# Supabase 后端开发

## 核心功能

```
🗄️ 数据库 - PostgreSQL 托管、实时订阅
🔐 认证 - 用户注册、OAuth、JWT
📦 存储 - 文件上传、图片处理
⚡ 实时 - WebSocket 订阅、实时同步
🔧 Edge Functions - Serverless 函数
```

## 项目初始化

```bash
# 安装 CLI
npm install -g supabase

# 登录
supabase login

# 初始化项目
supabase init

# 启动本地开发
supabase start
```

## 数据库操作

### 客户端配置

```typescript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_ANON_KEY!
);
```

### CRUD 操作

```typescript
// 创建
const { data, error } = await supabase
  .from('posts')
  .insert({
    title: 'Hello Supabase',
    content: 'My first post',
    user_id: user.id,
  })
  .select()
  .single();

// 查询
const { data: posts } = await supabase
  .from('posts')
  .select(`
    id,
    title,
    content,
    users(name, avatar_url),
    comments(count)
  `)
  .eq('published', true)
  .order('created_at', { ascending: false })
  .range(0, 9);  // 分页

// 更新
const { error } = await supabase
  .from('posts')
  .update({ published: true })
  .eq('id', postId);

// 删除
await supabase
  .from('posts')
  .delete()
  .eq('id', postId);
```

### 实时订阅

```typescript
// 订阅表变更
const channel = supabase
  .channel('posts-changes')
  .on('postgres_changes', {
    event: '*',
    schema: 'public',
    table: 'posts',
  }, (payload) => {
    console.log('Change received:', payload);
  })
  .subscribe();

// 取消订阅
channel.unsubscribe();
```

## 认证系统

### 邮箱密码注册

```typescript
const { data, error } = await supabase.auth.signUp({
  email: 'user@example.com',
  password: 'secure-password',
  options: {
    data: {
      name: 'John Doe',
    },
  },
});
```

### OAuth 登录

```typescript
// Google OAuth
await supabase.auth.signInWithOAuth({
  provider: 'google',
  options: {
    redirectTo: 'https://example.com/callback',
  },
});

// GitHub OAuth
await supabase.auth.signInWithOAuth({
  provider: 'github',
});
```

### 魔法链接

```typescript
await supabase.auth.signInWithOtp({
  email: 'user@example.com',
  options: {
    emailRedirectTo: 'https://example.com/welcome',
  },
});
```

### 用户状态

```typescript
// 获取当前用户
const { data: { user } } = await supabase.auth.getUser();

// 监听认证状态
supabase.auth.onAuthStateChange((event, session) => {
  if (event === 'SIGNED_IN') {
    console.log('User signed in:', session?.user);
  }
  if (event === 'SIGNED_OUT') {
    console.log('User signed out');
  }
});
```

## 文件存储

### 上传文件

```typescript
// 上传图片
const { data, error } = await supabase.storage
  .from('avatars')
  .upload(`${user.id}/avatar.png`, file, {
    cacheControl: '3600',
    upsert: true,
  });

// 获取公开 URL
const { data: { publicUrl } } = supabase.storage
  .from('avatars')
  .getPublicUrl(`${user.id}/avatar.png`);

// 生成签名 URL（私有文件）
const { data } = await supabase.storage
  .from('private-documents')
  .createSignedUrl('document.pdf', 3600);  // 1小时有效
```

### 下载文件

```typescript
const { data, error } = await supabase.storage
  .from('documents')
  .download('report.pdf');
```

## Edge Functions

### 创建函数

```typescript
// supabase/functions/hello/index.ts
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';

serve(async (req) => {
  const { name } = await req.json();

  return new Response(
    JSON.stringify({ message: `Hello ${name}!` }),
    { headers: { 'Content-Type': 'application/json' } }
  );
});
```

### 部署函数

```bash
supabase functions deploy hello
```

### 调用函数

```typescript
const { data, error } = await supabase.functions.invoke('hello', {
  body: { name: 'World' },
});
```

## Row Level Security (RLS)

### 启用 RLS

```sql
-- 启用 RLS
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- 允许公开读取已发布的文章
CREATE POLICY "Public posts are viewable by everyone"
ON posts FOR SELECT
USING (published = true);

-- 用户只能管理自己的文章
CREATE POLICY "Users can manage own posts"
ON posts FOR ALL
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);
```

## 数据库迁移

```bash
# 创建迁移
supabase migration new create_posts_table

# 编辑迁移文件
# supabase/migrations/20240101000000_create_posts_table.sql
```

```sql
CREATE TABLE posts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  title TEXT NOT NULL,
  content TEXT,
  user_id UUID REFERENCES auth.users NOT NULL,
  published BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- 启用实时
ALTER publication supabase_realtime ADD TABLE posts;
```

```bash
# 应用迁移
supabase db push

# 重置数据库
supabase db reset
```

## 最佳实践

```markdown
1. 始终启用 RLS 保护数据安全
2. 使用外键维护数据完整性
3. 合理设计数据库索引
4. 使用 Edge Functions 处理敏感逻辑
5. 实时订阅注意性能影响
6. 使用连接池优化数据库连接
```