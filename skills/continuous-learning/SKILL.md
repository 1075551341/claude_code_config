---
name: continuous-learning
description: ★强制执行★ 每次会话结束必须提取学习，不可跳过。从会话中自动提取可复用模式并固化
triggers:
  [
    ★强制执行★ 每次会话结束必须提取学习，不可跳过。从会话中自动提取可复用模式并固化,
  ]
---

# 持续学习模式（强制执行）

> **铁律：每次非简单任务完成后，必须执行学习提取流程。**

## 强制执行流程

```
任务完成后
├─ 简单任务(改bug/改配置) → 可跳过
└─ 非简单任务 → 必须执行 ↓
    ├─ 观察: 识别本次会话中的模式
    ├─ 提取: 将模式转为instinct
    ├─ 固化: 高置信度instinct转为skill/rule
    └─ 存储: 写入experiences/
```

## 学习流程

### 1. 观察（必须执行）

- 哪些工具组合最有效？
- 哪些操作重复出现？（可自动化）
- 哪些错误反复出现？（需预防）
- 哪些反问最有价值？（需固化）

### 2. 提取（必须执行）

从成功操作中提取"instinct"：

- **触发条件**：什么情况下使用此模式
- **操作步骤**：具体的工具调用序列
- **适用范围**：项目级 / 全局级
- **置信度**：0-1（使用次数 / 总机会次数）

### 3. 固化（自动执行）

- 置信度 > 0.7 的 instinct → 转为 skill
- 置信度 > 0.9 的 skill → 转为 rule
- 项目级 instinct → `<project>/.claude/instincts/`
- 全局级 instinct → `~/.claude/experiences/`

### 4. 应用（下次会话自动加载）

- 新会话启动时加载相关 instincts
- 匹配当前上下文的 instinct 自动建议
- 用户确认后执行

## Instinct 格式

```yaml
name: react-component-pattern
trigger: "创建 React 组件" 或 "新 .tsx 文件"
steps:
  1. 创建文件 + 类型接口
  2. 实现组件 + hooks
  3. 添加样式 (CSS Modules)
  4. 编写测试
scope: project
confidence: 0.85
learned_from: "session-2026-04-10"
```

## 防护机制

- **项目隔离**：instinct 不会跨项目污染
- **置信度门槛**：低于 0.5 的不建议
- **人工审核**：新 instinct 首次应用需用户确认
- **定期清理**：30 天未使用的 instinct 降权
