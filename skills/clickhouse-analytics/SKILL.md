---
name: clickhouse-analytics
description: 当需要使用ClickHouse进行分析查询、处理大数据分析、实现实时数据统计时调用此技能。触发词：ClickHouse、ClickHouse分析、大数据分析、实时分析、OLAP数据库、列式数据库。
---

# ClickHouse 分析

## 核心能力

**ClickHouse大数据分析、实时查询优化、OLAP数据库操作。**

---

## 适用场景

- 大数据分析查询
- 实时数据统计
- OLAP数据仓库
- 日志分析系统

---

## 基础概念

### 架构特点

```markdown
列式存储：
- 数据按列存储
- 高压缩比
- 只读取需要的列

向量化执行：
- SIMD指令优化
- 批量数据处理
- CPU缓存友好

分布式架构：
- 分片（Shard）
- 副本（Replica）
- 分布式表引擎
```

### 表引擎

```markdown
MergeTree系列：
- MergeTree：最常用，支持索引
- ReplicatedMergeTree：支持复制
- SummingMergeTree：预聚合求和
- AggregatingMergeTree：预聚合统计
- ReplacingMergeTree：去重
- CollapsingMergeTree：行折叠

Log系列：
- TinyLog：简单写入
- StripeLog：带压缩
- Log：带标记

集成引擎：
- MySQL：连接MySQL
- PostgreSQL：连接PostgreSQL
- Kafka：消费Kafka
- HDFS：读取HDFS
- S3：读取S3
```

---

## 数据操作

### 建表语句

```sql
-- 创建MergeTree表
CREATE TABLE events (
    event_date Date,
    event_time DateTime,
    user_id UInt64,
    event_type String,
    event_data String,
    platform LowCardinality(String)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, user_id, event_time)
SETTINGS index_granularity = 8192;

-- 创建分布式表
CREATE TABLE events_all ON CLUSTER cluster_name (
    -- 同本地表结构
)
ENGINE = Distributed(cluster_name, database, events, rand());

-- 创建复制表
CREATE TABLE events_replicated (
    -- 同上结构
)
ENGINE = ReplicatedMergeTree('/clickhouse/tables/{database}/events', 'replica1')
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, user_id);
```

### 数据写入

```sql
-- INSERT语句
INSERT INTO events (event_date, event_time, user_id, event_type, event_data, platform)
VALUES
    ('2025-01-15', '2025-01-15 10:00:00', 1001, 'click', '{"x":100}', 'web'),
    ('2025-01-15', '2025-01-15 10:01:00', 1002, 'view', '{"page":"home"}', 'app');

-- 从文件导入
INSERT INTO events
SELECT *
FROM file('events.csv', CSVWithNames);

-- 从其他表导入
INSERT INTO events
SELECT * FROM staging_events WHERE event_date >= '2025-01-01';
```

---

## 分析查询

### 聚合查询

```sql
-- 基础聚合
SELECT
    event_date,
    count() AS total_events,
    uniq(user_id) AS unique_users,
    countIf(event_type = 'click') AS clicks
FROM events
WHERE event_date >= '2025-01-01'
GROUP BY event_date
ORDER BY event_date;

-- 多维度分析
SELECT
    platform,
    event_type,
    count() AS cnt,
    uniq(user_id) AS users
FROM events
WHERE event_date BETWEEN '2025-01-01' AND '2025-01-31'
GROUP BY platform, event_type
WITH TOTALS
ORDER BY cnt DESC;

-- 滚动窗口分析
SELECT
    toStartOfDay(event_time) AS day,
    count() AS events,
    uniqExact(user_id) AS users,
    sumIf(1, event_type = 'purchase') AS purchases
FROM events
WHERE event_time >= now() - INTERVAL 30 DAY
GROUP BY day
ORDER BY day;
```

### 留存分析

```sql
-- N日留存
SELECT
    cohort_date,
    count() AS cohort_size,
    sumIf(1, days_since_first = 1) AS day1_retention,
    sumIf(1, days_since_first = 7) AS day7_retention,
    sumIf(1, days_since_first = 30) AS day30_retention
FROM (
    SELECT
        first_date AS cohort_date,
        user_id,
        dateDiff('day', first_date, event_date) AS days_since_first
    FROM (
        SELECT
            user_id,
            min(event_date) AS first_date,
            event_date
        FROM events
        GROUP BY user_id, event_date
    )
)
GROUP BY cohort_date
ORDER BY cohort_date;

-- 漏斗分析
SELECT
    level,
    count() AS users,
    round(count() / max(count()) OVER (), 4) AS conversion_rate
FROM (
    SELECT
        user_id,
        arrayJoin([1, 2, 3, 4]) AS level,
        hasCompletedLevel(user_id, level) AS completed
    FROM (
        SELECT DISTINCT user_id FROM events WHERE event_date >= '2025-01-01'
    )
    WHERE completed = 1
)
GROUP BY level
ORDER BY level;
```

