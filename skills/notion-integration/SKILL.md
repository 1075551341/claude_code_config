---
name: notion-integration
description: 使用Notion API
triggers: [使用Notion API, 集成Notion工作区, 操作Notion数据库]
---

# Notion 集成

## 快速开始

### 创建集成

1. 访问 https://www.notion.so/my-integrations
2. 点击 "New integration"
3. 获取 Internal Integration Token
4. 在目标页面添加连接

### 安装SDK

```bash
# Python
pip install notion-client

# Node.js
npm install @notionhq/client
```

## Python客户端

```python
from notion_client import Client

notion = Client(auth="your_integration_token")
notion = Client(auth="secret_xxx...")

# 获取页面
page = notion.pages.retrieve(page_id="page_id")

# 创建页面
new_page = notion.pages.create(
    parent={"database_id": "database_id"},
    properties={
        "Title": {"title": [{"text": {"content": "新页面"}}]}
    }
)

# 更新页面
notion.pages.update(
    page_id="page_id",
    properties={
        "Status": {"select": {"name": "完成"}}
    }
)
```

### Node.js客户端

```javascript
const { Client } = require("@notionhq/client");

const notion = new Client({ auth: "secret_xxx..." });

// 查询数据库
async function queryDatabase(databaseId) {
  const response = await notion.databases.query({
    database_id: databaseId,
    filter: {
      property: "Status",
      select: { equals: "进行中" },
    },
  });
  return response.results;
}

// 创建页面
async function createPage(databaseId, title) {
  await notion.pages.create({
    parent: { database_id: databaseId },
    properties: {
      Name: {
        title: [{ text: { content: title } }],
      },
    },
  });
}
```

---

## 数据库操作

### 查询数据库

```python
def query_notion_database(database_id, filter_conditions=None):
    """
    查询Notion数据库

    参数：
        database_id: 数据库ID
        filter_conditions: 过滤条件

    返回：
        list: 查询结果
    """
    query_params = {"database_id": database_id}

    if filter_conditions:
        query_params["filter"] = filter_conditions

    results = []
    has_more = True
    start_cursor = None

    while has_more:
        if start_cursor:
            query_params["start_cursor"] = start_cursor

        response = notion.databases.query(**query_params)
        results.extend(response["results"])

        has_more = response["has_more"]
        start_cursor = response.get("next_cursor")

    return results

# 使用示例
# 查询状态为"进行中"的任务
tasks = query_notion_database(
    "database_id",
    {
        "property": "状态",
        "select": {"equals": "进行中"}
    }
)
```

### 创建数据库条目

```python
def create_database_entry(database_id, properties):
    """
    创建数据库条目

    参数：
        database_id: 数据库ID
        properties: 属性字典

    返回：
        dict: 创建的页面
    """
    # 转换属性格式
    notion_properties = {}

    for key, value in properties.items():
        if isinstance(value, str):
            notion_properties[key] = {
                "title": [{"text": {"content": value}}]
            }
        elif isinstance(value, (int, float)):
            notion_properties[key] = {"number": value}
        elif isinstance(value, bool):
            notion_properties[key] = {"checkbox": value}
        elif isinstance(value, list) and len(value) > 0:
            notion_properties[key] = {
                "multi_select": [{"name": item} for item in value]
            }

    return notion.pages.create(
        parent={"database_id": database_id},
        properties=notion_properties
    )
```

### 更新数据库条目

```python
def update_database_entry(page_id, properties):
    """
    更新数据库条目

    参数：
        page_id: 页面ID
        properties: 要更新的属性
    """
    return notion.pages.update(
        page_id=page_id,
        properties=properties
    )

# 示例：更新任务状态
notion.pages.update(
    page_id="task_page_id",
    properties={
        "状态": {"select": {"name": "完成"}},
        "完成时间": {"date": {"start": "2025-01-15"}}
    }
)
```

---

## 页面内容操作

### 添加内容块

