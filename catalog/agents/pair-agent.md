---
name: pair-agent
description: 多 AI Agent 浏览器共享协作。触发词：多 Agent 协作、共享浏览器、pair、agent 互联。
tools: Read, Write, Bash, Glob, Grep, WebFetch
model: sonnet
---

# Pair Agent — 多 Agent 浏览器共享

> 来源: garrytan/gstack `/pair-agent` | v0.19

## 核心价值

让多个 AI Agent 共享同一个浏览器环境 — 每个 Agent 独立 tab，互相可见但隔离。

## 流程

### 1. 启动 headed mode
- 启动可见浏览器（非 headless）
- 开放 ngrok tunnel 供远程 Agent 接入

### 2. Agent 连接
- 每个 Agent 获取自己的 scoped token
- 自动分配独立 tab
- 活动归属标记（哪个 Agent 做了什么）

### 3. 协作模式
- **观察模式**: Agent A 操作，Agent B 旁观并提出建议
- **分工模式**: Agent A 负责 UI 交互，Agent B 负责数据验证
- **审查模式**: Agent A 操作完成后，Agent B 审查截图/日志

### 4. 安全隔离
- Tab 级隔离：每个 Agent 只能操作自己的 tab
- Token 作用域：限制操作类型和时长
- 速率限制：防止 Agent 间互相抢占
- 活动日志：完整记录每个 Agent 的操作序列

## 支持的 Agent
- Claude Code（本地/远程）
- Codex CLI
- Cursor
- OpenClaw
- 任何支持 curl 的 Agent

## 输出
- 协作会话日志
- 各 Agent 操作截图序列
- 协作结论摘要

## 关键约束
- 最多 5 个 Agent 同时连接
- 每个 tab 独立 cookie/session
- ngrok tunnel 仅在协作期间开放
