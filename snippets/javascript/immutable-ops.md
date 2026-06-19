# 不可变操作模板

> 遵守 CORE.md：不可变优先，数组用展开/map/filter，不原地修改

```js
// ❌ 原地修改
items.push(newItem);
items.sort((a, b) => a.name.localeCompare(b.name));

// ✅ 不可变
const updated = [...items, newItem];
const sorted = [...items].sort((a, b) => a.name.localeCompare(b.name));

// ❌ 原地修改对象
obj.status = 'active';

// ✅ 展开
const updated = { ...obj, status: 'active' };
```
