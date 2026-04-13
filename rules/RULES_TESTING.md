---
description: 测试编写、测试策略、测试框架相关任务时启用
alwaysApply: false
---

# 测试规则（专用）

> 配合核心规则使用，仅在测试场景加载

## 测试金字塔

```
        /\      E2E 测试（10%）- 用户流程
       /  \
      /----\    集成测试（20%）- 模块间交互
     /      \
    /--------\  单元测试（70%）- 函数/组件逻辑
```

## 测试框架选型

| 语言/框架 | 单元测试 | 集成测试 | E2E 测试 |
|-----------|----------|----------|----------|
| JS/TS | Vitest / Jest | Supertest | Playwright / Cypress |
| Python | pytest | pytest + fixtures | Playwright |
| Go | testing | testify | Playwright |
| Java | JUnit 5 | TestContainers | Selenium |

## 单元测试规范

### AAA 模式

```typescript
describe('Calculator', () => {
  it('should return sum of two numbers', () => {
    // Arrange
    const calc = new Calculator();
    // Act
    const result = calc.add(2, 3);
    // Assert
    expect(result).toBe(5);
  });
});
```

### 命名规范

```
测试文件：{module}.test.{ext}
测试函数：should_{expected_behavior}_when_{condition}
示例：should_return_user_when_id_exists / should_throw_error_when_user_not_found
```

### 边界测试覆盖

```typescript
describe('validateAge', () => {
  it.each([0, 1, 18, 65, 120])('should accept valid age: %i', (age) => { expect(validateAge(age)).toBe(true); });
  it.each([-1, 121])('should reject invalid age: %i', (age) => { expect(() => validateAge(age)).toThrow(); });
  it.each([null, undefined, NaN, Infinity])('should reject %s', (value) => { expect(() => validateAge(value)).toThrow(); });
});
```

## 集成测试规范

```typescript
describe('POST /api/users', () => {
  beforeEach(async () => { await setupTestDatabase(); });
  afterEach(async () => { await cleanupTestDatabase(); });

  it('should create user with valid data', async () => {
    const response = await request(app).post('/api/users').send({ name: 'Test', email: 'test@example.com' }).expect(201);
    expect(response.body.data).toMatchObject({ name: 'Test', email: 'test@example.com' });
  });
});
```

测试数据库原则：独立测试库 / 每测试前清理 / 事务回滚（更快）/ Mock 外部服务

## E2E 测试规范

```typescript
test('should complete registration', async ({ page }) => {
  await page.goto('/register');
  await page.fill('[name="name"]', 'Test User');
  await page.fill('[name="email"]', 'test@example.com');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL('/login');
});
```

E2E 最佳实践：测试关键流程 / data-testid 选择器 / waitFor 等待 / 独立运行 / 清理测试数据

## Mock 规范

```typescript
// 函数 Mock
const mockFetch = vi.fn().mockResolvedValue({ json: () => ({ data: 'test' }) });

// 模块 Mock（部分保留）
vi.mock('./api', async (importOriginal) => {
  const actual = await importOriginal();
  return { ...actual, fetchUser: vi.fn().mockResolvedValue({ id: 1 }) };
});
```

## 测试覆盖率要求

| 项目类型 | 语句覆盖 | 分支覆盖 | 函数覆盖 |
|----------|----------|----------|----------|
| 核心业务 | 80%+ | 75%+ | 85%+ |
| 工具库 | 90%+ | 85%+ | 95%+ |
| 配置代码 | 60%+ | 50%+ | 60%+ |

## TDD 工作流

```
1. Red    - 写失败的测试
2. Green  - 写最少代码通过测试
3. Refactor - 重构代码（保持测试通过）
4. 重复
```

## 测试清单

```
□ 正常路径（Happy Path）
□ 边界值（Boundary Values）
□ 异常处理（Error Cases）
□ 空值/Null 处理
□ 并发场景（如适用）
□ 性能基准（如适用）
```
