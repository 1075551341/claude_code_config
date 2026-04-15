---
name: architecture-diagrams
description: 系统架构图绘制，使用Mermaid绘制流程图、时序图、架构图
triggers: [架构图, Mermaid, 流程图, 时序图, ER图, 系统图, 技术图表]
---

# 架构图绘制

## Mermaid 图表类型

### 流程图

```mermaid
graph TD
    A[开始] --> B{判断}
    B -->|Yes| C[操作1]
    B -->|No| D[操作2]
    C --> E[结束]
    D --> E
```

```mermaid
graph LR
    Client --> Gateway --> ServiceA
    Gateway --> ServiceB
    ServiceA --> Database
    ServiceB --> Cache
```

### 时序图

```mermaid
sequenceDiagram
    participant U as 用户
    participant A as API
    participant D as 数据库

    U->>A: 发送请求
    A->>D: 查询数据
    D-->>A: 返回结果
    A-->>U: 响应数据
```

```mermaid
sequenceDiagram
    Client->>+Server: HTTP请求
    Server->>+Database: SQL查询
    Database-->>-Server: 结果
    Server->>+Cache: 更新缓存
    Cache-->>-Server: 确认
    Server-->>-Client: 响应
```

### 类图

```mermaid
classDiagram
    class User {
        +String name
        +String email
        +login()
        +logout()
    }
    class Order {
        +Int id
        +Date created
        +addItem()
    }
    User "1" --> "*" Order
```

### ER图（实体关系）

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    ORDER ||--|{ ITEM : contains
    USER {
        int id PK
        string name
        string email
    }
    ORDER {
        int id PK
        date created
        string status
    }
    ITEM {
        int id PK
        string name
        float price
    }
```

### 状态图

```mermaid
stateDiagram-v2
    [*] --> 待处理
    待处理 --> 处理中: 开始
    处理中 --> 已完成: 成功
    处理中 --> 失败: 异常
    已完成 --> [*]
    失败 --> 待处理: 重试
```

### 甘特图

```mermaid
gantt
    title 项目开发计划
    dateFormat YYYY-MM-DD
    section 设计
    需求分析 :a1, 2024-01-01, 7d
    UI设计 :a2, after a1, 5d
    section 开发
    前端开发 :b1, after a2, 14d
    后端开发 :b2, after a2, 14d
    section 测试
    集成测试 :c1, after b1, 7d
```

## 常见架构模式

### 微服务架构

```mermaid
graph TB
    Client --> Gateway
    Gateway --> Auth[认证服务]
    Gateway --> User[用户服务]
    Gateway --> Order[订单服务]
    Gateway --> Product[商品服务]

    Auth --> Redis[Redis缓存]
    User --> DB1[用户数据库]
    Order --> DB2[订单数据库]
    Product --> DB3[商品数据库]

    MQ[消息队列] -.-> Order
    MQ -.-> Product
```

### 前端架构

```mermaid
graph TD
    Browser[浏览器] --> SPA[单页应用]
    SPA --> Router[路由]
    Router --> Views[视图层]
    Views --> Components[组件]
    Components --> Store[状态管理]
    Store --> API[API层]
    API --> Backend[后端服务]
```

### 数据流架构

```mermaid
graph LR
    Source[数据源] --> ETL[ETL处理]
    ETL --> Clean[清洗]
    Clean --> Transform[转换]
    Transform --> Load[加载]
    Load --> DW[数据仓库]
    DW --> BI[BI分析]
    BI --> Report[报表]
```

## 图表最佳实践

### 布局方向

```
TD/TB - 从上到下（默认）
LR - 从左到右
RL - 从右到左
BT - 从下到上
```

### 连接样式

```
--> 实线箭头
--- 实线无箭头
-.- 虚线箭头
-.- 虚线无箭头
==> 加粗箭头
-- 文字标注 --
```

### 形状选择

```
[] 矩形（默认）
() 圆角矩形
((())) 圆形
{} 菱形（判断）
{{}} 六边形
[/] 平行四边形
```

## 使用场景

| 图表类型 | 适用场景           |
| -------- | ------------------ |
| 流程图   | 业务流程、算法逻辑 |
| 时序图   | API交互、协议流程  |
| 类图     | 面向对象设计       |
| ER图     | 数据库设计         |
| 状态图   | 状态机、生命周期   |
| 甘特图   | 项目计划、时间线   |

## 生成和渲染

### Markdown 内嵌

````markdown
```mermaid
graph TD
    A --> B
```
````

````

### HTML 渲染
```html
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<div class="mermaid">
graph TD
    A --> B
</div>
````

### CLI 导出图片

```bash
# 安装
npm install -g @mermaid-js/mermaid-cli

# 导出 PNG
mmdc -i diagram.mmd -o diagram.png

# 导出 SVG
mmdc -i diagram.mmd -o diagram.svg -b white
```

### Python 调用

```python
import subprocess

def render_mermaid(code: str, output: str, format: str = 'png'):
    """渲染 Mermaid 图表"""
    with open('temp.mmd', 'w') as f:
        f.write(code)

    subprocess.run([
        'mmdc',
        '-i', 'temp.mmd',
        '-o', output,
        '-f', format
    ])
```
