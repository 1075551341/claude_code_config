# `.claude\scripts` 工具说明

本目录存放 Claude Code 环境维护与辅助脚本（PowerShell）。默认在 **Windows** 下通过 `powershell -ExecutionPolicy Bypass -File <脚本名>` 执行。

关闭claude和node进程
Get-Process | Where-Object { $_.Name -like "*claude*" } | Stop-Process -Force
Get-Process | Where-Object { $_.Name -like "_node_" } | Stop-Process -Force

---

## 同步与验证（多编辑器）

### 已同步的编辑器（按本机实际目录）

| 编辑器   | 用户目录示例              | 说明             |
| -------- | ------------------------- | ---------------- |
| Cursor   | `%USERPROFILE%\.cursor`   | 若存在则参与同步 |
| Trae     | `%USERPROFILE%\.trae`     | 若存在则参与同步 |
| Windsurf | `%USERPROFILE%\.windsurf` | 若存在则参与同步 |
| Qoder    | `%USERPROFILE%\.qoder`    | 若不存在则跳过   |

### 同步的配置组件

- **技能库**（`skills/`）— 通过软链接或目录联接（Junction）指向 `~\.claude\skills`
- **代理库**（`agents/`）— 同上
- **规则库**（`rules/`）— 同上
- **`hooks/`** — **不同步到各编辑器**（避免陈旧编辑器配置仍能通过链接调用阻塞型 Hook；编辑器会直接读取 `~\.claude\settings.json` 中的绝对路径）
- **`scripts/`** — **不同步到各编辑器**（仅在 `~\.claude\scripts` 下维护）

**复制同步的文件**（非链接，改源文件后需重新执行 `sync.ps1`）：

- `CLAUDE.md`

**不同步的配置文件**：

- `.mcp.json`
- `settings.json`（CLI 完整配置仅保留在 `~/.claude`）

### 同步特点

- 管理员：符号链接；非管理员：Junction（目录联接）
- 源在 `~\.claude` 更新后，链接目标自动一致；复制类文件需再跑同步
- 强制重建链接：`sync.ps1 -Force`；仅预览：`sync.ps1 -DryRun`
- **环境哨兵**：`sync.ps1` 会向各编辑器用户目录与 **`%APPDATA%\<Editor>\User\settings.json`（Roaming）** 仅**合并** `env.CLAUDE_IN_EDITOR`，并移除 `terminal.integrated.env.windows.CLAUDE_IN_EDITOR`，避免污染集成终端里的 Claude Code CLI（与 `fix.ps1` 的 FIX C 一致）
- **不破坏界面配置**：若目标 `settings.json` 无法按**严格 JSON** 解析（如 JSONC、`//` 注释），脚本**跳过写回**并告警，不会用空对象覆盖字体、字号、主题、`workbench` 等；写回时使用 `ConvertTo-Json -Depth 100`，降低深层嵌套被截断的风险（仍可能改变键顺序与空白，属 PowerShell 限制）

### 同步后建议自测

1. 在各编辑器中确认配置可读、无报错
2. **确认字体、字号、颜色主题、缩放等未异常**（若 settings 为严格 JSON，仅合并 env；JSONC 时脚本会跳过写回）
3. 抽查技能、代理、规则是否生效
4. 确认 MCP 配置与本地服务一致
5. 确认不会在编辑器侧触发过长或循环 Hook

---

## 脚本一览

### `sync.ps1` — 将工具链同步到各编辑器（v8.4）

**作用**：仅同步 4 项到各编辑器目录：

- `skills/`、`agents/`、`rules/` → **软链接**（Junction/符号链接）
- `CLAUDE.md` → **复制**（必须是真实文件，不能是软链接）

**同时写入（只合并 env，不整文件替换为空白）**：在 **`~\.<editor>\settings.json`** 与 **Roaming `User\settings.json`** 中合并 `env.CLAUDE_IN_EDITOR`，并清理 `terminal.integrated.env.windows.CLAUDE_IN_EDITOR`（编辑器目录不存在则跳过）。脚本头部注释与运行横幅为中文说明。

**不再同步**：`hooks/`、`scripts/`（CLI 专用）、`.mcp.json`、Claude 侧的 `settings.json`（不把 `~\.claude\settings.json` 拷到编辑器）

**自动清理**：检测并移除旧版遗留的 `hooks/`、`scripts/` 软链接

**忽略文件**：若不存在则创建 `.<editor>ignore`，排除 `hooks/`、`plugins/` 等索引噪音

**用法**：

```powershell
powershell -ExecutionPolicy Bypass -File sync.ps1
powershell -ExecutionPolicy Bypass -File C:\Users\dell\.claude\scripts\sync.ps1
powershell -ExecutionPolicy Bypass -File sync.ps1 -Force
powershell -ExecutionPolicy Bypass -File sync.ps1 -DryRun
```

**参数**：

| 参数      | 说明             |
| --------- | ---------------- |
| `-Force`  | 强制重建所有链接 |
| `-DryRun` | 仅预览，不写盘   |

---

### `check.ps1` — 环境健康检查与评分（v3.1）

**作用**：检查目录结构、配置文件格式与安全、`~\.claude` 与各编辑器的链接状态、Hook 风险、Python/Node/Git/Docker 等运行时、（可选）MCP 相关依赖与连通性、工具箱统计，并输出得分与 `logs\check-YYYYMMDD.md` 报告。

**用法**：

```powershell
 powershell -ExecutionPolicy Bypass -File C:\Users\dell\.claude\scripts\check.ps1
powershell -ExecutionPolicy Bypass -File check.ps1 -Quick   # 跳过 MCP 连通性相关检查，更快
```

