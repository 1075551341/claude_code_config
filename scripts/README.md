# `.claude\scripts` 工具说明

本目录存放 Claude Code 环境维护与辅助脚本（PowerShell）。默认在 **Windows** 下通过 `pwsh -ExecutionPolicy Bypass -File <脚本名>` 执行（优先 PowerShell 7+ 稳定版；PS5.1 环境回退用 `powershell`）。

---

## 同步与验证（v11.1 多编辑器 1+N）

**1+N 模型**：Claude Code 原生读 `~/.claude`（零同步）；编辑器侧 = **Cursor + qoder-cn + trae-cn + workbuddy**（v11.1 恢复，清单单源 `config/sync-manifest.json` editors 段，home 缺席自动跳过；qoder/trae/codearts 定义保留待装）。`sync.sh`（Linux/macOS）维持已删（git 可回溯）。

### `sync.ps1` — 多编辑器同步（v20.0）

**Cursor 落点（默认模式全含）**：

| 落点                                           | 方式                             | 内容                                                                                              |
| ---------------------------------------------- | -------------------------------- | ------------------------------------------------------------------------------------------------- |
| `~/.cursor/` 根                                | 软链（回退 Copy）                | 6 个总纲/索引根文件：`CLAUDE.md`/`SPEC.md`/`MANIFEST.yaml`/3 INDEX                                |
| `~/.cursor/plugins/local/claude-config/rules/` | 实体 `.mdc`（每次刷新+孤儿清除） | `rules/*.md`（除 README）+ `00-CLAUDE`（=CLAUDE.md）+ `CURSOR-EDITOR`；唯一 Always-Apply 规则通道 |
| `~/.cursor/skills` `~/.cursor/agents`          | Junction                         | `-Skills` / `-All` 时                                                                             |

**用法**：

```powershell
pwsh -ExecutionPolicy Bypass -File sync.ps1                 # 日常：根文件 + 刷新 claude-config 插件
pwsh -ExecutionPolicy Bypass -File sync.ps1 -Skills         # + skills/ Junction
pwsh -ExecutionPolicy Bypass -File sync.ps1 -All                # + skills/ + agents/
pwsh -ExecutionPolicy Bypass -File sync.ps1 -All -DryRun        # 预览不写盘
```

> 改 `~/.claude/rules` / `CLAUDE.md` / `CURSOR-EDITOR` 后跑一次 `sync.ps1` 即可；Cursor Settings 中的 Claude Config 插件内容会随之更新。若列表未变，完全退出 Cursor 再开（仅 Reload 有时不重扫插件）。

> **Claude Code 官方安装**（v10.11 更新）：npm 安装已弃用；Windows 推荐 `irm https://claude.ai/install.ps1 | iex`，macOS/Linux `curl -fsSL https://claude.ai/install.sh | bash`，或 `winget install Anthropic.ClaudeCode`。Volta/npm 全局安装在 Windows 上会反复把 `claude.exe` 更新成找不到的占位路径，见 `fix-claude-cli.ps1`。
> **参数**：

| 参数            | 说明                                |
| --------------- | ----------------------------------- |
| `-Skills`       | 追加同步 skills/                    |
| `-All`          | 全量（根文件+rules+skills+agents）  |
| `-ProjectRules` | 复制 rules 到当前项目 .cursor/rules |
| `-DryRun`       | 仅预览，不写盘                      |
| `-Force`        | 跳过 hash 比对强制刷新              |
| `-Lint`         | 部署 lint 模板到当前项目            |
| `-InitProject`  | 部署项目初始化模板到当前项目        |

**机制**：

- 文件优先符号链接，失败回退 `Copy-Item`；目录管理员用符号链接、非管理员 `mklink /J` Junction、回退递归复制
- **插件规则例外**：一律实体复制（Cursor Settings Rules UI 不索引软链接；插件禁止外链）
- **常量单源**：根文件集合 + 插件特殊映射定义在 `config/sync-manifest.json`，`sync.ps1` / `check.ps1` / `templates/cursor-guard/hooks/_lib/impact_sync.py` 三个消费方统一读取（impact_sync 读取失败回退内置默认）
- **写前去重**：删除目标目录同基底名兄弟文件（任意扩展名/大小写），再写新文件；`~/.cursor/rules` 同名项一并清理（防双份 Always-Apply）
- 回归测试：`test-sync-dedup.ps1`

**永不同步（Claude Code 专用）**：`hooks/`、`scripts/`、`commands/`、`plugins/`、`.mcp.json`、`settings.json`、`~/.claude/.cursor/`（OpenSpec 本地资产）

### Cursor Guard（编辑器独立）

