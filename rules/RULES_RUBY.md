---
description: Ruby/Rails 开发规则
globs: ["*.rb", "*.erb", "Gemfile", "Rakefile", "*.yml"]
---

# Ruby/Rails 开发规则

## 项目结构

- Rails 标准：app/{models,controllers,views,helpers} + lib/ + config/
- Service Object：复杂业务逻辑抽到 app/services/
- Concern：可复用模块逻辑放 app/models/concerns/

## 编码规范

- 命名：变量/方法 snake_case、类/模块 PascalCase、常量 UPPER_SNAKE
- 冻结字符串：# frozen_string_literal: true
- 块：单行用 {}，多行用 do/end
- 避免猴子补丁：除非有充分理由并文档化

## Rails 约定

- 路由：RESTful 资源路由，嵌套不超过 2 层
- Strong Parameters：控制器必须白名单参数
- 回调：避免回调链过深，复杂逻辑用 Service Object
- N+1：用 includes / preload / eager_load 预加载
- 查询：复杂查询用 scope 链式调用

## 安全

- SQL 注入：用参数化查询，禁止字符串插值
- XSS：默认自动转义，JSON API 注意 raw 输出
- CSRF：非 API 控制器启用 protect_from_forgery
- 文件上传：验证文件类型和大小，禁止可执行文件
- 依赖审计：定期 bundle audit

## 测试

- RSpec：单元测试 + 系统测试（Capybara）
- Factory：用 FactoryBot，禁止 fixtures
- 测试覆盖：SimpleCov，目标 ≥ 80%

## 时间处理

- 禁止 Time.now / DateTime，用 Time.current / Time.zone.now
- 时区：config.time_zone 设置，存储 UTC，展示本地
