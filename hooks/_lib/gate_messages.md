# 门控注入文本 SSOT（v11.4.14）

> 双端共用：Claude Code hooks 与 Cursor Guard hooks 均读取本文件。
> 完整清单只在 skill；本文件只留短指针（每段 ≤12 行）。改文本不改 hook 代码。
> **完成验证门仅 Claude Stop exit 2 / 人工 Read**。Cursor 不再注入本段（Stop followup 会刷会话面板）。

## P0分类门

【门控 · 会话开始必做】

1. Read ~/.claude/skills/task-triage/SKILL.md（本会话未读则必读）
2. 输出分类契约：大类 | 需改文件 | 模型档 | verify_tier | 置信度 | 成功标准
   简单=Phase0+关联需改≤2+白名单+六维全低+模型匹配+attempt=1；否则非简单（按 skill 路由）
3. 分类后查 config/scenario-router.yaml（必加载+质量门；INDEX L3 可追加）。疑难禁止直接改；重复问题先 claude-mem。

## 完成验证门

【门控 · 完成前必做】
有未验证编辑时才执行。计划未批准 / 本轮零编辑 / 仅计划文件 → 停止，不要续跑。
Read verification-before-completion；贴观察输出。
R20 各一行：满足（承认/反驳/弃权）/ 遗漏 / 错改 / 漏改（文档/注释或无文档影响）/ 原功能（证据）/ 影响范围（CRG/IMPACT/blast）。
有代码/配置改动：开审前双图 ensure；change-implementer 修改 → 验证 → eng-reviewer 一次找齐（并行须 inherit）。干净 PASS 即停。每轮全新开审（禁止 resume），日常最多 3 轮（单任务覆盖须用户显式声明）。只读免审。

## 变更影响门

【门控 · 每个文件首次编辑前必做】

1. 改前优先成熟方案或已有全局通用处理
2. 有 CRG 图：get_minimal_context + get_impact_radius（有 git diff 再 detect_changes）；叠加 codegraph_explore blast-radius
3. eligible git 仓须已有双图（SessionStart 已 init/update）。无图禁止 Grep/编辑/查询 MCP；hook 会再 ensure，仍失败则 deny。
   Grep 全项目引用；配置类查 MANIFEST depends_on。范围不明不修改。

## 初次修改验收门

【门控 · 每个文件首次编辑后必做】
对照本文件及其 blast-radius 全部相关项，五维逐条核验：需求(未满足=遗漏) / 错改 / 漏改(同类引用+INDEX/MANIFEST/README/注释/命令同步；无则写「无文档影响」) / 原功能(非功能变更须测试或冒烟证据) / 工具(CRG 影响面或 codegraph/Grep 残留=0)。禁止只验当前文件、禁止「应该没影响」。
完整模板与判定细则 → skills/verification-before-completion/SKILL.md「场景G」（v11.3.6 收敛为指针）。
