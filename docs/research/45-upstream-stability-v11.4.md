# 上游仓库版本稳定性调研（v11.4.0 决策依据）

> 调研日期：2026-08-25 | 档位：L3（Firecrawl/GitHub 双源 + V1-V5 交叉验证）
> 结论消费方：v11.4.0 升级矩阵（CHANGELOG）、MANIFEST.yaml 版本串、T15 执行门

## 摘要

11 个钉扎仓库全部完成核查。9 个可安全推进（多为文档版本串/pin 同步），claude-mem
维持 13.13.1 钉扎有实锤依据（13.14+ 为 CMEM Pro 推销专版），无任何仓库存在阻碍
「多端验证精细化」主线的破坏性变更。新发现风险：`FORCE_AUTOUPDATE_PLUGINS=1`
可能使 claude-mem 运行态已越过 <13.14 钉扎线，须执行时核查 installed_plugins.json。

## 版本决策矩阵

| 仓库 | 当前 | 最新 | 裁决 | 置信度 | 证据 |
|---|---|---|---|---|---|
| obra/superpowers | 6.2.0 | 6.3.0 | 运行态随插件 autoUpdater 自升；本地仅 cherry-pick brainstorming 分级仪式；版本串→6.3.0 | 高 | release notes [web] + autoUpdater 机制 [memory] |
| Fission-AI/OpenSpec | 1.4.1 | 1.10.0 | **升**：六个 minor 全增量无 breaking；以 `openspec init --tools cursor` 冒烟为硬门 | 中高 | CHANGELOG [web]；1.8 vendor-neutral `.agents` 目标与 opencode AGENTS.md 设计互证 |
| open-gsd/gsd-core | 1.4.5 | 1.11.0 | **版本串升**：唯一硬约束 Node≥24 不适用（概念集成未装 npm 包）；honest-verifier/claim 三态处置记为后续 cherry-pick 候选 | 高 | CHANGELOG [web] + 集成模式 [inferred] |
| thedotmack/claude-mem | 13.13.1 | 13.15.3 | **维持钉扎 <13.14**：13.14 安装器 CMEM Pro 列首选项、13.15.0 内嵌 trial 漏斗(email→magic-link→Stripe)、13.15.2 全表面 Pro 横幅+observer 报错绑定 Pro 配额；区间无核心能力增益。双源一致 [web]+[memory] | 高 | CHANGELOG 逐条 [web] |
| affaan-m/ECC | 2.0.0 | 2.1.0 | 参考串升（cherry-pick 模式不安装实体）；官方新增 OpenCode/Kimi 目标 = opencode 接入设计旁证 | 高 | release [web] |
| bytedance/deer-flow | 2.0 | 2.0.0 | 已最新 | 高 | tags [web] |
| rtk-ai/rtk | 0.44.1 | 0.45.0 | 版本串升；执行时 `rtk --version` 核对二进制 | 高 | tags [web] |
| JuliusBrussee/caveman | 1.9.1 | 2.3.1 | **条件升级**：2.x 主体是 Learn v3 计费+代理网关，2.3.0 提及 ruleset framing 重写；我们仅集成压缩 skill 本体。执行时 diff 上游 SKILL，有实质变化才刷本地，否则仅升串。单源限制（V1 未满）→ diff 门兜底 | 中 | releases [web] 单源 |
| tirth8205/code-review-graph | 2.3.6 | 2.3.8 | **升 pin 至 2.3.8**（opencode.json + .mcp.json 两处）：2.3.7 明示 No breaking changes（MCP 并发/Windows 加固）；2.3.8 token 预算硬顶+诚实空结果，直接利好 detect_changes 用法 | 高 | releases 明示 [web] |
| garrytan/gstack | 0.19 | 无发布渠道 | vendored 维持 | 高 | API 404 [web] |
| firecrawl-mcp / exa-mcp-server | 3.23.9 / 3.4.0 | npm latest | 例行 minor 升 pin（opencode.json + .mcp.json） | 中 | 执行时 `npm view` |

## 关键交叉验证记录

- **V1**：OpenSpec「无破坏」以 CHANGELOG 为单一 web 源 → 以执行时 init 冒烟补第二证据；
  caveman 同理以 diff 门兜底。
- **V2 矛盾点**：MANIFEST 注记称 13.14+ 「推 CMEM Pro 订阅」，changelog 实证为安装器
  首选项+试用漏斗+全表面横幅——方向一致，粒度更细，裁决不变。
- **V4**：钉扎理由属训练记忆 [memory]，本次以 changelog 实证刷新 [web]。
- **新风险**：settings.json env `FORCE_AUTOUPDATE_PLUGINS=1` 与 claude-mem 钉扎存在张力，
  执行时须核对运行态实际版本并纠偏。

## 对本仓设计的旁证

- OpenSpec 1.8 `--tools agents`（`.agents/skills/` 共享位）与 ECC 2.1 官方 OpenCode 目标，
  双重印证 v11.4 opencode 经 AGENTS.md 接线的路线正确。
- gsd-core honest-verifier 的 claim 三态处置（admit/refute/abstain）已于 **v11.4.5** 吸收为 R20「满足」行承认/反驳/弃权（硬门仍用 coverage_ok 关键词覆盖）。
- **明确不吸收（v11.4.5）**：sdsrss/dorkian 等竞品 code-graph plugin；ralph-loop / Cursor `/loop` 独立进程；Anthropic 实验性 agent-Stop hook；caveman 2.x；claude-mem ≥13.14；OpenSpec 1.10 大升。

## 执行结果回填（2026-08-25 T15）

| 仓库 | 计划 | 实际结果 |
|---|---|---|
| OpenSpec | 升 1.10.0 + init 冒烟 | ✅ npm -g 安装成功；`openspec init --tools cursor` 冒烟 exit=0，opsx 命令/skills 结构兼容 |
| superpowers | 运行态自升假设 | ⚠️ 修正：autoUpdater 未拉取（仍 6.2.0）；已显式 `claude plugin update` → **6.3.0**（重启生效） |
| claude-mem | 核查运行态越线 | ✅ installed_plugins.json 实测 13.13.1，钉扎完好 |
| CRG pin | 2.3.6→2.3.8 | ✅ .mcp.json + opencode.json 双处已改 |
| firecrawl/exa | 例行升 pin | ✅ 3.24.0 / 3.4.1 双处已改 |
| rtk/ECC/gsd-core | 版本串 | ✅ 0.45.0 / 2.1.0 / 1.11.0（rtk 二进制以本机为准，Stop 门 which 探测降级兼容） |
| caveman | 条件升级（diff 门） | 🔴 **门未过→豁免**：上游 2.3.1 同名技能已重定位为「文件压缩器」（scripts 覆写原文件），与本仓「输出风格压缩」语义冲突；本地 1.9.1 正文保持，MANIFEST 登记豁免 |
