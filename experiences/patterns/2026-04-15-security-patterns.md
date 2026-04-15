# 安全经验模式

> 来源：owasp, awesome-claude-code

---

## 模式9: OWASP Top 10 防护

````markdown
---
name: owasp-top10-protection
date: 2026-04-15
confidence: 0.95
source: security-rules
tags: [security, owasp, validation]
---

# OWASP Top 10 防护清单

## 1. 注入攻击

```typescript
// ❌ 禁止拼接
const query = `SELECT * FROM users WHERE id = ${userId}`;

// ✅ 参数化查询
const query = "SELECT * FROM users WHERE id = ?";
db.query(query, [userId]);
```
````

## 2. 失效的身份认证

- 密码：bcrypt/scrypt 加密存储
- Token：JWT 短有效期 + Refresh Token
- 会话：httpOnly Cookie、Secure、SameSite

## 3. 敏感数据泄露

```typescript
// ❌ 泄露敏感字段
res.json({ user: { id, password, ssn, creditCard } });

// ✅ 过滤敏感字段
res.json({ user: { id, name, email } });
```

## 4. XXE

```python
# ❌ 危险配置
etree.XMLParser(load_dtd=True, resolve_entities=True)

# ✅ 安全配置
etree.XMLParser(load_dtd=False, resolve_entities=False, no_network=True)
```

## 5. 访问控制失效

```typescript
// ❌ 仅检查登录状态
if (!req.user) return res.status(401);

// ✅ 检查资源归属
if (resource.userId !== req.user.id) return res.status(403);
```

## 6-10. 其他

- 安全配置：禁用目录列表、安全Headers
- XSS：textContent优先/DOMPurify
- 反序列化：JSON优先
- 组件漏洞：定期npm audit
- 日志监控：记录异常登录

## 提取决策

- 置信度: 0.95
- 提取为: security checklist
- 原因: OWASP标准，业界公认

````

---

## 模式10: 密钥检测模式

```markdown
---
name: secret-detection-patterns
date: 2026-04-15
confidence: 0.95
source: everything-claude-code
tags: [security, secrets, detection]
---

# 密钥检测模式

## 背景
代码中意外提交密钥是严重安全风险。

## 检测模式
```regex
# GitHub Token
ghp_[a-zA-Z0-9]{36}
ghs_[a-zA-Z0-9]{36}
ghu_[a-zA-Z0-9]{36}

# OpenAI Key
sk-[a-zA-Z0-9]{48}

# AWS Key
AKIA[0-9A-Z]{16}

# Private Key
-----BEGIN (RSA | EC | DSA | OPENSSH) PRIVATE KEY-----

# Generic Secret
(password|api_key|token|secret|credential)\s*[=:]\s*['"]?[a-zA-Z0-9+/=]{20,}
````

## 提取决策

- 置信度: 0.95
- 提取为: hook pattern
- 原因: 防止密钥泄露的关键防线

```

```
