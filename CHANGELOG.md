# Changelog

## 1.0.0

First release.

- Audit a skill against the Agent Skills spec, Anthropic's authoring best practices and the Claude Code skills docs, with ID-numbered findings (`references/checklist.md`).
- `scripts/skill_audit.py`: standard-library checker for frontmatter, description, length and loading budget, filler, hedges, emphasis, duplicates, references and portability; `compare` shows before/after numbers.
- Invariants ledger, trigger test and behavior test (original vs trimmed, blind comparison) so a shorter skill does not quietly lose behavior (`references/regression-test.md`).
- `scripts/safe_apply.py`: applies a trimmed copy only after a hash-verified backup, refuses when the target changed since the snapshot, and restores with one command.
