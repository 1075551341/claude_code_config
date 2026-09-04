---
trigger: always_on
alwaysApply: true
layer: skeleton
description: 代码开发时始终启用 — 骨架层：编码规范 + 铁律 R1–R20 + 三横切 + 阈值
paths:
  - "**"
---

# CORE — 机器执行层骨架

> SSOT：三横切、阈值、编码规范、铁律 R1–R20。治理详情→`skills/governance`。五阶段→`CLAUDE.md`。R20 六字段模板→`skills/verification-before-completion`。

## 三横切

L1 治理（MANIFEST 防互博 + hook） | L2 RTK + caveman + 70/90 阈值 | L3 codegraph + Firecrawl/Exa。codebase-memory 已禁用（全盘索引爆内存）。UA removed v10.5。

## 上下文阈值

| 使用率 | Cursor               | Claude Code          |
| ------ | -------------------- | -------------------- |
| <70%   | 正常                 | 正常                 |
| 70%    | `/summarize`         | `/compact`           |
| 90%    | 强制压缩或新子 Agent | 强制压缩或新子 Agent |

禁止达到 100%。GSD 70% 为任务边界（切子 Agent/写制品），非强制压缩。子 Agent：无依赖并行，有依赖串行，同制品禁并行写。

## 优先级与规范

简单至上；精准响应；主动确认；第一性原理。DRY + 单一职责；不可变优先；安全→`skills/security-policy`；注释模板→`skills/governance`。文件宜 200–400 行（上限 800）。热路径：测量→优化→验证。业务逻辑禁 `new Date()`/`Date.now()`/`datetime.now()`（Clock 注入；CLI/UI 除外）。

## 文件编码与写入（R2/R9）

默认 UTF-8 无 BOM；保留目标文件既有 BOM/EOL。内容写入一律 Edit/Write，禁止 `echo`/`tee`/`Set-Content`/`Out-File`/heredoc 重定向写文件。含中文输出的命令先确保 `[Console]::OutputEncoding=UTF8`。检测到乱码（U+FFFD/GBK/非法 UTF-8）立即回滚，禁止在损坏内容上叠加。二进制禁 Read/Edit。

## 错误升级

瞬态失败重试 ≤R5（同方案 2 次）→ 非核心降级 DONE_WITH_CONCERNS → 权限/数据风险需确认 → 安全/不可逆硬阻断。禁止静默吞错（R16）。

## 工程原则

KISS / YAGNI / 删除过时优先于兼容层 / 依赖克制。详参 `skills/governance`。

## 铁律 R1–R20

