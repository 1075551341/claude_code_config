# `.claude\scripts` 工具说明

本目录存放 Claude Code 环境维护与辅助脚本（PowerShell）。默认在 **Windows** 下通过 `powershell -ExecutionPolicy Bypass -File <脚本名>` 执行。

---

## 同步与验证（多编辑器）

### 已同步的编辑器（按本机实际目录）

| 编辑器    | 用户目录示例                  | 说明                                  |
| --------- | ----------------------------- | ------------------------------------- |
| Cursor    | `%USERPROFILE%\.cursor`       | 若存在则参与同步；规则走 local plugin |
| Trae      | `%USERPROFILE%\.trae(.cn)`    | 若存在则参与同步                      |
| Qoder     | `%USERPROFILE%\.qoder(-cn)`   | 若不存在则跳过                        |
| WorkBuddy | `%USERPROFILE%\.workbuddy`    | CLAUDE.md + skills/；无 rules 通道    |
| CodeArts  | `%USERPROFILE%\.codeartsdoer` | CLAUDE.md + rule/\*.mdc               |

> v18.3 已移除：Devin

### `sync.ps1` — 多编辑器分层同步（v18.4）

**模式**：

| 模式                     | 同步内容                                                                                                                                                |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 默认                     | **全部** `rules/*.md`（优先软链）+ `CLAUDE.md` + ROUTER；Cursor **每次刷新** `plugins/local/claude-config`（实体 .mdc，Settings 可见）+ `CURSOR-EDITOR` |
| `-Skills`                | 默认 + `skills/` Junction/同步                                                                                                                          |
| `-All`                   | 默认 + `skills/` + `agents/`                                                                                                                            |
| `-ProjectRules`          | 另将 rules 复制到 **当前目录** `.cursor/rules`（显式 opt-in；CWD 为 `~/.claude` 时跳过）                                                                |
| `-Lint` / `-InitProject` | 仅向当前项目目录部署模板，不同步编辑器                                                                                                                  |

**用法**：

```powershell
powershell -ExecutionPolicy Bypass -File sync.ps1                 # 日常：全 rules + 刷新 claude-config
powershell -ExecutionPolicy Bypass -File sync.ps1 -Skills
powershell -ExecutionPolicy Bypass -File sync.ps1 -All            # + agents
powershell -ExecutionPolicy Bypass -File sync.ps1 -All -DryRun    # 预览不写盘
```

> 改 `~/.claude/rules` / `CLAUDE-ROUTER` / `CURSOR-EDITOR` 后跑一次 `sync.ps1` 即可；Cursor Settings 中的 Claude Config 插件内容会随之更新。若列表未变，完全退出 Cursor 再开（仅 Reload 有时不重扫插件）。

> **Claude Code 官方安装**（v10.11 更新）：npm 安装已弃用；Windows 推荐 `irm https://claude.ai/install.ps1 | iex`，macOS/Linux `curl -fsSL https://claude.ai/install.sh | bash`，或 `winget install Anthropic.ClaudeCode`。
> **参数**：

| 参数            | 说明                                  |
| --------------- | ------------------------------------- |
| `-Skills`       | 追加同步 skills/                      |
| `-All`          | 全量（rules+skills+agents+CLAUDE.md） |
| `-ProjectRules` | 复制 rules 到当前项目 .cursor/rules   |
| `-DryRun`       | 仅预览，不写盘                        |
| `-Lint`         | 部署 lint 模板到当前项目              |
| `-InitProject`  | 部署项目初始化模板到当前项目          |

**机制**：

- 文件优先符号链接，失败回退 `Copy-Item`；目录管理员用符号链接、非管理员 `mklink /J` Junction、回退递归复制
- **Cursor 例外**：`rules/*.mdc` 一律实体复制（Settings Rules UI 不索引软链接）
- 规则扩展名：cursor/qoder/codearts → `.mdc`，trae → `.md`；workbuddy 无 rules 通道（仅 CLAUDE.md + skills/）
- **总纲/索引根文件（8 项，v18.4）**：`CLAUDE.md` + `CLAUDE-ROUTER.mdc` + `SPEC.md` + `MANIFEST.yaml` + `agent.yaml` + 三个 `*-INDEX.md`，部署到除 workbuddy 外的所有编辑器（`$ROOT_INDEX_SKIP_EDITORS`）。该集合在 `sync.ps1` / `sync.sh` / `check.ps1` / `templates/cursor-guard/hooks/_lib/impact_sync.py` 四处必须一致，改一处要同步四处
- **写前去重**：删除目标目录同基底名兄弟文件（任意扩展名/大小写），再写新文件
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

