---
name: testing-standards
description: 当需要编写测试规范、制定测试策略、编写单元测试/集成测试/E2E测试时调用此技能。触发词：测试规范、单元测试、集成测试、E2E测试、测试策略、测试覆盖、Jest、Vitest、测试框架、测试最佳实践。
---

# 测试规范

## 测试原则

```
🎯 快速反馈 - 测试要快，问题早发现
📐 可重复 - 测试结果稳定一致
🔍 自描述 - 测试即文档
🧩 单一职责 - 一个测试只验证一个点
🔄 独立性 - 测试之间不依赖
```

## 测试金字塔

```
          /\
         /  \        E2E 测试（少量，慢）
        /----\
       /      \      集成测试（适量，中）
      /--------\
     /          \    单元测试（大量，快）
    /------------\
```

## 单元测试

### Vitest 配置

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      exclude: ['node_modules/', 'dist/', '**/*.test.ts']
    }
  }
})
```

### 测试命名和组织

```typescript
// __tests__/services/user.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { UserService } from '../services/user'

describe('UserService', () => {
  let service: UserService

  beforeEach(() => {
    service = new UserService()
  })

  describe('getUserById', () => {
    it('should return user when user exists', async () => {
      // Arrange
      const mockUser = { id: '1', name: '张三' }
      vi.spyOn(service, 'findById').mockResolvedValue(mockUser)

      // Act
      const result = await service.getUserById('1')

      // Assert
      expect(result).toEqual(mockUser)
    })

    it('should throw NotFoundError when user does not exist', async () => {
      // Arrange
      vi.spyOn(service, 'findById').mockResolvedValue(null)

      // Act & Assert
      await expect(service.getUserById('999'))
        .rejects.toThrow('用户不存在')
    })

    it('should throw ValidationError when id is invalid', async () => {
      // Act & Assert
      await expect(service.getUserById(''))
        .rejects.toThrow('无效的用户ID')
    })
  })
})
```

### AAA 模式

```typescript
it('should calculate order total correctly', () => {
  // Arrange（准备）
  const order = {
    items: [
      { price: 100, quantity: 2 },
      { price: 50, quantity: 1 }
    ]
  }
  const calculator = new OrderCalculator()

  // Act（执行）
  const total = calculator.calculateTotal(order)

  // Assert（断言）
  expect(total).toBe(250)
})
```

### Mock 最佳实践

```typescript
// 模块 Mock
vi.mock('@/api/user', () => ({
  userApi: {
    getUser: vi.fn(),
    createUser: vi.fn()
  }
}))

// 定时器 Mock
vi.useFakeTimers()
it('should call callback after delay', () => {
  const callback = vi.fn()
  setTimeout(callback, 1000)

  vi.advanceTimersByTime(1000)

  expect(callback).toHaveBeenCalled()
})
vi.useRealTimers()

// 函数 Mock
const mockCallback = vi.fn()
mockCallback.mockReturnValue('mocked')
mockCallback.mockResolvedValue('async mocked')

// 验证调用
expect(mockCallback).toHaveBeenCalled()
expect(mockCallback).toHaveBeenCalledWith('arg1', 'arg2')
expect(mockCallback).toHaveBeenCalledTimes(2)
```

## Vue 组件测试

```typescript
// __tests__/components/UserCard.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import UserCard from '@/components/UserCard.vue'

describe('UserCard', () => {
  it('should render user name', () => {
    const wrapper = mount(UserCard, {
      props: {
        user: { id: '1', name: '张三', email: 'test@example.com' }
      }
    })

    expect(wrapper.text()).toContain('张三')
  })

  it('should emit edit event when button clicked', async () => {
    const wrapper = mount(UserCard, {
      props: {
        user: { id: '1', name: '张三', email: 'test@example.com' },
        editable: true
      }
    })

    await wrapper.find('.edit-btn').trigger('click')

    expect(wrapper.emitted('edit')).toBeTruthy()
    expect(wrapper.emitted('edit')[0]).toEqual(['1'])
  })

  it('should not show edit button when not editable', () => {
    const wrapper = mount(UserCard, {
      props: {
        user: { id: '1', name: '张三', email: 'test@example.com' },
        editable: false
      }
    })

    expect(wrapper.find('.edit-btn').exists()).toBe(false)
  })

  it('should match snapshot', () => {
    const wrapper = mount(UserCard, {
      props: {
        user: { id: '1', name: '张三', email: 'test@example.com' }
      }
    })

    expect(wrapper.html()).toMatchSnapshot()
  })
})
```

## React 组件测试

```typescript
// __tests__/components/UserCard.test.tsx
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { UserCard } from '@/components/UserCard'

describe('UserCard', () => {
  it('should render user name', () => {
    render(
      <UserCard
        user={{ id: '1', name: '张三', email: 'test@example.com' }}
      />
    )

    expect(screen.getByText('张三')).toBeInTheDocument()
  })

  it('should call onEdit when button clicked', async () => {
    const onEdit = vi.fn()

    render(
      <UserCard
        user={{ id: '1', name: '张三', email: 'test@example.com' }}
        editable
        onEdit={onEdit}
      />
    )

    fireEvent.click(screen.getByRole('button', { name: /编辑/i }))

    expect(onEdit).toHaveBeenCalledWith('1')
  })
})
```

## E2E 测试

### Playwright 配置

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  baseURL: 'http://localhost:3000',
  use: {
    trace: 'on-first-retry',
    screenshot: 'only-on-failure'
  },
  webServer: {
    command: 'pnpm dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI
  }
})
```

### E2E 测试示例

```typescript
// e2e/login.spec.ts
import { test, expect } from '@playwright/test'

test.describe('登录功能', () => {
  test('should login successfully with valid credentials', async ({ page }) => {
    await page.goto('/login')

    await page.fill('input[name="email"]', 'test@example.com')
    await page.fill('input[name="password"]', 'password123')
    await page.click('button[type="submit"]')

    // 等待跳转到首页
    await expect(page).toHaveURL('/')

    // 验证用户信息显示
    await expect(page.locator('.user-name')).toContainText('测试用户')
  })

  test('should show error with invalid credentials', async ({ page }) => {
    await page.goto('/login')

    await page.fill('input[name="email"]', 'test@example.com')
    await page.fill('input[name="password"]', 'wrongpassword')
    await page.click('button[type="submit"]')

    // 验证错误提示
    await expect(page.locator('.error-message')).toContainText('邮箱或密码错误')
  })
})
```

## 测试覆盖率要求

| 类型 | 最低覆盖率 | 目标覆盖率 |
|------|-----------|-----------|
| 工具函数 | 80% | 95% |
| 业务逻辑 | 70% | 85% |
| 组件 | 60% | 75% |
| 总体 | 70% | 80% |

## 测试检查清单

### 单元测试

- [ ] 测试覆盖正常情况
- [ ] 测试覆盖边界条件
- [ ] 测试覆盖错误情况
- [ ] Mock 使用合理
- [ ] 测试命名清晰

### 集成测试

- [ ] 模块间交互正确
- [ ] 数据库操作正确
- [ ] API 响应符合预期

### E2E 测试

- [ ] 关键用户流程覆盖
- [ ] 测试数据独立可清理
- [ ] 测试稳定可重复