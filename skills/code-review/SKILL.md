---
name: code-review
description: 进行全面代码审查，关注架构、安全、性能和可维护性。审查 PR、代码审计或评估代码质量时使用。
---

# Code Review

## 审查维度（按优先级）

### 1. 正确性与逻辑
- 代码是否实现了预期功能？边界情况是否覆盖？
- 错误处理是否完整？有无逻辑漏洞？

### 2. 安全性
- 输入验证与净化（XSS、SQL 注入、CSRF）
- 认证/授权检查是否遗漏
- 敏感数据（密码、Token、PII）处理方式
- 依赖库已知漏洞（`npm audit` / `pip audit`）

### 3. 性能
- 算法复杂度是否合理？有无 N+1 查询？
- 内存泄漏风险？不必要的重渲染/重计算？
- 可加缓存的热点？

### 4. 可维护性
- 函数/类是否遵循单一职责？
- 魔法数字/硬编码字符串 → 常量/配置
- 命名是否清晰表达意图？
- 复杂逻辑是否有注释？

### 5. 测试覆盖
- 核心路径有无单元测试？
- 边界条件和错误路径是否覆盖？

## 反馈格式
```
🔴 [严重] 安全漏洞 / 数据丢失风险 → 必须修复
🟡 [建议] 性能/可维护性改进 → 强烈推荐
🟢 [优化] 代码风格/小优化 → 可选
💡 [思考] 架构层面讨论
```

## 常见问题速查

### 安全
```typescript
// ❌ XSS
element.innerHTML = userInput
// ✅
element.textContent = userInput

// ❌ SQL 注入
`SELECT * FROM users WHERE id = ${id}`
// ✅
db.query('SELECT * FROM users WHERE id = ?', [id])
```

### 性能
```typescript
// ❌ N+1
const orders = await Order.findAll()
for (const o of orders) { o.user = await User.findById(o.userId) }
// ✅
const orders = await Order.findAll({ include: User })

// ❌ 无效 memo
const val = useMemo(() => props.name.toUpperCase(), []) // 依赖缺失
// ✅
const val = useMemo(() => props.name.toUpperCase(), [props.name])
```

### 错误处理
```typescript
// ❌ 裸 await
const data = await fetchData()
// ✅
try { const data = await fetchData() }
catch (e) { logger.error(e); throw new AppError('获取数据失败', e) }
```

## 审查结论模板
```
## 审查结论
**总体评价**：[通过/需修改/重大问题]

**必须修改**：
- [问题] → [建议方案]

**建议改进**：
- [问题] → [建议方案]

**亮点**：
- [值得肯定的设计/实现]
```
