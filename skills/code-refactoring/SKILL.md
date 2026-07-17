---
name: code-refactoring
description: '代码重构技能：在不改变代码行为的前提下优化代码结构。包括抽取函数、重命名变量、拆分超大函数、提升类型安全、消除代码异味、应用设计模式等。适用于渐进式代码改进。**触发场景**：当用户说"重构"、"重构这个函数"、"优化这个函数"、"清理这段代码"、"拆分过长函数"、"优化类结构"、"消除代码异味"、"使用设计模式重构"、"类型不安全"、"参数过多"等类似表达时使用此技能'
license: Huawei Inner Source License (HISL)
metadata:
  version: 1.0.0
loading_tier: L3
disable-model-invocation: true
---

# Code Refactoring

## Overview

在不影响代码本身逻辑的前提下重构代码，重构超大函数，提升类型安全，消除代码异味和使用合适的设计模式。

**关键要求**：
- 重构前必须先运行单元测试建立基线，重构后必须再次运行所有测试确保通过。
- 如果用户没有单元测试用例，提醒用户添加，但是不阻塞用户接下来的重构操作，提示后继续重构。
- 全程必须提供风险评估和收益评估报告。
- 如果用户单次重构文件超过3个，或者单次重构超过2000行，那么就提醒用户是否继续重构。

## When to Use
- 代码难以理解或维护
- 函数/类过大（函数超过50行）
- 需要处理代码异味
- 由于代码结构问题导致添加功能困难
- 用户要求"清理代码"、"重构"、"改进代码"
---
## Refactoring Principles
### The Golden Rules
1. **行为保持不变** - 重构不改变代码做什么，只改变如何做
2. **小步前进** - 做微小的改动，每步之后测试
3. **修改需要版本控制** - 在每个安全状态前后提交
4. **测试至关重要** - 没有测试，你是在编辑而不是重构
5. **一次只做一件事** - 不要混合重构和功能变更
### When NOT to Refactor
```
- 稳定运行了很久的代码，不要轻易重构
- 没有测试用例的代码不要重构（先添加测试）
- 需要非常清晰的重构目标，否则不要重构
- 当你处于紧迫的截止日期时
- 需要明确的重构目的
```
---
## Features
### 特性集

- **抽取公共方法**：避免一个函数过长，一个函数不要超过50行代码
- **类型安全检测**：检测到不安全的类型转换要重构
- **类型匹配检查**：能够检测到类型不匹配风险，例如返回了long类型的数据赋值给了int类型的变量
- **安全重构**：要一步一步解决，持续测试和验证
---

## Common Code Smells & Fixes

### 1. 大函数重构 (Long Method/Function)

将函数重构到50行代码以内，超过50行的函数要进行进一步抽象。

#### 重构执行流程（必须执行）

当用户要求"优化函数"、"重构函数"时，必须按以下步骤执行：

##### 步骤 0：重构范围检查（必须）
```
1. 识别用户要求重构的所有文件
2. 统计文件数量和总代码行数
3. 如果文件数量超过3个或总代码行数超过2000行:
   - 使用question工具询问用户："检测到重构范围较大（XX个文件/XX行代码），是否继续？"
   - 选项：
     * "继续重构" - 继续执行后续步骤
     * "取消重构" - 终止重构操作
   - 根据用户选择决定是否继续
4. 如果用户选择继续或范围未超标，则继续执行后续步骤
```

##### 步骤 1：运行重构前测试（必须）
```
1. 找到目标函数对应的测试文件
2. 运行单元测试并记录结果
3. 如果测试失败，报告用户并让用户确认风险，继续重构
4. 如果没有测试用例，提示用户先补充测试
```

##### 步骤 2：风险评估（必须）
在重构前，必须进行风险评估并输出报告：
```markdown
## 重构风险评估报告

| 评估项 | 评估结果 | 风险等级 |
|--------|----------|----------|
| 代码行数 | XX行 | 高/中/低 |
| 圈复杂度 | XX | 高/中/低 |
| 依赖深度 | XX层 | 高/中/低 |
| 测试覆盖率 | XX% | 高/中/低 |
| 代码变更频率 | 近6个月XX次 | 高/中/低 |

**总体风险等级**：[高/中/低]
**重构建议**：[可进行/需先补充测试/建议暂缓]
```

