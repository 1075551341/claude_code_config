# -*- coding: utf-8 -*-
"""issue_state.py 判定逻辑单元测试（v11.1.1 相似匹配重构）。

直接运行：`python hooks/tests/test_issue_state.py`（退出码 0 = 全过）。
用临时 CLAUDE_HOME 隔离状态；时间相关断言通过直接改写 state 字段模拟，不 sleep。
"""
from __future__ import annotations

import importlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
LIB_DIR = TESTS_DIR.parent / "_lib"
sys.path.insert(0, str(LIB_DIR))

_tmp = tempfile.mkdtemp(prefix="issue-state-test-")
os.environ["CLAUDE_HOME"] = _tmp

import issue_state  # noqa: E402

importlib.reload(issue_state)

CFG = issue_state.merge_config({"min_interval_sec": 0})  # 关防抖便于断言
CWD = r"C:\Proj\App"
PASSED = []
FAILED = []


def check(name: str, cond: bool, detail: str = "") -> None:
    (PASSED if cond else FAILED).append(name)
    mark = "OK " if cond else "FAIL"
    print(f"  [{mark}] {name}" + (f" -- {detail}" if detail and not cond else ""))


def reset_state() -> None:
    f = issue_state.state_file()
    if f.exists():
        f.unlink()


def raw_state() -> dict:
    f = issue_state.state_file()
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


# 1. 首问不注入、建桶
reset_state()
r1 = issue_state.record("修复登录接口报错 500，auth_service.py 里 token 校验失败", CWD, "s1", CFG)
check("should_not_inject_when_first_ask", r1 is None)
check("should_create_entry_when_first_ask", len(raw_state()) == 1)

# 2. 同措辞跨会话重问 → 硬提醒
r2 = issue_state.record("修复登录接口报错 500，auth_service.py 里 token 校验失败", CWD, "s2", CFG)
check("should_inject_hard_when_exact_repeat", bool(r2) and "禁止从头重来" in r2)

# 3. 中文改写命中（bigram 相似）：无逐字重复仍应命中同一条目
r3 = issue_state.record("登录接口 500 还是报错，token 校验没通过", CWD, "s3", CFG)
check("should_match_when_chinese_paraphrase", bool(r3), f"state={len(raw_state())}")
check("should_not_create_second_entry_when_paraphrase", len(raw_state()) == 1)

# 4. 跨端 cwd 形态归一：大小写/斜杠方向/尾分隔符不同仍命中
r4 = issue_state.record("修复登录接口报错 500，auth_service.py 里 token 校验失败", "c:/proj/app/", "s4", CFG)
check("should_match_when_cwd_form_differs", bool(r4))
check("should_keep_single_entry_when_cwd_form_differs", len(raw_state()) == 1)

# 5. 不同问题不误报（同 cwd）
r5 = issue_state.record("数据库迁移脚本 migrate_users.sql 执行超时，需要分批提交", CWD, "s5", CFG)
check("should_not_inject_when_different_issue", r5 is None)
check("should_create_new_entry_when_different_issue", len(raw_state()) == 2)

# 6. 泛化追问续接：同会话最近条目存在 → 注入且不建新桶
n_before = len(raw_state())
r6 = issue_state.record("还是不行", CWD, "s5", CFG)
check("should_attach_generic_followup_to_recent_entry", bool(r6))
check("should_not_create_bucket_for_generic_followup", len(raw_state()) == n_before)

# 7. 泛化追问无近期同会话条目 → 忽略且不建桶
r7 = issue_state.record("还是不行", CWD, "fresh-session", CFG)
check("should_ignore_generic_followup_without_recent_entry", r7 is None)
check("should_not_create_bucket_when_generic_ignored", len(raw_state()) == n_before)

# 8. resolved：首次命中轻提示，再次命中判回归升级硬提醒
marked = issue_state.mark_session_resolved("s5")
check("should_mark_resolved_for_session_entries", marked >= 1)
r8a = issue_state.record("数据库迁移脚本 migrate_users.sql 执行超时，需要分批提交", CWD, "s6", CFG)
check("should_light_message_when_first_hit_after_resolved", bool(r8a) and "提示" in r8a and "禁止" not in r8a)
r8b = issue_state.record("数据库迁移脚本 migrate_users.sql 执行超时，需要分批提交", CWD, "s7", CFG)
check("should_escalate_regression_when_second_hit_after_resolved", bool(r8b) and "回归" in r8b)

# 9. 旧格式条目（无 features）不崩溃
st = raw_state()
st["legacy0000ab"] = {"count": 3, "first_ts": time.time(), "last_ts": time.time(),
                      "last_inject_ts": 0, "last_session_id": "old", "sessions": ["old"]}
issue_state.state_file().write_text(json.dumps(st, ensure_ascii=False), encoding="utf-8")
r9 = issue_state.record("一个全新的前端构建缓存问题 vite cache 失效", CWD, "s8", CFG)
check("should_survive_legacy_entries_without_features", r9 is None)

# 10. 防抖：min_interval_sec 内命中不重复注入但计数增加
cfg_db = issue_state.merge_config({"min_interval_sec": 3600})
issue_state.record("防抖测试 debounce_case.py 报 TypeError", CWD, "s9", cfg_db)
first_inject = issue_state.record("防抖测试 debounce_case.py 报 TypeError", CWD, "s9", cfg_db)
second_inject = issue_state.record("防抖测试 debounce_case.py 报 TypeError", CWD, "s9", cfg_db)
key = [k for k, v in raw_state().items() if "debounce_case.py" in json.dumps(v.get("features", {}))]
cnt = raw_state()[key[0]]["count"] if key else 0
check("should_inject_once_within_debounce_window", bool(first_inject) and second_inject is None)
check("should_still_count_within_debounce_window", cnt == 3, f"count={cnt}")

# 11. compact 后重问（同会话 >1h 间隔）→ 轻提示
st = raw_state()
k11 = [k for k, v in st.items() if v.get("last_session_id") == "s9"][0]
st[k11]["last_ts"] = time.time() - 4000
st[k11]["last_inject_ts"] = 0
issue_state.state_file().write_text(json.dumps(st, ensure_ascii=False), encoding="utf-8")
r11 = issue_state.record("防抖测试 debounce_case.py 报 TypeError", CWD, "s9", CFG)
check("should_light_message_when_compact_gap_reask", bool(r11) and "compact" in r11)

# 12. 纯弱信号阈值抬高：两个只有少量共同泛词的不同问题不误报
reset_state()
issue_state.record("页面加载速度优化方案讨论", CWD, "w1", CFG)
r12 = issue_state.record("页面布局样式错乱修一下", CWD, "w2", CFG)
check("should_not_match_when_weak_overlap_low", r12 is None)

print()
print(f"passed={len(PASSED)} failed={len(FAILED)}")
if FAILED:
    print("FAILED:", ", ".join(FAILED))
    sys.exit(1)
print("ALL ISSUE-STATE TESTS PASSED")
sys.exit(0)
