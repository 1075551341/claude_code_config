---
name: agent-browser
description: Rust极速无头浏览器自动化，支持网页交互和数据采集
triggers: [浏览器自动化, 无头浏览器, agent browser, 网页自动化, 浏览器测试]
---

# Agent浏览器

## 核心功能

- 无头浏览器控制
- 页面交互自动化
- 数据采集提取
- 性能测试

## 技术特点

- Rust实现，高性能
- 极速渲染引擎
- 低内存占用
- 并发支持

## 使用场景

- 网页自动化测试
- 数据抓取
- 页面截图
- 性能监控

## API示例

```rust
// 启动浏览器
let browser = Browser::new()?;

// 访问页面
let page = browser.new_page()?;
page.goto("https://example.com")?;

// 提取数据
let text = page.find_element("body")?.text()?;
```
