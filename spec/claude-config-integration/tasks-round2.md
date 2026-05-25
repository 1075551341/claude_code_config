# 24 仓库审计整合实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 从 mattpocock/skills 精选 2 个 skill 补入 .claude，更新关联索引文件

**Architecture:** 五柱骨架不变，skills 25→27，在现有 skills/ 目录新增 triage 和 improve-codebase-architecture 两个中文精简版 SKILL.md，同步更新 CLAUDE.md/SPEC.md/MANIFEST.yaml 索引

**Tech Stack:** Markdown + YAML

---

### Task 1: 创建 skills/triage/SKILL.md

**Files:**
- Create: `C:\Users\DELL\.claude\skills\triage\SKILL.md`

- [ ] **Step 1: 创建目录**

```bash
mkdir -p /c/Users/DELL/.claude/skills/triage
```

- [ ] **Step 2: 写入 SKILL.md**

写入文件 `C:\Users\DELL\.claude\skills\triage\SKILL.md`：

```markdown
---
name: triage
description: 问题分诊，Bug报告/Issue的第一道分类关卡，判断类型、严重度、指派方向
triggers: [问题分诊, bug分类, issue分类, triage, 问题报告, 用户反馈]
layer: supplement
source: mattpocock/skills
---

# 问题分诊

收到问题报告后，先分类再路由，禁止跳过分类直接修。

## 分诊流程

1. **复现判断** — 能复现吗？有最小复现步骤吗？
2. **范围评估** — 影响面多大？涉及哪些模块？
3. **分类** — bug / feature / 疑问 / 技术债
4. **严重度** — P0(阻断) / P1(严重) / P2(一般) / P3(低)
5. **指派方向** — 哪个领域/谁处理

## 输出格式

```
## 分诊报告
- 分类: [bug/feature/疑问/技术债]
- 严重度: [P0/P1/P2/P3]
- 影响范围: [模块/文件]
- 建议下一步: [skill/systematic-debugging | skill/brainstorming | 追问用户]
- 预估工时: [小/中/大]
```

## 路由规则

| 分类 | 路由 |
|------|------|
| bug + 可复现 | → skill/systematic-debugging |
| feature 请求 | → skill/brainstorming |
| 疑问 | → 直接回答或追问 |
| 技术债 | → skill/improve-codebase-architecture |

## 边界

- triage 只做分类，不做修复
- 不确定分类时标注"待确认"并追问用户
- 与 systematic-debugging 的边界：triage 回答"这是什么问题"，debugging 回答"为什么发生"
```

- [ ] **Step 3: 验证文件**

```bash
wc -l /c/Users/DELL/.claude/skills/triage/SKILL.md
```

- [ ] **Step 4: Commit**

```bash
git add skills/triage/SKILL.md
git commit -m "feat: add triage skill (mattpocock/skills)"
```

---

### Task 2: 创建 skills/improve-codebase-architecture/SKILL.md

**Files:**
- Create: `C:\Users\DELL\.claude\skills\improve-codebase-architecture\SKILL.md`

- [ ] **Step 1: 创建目录**

```bash
mkdir -p /c/Users/DELL/.claude/skills/improve-codebase-architecture
```

- [ ] **Step 2: 写入 SKILL.md**

写入文件 `C:\Users\DELL\.claude\skills\improve-codebase-architecture\SKILL.md`：

```markdown
---
name: improve-codebase-architecture
description: 架构渐进改进，对现有代码做领域驱动的结构优化，跨文件重构
triggers: [架构改进, 重构, 代码结构, architecture, refactor, 模块拆分, 领域驱动]
layer: supplement
source: mattpocock/skills
---

# 架构渐进改进

对现有代码库做领域驱动的架构改进，跨文件、渐进式、不破坏现有功能。

## 何时触发

- 模块超过 800 行
- 跨文件职责混乱
- 循环依赖
- 边界不清晰

## 改进流程

1. **识别** — 分析 CONTEXT.md 或项目结构，定位边界违规
2. **方案** — 提出拆分/合并方案，最小改动原则
3. **验证** — 确认不破坏现有功能（现有测试全通过）
4. **渐进** — 一次改一个边界，不搞大爆炸重构

## 输出格式

```
## 架构改进方案
- 问题: [边界违规/循环依赖/职责混乱]
- 影响文件: [列表]
- 改进方向: [拆分/合并/提取接口]
- 风险: [低/中/高]
- 验证方法: [运行测试/手动验证]
```

## 原则

- **最小改动** — 能拆分不重写
- **保持兼容** — 对外接口不变
- **渐进提交** — 每步可独立 revert
- **先有测试** — 无测试先补测试再重构

## 边界

- 与 brainstorming 的边界：brainstorming 设计新功能，本 skill 改进已有代码
- 与 code-reviewer 的边界：code-reviewer 审查单次 PR，本 skill 做跨文件的架构层面改进
```

- [ ] **Step 3: 验证文件**

```bash
wc -l /c/Users/DELL/.claude/skills/improve-codebase-architecture/SKILL.md
```

- [ ] **Step 4: Commit**

```bash
git add skills/improve-codebase-architecture/SKILL.md
git commit -m "feat: add improve-codebase-architecture skill (mattpocock/skills)"
```

---

### Task 3: 更新 CLAUDE.md

**Files:**
- Modify: `C:\Users\DELL\.claude\CLAUDE.md`

- [ ] **Step 1: 读取当前文件**

```bash
cat /c/Users/DELL/.claude/CLAUDE.md
```

- [ ] **Step 2: 找到 "P0 强制 Skill" 段落后插入新 skill 索引**

在 CLAUDE.md 的 "P0 强制 Skill（4 个）" 表格之后、"任务决策树" 之前，插入：

