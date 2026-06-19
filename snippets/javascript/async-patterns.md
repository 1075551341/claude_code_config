# 异步模式（禁止裸 await）

> CORE.md: "异步操作必须 try/catch，禁止裸 await"

## 标准 async/await

```typescript
async function fetchUser(id: string): Promise<User> {
  try {
    const response = await api.get(`/users/${id}`);
    return response.data;
  } catch (error) {
    throw new AppError('API_001', `获取用户失败: ${id}`, { original: error });
  }
}
```

## Promise.all 并发

```typescript
const [users, posts] = await Promise.all([
  fetchUsers().catch(e => { logger.error('users failed', e); return [] as User[]; }),
  fetchPosts().catch(e => { logger.error('posts failed', e); return [] as Post[]; }),
]);
```

## 防抖/节流

```typescript
function debounce<T extends (...args: any[]) => any>(fn: T, ms: number) {
  let timer: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), ms);
  };
}
```
