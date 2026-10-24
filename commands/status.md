---
description: 查看当前工作流（config/workflow.yaml 轨道/阶段）状态与进度
---

# /status — 工作流状态

查看当前工作流阶段和进度。

## 输出

```
当前轨道: [simple / bug / non_simple / research]
当前阶段: [triage / debug / research / discuss / spec / execute / verify / learn / ship]
当前任务: [任务描述]
进度: [完成数]/[总数]
上下文使用率: [%]
未解决问题: [数量]
下一步: [建议行动]
```

## 阶段判定

> 阶段与轨道 SSOT = `config/workflow.yaml`（`stages` / `tracks`）；`python scripts/workflow.py show` 打印模型档、角色路由与阶段/轨道/出口门。下表 id 与 `stages` 键一致。

- **triage** — 新任务，未分类 | ⓪分类
- **debug** — Bug 类，根因未定位 | ⓑ根因
- **research** — 调研类，结论未交叉验证 | ⓡ调研
- **discuss** — 需求未对齐，有歧义待澄清 | ①规划（/discuss）
- **spec** — 需求已对齐，方案设计中 | ②规格（/plan）
- **execute** — 计划已批准，执行中 | ③执行（/execute）
- **verify** — 实现完成，验证 + 独立审查中 | ④验证（/verify）
- **learn** — 验证通过，模式提取/上下文释放 | ⑤学习（/compact）
- **ship** — 按需：用户明确要求提交 / 开 PR / 发布 | ⓢ交付（/ship）
