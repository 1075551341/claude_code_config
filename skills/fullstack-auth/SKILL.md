# 全栈认证授权最佳实践

## 描述
全栈认证授权技能，涵盖 JWT/Session 方案选型、OAuth2.0 接入、
RBAC 权限模型、Token 管理和安全防护。

## 触发条件
当需要实现用户注册登录、权限控制、第三方登录、Token 管理时使用。

## 方案选型

| 方案 | 适用场景 | 特点 |
|------|----------|------|
| JWT | 前后端分离 SPA | 无状态，适合分布式 |
| Session | 传统 Web 应用 | 服务端控制，即时撤销 |
| OAuth 2.0 | 第三方登录 | 标准协议，GitHub/Google/微信 |
| JWT + Refresh Token | 生产级推荐 | 短期 Access + 长期 Refresh |

## JWT 双 Token 实现

```typescript
// 生成 Token 对
function generateTokenPair(userId: string) {
  const accessToken = jwt.sign(
    { sub: userId, type: 'access' },
    process.env.JWT_SECRET,
    { expiresIn: '15m' }
  )
  const refreshToken = jwt.sign(
    { sub: userId, type: 'refresh' },
    process.env.JWT_REFRESH_SECRET,
    { expiresIn: '7d' }
  )
  return { accessToken, refreshToken }
}

// 刷新 Token
async function refreshAccessToken(refreshToken: string) {
  const payload = jwt.verify(refreshToken, process.env.JWT_REFRESH_SECRET)
  if (payload.type !== 'refresh') throw new Error('Token 类型无效')

  // 检查是否在黑名单中（用户登出或密码变更后失效）
  const isRevoked = await redis.get(`revoked:${refreshToken}`)
  if (isRevoked) throw new Error('Token 已撤销')

  return generateTokenPair(payload.sub)
}
```

## RBAC 权限模型

```sql
-- 角色表
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

-- 权限表
CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    resource VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    UNIQUE(resource, action)
);

-- 角色-权限关联
CREATE TABLE role_permissions (
    role_id INT REFERENCES roles(id),
    permission_id INT REFERENCES permissions(id),
    PRIMARY KEY(role_id, permission_id)
);

-- 用户-角色关联
CREATE TABLE user_roles (
    user_id BIGINT REFERENCES users(id),
    role_id INT REFERENCES roles(id),
    PRIMARY KEY(user_id, role_id)
);
```

## 权限校验中间件

```typescript
function requirePermission(resource: string, action: string) {
  return async (req: Request, res: Response, next: NextFunction) => {
    const userId = req.user.id
    const hasPermission = await checkUserPermission(userId, resource, action)
    if (!hasPermission) {
      return res.status(403).json({ code: 403, msg: '权限不足' })
    }
    next()
  }
}

// 使用
router.delete('/users/:id', requirePermission('users', 'delete'), deleteUser)
```

## 安全规范

1. **密码存储**：bcrypt hash（cost >= 12），禁止明文或 MD5
2. **Token 存储**：httpOnly Cookie（防 XSS），SameSite=Strict（防 CSRF）
3. **刷新策略**：Access Token 15 分钟，Refresh Token 7 天
4. **撤销机制**：登出/改密码时将 Refresh Token 加入 Redis 黑名单
5. **限流防护**：登录接口 IP 限流（5次/分钟），失败锁定
6. **传输安全**：强制 HTTPS，Token 不出现在 URL 参数中
