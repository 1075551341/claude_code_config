# 本地代码图谱的按需刷新（Claude 本端可选工具说明）

> 本参考仅描述 Claude 本端自带的按需图谱刷新工具；未配备该工具的宿主环境直接使用源码搜索与显式影响清单即可。

## 快速用法

需要结构分析时可手动运行本端 `tools/graph_freshness_cli.py`（不注册 hook，不启动 MCP、watcher、模型或网络安装）：

```text
python <本端方法目录>/tools/graph_freshness_cli.py status --cwd <精确Git仓根> --require-both --no-subprojects
python <本端方法目录>/tools/graph_freshness_cli.py ensure --cwd <精确Git仓根> --require-both --no-subprojects
python <本端方法目录>/tools/graph_freshness_cli.py refresh --cwd <精确Git仓根> --require-both --no-subprojects
```

- 仅当退出 0 且 JSON `fresh: true` 时才能声称图谱新鲜；退出 2 表示过期、缺依赖、坏库或锁冲突等。
- 如图谱为可选增强，失败时可直接用源码搜索和显式影响清单继续并说明边界，不虚报成功。

## 运行契约

- `status` 只读 SQLite，不创建缺失库、不运行 native status 的迁移或修复。核验原生支持/忽略规则下的文件清单、当前内容 SHA256、删改名残留、非空节点和索引元数据；不以时间戳、HEAD、库存在或原生命令退出 0 代替 freshness。
- `ensure` 已新鲜时跳过；缺失时用已安装的本地 AST 引擎建图；`refresh` 优先增量。CRG 补齐 Git 可见未跟踪文件并执行本地 postprocess；Codegraph 用逐文件 indexFiles 补其大小/mtime 预筛遗漏，不重建已有 DB。
- CRG 2.3.8 虽识别 YAML 扩展，但原生 `parse_bytes` 明确不提取普通 YAML；`excluded_files` 按原因报告这类文件及缺少内容证据的 Ansible 路径数量。Spring 配置、真正符合原生内容条件的 Ansible YAML、空 Python 和普通未跟踪代码仍必须产生真实 File 行和匹配哈希。Ansible 内容变为普通配置时，通过原生清理 API 删除其旧节点/引用并重新 postprocess，不能保留过期图谱或伪造 File 行。
- `--require-both` 要求 codegraph 与 code-review-graph 都通过；项目明确双图时必须带。`--no-subprojects` 为兼容参数：始终只处理明确仓根，不另遍历、启动子项目的刷新；原生扫描仍遵守该仓已有 include/ignore 范围。
- 每端工具、配置、bridge 完整自持，不读取其他端方法目录；安装的原生运行时由本端 `tools/graph-refresh.json` 指定或从 PATH/Volta 发现，不固定 npx 缓存 hash，不自动下载或升级。已核验版本为 Codegraph 1.6.0、CRG 2.3.8；换版本应重新核验 API/数据库契约。
- 每次写入前以 SQLite backup API 将现有库的一致性快照放在本仓 Git 管理目录的 `graph-freshness-backups/`。坏库拒绝覆盖；不删除锁、不杀 daemon，不自动覆盖恢复。跨端副本共用本仓 Git 管理目录的 advisory lock；不能约束外部 watcher，故刷新前后比较源码快照并再次核验真实 DB，变动时明确失败。
- 子进程设置 `DO_NOT_TRACK=1`、`CODEGRAPH_NO_UPDATE_CHECK=1`、`CODEGRAPH_NO_DOWNLOAD=1`、`NO_COLOR=1`；不改全局环境。CRG embedding provider/model 均为 None；只走本地解析 API，不走 MCP/LLM，不把源码传出。
- 超出原生支持范围、解析/索引告警、空仓、损坏或不兼容库都明确保留未验状态。锁冲突后由用户/原进程正常释放再重试，不规避沙箱拒绝。
- 输出路径在读写前校验：默认缓存限于本仓，元数据目录、DB、`.gitignore`、WAL/SHM/journal、锁和备份不接受未声明的链接/硬链接。CRG 保留原生已有 registry exact-repo 映射优先、再 `CRG_DATA_DIR`、最后默认路径的规则，并报告 `storage_origin`；只读检查不会创建 registry。配置值若词法上位于仓内，仍受仓根约束；只有明确外置的 native 配置才授权对应 canonical 数据根，其内部子路径不能再用链接逃逸。原生 legacy 库及伴随文件在迁移/清理前检查；自有锁和备份以实际 canonical Git 元数据根为边界，合法 worktree 的外部 gitdir 保持可用。失败返回脱敏错误且不声称 fresh，不删除链接或覆盖修复用户数据。

## 回归测试（仅改图谱工具时运行）

- 范围与刷新回归：`python <本端方法目录>/tools/tests/test_graph_freshness.py --cli <本端方法目录>/tools/graph_freshness_cli.py --report <临时结果JSON>`（新建临时 Git 仓，调用真实引擎验证摄入、未跟踪文件、删改名、跳过、锁和坏库，不刷新真实项目）。
- 仅测范围契约可加 `--scope-only`：验证普通 YAML 原生排除报告、Spring/Ansible 摄入、空 Python、未跟踪变化及 Ansible 支持范围双向变化。
- 输出边界回归：`python <本端方法目录>/tools/tests/test_graph_output_paths.py --cli <本端方法目录>/tools/graph_freshness_cli.py --report <临时结果JSON> --history-source <现有本地Git仓>`（仅读现有历史并向临时 fixture 写入，校验外目录拒绝、显式外置及 worktree 正例）。
