---
name: code-refactor
description: 当需要重构代码、优化代码结构、消除重复代码、改进代码设计时调用此技能。触发词：代码重构、重构、代码优化、代码整理、消除重复、代码改进、设计模式应用、函数提取、类拆分。
---

# 代码重构

## 重构原则

### 核心原则

1. **小步重构**：每次只做一个小改动，确保每步都可运行
2. **测试先行**：重构前确保有足够的测试覆盖
3. **保持行为不变**：重构不改变代码的外部行为
4. **持续集成**：频繁提交，便于回滚

### 重构时机

| 信号 | 重构方向 |
|------|----------|
| 重复代码 | 提取公共函数/类 |
| 过长函数 | 拆分为小函数 |
| 过大类 | 提取职责，拆分类 |
| 过长参数列表 | 封装为对象 |
| 发散式变化 | 拆分职责 |
| 霰弹式修改 | 合并相关逻辑 |
| 依恋情结 | 移动方法到数据所在类 |

## 常用重构手法

### 1. 提取函数

```typescript
// ❌ 重构前：内联逻辑
function printOwing(invoice) {
  let outstanding = 0
  console.log('***********************')
  console.log('*** Customer Owes ***')
  console.log('***********************')

  for (const o of invoice.orders) {
    outstanding += o.amount
  }

  console.log(`name: ${invoice.customer}`)
  console.log(`amount: ${outstanding}`)
}

// ✅ 重构后：提取函数
function printOwing(invoice) {
  printBanner()
  const outstanding = calculateOutstanding(invoice)
  printDetails(invoice, outstanding)
}

function printBanner() {
  console.log('***********************')
  console.log('*** Customer Owes ***')
  console.log('***********************')
}

function calculateOutstanding(invoice) {
  return invoice.orders.reduce((sum, o) => sum + o.amount, 0)
}

function printDetails(invoice, outstanding) {
  console.log(`name: ${invoice.customer}`)
  console.log(`amount: ${outstanding}`)
}
```

### 2. 提取变量

```typescript
// ❌ 重构前
if (platform.toUpperCase().indexOf('MAC') > -1 &&
    browser.toUpperCase().indexOf('IE') > -1 &&
    initialized && resize > 0) {
  // ...
}

// ✅ 重构后
const isMacOS = platform.toUpperCase().indexOf('MAC') > -1
const isIE = browser.toUpperCase().indexOf('IE') > -1
const wasResized = resize > 0

if (isMacOS && isIE && initialized && wasResized) {
  // ...
}
```

### 3. 封装字段

```typescript
// ❌ 重构前：暴露内部数据
class Person {
  name: string
}

// ✅ 重构后：封装访问
class Person {
  private _name: string

  get name(): string {
    return this._name
  }

  set name(value: string) {
    if (value.length < 2) {
      throw new Error('Name too short')
    }
    this._name = value
  }
}
```

### 4. 以多态取代条件表达式

```typescript
// ❌ 重构前：switch/if-else 链
function calculateSalary(employee) {
  switch (employee.type) {
    case 'ENGINEER':
      return employee.monthlySalary
    case 'MANAGER':
      return employee.monthlySalary + employee.bonus
    case 'SALESMAN':
      return employee.monthlySalary + employee.commission
  }
}

// ✅ 重构后：多态
abstract class Employee {
  abstract calculateSalary(): number
}

class Engineer extends Employee {
  calculateSalary() {
    return this.monthlySalary
  }
}

class Manager extends Employee {
  calculateSalary() {
    return this.monthlySalary + this.bonus
  }
}

class Salesman extends Employee {
  calculateSalary() {
    return this.monthlySalary + this.commission
  }
}
```

### 5. 策略模式重构

```typescript
// ❌ 重构前：硬编码逻辑
function calculateShipping(order) {
  if (order.type === 'standard') {
    return order.weight * 1.5
  } else if (order.type === 'express') {
    return order.weight * 3
  } else if (order.type === 'overnight') {
    return order.weight * 5 + 10
  }
}

// ✅ 重构后：策略模式
const shippingStrategies = {
  standard: (order) => order.weight * 1.5,
  express: (order) => order.weight * 3,
  overnight: (order) => order.weight * 5 + 10
}

function calculateShipping(order) {
  return shippingStrategies[order.type](order)
}
```

## 重构安全策略

### 1. 测试覆盖

```typescript
// 重构前确保有测试
describe('calculateSalary', () => {
  it('should calculate engineer salary', () => {
    const engineer = { type: 'ENGINEER', monthlySalary: 5000 }
    expect(calculateSalary(engineer)).toBe(5000)
  })

  it('should calculate manager salary with bonus', () => {
    const manager = { type: 'MANAGER', monthlySalary: 6000, bonus: 1000 }
    expect(calculateSalary(manager)).toBe(7000)
  })
})
```

### 2. 渐进式重构

```typescript
// 步骤 1：添加新实现，保留旧实现
function processLegacy(data) {
  // 旧逻辑
}

function processNew(data) {
  // 新逻辑
}

function process(data) {
  // 使用 feature flag 切换
  if (featureFlags.useNewProcess) {
    return processNew(data)
  }
  return processLegacy(data)
}

// 步骤 2：验证新实现正确
// 步骤 3：删除旧实现
```

### 3. IDE 重构工具

| 功能 | VS Code 快捷键 |
|------|---------------|
| 重命名符号 | F2 |
| 提取函数 | Ctrl+Shift+R |
| 提取变量 | Ctrl+Shift+V |
| 移动到新文件 | Ctrl+. |

## 重构检查清单

- [ ] 有足够的测试覆盖
- [ ] 小步进行，每步可编译运行
- [ ] 保持功能不变
- [ ] 代码更易理解
- [ ] 没有引入重复
- [ ] 提交信息清晰
- [ ] 团队成员理解变更