**参数**：

| 参数     | 说明                |
| -------- | ------------------- |
| `-Quick` | 跳过 MCP 连通性测试 |

---

### `fix.ps1` — 修复编辑器内 Hook 超时/僵死（v5.0）

**作用**：部署 `~\.claude\hooks\_editor_hook_launcher.py`（**v2.0**），以 **GetConsoleWindow()** 为主判定：扩展宿主拉起的 Python **无控制台**时快速跳过，仅输出 `{"continue":true}`；**真实终端**下仍经 launcher **转调**原 Hook，逻辑完整执行。同时将 `~\.claude\settings.json` 中各 Python Hook 命令改为 `python ...\_editor_hook_launcher.py <原脚本>`。

**`-Fix` 还会做**：删除各 `~\.<editor>\hooks` 的**陈旧软链接**；在 **用户目录与 Roaming** 的 `settings.json` 中合并 `env.CLAUDE_IN_EDITOR`（若解析失败则**跳过写回**以免覆盖字体/主题等）；移除 `terminal.integrated.env.windows.CLAUDE_IN_EDITOR`；更新 `.<editor>ignore`。

**用法**：

```powershell
# 诊断（launcher、Hook 命令格式、CLAUDE_IN_EDITOR、陈旧 hooks 链接）
powershell -ExecutionPolicy Bypass -File fix.ps1

# 应用修复（部署 launcher、改写 Hook 命令、环境哨兵）
 powershell -ExecutionPolicy Bypass -File C:\Users\dell\.claude\scripts\fix.ps1 -Fix

# 撤销（Hook 恢复为直接 python，见脚本说明）
powershell -ExecutionPolicy Bypass -File fix.ps1 -Restore
```

**参数**：

| 参数       | 说明                                  |
| ---------- | ------------------------------------- |
| `-Fix`     | 应用修复                              |
| `-Restore` | 从 settings.json 中移除 launcher 包装 |

> **注意**：`-Fix` 后请**完全退出并重启**各编辑器。若 Hook 日志仍偶现秒级耗时，可再执行 `sync.ps1` 确认 Roaming `User\settings.json` 的 `env.CLAUDE_IN_EDITOR`，并确认集成终端的 `terminal.integrated.env.windows` 中无同名变量。

---

### `collect-experience.ps1` — 开发经验收集

**作用**：从 Git 历史等抽取信息，在 `~\.claude\experiences` 下生成当日经验 Markdown 摘要。

**用法**：

```powershell
powershell -ExecutionPolicy Bypass -File collect-experience.ps1
powershell -ExecutionPolicy Bypass -File collect-experience.ps1 "D:\path\to\project"
```

---

### `search-github-tools.ps1` — GitHub 工具检索

**作用**：按分类搜索 GitHub 热门仓库并与本地 `skills` 等对比，可选保存报告。建议配置环境变量 `GITHUB_TOKEN` 提高 API 限额。

**用法**：

```powershell
powershell -ExecutionPolicy Bypass -File search-github-tools.ps1
powershell -ExecutionPolicy Bypass -File search-github-tools.ps1 -Category all -SaveReport
```

---

## 典型工作流

### 首次配置或修改后

```powershell
# 1. 修复 hooks（部署 launcher + 改写 settings 中 Hook 命令，防止编辑器内僵死）
powershell -ExecutionPolicy Bypass -File .claude\scripts\fix.ps1 -Fix

# 2. 重新同步（只同步 4 项：skills/ agents/ rules/ + CLAUDE.md）
powershell -ExecutionPolicy Bypass -File .claude\scripts\sync.ps1

# 3. 重启编辑器，验证不再僵死
```

### 日常维护

1. 修改 `~\.claude` 下技能、规则后执行 `sync.ps1`
2. 发现编辑器异常时先运行 `fix.ps1` 诊断
3. 定期执行 `check.ps1` 做环境体检

### 已验证现状

1. Cursor 会直接加载 `~\.claude\settings.json`（用户级 Claude 配置），因此执行日志里出现 `~\.claude\hooks\*.py` 属正常，**不代表** `sync.ps1` 把 `hooks/` 链到了编辑器目录。
2. **launcher v2.0** 以无控制台（编辑器）与有控制台（CLI）区分；IDE 侧成功跳过时 Hook 耗时多在 **约 30–60ms** 量级。
3. 若日志里**同一脚本**时而毫秒级、时而数秒，多为子进程环境差异；请对照 Cursor **Hooks 执行记录**，并确认 `%APPDATA%\Cursor\User\settings.json` 中 `env.CLAUDE_IN_EDITOR` 仍存在，且 `terminal.integrated.env.windows` 中**没有**残留同名变量。

### 如需撤销 launcher 包装

```powershell
powershell -ExecutionPolicy Bypass -File .claude\scripts\fix.ps1 -Restore
```

---

## 说明

- 脚本内注释与界面文案以中文为主；部分技术字段名（如 JSON 键名）保持英文。
- `sync.ps1`、`fix.ps1` 源文件使用 **UTF-8（含 BOM）** 保存，便于 Windows PowerShell 5.1 正确解析中文；若 CMD/旧控制台仍显示乱码，可改用 **Windows Terminal** 或先执行 `chcp 65001`。
- 历史文件 `SYNC_RESULT.md` 已合并进本文档，不再单独维护。
- **文档与脚本版本对齐**：`sync.ps1` **v8.4**，`fix.ps1` **v5.0**（launcher + GetConsoleWindow），`check.ps1` **v3.1**；升级脚本后若 README 未提新版本号，以各 `.ps1` 文件头注释为准。