### 用户行为分析

```sql
-- 用户路径分析
SELECT
    groupArray(event_type) AS path,
    count() AS cnt
FROM (
    SELECT
        user_id,
        event_type,
        row_number() OVER (PARTITION BY user_id ORDER BY event_time) AS rn
    FROM events
    WHERE event_date = '2025-01-15'
    LIMIT 5 BY user_id
)
GROUP BY path
ORDER BY cnt DESC
LIMIT 20;

-- 会话分析
SELECT
    session_duration_sec,
    count() AS sessions,
    round(avg(events_per_session), 2) AS avg_events
FROM (
    SELECT
        user_id,
        dateDiff('second', min(event_time), max(event_time)) AS session_duration_sec,
        count() AS events_per_session
    FROM events
    WHERE event_date = '2025-01-15'
    GROUP BY user_id, toStartOfInterval(event_time, INTERVAL 30 MINUTE)
)
GROUP BY session_duration_sec
ORDER BY session_duration_sec;
```

---

## 性能优化

### 索引优化

```sql
-- 主键索引（ORDER BY）
ORDER BY (event_date, user_id, event_time)

-- 跳数索引
ALTER TABLE events ADD INDEX idx_type event_type TYPE bloom_filter GRANULARITY 4;
ALTER TABLE events ADD INDEX idx_data event_data TYPE tokenbf_v1(512, 3, 0) GRANULARITY 4;

-- 物化视图
CREATE MATERIALIZED VIEW events_daily_mv
ENGINE = SummingMergeTree()
ORDER BY (event_date, event_type)
AS SELECT
    event_date,
    event_type,
    count() AS event_count,
    uniqState(user_id) AS unique_users
FROM events
GROUP BY event_date, event_type;

-- 查询物化视图
SELECT
    event_date,
    event_type,
    event_count,
    uniqMerge(unique_users) AS users
FROM events_daily_mv
GROUP BY event_date, event_type, event_count;
```

### 查询优化

```sql
-- 使用PREWHERE过滤（只适用于MergeTree）
SELECT count()
FROM events
PREWHERE event_date = '2025-01-15'
WHERE event_type = 'click';

-- 限制读取列
SELECT user_id, event_type
FROM events
WHERE event_date = '2025-01-15'
LIMIT 1000;

-- 使用SAMPLE采样
SELECT count() AS estimate_total
FROM events
SAMPLE 0.1;  -- 10%采样

-- 使用FINAL（谨慎使用）
SELECT *
FROM events
FINAL
WHERE event_date = '2025-01-15';
```

---

## 常用函数

### 聚合函数

```sql
-- 计数
count()          -- 总数
countIf(x > 0)   -- 条件计数
uniq(x)          -- 近似去重
uniqExact(x)     -- 精确去重
uniqCombined(x)  -- 组合去重

-- 统计
sum(x)
avg(x)
min(x)
max(x)
median(x)
quantile(0.95)(x)  -- 分位数

-- 数组聚合
groupArray(x)    -- 转为数组
groupUniqArray(x) -- 去重数组
```

### 时间函数

```sql
-- 时间转换
toDate('2025-01-15')
toDateTime('2025-01-15 10:00:00')
toUnixTimestamp(now())

-- 时间截取
toStartOfDay(event_time)
toStartOfHour(event_time)
toStartOfMinute(event_time)
toStartOfMonth(event_date)

-- 时间计算
dateAdd(DAY, 7, event_date)
dateDiff('day', start_date, end_date)
now() - INTERVAL 7 DAY
```

### 字符串函数

```sql
-- 字符串操作
concat(s1, s2)
substring(s, offset, length)
lower(s)
upper(s)
trim(s)

-- 正则匹配
match(s, pattern)
extract(s, pattern)
replaceRegexpAll(s, pattern, replacement)
```

---

## 集成配置

### Python客户端

```python
from clickhouse_driver import Client

# 连接客户端
client = Client('localhost', port=9000)

# 执行查询
result = client.execute('''
    SELECT
        event_date,
        count() AS cnt
    FROM events
    GROUP BY event_date
    ORDER BY event_date
''')

# 插入数据
client.execute('''
    INSERT INTO events VALUES
''', [
    ('2025-01-15', '2025-01-15 10:00:00', 1001, 'click', '{}', 'web'),
    ('2025-01-15', '2025-01-15 10:01:00', 1002, 'view', '{}', 'app')
])
```

---

## 注意事项

```
必须：
- 合理设计ORDER BY
- 利用分区裁剪
- 使用PREWHERE过滤
- 控制并发查询

避免：
- 大量小INSERT
- SELECT * 查询
- 不合理的JOIN
- 过多列的ORDER BY
```

---

## 相关技能

- `sql-database` - SQL数据库
- `data-analysis` - 数据分析
- `mongodb` - MongoDB