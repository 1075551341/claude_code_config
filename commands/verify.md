---
description: 交叉验证与质量门检查（④验证阶段）
---

# /verify — 交叉验证与质量门检查

对已完成工作执行完整验证。Claim → Evidence，每项验证必须附证据。

**正文 SSOT**：Read `skills/verification-before-completion/SKILL.md`（verify_tier 两档 + 全部验证清单 + 质量门 + 审查委派 + 反合理化检查）。

流程：确认 verify_tier → 按清单逐项验证并贴命令证据 → 输出会话终验（R20）逐条回放（满足/遗漏/错改/漏改/原功能；漏改含文档/备注与文件/配置一致；模板见 verification skill）→ 输出验证报告（通过）或失败项+修复方案（不声称完成）。

> 硬门兜底：Stop 时 `stop-verification-gate.py` 自动核查，未通过 exit 2 阻止停止。
