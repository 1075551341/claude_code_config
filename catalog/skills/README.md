# Catalog Skills — 按需复制

> 此目录提供领域专用 skill 定义，按需复制到项目 `.claude/skills/` 使用。
> 全局 skills 在 `~/.claude/skills/`。清单见 [../INDEX.md](../INDEX.md)。

## 使用策略

```
全局 skills/ → 五柱核心，会话自动匹配触发（清单见 ~/.claude/skills-INDEX.md）
catalog/skills/ (107) → 领域专用 + v11 降级变体，按需复制到项目
```

## v11 新入 catalog（原全局降级）

`browser-qa` · `claude-to-deerflow` · `instinct-learning` · `office-hours`（并入原 product-manager 六问框架）· `onboarding-guide` · `taste-memory`

## 同名项消歧（v10.17）

`deep-research`、`git-workflow` 在顶层 `~/.claude/skills/` 也存在。**顶层为权威实现**
（INDEX 与 `commands/` 均指向它），本目录同名项是变体副本，仅在复制到项目时使用，
不要在全局会话中加载或引用。

## 复制命令

```powershell
# 复制单个 skill 到项目
python ~/.claude/scripts/migrate-from-legacy.py --project <path> --skill <name>

# 示例
python ~/.claude/scripts/migrate-from-legacy.py --project . --skill python-backend
```

## 领域分类

| 分类 | 数量 | 示例 |
|------|------|------|
| 前端 | 15+ | frontend-design, react-component, vue3-composable |
| 后端 | 20+ | api-development, fastapi-crud, django-rest |
| 数据库 | 10+ | postgres-optimization, mongodb-aggregation |
| DevOps | 10+ | cicd-pipeline, docker-compose, k8s-deploy |
| 安全 | 8+ | security-audit, owasp-scan, secret-detection |
| AI/ML | 8+ | model-training, prompt-engineering, rag-setup |
| 移动 | 8+ | react-native, flutter-widget, ios-swiftui |
| 测试 | 6+ | unit-testing, e2e-playwright, api-testing |
| 文档 | 5+ | api-documentation, changelog-generator, readme-builder |
| 工具 | 7+ | code-refactor, git-workflow, data-migration |

## 与全局 skills/ 的关系

- **去重原则**: catalog 中的 skill 若与全局 skills/ 同名 → 全局版本优先
- **按需原则**: catalog skills 不在运行时自动加载，需要显式复制到项目
- **触发条件**: 复制后由 SKILL.md 的 `description` 字段控制触发
