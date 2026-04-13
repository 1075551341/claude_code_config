---
description: 安全开发、安全审计、漏洞修复相关任务时启用
alwaysApply: false
---

# 安全规则（专用）

> 配合核心规则使用，仅在安全相关场景加载

## OWASP Top 10 防护

### 1. 注入攻击（SQL/NoSQL/命令注入）

```javascript
// ❌ 禁止拼接：`SELECT * FROM users WHERE id = ${userId}`
// ✅ 参数化查询：db.query('SELECT * FROM users WHERE id = ?', [userId])
// ✅ ORM：await User.findByPk(userId)
```

### 2. 失效的身份认证

```
密码：bcrypt/scrypt 加密存储 | Token：JWT 短有效期 + Refresh Token
会话：httpOnly Cookie、Secure、SameSite | 登录：失败次数限制、验证码 | 敏感操作：二次验证
```

### 3. 敏感数据泄露

```javascript
// ❌ res.json({ user: { id, password, ssn, ... } })
// ✅ res.json({ user: { id, name, email } })  // 过滤敏感字段
// ✅ logger.info('User login', { userId, email: maskEmail(email) })  // 日志脱敏
```

### 4. XML 外部实体（XXE）

```python
# ❌ etree.XMLParser(load_dtd=True, resolve_entities=True)
# ✅ etree.XMLParser(load_dtd=False, resolve_entities=False, no_network=True)
```

### 5. 访问控制失效

```typescript
// ❌ 仅检查登录状态：if (!req.user) return res.status(401)
// ✅ 检查资源归属：if (resource.userId !== req.user.id) return res.status(403)
```

### 6-10. 其他 OWASP 防护要点

```
6. 安全配置：禁用目录列表 / 移除默认账户 / 关闭调试 / 安全 Headers / CORS 白名单
7. XSS：textContent 优先 / DOMPurify 清理 / CSP 配置
8. 反序列化：JSON 优先 / pickle 用白名单 / 禁止 pickle 不可信数据
9. 组件漏洞：定期 npm audit / pip audit / 及时更新依赖
10. 日志监控：记录登录/敏感操作/失败访问/系统异常，不含敏感数据
```

## 安全 Headers 配置

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Content-Security-Policy "default-src 'self'" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

## 敏感数据处理

| 用途 | 推荐算法 |
|------|----------|
| 密码存储 | bcrypt / scrypt / Argon2 |
| 对称加密 | AES-256-GCM |
| 非对称加密 | RSA-4096 / Ed25519 |
| 哈希 | SHA-256 / SHA-3 |
| 签名 | HMAC-SHA256 |

密钥管理：不存代码库 / 环境变量或密钥管理服务 / 定期轮换 / 最小权限 / 不在日志中打印

## API 安全

```
认证：OAuth 2.0 / JWT / API Key（后端服务间）
授权：RBAC（基于角色）/ ABAC（基于属性）
防护：Rate Limiting / 请求签名 / 参数验证 / 输出编码
```

## 安全审计清单

```
代码审查：□ 无硬编码密钥 □ 输入验证覆盖 □ 输出编码覆盖 □ SQL 参数化 □ 文件上传检查
配置检查：□ HTTPS 强制 □ 安全 Headers □ CORS 配置 □ 调试模式关闭
运行监控：□ 异常登录告警 □ 接口异常监控 □ 依赖漏洞扫描
```
