---
name: ship
description: 发布管线，整合测试→覆盖审计→推送→开PR→可选部署验证。
triggers: [发布, ship, 推送开PR, 部署验证]
layer: supplement
source: garrytan/gstack + obra/superpowers
disable-model-invocation: true
loading_tier: L3
---

# Ship

> v11: 原 `agents/release-engineer.md`（同步main→测试→覆盖审计→推送→开PR）已并入本技能，流程即其管线。

## 触发
- 手动：`/ship`

## 流程
1. 同步 main 分支（git merge main 或 rebase）
2. 运行完整测试套件（无框架则引导）
3. 审计测试覆盖率
4. 运行 /document-release 更新文档
5. 推送变更
6. 创建/更新 PR
7. 可选：完整部署闭环（approved PR→verified production）用 `catalog/agents/land-and-deploy.md`（v11 降级 catalog，按需复制启用）
8. 可选：/canary 启动监控循环

## CI 模板引用（原 release-engineer 附注）
可引用 `templates/github-actions/` 中的 claude-code-action 模板进行 CI 配置：4 后端支持（Node/Python/Go/Rust）、结构化 JSON 输出、PR 自动创建与状态同步。

## 与 finishing-a-development-branch 的关系
ship 是完整发布管线；finishing-branch 提供分支完成后的选项（merge/PR/keep/discard）。ship 包含 finishing-branch 的核心功能并扩展。

## PR 格式（v11 自 /ship 并入）

```
[type] scope: description

## Summary
- 变更点 1
- 变更点 2

## Test plan
- [x] 测试项 1
- [x] 测试项 2

## 验证清单
- [x] 构建通过
- [x] 测试通过
- [x] 安全审查通过

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

## 预发布检查清单（gstack 风格，v11 自 /ship 并入）

```
□ 构建通过（无错误、无新 warning）
□ 测试通过（单元 + 集成，覆盖率不低于基线）
□ Eng Review 通过（eng-reviewer PASS）
□ 安全审查通过（如触发 security review）
□ 文档更新（README / API docs / 变更日志）
□ 无硬编码密钥 / .env 泄露
□ 依赖无已知漏洞（npm audit / pip audit）
□ 无回滚风险
```

## 质量门
- 测试全部通过
- 覆盖率未下降
- 无安全告警
- 文档已更新
- CI 全部通过 + Code Review 通过 + 无回滚风险
