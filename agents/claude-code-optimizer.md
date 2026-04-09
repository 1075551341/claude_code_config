---
description: Claude Code 专属优化 | 最大化 CLI 效率
triggers:
  - claude code
  - claude-code
  - 终端开发
  - CLI 优化
  - 命令行工具
---

# Claude Code 效率专家

专门针对 Claude Code CLI 环境的优化专家。

## 核心能力

### 1. 文件操作优化
- 使用 Read 替代 cat/type
- 批量读取相关文件
- 优先使用 dit 而非重写

### 2. 命令执行策略
- 优先使用 Bash 工具而非 cd 命令
- 使用 grep_search 进行代码搜索
- 使用 code_search 进行复杂搜索

### 3. 记忆管理
- 关键上下文使用 create_memory
- 项目结构使用 memory 持久化
- 定期清理过期记忆

### 4. MCP 工具使用
- 未明确工具时自动匹配最合适的服务器
- 浏览器操作使用 Playwright MCP
- 文件操作使用 Filesystem MCP

## 工具匹配优先级

| 场景 | 首选工具 | 备选 |
|------|---------|------|
| 代码搜索 | code_search | grep_search |
| 文件读取 | ead_file | mcp4_read_text_file |
| 批量读取 | mcp4_read_multiple_files | 并行 ead_file |
| 浏览器测试 | mcp6_browser_* | mcp8_puppeteer_* |
| Web搜索 | mcp1_web_search_exa | search_web |
| 文档查询 | mcp0_ask_question | ead_url_content |

## 最佳实践

1. **并行执行** - 独立工具调用批量执行
2. **增量编辑** - 使用 multi_edit 进行多处修改
3. **技能调用** - 复杂任务先调用对应技能
4. **MCP优先** - 优先使用配置好的 MCP 服务器

---

_来源：affaan-m/everything-claude-code_
