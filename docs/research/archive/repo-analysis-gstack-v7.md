# gstack 深度分析 v0.19

> Garry Tan (Y Combinator CEO) 的虚拟工程团队 — 23 角色 + 8 工具 + Sprint 流程

---

## 生产力数据

- **2026 年运行率**: ~810× 2013 年 pace (11,417 vs 14 逻辑行/天)
- **2026 YTD (至 4/18)**: 240× 2013 全年
- **40+ shipped features**: 60 天内, 兼职, 同时运营 YC
- **1,237 contributions**: 2026 GitHub 统计

---

## 23 角色详细分析

### 规划阶段 (5 角色)

#### /office-hours — YC Office Hours
- **6 个强制问题** 重构产品定义
- 追问具体案例而非假设
- 挑战前提假设
- 生成 3 种实现方案 + 工作量估算
- 输出设计文档 → 自动馈入下游技能

#### /plan-ceo-review — CEO/Founder
- 4 种 scope 模式: Expansion / Selective Expansion / Hold Scope / Reduction
- 在请求内部找到 "10 星产品"
- 10 节完整审查

#### /plan-eng-review — Eng Manager
- ASCII 数据流图
- 状态机
- 错误路径分析
- 测试矩阵
- 失败模式识别
- 安全关注点

#### /plan-design-review — Senior Designer
- 每维度 0-10 评分
- 解释"10 分什么样"
- AI Slop 检测
- 交互式: 每设计选择一个 AskUserQuestion

#### /plan-devex-review — Developer Experience Lead
- 3 模式: DX EXPANSION / DX POLISH / DX TRIAGE
- 20-45 强制问题
- 竞品 TTHW 基准
- 摩擦点逐步追踪

### 设计阶段 (4 角色)

#### /design-consultation — Design Partner
- 从零构建完整设计系统
- 竞品研究
- 创意风险建议
- 生成逼真产品 mockup

#### /design-shotgun — Design Explorer
- 生成 4-6 个 AI mockup 变体
- 浏览器比较板
- 收集反馈迭代
- **品味记忆**: 学习用户偏好

#### /design-html — Design Engineer
- Mockup → 生产 HTML
- Pretext computed layout (文本自动换行、高度调整)
- 30KB, 零依赖
- 检测 React/Svelte/Vue
- 按设计类型智能 API 路由

#### /design-review — Designer Who Codes
- 同 plan-design-review 审计
- 然后修复发现的问题
- 原子提交
- Before/After 截图

### 开发阶段 (2 角色)

#### /review — Staff Engineer
- 发现 CI 通过但生产会爆炸的 bug
- 自动修复明显问题
- 完整性检查
- 标记遗漏

#### /investigate — Debugger
- 系统根因调试
- **铁律**: 无调查不修复
- 数据流追踪
- 假设测试
- **3 次失败即停**

### 测试阶段 (3 角色)

#### /qa — QA Lead
- 真浏览器操作测试
- 发现 bug → 原子修复 → 重新验证
- 为每个修复自动生成回归测试

#### /qa-only — QA Reporter
- 同 /qa 方法论但仅报告
- 纯 bug 报告不修改代码

#### /devex-review — DX Tester
- 实测开发者体验
- 导航文档 → 尝试入门流程 → 计时 TTHW
- 截图错误
- 与 /plan-devex-review 分数对比

### 安全阶段 (1 角色)

#### /cso — Chief Security Officer
- OWASP Top 10 + STRIDE 威胁模型
- **17 假阳性排除**: 零噪音
- **8/10+ 置信度门**: 低置信不上报
- 独立验证每个发现
- 每个发现包含具体利用场景

### 发布阶段 (3 角色)

#### /ship — Release Engineer
- 同步 main → 运行测试 → 审计覆盖 → 推送 → 开 PR
- 无测试框架时自动 bootstrap

#### /land-and-deploy — Release Engineer
- 合并 PR → 等待 CI 和部署 → 验证生产健康
- 从 "approved" 到 "verified in production" 一条命令

#### /canary — SRE
- 部署后监控循环
- Console 错误
- 性能回归
- 页面失败

### 性能 (1 角色)

#### /benchmark — Performance Engineer
- 基线页面加载时间
- Core Web Vitals
- 资源大小
- PR 前后对比

### 元工具 (4 角色)

#### /pair-agent — Multi-Agent Coordinator
- 多 AI Agent 共享浏览器
- 每个 Agent 独立 tab
- 自动启动 headed mode
- 自动 ngrok tunnel (远程 agent)
- 作用域 token + tab 隔离 + 速率限制 + 活动归属

#### /autoplan
- 自动规划 → 执行 → /ship

#### /learn
- 跨会话经验提取

#### /codex
- 跨模型独立审查 (不同模型视角发现盲点)

---

## ML 注入防御 (gstack v0.19 独有)

```
Layer 1: 22MB ML 分类器 — 本地扫描每页和工具输出
Layer 2: Canary Tokens — 注入诱饵 token，触发即告警
Layer 3: Haiku 转录检查 — 低成本模型快速扫描
```

---

## 集成清单

| gstack 角色 | 本地 agent | 状态 |
|-------------|-----------|------|
| /review | eng-reviewer | ✅ |
| /cso | cso + security-reviewer | ✅ |
| /plan-ceo-review | ceo-reviewer | ✅ |
| /plan-design-review | designer | ✅ |
| /plan-eng-review | architect | ✅ (部分) |
| /qa | qa | ✅ (部分, 无浏览器) |
| /ship | release-engineer | ✅ |
| /canary | sre | ✅ |
| /benchmark | performance-engineer | ✅ |
| /codex | codex-reviewer | ✅ |
| /office-hours | product-manager | ⚠️ (概念对齐) |
| /design-shotgun | — | ❌ 缺失 |
| /design-html | design-engineer | ⚠️ (功能差异) |
| /pair-agent | — | ❌ 缺失 |
| /land-and-deploy | — | ❌ 缺失 |
| /investigate | systematic-debugging skill | ✅ |
| /learn | instinct-learning skill | ✅ |
