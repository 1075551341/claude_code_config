# 门控注入文本 SSOT（v10.15.0）

> 双端共用：Claude Code hooks 与 Cursor Guard hooks 均读取本文件。
> 修改后无需改 hook 代码；Cursor 侧改动随 deploy-cursor-guard.ps1 生效。
> v10.15：分类门新增 TDD/SDD 默认关闭、疑难禁直接改、重复问题去重；完成验证门新增残留引用+回归保持。
> v10.14：完成验证门升级硬阻断（Claude Stop hook exit 2）+ 引入 code-review-graph 审查/验证专用层。

## P0分类门

【门控 · 会话开始必做】
本消息为 hook 强制注入，非可选建议。第一轮回复前必须执行分类：

1. Read ~/.claude/skills/task-triage/SKILL.md（本会话未读则必读；Phase0 前置盘点 → 简单=关联需改≤2+白名单+六维全低+模型匹配+attempt=1，分类树以该文件为唯一 SSOT）
2. 输出分类契约：大类 | 需改文件列表 | 模型档(当前≥所需) | verify_tier | 置信度 | 成功标准(1句)
   - 简单 → Read change-impact-analysis → **一次改齐** → 完成前验证（比例；仅 attempt=1）
   - 非简单 Bug（多文件/根因不明/执行升档）→ triage 分级 → Read systematic-debugging → 全量验证
   - 非简单 功能/架构/配置/删除 → 先访谈用户（grill：一次一问+推荐答案，≤5问）→ Read brainstorming（HARD-GATE：用户批准设计前禁止实现）
   - 非简单 调研 → Read skills/deep-research（L3 双源）
   - 初判简单但 attempt≥2 / 首轮未解决 → **执行升档非简单** + verify_tier=全量
   - **默认不启用 TDD/SDD**（v10.15）：仅用户显式要求（TDD/测试先行/子Agent派发）才触发；非简单默认主会话按骨架直接执行
   - **疑难/歧义项禁止直接修改**（v10.16 机械触发）：满足任一即视为疑难，必须 grill 澄清 + 输出影响面清单（≥3 项：目标符号/调用方/被调用方），用户确认后再改：
     ① 需求含「或/还是/可能」不确定性词 ② 影响面清单≥3 文件 ③ 变更命中黑名单 ④ 跨模块调用链
   - **疑似重复问题**：先查 claude-mem + 上轮制品/结论，禁止从头重做（issue-tracker hook 会辅助提示）
     禁止凭记忆跳过；skill 已读且范围未变可不重复 Read。

## 完成验证门

【门控 · 完成前必做 — v10.14 硬阻断】
检测到你即将声称完成。按配置（verification-before-completion，L2 门控）：

1. Read ~/.claude/skills/verification-before-completion/SKILL.md
2. 确认 verify_tier（比例 | 全量）；持续处理同一问题则必须全量，且执行已升档非简单
3. 实际运行验证命令（测试/lint/构建/功能核验），贴出输出证据
4. 项目已建 code-review-graph（存在 .code-review-graph/ 目录）：调用 detect_changes_tool
   检查 test-gap 与高风险函数，将受影响文件纳入验证范围
5. 残留引用检测：Grep 旧函数名/旧路径/旧配置key — 结果必须为 0（任何修改必须，两档同强制）
6. 非功能变更回归保持：重构/格式/配置类变更必须核验原功能行为不变（运行既有测试或冒烟核验），保留必要注释
7. 证据齐全后方可声称完成；跳过验证的完成声明视为无效（R1）
   先证据后断言，禁止"应该没问题"；禁止以「轻量验证」跳过本 skill。
8. 会话终验（R20）：全部任务完成后按用户原始要求逐条回放（禁止把实现重做一遍），
   输出满足/遗漏/错改/漏改/原功能；非功能变更「原功能」必须写保持并给测试或冒烟证据。
   模板见 skills/verification-before-completion；未输出不得声称完成。

⚠️ 硬门兜底（Claude Code）：Stop 时 stop-verification-gate.py 将强制核查——
   ① 变更范围轻量自动检查（ruff/tsc，仅变更文件，25s 超时）
   ② 测试/验证命令证据（最后一次编辑后须有验证命令运行记录）
   ③ 预期符合性（存在活跃 plan/spec 制品须对照 tasks 清单）
   ④ 会话内编辑 ≥3 个代码文件须委派 eng-reviewer 审查
      注：这是 Stop 门的**代理规则**（按会话累计编辑数触发），与 task-triage 的六维分类**不是同一维度**；
      2 文件的非简单任务不触发本项，但仍须按 verify_tier=全量 完成验证。
   ⑤ 工作树交叉核查：git 实际变更文件必须全部出现在本会话编辑记录中；
      出现未追踪变更（MCP/Shell 写入）→ 视为验证范围缺口，须纳入验证后再声称完成。
   ⑥ 会话终验（R20）：最后一条回复须含按原始要求逐条回放的满足/遗漏/错改/漏改/原功能（纯文档编辑同样适用；非功能变更必须证明原功能保持）。
   未通过 → exit 2 阻止停止并回灌强制补验（上限 3 次，达上限放行标 DONE_WITH_CONCERNS）。
   Cursor 侧无 Stop 阻断能力，enforce_mode=soft 仅注入提醒，硬门在 Claude Code 兜底。

## 变更影响门

【门控 · 每个文件首次编辑前必做】
范围不明不修改（change-impact-analysis，L1 常驻）。本次编辑前必须：

1. 改前优先成熟方案或已有全局通用处理（禁止为单编辑器/单场景发明特例；不够才开特例）
2. codegraph_explore 目标符号 blast-radius（或 codegraph_impact）
3. Grep 全项目引用（函数名/类型名/配置 key/路径）
4. 配置类改动查 MANIFEST.yaml depends_on 与 INDEX 同步
   输出受影响文件清单（至少含 3 项：目标符号/调用方/被调用方）后再改；残留引用 >0 不得声称完成。
   疑难/歧义项禁止直接修改（v10.16 机械触发：不确定性词/清单≥3 文件/黑名单/跨模块链）— 先 grill 澄清 + 用户确认影响面清单后再动手。
   未索引项目降级：先 Grep 全扫并在结果中标注 DONE_WITH_CONCERNS。
