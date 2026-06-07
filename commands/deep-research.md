---
description: 多角度深度调研（Firecrawl+Exa+交叉验证，触发 catalog/skills/deep-research）
---

# /deep-research — 深度调研

系统化深度研究：广度探索 → 深度下钻 → 多样性验证 → 综合检查。

## 触发

1. 加载 `catalog/skills/deep-research/SKILL.md`
2. 外部信息：**Firecrawl**（`crawl` MCP / firecrawl CLI）抓取网页
3. 语义搜索：**Exa**（Cursor 插件 MCP）补充来源
4. 技术文档：**Context7** MCP（库/API 官方文档）
5. 代码结构：**codegraph** MCP（项目内，非网页调研）

## 输出要求

- 关键结论至少 **2 个独立来源** 交叉验证
- 标注信息时效性与可信度
- 矛盾信息显式列出，不掩盖不确定性
- 调研类任务默认走此管线，禁止仅凭训练数据断言

## 与执行区分

| 类型 | 路由 |
|------|------|
| 网页/竞品/趋势调研 | 本命令 + Firecrawl/Exa |
| 代码库结构探索 | codegraph / understand-anything |
| 功能实现 | /plan → /execute（非本命令） |
