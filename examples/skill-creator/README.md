# Real-world example: Anthropic's `skill-creator`

An agent running skill-diet audited and trimmed **skill-creator** from [anthropics/skills](https://github.com/anthropics/skills/tree/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/skill-creator) (commit `dbd4588`, 2026-10-09, Apache-2.0). It is a real, widely used skill, and was chosen because its body (about 8,200 tokens) is over the spec's ~5,000-token recommendation.

This is an independent example. It is not affiliated with or endorsed by Anthropic, and the trimmed copy was **not** proposed upstream. The original is redistributed and modified here under the Apache License 2.0 ([`LICENSE.skill-creator.txt`](LICENSE.skill-creator.txt)); modified files carry a notice at the top.

## Files

| File | What it is |
|---|---|
| [`SKILL.before.md`](SKILL.before.md) | The original SKILL.md, unchanged |
| [`SKILL.after.md`](SKILL.after.md) | The trimmed SKILL.md (modified file) |
| [`description-optimization.after.md`](description-optimization.after.md) | New reference file: the description-optimization section moved out of the body (modified file) |
| [`audit-before.txt`](audit-before.txt) | `skill_audit.py audit` on the original |
| [`compare.txt`](compare.txt) | `skill_audit.py compare` original → trimmed |
| [`ledger.md`](ledger.md) | 74 invariants with their original and new locations |
| [`trigger-original.json`](trigger-original.json), [`trigger-trimmed.json`](trigger-trimmed.json) | Trigger test results (skill-creator's own `run_eval.py`) |
| [`behavior-assertions.md`](behavior-assertions.md) | The behavior-test tasks and assertions |
| [`blind-results.md`](blind-results.md) | Every blind comparison, with which side was which |

Everything else in the skill (all scripts, `eval-viewer/`, `assets/`, `agents/*.md`, `references/schemas.md`, `LICENSE.txt`) was kept byte-identical; SHA-256 checked, 0 differences.

## Numbers

| | before | after | change |
|---|---|---|---|
| SKILL.md body lines | 482 | 264 | −45% |
| SKILL.md body tokens (est.) | 8,225 | 4,414 | −46% |
| Headings | 34 | 23 | −32% |
| Bold spans | 46 | 15 | −67% |
| Filler / hedge lines | 16 / 12 | 4 / 2 | |
| Description | 319 chars | 319 chars | unchanged on purpose |
| Supporting files tokens (est., loaded on demand) | 12,533 | 13,635 | +9%: the moved section |

What the cut buys: the body is loaded every time skill-creator triggers, and after context compaction Claude Code keeps only the first 5,000 tokens of each skill. In the original, everything from about line 313 on (the iteration loop, the Claude.ai and Cowork rules, description optimization) sat past that point. In the trimmed copy, the whole body fits.

## What changed

- **Cut:** pep talk and sign-offs ("Cool? Cool.", "Good luck!", "billions a year in economic value"), the story about who uses the skill, filler and hedge phrases, decorative bold and headings, the closing recap of the process, one of three near-identical `feedback.json` rows.
- **Moved:** "Description Optimization" (about 1,000 tokens, needed only when the user accepts that step) to `references/description-optimization.md`, almost word for word, with a pointer in SKILL.md.
- **Merged:** the Claude.ai and Cowork sections into one "Environment differences" block; three statements of "generate the viewer before evaluating yourself" into one near the top; three statements of the `--static` / feedback-download rule into one.
- **Kept on purpose:** the description verbatim; every command, path, flag and JSON field name; both all-caps rules (the viewer rule, which the original says guards an observed failure, and the `/skill-test` ban); the "explain the why" and "ALWAYS/NEVER is a yellow flag" advice, which shapes the skills users write.
- **One behavior-visible change:** the original contradicts itself on test-case directory names (`eval-0/`, `eval-1/` on one line; "a descriptive name … not just eval-0, use it for the directory" on another). The trimmed copy keeps only the explicit rule.

## Verification

- **Ledger:** 74 of 74 invariants located in the trimmed files.
- **Independent check** (run separately from the trimming agent): all 66 backticked items (commands, paths, flags, field names) and all 17 distinct numbers in the original appear in the trimmed SKILL.md or the new reference file, except the `eval-0/` example above and two mentions of `package_skill.py` whose rule survives in other words ("packaging works anywhere with Python") next to the `python -m scripts.package_skill` command.
- **Trigger test** (20 queries, 10 should trigger and 10 near misses, fictional names, one run each, sequential, `claude -p` limited to the Skill and Read tools): original 17/20, trimmed 17/20, all negatives correct in both. The description is byte-identical, so the two differing queries are run-to-run variation.
- **Behavior test:** three tasks with fictional data (create a skill and stop after saving test cases; grade, aggregate and present a headless review; build a trigger eval set and present it without running the loop). Fresh `claude -p` runs with a narrow tool list for each version. Every assertion passed for both versions in every run. In task 3 the trimmed runs opened the moved reference file when they needed it.
- **Blind comparison:** first round, the original won tasks 1 and 2 and the trimmed copy won task 3. Before counting those as regressions, the original was compared with itself: on both tasks, one run of the original beat another run of the original, and in later pairs the trimmed copy won tasks 1 and 2. The losses are within the variation of the unchanged original. Details: [`blind-results.md`](blind-results.md).

## Not tested

- Claude.ai (no subagents) and Cowork behavior.
- A full `run_loop.py` description-optimization run.
- Interactive use of the review viewer.
- More than 1–2 runs per version per task. The weakest evidence is the analyst pass in task 2 (writing notes into `benchmark.json`), done in 1 of 2 original runs and 0 of 1 trimmed run; all runs wrote the analysis in their final message.
- Most of `eval-viewer/viewer.html` and the HTML layout in `scripts/generate_report.py` were not read; they are byte-identical and no change relies on them.
