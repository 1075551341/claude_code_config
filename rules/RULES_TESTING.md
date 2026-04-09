---
description: 测试编写、测试策略、测试框架相关任务时启用
alwaysApply: false
---

# 测试规则（专用）

> 配合核心规则使用，仅在测试场景加载

## 测试金字塔

```
        /\
       /  \      E2E 测试（10%）- 用户流程
      /----\     
     /      \    集成测试（20%）- 模块间交互
    /--------\
   /          \  单元测试（70%）- 函数/组件逻辑
  /------------\
```

## 测试框架选型

| 语言/框架 | 单元测试 | 集成测试 | E2E 测试 |
|-----------|----------|----------|----------|
| JavaScript/TypeScript | Vitest / Jest | Supertest | Playwright / Cypress |
| Python | pytest | pytest + fixtures | Playwright |
| Go | testing | testify | Playwright |
| Java | JUnit 5 | TestContainers | Selenium |

## 单元测试规范

### 测试结构（AAA 模式）

```typescript
describe('Calculator', () => {
  describe('add', () => {
    it('should return sum of two numbers', () => {
      // Arrange（准备）
      const calc = new Calculator();
      const a = 2;
      const b = 3;

      // Act（执行）
      const result = calc.add(a, b);

      // Assert（断言）
      expect(result).toBe(5);
    });

    it('should throw error for invalid input', () => {
      const calc = new Calculator();
      expect(() => calc.add(NaN, 1)).toThrow('Invalid number');
    });
  });
});
```

### 测试命名规范

```markdown
测试文件：{module}.test.{ext}
测试函数：should_{expected_behavior}_when_{condition}

示例：
- userService.test.ts
- should_return_user_when_id_exists
- should_throw_error_when_user_not_found
```

### 边界测试覆盖

```typescript
describe('validateAge', () => {
  // 正常值
  it.each([0, 1, 18, 65, 120])('should accept valid age: %i', (age) => {
    expect(validateAge(age)).toBe(true);
  });

  // 边界值
  it.each([-1, 121])('should reject invalid age: %i', (age) => {
    expect(() => validateAge(age)).toThrow();
  });

  // 特殊值
  it.each([null, undefined, NaN, Infinity])('should reject %s', (value) => {
    expect(() => validateAge(value)).toThrow();
  });
});
```

## 集成测试规范

### API 测试模板

```typescript
describe('POST /api/users', () => {
  beforeEach(async () => {
    await setupTestDatabase();
  });

  afterEach(async () => {
    await cleanupTestDatabase();
  });

  it('should create user with valid data', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({ name: 'Test', email: 'test@example.com' })
      .expect(201);

    expect(response.body.data).toMatchObject({
      name: 'Test',
      email: 'test@example.com'
    });
  });

  it('should reject duplicate email', async () => {
    await createUser({ email: 'test@example.com' });
    
    await request(app)
      .post('/api/users')
      .send({ name: 'Test2', email: 'test@example.com' })
      .expect(409);
  });
});
```

### 测试数据库

```markdown
原则：
- 使用独立测试数据库
- 每个测试前清理/重置
- 使用事务回滚（更快）
- Mock 外部服务

示例：
- 测试数据库：test_db
- 内存数据库：SQLite :memory:
- TestContainers：Docker 容器
```

## E2E 测试规范

### Playwright 示例

```typescript
test.describe('User Registration Flow', () => {
  test('should complete registration successfully', async ({ page }) => {
    // 访问注册页
    await page.goto('/register');

    // 填写表单
    await page.fill('[name="name"]', 'Test User');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'SecurePass123!');

    // 提交表单
    await page.click('button[type="submit"]');

    // 验证跳转到登录页
    await expect(page).toHaveURL('/login');
    
    // 验证提示信息
    await expect(page.locator('.toast')).toContainText('注册成功');
  });
});
```

### E2E 最佳实践

```markdown
1. 测试关键用户流程
2. 使用稳定的元素选择器（data-testid）
3. 添加适当的等待（waitFor）
4. 独立运行（无依赖顺序）
5. 清理测试数据
```

## Mock 规范

### 函数 Mock

```typescript
// Vitest/Jest
const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

mockFetch.mockResolvedValue({ json: () => ({ data: 'test' }) });
```

### 模块 Mock

```typescript
// 完全 Mock
vi.mock('./api', () => ({
  fetchUser: vi.fn().mockResolvedValue({ id: 1, name: 'Test' })
}));

// 部分保留
vi.mock('./api', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    fetchUser: vi.fn().mockResolvedValue({ id: 1 })
  };
});
```

## 测试覆盖率要求

| 项目类型 | 语句覆盖 | 分支覆盖 | 函数覆盖 |
|----------|----------|----------|----------|
| 核心业务 | 80%+ | 75%+ | 85%+ |
| 工具库 | 90%+ | 85%+ | 95%+ |
| 配置代码 | 60%+ | 50%+ | 60%+ |

```javascript
// vite.config.ts / jest.config.js
coverage: {
  provider: 'v8',
  reporter: ['text', 'html'],
  exclude: [
    'node_modules/',
    '**/*.d.ts',
    '**/*.config.*',
    '**/types/**'
  ],
  thresholds: {
    lines: 80,
    functions: 85,
    branches: 75,
    statements: 80
  }
}
```

## TDD 工作流

```
1. 🔴 Red    - 写失败的测试
2. 🟢 Green  - 写最少代码通过测试
3. 🔵 Refactor - 重构代码（保持测试通过）
4. 重复
```

## 测试清单

```markdown
□ 正常路径（Happy Path）
□ 边界值（Boundary Values）
□ 异常处理（Error Cases）
□ 空值/Null 处理
□ 并发场景（如适用）
□ 性能基准（如适用）
```