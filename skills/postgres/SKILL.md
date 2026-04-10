---
name: postgres
description: PostgreSQL数据库操作，包括查询优化、索引设计、性能调优。触发词：PostgreSQL、postgres、SQL优化、数据库查询、索引设计、性能调优。
---

# PostgreSQL 数据库

## 核心能力

- SQL查询编写和优化
- 索引设计和策略
- 查询性能分析
- 数据库架构设计
- 备份和恢复

## 常用操作

### 查询优化

```sql
-- 使用EXPLAIN分析查询计划
EXPLAIN ANALYZE SELECT * FROM table WHERE condition;

-- 创建索引
CREATE INDEX idx_name ON table(column);

-- 查看索引使用情况
SELECT * FROM pg_stat_user_indexes;
```

### 性能监控

```sql
-- 查看慢查询
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;

-- 查看表大小
SELECT pg_size_pretty(pg_total_relation_size('table_name'));
```

## 最佳实践

- 为WHERE、JOIN、ORDER BY字段创建索引
- 避免SELECT *，只查询需要的字段
- 使用连接池管理连接
- 定期VACUUM和ANALYZE