##### 步骤 3：分步重构
```
1. 每次重构不超过20行代码变化
2. 每完成一步立即运行相关测试
3. 测试通过后再进行下一步
4. 如果测试失败，立即回滚
```

##### 步骤 4：运行重构后测试（必须）
```
1. 运行完整的单元测试套件，如果没有，提醒用户补充，但是继续重构下去
2. 记录测试结果
3. 如果测试失败，必须回滚并重新评估
4. 确保所有测试通过才能交付
```

##### 步骤 5：收益评估（必须）
重构完成后，必须输出收益评估报告：

```markdown
## 重构收益评估报告

| 收益类型 | 重构前 | 重构后 | 改善幅度 |
|----------|--------|--------|----------|
| 函数行数 | XX行 | XX行 | -XX% |
| 圈复杂度 | XX | XX | -XX% |
| 可测试性 | 低/中/高 | 低/中/高 | 提升XX级 |
| 可维护性 | 低/中/高 | 低/中/高 | 提升XX级 |

**总体收益**：[显著/中等/有限]
```
---
```diff
# BAD: 200行的大函数，什么都做
- async function processOrder(orderId) {
-   // 50行: 获取订单
-   // 30行: 验证订单
-   // 40行: 计算价格
-   // 30行: 更新库存
-   // 20行: 创建发货
-   // 30行: 发送通知
- }

# GOOD: 拆分为专注的小函数
+ async function processOrder(orderId) {
+   const order = await fetchOrder(orderId);
+   validateOrder(order);
+   const pricing = calculatePricing(order);
+   await updateInventory(order);
+   const shipment = await createShipment(order);
+   await sendNotifications(order, pricing, shipment);
+   return { order, pricing, shipment };
+ }
```

### 2. 抽取公共方法去除重复代码 (Duplicated Code)

```diff
# BAD: 多处相同的逻辑
- function calculateUserDiscount(user) {
-   if (user.membership === 'gold') return user.total * 0.2;
-   if (user.membership === 'silver') return user.total * 0.1;
-   return 0;
- }
-
- function calculateOrderDiscount(order) {
-   if (order.user.membership === 'gold') return order.total * 0.2;
-   if (order.user.membership === 'silver') return order.total * 0.1;
-   return 0;
- }

# GOOD: 提取公共逻辑
+ function getMembershipDiscountRate(membership) {
+   const rates = { gold: 0.2, silver: 0.1 };
+   return rates[membership] || 0;
+ }
+
+ function calculateUserDiscount(user) {
+   return user.total * getMembershipDiscountRate(user.membership);
+ }
+
+ function calculateOrderDiscount(order) {
+   return order.total * getMembershipDiscountRate(order.user.membership);
+ }
```

### 3. 大类/大模块重构 (Large Class/Module)

符合SOLID之单一职责原则。

```diff
# BAD: 上帝对象，知道太多
- class UserManager {
-   createUser() { /* ... */ }
-   updateUser() { /* ... */ }
-   deleteUser() { /* ... */ }
-   sendEmail() { /* ... */ }
-   generateReport() { /* ... */ }
-   handlePayment() { /* ... */ }
-   validateAddress() { /* ... */ }
-   // 50 more methods...
- }

# GOOD: 每个类单一职责
+ class UserService {
+   create(data) { /* ... */ }
+   update(id, data) { /* ... */ }
+   delete(id) { /* ... */ }
+ }
+
+ class EmailService {
+   send(to, subject, body) { /* ... */ }
+ }
+
+ class ReportService {
+   generate(type, params) { /* ... */ }
+ }
+
+ class PaymentService {
+   process(amount, method) { /* ... */ }
+ }
```

### 4. 重构过长参数列表 (Long Parameter List)
函数输入参数超过5个，将参数组合成一个对象进行输入。

