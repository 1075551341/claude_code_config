---
name: mongodb
description: 操作MongoDB数据库
triggers: [操作MongoDB数据库, 编写MongoDB查询, 设计文档结构, 实现MongoDB最佳实践]
---

# MongoDB 数据库

## 核心能力

**MongoDB操作、文档设计、聚合查询、性能优化。**

---

## 适用场景

- MongoDB 数据操作
- 文档数据库设计
- 聚合查询
- NoSQL 开发

---

## 基本操作

### CRUD 操作

```javascript
// 插入
db.users.insertOne({ name: "John", age: 30 })
db.users.insertMany([
  { name: "Alice", age: 25 },
  { name: "Bob", age: 35 }
])

// 查询
db.users.findOne({ name: "John" })
db.users.find({ age: { $gt: 25 } })
db.users.find({}).sort({ age: -1 }).limit(10)

// 更新
db.users.updateOne(
  { name: "John" },
  { $set: { age: 31 } }
)
db.users.updateMany(
  { age: { $lt: 30 } },
  { $set: { status: "young" } }
)

// 删除
db.users.deleteOne({ name: "John" })
db.users.deleteMany({ status: "inactive" })
```

---

## 查询操作符

### 比较操作符

```javascript
{ age: { $eq: 30 } }     // 等于
{ age: { $ne: 30 } }     // 不等于
{ age: { $gt: 25 } }     // 大于
{ age: { $gte: 25 } }    // 大于等于
{ age: { $lt: 40 } }     // 小于
{ age: { $lte: 40 } }    // 小于等于
{ age: { $in: [25, 30, 35] } }  // 在列表中
{ age: { $nin: [25, 30] } }     // 不在列表中
```

### 逻辑操作符

```javascript
{ $and: [{ age: { $gt: 20 } }, { status: "active" }] }
{ $or: [{ role: "admin" }, { role: "moderator" }] }
{ $not: { age: { $gt: 30 } } }
```

### 数组操作符

```javascript
{ tags: "javascript" }           // 包含元素
{ tags: { $all: ["js", "ts"] } } // 包含所有
{ tags: { $size: 3 } }           // 数组长度
{ tags: { $elemMatch: { score: { $gt: 80 } } } }
```

---

## 聚合管道

```javascript
db.orders.aggregate([
  // 匹配
  { $match: { status: "completed" } },
  
  // 分组
  { $group: {
    _id: "$customerId",
    totalAmount: { $sum: "$amount" },
    orderCount: { $sum: 1 },
    avgAmount: { $avg: "$amount" }
  }},
  
  // 排序
  { $sort: { totalAmount: -1 } },
  
  // 限制
  { $limit: 10 },
  
  // 投影
  { $project: {
    customerId: "$_id",
    totalAmount: 1,
    _id: 0
  }}
])
```

### 常用聚合阶段

| 阶段 | 说明 |
|------|------|
| $match | 过滤文档 |
| $group | 分组聚合 |
| $sort | 排序 |
| $limit | 限制数量 |
| $skip | 跳过数量 |
| $project | 选择字段 |
| $lookup | 关联查询 |
| $unwind | 展开数组 |

---

## 索引优化

```javascript
// 创建索引
db.users.createIndex({ name: 1 })              // 单字段索引
db.users.createIndex({ name: 1, age: -1 })     // 复合索引
db.users.createIndex({ email: 1 }, { unique: true })  // 唯一索引
db.users.createIndex({ location: "2dsphere" }) // 地理索引

// 查看索引
db.users.getIndexes()

// 分析查询
db.users.find({ name: "John" }).explain("executionStats")

// 删除索引
db.users.dropIndex("name_1")
```

---

## Mongoose 使用

### 定义模型

```typescript
import mongoose from 'mongoose';

const userSchema = new mongoose.Schema({
  name: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  age: { type: Number, min: 0, max: 120 },
  role: { type: String, enum: ['user', 'admin'], default: 'user' },
  createdAt: { type: Date, default: Date.now }
});

// 索引
userSchema.index({ name: 1 });

// 虚拟属性
userSchema.virtual('isAdult').get(function() {
  return this.age >= 18;
});

export const User = mongoose.model('User', userSchema);
```

### CRUD 操作

```typescript
// 创建
const user = await User.create({ name: 'John', email: 'john@example.com' });

// 查询
const users = await User.find({ age: { $gt: 20 } })
  .sort({ createdAt: -1 })
  .limit(10)
  .lean();

// 更新
const updated = await User.findByIdAndUpdate(id, { age: 31 }, { new: true });

// 删除
await User.findByIdAndDelete(id);
```

---

## 注意事项

```
必须:
- 创建合适索引
- 限制返回字段
- 使用连接池
- 监控性能指标

避免:
- 大量删除操作
- 过深嵌套文档
- 无索引查询
- 过大文档(>16MB)
```

---

## 相关技能

- `sql-database` - SQL 数据库
- `database-design` - 数据库设计
- `nodejs-backend` - Node.js 后端