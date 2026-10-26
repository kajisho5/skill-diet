"""Tests for scripts/skill_audit.py and scripts/safe_apply.py (stdlib unittest).

Run: python3 -m unittest discover -s tests -v
All sample skills here are fictional.
"""

import contextlib
import io
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import safe_apply  # noqa: E402
import skill_audit  # noqa: E402

GOOD = """---
name: {name}
description: Converts sample widget logs into a summary table. Use when the user shares a widget log or asks for a widget summary.
---

# Widget summary

1. Read the log.
2. Run `python3 scripts/tool.py`.
3. Write `summary.md`.

Details: [references/more.md](references/more.md)
"""


def make_skill(base, name="widget-summary", body=None, files=None):
    d = Path(base) / name
    (d / "references").mkdir(parents=True)
    (d / "scripts").mkdir()
    (d / "SKILL.md").write_text(body or GOOD.format(name=name), encoding="utf-8")
    (d / "references" / "more.md").write_text("# More\n\nExtra detail.\n",
                                               encoding="utf-8")
    (d / "scripts" / "tool.py").write_text("print('ok')\n", encoding="utf-8")
    for rel, text in (files or {}).items():
        (d / rel).parent.mkdir(parents=True, exist_ok=True)
        (d / rel).write_text(text, encoding="utf-8")
    return d


def ids(report, level=None):
    return {f["id"] for f in report["findings"]
            if level is None or f["level"] == level}


def quiet(fn, *args):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args)


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_clean_skill_has_no_errors_or_warnings(self):
        r = skill_audit.audit(make_skill(self.tmp))
        self.assertEqual([f for f in r["findings"] if f["level"] != "INFO"], [])

    def test_this_repository_passes_its_own_audit(self):
        r = skill_audit.audit(ROOT)
        self.assertEqual(ids(r, "ERROR") | ids(r, "WARN"), set(), r["findings"])

    def test_name_rules(self):
        for bad in ("Widget", "-widget", "wid--get", "claude-helper"):
            body = GOOD.format(name=bad)
            d = make_skill(self.tmp, name="x" + str(abs(hash(bad))), body=body)
            self.assertIn("F3", ids(skill_audit.audit(d), "ERROR"), bad)

    def test_name_must_match_folder(self):
        d = make_skill(self.tmp, name="folder-a",
                       body=GOOD.format(name="other-name"))
        self.assertIn("F4", ids(skill_audit.audit(d)))

    def test_description_errors(self):
        body = GOOD.replace("description: Converts", "description: <b>Converts")
        d = make_skill(self.tmp, body=body.format(name="widget-summary"))
        self.assertIn("D1", ids(skill_audit.audit(d), "ERROR"))

    def test_first_person_and_missing_trigger(self):
        body = ("---\nname: widget-summary\ndescription: I can help you with "
                "widgets.\n---\n\n# W\n\nDo it.\n")
        r = skill_audit.audit(make_skill(self.tmp, body=body))
        self.assertTrue({"D3", "D4"} <= ids(r))

    def test_frontmatter_must_start_on_line_one(self):
        body = "\n" + GOOD.format(name="widget-summary")
        self.assertIn("F1", ids(skill_audit.audit(make_skill(self.tmp, body=body)),
                                "ERROR"))

    def test_block_scalar_description_is_read(self):
        body = ("---\nname: widget-summary\ndescription: >\n  Converts widget "
                "logs.\n  Use when the user shares a widget log.\n---\n\n# W\n")
        r = skill_audit.audit(make_skill(self.tmp, body=body))
        self.assertNotIn("D1", ids(r))
        self.assertGreater(r["stats"]["description_chars"], 30)

    def test_claude_code_only_keys_flagged(self):
        body = GOOD.format(name="widget-summary").replace(
            "---\n\n#", "context: fork\n---\n\n#", 1)
        self.assertIn("P1", ids(skill_audit.audit(make_skill(self.tmp, body=body))))

    def test_reference_problems(self):
        d = make_skill(self.tmp, files={
            "references/more.md": "# More\n\nSee [deep](deep.md).\n",
            "references/deep.md": "# Deep\n",
            "orphan.md": "# Unused\n",
        })
        (d / "SKILL.md").write_text(GOOD.format(name="widget-summary")
                                    + "\n[gone](references/missing.md)\n",
                                    encoding="utf-8")
        r = skill_audit.audit(d)
        self.assertIn("R1", ids(r, "ERROR"))
        self.assertIn("R2", ids(r))
        self.assertIn("R5", ids(r))

    def test_module_imported_by_a_mentioned_script_is_not_flagged(self):
        d = make_skill(self.tmp, files={
            "scripts/tool.py": "from helpers import load\nprint(load())\n",
            "scripts/helpers.py": "def load():\n    return 1\n",
            "scripts/stray.py": "print('unused')\n",
        })
        msgs = [f["message"] for f in skill_audit.audit(d)["findings"] if f["id"] == "R5"]
        self.assertFalse(any("helpers.py" in m for m in msgs), msgs)
        self.assertTrue(any("stray.py" in m for m in msgs), msgs)

    def test_emphasis_density(self):
        rules = "\n".join(f"- You MUST ALWAYS do thing {i}." for i in range(10))
        body = GOOD.format(name="widget-summary") + "\n" + rules + "\n"
        self.assertIn("E1", ids(skill_audit.audit(make_skill(self.tmp, body=body))))

    def test_two_guarded_rules_in_a_short_skill_are_not_flagged(self):
        body = GOOD.format(name="widget-summary") + "\n- NEVER delete input.\n- NEVER skip row checks.\n"
        self.assertNotIn("E1", ids(skill_audit.audit(make_skill(self.tmp, body=body))))

    def test_emphasis_in_inline_code_is_ignored(self):
        body = GOOD.format(name="widget-summary") + "\nKeep `MUST` and `NEVER` rare.\n"
        self.assertNotIn("E1", ids(skill_audit.audit(make_skill(self.tmp, body=body))))

    def test_compare_reports_reduction(self):
        old = make_skill(Path(self.tmp) / "a",
                         body=GOOD.format(name="widget-summary") + "\nPlease note that "
                         "this is basically just a very long padded line.\n" * 30)
        new = make_skill(Path(self.tmp) / "b")
        c = skill_audit.compare(old, new)
        rows = {k: (x, y) for k, x, y, _ in c["rows"]}
        self.assertLess(rows["body_tokens_est"][1], rows["body_tokens_est"][0])
        self.assertFalse(c["name_changed"])

    def test_cli_exit_codes(self):
        d = make_skill(self.tmp)
        self.assertEqual(quiet(skill_audit.main, ["audit", str(d)]), 0)
        self.assertEqual(quiet(skill_audit.main, ["nonsense"]), 2)


class SafeApplyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.target = make_skill(self.tmp / "installed")
        self.ws = self.tmp / "widget-summary-trim"
        shutil.copytree(self.target, self.ws / "original" / "widget-summary")
        shutil.copytree(self.target, self.ws / "trimmed" / "widget-summary")
        self.trim = self.ws / "trimmed" / "widget-summary"
        (self.trim / "SKILL.md").write_text(
            GOOD.format(name="widget-summary").replace("3. Write `summary.md`.\n", "")
            + "3. Write `summary.md`.\n", encoding="utf-8")
        (self.trim / "scripts" / "tool.py").unlink()
        (self.trim / "SKILL.md").write_text(
            (self.trim / "SKILL.md").read_text().replace(
                "2. Run `python3 scripts/tool.py`.\n", ""), encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_plan_only_without_yes(self):
        before = safe_apply.tree_hashes(self.target)
        self.assertEqual(quiet(safe_apply.cmd_apply, self.ws, self.target, False), 0)
        self.assertEqual(safe_apply.tree_hashes(self.target), before)
        self.assertFalse((self.ws / "backups").exists())

    def test_apply_then_restore(self):
        before = safe_apply.tree_hashes(self.target)
        self.assertEqual(quiet(safe_apply.cmd_apply, self.ws, self.target, True), 0)
        self.assertEqual(safe_apply.tree_hashes(self.target),
                         safe_apply.tree_hashes(self.trim))
        self.assertFalse((self.target / "scripts" / "tool.py").exists())
        backup = next((self.ws / "backups").iterdir())
        self.assertEqual(quiet(safe_apply.cmd_restore, backup, self.target,
                               True, False), 0)
        self.assertEqual(safe_apply.tree_hashes(self.target), before)

    def test_refuses_when_target_changed_since_snapshot(self):
        (self.target / "SKILL.md").write_text("edited meanwhile", encoding="utf-8")
        self.assertEqual(quiet(safe_apply.cmd_apply, self.ws, self.target, True), 1)
        self.assertFalse((self.ws / "backups").exists())

    def test_refuses_name_change(self):
        (self.trim / "SKILL.md").write_text(GOOD.format(name="renamed-skill"),
                                            encoding="utf-8")
        self.assertEqual(quiet(safe_apply.cmd_apply, self.ws, self.target, True), 1)

    def test_refuses_trim_with_audit_errors(self):
        (self.trim / "SKILL.md").write_text("no frontmatter", encoding="utf-8")
        self.assertEqual(quiet(safe_apply.cmd_apply, self.ws, self.target, True), 1)

    def test_restore_refuses_edits_after_apply_unless_forced(self):
        quiet(safe_apply.cmd_apply, self.ws, self.target, True)
        backup = next((self.ws / "backups").iterdir())
        (self.target / "SKILL.md").write_text("hand edit", encoding="utf-8")
        self.assertEqual(quiet(safe_apply.cmd_restore, backup, self.target,
                               True, False), 1)
        self.assertEqual(quiet(safe_apply.cmd_restore, backup, self.target,
                               True, True), 0)


if __name__ == "__main__":
    unittest.main()
