# 本端开发配置 · v15.0.0

以目标澄清、风险分级和真实验证支持高效开发。方法不指定模型或通用工具链；本目录只维护 Claude 本端运行配置，不充当其他工具的配置中心。

## 使用

Claude 从 `CLAUDE.md` 导入本端 `AGENTS.md`。按任务读取技能，不叠加另一套插件流程。
低风险小改直接执行并针对性验证；普通多文件任务用短计划；高风险设计确认后执行，完成前独立审查。

其他工具持有自己的完整入口、方法和原生配置，手动维护；不引用本目录、不使用跨工具链接或同步器。
可移植的是方法正文；角色权限、hook 事件、MCP 作用域必须按宿主能力配置，不能把文件复制成功当生效证据。

## 内容

- `AGENTS.md`：唯一方法入口；`CLAUDE.md`：本端原生入口。
- `skills/`：8 个按需技能，含开发、调试、调研、验证、交接、Git、ADR 和显式 TDD。
- `agents/`：4 个按需角色；`commands/`：8 个手动薄入口。
- `catalog/`：98 个领域技能、41 个专家角色、15 份领域规则，仅选择所需内容。
- `templates/`、`snippets/`：可选项目材料，不依赖用户全局目录。
- `config/toolchain.yaml`：项目工具链选择原则，不是全局版本地板。
- `hooks/`、`scripts/`：本端安全保护与自检；运行说明见 `docs/runtime.md`。
- `docs/research/`：来源与能力去向；`docs/ADR/`：决策；`docs/archive/`：不执行的历史资料。

## 当前运行默认

默认保留危险命令防护、密钥脱敏提醒和编码检查；关闭启动图谱刷新、Stop 审查门与自动格式化。
增强 MCP 默认不常驻；可选定义在 `mcp-configs/`，私人服务定义不入库。
插件保留登记并默认停用，实际可用性需原生列表和调用验证；不自动安装或升级。

## 验证

```text
python scripts/check-config.py
python hooks/tests/test_hooks.py
claude mcp list
```

自检验证结构与契约，原生列表验证配置作用域；实际行为和加载仍需新会话取证。
本轮迁移、跨工具加载及独立审查的最终证据由本次任务记录，不以本说明宣称全部完成。

## 版本与恢复

本轮从当前磁盘状态备份后重构，不回退已有未提交改动。
方法变更与采用理由见 `docs/ADR/2026-11-15-risk-based-independent-config.md`，来源和能力去向见 `docs/research/config-merits-20261115.md`。
历史规则编号与旧适配设计仅供考古，已被本轮决策替代。恢复时仅还原本轮相应备份，不覆盖用户后续修改。

## 按需图谱

手动运行本端 `tools/graph_freshness_cli.py` 的 `status`、`ensure` 或 `refresh`，传 `--cwd <精确Git仓根>`；项目要求双图时加 `--require-both --no-subprojects`。工具以当前源码哈希、真实 SQLite 文件清单/节点核验新鲜度，增量补齐未跟踪文件，不注册自动 hook。用法与边界见 `skills/development-workflow/references/graph-refresh.md`。
