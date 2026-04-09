---
name: sql-database
description: 当需要编写SQL查询、优化数据库性能、设计SQL索引、使用MySQL/PostgreSQL时调用此技能。触发词：SQL数据库、MySQL、PostgreSQL、SQLite、SQL查询、SQL优化、索引设计、数据库优化、SQL语句。
---

# SQL 数据库开发

## 查询优化

### 索引设计原则

```sql
-- 1. 为 WHERE、JOIN、ORDER BY 字段创建索引
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_order_status_date ON orders(status, created_at);

-- 2. 复合索引遵循最左前缀原则
-- 索引 (a, b, c) 可用于: a, (a,b), (a,b,c)
-- 不能用于: b, c, (b,c)

-- 3. 避免过度索引
-- 写入性能下降，存储空间增加
```

### 查询优化技巧

```sql
-- ❌ 避免 SELECT *
SELECT * FROM users;

-- ✅ 只查询需要的字段
SELECT id, name, email FROM users;

-- ❌ 避免 OR 导致索引失效
SELECT * FROM users WHERE status = 1 OR status = 2;

-- ✅ 使用 IN 或 UNION
SELECT * FROM users WHERE status IN (1, 2);

-- ❌ 避免函数操作索引列
SELECT * FROM users WHERE YEAR(created_at) = 2024;

-- ✅ 使用范围查询
SELECT * FROM users WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01';

-- ❌ 避免 LIKE 左模糊
SELECT * FROM users WHERE name LIKE '%张%';

-- ✅ 使用右模糊或全文索引
SELECT * FROM users WHERE name LIKE '张%';
```

### 分页优化

```sql
-- ❌ 传统 OFFSET 分页（大偏移量性能差）
SELECT * FROM orders ORDER BY id LIMIT 100000, 20;

-- ✅ 游标分页（推荐）
SELECT * FROM orders WHERE id > 100000 ORDER BY id LIMIT 20;

-- ✅ 延迟关联
SELECT o.* FROM orders o
INNER JOIN (SELECT id FROM orders ORDER BY id LIMIT 100000, 20) tmp
ON o.id = tmp.id;
```

## 事务处理

### 事务隔离级别

| 级别 | 脏读 | 不可重复读 | 幻读 | 性能 |
|------|------|-----------|------|------|
| READ UNCOMMITTED | ✓ | ✓ | ✓ | 最高 |
| READ COMMITTED | ✗ | ✓ | ✓ | 高 |
| REPEATABLE READ | ✗ | ✗ | ✓ | 中 |
| SERIALIZABLE | ✗ | ✗ | ✗ | 低 |

### 事务最佳实践

```sql
-- 1. 保持事务简短
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;

-- 2. 避免长事务
-- 长事务会锁定资源，影响并发

-- 3. 正确处理死锁
-- MySQL 会自动检测并回滚一个事务
-- 应用层需要捕获死锁错误并重试
```

## 数据库设计

### 表设计规范

```sql
-- 主键使用自增 ID 或 UUID
CREATE TABLE users (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  -- 或 id CHAR(36) PRIMARY KEY DEFAULT (UUID())

  -- 字段命名：snake_case
  username VARCHAR(50) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,

  -- 时间字段
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  -- 软删除
  deleted_at TIMESTAMP NULL,

  -- 索引
  INDEX idx_email (email),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 常用数据类型

| 类型 | 用途 | 示例 |
|------|------|------|
| INT/BIGINT | 整数、ID | `user_id BIGINT` |
| DECIMAL | 精确小数、金额 | `price DECIMAL(10,2)` |
| VARCHAR | 变长字符串 | `name VARCHAR(100)` |
| TEXT | 长文本 | `content TEXT` |
| JSON | JSON 数据 | `meta JSON` |
| TIMESTAMP | 时间戳 | `created_at TIMESTAMP` |
| ENUM | 枚举 | `status ENUM('active','inactive')` |

## 安全防护

```sql
-- 1. 参数化查询（防止 SQL 注入）
-- ❌ 字符串拼接
"SELECT * FROM users WHERE id = " + userId

-- ✅ 参数化
SELECT * FROM users WHERE id = ?

-- 2. 最小权限原则
GRANT SELECT, INSERT, UPDATE ON mydb.* TO 'app_user'@'%';

-- 3. 敏感数据加密
-- 密码使用 bcrypt，不存储明文
-- 敏感字段使用 AES 加密
```

## 性能监控

```sql
-- MySQL 慢查询
SHOW VARIABLES LIKE 'slow_query%';
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;

-- 查看执行计划
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';

-- 查看索引使用情况
SHOW INDEX FROM users;

-- PostgreSQL 查看活动查询
SELECT * FROM pg_stat_activity;
```

## ORM 最佳实践

### Prisma (Node.js)

```typescript
// 1. 使用 select 只查询需要的字段
const user = await prisma.user.findFirst({
  where: { email },
  select: { id: true, name: true }
})

// 2. 批量操作
await prisma.user.createMany({ data: users })

// 3. 事务
await prisma.$transaction([
  prisma.account.update({ where: { id: 1 }, data: { balance: { decrement: 100 } } }),
  prisma.account.update({ where: { id: 2 }, data: { balance: { increment: 100 } } })
])
```

### SQLAlchemy (Python)

```python
# 1. 批量插入
session.bulk_insert_mappings(User, users)

# 2. 关联查询
users = session.query(User).options(joinedload(User.posts)).all()

# 3. 事务
with session.begin():
    session.add(user)
```