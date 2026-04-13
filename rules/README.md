# Rules 规则索引

16 个规则文件，覆盖开发全场景。

---

## 规则列表

| 规则文件              | 适用场景                   | 自动加载    |
| --------------------- | -------------------------- | ----------- |
| `RULES_CORE.md`       | 核心规则（含通用编码规范） | ✅ 始终启用 |
| `RULES_BACKEND.md`    | 后端 API 开发              | ❌ 按需加载 |
| `RULES_FRONTEND.md`   | 前端 UI 开发               | ❌ 按需加载 |
| `RULES_DATABASE.md`   | 数据库设计/查询            | ❌ 按需加载 |
| `RULES_SECURITY.md`   | 安全开发/审计              | ❌ 按需加载 |
| `RULES_TESTING.md`    | 测试编写/策略              | ❌ 按需加载 |
| `RULES_PYTHON.md`     | Python 开发                | ❌ 按需加载 |
| `RULES_TYPESCRIPT.md` | TypeScript 开发            | ❌ 按需加载 |
| `RULES_AI.md`         | AI/LLM 应用开发            | ❌ 按需加载 |
| `RULES_DEVOPS.md`     | CI/CD、容器化、部署        | ❌ 按需加载 |
| `RULES_GIT.md`        | 版本控制、分支管理         | ❌ 按需加载 |
| `RULES_MOBILE.md`     | 移动端开发                 | ❌ 按需加载 |
| `RULES_CSHARP.md`     | C# / .NET 开发             | ❌ 按需加载 |
| `RULES_DART.md`       | Dart / Flutter 开发        | ❌ 按需加载 |
| `RULES_GO.md`         | Go 语言开发                | ❌ 按需加载 |
| `RULES_RUST.md`       | Rust 语言开发              | ❌ 按需加载 |

---

## 使用方式

规则通过 `alwaysApply` 配置自动加载，或通过 globs 模式匹配文件类型自动触发。

### 手动触发

```
使用 [规则名] 规则来 [任务描述]
```

示例：

- "使用数据库规则设计订单表结构"
- "使用安全规则审计这个 API"
- "使用测试规则编写单元测试"

---

## 同步机制

```powershell
./sync.ps1
```

同步内容：`rules/` → 软连接到各编辑器目录，配合 `CLAUDE.md` 全局指令使用。
