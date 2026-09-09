---
description: 交叉验证与质量门检查（④验证阶段）
---

# /verify — 交叉验证与质量门检查

对已完成工作执行完整验证。Claim → Evidence，每项验证必须附证据。

**正文 SSOT**：Read `skills/verification-before-completion/SKILL.md`（verify_tier 两档 + 全部验证清单 + 质量门 + 审查委派 + 反合理化检查）。

流程：确认 verify_tier → 按清单逐项验证并贴命令证据 → 输出会话终验（R20）七维回放（满足/遗漏/错改/漏改/原功能/影响范围/问题是否解决；核对范围=blast-radius 全部相关项；漏改须含文档或无文档影响；原功能须含证据；模板见 verification skill）→ 输出验证报告（通过）或失败项+修复方案（不声称完成）。

> 硬门兜底：Claude Stop `stop-verification-gate.py` 未通过 exit 2。Cursor 完成门不 followup。审查政策 → `skills/verification-before-completion/SKILL.md`。验证全绿后才执行 `sync.ps1`。
