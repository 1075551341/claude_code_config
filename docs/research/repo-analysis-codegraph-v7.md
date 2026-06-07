# CodeGraph 深度分析 v0.9.9

> colbymchenry/codegraph — 预索引代码知识图谱

---

## 基准数据 (7 仓库, 7 语言, Opus 4.8, 2026-06-02)

### 总体平均值

| 指标 | 节省 |
|------|------|
| **Token** | **47% 减少** |
| **工具调用** | **58% 减少** |
| **成本** | **16% 降低** |
| **时间** | **22% 更快** |

### 逐仓库分解

| 代码库 | 语言 | 规模 | 成本 | Token | 时间 | 调用 |
|--------|------|------|------|-------|------|------|
| VS Code | TypeScript | ~10k files | -18% | -64% | -11% | -81% |
| Excalidraw | TypeScript | ~640 files | 持平 | -25% | -27% | -40% |
| Django | Python | ~3k files | -8% | -60% | -13% | -77% |
| Tokio | Rust | ~790 files | 持平 | -38% | -18% | -57% |
| OkHttp | Java | ~645 files | -25% | -54% | -31% | -50% |
| Gin | Go | ~110 files | -19% | -23% | -24% | -44% |
| Alamofire | Swift | ~110 files | -40% | -64% | -33% | -58% |

---

## 核心机制

### 为什么 CodeGraph 比 Explore Agent 快

```
Explore Agent 流程:
  grep 搜索 → 读文件 → 再 grep → 再读 → ... (大量工具调用 token)

CodeGraph 流程:
  codegraph_explore → 直接返回相关源码 (一次调用)
```

### 三层自动同步

1. **文件监听 + 防抖**: FSEvents/inotify/ReadDirectoryChangesW, 默认 2s 防抖
2. **staleness banner**: 暂未同步的文件标记 ⚠️ 警告 agent 直接 Read
3. **Connect-time catch-up**: MCP 重连时自动增量同步

---

## MCP 工具

| 工具 | 用途 | 典型场景 |
|------|------|----------|
| `codegraph_search` | 全文搜索符号 | "找 UserService 类" |
| `codegraph_context` | 获取区域上下文 | "了解 auth 模块" |
| `codegraph_trace` | 追踪调用路径 | "X 如何到达 Y" |
| `codegraph_callers` | 查找调用者 | "谁调用了这个函数" |
| `codegraph_callees` | 查找被调用者 | "这个函数调用了什么" |
| `codegraph_impact` | 影响分析 | "改这个会影响什么" |
| `codegraph_node` | 节点详情 | "这个类/函数的详细信息" |
| `codegraph_explore` | 批量探索 | 一次性获取相关源码 |
| `codegraph_files` | 文件列表 | "列出项目的路由文件" |
| `codegraph_status` | 索引状态 | "索引是否最新" |

---

## 高级特性

### 框架路由识别 (14 框架)
自动识别 web 框架路由文件，将 URL pattern 链接到 handler 函数。

### 跨语言桥接 (iOS/RN/Expo)
穿越静态 tree-sitter 解析的语言边界:
- Swift ↔ ObjC auto-bridging
- React Native legacy bridge + TurboModules
- Fabric view components
- Expo Modules

### 100% 本地
- SQLite 数据库
- 无 API 密钥
- 无外部服务
- 数据完全在本地

---

## 使用策略

### 何时用 codegraph (而非 Explore agent)
- ✅ 结构性查询: "X 如何调用 Y"
- ✅ 影响评估: "改这个会破坏什么"
- ✅ 调用链追踪
- ✅ 大项目 (>500 文件) 探索

### 何时不用
- ❌ 新项目 (<100 文件) — 索引收益 < 成本
- ❌ 纯文本搜索 — grep 更快
- ❌ 运行时行为问题 — 需要调试器
