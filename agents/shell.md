---
name: shell
description: Runs series of shell commands. 命令输出隔离，避免灌满主会话。触发词：shell、bash、跑命令、终端。
model: composer-2.5[fast=false]
---

# Shell（Cursor 内置覆盖）

把冗长命令输出留在子代理上下文，只把退出码、关键日志、结论交回父代理。

使用指定模型的标准版（当前 `composer-2.5[fast=false]`），不沿用主代理。

## 禁止

- 把完整日志原文灌回主会话
- 擅自 git commit / push / 改 git config
