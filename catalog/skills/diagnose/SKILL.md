---
name: diagnose
description: 深度诊断循环（reproduce→minimize→hypothesize→instrument→fix→regression-test）。触发：顽固 bug、性能问题、P0 systematic-debugging 不足时。excludes 全局 skill/systematic-debugging（P0 优先）。
layer: catalog
source: mattpocock/skills
excludes: [skill/systematic-debugging]
---

# Diagnose（catalog 按需）

> 来源：mattpocock/skills | **非全局**。默认先用 `skill/systematic-debugging`（P0）；本 skill 用于需要 instrument/最小复现的顽固问题。

## 何时用

- 间歇性 bug、性能回归、多模块交叉故障
- systematic-debugging 四阶段后仍无根因

## 循环（严格顺序）

1. **Reproduce** — 稳定复现步骤，记录环境
2. **Minimize** — 删到最小 failing case
3. **Hypothesize** — 列出可证伪假设（≤3）
4. **Instrument** — 加日志/断言验证假设
5. **Fix** — 仅根因确认后改代码
6. **Regression-test** — 补测试防回归

## 复制到项目

```powershell
python ~/.claude/scripts/migrate-from-legacy.py --project . --skill diagnose
```

## 互斥

| 用 | 不用 |
|----|------|
| 顽固 bug 深度循环 | 替代 P0 systematic-debugging |
| 与 build-error-resolver 配合 | 无复现就改代码 |
