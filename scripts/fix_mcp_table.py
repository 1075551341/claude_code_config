#!/usr/bin/env python3
"""Fix MCP table in CLAUDE.md - replace hardcoded mcp0/mcp1 prefixes with generic names"""
import re

filepath = r'C:\Users\DELL\.claude\CLAUDE.md'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the old MCP table with the new one
old_table_start = '| 自然语言关键词 | 首选工具 | 备用方案 | 典型场景 | 工具前缀 |'
old_table_end = '| Linear、项目管理 | linear | - | 任务跟踪 | - |'

new_table = """| 自然语言关键词 | 首选工具 | 备用方案 | 典型场景 |
|--------------|---------|---------|---------|
| "技术文档、API文档、用法、reference" | ctx7 | brave | 查询库/框架最新 API |
| "搜索、查找资料、semantic search" | exa | brave | AI 语义搜索 |
| "https://...、网页内容、URL" | fetch | - | 直接获取指定 URL |
| "figma.com、设计稿、UI 设计" | figma | - | 设计稿转代码 |
| "git 状态、提交历史、分支" | git | gh | 本地 Git 操作 |
| "截图、网页测试、E2E、表单填写" | pw | puppeteer | Playwright 浏览器测试 |
| "记住、保存上下文、跨会话记忆" | memory | - | 持久化重要信息 |
| "PDF 生成、打印页面" | puppeteer | pw | Chrome 自动化 |
| Redis、缓存 | redis | - | 缓存操作 |
| SQLite、本地数据库 | sqlite | - | 軽量数据库 |
| PostgreSQL、PG | postgres | - | 生产数据库 |
| Docker、容器 | docker | - | 容器管理 |
| 时间、时区 | time | - | 时间计算 |
| 复杂推理、架构设计 | thinking | - | 多方案比较 |
| Slack、通知 | slack | - | 消息发送 |
| Linear、项目管理 | linear | - | 任务跟踪 |"""

# Find start and end positions
start_idx = content.find(old_table_start)
end_idx = content.find(old_table_end)

if start_idx != -1 and end_idx != -1:
    end_idx += len(old_table_end)
    new_content = content[:start_idx] + new_table + content[end_idx:]
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'SUCCESS: Replaced MCP table (chars {start_idx}-{end_idx})')
else:
    print(f'NOT FOUND: start={start_idx}, end={end_idx}')
