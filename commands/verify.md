---
description: 交叉验证与质量门检查（④验证阶段）
---

# /verify — 交叉验证与质量门检查

对已完成工作执行完整验证。Claim → Evidence，每项验证必须附证据。

**正文 SSOT**：Read `skills/verification-before-completion/SKILL.md`（verify_tier 两档 + 全部验证清单 + 质量门 + 审查委派 + 反合理化检查）。

流程：确认 verify_tier → 按清单逐项验证并贴命令证据 → 输出会话终验（R20）七维回放（满足/遗漏/错改/漏改/原功能/影响范围/问题是否解决；核对范围=blast-radius 全部相关项；漏改须含文档或无文档影响；原功能须含证据；模板见 verification skill）→ 输出验证报告（通过）或失败项+修复方案（不声称完成）。

> 硬门兜底：Claude Stop `stop-verification-gate.py` 未通过 exit 2。Cursor 完成门不 followup。审查政策 → `skills/verification-before-completion/SKILL.md`。验证全绿后才执行 `sync.ps1`。

<!-- spine:stage-gate -->
## 门控（派生自 config/workflow.yaml，改配置后 `python scripts/workflow.py render`，勿手改）

- 阶段：④验证 | skill：`skills/verification-before-completion/SKILL.md` | 角色：session
- 进入：执行阶段 exit 满足
- 退出（全部满足才进入下一阶段）：
  - verify_tier 对应清单全部附命令证据
  - 审查前刷图（last_edit 之后）
  - 本轮全新独立审查全部 PASS（completion + review.routing）
- verify_tier：
  - `proportional`：初判简单且 attempt=1：代码级 + 功能级 + 关联文件；贴命令证据
  - `full`：非简单或持续处理：比例全部 + 交叉验证全项 + 残留引用

**完成定义**（派生自 config/workflow.yaml，改配置后 `python scripts/workflow.py render`，勿手改）：没有独立审查 PASS ⇒ 任务未完成；适用全部轨道（simple, bug, non_simple, research），简单/只读/文档任务同样适用。

- verify_tier 清单全部附观察到的命令输出
- 本轮全新独立审查者（非实现者、未 resume）给出 PASS，七维齐全，且 review.pass_requires 两道门（符合预期要求 + 原功能保持）均附证据通过
- **PASS = 两道门同时满足**（任一不满足即 NEEDS-CHANGES）：
  1. **符合预期要求**：每项改动都对应原始要求 / 验收标准；逐条无遗漏；无破坏要求的范围外改动（满足 + 遗漏 + 错改 维）。证据：原始要求逐条 → 对应改动或明确的反驳/弃权理由。
  2. **原功能保持**：起点 tip 上既有的预期行为全部保持，无静默回归；有意的行为变更逐条显式列出并对应原始要求（原功能 维）。证据：相关测试 / validate / check 脚本的观察输出 + 相对起点 tip 的行为差异说明。
- 一轮 = 改 → 验 → 刷图 → 并行全新审查（一次找齐）；目标第 1 轮 PASS，上限 **3** 轮。
- 3 轮仍未 PASS ⇒ **BLOCKED**（未完成），不得声称完成，也不得改为「跳过审查」。
- 自检、实现者自签、验证命令全绿都不能替代独立审查；仅用户显式豁免时放行，状态记 `DONE_WITH_CONCERNS`。
- 站立目标 `/goal`：所有修改符合预期要求；且原功能保持不变（= 上述两道门，不是第三道门，也不另建 Stop hook）。
<!-- /spine:stage-gate -->
