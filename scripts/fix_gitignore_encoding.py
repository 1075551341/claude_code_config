# -*- coding: utf-8 -*-
"""修 .gitignore：GBK→UTF-8 乱码注释修复 + /.cursor 白名单移除 + /.ruff_cache/ 增补"""
import io

P = r"C:\Users\DELL\.claude\.gitignore"
raw = open(P, "rb").read()

enc = None
for e in ("utf-8-sig", "utf-8", "gbk"):
    try:
        text = raw.decode(e)
        enc = e
        break
    except UnicodeDecodeError:
        continue
print("detected encoding:", enc)

lines = text.splitlines()
out = []
removed_cursor_whitelist = 0
fixed_comments = 0
added_ruff = False

skip_next_comment = False
for i, ln in enumerate(lines):
    s = ln.strip()

    # 1) 移除 /.cursor/* 白名单三行 + 其紧邻的乱码说明注释行
    if s.startswith("/.cursor/") or s.startswith("!/.cursor/"):
        removed_cursor_whitelist += 1
        # 若上一条已输出行是本块的注释行（含 Cursor assets 字样），撤掉它
        if out and "Cursor assets" in out[-1]:
            out.pop()
            fixed_comments += 1
        continue

    # 2) 修复已知乱码注释行（按特征重写为干净中文）
    if s.startswith("#") and ("Misc generated" in s):
        out.append("# Misc generated：根目录临时 txt/html 忽略（skills/*/LICENSE.txt 与 templates/*.txt 属版本化资产勿删）")
        fixed_comments += 1
        continue
    if s.startswith("#") and s.startswith("# v10.17"):
        out.append("# v10.17：运行制品（计划/报告/执行记录）不入版本库——只保留最新一份在本地。")
        fixed_comments += 1
        continue
    if s.startswith("#") and s.startswith("# v11.3.5"):
        out.append("# v11.3.5：编辑器同步临时产物 + 项目级 hook 运行时状态")
        fixed_comments += 1
        continue

    out.append(ln)

    # 3) Python 段后补 /.ruff_cache/
    if s == "__pycache__/" and not added_ruff:
        out.append("/.ruff_cache/")
        added_ruff = True

# 4) 若 .cursor 块的注释行是独立乱码行（含"Workspace-local"）且仍在输出中，清理
out = [l for l in out if not ("Workspace-local Cursor assets" in l)]

new = "\n".join(out) + ("\n" if text.endswith(("\n",)) else "")
open(P, "w", encoding="utf-8", newline="").write(new)

print("removed .cursor whitelist lines:", removed_cursor_whitelist)
print("fixed comment lines:", fixed_comments)
print("added /.ruff_cache/:", added_ruff)
print("total lines:", len(lines), "->", len(out))
