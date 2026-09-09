---
name: requesting-code-review
description: 请求代码审查，向审查者提供精确的上下文
triggers: [请求代码审查, 提供精确上下文, 代码审查请求]
layer: supplement
source: obra/superpowers
disable-model-invocation: true
loading_tier: L3
---

# 请求代码审查

## @Examples

```
用户: "这个功能完成了，帮我审查"
Claude: /requesting-code-review → 审查前刷图 → 派发 gstack 审查路由 → 填写七维模板

用户: "PR #123 需要审查"
Claude: 获取变更 → 识别关键文件 → 提供上下文 → 派发 eng-reviewer（及并行路由）
```

## 核心原则

**使用精确构建的上下文派发代码审查子代理——绝不是你的会话历史。**

政策 SSOT → `skills/verification-before-completion/SKILL.md`。并行路由 → `rules/AGENTS.md`。

## 必须审查的时机

- 有交付物编辑（含文档）且将声称完成
- 子代理驱动开发中每个任务完成后
- 完成主要功能后 / 合并到主分支前

计划未批准 / 仅 `*.plan.md` / 纯澄清问答（无交付）不派审。

## 审查流程

### 步骤 1: 审查前刷图

`last_edit` 之后增量 refresh 双图（`graph_freshness.refresh_incremental`）。`last_pre_review_graph_ts > last_edit_ts` 才允许派审。同一轮并行审查者共享这一次刷新。

### 步骤 2: 获取提交范围

```bash
BASE_SHA=$(git merge-base origin/main HEAD)
HEAD_SHA=$(git rev-parse HEAD)
```

### 步骤 3: 派发审查代理（gstack 路由）

使用 Task 工具派发，**禁止 `resume` 上一轮审查者**。Cursor 无对应 `subagent_type` 时用 `generalPurpose`，prompt 必须声明角色。

- 必派：`eng-reviewer`
- 产品/新功能：`+ ceo-reviewer`
- UI/UX：`+ designer` + `dx-reviewer`
- 测试边界：`+ qa`
- 安全敏感：`+ security-reviewer`

无依赖：同一条消息多个 `Task` 并行。有依赖串行。

**每个审查者 prompt 必须含**：本轮已刷新；CRG `get_impact_radius` / `get_review_context`（有图）+ `codegraph_explore` blast-radius；对照原始要求做七维；只读，禁止改文件。

### 步骤 4: 七维模板（缺任一项本轮无效）

```markdown
## 审查请求

### 实现内容
[简要描述]

### 计划/需求
[原始要求关键词]

### 提交范围
- BASE_SHA: [基准]
- HEAD_SHA: [当前]
- 本轮已刷新双图：是

### 关键文件
- `path/to/file` - [变更说明]

### 七维（审查者必须逐项输出）
- 满足：（承认/反驳/弃权 + 证据）
- 遗漏：
- 错改：
- 漏改：（文档/注释已同步或「无文档影响」）
- 原功能：（保持 + 测试/冒烟证据）
- 影响范围：（CRG get_impact_radius / IMPACT / blast）
- 问题是否解决：已解决 | 未解决 | 部分解决（证据：观察输出）
结论：PASS / NEEDS-CHANGES
```

### 步骤 5: 处理反馈

主会话合并本批清单。任一 `NEEDS-CHANGES` / 七维缺项 → 整轮不通过，派**一次** `change-implementer` 集中改齐。干净 PASS 即停。轮次 → `quality_gates.review_max_rounds`。

## 红旗警告

```markdown
🚨 以下行为会导致审查失败：

- "这太简单了，跳过审查"
- resume 上一轮审查者
- 审查前未在 last_edit 之后刷图
- 发现一条就停审或边审边改
- 缺七维仍给 PASS
- 不提供上下文 / 让审查者改文件
```
