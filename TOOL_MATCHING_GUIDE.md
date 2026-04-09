---
description: 精确工具匹配指南 | 未明确工具时的选择策略
---

# MCP 工具精确匹配指南

当用户未明确指定工具时，按以下决策树自动匹配：

## 核心原则

1. **语义优先**: 根据用户意图而非关键词匹配
2. **场景明确**: 每个工具都有最佳使用场景
3. **组合使用**: 复杂任务组合多个工具
4. **编辑器兼容**: 优先使用 MCP 标准工具

## 工具匹配速查表

###  信息获取类

| 场景 | 首选工具 | 触发关键词 |
|------|---------|-----------|
| 搜索任意主题 | mcp1_web_search_exa | 搜索、查找、资料 |
| 获取特定URL内容 | mcp2_fetch | 网页、URL、获取内容 |
| GitHub仓库文档 | mcp0_read_wiki_structure | github.com、仓库、文档 |
| 技术库最新API | mcp0_ask_question | React/Vue/Node文档 |

###  文件操作类

| 场景 | 首选工具 | 触发关键词 |
|------|---------|-----------|
| 读取项目文件 | ead_file | 读取文件、查看代码 |
| 批量读取 | mcp4_read_multiple_files | 多个文件、批量读取 |
| 搜索代码 | code_search | 搜索代码、查找函数 |
| 文本搜索 | grep_search | grep、查找字符串 |
| 目录结构 | mcp4_list_directory | 目录、文件列表 |

###  浏览器自动化类

| 场景 | 首选工具 | 触发关键词 |
|------|---------|-----------|
| E2E测试、表单 | mcp6_browser_navigate | 浏览器、测试页面 |
| 网页截图 | mcp6_browser_take_screenshot | 截图、网页截图 |
| 点击交互 | mcp6_browser_click | 点击按钮、操作页面 |
| PDF生成 | mcp8_puppeteer_screenshot | PDF、打印页面 |

###  开发工具类

| 场景 | 首选工具 | 触发关键词 |
|------|---------|-----------|
| Git操作 | mcp5_git_status/log/diff | git、提交、分支 |
| Figma设计稿 | mcp3_get_design_context | figma、设计稿、UI |
| 流程图生成 | mcp3_generate_diagram | 流程图、mermaid |

###  知识与记忆类

| 场景 | 首选工具 | 触发关键词 |
|------|---------|-----------|
| 存储记忆 | mcp7_create_memory | 记住、保存上下文 |
| 查询记忆 | mcp7_search_nodes | 查询记忆、之前说过 |
| 复杂推理 | skill -> sequentialthinking | 分析、规划、决策 |

## 常见场景决策树

### 场景1: \ 帮我分析这个API问题\
`
用户: 帮我分析这个API问题
 有API文档URL?  mcp2_fetch 获取文档
 是GitHub项目?  mcp0_ask_question 查询仓库
 需要搜索解决方案?  mcp1_web_search_exa
`

### 场景2: \优化这个函数\
`
用户: 优化这个函数
 先读取文件  read_file
 分析性能瓶颈  code_search 查找相关代码
 应用优化  edit
`

### 场景3: \设计一个系统架构\
`
用户: 设计一个系统架构
 启动推理  skill (design-brainstorming)
 生成流程图  mcp3_generate_diagram
 存储方案  mcp7_create_memory
`

## 技能触发器

| 技能 | 触发词 |
|------|--------|
| design-brainstorming | 设计、架构、brainstorm |
| systematic-debugging | bug、错误、调试、报错 |
| code-refactor | 重构、优化代码、整理 |
| 	est-driven-development | TDD、测试驱动、先写测试 |
| writing-plans | 写计划、实施计划、规划 |
| plan-execution | 执行计划、按计划实施 |

## 最佳实践

1. **复杂任务先技能**: 不确定时调用对应技能
2. **信息获取并行**: 多个独立搜索并行执行
3. **文件操作批量**: 相关文件批量读取
4. **浏览器测试Playwright**: 优先使用 Playwright MCP
5. **记忆持久化**: 重要上下文及时存储

---

_最后更新：2026-04-09_