```diff
# BAD: 参数过多
- function createUser(email, password, name, age, address, city, country, phone) {
-   /* ... */
- }

# GOOD: 将相关参数分组
+ interface UserData {
+   email: string;
+   password: string;
+   name: string;
+   age?: number;
+   address?: Address;
+   phone?: string;
+ }
+
+ function createUser(data: UserData) {
+   /* ... */
+ }

# EVEN BETTER: 使用建造者模式处理复杂构造
+ const user = UserBuilder
+   .email('test@example.com')
+   .password('secure123')
+   .name('Test User')
+   .address(address)
+   .build();
```

### 5. 避免特性依赖 (Feature Envy)

不要违背面向对象设计中的"数据与行为绑定"原则。

```diff
# BAD: 方法使用另一个对象的数据多于自己的
- class Order {
-   calculateDiscount(user) {
-     if (user.membershipLevel === 'gold') {
+       return this.total * 0.2;
+     }
+     if (user.accountAge > 365) {
+       return this.total * 0.1;
+     }
+     return 0;
+   }
+ }

# GOOD: 将逻辑移到拥有数据的对象
+ class User {
+   getDiscountRate(orderTotal) {
+     if (this.membershipLevel === 'gold') return 0.2;
+     if (this.accountAge > 365) return 0.1;
+     return 0;
+   }
+ }
+
+ class Order {
+   calculateDiscount(user) {
+     return this.total * user.getDiscountRate(this.total);
+   }
+ }
```

### 6. 基本类型偏执 (Primitive Obsession)

引入领域类型实现面向对象编程

```diff
# BAD: 使用基本类型表示领域概念
- function sendEmail(to, subject, body) { /* ... */ }
- sendEmail('user@example.com', 'Hello', '...');

- function createPhone(country, number) {
-   return `${country}-${number}`;
- }

# GOOD: 使用领域类型
+ class Email {
+   private constructor(public readonly value: string) {
+     if (!Email.isValid(value)) throw new Error('Invalid email');
+   }
+   static create(value: string) { return new Email(value); }
+   static isValid(email: string) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email); }
+ }
+
+ class PhoneNumber {
+   constructor(
+     public readonly country: string,
+     public readonly number: string
+   ) {
+     if (!PhoneNumber.isValid(country, number)) throw new Error('Invalid phone');
+   }
+   toString() { return `${this.country}-${this.number}`; }
+   static isValid(country: string, number: string) { /* ... */ }
+ }
+
+ // Usage
+ const email = Email.create('user@example.com');
+ const phone = new PhoneNumber('1', '555-1234');
```

### 7. 避免魔鬼数字 (Magic Numbers/Strings)

```diff
# BAD: 未解释的值
- if (user.status === 2) { /* ... */ }
- const discount = total * 0.15;
- setTimeout(callback, 86400000);

# GOOD: 命名常量
+ const UserStatus = {
+   ACTIVE: 1,
+   INACTIVE: 2,
+   SUSPENDED: 3
+ } as const;
+
+ const DISCOUNT_RATES = {
+   STANDARD: 0.1,
+   PREMIUM: 0.15,
+   VIP: 0.2
+ } as const;
+
+ const ONE_DAY_MS = 24 * 60 * 60 * 1000;
+
+ if (user.status === UserStatus.INACTIVE) { /* ... */ }
+ const discount = total * DISCOUNT_RATES.PREMIUM;
+ setTimeout(callback, ONE_DAY_MS);
```

### 8. 避免嵌套条件 (Nested Conditionals)

使用卫语句实现扁平化。

```diff
# BAD: 箭头代码
- function process(order) {
-   if (order) {
-     if (order.user) {
-       if (order.user.isActive) {
-         if (order.total > 0) {
-           return processOrder(order);
+         } else {
+           return { error: 'Invalid total' };
+         }
+       } else {
+         return { error: 'User inactive' };
+       }
+     } else {
+       return { error: 'No user' };
+     }
+   } else {
+     return { error: 'No order' };
+   }
+ }

# GOOD: 卫语句 / 提前返回
+ function process(order) {
+   if (!order) return { error: 'No order' };
+   if (!order.user) return { error: 'No user' };
+   if (!order.user.isActive) return { error: 'User inactive' };
+   if (order.total <= 0) return { error: 'Invalid total' };
+   return processOrder(order);
+ }

# EVEN BETTER: 使用Result类型
+ function process(order): Result<ProcessedOrder, Error> {
+   return Result.combine([
+     validateOrderExists(order),
+     validateUserExists(order),
+     validateUserActive(order.user),
+     validateOrderTotal(order)
+   ]).flatMap(() => processOrder(order));
+ }
```