| #   | 约束          | 必做                                                                                                                                                                                                | 禁止                                         |
| --- | ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| R1  | 任务完成      | 验证通过才声称完成                                                                                                                                                                                  | 以叙述代替证据                               |
| R2  | 修改确认      | Read→Edit→Read                                                                                                                                                                                      | 未读就改；shell 写内容                       |
| R3  | 关联全修      | blast-radius + Grep 全修后确认残留=0                                                                                                                                                                | 只改点名文件                                 |
| R4  | 配置变更      | 扫引用 + INDEX/MANIFEST + 构建                                                                                                                                                                      | 改配置不改引用                               |
| R5  | 重试上限      | 同方案 ≤2 次后换方案或上报                                                                                                                                                                          | 空转同一失败路径                             |
| R6  | 非简单        | ①→⑤ 全链                                                                                                                                                                                            | 把非简单当简单旁路                           |
| R7  | 交叉验证      | 完成前按 verification skill                                                                                                                                                                         | 跳过验证清单                                 |
| R8  | 高危确认      | 删数据/强推 main/DROP 先确认                                                                                                                                                                        | 未确认执行不可逆操作                         |
| R9  | 命令安全      | Windows 主 shell=`pwsh`；禁 `cd`+重定向、禁 `powershell -Command`。Qoder MCP 启动脚本例外                                                                                                           | 用 PS5.1 当 Agent 主壳                       |
| R10 | 简洁优先      | 高内聚低耦合、最小改动集                                                                                                                                                                            | 顺手重构、过度抽象                           |
| R11 | 安全默认      | 不信任输入；密钥走环境变量/`settings.local.json`                                                                                                                                                    | 硬编码密钥                                   |
| R12 | 子 Agent 隔离 | fresh context + 制品通信                                                                                                                                                                            | 共享可变状态                                 |
| R13 | 制品存活      | PROJECT/REQUIREMENTS/ROADMAP/STATE 跨会话                                                                                                                                                           | 只放会话内存                                 |
| R14 | 版本克制      | 非必要不升 major；详情→governance                                                                                                                                                                   | 无评估追 latest major                        |
| R15 | 工具与包管理  | 语言统一标准 PM，不可用再兜底；OS 选稳定 CLI。见下节                                                                                                                                                | 异种 lock 点餐；幻影依赖；Windows 回落 PS5.1 |
| R16 | 错误暴漏      | 异常传播或显式报告                                                                                                                                                                                  | 裸 `except: pass`                            |
| R17 | 代码探索      | 仅 `codegraph_explore`；影响面→CRG；无双图 deny                                                                                                                                                     | 跳级 Grep/Read；调用 cbm                     |
| R18 | 记忆优先      | 为什么/约定/偏好→claude-mem                                                                                                                                                                         | 把偏好塞进 codegraph                         |
| R19 | Git 禁令      | 禁自动 stash/commit/push；禁自动建/切分支（含 `worktree add -b`）；禁强推 main                                                                                                                      | 无用户本条显式指令改 Git 历史或分支          |
| R20 | 会话终验      | 逐条回放满足/遗漏/错改/漏改/原功能/影响范围；配置/文档/注释同步；独立审查一次找齐且每轮全新开审；修改走 `change-implementer`；证据须观察输出。模板→verification skill。有写入则 Stop 须新鲜审查记录 | resume 上轮审查者；边审边改；只连审不改      |

### R15 两层（标准 → 不可用再兜底）

**A. 语言包管理器**：JS/TS `pnpm`→`npm`；Python `uv`→`pip`；Go `go`；Rust `cargo`；.NET `dotnet`；Java Maven→Gradle；PHP Composer；Ruby Bundler→`gem`。禁止双 lock；禁止 `npx`/`pip install X` 装未写入清单的包（幻影依赖）。已有异种 lock 仍走该语言标准，迁移只留一份 lock。

**B. 操作系统 CLI**（R9 管安全，本节管选用）：Windows 标准 **pwsh ≥ 7.5**；仅有 7.0–7.4 时用该 pwsh 并警告升级；**禁止** `powershell.exe`（5.1）与 `cmd.exe` 作 Agent 主壳。macOS：zsh + Homebrew，不可用再 bash 5+。Linux：bash 5+ 优先，包管理跟发行版（apt/dnf/pacman）不混装。

### R17–R18（禁止跳级）

| 需求                 | 首选                                                               | 禁止                     |
| -------------------- | ------------------------------------------------------------------ | ------------------------ |
| 结构/调用链/怎么运作 | `codegraph_explore`                                                | 直接 Grep/Read           |
| 影响面/审查/PR       | CRG `get_minimal_context` / `get_impact_radius` / `detect_changes` | 凭直觉估范围             |
| 为什么/约定/偏好     | claude-mem                                                         | 塞入 codegraph；启用 cbm |

codegraph 返回源码视为已读。改前查 blast-radius；残留引用>0 不得声称完成。eligible git 仓无双图 **deny**。

### R3/R4 变更彻底性

改函数签名/类型/配置/重命名前：CRG impact（有图）+ codegraph blast-radius + Grep。只改指定文件、跳过 Grep、「看起来差不多」均禁止。残留>0 违反 R1。

### R20 短条款

独立审查只找问题、一次找齐、每轮全新开审（禁止 resume）；清单齐后 `change-implementer` 集中改；最多 3 轮。计划未批准禁止声称完成。六字段与硬门模板→verification skill。

## 工作约定

中文沟通。Git→`skills/git-workflow`。同步→`scripts/sync.ps1`。Karpathy→`skills/karpathy-guidelines`。
