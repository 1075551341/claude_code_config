---
name: test-driven-development
description: 遵循TDD流程开发功能，RED-GREEN-REFACTOR循环
triggers: [TDD, 测试驱动, 测试先行, RED-GREEN-REFACTOR, 先写测试, 单元测试]
---

# 测试驱动开发（TDD）

## @Examples

```
用户: "用TDD实现这个功能"
Claude: /test-driven-development → RED(写失败测试) → GREEN(最小实现) → REFACTOR(优化)

用户: "先写测试"
Claude: /test-driven-development → 设计测试 → 编写失败测试 → 实现功能
```

## 核心理念

**RED-GREEN-REFACTOR 循环：先写失败测试，再实现功能，最后重构优化。**

---

## 适用场景

- 新功能开发
- Bug 修复（先写失败测试复现 Bug）
- 重构前建立安全网
- API 开发
- 库/模块开发

---

## 三阶段循环

### RED：写失败测试

```bash
# 步骤
1. 理解需求
2. 设计接口（函数签名、输入输出）
3. 编写测试描述预期行为
4. 运行测试 → 必须失败
5. 失败信息验证测试正确
```

**测试结构：**
```
描述测试意图 → 安排测试数据 → 执行被测代码 → 断言结果
```

**原则：**
- 一个测试一个断言
- 测试名称描述行为，不是"测试 X"
- 测试应失败并给出清晰原因

### GREEN：最小实现

```bash
# 步骤
1. 写最简单代码让测试通过
2. 硬编码返回值也行
3. 运行测试 → 必须通过
4. 不提前优化
```

**原则：**
- 最小改变
- 不添加额外功能
- "作弊"通过比过度实现好

### REFACTOR：优化清理

```bash
# 步骤
1. 测试通过后检查代码
2. 消除重复
3. 改善命名
4. 优化结构
5. 每次小重构后运行测试
6. 测试始终通过
```

**重构清单：**
- 重复代码 → 提取函数
- 长函数 → 拆分
- 魔法数字 → 常量
- 复杂条件 → 策略模式

---

## 测试金字塔

```
       /\
      /E2E\       少量，慢，高价值
     /------\
    /集成测试\     适量，中等速度
   /----------\
  /  单元测试  \   大量，快，低成本
 /--------------\
```

**优先级：单元测试 > 集成测试 > E2E 测试**

---

## 测试命名规范

```javascript
// 好命名
describe('Calculator', () => {
  it('should add two numbers correctly', () => {})
  it('should throw error when dividing by zero', () => {})
  it('should return negative result for negative inputs', () => {})
})

// 坏命名
describe('Calculator', () => {
  it('testAdd', () => {})        // 不描述行为
  it('test1', () => {})          // 无意义
  it('works', () => {})          // 太模糊
})
```

---

## Mock 与依赖隔离

```javascript
// 依赖注入
function UserService(apiClient) {
  this.client = apiClient
}

// 测试时注入 Mock
const mockClient = {
  getUser: jest.fn().mockResolvedValue({ id: 1, name: 'Test' })
}
const service = new UserService(mockClient)

// 真实代码注入真实实现
const realClient = new ApiClient()
const service = new UserService(realClient)
```

---

## 测试框架选择

| 语言 | 推荐 |
|------|------|
| JavaScript/TypeScript | Jest, Vitest |
| Python | pytest |
| Go | testing 包 |
| Java | JUnit 5 |
| Rust | cargo test |

---

## 常见陷阱

| 问题 | 解决方案 |
|------|----------|
| 测试依赖顺序 | 每个测试独立，不共享状态 |
| Mock 过度 | 只隔离外部依赖，内部用真实实现 |
| 测试太慢 | 并行执行，分层测试 |
| 覆盖率虚荣 | 关注关键路径，不是数字 |
| 测试脆弱 | 避免依赖 UI 细节 |

---

## 相关技能

- `testing-standards` - 测试规范详情
- `systematic-debugging` - 调试流程
- `code-refactor` - 重构技巧