---
name: spec-compliance
description: 规格合规性检查和验证。触发词：规格合规、合规检查、规格验证、需求验证、acceptance criteria。
---

# 规格合规检查

## 检查流程

```
📋 规格解析 → 🔍 实现检查 → ✅ 合规报告
```

## 检查维度

### 1. 功能完整性

```markdown
## 需求项检查

| 需求ID | 描述 | 状态 | 证据 |
|--------|------|------|------|
| REQ-001 | 用户登录 | ✅ | src/auth/login.ts:45 |
| REQ-002 | 密码重置 | ✅ | src/auth/reset.ts:12 |
| REQ-003 | 记住我功能 | ❌ | 未实现 |

完成率：66% (2/3)
```

### 2. 接口合规

```typescript
// 规格定义
interface UserAPI {
  GET /api/users: User[];
  POST /api/users: User;
  GET /api/users/:id: User;
}

// 合规检查
✅ GET /api/users - 实现匹配
✅ POST /api/users - 实现匹配
❌ GET /api/users/:id - 返回类型不匹配（规格要求 User，实际返回 UserDTO）
```

### 3. 数据模型合规

```markdown
## 数据模型检查

### 规格要求
\`\`\`typescript
interface User {
  id: string;        // UUID
  name: string;      // 2-100 字符
  email: string;     // 有效邮箱
  createdAt: Date;
}
\`\`\`

### 实现检查
- ✅ id: string - 匹配
- ✅ name: string - 匹配（验证规则已实现）
- ✅ email: string - 匹配（邮箱格式验证已实现）
- ✅ createdAt: Date - 匹配
```

### 4. 验收标准检查

```markdown
## Acceptance Criteria 验证

### AC-001: 用户登录成功后跳转到首页
- [x] 输入正确凭据
- [x] 点击登录按钮
- [x] 验证跳转到首页
- 证据：tests/e2e/auth.spec.ts:25

### AC-002: 连续登录失败 5 次后锁定账户
- [x] 模拟 5 次失败登录
- [x] 验证账户被锁定
- [x] 验证显示锁定提示
- 证据：tests/unit/auth.test.ts:78

### AC-003: 锁定账户 30 分钟后自动解锁
- ❌ 未测试
- 原因：时间相关测试需要 mock
```

### 5. 非功能需求

```markdown
## 性能要求

| 指标 | 规格要求 | 实测结果 | 状态 |
|------|----------|----------|------|
| API 响应时间 | < 200ms | 156ms | ✅ |
| 页面加载时间 | < 3s | 2.1s | ✅ |
| 并发用户 | 100 | 测试中 | ⏳ |

## 安全要求

| 要求 | 状态 | 证据 |
|------|------|------|
| HTTPS | ✅ | 证书配置完成 |
| 密码加密 | ✅ | bcrypt, rounds=12 |
| JWT 过期 | ✅ | 1 小时过期 |
| SQL 注入防护 | ✅ | 参数化查询 |
```

## 合规报告模板

```markdown
# 规格合规报告

## 概览
- 规格版本：v1.2.0
- 检查时间：YYYY-MM-DD HH:mm
- 总体合规率：85%

## 功能合规
| 模块 | 合规项 | 非合规项 | 合规率 |
|------|--------|----------|--------|
| 用户认证 | 8 | 1 | 89% |
| 订单管理 | 12 | 2 | 86% |
| 支付系统 | 5 | 3 | 63% |

## 问题清单

### 高优先级
1. [REQ-003] 记住我功能未实现
2. [REQ-015] 支付回调处理缺失

### 中优先级
1. [REQ-008] 分页参数未完全对齐
2. [REQ-022] 错误码不规范

### 低优先级
1. [REQ-030] 日志格式不一致

## 建议
1. 优先处理高优先级问题
2. 补充缺失的单元测试
3. 完善错误处理逻辑
```

## 自动化检查

```bash
# 运行合规检查
npm run spec-check

# 生成报告
npm run spec-report

# 检查 API 合规
npm run api-compliance
```