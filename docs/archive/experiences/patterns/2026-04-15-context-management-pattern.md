---
date: 2026-04-15
confidence: 0.8
category: context-management
status: active
verified_count: 1
---

# 上下文管理经验模式

> 来源：zilliztech/claude-context, obra/superpowers

---

## 模式1: Merkle DAG 增量同步

```markdown
---
name: merkle-dag-incremental-sync
date: 2026-04-15
confidence: 0.9
source: claude-context
tags: [context, sync, performance]
---

# Merkle DAG 增量同步

## 背景

每次会话都全量扫描代码库导致性能低下，尤其是在大型代码库中。

## 模式

使用 Merkle DAG 进行增量变更检测：

1. 文件哈希快照存储在 `~/.context/merkle/*.json`
2. 检测变更：added, modified, removed
3. 只重索引变更文件，而非全量重索引

## 验证

在 1000+ 文件的代码库中，从 45s 降低到 3s。

## 提取决策

- 置信度: 0.9
- 提取为: hook + context system
- 原因: 显著提升大型代码库的响应速度
```

---

## 模式2: AST感知分块

```markdown
---
name: ast-aware-chunking
date: 2026-04-15
confidence: 0.85
source: claude-context
tags: [context, chunking, semantics]
---

# AST感知分块

## 背景

基于字符数的分块会切断语义单元，导致上下文碎片化。

## 模式

1. 解析 AST，识别语言特定的逻辑节点
2. 按函数/类/方法边界切分
3. 保持语义完整性
4. 300字符 overlap 确保跨块引用

## 验证

在 TypeScript 代码库中，上下文召回率提升 40%。

## 提取决策

- 置信度: 0.85
- 提取为: context system
- 原因: 保持语义完整性是关键
```

---

## 模式3: 子代理精确上下文构造

````markdown
---
name: subagent-precise-context
date: 2026-04-15
confidence: 0.95
source: superpowers
tags: [subagent, context, isolation]
---

# 子代理精确上下文构造

## 背景

子代理继承父会话历史导致上下文污染和性能下降。

## 模式

子代理应该从不继承会话历史：

1. 精确构造所需上下文
2. 指定单一问题域
3. 明确成功标准
4. 明确禁止的行为
5. 具体返回格式

## 反模式

```markdown
# 错误：继承全部历史

"你现在的上下文是：[全部历史]"

# 正确：精确构造

"你是一个代码审查专家。审查 {file} 中的 {issue}。
成功标准：找到所有 X 类型的问题。
禁止：修改代码。
返回格式：JSON {issues: []}"
```
````

## 提取决策

- 置信度: 0.95
- 提取为: subagent workflow
- 原因: 多次验证，几乎总是有效

````

---

## 模式4: SessionStart上下文注入

```markdown
---
name: sessionstart-context-injection
date: 2026-04-15
confidence: 0.9
source: superpowers
tags: [session, context, bootstrap]
---

# SessionStart上下文注入

## 背景
每次新会话需要重新加载技能定义，导致效率低下。

## 模式
在 SessionStart 时注入 using-superpowers：
```xml
<EXTREMELY_IMPORTANT>
You have superpowers.
**Below is the full content of your 'superpowers:using-superpowers' skill**
</EXTREMELY_IMPORTANT>
````

## 验证

会话启动时间减少 30%，技能调用准确率提升。

## 提取决策

- 置信度: 0.9
- 提取为: hook
- 原因: 显著提升会话初始化效率

```

```
