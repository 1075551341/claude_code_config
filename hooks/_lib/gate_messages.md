# 门控注入文本 SSOT（v10.12.0）

> 双端共用：Claude Code hooks 与 Cursor Guard hooks 均读取本文件。
> 修改后无需改 hook 代码；Cursor 侧改动随 deploy-cursor-guard.ps1 生效。

## P0分类门

【门控 · 会话开始必做】
本消息为 hook 强制注入，非可选建议。第一轮回复前必须执行分类：

1. Read ~/.claude/skills/task-triage/SKILL.md（本会话未读则必读；简单=关联需改≤2+白名单+六维全低+模型匹配，分类树以该文件为唯一 SSOT）
2. 输出分类契约：大类 | 需改文件列表 | 模型档 | verify_tier | 置信度 | 成功标准(1句)
   - 简单（含关联需改≤2可复现Bug）→ Read change-impact-analysis 后直接改 → 完成前验证（比例；持续处理则全量）
   - 非简单 Bug（多文件/根因不明）→ triage 分级 → Read systematic-debugging → 全量验证
   - 非简单 功能/架构/配置/删除 → 先访谈用户（grill：一次一问+推荐答案，≤5问收敛：目标/范围/风险/约束/输出）→ Read brainstorming（HARD-GATE：用户批准设计前禁止实现）
   - 非简单 调研 → Read skills/deep-research（L3 双源）
     禁止凭记忆跳过；skill 已读且范围未变可不重复 Read。

## 完成验证门

【门控 · 完成前必做】
检测到你即将声称完成。按配置（verification-before-completion，L2 门控）：

1. Read ~/.claude/skills/verification-before-completion/SKILL.md
2. 确认 verify_tier（比例 | 全量）；持续处理同一问题则必须全量
3. 实际运行验证命令（测试/lint/构建/功能核验），贴出输出证据
4. 证据齐全后方可声称完成；跳过验证的完成声明视为无效（R1）
   先证据后断言，禁止"应该没问题"；禁止以「轻量验证」跳过本 skill。

## 变更影响门

【门控 · 本会话首次编辑前必做】
范围不明不修改（change-impact-analysis，L1 常驻）。本次编辑前必须：

1. codegraph_explore 目标符号 blast-radius（或 codegraph_impact）
2. Grep 全项目引用（函数名/类型名/配置 key/路径）
3. 配置类改动查 MANIFEST.yaml depends_on 与 INDEX 同步
   输出受影响文件清单后再改；残留引用 >0 不得声称完成。
   未索引项目降级：先 Grep 全扫并在结果中标注 DONE_WITH_CONCERNS。
