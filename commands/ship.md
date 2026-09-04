---
description: 验证通过后合并部署（触发 skill/ship）
---

# /ship — 合并、部署

验证全部通过后，执行合并和部署。

**正文 SSOT**：Read `skills/ship/SKILL.md`（完整管线：同步 main→测试→覆盖审计→推送→开 PR + PR 格式 + 预发布检查清单 + 质量门；v11 已并入原 release-engineer）。

流程摘要：确认所有验证通过 → 检查 Git 状态 → 按 skill 管线执行 → 可选部署闭环走 `agents/land-and-deploy.md`。
