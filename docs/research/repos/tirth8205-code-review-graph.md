# tirth8205/code-review-graph v2.3.6

> 层: L3 洞察（审查/验证专用） | 置信度: 高 | 刷新: 2026-08-07 | 来源: GitHub + npm + 官方文档 双源交叉

## 核心价值

- **代码审查专用图谱**：基于 Tree-sitter 构建函数/类/调用关系 + **TESTED_BY 边**（哪些函数被哪些测试覆盖）
- **变更风险评分**：`detect_changes_tool` 接收 diff → 返回受影响函数、执行流路径、测试缺口、风险等级
- **测试缺口检测**：`get_knowledge_gaps_tool` 识别高频调用但未测试的热点函数
- **增量更新**：~2.5s 增量重建（500 文件项目实测）；全量 ~10s
- **~65x token 压缩**：6 仓库实测中位（相比喂全量 diff 给模型）
- **30 个 MCP 工具**：build / update / detect_changes / review_delta / get_knowledge_gaps / pre_merge_check 等
- **双端支持**：官方 `install` 同时写 claude-code 和 cursor 配置；MCP stdio 模式
- **本地优先**：默认 100% 本地嵌入（可选云 provider，`CRG_ACCEPT_CLOUD_EMBEDDINGS` 控制开关）

## v10.14 集成决策（2026-08-07）

- **引入**：作为审查/验证专用层，与 codegraph（R17 探索主位）互补
- **分工边界**（写入 CORE.md R17 表）：
  - codegraph = 符号/调用链/blast-radius/变更前影响面（R17 强制优先）
  - CRG = 变更后 test-gap、detect_changes 风险评分、review-delta、pre_merge_check
- **安装**：`pipx install code-review-graph==2.3.6`（pipx 隔离依赖；钉扎 R14）
- **MCP 注册**：`.mcp.json` + `mcp-configs/dev.json` + Cursor `mcp-recommended.json`（uvx serve）
- **项目级启用**：业务项目内 `code-review-graph build` 建图（与 codegraph mandate_init 同策略）
- **验证链接入点**：
  - stop-verification-gate.py 检查 2 用其影响半径确定"关联/影响文件"
  - verification-before-completion SKILL 全量档新增 detect_changes 步骤
  - /verify 命令同步
- **不吸收**：
  - 语义嵌入云 provider（默认不启，`CRG_ACCEPT_CLOUD_EMBEDDINGS` 不设）
  - GitHub Action（本地先用 MCP 模式）
  - 自动升级（钉扎 2.3.6，R14）

## 双源证据

- GitHub: tirth8205/code-review-graph v2.3.6（2026-08-07 核实）
- npm: code-review-graph 包
- 官方文档：USAGE.md / README.zh-CN.md

## 与 codegraph 对比

| 维度 | codegraph | code-review-graph |
|------|-----------|-------------------|
| 定位 | 探索主位（R17） | 审查/验证专用 |
| 核心能力 | 符号/调用链/blast-radius | test-gap/风险评分/review-delta |
| TESTED_BY 边 | 无 | 有（核心差异化） |
| 变更影响 | blast-radius（变更前） | detect_changes（变更后） |
| token 压缩 | ~47% | ~65x（不同测量口径） |
| 本地集成 | 已常驻 | v10.14 新增 |
