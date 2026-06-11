# Hooks 钩子系统 v5.0

> Claude Code 专用，不同步编辑器。14 核心 hooks + 37 _optional
> 五阶段×三层矩阵：骨架层(always-on) + 执行层(reactive) + 横切层(cross-cutting)
> **v5.0 变更**：SessionStart 改由 superpowers + claude-mem 插件负责，本地不再重复

## 目录结构

| 目录 | 数量 | 用途 |
|------|------|------|
| `hooks/` | 15 核心 | standard profile（settings.json 已注册） |
| `hooks/_optional/` | 37 | strict profile / 已精简冗余 |
| `hooks/_deprecated/` | 1 | pre-task-planner（禁止启用） |

---

## 14 核心 Hook 清单（SessionStart 由插件负责）

### SessionStart — 由插件负责
| 提供者 | 功能 |
|--------|------|
| superpowers plugin | using-superpowers bootstrap |
| claude-mem plugin | worker 启动 + 上下文注入 |

> 本地 `session-start-bootstrap.py` 保留备用（无插件环境），但不在 settings.local.json 中注册。

### PreToolUse (6)
| Hook | 触发 | 功能 | 层 |
|------|------|------|-----|
| `pre-context-injector.py` | Task/Bash/Write/Edit | 项目 CLAUDE.md 上下文注入（每会话一次） | 骨架 |
| `pre-rtk-rewrite.py` | Bash | RTK Shell 命令压缩改写 | 横切 |
| `pre-bash-guard.py` | Bash | 危险命令拦截 + git --no-verify 阻止 + dep check | 骨架 |
| `pre-read-before-edit.py` | Write/Edit | GSD read-before-edit 强制 | 执行 |
| `pre-config-protection.py` | Write/Edit | 配置文件保护 | 骨架 |
| `pre-manifest-validator.py` | 全局 | MANIFEST 归属校验防互博 | 横切 |

### PostToolUse (3)
| Hook | 触发 | 功能 | 层 |
|------|------|------|-----|
| `post-edit-format.py` | Edit/Write | 代码格式化 + Lint | 执行 |
| `post-secret-detector.py` | Edit/Write | 密钥/Token/密码泄露扫描 | 横切 |
| `post-operation-log.py` | 全局 | 操作审计日志 | 横切 |

### PreCompact (1)
| Hook | 功能 | 层 |
|------|------|-----|
| `pre-compact-state.py` | 压缩前状态快照 | 横切 |

### Stop (4)
| Hook | 功能 | 层 |
|------|------|-----|
| `stop-quality-gate.py` | schema_drift + security_anchor + scope_reduction | 执行 |
| `stop-pattern-extraction.py` | 会话模式提取→experiences/ | 执行 |
| `stop-session-summary.py` | 会话摘要 | 执行 |
| `stop-readme-updater.py` | README 自动更新 | 执行 |

---

## 精简说明（v2.4 → v3.0）

| 移除的 hook | 去向 | 原因 |
|-------------|------|------|
| `pre-dep-checker.py` | 合并到 pre-bash-guard | 功能重叠 |
| `pre-git-hook-bypass-block.py` | 合并到 pre-bash-guard | 功能重叠 |
| `post-edit-lint.py` | 合并到 post-edit-format | 合并减少调用 |
| `post-test-runner.py` | _optional/ | 60s 太重，改为验证阶段手动 |
| `post-doc-reminder.py` | 合并到 stop-readme-updater | 功能重叠 |
| `stop-notify.py` | _optional/ | 桌面通知与核心流程无关 |
| `stop-debug-checker.py` | 合并到 stop-quality-gate | 功能重叠 |
| `stop-daily-summary.py` | 合并到 stop-session-summary | 功能重叠 |

**新增**
| `pre-manifest-validator.py` | 新增 | PreToolUse 校验 MANIFEST 归属，防左右手互博 |

---

## Profile 配置

```bash
ECC_HOOK_PROFILE=minimal   # 仅生命周期+安全 (5 hooks)
ECC_HOOK_PROFILE=standard  # 默认：15 核心 (当前)
ECC_HOOK_PROFILE=strict    # 15核心 + _optional/ 安全扫描
```

**strict 额外注册**：
- `_optional/pre-userprompt-secret-scan.py` (dwarvesf/claude-guardrails)
- `_optional/post-prompt-injection-scan.py` (lasso-security/claude-hooks)

---

## Cursor 编辑器

Claude Code hooks **不在 Cursor 内执行**（`_editor_hook_launcher.py` 快速跳过）。  
Cursor Guard v1.1（`templates/cursor-guard/` + `deploy-cursor-guard.ps1`）：同步、70%/90% 压缩、codegraph 路由、shell/密钥守卫、维护提示。详见 `docs/CURSOR_EDITOR_SETUP.md` 与 `docs/SYNC_GUIDE.md` §Cursor Guard。

## 设计原则

1. **事件驱动**：PreToolUse(守卫) → Tool executes → PostToolUse(审计)
2. **Profile 控制**：环境变量切换，无需改配置文件
3. **平台自适应**：_editor_hook_launcher.py 检测 Claude Code/Cursor/Windsurf
4. **Python 3**：跨平台 Windows/macOS/Linux

## 退出码

| 码 | 含义 |
|----|------|
| 0 | 允许继续 |
| 2 | 阻止执行 |

---

_版本：3.0 | 15 核心 + 37 optional_
