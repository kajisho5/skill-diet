# Changelog

## 1.1.0

- Audit-only mode: when the user asks only for a review, the skill stops after the audit pass and reports findings without rewriting.
- `skill_audit.py`: the emphasis finding (E1) now needs more than 3 markers as well as a high density, so a short skill that keeps two guarded `NEVER` rules is no longer flagged.
- `skill_audit.py`: files under `.github/` and `dist/` are no longer counted as part of the skill.
- README rewritten in full, with the measured before/after of a sample skill (`examples/csv-tidy/`), logo and icon.

## 1.0.0

First release.

- Audit a skill against the Agent Skills spec, Anthropic's authoring best practices and the Claude Code skills docs, with ID-numbered findings (`references/checklist.md`).
- `scripts/skill_audit.py`: standard-library checker for frontmatter, description, length and loading budget, filler, hedges, emphasis, duplicates, references and portability; `compare` shows before/after numbers.
- Invariants ledger, trigger test and behavior test (original vs trimmed, blind comparison) so a shorter skill does not quietly lose behavior (`references/regression-test.md`).
- `scripts/safe_apply.py`: applies a trimmed copy only after a hash-verified backup, refuses when the target changed since the snapshot, and restores with one command.
