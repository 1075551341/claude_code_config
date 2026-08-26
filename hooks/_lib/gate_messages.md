# 门控注入文本 SSOT（v11.4.3）

> 双端共用：Claude Code hooks 与 Cursor Guard hooks 均读取本文件。
> 完整清单只在 skill；本文件只留短指针（每段 ≤12 行）。改文本不改 hook 代码。
> Cursor Stop：`followup_message` 等效硬门（非 permission deny）。Claude Stop：exit 2。

## P0分类门

【门控 · 会话开始必做】

1. Read ~/.claude/skills/task-triage/SKILL.md（本会话未读则必读）
2. 输出分类契约：大类 | 需改文件 | 模型档 | verify_tier | 置信度 | 成功标准
   简单=Phase0+关联需改≤2+白名单+六维全低+模型匹配+attempt=1；否则非简单（按 skill 路由）
3. 疑难（或/还是/可能、清单≥3、黑名单、跨模块）禁止直接改；重复问题先 claude-mem。

## 完成验证门

【门控 · 完成前必做】
Read ~/.claude/skills/verification-before-completion/SKILL.md

1. 运行测试/lint/构建并贴证据（R1）；Grep 残留引用必须为 0；验证证据须为观察输出（命令/测试/文件），不信叙述（v11.3.5）
2. 会话终验 R20：满足/遗漏/错改/漏改/原功能；漏改须含「文档」或「无文档影响」；原功能须含证据/测试/冒烟；核对范围=影响面全部相关项（非仅已编辑文件）
3. 全量档：有 .code-review-graph/ 时调用 detect_changes_tool；交叉验证全项
   Claude Stop 不合格 → exit 2。Cursor Stop 不合格 → followup_message 续轮（loop_limit=max_blocks）。

## 变更影响门

【门控 · 每个文件首次编辑前必做】

1. 改前优先成熟方案或已有全局通用处理
2. codegraph_explore 目标 blast-radius（无索引 → Grep 全扫 + DONE_WITH_CONCERNS）
3. Grep 全项目引用；配置类查 MANIFEST.yaml depends_on 与 INDEX
   范围不明不修改。疑难先 grill。残留引用 >0 不得声称完成。

## 初次修改验收门

【门控 · 每个文件首次编辑后必做】
对照本文件及其 blast-radius 全部相关项，五维逐条核验：需求(未满足=遗漏) / 错改 / 漏改(同类引用+INDEX/MANIFEST/README/注释/命令同步；无则写「无文档影响」) / 原功能(非功能变更须测试或冒烟证据) / 工具(codegraph/Grep 残留=0)。禁止只验当前文件、禁止「应该没影响」。
完整模板与判定细则 → skills/verification-before-completion/SKILL.md「场景G」（v11.3.6 收敛为指针）。
