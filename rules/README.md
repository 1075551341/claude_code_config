# Rules 规则索引

17 个专用规则文件，覆盖开发全场景。

---

## 规则列表

| 规则文件              | 适用场景            | 自动加载    |
| --------------------- | ------------------- | ----------- |
| `RULES_CORE.md`       | 所有代码开发        | ✅ 始终启用 |
| `RULES_COMMON.md`     | 通用编码规范        | ✅ 始终启用 |
| `RULES_BACKEND.md`    | 后端 API 开发       | ❌ 按需加载 |
| `RULES_FRONTEND.md`   | 前端 UI 开发        | ❌ 按需加载 |
| `RULES_DATABASE.md`   | 数据库设计/查询     | ❌ 按需加载 |
| `RULES_SECURITY.md`   | 安全开发/审计       | ❌ 按需加载 |
| `RULES_TESTING.md`    | 测试编写/策略       | ❌ 按需加载 |
| `RULES_PYTHON.md`     | Python 开发         | ❌ 按需加载 |
| `RULES_TYPESCRIPT.md` | TypeScript 开发     | ❌ 按需加载 |
| `RULES_AI.md`         | AI/LLM 应用开发     | ❌ 按需加载 |
| `RULES_DEVOPS.md`     | CI/CD、容器化、部署 | ❌ 按需加载 |
| `RULES_GIT.md`        | 版本控制、分支管理  | ❌ 按需加载 |
| `RULES_MOBILE.md`     | 移动端开发          | ❌ 按需加载 |
| `RULES_CSHARP.md`     | C# / .NET 开发      | ❌ 按需加载 |
| `RULES_DART.md`       | Dart / Flutter 开发 | ❌ 按需加载 |
| `RULES_GO.md`         | Go 语言开发         | ❌ 按需加载 |
| `RULES_RUST.md`       | Rust 语言开发       | ❌ 按需加载 |

---

## 使用方式

规则通过 Claude Code 的 `alwaysApply` 配置自动加载：

```yaml
---
description: 规则描述
alwaysApply: true # 始终加载
---
```

### 手动触发

```
使用 [规则名] 规则来 [任务描述]
```

示例：

- "使用数据库规则设计订单表结构"
- "使用安全规则审计这个 API"
- "使用测试规则编写单元测试"

---

## 规则内容概览

### RULES_CORE.md（核心规则）

- 角色定位：20 年经验全栈专家
- 优先级：简单至上、精准响应、最佳实践
- 代码规范：DRY、安全防御、错误处理
- 注释规则：触发条件、模板格式

### RULES_BACKEND.md（后端规则）

- 技术选型：Express / FastAPI / Gin
- API 设计：RESTful 路由、统一响应格式
- 数据库规范：索引、事务、Migration
- 安全基线：SQL 注入、认证、权限

### RULES_FRONTEND.md（前端规则）

- 技术选型：React / Vue
- 组件规范：文件结构、注释模板
- 样式规范：CSS Variables、响应式
- 性能检查：懒加载、代码分割、虚拟滚动

### RULES_DATABASE.md（数据库规则）

- 数据库选型：PostgreSQL / MySQL / MongoDB / Redis
- 表设计规范：命名、字段类型、索引
- 查询规范：禁止 SELECT \*、参数化查询
- Migration 规范：可回滚、分步执行

### RULES_SECURITY.md（安全规则）

- OWASP Top 10 防护
- 安全 Headers 配置
- 敏感数据处理
- 加密算法选择

### RULES_TESTING.md（测试规则）

- 测试金字塔：单元 70%、集成 20%、E2E 10%
- 测试框架选型
- 测试命名规范
- 覆盖率要求

### RULES_PYTHON.md（Python 规则）

- 版本：Python 3.11+
- 代码风格：命名、类型注解、文档字符串
- 异步编程：asyncio、aiohttp
- 数据验证：Pydantic

### RULES_TYPESCRIPT.md（TypeScript 规则）

- tsconfig 配置
- 类型系统：禁止 any、泛型约束
- 函数规范：签名、重载
- React/前端规范

### RULES_AI.md（AI 开发规则）

- 模型选型
- Prompt 工程原则
- API 调用规范
- RAG 系统设计
- Token 管理

### RULES_DEVOPS.md（DevOps 规则）

- 技术选型：CI/CD、容器化、编排
- Docker 规范：多阶段构建、最佳实践
- Kubernetes 配置：部署、安全、可靠性
- CI/CD 流水线设计
- 监控告警配置
- 基础设施即代码

### RULES_GIT.md（Git 规则）

- 分支策略：Git Flow、Trunk Based
- Commit 规范：格式、类型、示例
- PR 规范：模板、Code Review
- 危险操作防护
- 常用命令速查
- Git Hooks 配置

---

## 同步机制

规则文件通过软连接同步到各编辑器：

```powershell
# 运行同步脚本
./sync.ps1
```

同步内容：

- `rules/` → 软连接到各编辑器目录
- 配合 `CLAUDE.md` 全局指令使用
