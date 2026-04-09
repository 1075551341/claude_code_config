---
description: 安全开发、安全审计、漏洞修复相关任务时启用
alwaysApply: false
---

# 安全规则（专用）

> 配合核心规则使用，仅在安全相关场景加载

## OWASP Top 10 防护

### 1. 注入攻击（SQL/NoSQL/命令注入）

```javascript
// ❌ 禁止拼接
const query = `SELECT * FROM users WHERE id = ${userId}`;

// ✅ 参数化查询
const query = 'SELECT * FROM users WHERE id = ?';
db.query(query, [userId]);

// ✅ ORM 使用
const user = await User.findByPk(userId);
```

### 2. 失效的身份认证

```markdown
防护措施：
- 密码：bcrypt/scrypt 加密存储
- Token：JWT 短有效期 + Refresh Token
- 会话：httpOnly Cookie、Secure、SameSite
- 登录：失败次数限制、验证码
- 敏感操作：二次验证
```

### 3. 敏感数据泄露

```javascript
// ❌ 禁止返回敏感字段
res.json({ user: { id, password, ssn, ... } });

// ✅ 过滤敏感字段
res.json({ user: { id, name, email } });

// ✅ 日志脱敏
logger.info('User login', { userId, email: maskEmail(email) });
```

### 4. XML 外部实体（XXE）

```python
# ❌ 禁用外部实体解析
parser = etree.XMLParser(load_dtd=True, resolve_entities=True)

# ✅ 安全配置
parser = etree.XMLParser(
    load_dtd=False,
    resolve_entities=False,
    no_network=True
)
```

### 5. 访问控制失效

```typescript
// ❌ 仅检查登录状态
if (!req.user) return res.status(401);

// ✅ 检查资源归属
const resource = await Resource.findById(req.params.id);
if (resource.userId !== req.user.id) {
    return res.status(403).json({ error: '无权访问' });
}
```

### 6. 安全配置错误

```yaml
安全检查清单：
□ 禁用目录列表
□ 移除默认账户/密码
□ 关闭调试模式
□ 设置安全 Headers
□ 禁用不必要的服务/端口
□ 配置 CORS 白名单
```

### 7. 跨站脚本（XSS）

```javascript
// ❌ 直接插入 HTML
element.innerHTML = userInput;

// ✅ 使用 textContent
element.textContent = userInput;

// ✅ 使用 DOMPurify
element.innerHTML = DOMPurify.sanitize(userInput);

// ✅ CSP 配置
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-xxx'
```

### 8. 不安全的反序列化

```python
# ❌ pickle 反序列化不可信数据
data = pickle.loads(untrusted_data)

# ✅ 使用 JSON
data = json.loads(untrusted_data)

# ✅ 如必须 pickle，使用白名单
data = pickle.loads(untrusted_data, safe_modules=['datetime', 'decimal'])
```

### 9. 组件漏洞

```bash
# 定期检查依赖漏洞
npm audit
pip audit
yarn audit

# 及时更新依赖
npm update
pip install --upgrade package
```

### 10. 日志与监控不足

```markdown
必须记录：
- 登录/登出事件
- 敏感操作（修改密码、权限变更）
- 失败的访问尝试
- 系统异常

日志要求：
- 不包含敏感数据
- 包含时间戳、用户ID、IP、操作
- 集中存储、定期审计
```

## 安全 Headers 配置

```nginx
# Nginx 配置
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Content-Security-Policy "default-src 'self'" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

## 敏感数据处理

### 加密算法选择

| 用途 | 推荐算法 |
|------|----------|
| 密码存储 | bcrypt / scrypt / Argon2 |
| 对称加密 | AES-256-GCM |
| 非对称加密 | RSA-4096 / Ed25519 |
| 哈希 | SHA-256 / SHA-3 |
| 签名 | HMAC-SHA256 |

### 密钥管理

```markdown
密钥存储：
- 不存代码库
- 使用环境变量或密钥管理服务
- 定期轮换

密钥使用：
- 最小权限原则
- 不在日志中打印
- 使用后立即清除内存
```

## API 安全

```markdown
认证：
- OAuth 2.0 / JWT
- API Key（后端服务间）

授权：
- RBAC（基于角色）
- ABAC（基于属性）

防护：
- Rate Limiting
- 请求签名
- 参数验证
- 输出编码
```

## 安全审计清单

```markdown
代码审查：
□ 无硬编码密钥/密码
□ 输入验证覆盖
□ 输出编码覆盖
□ SQL 参数化
□ 文件上传检查

配置检查：
□ HTTPS 强制
□ 安全 Headers
□ CORS 配置
□ 调试模式关闭

运行监控：
□ 异常登录告警
□ 接口异常监控
□ 依赖漏洞扫描
```