Claude Code hooks 在 Cursor 内不执行；编辑器侧由 **Cursor Guard** 负责影响驱动同步与上下文 70%/90% 监控。

```powershell
powershell -ExecutionPolicy Bypass -File scripts/deploy-cursor-guard.ps1
```

- 模板：`templates/cursor-guard/`；运行时：`~/.cursor/hooks.json`、`guard-config.json`
- 显式同步：聊天输入「同步配置」
- **重部署时机（v10.7.0）**：改 `templates/cursor-guard/` 下任何文件（hooks/config/hooks.json）→ 重跑 `deploy-cursor-guard.ps1` → **重启 Cursor** 生效；改 `hooks/_lib/gate_messages.md` 无需重部署（Guard hook 运行时直读 `~/.claude`）

### 同步触发规则（v10.7.0）

| 改动                                            | 必跑                                             |
| ----------------------------------------------- | ------------------------------------------------ |
| `rules/*.md` / `skills/` / `agents/` 任何增删改 | `sync.ps1 -All`（默认模式只同步根文件+插件规则） |
| `templates/cursor-guard/**`                     | `deploy-cursor-guard.ps1` + 重启 Cursor          |
| `hooks/`（Claude 侧）                           | 无需同步；settings.json 注册即生效（新会话）     |
| `hooks/_lib/gate_messages.md`                   | 双端运行时直读，零操作                           |

> **多项目适配（全局/个人优先）**：默认只同步到 Cursor 个人目录 `~/.cursor/`（rules 软链、skills/agents Junction），**不写入业务项目**。
>
> **重要（Cursor UI）**：Settings → Rules → **User** 页签**不会枚举** `~/.cursor/rules/*.mdc`。全局 `.mdc` 靠本地插件 `~/.cursor/plugins/local/claude-config`（**实体 .mdc 副本**，因插件禁止外链软链）。skills/agents 仍 Junction。改规则后跑 `sync.ps1`，然后**完全退出并重开 Cursor**（Reload 有时不重扫 local plugins）。

### 同步后建议自测

1. 在 Cursor 中确认配置可读、无报错（Claude Code 直读 `~/.claude`，无需自测同步）
2. 抽查技能、代理、规则是否生效（重开无关项目验证全局规则加载）
3. 确认 MCP 配置与本地服务一致
4. 确认不会在编辑器侧触发过长或循环 Hook

---

## 脚本一览

### `check.ps1` — 环境健康检查与评分

检查目录结构、配置文件格式与安全、`~\.claude` 与各编辑器的链接状态、Hook 风险、运行时环境，输出得分与报告。

```powershell
powershell -ExecutionPolicy Bypass -File check.ps1
powershell -ExecutionPolicy Bypass -File check.ps1 -Quick   # 跳过 MCP 连通性，更快
```

### `validate_config.py` — 配置校验（V1–V19）

```powershell
python scripts/validate_config.py    # 含 R16 裸 except 扫描、核心 hooks 存在性、loading_tier 等
```

V19（v10.17 新增）比对三大 INDEX 与磁盘双向一致：INDEX 不得引用已删除项，磁盘上的 skill/agent/rule 也不得漏登记。该检查原在 `scripts/tests/_simtest.py`，随该脚本删除移植进来，并顺带补上了此前无人覆盖的 rules-INDEX。

### `python-mcp.ps1` — Python 系 MCP 启动包装

Cursor/编辑器 spawn `uv`/`uvx`/`serena` 前清除 `PYTHONHOME`/`PYTHONPATH`（残缺前缀会导致 `No module named encodings`）。`uv`/`uvx` 未传 `--python` 时钉到 `C:\Python312\python.exe`。RepoMapper 要求 `>=3.13`，调用方须显式 `--python 3.13`。

