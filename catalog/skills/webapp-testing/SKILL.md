---
name: webapp-testing
description: 用于 Web 应用自动化测试，使用 Playwright 进行端到端测试。测试 Web 应用
triggers: [用于 Web 应用自动化测试，使用 Playwright 进行端到端测试。测试 Web 应用, 编写 E2E 测试, 自动化浏览器操作时使用]
---

# Web 应用测试

## 核心原则

```
用户视角 → 模拟真实用户行为
稳定可靠 → 避免脆弱的选择器
快速反馈 → 并行执行，智能等待
可维护性 → Page Object 模式
```

## Playwright 基础

### 安装配置

```bash
# 安装
npm init playwright@latest

# 或手动安装
npm install -D @playwright/test
npx playwright install
```

### 基础测试

```typescript
import { test, expect } from "@playwright/test";

test("用户登录流程", async ({ page }) => {
  // 导航到页面
  await page.goto("https://example.com/login");

  // 填写表单
  await page.fill('[name="email"]', "user@example.com");
  await page.fill('[name="password"]', "password123");

  // 点击登录
  await page.click('button[type="submit"]');

  // 验证结果
  await expect(page).toHaveURL(/.*dashboard/);
  await expect(page.locator(".welcome")).toBeVisible();
});
```

## 选择器策略

### 优先级

```typescript
// 1. 角色 + 名称（最稳定）
await page.getByRole("button", { name: "提交" });
await page.getByRole("textbox", { name: "邮箱" });

// 2. 测试 ID（推荐用于测试关键元素）
await page.getByTestId("submit-button");

// 3. 文本内容
await page.getByText("欢迎回来");

// 4. 标签
await page.getByLabel("密码");

// 5. 占位符
await page.getByPlaceholder("请输入邮箱");

// 6. CSS 选择器（最后选择）
await page.locator(".submit-btn");
await page.locator("#login-form button");
```

### 添加测试 ID

```html
<!-- React -->
<button data-testid="submit-btn">提交</button>

<!-- Vue -->
<button data-testid="submit-btn">提交</button>
```

## 等待策略

```typescript
// 自动等待（推荐）
await expect(page.locator(".result")).toBeVisible();
await expect(page.locator(".count")).toHaveText("5");

// 显式等待元素
await page.waitForSelector(".loaded");

// 等待网络请求完成
await page.waitForLoadState("networkidle");

// 等待特定响应
const responsePromise = page.waitForResponse("**/api/users");
await page.click("button");
const response = await responsePromise;

// 等待超时
await page.waitForTimeout(1000); // 不推荐，仅调试用
```

## 常用操作

```typescript
// 导航
await page.goto(url);
await page.goBack();
await page.goForward();
await page.reload();

// 表单操作
await page.fill(selector, value);
await page.selectOption(selector, value);
await page.check(selector);
await page.uncheck(selector);
await page.setInputFiles(selector, filePath);

// 鼠标操作
await page.click(selector);
await page.dblclick(selector);
await page.hover(selector);
await page.dragAndDrop(source, target);

// 键盘操作
await page.press(selector, "Enter");
await page.keyboard.type("Hello");
await page.keyboard.press("Control+A");

// 截图
await page.screenshot({ path: "screenshot.png" });
await element.screenshot({ path: "element.png" });

// 滚动
await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
```

## 断言

```typescript
// 元素状态
await expect(locator).toBeVisible();
await expect(locator).toBeHidden();
await expect(locator).toBeEnabled();
await expect(locator).toBeDisabled();
await expect(locator).toBeChecked();

// 内容
await expect(locator).toHaveText("Hello");
await expect(locator).toContainText("Hello");
await expect(locator).toHaveValue("input value");
await expect(locator).toHaveAttribute("href", "/path");

// 数量
await expect(locator).toHaveCount(3);

// 页面
await expect(page).toHaveURL(/.*dashboard/);
await expect(page).toHaveTitle(/首页/);

// 截图对比
await expect(page).toHaveScreenshot();
```

## Page Object 模式

```typescript
// pages/LoginPage.ts
export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByLabel("邮箱");
    this.passwordInput = page.getByLabel("密码");
    this.submitButton = page.getByRole("button", { name: "登录" });
  }

  async goto() {
    await this.page.goto("/login");
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}

// tests/login.spec.ts
test("登录测试", async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login("user@example.com", "password");
  await expect(page).toHaveURL(/.*dashboard/);
});
```

## 测试组织

```typescript
// describe 分组
test.describe("用户管理", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/login");
    // 登录操作...
  });

  test("创建用户", async ({ page }) => {
    // ...
  });

  test("删除用户", async ({ page }) => {
    // ...
  });
});

// 并行执行
test.describe.parallel("并行测试组", () => {
  // 这些测试会并行执行
});

// 串行执行（有依赖的测试）
test.describe.serial("串行测试组", () => {
  // 这些测试会按顺序执行
});
```

## API 测试

```typescript
import { request } from "@playwright/test";

test("API 测试", async () => {
  const context = await request.newContext();

  // GET 请求
  const response = await context.get("/api/users");
  expect(response.ok()).toBeTruthy();
  const users = await response.json();

  // POST 请求
  const createResponse = await context.post("/api/users", {
    data: { name: "Test User" },
  });
  expect(createResponse.status()).toBe(201);
});
```

## Mock 和拦截

```typescript
// Mock API 响应
await page.route("**/api/users", (route) => {
  route.fulfill({
    status: 200,
    body: JSON.stringify([{ id: 1, name: "Mock User" }]),
  });
});

// 修改请求
await page.route("**/api/**", (route) => {
  route.continue({
    headers: { ...route.request().headers(), Authorization: "Bearer token" },
  });
});

// 阻止请求
await page.route("**/analytics/**", (route) => route.abort());
```

## 配置文件

```typescript
// playwright.config.ts
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: "html",
  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "firefox", use: { ...devices["Desktop Firefox"] } },
    { name: "webkit", use: { ...devices["Desktop Safari"] } },
    { name: "Mobile Chrome", use: { ...devices["Pixel 5"] } },
  ],
  webServer: {
    command: "npm run dev",
    url: "http://localhost:3000",
    reuseExistingServer: !process.env.CI,
  },
});
```

## 调试技巧

```bash
# UI 模式调试
npx playwright test --ui

# 查看追踪
npx playwright show-trace trace.zip

# 调试模式
npx playwright test --debug

# 生成代码
npx playwright codegen https://example.com
```

## 最佳实践清单

```markdown
- [ ] 使用稳定的选择器（角色、测试 ID）
- [ ] 使用自动等待而非固定等待
- [ ] Page Object 模式组织测试
- [ ] 测试独立，不依赖执行顺序
- [ ] 有意义的断言消息
- [ ] 合理使用 Mock，但不过度
- [ ] 测试覆盖关键用户流程
- [ ] CI 中运行前检查
```