| 改动                                            | 必跑                                         |
| ----------------------------------------------- | -------------------------------------------- |
| `rules/*.md` / `skills/` / `agents/` 任何增删改 | `sync.ps1 -All`（默认模式只同步 L0 四件套）  |
| `templates/cursor-guard/**`                     | `deploy-cursor-guard.ps1` + 重启 Cursor      |
| `hooks/`（Claude 侧）                           | 无需同步；settings.json 注册即生效（新会话） |
| `hooks/_lib/gate_messages.md`                   | 双端运行时直读，零操作                       |

> **多项目适配（全局/个人优先）**：默认只同步到 Cursor 个人目录 `~/.cursor/`（rules 软链、skills/agents Junction），**不写入业务项目**。
>
> **重要（Cursor UI）**：Settings → Rules → **User** 页签**不会枚举** `~/.cursor/rules/*.mdc`。全局 `.mdc` 靠本地插件 `~/.cursor/plugins/local/claude-config`（**实体 .mdc 副本**，因插件禁止外链软链）。skills/agents 仍 Junction。改规则后跑 `sync.ps1`，然后**完全退出并重开 Cursor**（Reload 有时不重扫 local plugins）。

### 同步后建议自测

1. 在各编辑器中确认配置可读、无报错
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

### `fix.ps1` — 修复编辑器内 Hook 超时/僵死

部署 `hooks/_editor_hook_launcher.py`（以 GetConsoleWindow() 判定编辑器/终端），并将 `settings.json` 中 Hook 命令改为 launcher 包装。

```powershell
powershell -ExecutionPolicy Bypass -File fix.ps1          # 诊断
powershell -ExecutionPolicy Bypass -File fix.ps1 -Fix     # 应用修复（后需重启编辑器）
powershell -ExecutionPolicy Bypass -File fix.ps1 -Restore # 撤销包装
```

### `collect-experience.ps1` — 开发经验收集

从 Git 历史抽取信息，在 `experiences/` 下生成当日经验 Markdown 摘要。

### `search-github-tools.ps1` — GitHub 工具检索

按分类搜索 GitHub 热门仓库并与本地对比；建议配置 `GITHUB_TOKEN`。

### 测试与辅助

- `test-cursor-guard-regression.ps1` — Cursor Guard 一键回归（上层入口，自动清状态 + 设 UTF-8）；底层实调 `test-cursor-guard-hooks.py`
- `test-sync-dedup.ps1` — sync.ps1 去重逻辑回归，覆盖三处落点：plugin rules、模板副本 rules、`~/.cursor/rules` 不得遮蔽 plugin
- `audit_hooks.py` — 只读审计 settings.json 的 hook 注册（launcher 覆盖率 + 超时）
- `cbm-index.ps1` — codebase-memory 索引辅助；**cbm 自 v10.10 永久禁用**，仅留作手工排查，日常勿用
- `hooks/_lib/knowledge_graph_sync.py` — codegraph + cbm 双引擎同步（PostToolUse debounce / Stop force / sync.ps1）
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

`settings.json` 含 API token，被 `.gitignore` 排除，因此 **hook 注册与 matcher 无法随仓库克隆恢复**（`agent.yaml` 只登记 hook 名，不含 matcher/timeout）。可跟踪快照在 `templates/claude-settings/hooks.snippet.json`：

```powershell
$snippet = Get-Content templates\claude-settings\hooks.snippet.json -Raw `
    | ForEach-Object { $_ -replace '\{\{CLAUDE_HOME\}\}', 'C:/Users/<你>/.claude' } `
    | ConvertFrom-Json
$settings = Get-Content settings.json -Raw | ConvertFrom-Json
$settings | Add-Member -NotePropertyName hooks -NotePropertyValue $snippet.hooks -Force
$settings | ConvertTo-Json -Depth 12 | Set-Content settings.json -Encoding UTF8
python scripts\audit_hooks.py    # 核对 23 个注册项与 matcher（含 mcp__serena__.* 两组）
```

⚠️ 反向也要维护：**改动 `settings.json` 的 hooks 段后，须同步刷新该快照**，否则重装会退回旧注册（MCP 写工具将绕过验证追踪链）。

---

## 说明

- 脚本内注释与界面文案以中文为主；部分技术字段名保持英文。
- `sync.ps1`、`fix.ps1` 源文件使用 **UTF-8（含 BOM）** 保存，便于 Windows PowerShell 5.1 正确解析中文。
- **文档与脚本版本对齐（v10.17.0）**：`sync.ps1` **v18.4**（`sync.sh` v2.3），`fix.ps1` v5.x，`check.ps1` v3.x；以各脚本文件头注释为准。
