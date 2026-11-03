#!/usr/bin/env python3
"""Regression tests for scripts/principles.py (R21-R25 merged iron laws)."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("principles", ROOT / "scripts" / "principles.py")
assert SPEC and SPEC.loader
principles = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(principles)


class PrinciplesTests(unittest.TestCase):
    def source_block(self) -> str:
        text, _, _ = principles.read_text(principles.SOURCE)
        block = principles.extract_block(text)
        self.assertIsNotNone(block)
        return block

    def test_source_block_is_5_groups_18_subs(self):
        block = self.source_block()
        self.assertEqual(principles.validate_block(block), [])
        groups = principles.GROUP_RE.findall(block)
        subs = principles.SUB_RE.findall(block)
        self.assertEqual(len(groups), principles.EXPECTED_GROUPS)
        self.assertEqual({f"R{g}" for g, _ in groups}, set(principles.GROUP_NAMES))
        self.assertEqual(len(subs), principles.EXPECTED_SUBS_COUNT)
        self.assertEqual({(int(g), int(s)) for g, s in subs}, principles.EXPECTED_SUBS)

    def test_validate_rejects_missing_rule(self):
        block = self.source_block().replace(
            "- **R25.3 简单满足即不升级**：够用即止。\n", ""
        )
        self.assertTrue(any("R sub-rules" in e or "R sub ids" in e for e in principles.validate_block(block)))

    def test_validate_rejects_duplicate_rule(self):
        line = "- **R22.2 DRY**：重复逻辑第三次或成本有证据才抽象。\n"
        block = self.source_block().replace(line, line + line)
        self.assertTrue(any("R sub-rules" in e or "R section counts" in e for e in principles.validate_block(block)))

    def test_validate_rejects_missing_conflict_table(self):
        block = "\n".join(
            line for line in self.source_block().splitlines()
            if not principles.CONFLICT_RE.match(line)
        )
        self.assertTrue(any("conflict rows" in e for e in principles.validate_block(block)))

    def test_validate_rejects_subrule_order(self):
        a = "- **R21.1 第一性原理**：先理解真实目标与约束，再选方案。\n"
        b = "- **R21.2 本质优先/YAGNI**：先解本质；不为假设未来过度设计。\n"
        block = self.source_block().replace(a + b, b + a)
        self.assertTrue(any("out of order" in e for e in principles.validate_block(block)))

    def test_validate_rejects_subrule_moved_between_groups(self):
        line = "- **R21.1 第一性原理**：先理解真实目标与约束，再选方案。\n"
        block = self.source_block().replace(line, "").replace(
            "#### R22 简洁与设计\n", "#### R22 简洁与设计\n" + line
        )
        self.assertTrue(
            any("sub-rule R21.1" in e or "R section counts" in e
                for e in principles.validate_block(block))
        )

    def test_validate_rejects_conflict_right_ref(self):
        block = self.source_block().replace(
            "| R21.1 / R24.2 | 原理决定是否自建；商品化默认 R24.2。 |",
            "| R21.1 / R24.2 | 原理决定是否自建；商品化默认 R99.9。 |",
        )
        self.assertTrue(
            any("conflict refs missing" in e for e in principles.validate_block(block))
        )

    def test_validate_rejects_subrule_after_conflict_heading(self):
        line = "- **R25.3 简单满足即不升级**：够用即止。\n"
        block = self.source_block().replace(line, "").replace(
            "#### 冲突裁决（R 组）\n", "#### 冲突裁决（R 组）\n" + line
        )
        self.assertTrue(
            any("under no group" in e or "R section counts" in e
                for e in principles.validate_block(block))
        )

    def test_validate_rejects_duplicate_conflict(self):
        line = "| R21.1 / R24.2 | 原理决定是否自建；商品化默认 R24.2。 |\n"
        block = self.source_block() + "\n" + line
        self.assertTrue(any("duplicate conflict" in e for e in principles.validate_block(block)))

    def test_validate_rejects_group_map_swap(self):
        block = self.source_block().replace(
            "#### R21 核心思想", "#### R21 架构"
        )
        self.assertTrue(any("group name" in e for e in principles.validate_block(block)))

    def test_stale_id_regex(self):
        for text in ("R26", "R38", "R21-R38", "P5", "P1–P18"):
            self.assertIsNotNone(principles.STALE_RE.search(text), text)
        for text in ("P0", "P1", "P3", "R25", "R21.1"):
            self.assertIsNone(principles.STALE_RE.search(text), text)

    def test_validate_rejects_old_p_block(self):
        block = self.source_block() + "\n<!-- principles:start -->\n"
        self.assertTrue(any("old P namespace" in e for e in principles.validate_block(block)))

    def test_encoded_size_matches_crlf_file(self):
        self.assertEqual(principles.encoded_size("a\nb\n", True, False), 6)
        self.assertEqual(principles.encoded_size("a\nb\n", False, False), 4)

    def test_replace_block_with_markers(self):
        text = f"# t\n\n{principles.START}\nold\n{principles.END}\n"
        updated = principles.replace_block(text, "BLOCK")
        self.assertIsNotNone(updated)
        self.assertIn("BLOCK", updated)
        self.assertNotIn("old", updated)

    def test_block_under_iron_law_rejects_toolchain_parent(self):
        text = "## 铁律\n\n## 工具链地板\n\n" + self.source_block() + "\n"
        self.assertFalse(principles.block_under_iron_law(text))

    def test_reposition_crlf_keeps_single_blank_line(self):
        text = (
            "## 铁律\r\n\r\ntable\r\n\r\n## 工具链地板\r\n\r\n"
            + self.source_block()
            + "\r\n"
        )
        updated = principles.reposition_block(text, "BLOCK", Path("CORE.md"))
        self.assertIsNotNone(updated)
        self.assertNotIn("\r\n\r\n\r\n", updated)
        self.assertIn("BLOCK", updated)

    def test_reposition_uses_next_h2_not_toolchain(self):
        text = (
            "## 铁律\n\ntable\n\n## 安全\n\nx\n\n## 工具链地板\n\n"
            + self.source_block()
            + "\n"
        )
        updated = principles.reposition_block(text, "BLOCK", Path("CORE.md"))
        self.assertIsNotNone(updated)
        self.assertLess(updated.find("BLOCK"), updated.find("## 安全"))

    def test_reposition_block_moves_before_toolchain(self):
        text = "## 铁律\n\n## 工具链地板\n\n" + self.source_block() + "\n\n## 开发习惯\n"
        updated = principles.reposition_block(text, "BLOCK", Path("CORE.md"))
        self.assertIsNotNone(updated)
        self.assertNotIn("engineering-rules:start", updated)
        self.assertIn("BLOCK\n\n## 工具链地板", updated)

    def test_migrate_core_without_marker(self):
        text = "# CORE\n\n## 铁律\n\ntable\n\n## 工具链地板\n\n"
        updated = principles.migrate_block(text, "BLOCK", Path("CORE.md"))
        self.assertIsNotNone(updated)
        self.assertIn("BLOCK\n\n## 工具链地板", updated)

    def test_migrate_block_inserts_before_tool_gate(self):
        text = (
            "<!-- principles:start -->\n## 工程原则（全局常驻）\nold\n"
            "<!-- principles:end -->\n\n## 工具门控与路由\n"
        )
        updated = principles.migrate_block(text, "BLOCK", Path("AGENTS.md"))
        self.assertIsNotNone(updated)
        self.assertNotIn("<!-- principles:start -->", updated)
        self.assertIn("## 铁律\n\nBLOCK\n\n## 工具门控与路由", updated)

    def test_check_detects_target_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "CORE.md"
            target = root / "AGENTS.md"
            doc = root / "doc.md"
            source.write_text("# CORE\n\n## 铁律\n\n" + self.source_block() + "\n", encoding="utf-8")
            target.write_text(
                "# CORE\n\n## 铁律\n\n"
                + self.source_block().replace(
                    "**R22.1 KISS**：简单直接，避免多余复杂度。",
                    "**R22.1 KISS**：简单直接，避免多余复杂度（改）。",
                )
                + "\n",
                encoding="utf-8",
            )
            doc.write_text(
                "\n".join(f"- **R{g}.{s} x**：x" for g, s in sorted(principles.EXPECTED_SUBS))
                + "\n## 裁决\n",
                encoding="utf-8",
            )
            old = (
                principles.SOURCE,
                principles.DOC,
                principles.ALL_TARGETS,
                principles.REQUIRED_TARGETS,
                principles.OC_AGENTS,
                principles.DSH_AGENTS,
            )
            try:
                principles.SOURCE = source
                principles.DOC = doc
                principles.ALL_TARGETS = [source, target]
                principles.REQUIRED_TARGETS = [source, target]
                principles.OC_AGENTS = target
                principles.DSH_AGENTS = target
                err = io.StringIO()
                with contextlib.redirect_stderr(err):
                    self.assertEqual(principles.check(), 1)
                self.assertIn("drifted from source", err.getvalue())
            finally:
                (
                    principles.SOURCE,
                    principles.DOC,
                    principles.ALL_TARGETS,
                    principles.REQUIRED_TARGETS,
                    principles.OC_AGENTS,
                    principles.DSH_AGENTS,
                ) = old

    def test_sync_removes_old_p_block_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "CORE.md"
            target = root / "AGENTS.md"
            source.write_text("# CORE\n\n## 铁律\n\n" + self.source_block() + "\n", encoding="utf-8")
            target.write_text(
                "# AGENTS\n\n## 铁律\n\n"
                + self.source_block()
                + "\n\n<!-- principles:start -->\nold\n<!-- principles:end -->\n",
                encoding="utf-8",
            )
            old = (
                principles.SOURCE,
                principles.SYNC_TARGETS,
                principles.OC_AGENTS,
                principles.DSH_AGENTS,
            )
            try:
                principles.SOURCE = source
                principles.SYNC_TARGETS = [target]
                principles.OC_AGENTS = target
                principles.DSH_AGENTS = target
                out = io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
                    self.assertEqual(principles.sync(False), 0)
                text = target.read_text(encoding="utf-8")
                self.assertNotIn("<!-- principles:start -->", text)
                self.assertIn(principles.START, text)
                out2 = io.StringIO()
                with contextlib.redirect_stdout(out2), contextlib.redirect_stderr(out2):
                    self.assertEqual(principles.sync(False), 0)
                self.assertIn("0 file(s) updated", out2.getvalue())
            finally:
                (
                    principles.SOURCE,
                    principles.SYNC_TARGETS,
                    principles.OC_AGENTS,
                    principles.DSH_AGENTS,
                ) = old

    def test_strip_old_p_block(self):
        text = "A\n<!-- principles:start -->\nold\n<!-- principles:end -->\nB"
        stripped = principles.strip_old_p_block(text)
        self.assertNotIn("principles:start", stripped)
        self.assertIn("A", stripped)
        self.assertIn("B", stripped)

    def test_sync_rejects_malformed_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "CORE.md"
            target = root / "AGENTS.md"
            source.write_text(
                "# CORE\n\n## 铁律\n\n<!-- principles:start -->\nold\n",
                encoding="utf-8",
            )
            target.write_text("# AGENTS\n\n## 铁律\n\n", encoding="utf-8")
            old = (principles.SOURCE, principles.SYNC_TARGETS)
            try:
                principles.SOURCE = source
                principles.SYNC_TARGETS = [target]
                err = io.StringIO()
                with contextlib.redirect_stdout(err), contextlib.redirect_stderr(err):
                    self.assertEqual(principles.sync(False), 1)
                self.assertIn("source has malformed/duplicate markers", err.getvalue())
            finally:
                principles.SOURCE, principles.SYNC_TARGETS = old

    def test_sync_rejects_malformed_old_p_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "CORE.md"
            target = root / "AGENTS.md"
            source.write_text("# CORE\n\n## 铁律\n\n" + self.source_block() + "\n", encoding="utf-8")
            original = "# AGENTS\n\n## 铁律\n\n<!-- principles:start -->\nold\n"
            target.write_text(original, encoding="utf-8")
            old = (principles.SOURCE, principles.SYNC_TARGETS)
            try:
                principles.SOURCE = source
                principles.SYNC_TARGETS = [target]
                err = io.StringIO()
                with contextlib.redirect_stdout(err), contextlib.redirect_stderr(err):
                    self.assertEqual(principles.sync(False), 1)
                self.assertEqual(target.read_text(encoding="utf-8"), original)
                self.assertIn("malformed old P block", err.getvalue())
            finally:
                principles.SOURCE, principles.SYNC_TARGETS = old

    def test_block_span_rejects_following_h2(self):
        text = (
            "## 铁律\n\n"
            + self.source_block().replace(
                principles.END, "\n## 工具链地板\n\nx\n" + principles.END
            )
            + "\n"
        )
        self.assertFalse(principles.block_span_ok(text))

    def test_sync_rejects_target_end_after_h2(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "CORE.md"
            target = root / "AGENTS.md"
            source.write_text("# CORE\n\n## 铁律\n\n" + self.source_block() + "\n", encoding="utf-8")
            bad_block = self.source_block().replace(
                principles.END, "\n## 工具链地板\n\nx\n" + principles.END
            )
            original = "# AGENTS\n\n## 铁律\n\n" + bad_block + "\n"
            target.write_text(original, encoding="utf-8")
            old = (principles.SOURCE, principles.SYNC_TARGETS)
            try:
                principles.SOURCE = source
                principles.SYNC_TARGETS = [target]
                err = io.StringIO()
                with contextlib.redirect_stdout(err), contextlib.redirect_stderr(err):
                    self.assertEqual(principles.sync(False), 1)
                self.assertEqual(target.read_text(encoding="utf-8"), original)
                self.assertIn("block spans a following ## section", err.getvalue())
            finally:
                principles.SOURCE, principles.SYNC_TARGETS = old

    def test_sync_migrates_markerless_agents(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "CORE.md"
            target = root / "AGENTS.md"
            source.write_text("# CORE\n\n## 铁律\n\n" + self.source_block() + "\n", encoding="utf-8")
            target.write_text(
                "# AGENTS\n\n## 铁律\n\ntable\n\n## 工具门控与路由\n\n",
                encoding="utf-8",
            )
            old = (principles.SOURCE, principles.SYNC_TARGETS)
            try:
                principles.SOURCE = source
                principles.SYNC_TARGETS = [target]
                out = io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
                    self.assertEqual(principles.sync(False), 0)
                text = target.read_text(encoding="utf-8")
                self.assertIn(principles.START, text)
                self.assertLess(text.find("## 铁律"), text.find(principles.START))
                self.assertLess(text.find(principles.START), text.find("## 工具门控与路由"))
            finally:
                principles.SOURCE, principles.SYNC_TARGETS = old

    def test_sync_migrates_old_p_only_agents(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "CORE.md"
            target = root / "AGENTS.md"
            source.write_text("# CORE\n\n## 铁律\n\n" + self.source_block() + "\n", encoding="utf-8")
            target.write_text(
                "# AGENTS\n\n## 铁律\n\ntable\n\n"
                "<!-- principles:start -->\nold\n<!-- principles:end -->\n\n"
                "## 工具门控与路由\n\n",
                encoding="utf-8",
            )
            old = (principles.SOURCE, principles.SYNC_TARGETS)
            try:
                principles.SOURCE = source
                principles.SYNC_TARGETS = [target]
                out = io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
                    self.assertEqual(principles.sync(False), 0)
                text = target.read_text(encoding="utf-8")
                self.assertNotIn("<!-- principles:start -->", text)
                self.assertIn(principles.START, text)
            finally:
                principles.SOURCE, principles.SYNC_TARGETS = old

    def test_sync_migrates_markerless_core(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "CORE.md"
            target = root / "target"
            target.mkdir()
            target = target / "CORE.md"
            source.write_text("# CORE\n\n## 铁律\n\n" + self.source_block() + "\n", encoding="utf-8")
            target.write_text(
                "# CORE\n\n## 铁律\n\ntable\n\n## 工具链地板\n\n",
                encoding="utf-8",
            )
            old = (principles.SOURCE, principles.SYNC_TARGETS)
            try:
                principles.SOURCE = source
                principles.SYNC_TARGETS = [target]
                out = io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
                    self.assertEqual(principles.sync(False), 0)
                text = target.read_text(encoding="utf-8")
                self.assertIn(principles.START, text)
                self.assertLess(text.find(principles.START), text.find("## 工具链地板"))
            finally:
                principles.SOURCE, principles.SYNC_TARGETS = old

    def test_strip_old_p_block_rejects_malformed(self):
        self.assertIsNone(principles.strip_old_p_block("<!-- principles:start -->\nold"))
        self.assertIsNone(principles.strip_old_p_block("old\n<!-- principles:end -->"))
        self.assertIsNone(
            principles.strip_old_p_block(
                "<!-- principles:end -->\n<!-- principles:start -->\n"
            )
        )


    def test_crlf_round_trip_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "AGENTS.md"
            path.write_bytes(b"a\r\nb\r\n")
            text, crlf, bom = principles.read_text(path)
            self.assertTrue(crlf)
            principles.write_text(path, text, crlf, bom)
            first = path.read_bytes()
            text, crlf, bom = principles.read_text(path)
            principles.write_text(path, text, crlf, bom)
            second = path.read_bytes()
            self.assertNotIn(b"\r\r\n", first)
            self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
