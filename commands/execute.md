---
description: 按已批准计划执行实现（③执行阶段）
---

# /execute — 按计划执行

③执行阶段入口。**正文 SSOT → Read `skills/executing-plans/SKILL.md`**（依赖序执行、失败隔离、状态摘要；R5 同方案≤2 次、R11 安全），本命令不复写流程（v11.1 薄壳化）。

<!-- spine:stage-gate -->
## 门控（派生自 config/workflow.yaml，改配置后 `python scripts/workflow.py render`，勿手改）

- 阶段：③执行 | skill：`skills/executing-plans/SKILL.md` | 角色：change-implementer
- 进入：就绪定义全部满足
- 退出（全部满足才进入下一阶段）：
  - 清单内文件一次改齐（含文档/注释/INDEX/版本戳）
  - 构建/类型/Lint 通过；R16 无静默吞异常
  - 交审前自检（quality.self_check）通过
<!-- /spine:stage-gate -->

<!-- spine:concurrency -->
**执行并发**（派生自 config/workflow.yaml，改配置后 `python scripts/workflow.py render`，勿手改）：无依赖且可后台的命令/操作不得阻塞会话，优先并行。有依赖或下一步需要其输出的仍按序、禁止后台。长驻服务器 / watcher 保持后台。不是第三道 PASS 门，不另建 Stop hook，不改 `browser_ui_tests`。

- 无依赖且可后台的命令/操作不得阻塞会话，优先并行
- 有依赖或下一步需要其输出的步骤仍按序执行，禁止后台
- 长驻服务器 / watcher 保持后台
<!-- /spine:concurrency -->
