---
name: ship
description: 发布管线，整合测试→覆盖审计→推送→开PR→可选部署验证。
layer: supplement
source: garrytan/gstack + obra/superpowers
disable-model-invocation: true
loading_tier: L3
---

# Ship

## 触发
- 手动：`/ship`

## 流程
1. 同步 main 分支（git merge main 或 rebase）
2. 运行完整测试套件（无框架则引导）
3. 审计测试覆盖率
4. 运行 /document-release 更新文档
5. 推送变更
6. 创建/更新 PR
7. 可选：/land-and-deploy 合并+部署+验证
8. 可选：/canary 启动监控循环

## 与 finishing-a-development-branch 的关系
ship 是完整发布管线；finishing-branch 提供分支完成后的选项（merge/PR/keep/discard）。ship 包含 finishing-branch 的核心功能并扩展。

## 质量门
- 测试全部通过
- 覆盖率未下降
- 无安全告警
- 文档已更新
