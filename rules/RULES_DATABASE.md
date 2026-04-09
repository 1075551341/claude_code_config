---
description: 数据库设计、查询、迁移相关任务时启用
alwaysApply: false
---

# 数据库规则（专用）

> 配合核心规则使用，仅在数据库场景加载

## 数据库选型

```
场景               →  推荐方案
───────────────────────────────────
关系型事务系统     →  PostgreSQL / MySQL
高并发读/简单写    →  MySQL（InnoDB）
复杂查询/分析      →  PostgreSQL
嵌入式/轻量        →  SQLite
文档存储           →  MongoDB
缓存/会话          →  Redis
全文搜索           →  Elasticsearch / MeiliSearch
时序数据           →  TimescaleDB / InfluxDB
```

## 表设计规范

### 命名规范

```
表名：snake_case 复数形式（users, order_items）
主键：id（BIGINT AUTO_INCREMENT / UUID）
外键：{关联表}_id（user_id, order_id）
索引：idx_{表名}_{字段名}（idx_users_email）
唯一索引：uniq_{表名}_{字段名}
```

### 字段规范

```sql
-- 必备字段
id          BIGINT PRIMARY KEY AUTO_INCREMENT,
created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
is_deleted  TINYINT(1) DEFAULT 0,  -- 软删除标记

-- 字段类型选择
金额        DECIMAL(19,4)  -- 不用 FLOAT/DOUBLE
状态        TINYINT / ENUM
JSON        JSON（MySQL 5.7+）
大文本      TEXT / LONGTEXT
时间        TIMESTAMP / DATETIME
```

### 索引原则

```markdown
必须建索引：
- 主键、外键
- WHERE 条件字段
- ORDER BY / GROUP BY 字段
- JOIN 关联字段

避免过度索引：
- 单表索引不超过 5 个
- 复合索引遵循最左前缀
- 低选择性字段不建索引（如性别）
```

## 查询规范

### 禁止事项

```sql
-- ❌ 禁止 SELECT *
SELECT * FROM users;

-- ✅ 明确字段
SELECT id, name, email FROM users;

-- ❌ 禁止拼接 SQL
"SELECT * FROM users WHERE id = " + userId

-- ✅ 参数化查询
PREPARE stmt FROM 'SELECT * FROM users WHERE id = ?';
EXECUTE stmt USING @userId;

-- ❌ 禁止无 LIMIT 的批量操作
UPDATE users SET status = 1;

-- ✅ 分批处理
UPDATE users SET status = 1 WHERE id BETWEEN 1 AND 1000;
```

### 性能优化

```sql
-- 使用 EXPLAIN 分析查询计划
EXPLAIN SELECT * FROM orders WHERE user_id = 123;

-- 避免函数操作索引字段
-- ❌
WHERE DATE(created_at) = '2024-01-01'
-- ✅
WHERE created_at >= '2024-01-01' AND created_at < '2024-01-02'

-- 大数据量分页优化
-- ❌
SELECT * FROM orders LIMIT 10000, 20;
-- ✅
SELECT * FROM orders WHERE id > 10000 ORDER BY id LIMIT 20;
```

## Migration 规范

### 迁移脚本结构

```sql
-- migrations/20240101_001_create_users.sql

-- +migrate Up
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_users_email (email)
);

-- +migrate Down
DROP TABLE IF EXISTS users;
```

### 迁移原则

```markdown
1. 每个迁移必须可回滚（Up/Down 配对）
2. 不修改已执行的迁移脚本
3. 大表变更分多步执行：
   - 添加新列（允许 NULL）
   - 数据迁移（分批）
   - 添加约束/索引
4. 生产环境迁移先在 staging 验证
5. 迁移前备份数据
```

## 事务规范

```sql
-- 事务模板
START TRANSACTION;

-- 设置超时（MySQL）
SET SESSION innodb_lock_wait_timeout = 5;

-- 业务操作
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

-- 检查业务条件
SELECT balance INTO @bal FROM accounts WHERE id = 1;
IF @bal < 0 THEN
    ROLLBACK;
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '余额不足';
END IF;

COMMIT;
```

## 安全规范

| 风险 | 措施 |
|------|------|
| SQL 注入 | 参数化查询、ORM、输入验证 |
| 敏感数据泄露 | 字段加密、日志脱敏 |
| 越权访问 | 行级权限检查 |
| 数据丢失 | 定期备份、主从复制 |

## 备份策略

```markdown
备份频率：
- 全量备份：每日凌晨
- 增量备份：每小时
- binlog：实时

保留周期：
- 全量：30 天
- 增量：7 天
- binlog：3 天

恢复演练：每季度一次
```