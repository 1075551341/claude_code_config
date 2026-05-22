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
索引：idx_{表名}_{字段名} | 唯一索引：uniq_{表名}_{字段名}
```

### 字段规范

```sql
-- 必备字段
id BIGINT PRIMARY KEY AUTO_INCREMENT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
is_deleted TINYINT(1) DEFAULT 0,  -- 软删除标记

-- 金额 DECIMAL(19,4) 不用 FLOAT/DOUBLE | 状态 TINYINT/ENUM | 时间 TIMESTAMP/DATETIME
```

### 索引原则

```
必须建索引：主键/外键 / WHERE 条件字段 / ORDER BY/GROUP BY 字段 / JOIN 关联字段
避免过度：单表索引≤5 / 复合索引遵循最左前缀 / 低选择性字段不建索引
```

## 查询规范

```sql
-- ❌ 禁止 SELECT *  →  ✅ 明确字段
-- ❌ 禁止拼接 SQL  →  ✅ 参数化查询
-- ❌ 禁止无 LIMIT 批量操作  →  ✅ 分批处理

-- 避免函数操作索引字段
-- ❌ WHERE DATE(created_at) = '2024-01-01'
-- ✅ WHERE created_at >= '2024-01-01' AND created_at < '2024-01-02'

-- 大数据量分页优化
-- ❌ SELECT * FROM orders LIMIT 10000, 20
-- ✅ SELECT * FROM orders WHERE id > 10000 ORDER BY id LIMIT 20
```

## Migration 规范

```sql
-- migrations/20240101_001_create_users.sql
-- +migrate Up: CREATE TABLE users (...)
-- +migrate Down: DROP TABLE IF EXISTS users
```

迁移原则：每个迁移可回滚 / 不修改已执行迁移 / 大表变更分步（加列 → 数据迁移 → 加约束） / 生产先 staging 验证 / 迁移前备份

## 事务规范

```sql
START TRANSACTION;
SET SESSION innodb_lock_wait_timeout = 5;
-- 业务操作 + 条件检查
-- 失败 ROLLBACK; 成功 COMMIT;
```

## 安全规范

| 风险         | 措施                      |
| ------------ | ------------------------- |
| SQL 注入     | 参数化查询、ORM、输入验证 |
| 敏感数据泄露 | 字段加密、日志脱敏        |
| 越权访问     | 行级权限检查              |
| 数据丢失     | 定期备份、主从复制        |

## 备份策略

```
全量备份：每日凌晨（保留30天）| 增量备份：每小时（保留7天）| binlog：实时（保留3天）
恢复演练：每季度一次
```