编辑器 `mcp.json` 各自维护，**禁止经 `sync.ps1` 复制**。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File python-mcp.ps1 C:\Users\DELL\.local\bin\serena.exe --help
```

### `fix-claude-cli.ps1` — 修复 `claude` 命令反复失效 + GitHub MCP 本地二进制

Windows 上 Volta/npm 全局包的 `bin/claude.exe` 会被自更新改名为 `claude.exe.old.*`，shim 仍指向已消失的 exe，表现为「不是内部或外部命令」。官方已弃用 npm 安装。本脚本幂等：卸 Volta/npm shim、把 `~/.local\bin` 放到 User PATH 最前、安装 native `claude.exe`、**关闭 CLI 自动更新**（`DISABLE_AUTOUPDATER=1` + `autoUpdaterStatus=disabled`；插件仍可用 `FORCE_AUTOUPDATE_PLUGINS=1`）、同步 `GITHUB_PERSONAL_ACCESS_TOKEN`、下载 `github-mcp-server.exe`。

```powershell
powershell -ExecutionPolicy Bypass -File fix-claude-cli.ps1              # 修复
powershell -ExecutionPolicy Bypass -File fix-claude-cli.ps1 -DiagnoseOnly # 只诊断
```

禁止再执行 `npm i -g @anthropic-ai/claude-code`、`volta install @anthropic-ai/claude-code` 或 `claude update`。GitHub MCP 必须用本地 stdio，不要改回 `api.githubcopilot.com`（会变成 `mcp_auth` + 0 tools）。修复后需**完全退出** Cursor / Claude Code 再开。

### `fix.ps1` — 修复编辑器内 Hook 超时/僵死

部署 `hooks/_editor_hook_launcher.py`（以 GetConsoleWindow() 判定编辑器/终端），并将 `settings.json` 中 Hook 命令改为 launcher 包装。

```powershell
powershell -ExecutionPolicy Bypass -File fix.ps1          # 诊断
powershell -ExecutionPolicy Bypass -File fix.ps1 -Fix     # 应用修复（后需重启编辑器）
powershell -ExecutionPolicy Bypass -File fix.ps1 -Restore # 撤销包装
```

### `search-github-tools.ps1` — GitHub 工具检索

按分类搜索 GitHub 热门仓库并与本地对比；建议配置 `GITHUB_TOKEN`。

### 测试与辅助

- `test-cursor-guard-regression.ps1` — Cursor Guard 一键回归（上层入口，自动清状态 + 设 UTF-8）；底层实调 `test-cursor-guard-hooks.py`
- `test-sync-dedup.ps1` — sync.ps1 去重逻辑回归，覆盖两处落点（v11 删模板镜像层）：plugin rules、`~/.cursor/rules` 不得遮蔽 plugin
- `audit_hooks.py` — 只读审计 settings.json 的 hook 注册（launcher 覆盖率 + 超时）
- codegraph 索引同步：v11 起由 codegraph v1.5 MCP server 原生监听自动完成（`_lib/knowledge_graph_sync.py` 与双侧 sync hook 已退役；cbm 已永久禁用，`cbm-index.ps1` 已删除）
- `sync_mcp.py`、`sync-compact-window.py` — MCP/压缩窗口同步
- `gen-catalog-index.py` — 重新生成 `catalog/INDEX.md`（含与顶层同名项的权威/变体消歧表）；新增或删除 `catalog/` 条目后必跑

---

## 典型工作流

### 修改配置后

```powershell
powershell -ExecutionPolicy Bypass -File scripts\sync.ps1    # 重新同步 L0
python scripts\validate_config.py                             # 校验
powershell -ExecutionPolicy Bypass -File scripts\check.ps1 -Quick
```

### 日常维护

1. 修改 `~\.claude` 下技能、规则后执行 `sync.ps1`（`-All` 按需）
2. 发现编辑器异常先运行 `fix.ps1` 诊断
3. 定期 `check.ps1` 体检

### 重装后恢复 hook 注册

`settings.json` 含 API token，被 `.gitignore` 排除，因此 **hook 注册与 matcher 无法随仓库克隆恢复**（`MANIFEST.yaml` harness 节只登记 hook 名，不含 matcher/timeout）。可跟踪快照在 `templates/claude-settings/hooks.snippet.json`：

```powershell
$snippet = Get-Content templates\claude-settings\hooks.snippet.json -Raw `
    | ForEach-Object { $_ -replace '\{\{CLAUDE_HOME\}\}', 'C:/Users/<你>/.claude' } `
    | ConvertFrom-Json
$settings = Get-Content settings.json -Raw | ConvertFrom-Json
$settings | Add-Member -NotePropertyName hooks -NotePropertyValue $snippet.hooks -Force
$settings | ConvertTo-Json -Depth 12 | Set-Content settings.json -Encoding UTF8
python scripts\audit_hooks.py    # 核对 20 个注册项与 matcher（含 mcp__serena__.* 两组；v11 退役 kg sync 后 23→20）
```

⚠️ 反向也要维护：**改动 `settings.json` 的 hooks 段后，须同步刷新该快照**，否则重装会退回旧注册（MCP 写工具将绕过验证追踪链）。

---

## 说明

- 脚本内注释与界面文案以中文为主；部分技术字段名保持英文。
- `sync.ps1`、`fix.ps1` 源文件使用 **UTF-8（含 BOM）** 保存，便于 Windows PowerShell 5.1 正确解析中文。
- **文档与脚本版本对齐（v11.1.0）**：`sync.ps1` **v20.0**（多编辑器 1+N，`sync.sh` 已删除），`fix.ps1` v5.x，`check.ps1` v3.x；以各脚本文件头注释为准。
