---
name: js-code-snippets
description: 当需要快速查找JavaScript/ES6代码片段、常用代码模式、代码技巧参考时调用此技能。触发词：JS代码片段、JavaScript技巧、ES6技巧、代码模式、JS实用代码、JavaScript速查、JS常用方法、代码技巧。
---

# JavaScript/ES6 代码片段

## 核心能力

**常用代码模式速查、ES6 语法技巧、实用片段参考。**

---

## 适用场景

- 快速查找代码模式
- ES6 语法参考
- 常用操作速查
- 代码技巧学习

---

## 数组操作

### 去重

```javascript
// Set 去重
const unique = [...new Set(arr)]

// filter 去重
const unique = arr.filter((v, i) => arr.indexOf(v) === i)
```

### 排序

```javascript
// 数字排序
arr.sort((a, b) => a - b)

// 对象排序
arr.sort((a, b) => a.key.localeCompare(b.key))
```

### 分组

```javascript
// reduce 分组
const grouped = arr.reduce((acc, item) => {
  const key = item.category
  acc[key] = acc[key] || []
  acc[key].push(item)
  return acc
}, {})
```

### 扁平化

```javascript
// flat 一层
arr.flat()

// flat 全部
arr.flat(Infinity)
```

---

## 对象操作

### 合并

```javascript
// spread 合并
const merged = { ...obj1, ...obj2 }

// Object.assign
const merged = Object.assign({}, obj1, obj2)
```

### 深拷贝

```javascript
// JSON 方式（简单对象）
const deepCopy = JSON.parse(JSON.stringify(obj))

// structuredClone（现代浏览器）
const deepCopy = structuredClone(obj)
```

### 属性选取

```javascript
// 选取部分属性
const picked = ({ a, b }) => ({ a, b })(obj)

// 解构选取
const { a, b, ...rest } = obj
```

---

## 字符串操作

### 模板字符串

```javascript
const str = `Hello, ${name}!`
const multiline = `
  Line 1
  Line 2
`
```

### 常用方法

```javascript
// 包含检查
str.includes('substring')

// 重复
str.repeat(3)

// 填充
str.padStart(8, '0')
str.padEnd(8, '0')

// 去空白
str.trim()
str.trimStart()
str.trimEnd()
```

---

## 函数技巧

### 箭头函数

```javascript
// 单表达式
const add = (a, b) => a + b

// 返回对象
const makeObj = (x) => ({ value: x })

// 解构参数
const fn = ({ a, b }) => a + b
```

### 默认参数

```javascript
const fn = (a = 0, b = 'default') => {
  // ...
}
```

### Rest/Spread

```javascript
// Rest 收集
const fn = (...args) => args.reduce((a, b) => a + b)

// Spread 展开
const arr2 = [...arr1, newItem]
```

---

## 异步处理

### Promise

```javascript
// 基本
fetch(url)
  .then(res => res.json())
  .then(data => console.log(data))
  .catch(err => console.error(err))

// 并行
Promise.all([p1, p2, p3])
Promise.race([p1, p2])
```

### async/await

```javascript
// 基本
async function getData() {
  try {
    const res = await fetch(url)
    const data = await res.json()
    return data
  } catch (err) {
    console.error(err)
  }
}

// 并行
async function getAll() {
  const [d1, d2] = await Promise.all([fetch1(), fetch2()])
}
```

---

## 解构赋值

### 数组解构

```javascript
const [first, second] = arr
const [first, ...rest] = arr
const [a, b, c = 0] = arr  // 默认值
```

### 对象解构

```javascript
const { name, age } = obj
const { name: n, age: a } = obj  // 重命名
const { a, b, ...rest } = obj
```

---

## Map/Set

### Map

```javascript
const map = new Map()
map.set('key', 'value')
map.get('key')
map.has('key')
map.delete('key')

// 遍历
for (const [k, v] of map) {}
map.forEach((v, k) => {})
```

### Set

```javascript
const set = new Set([1, 2, 3])
set.add(4)
set.has(1)
set.delete(1)

// 遍历
for (const v of set) {}
set.forEach(v => {})
```

---

## 常用工具函数

### 类型检查

```javascript
typeof x === 'string'
Array.isArray(arr)
Number.isNaN(x)
```

### 数值处理

```javascript
// 安全整数
Number.isSafeInteger(x)

// 取整
Math.trunc(1.9)  // 1
Math.floor(1.9)  // 1
Math.ceil(1.1)   // 2
Math.round(1.5)  // 2
```

---

## 注意事项

```
避免：
- var（使用 let/const）
- ==（使用 ===）
- for...in 数组（使用 for...of）
- 修改原型链
```

---

## 相关技能

- `typescript` - TypeScript 类型
- `react-component` - React 开发
- `nodejs-backend` - Node.js 后端