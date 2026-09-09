---
trigger: glob
description: 数据库设计、查询、迁移相关任务时启用
globs:
  - "**/*.{sql,prisma}"
  - "**/migrations/**"
---

# 数据库规则（薄层）

> 配合 CORE 使用。完整选型/备份策略 → `catalog/rules/RULES_DATABASE.md`。允许与 BACKEND glob 重叠。

## 表设计

```
表名：snake_case 复数（users, order_items）
主键：id
外键：{关联表}_id
索引：idx_{表}_{字段} | 唯一：uniq_{表}_{字段}
必备：created_at / updated_at；金额用 DECIMAL，不用 FLOAT
```

必须建索引：主键/外键、WHERE / ORDER BY / JOIN 字段。单表索引克制；复合索引最左前缀。

## 查询

- 禁止 `SELECT *`；禁止拼接 SQL（参数化 / ORM）
- 禁止无 LIMIT 批量操作
- 避免对索引字段做函数包装

## Migration

- 每个迁移可回滚；不修改已执行迁移
- 大表变更分步（加列 → 数据迁移 → 加约束）
- 生产先 staging；迁移前备份

## 事务

短事务；失败 ROLLBACK。锁等待须有超时。业务条件检查与写入同一事务。

## 安全

SQL 注入 → 参数化；敏感字段加密/日志脱敏；行级权限。详见 `rules/SECURITY.md`。
