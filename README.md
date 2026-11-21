# 本端开发配置 · v16.0.0

以目标澄清、最小/全局协同改法、反兜底、风险分级和真实验证支持高效开发。方法不指定模型或通用工具链；本目录只维护 Claude 本端运行配置，不充当其他工具的配置中心。

## 使用

Claude 仅通过单一原生入口 `CLAUDE.md` 加载本端约定（不保留或导入全局 `AGENTS.md`）。按任务读取技能，不叠加另一套插件流程。
动机/目标不清时先停下讨论，路径非最短时建议更短方案；局部问题做最小改动、共性缺口优先在全局/公共层修正，不做不必要兜底；低风险小改且目标路径清晰时直接执行并针对性验证，普通多文件任务用短计划，高风险设计确认后执行并在完成前独立审查。

其他工具持有自己的完整 `AGENTS.md` 入口、方法和原生配置，手动独立维护；不引用本目录、不使用跨工具链接或同步器。
可移植的是通用方法正文；角色权限、hook 事件、MCP 作用域必须按宿主能力配置，不能把文件复制成功当生效证据。

## 内容

- `CLAUDE.md`：Claude 本端唯一方法与运行入口（其余工具各自独立使用 `AGENTS.md`）。
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
插件安装清单经清理后保留 3 项磁盘实际存在登记（均在 `settings.json` `enabledPlugins` 中显式设为 false，其余 15 项失效历史登记已于 v16.0.0 移除）；实际状态以原生列表和调用为准，不自动安装或升级。

## 验证

```text
python scripts/check-config.py
python hooks/tests/test_hooks.py
claude mcp list
```

自检验证结构、引用、hook 契约与 catalog 计数。本轮清理前 CLI 观察 `claude mcp list` 无服务器、`claude plugin list` 均为 disabled；清理 `installed_plugins.json` 失效登记后待在新会话/CLI 复核。规则/技能/hooks 的 IDE 新会话加载来源仍待取证，不以本说明宣称已生效。

## 版本与恢复

本轮从当前磁盘状态备份后重构，不回退已有未提交改动。
方法变更与采用理由见 `docs/ADR/2026-11-15-risk-based-independent-config.md` 与 `docs/ADR/2026-11-18-v15-1-entry-decoupling-and-merits-restoration.md`，来源和能力去向见 `docs/research/config-merits-20261115.md`。
历史规则编号与旧适配设计仅供考古，已被本轮决策替代。恢复时仅还原本轮相应备份，不覆盖用户后续修改。

## 按需图谱

手动运行本端 `tools/graph_freshness_cli.py` 的 `status`、`ensure` 或 `refresh`，传 `--cwd <精确Git仓根>`；项目要求双图时加 `--require-both --no-subprojects`。工具以当前源码哈希、真实 SQLite 文件清单/节点核验新鲜度，增量补齐未跟踪文件，不注册自动 hook。用法与边界见 `skills/development-workflow/references/graph-refresh.md`。
