---
name: web-testing
description: 使用 Playwright 测试 Web 应用，支持导航、表单填写、元素交互、截图和验证。测试 Web 应用或调试前端问题时使用。
---

# Web Testing with Playwright

## 决策树
```
任务类型？
├─ 静态 HTML  → 直接读文件获取选择器 → 写 Playwright 脚本
└─ 动态应用   → 服务是否在运行？
    ├─ 否 → 先启动服务
    └─ 是 → 侦察（截图/审查 DOM）→ 获取选择器 → 执行操作
```

## 基础脚本模板
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # 导航并等待加载
    page.goto("http://localhost:3000")
    page.wait_for_load_state("networkidle")
    
    # 截图侦察（获取 DOM 状态）
    page.screenshot(path="screenshot.png")
    
    # 表单填写
    page.fill('[data-testid="email"]', "test@example.com")
    page.fill('[data-testid="password"]', "password")
    page.click('[type="submit"]')
    
    # 等待导航完成
    page.wait_for_url("**/dashboard")
    
    # 断言
    assert page.locator("h1").text_content() == "Welcome"
    
    browser.close()
```

## 选择器优先级
```python
# 优先顺序（从高到低）
page.get_by_role("button", name="提交")       # 1. 语义角色
page.get_by_label("用户名")                    # 2. 标签关联
page.get_by_test_id("submit-btn")             # 3. data-testid
page.locator('[data-testid="submit"]')         # 4. 属性选择器
page.locator("button.primary")                 # 5. CSS（最后选）
```

## 异步等待（避免硬等待）
```python
# ❌ 硬等待
time.sleep(2)
# ✅ 等待特定状态
page.wait_for_selector(".data-loaded")
page.wait_for_response("**/api/users")
page.wait_for_function("() => document.readyState === 'complete'")
page.expect_response(lambda r: r.url.endswith("/api/data") and r.status == 200)
```

## 服务管理（本地应用）
```python
import subprocess, time

# 启动服务
proc = subprocess.Popen(["npm", "start"], stdout=subprocess.PIPE)
time.sleep(2)  # 等待启动

try:
    # 执行测试
    run_tests()
finally:
    proc.terminate()
```

## 调试技巧
```python
# 捕获控制台日志
page.on("console", lambda msg: print(f"[{msg.type}] {msg.text}"))

# 捕获网络错误
page.on("requestfailed", lambda req: print(f"失败请求: {req.url}"))

# 暴露页面内部状态
state = page.evaluate("() => window.__appState")
```

## 测试清单
- [ ] 验证成功路径（Happy Path）
- [ ] 验证错误处理（表单校验、网络错误）
- [ ] 测试加载状态（Loading → 完成 → 错误）
- [ ] 边界条件（空数据、长文本、特殊字符）
- [ ] 截图留证（关键步骤前后）