### 9. 删除不用的代码 (Delete Unused code)

在删除之前要提示用户确认。

```diff
# BAD: 未使用的代码残留
- function oldImplementation() { /* ... */ }
- const DEPRECATED_VALUE = 5;
- import { unusedThing } from './somewhere';
- // 注释掉的代码
- // function oldCode() { /* ... */ }

# GOOD: 删除它
+ // 删除未使用的函数、导入和注释代码
+ // 如果需要，git历史中有记录
```

**删除流程：**
1. 扫描代码库，识别未被引用的代码
2. 向用户展示待删除的代码列表
3. 用户确认后执行删除
4. 运行测试确保删除安全

### 10. 提高封装性 (Inappropriate Intimacy)

符合高内聚，低耦合设计原则。

```diff
# BAD: 一个类深入访问另一个类
- class OrderProcessor {
-   process(order) {
-     order.user.profile.address.street;  // 过于亲密
-     order.repository.connection.config;  // 破坏封装
+   }
+ }

# GOOD: 询问，不要告知
+ class OrderProcessor {
+   process(order) {
+     order.getShippingAddress();  // Order知道如何获取
+     order.save();  // Order知道如何保存自己
+   }
+ }
```

---

## Type Safety Refactoring

### 类型安全检测

检测不安全的类型转换和类型不匹配风险。

```diff
# BAD: 不安全的类型转换
- const value: any = getData();
- const result = value as SomeType;

# GOOD: 安全的类型检查
+ const value: unknown = getData();
+ if (isSomeType(value)) {
+   const result = value;
+ }

# BAD: 类型不匹配风险
- function getId(): long { return 12345678901234L; }
- const id: int = getId();  // 潜在的精度丢失

# GOOD: 使用正确的类型
+ function getId(): long { return 12345678901234L; }
+ const id: long = getId();  // 类型匹配
```

---

## Design Patterns for Refactoring

### Strategy Pattern

```diff
# Before: 条件逻辑
- function calculateShipping(order, method) {
-   if (method === 'standard') {
-     return order.total > 50 ? 0 : 5.99;
-   } else if (method === 'express') {
-     return order.total > 100 ? 9.99 : 14.99;
+   } else if (method === 'overnight') {
+     return 29.99;
+   }
+ }

# After: 策略模式
+ interface ShippingStrategy {
+   calculate(order: Order): number;
+ }
+
+ class StandardShipping implements ShippingStrategy {
+   calculate(order: Order) {
+     return order.total > 50 ? 0 : 5.99;
+   }
+ }
+
+ class ExpressShipping implements ShippingStrategy {
+   calculate(order: Order) {
+     return order.total > 100 ? 9.99 : 14.99;
+   }
+ }
+
+ class OvernightShipping implements ShippingStrategy {
+   calculate(order: Order) {
+     return 29.99;
+   }
+ }
+
+ function calculateShipping(order: Order, strategy: ShippingStrategy) {
+   return strategy.calculate(order);
+ }
```

### Chain of Responsibility

```diff
# Before: 嵌套验证
- function validate(user) {
-   const errors = [];
-   if (!user.email) errors.push('Email required');
+   else if (!isValidEmail(user.email)) errors.push('Invalid email');
+   if (!user.name) errors.push('Name required');
+   if (user.age < 18) errors.push('Must be 18+');
+   if (user.country === 'blocked') errors.push('Country not supported');
+   return errors;
+ }

# After: 责任链模式
+ abstract class Validator {
+   abstract validate(user: User): string | null;
+   setNext(validator: Validator): Validator {
+     this.next = validator;
+     return validator;
+   }
+   validate(user: User): string | null {
+     const error = this.doValidate(user);
+     if (error) return error;
+     return this.next?.validate(user) ?? null;
+   }
+ }
+
+ class EmailRequiredValidator extends Validator {
+   doValidate(user: User) {
+     return !user.email ? 'Email required' : null;
+   }
+ }
+
+ // Build the chain
+ const validator = new EmailRequiredValidator()
+   .setNext(new EmailFormatValidator())
+   .setNext(new NameRequiredValidator())
+   .setNext(new AgeValidator())
+   .setNext(new CountryValidator());
```

