# 零使用率审计 v10.6.0（2026-07-29）

> 依据原提示词 Phase 0 要求：逐项标注技能/Agent"最近是否被实际触发"，零触发项降级或废弃。
> **方法论与局限（先读）**：
> - 数据源 A：`projects/*.jsonl` 会话语料 44 文件 / 7.7MB（近约 6 周 Claude Code 会话）技能/Agent 名频次
> - 数据源 B：`history.jsonl` 用户提示语料
> - 数据源 C：claude-mem search 提示记录（信号弱，仅辅助）
> - **局限**：语料主要是"配置仓库自身优化"会话（自指偏差，brainstorming/writing-plans 偏高）；Cursor 侧触发不可见；`disable-model-invocation` 的 slash-only 技能会低报。结论仅作降级**候选**，逐项用户确认后才动配置。

## 一、技能（44）

### 活跃（>10 次，语料A）

| 技能 | 次数 |
|------|-----:|
| brainstorming | 169 |
| ship | 92 |
| deep-research | 91 |
| writing-plans | 71 |
| using-superpowers | 44 |
| systematic-debugging | 28 |
| skill-creator | 14 |

### 低频（1–10 次）

writing-skills(6) · office-hours(6) · subagent-driven-development(6) · finishing-a-development-branch(6) · requesting-code-review(6) · executing-plans(6) · using-git-worktrees(6) · change-impact-analysis(6) · verification-before-completion(6) · autoplan(6) · test-driven-development(6) · receiving-code-review(6) · triage(1)

> 注：P0/L2 门控技能（change-impact、verification、executing-plans 等）即使低报也**不可降级**——它们是流程门控，非常驻但强制。

### 零触发候选（语料 A+B 均为 0，共 23）

adr-management · browser-qa · caveman-compress · claude-mem-maintenance · claude-to-deerflow · code-refactoring · context-engineering · design-pipeline · frontend-design-pattern-applier · frontend-library-advisor · frontend-refactor-proposer · git-workflow · improve-codebase-architecture · instinct-learning · karpathy-guidelines · memory-compression · onboarding-guide · pr-workflow · skill-reviewer · spec-validation · structured-artifacts · taste-memory · test-edge-case-analyzer · workstream-management

**处置建议（待逐项确认）**：

| 分组 | 项 | 建议 |
|------|-----|------|
| 保留（基础设施性质，触发词清晰） | structured-artifacts / context-engineering / memory-compression / caveman-compress / claude-mem-maintenance / karpathy-guidelines / git-workflow / pr-workflow / adr-management / workstream-management / spec-validation | 已为 L3 按需，常驻成本=0，保留观察 |
| 保留（v10.5.2 新增，样本期太短） | code-refactoring / frontend-*×3 / skill-reviewer / test-edge-case-analyzer | 新增技能，下轮审计再判 |
| 降级候选（建议确认后处理） | browser-qa / claude-to-deerflow / design-pipeline / instinct-learning / improve-codebase-architecture / onboarding-guide / taste-memory | 零触发且非流程必需；建议降级为 catalog/ 或标注"观察一轮" |

## 二、Agent（25）

| 分类 | 项 |
|------|-----|
| 活跃 | qa(249) / architect(148) / planner(130) / code-explorer(20) / code-reviewer(20) |
| 低信号（~10，疑为枚举讨论非真实调用） | 其余 20 个 |

> Agent 频次无法区分"真实 Task 调用"与"文档枚举提及"，不做降级建议；gstack 审查组是审查路由组成部分，保留。

## 三、Hooks

12 激活核心已在 settings.json 注册（自动触发，无"零使用"概念）；`_archive/` 35 个已正名为非激活资产库（W5 完成）；3 个 stub 已除名（W5 完成）。

## 四、结论

1. **P0/P1 常驻集合无需降级**：当前常驻仅 CLAUDE.md + CORE（瘦身版）+ ROUTER + CURSOR-EDITOR，无零触发项占用常驻预算。
2. **零触发技能均为 L3 按需加载**，常驻 token 成本为零 → 不强制删除，按上表分组处理。
3. 7 个"降级候选"技能：**用户已确认（2026-07-29）全部保留观察一轮**，下轮审计再判。
4. 下一轮审计建议：会话结束 hook 记录真实 skill 触发日志（数据来源改进），Cursor 侧单独采样。
