---
name: ui-ux-pro-max
description: UI/UX设计知识库，67风格+161色板+99UX指南，CSV数据驱动设计决策。触发词：UI设计、UX、设计系统、landing、dashboard。
source: nextlevelbuilder/ui-ux-pro-max-skill
layer: P1
---

# UI/UX Pro Max（catalog 按需）

> 来源：nextlevelbuilder/ui-ux-pro-max-skill | 按需复制到项目

## 数据资产

| 文件 | 内容 | 条数 |
|------|------|------|
| `data/styles.csv` | UI风格 | 84 |
| `data/colors.csv` | 色板 | 160 |
| `data/ux-guidelines.csv` | UX指南 | 98 |
| `data/typography.csv` | 排版规则 | 73 |
| `data/landing.csv` | 落地页模式 | 34 |

## 使用方式

Grep 匹配设计需求对应的数据行：

```bash
grep -i "<关键词>" data/styles.csv       # 风格
grep -i "<关键词>" data/colors.csv       # 色板
grep -i "<关键词>" data/ux-guidelines.csv # UX指南
```

## 补充数据

源仓库共 15 个 CSV（含 app-interface/charts/design/google-fonts/icons/products/react-performance/ui-reasoning 等），按需下载：

```bash
curl -sL "https://raw.githubusercontent.com/nextlevelbuilder/ui-ux-pro-max-skill/main/src/ui-ux-pro-max/data/<name>.csv" -o data/<name>.csv
```
