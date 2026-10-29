---
description: 验证通过后合并部署（触发 skill/ship）
---

# /ship — 合并、部署

验证全部通过后，执行合并和部署。

**正文 SSOT**：Read `skills/ship/SKILL.md`（完整管线：同步 main→测试→覆盖审计→推送→开 PR + PR 格式 + 预发布检查清单 + 质量门；v11 已并入原 release-engineer）。

流程摘要：确认所有验证通过 → 检查 Git 状态 → 按 skill 管线执行 → 可选部署闭环走 `catalog/agents/land-and-deploy`。

<!-- spine:stage-gate -->
## 门控（派生自 config/workflow.yaml，改配置后 `python scripts/workflow.py render`，勿手改）

- 阶段：ⓢ交付 | skill：`skills/ship/SKILL.md` | 角色：session
- 进入：任务已完成（completion.done_when 全部满足）；用户明确要求提交 / 开 PR / 发布
- 退出（全部满足才进入下一阶段）：
  - 用户要求的交付物完成（commit / PR / 发布），CI 绿
<!-- /spine:stage-gate -->
