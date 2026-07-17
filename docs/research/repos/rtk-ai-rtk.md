# rtk-ai/rtk v0.41.0

> 层: L2 优化 | 置信度: 高 | 刷新: 2026-06-26 | 来源: GitHub Releases + Tags + 官网 三源

## v10.5 delta (2026-07-17)

- **最新元数据**：71,425 stars；GitHub Release **v0.43.0**；`pushed_at` 2026-07-16T10:40:01Z。
- **自 2026-06-29 的变化**：v0.41.0 后已有 v0.43.0 release；版本已跨 minor，需在升级前单独核对 changelog 与 hook 兼容性。
- **本地吸收**：不变——维持现有 pre-rtk-rewrite 接线；不自动升级或改变 RTK 与 caveman 的输入/输出边界。
- **双源**：GitHub API（stars/release/push）+ 仓库 README/既有 Releases 与官网研究记录。


## v10.5.1 delta (2026-07-17)
- **最新元数据**：71,428★；Release **v0.43.0**；`pushed_at` 2026-07-16T10:40:01Z。
- **漂移要点**：shell 输出压缩 60–90%；Rust 单二进制。
- **本地吸收 / 缺口**：hook integrated；与 caveman 输出压缩 **互斥场景** 已声明。
- **不吸收**：强制全局替换所有 shell。
- **双源**：GitHub API + 既有卡片交叉。
## 核心价值

- Shell 命令 60–90% token 压缩
- pre-rtk-rewrite hook 透明重写
- 输入侧压缩（与 caveman 输出侧互补）
- RTK 别名/宏系统

## 证据

- [GitHub rtk-ai/rtk](https://github.com/rtk-ai/rtk)
- 本地 hook 已注册

## 本地映射

| MANIFEST concern | 路径 |
|------------------|------|
| shell_token | `hooks/pre-rtk-rewrite.py` |
| RTK 文档 | `RTK.md` |

## 吸收决策

**采纳** — hook 已注册；与 caveman 互斥（输入 vs 输出）。

## 互博检查

- vs caveman：`[shell_token, output_token]` excludes 互斥

## v10.1 增量

- v0.42.1 版本维持；hook 接线已验收

## v10.2.1 增量（双源刷新 2026-06-19）

- 稳定版 **v0.42.4**（dev-0.43.0-rc 跟踪）；MANIFEST 已对齐，无动作
- 范围提醒：hook 仅拦截 Bash 工具；Read/Grep/Glob 内置工具不经 RTK，需显式 `rtk read/grep/find`

## v10.3.1 增量（双源刷新 2026-06-26）

**版本纠正**：v0.42.4 → v0.41.0（GitHub Releases + Tags 交叉验证）：
- GitHub Releases 最新稳定版 = **v0.41.0** (2026-05-23)
- 原卡片 "v0.42.4" **不存在** — v0.42.x 从未发布稳定版（v10.2.1 增量段记录有误）
- 最新预发布 = dev-0.43.0-rc.286 (2026-06-23)
- v0.41.0 changelog 摘要：tail hints for tee & hints、docker --tail flag forwarding、aggressive filter batch 修复、git status 移除 -uall、kubectl 别名、安装 archive 路径遍历防护（#1250）

**版本演进链路修正**：
```
v0.40.0 → v0.41.0 (2026-05-23, 稳定) → dev-0.43.0-rc.286 (2026-06-23, 预发布)
```
（v0.42.x 跳过，从未发布稳定版）

**本地影响**：
- MANIFEST `shell_token` 版本号需更新 v0.42.4 → v0.41.0
- hook 接线不变（pre-rtk-rewrite.py）
- R14 评估：v0.41.0 → v0.43.0（待稳定）跨 minor，需用户确认

**根因分析**（R16 错误暴漏）：
- v10.2.1 增量段 "稳定版 v0.42.4" 来源不明，可能混淆 npm dev tag 与 stable release
- 教训：版本号必须以 GitHub Releases 页面 "Latest" 标签为准，非 Tags 列表（Tags 包含预发布）

## v10.4 增量（2026-06-29）

- 上游无新稳定 release（仍 v0.41.0）；hook 接线不变
- L2 优化层不受 v10.4 L3 双引擎变更影响