```python
def add_blocks(page_id, blocks):
    """
    向页面添加内容块

    参数：
        page_id: 页面ID
        blocks: 内容块列表
    """
    return notion.blocks.children.append(
        block_id=page_id,
        children=blocks
    )

# 添加文本块
add_blocks("page_id", [
    {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"type": "text", "text": {"content": "这是一段文本"}}]
        }
    }
])

# 添加标题
add_blocks("page_id", [
    {
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": "标题"}}]
        }
    }
])

# 添加待办事项
add_blocks("page_id", [
    {
        "type": "to_do",
        "to_do": {
            "rich_text": [{"type": "text", "text": {"content": "待办事项"}}],
            "checked": False
        }
    }
])

# 添加代码块
add_blocks("page_id", [
    {
        "type": "code",
        "code": {
            "rich_text": [{"type": "text", "text": {"content": "print('Hello')"}}],
            "language": "python"
        }
    }
])
```

### 获取页面内容

```python
def get_page_content(page_id):
    """
    获取页面的所有内容块

    参数：
        page_id: 页面ID

    返回：
        list: 内容块列表
    """
    blocks = []
    has_more = True
    start_cursor = None

    while has_more:
        params = {"block_id": page_id}
        if start_cursor:
            params["start_cursor"] = start_cursor

        response = notion.blocks.children.list(**params)
        blocks.extend(response["results"])

        has_more = response["has_more"]
        start_cursor = response.get("next_cursor")

    return blocks
```

---

## 常用场景

### 任务管理同步

```python
def sync_tasks_from_external(api_url, database_id):
    """
    从外部系统同步任务到Notion

    参数：
        api_url: 外部API地址
        database_id: Notion数据库ID
    """
    import requests

    # 获取外部任务
    response = requests.get(api_url)
    external_tasks = response.json()

    for task in external_tasks:
        # 检查是否已存在
        existing = notion.databases.query(
            database_id=database_id,
            filter={
                "property": "外部ID",
                "rich_text": {"equals": task["id"]}
            }
        )

        if existing["results"]:
            # 更新现有任务
            notion.pages.update(
                page_id=existing["results"][0]["id"],
                properties={
                    "标题": {"title": [{"text": {"content": task["title"]}}]},
                    "状态": {"select": {"name": task["status"]}}
                }
            )
        else:
            # 创建新任务
            notion.pages.create(
                parent={"database_id": database_id},
                properties={
                    "标题": {"title": [{"text": {"content": task["title"]}}]},
                    "状态": {"select": {"name": task["status"]}},
                    "外部ID": {"rich_text": [{"text": {"content": task["id"]}}]}
                }
            )
```

### 日报生成

```python
def generate_daily_report(database_id, date):
    """
    生成日报

    参数：
        database_id: 任务数据库ID
        date: 日期字符串
    """
    # 查询当日完成的任务
    completed = notion.databases.query(
        database_id=database_id,
        filter={
            "and": [
                {"property": "状态", "select": {"equals": "完成"}},
                {"property": "完成时间", "date": {"equals": date}}
            ]
        }
    )

    # 查询进行中的任务
    in_progress = notion.databases.query(
        database_id=database_id,
        filter={"property": "状态", "select": {"equals": "进行中"}}
    )

    # 生成报告
    report = f"""
# 日报 - {date}

## 今日完成
{chr(10).join([f"- {task['properties']['标题']['title'][0]['text']['content']}" for task in completed['results']])}

## 进行中
{chr(10).join([f"- {task['properties']['标题']['title'][0]['text']['content']}" for task in in_progress['results']])}
    """

    return report
```

---

## 注意事项

```
API限制：
- 请求速率限制：3 requests/second
- 单次查询最多返回100条
- 页面内容最多100层嵌套

权限要求：
- 集成需要被添加到目标页面/数据库
- 某些操作需要特定权限

最佳实践：
- 使用分页处理大量数据
- 缓存数据库schema
- 错误重试机制
```

---

## 相关技能

- `note-management` - 笔记管理
- `api-development` - API开发
- `python-automation` - Python自动化
