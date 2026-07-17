---
description: L3 深度调研（Firecrawl+Exa+交叉验证，Read skills/deep-research）
---

# /deep-research — 深度调研

系统化深度研究：广度探索 → 深度下钻 → 多样性验证 → 综合检查。

## 调研分级（using-superpowers SSOT）

| 档位   | 场景                           | 加载                                 |
| ------ | ------------------------------ | ------------------------------------ |
| L1     | 单点事实、API 签名             | Context7 或 Exa 单次                 |
| L2     | 方案对比、最佳实践             | Exa + Firecrawl 单页                 |
| **L3** | 本命令、技术选型、竞品全面分析 | Read `skills/deep-research/SKILL.md` |

**升级**：L1 不足 → L2；L2 不足或用户 `/deep-research` → L3。禁止无因跳级。

**前置**：claude-mem search（R18）→ 项目内代码用 codegraph（非 Firecrawl）。

## L3 执行链

1. Read `skills/deep-research/SKILL.md`
2. **Firecrawl**（`user-crawl` MCP）抓取网页
3. **Exa** 语义搜索补充来源
4. **Context7** 验证库/API 声明
5. **codegraph** 仅项目内结构（非网页调研）

## 输出要求

- 关键结论至少 **2 个独立来源** 交叉验证
- 标注信息时效性与可信度
- 矛盾信息显式列出，不掩盖不确定性
- 禁止仅凭训练数据断言

## 与执行区分

| 类型               | 路由                                |
| ------------------ | ----------------------------------- |
| 网页/竞品/趋势调研 | 本命令 + Firecrawl/Exa              |
| 代码库结构探索     | codegraph（+ cbm L4 架构场景）      |
| 功能实现           | /plan → /execute（非本命令）        |
| >30min 自主编排    | L3 `claude-to-deerflow`（非本命令） |
