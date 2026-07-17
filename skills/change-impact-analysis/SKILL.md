---
name: change-impact-analysis
description: 变更影响分析 — 改任何文件/函数/类型/配置前必须先执行。触发词：修改、改、重构、更新、删除、变更、rename、move。
layer: skeleton
loading_tier: L1
source: internal
---

# 变更影响分析

> **L1 常驻**（P0 路由集）：任何阶段有修改意图时 Read 全文。同会话已 Read 且范围未变可不重复 Read。

## 核心原则

**范围不明不修改。** 改一个符号可能影响 N 个文件 — 先找到所有 N，再全部修改，最后验证无遗漏。

## 强制流程

### 阶段 1: 范围识别

```
① codegraph_explore(target) blast-radius 或 codegraph_impact（env 启用）
   └ git diff 变更风险场景（L4）：codebase-memory detect_changes

② Grep 全项目(reference_pattern)
   → 搜索: 函数名/类型名/文件名/配置key/路径引用
   → 命令: grep -rn "pattern" --include="*.ext"

③ MANIFEST.yaml concern → depends_on
   → 查: 改 rules/CONTEXT.md 是否影响 rules/CORE.md 的阈值引用？
   → 查: 改 agent 定义是否需同步 agents-INDEX.md？

输出: 受影响文件完整清单（含依赖关系）
```

### 阶段 2: 逐文件执行

```
按依赖拓扑序修改（被依赖的先改，依赖别人的后改）
  每文件: Read → 确认当前内容 → Edit → Read → 验证修改正确
  清单逐项勾销: ☐ → ☑
  中途发现新关联: 追加到清单末尾
```

### 阶段 3: 残留检测

```
① Grep 旧引用模式
   → grep -rn "old_function_name" --include="*.ext"
   → grep -rn "old_config_key" --include="*.{yaml,json,md}"
   → 残留 > 0 → 回到阶段 2 继续修改

② 构建/类型/Lint 验证
   → npm run build / pnpm run typecheck / pnpm run lint

③ MANIFEST 一致性
   → python hooks/_editor_hook_launcher.py hooks/pre-manifest-validator.py
```

## 触发条件

| 变更类型 | 检测范围 |
|----------|----------|
| 改函数名/签名 | codegraph blast-radius/impact + Grep 全项目函数名 |
| 改类型/接口 | codegraph blast-radius/impact + Grep import 引用 |
| git diff 变更风险（L4 cbm 已启用） | detect_changes + Grep 残留 |
| 改配置文件 | MANIFEST depends_on 遍历 |
| 重命名/移动文件 | Grep 全项目路径引用 |
| 改 rule/skill/agent | 同步更新 INDEX.md + MANIFEST.yaml |
| 删除代码 | Grep 确认无残留引用 |
| 调研/探索任务 | codegraph_explore blast-radius 先确定范围 |

## 反模式（禁止）

| 禁止 | 正确做法 |
|------|----------|
| 只改指定文件 | Grep 找到所有关联文件一并修改 |
| "应该只有这些" | codegraph 验证，不靠直觉 |
| 手动估计范围 | codegraph_explore +（L4）detect_changes + Grep 实证 |
| 残留引用 > 0 声称完成 | 违反 R1（验证通过才算完成） |
| 跳过阶段 1 直接改 | 范围不明 = 盲改 = 必遗漏 |

## 门控

- 阶段 1 清单为空 → **拒绝执行**（先让用户明确变更范围）
- 阶段 3 残留 > 0 → **不可声称完成**（回到阶段 2）
- 全部通过 → 进入 verification-before-completion
