# Catalog Agents — 按需复制

> 此目录提供领域专用 agent 定义，按需复制到项目 `.claude/agents/` 使用。
> 全局 agents 在 `~/.claude/agents/`，始终可用，无需从此目录复制。

## 使用策略

```
全局 agents/ (24) → 五柱核心 + gstack 审查，会话始终可用
catalog/agents/ (27) → 领域专用，按需复制到项目
```

## 复制命令

```powershell
# 复制单个 agent 到当前项目
copy ~/.claude/catalog/agents/<name>.md .\.claude\agents\

# 或使用迁移脚本
python ~/.claude/scripts/migrate-from-legacy.py --project . --agent <name>
```

## Catalog 清单（27）

| Agent | 领域 | 用途 |
|-------|------|------|
| accessibility-expert | 前端 | 无障碍审查 |
| ai-engineer | AI/ML | AI 功能开发 |
| api-versioner | 后端 | API 版本管理 |
| backend-developer | 后端 | 后端开发 |
| ceo-reviewer | 产品 | 产品审查（catalog版） |
| changelog-generator | 文档 | 变更日志生成 |
| compliance-checker | 安全 | 合规审查 |
| context-rot-monitor | 运维 | 上下文腐烂监控 |
| cpp-reviewer | C++ | C++ 代码审查 |
| csharp-reviewer | C# | C# 代码审查 |
| data-engineer | 数据 | 数据工程 |
| database-expert | 数据库 | 数据库设计 |
| designer | 设计 | UI/UX 审查（catalog版） |
| devops-engineer | DevOps | CI/CD + 基础设施 |
| docs-expert | 文档 | 技术文档 |
| eng-reviewer | 工程 | 工程审查（catalog版） |
| flutter-reviewer | Flutter | Flutter 审查 |
| frontend-developer | 前端 | 前端开发 |
| git-expert | 工具 | Git 高级操作 |
| go-reviewer | Go | Go 代码审查 |
| java-reviewer | Java | Java 代码审查 |
| kotlin-reviewer | Kotlin | Kotlin 代码审查 |
| mobile-developer | 移动 | 移动开发 |
| python-reviewer | Python | Python 代码审查 |
| rust-reviewer | Rust | Rust 代码审查 |
| security-expert | 安全 | 安全专家 |
| swift-reviewer | Swift | Swift 代码审查 |

## 与全局 agents/ 的关系

- **去重原则**: catalog 中的 agent 若与全局 agents/ 同名 → 优先使用全局版本
- **特殊化原则**: catalog 提供语言/领域特定版本（如 `go-reviewer`, `rust-reviewer`）
- **按需加载**: 全局 24 agents 已覆盖通用场景，catalog 仅在特定领域需求时启用