```markdown
## Mattpocock 精选 Skill（2）

| Skill | 触发 |
|-------|------|
| triage | Bug 报告/Issue → 分类 → 路由 |
| improve-codebase-architecture | 架构改进、跨文件重构、模块拆分 |
```

- [ ] **Step 3: 更新任务决策树**

将现有的：
```
收到任务
├─ 简单（≤3文件、需求明确、无方案选择）→ 执行 → 验证
└─ 非简单 → skill/brainstorming → ...
```

改为：
```
收到任务
├─ Bug 报告/Issue → skill/triage → 分类路由
├─ 简单（≤3文件、需求明确、无方案选择）→ 执行 → 验证
└─ 非简单 → skill/brainstorming → skill/writing-plans → 执行 → skill/verification-before-completion
```

- [ ] **Step 4: 更新命令速查表**

在命令速查表中新增一行：

```markdown
| /triage | 问题分诊（→ triage skill） |
```

- [ ] **Step 5: 验证 CLAUDE.md 行数**

```bash
wc -l /c/Users/DELL/.claude/CLAUDE.md
```

- [ ] **Step 6: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md with triage and improve-codebase-architecture skills"
```

---

### Task 4: 更新 SPEC.md

**Files:**
- Modify: `C:\Users\DELL\.claude\SPEC.md`

- [ ] **Step 1: 读取当前 SPEC.md skills 相关段落**

- [ ] **Step 2: 更新规模约束表**

将：
```
| 全局 skills | ≤25 | 25（superpowers 13 + 扩展 8 + meta 4） |
```
改为：
```
| 全局 skills | ≤28 | 27（superpowers 13 + 扩展 8 + meta 4 + mattpocock 2） |
```

- [ ] **Step 3: 在 "扩展 8" 之后新增 "mattpocock 精选 2"**

```markdown
**mattpocock 精选 2**：triage, improve-codebase-architecture
```

- [ ] **Step 4: Commit**

```bash
git add SPEC.md
git commit -m "docs: update SPEC.md skills inventory (25→27, limit 25→28)"
```

---

### Task 5: 更新 MANIFEST.yaml

**Files:**
- Modify: `C:\Users\DELL\.claude\MANIFEST.yaml`

- [ ] **Step 1: 在 concerns 段新增 triage 和 improve-codebase-architecture 归属**

在 `concerns:` 下新增：

```yaml
  triage:
    owner: skill/triage
    source: mattpocock/skills
    excludes: [skill/systematic-debugging]

  architecture_improvement:
    owner: skill/improve-codebase-architecture
    source: mattpocock/skills
    excludes: [skill/brainstorming, agent/code-reviewer]
```

- [ ] **Step 2: 验证 YAML 语法**

```bash
python -c "import yaml; yaml.safe_load(open('/c/Users/DELL/.claude/MANIFEST.yaml'))" && echo "YAML valid"
```

- [ ] **Step 3: Commit**

```bash
git add MANIFEST.yaml
git commit -m "docs: add triage and architecture_improvement to MANIFEST"
```

---

### Task 6: 微调 rules/CONTEXT.md

**Files:**
- Modify: `C:\Users\DELL\.claude\rules\CONTEXT.md`

- [ ] **Step 1: 更新阈值表措辞**

将：
```markdown
| 50% | 逻辑断点 `/compact` |
```
改为：
```markdown
| 50% | 逻辑断点 `/compact`，释放已完成上下文 |
```

- [ ] **Step 2: Commit**

```bash
git add rules/CONTEXT.md
git commit -m "docs: clarify 50% threshold action in CONTEXT.md"
```

---

### Task 7: 验证 — sync 兼容性

- [ ] **Step 1: Dry-run 同步**

```bash
powershell -ExecutionPolicy Bypass -File /c/Users/DELL/.claude/scripts/sync.ps1 -DryRun
```

Expected: 无报错，新 skills/triage 和 skills/improve-codebase-architecture 出现在 skills/ 目录链接中

- [ ] **Step 2: 确认新 skill 目录可被 sync 发现**

```bash
ls /c/Users/DELL/.claude/skills/triage/SKILL.md && echo "triage OK"
ls /c/Users/DELL/.claude/skills/improve-codebase-architecture/SKILL.md && echo "improve-codebase-architecture OK"
```

---

### Task 8: 验证 — 职责重叠检查

- [ ] **Step 1: Grep 检查 triage 与 systematic-debugging 无 trigger 重叠**

```bash
grep -i "triage\|分诊" /c/Users/DELL/.claude/skills/systematic-debugging/SKILL.md || echo "No overlap with debugging"
grep -i "debug\|调试\|根因" /c/Users/DELL/.claude/skills/triage/SKILL.md || echo "No overlap with triage"
```

- [ ] **Step 2: Grep 检查 improve-codebase-architecture 与 brainstorming 无 trigger 重叠**

```bash
grep -i "refactor\|重构\|架构改进" /c/Users/DELL/.claude/skills/brainstorming/SKILL.md || echo "No overlap with brainstorming"
grep -i "新功能\|brainstorm\|头脑风暴" /c/Users/DELL/.claude/skills/improve-codebase-architecture/SKILL.md || echo "No overlap with architecture skill"
```

---

### Task 9: 验证 — Git diff 全量审查

- [ ] **Step 1: 查看完整 diff**

```bash
git diff HEAD~6..HEAD --stat
```

- [ ] **Step 2: 确认变更范围**

Expected 输出应包含：
```
 CLAUDE.md
 MANIFEST.yaml
 SPEC.md
 rules/CONTEXT.md
 skills/improve-codebase-architecture/SKILL.md
 skills/triage/SKILL.md
```
6 个文件，无意外变更。

- [ ] **Step 3: 最终验证**

```bash
git status
```

Expected: clean working tree
