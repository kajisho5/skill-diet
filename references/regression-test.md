# Regression test: the trimmed skill must behave like the original

## Contents
- 1. Invariants ledger (always)
- 2. Trigger test (when the description changed)
- 3. Behavior test (when the body changed)
- 4. Without subagents
- 5. Pass criteria

## 1. Invariants ledger (always)

Build it from the original before editing, as `ledger.md` in the workspace:

| ID | Kind | Original (file:line, quote) | Trimmed location |
|---|---|---|---|
| I1 | limit | SKILL.md:42 "max 20 rows per batch" | |

Kinds: limit, path, command, format, condition, order, safety, trigger, example, rationalization.
Use the Keep list in checklist.md to decide what is an invariant. When unsure, add it.

After the rewrite, fill "Trimmed location" for every row (file:line). A row with no location is a regression unless the user approved removing it; list approved removals in the report.

## 2. Trigger test (when the description changed)

1. Write 16–20 realistic queries: half should trigger, half are near misses that share keywords but need something else. Use concrete details (file names, casual wording). Reuse the skill's existing trigger evals if it has any.
2. If the `claude` CLI is available, run skill-creator's `scripts/run_eval.py` once with the old description and once with the new one. Timeouts count as "not triggered", so check that at least one should-trigger query fired in each run; if none did, the run is invalid. Re-run sequentially with a longer timeout (120 s worked in testing).
3. Otherwise, approximate: give a fresh subagent the list of installed skill descriptions (with this skill's old description), ask which skill it would consult for each query; repeat with the new description. Report it as an approximation.
4. A regression is a query the old description handled correctly and the new one does not.

## 3. Behavior test (when the body changed)

1. Take 3 realistic tasks the skill exists for. Prefer the skill's `evals/` cases; otherwise derive them from its examples. Use fictional data.
2. For each task, in the same turn, spawn two fresh subagents: one pointed at `original/<name>/`, one at `trimmed/<name>/`. Same prompt, separate output folders. Give each only the tools the task needs (for example Read, Write, Edit, Bash).
3. Write 2–4 checkable assertions per task, mostly taken from the ledger (the trimmed run must still do what the invariants require).
4. Grade both runs. Then give both outputs, unlabeled, to a third subagent and ask which better completes the task (skill-creator's `agents/comparator.md` if available).
5. Read the transcripts, not only the outputs: did the trimmed run open moved reference files when it needed them? Did it stop doing something the original made it do?

## 4. Without subagents

On surfaces with no subagents (claude.ai chat), run each task yourself with the trimmed skill only, check the assertions, and say in the report that the test was self-run and weaker. Skip the blind comparison and the trigger test, and say so.

## 5. Pass criteria

- Ledger: every row has a location or a user-approved removal.
- Trigger test: no regressions, or each one explained and accepted by the user.
- Behavior test: trimmed passes every assertion the original passes; blind comparison is a win or tie on every task.
- Noise check: before counting a loss, run the original once more on that task. A difference that also appears between two runs of the original is run-to-run variation, not a regression; report it as an ambiguity in the original.

If anything fails, restore the missing content (shortest form that passes), then re-run the failing test only.
