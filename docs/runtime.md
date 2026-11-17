# Claude 本端运行说明

本文件只解释 Claude 本端配置，不管理其他工具。

## 作用域与默认值

- `settings.json` 注册用户 hooks；项目/local 设置及插件仍可能合并，实际结果需原生会话核对。
- 当前默认仅保留危险命令、编码和密钥检查；无启动图谱刷新或 Stop 审查门。
- 格式化默认不运行；仅项目有明确配置并选择启用时使用项目工具，错误须可见。
- `.mcp.json` 是所在项目的配置，不是用户级 MCP。用户级与项目私有登记实际在用户原生配置中，不能只查本目录推断全局状态。
- 本轮已将用户级 17 项旧增强定义转为私有可选资料；原生 `claude mcp list` 观察为无默认服务器。
- 五项开发增强定义保留在 `mcp-configs/development.json`；私人服务定义不入库，不在文档中复制。
- 现有 18 项插件登记均停用；登记不保证对应安装文件存在，不以“已安装”描述未经加载核实的插件。

## 按需使用

优先使用宿主已有能力。需要额外工具时，先按当前版本官方说明选择单个定义，并核实作用域、路径、依赖及认证。
不自动整包合并增强配置，不同时加载同职责插件和 MCP；不安装或升级没有实际任务需要的依赖。

需要结构分析而无图谱时，本地搜索、源码和显式影响清单可完成普通任务。
来源检索使用可用可靠能力；缺来源说明不确定性，不依赖特定搜索提供方。

## 核验

```text
python scripts/check-config.py
python hooks/tests/test_hooks.py
claude mcp list
```

自检验证配置契约，hook 测试验证输入输出；原生列表和新会话的加载来源、工具列表及实际行为提供生效证据。
将验证结果与范围记录在任务制品；缺少加载证据保留待验，不因文件存在宣称正常使用。

## 手动图谱刷新

本端提供完整独立的 `tools/graph_freshness_cli.py`、本地桥接与 `tools/graph-refresh.json`。项目需要双图时，手动运行 `python <本端方法目录>/tools/graph_freshness_cli.py ensure --cwd <精确Git仓根> --require-both --no-subprojects`；收尾用 `refresh`，只读检查用 `status`。
它实际核对 SQLite 文件哈希和节点，补齐未跟踪文件；退出 0 且 JSON `fresh: true` 才表示当前适用范围已新鲜。不会注册自动 hook、启用 MCP 或安装依赖。错误时报告边界，可按项目约定回退源码搜索；详细范围、锁和恢复说明见本端 `skills/development-workflow/references/graph-refresh.md`。