---

## Refactoring Steps

### Safe Refactoring Process

```
1. 准备 (PREPARE)
   - 确保测试存在（如果缺失则编写）
   - 提交当前状态
   - 创建功能分支

2. 识别 (IDENTIFY)
   - 找到要处理的代码异味
   - 理解代码做什么
   - 规划重构

3. 重构 (REFACTOR) - 小步骤
   - 做一个小改动
   - 运行测试
   - 如果测试通过则提交
   - 重复

4. 验证 (VERIFY)
   - 所有测试通过
   - 如需要则手动测试
   - 性能不变或改进

5. 清理 (CLEAN UP)
   - 更新注释
   - 更新文档
   - 最终提交
```

## Refactoring Checklist

### Code Quality

- [ ] 函数代码行数超大（< 50行）
- [ ] 去除重复代码
- [ ] 描述性名称（变量、函数、类）
- [ ] 无魔鬼数字/字符串
- [ ] 删除未使用代码

### Structure

- [ ] 相关代码在一起
- [ ] 清晰的模块边界
- [ ] 依赖单向流动
- [ ] 无循环依赖

### Type Safety

- [ ] 所有公共API定义类型
- [ ] 无未说明的`any`类型
- [ ] 可空类型明确标记
- [ ] 无不安全的类型转换
- [ ] 类型匹配检查（如long到int）

### Testing

- [ ] 重构代码通过单元测试
- [ ] 测试覆盖边界情况
- [ ] 所有测试通过

---

## Common Refactoring Operations

| Operation                                     | Description                           |
| --------------------------------------------- | ------------------------------------- |
| Extract Method                                | 将代码片段转为方法                     |
| Extract Class                                 | 将行为移到新类                         |
| Extract Interface                             | 从实现创建接口                         |
| Inline Method                                 | 将方法体移回调用者                     |
| Inline Class                                  | 将类行为移到调用者                     |
| Pull Up Method                                | 将方法移到超类                         |
| Push Down Method                              | 将方法移到子类                         |
| Rename Method/Variable                        | 提高清晰度                             |
| Introduce Parameter Object                    | 分组相关参数                           |
| Replace Conditional with Polymorphism         | 用多态替代switch/if                    |
| Replace Magic Number with Constant            | 命名常量                               |
| Decompose Conditional                         | 分解复杂条件                           |
| Consolidate Conditional                       | 合并重复条件                           |
| Replace Nested Conditional with Guard Clauses | 提前返回                               |
| Introduce Null Object                         | 消除null检查                           |
| Replace Type Code with Class/Enum             | 强类型                                 |
| Replace Inheritance with Delegation           | 组合优于继承                           |

---

## Risk Assessment

### 重构风险评估

在执行重构前，评估以下风险：

| 风险类型           | 评估标准                           | 缓解措施                     |
| ------------------ | ---------------------------------- | ---------------------------- |
| 测试覆盖率不足     | 测试覆盖率 < 90%                   | 先补充测试用例               |
| 代码复杂度高       | 圈复杂度 > 10                      | 分步重构，每步验证           |
| 依赖关系复杂       | 依赖深度 > 3层                     | 先解耦，再重构               |
| 业务逻辑关键       | 核心业务流程                       | 增加集成测试                 |
| 代码历史久远       | 最后修改时间 > 1年                 | 与业务方确认需求             |

### 收益评估

| 收益类型           | 评估标准                           |
| ------------------ | ---------------------------------- |
| 可维护性提升       | 代码行数减少、结构清晰             |
| 可测试性提升       | 测试覆盖率提升                     |
| 性能改善           | 执行时间减少                       |
| Bug风险降低        | 类型安全提升、边界检查完善         |
