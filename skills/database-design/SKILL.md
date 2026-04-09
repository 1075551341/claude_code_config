---
name: database-design
description: 当需要设计数据库表结构、规划索引策略、进行数据库架构设计、选择数据库类型时调用此技能。触发词：数据库设计、表结构设计、数据库架构、索引设计、ER图、数据库建模、表设计、字段设计、数据库选型。
---

# 数据库设计最佳实践

## 描述
数据库架构设计技能，涵盖关系型数据库（PostgreSQL/MySQL）表设计、
索引策略、范式与反范式、分库分表和 NoSQL 选型。

## 触发条件
当需要设计数据库表结构、优化查询性能、规划数据架构时使用。

## 技术选型

| 场景 | 推荐方案 | 理由 |
|------|----------|------|
| 通用业务系统 | PostgreSQL | 功能强大，JSON 支持，扩展丰富 |
| 高并发读写 | MySQL 8.0 | 成熟稳定，读写分离成熟 |
| 文档型存储 | MongoDB | Schema 灵活，适合内容管理 |
| 缓存/会话 | Redis | 亚毫秒延迟，数据结构丰富 |
| 搜索引擎 | Elasticsearch | 全文检索，聚合分析 |
| 时序数据 | TimescaleDB | 基于 PG，时序查询优化 |

## 表设计规范

```sql
-- 统一表结构模板
CREATE TABLE users (
    id          BIGSERIAL PRIMARY KEY,
    username    VARCHAR(50) NOT NULL UNIQUE,
    email       VARCHAR(255) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,  -- bcrypt 哈希存储
    status      SMALLINT DEFAULT 1,     -- 1:正常 0:禁用
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW(),
    deleted_at  TIMESTAMPTZ             -- 软删除
);

-- 索引设计
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_created ON users(created_at DESC);
```

## 命名规范

| 对象 | 规范 | 示例 |
|------|------|------|
| 表名 | snake_case 复数 | users, order_items |
| 列名 | snake_case | created_at, user_id |
| 主键 | id (BIGSERIAL) | id |
| 外键 | 表名单数_id | user_id, order_id |
| 索引 | idx_表名_列名 | idx_users_email |
| 唯一约束 | uq_表名_列名 | uq_users_username |

## 索引策略

1. **主键索引**：自增 BIGINT，避免 UUID 作主键（索引膨胀）
2. **查询索引**：WHERE 条件高频列必须建索引
3. **组合索引**：遵循最左前缀原则
4. **部分索引**：`WHERE deleted_at IS NULL` 排除软删除数据
5. **禁止全表扫描**：所有列表查询必须走索引

## ORM 选型

| 框架 | ORM | 特点 |
|------|-----|------|
| Node.js | Prisma | 类型安全，Migration 自动化 |
| Node.js | Drizzle | 轻量，SQL-like API |
| Python | SQLAlchemy | 功能最完整，灵活 |
| Python | Tortoise-ORM | 异步友好，Django-like |

## 最佳实践

1. **软删除**：业务表使用 deleted_at 字段，而非物理删除
2. **时间戳**：统一使用 TIMESTAMPTZ（带时区），UTC 存储
3. **枚举字段**：使用 SMALLINT + 注释，避免 ENUM 类型（修改困难）
4. **JSON 字段**：仅用于非结构化扩展数据，不替代关系设计
5. **Migration**：所有 Schema 变更必须通过 Migration 脚本，禁止直接改表
6. **备份策略**：自动化每日全量 + 实时 WAL 归档
