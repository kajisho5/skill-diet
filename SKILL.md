---
name: skill-diet
description: Audits an Agent Skill (SKILL.md plus its bundled files) against the Agent Skills spec and Anthropic's authoring guidance, and produces a shorter copy that behaves the same, with a findings report and a regression check. Use when the user asks to review, audit, lint, slim down, trim, compress or cut the token cost of a skill or SKILL.md, or says a skill is too long, bloated, ignored or not triggering, even if they only paste the file. Also for Japanese requests such as スキルを短く, SKILL.mdを監査, skillを軽く.
license: MIT
metadata:
  version: "1.0.0"
---

# skill-diet

Goal: the smallest skill that does exactly what the original does. Output: an audit report and a trimmed copy. The original is replaced only when the user asks, through `safe_apply.py`.

Scripts are in `scripts/` next to this file: run them as `python3 <this-skill-dir>/scripts/<name>.py` (Python 3.9+, standard library only).

## Workflow

Copy into the task list and tick off:

```
- [ ] 1. Set up workspace
- [ ] 2. Measure
- [ ] 3. Read everything
- [ ] 4. Build invariants ledger
- [ ] 5. Audit pass
- [ ] 6. Rewrite the copy
- [ ] 7. Repeat passes until 3 in a row find nothing new
- [ ] 8. Regression test
- [ ] 9. Report and deliver
- [ ] 10. Apply only if the user asks
```

1. **Set up.** Create `<name>-trim/` beside the skill (or in a writable temp folder if the skill is read-only). Copy the skill to `original/<name>/` and `trimmed/<name>/` inside it, keeping the folder name so the name check stays valid. Work only in `trimmed/<name>/`.
2. **Measure.** Run `skill_audit.py audit <skill-dir>` and keep the output. Its findings carry IDs from [references/checklist.md](references/checklist.md). Heuristic hits are candidates: confirm each by reading the line.
3. **Read everything.** Read SKILL.md and every bundled text file in full, and know what each script does. Anything you could not read goes in the report under "Not read".
4. **Ledger.** Before changing a word, list every invariant per [references/regression-test.md](references/regression-test.md) §1.
5. **Audit pass.** Walk [references/checklist.md](references/checklist.md) top to bottom. Record each finding as: ID, file:line, quote, action (cut / move / merge / rewrite / keep), estimated tokens saved.
6. **Rewrite** `trimmed/<name>/`. Apply the cut test to every sentence: "If this is gone, would a capable model do anything differently?" No → cut. Unsure → keep and list it. Move task-specific detail to `references/` with a "read when …" pointer; never delete an invariant.
7. **Repeat.** Run `skill_audit.py compare original/<name> trimmed/<name>`, then do another full pass from a viewpoint not yet used:
   - a fresh agent reading cold: what is now unclear?
   - sentence by sentence: does the model already know this?
   - duplication across SKILL.md and references
   - description vs body overlap, trigger words kept
   - what breaks if this line is gone (ledger)
   - load order: are hard rules within the first 5,000 tokens?
   - portability and file structure

   Stop after three consecutive passes add no finding.
8. **Regression test** per [references/regression-test.md](references/regression-test.md) §2–§5. Fix failures by restoring the shortest form that passes.
   If the cuts save under ~10% of body tokens and fix no ERROR/WARN finding, stop here and report "already lean" instead of proposing a trim.
9. **Report and deliver** (format below). Package `trimmed/<name>/` as `<name>.skill` (a zip with the skill folder at its root, or skill-creator's `package_skill.py`) when a file-delivery tool exists.
10. **Apply on request only.** Run `safe_apply.py apply <workspace> <target>`; it prints a plan and refuses if the target changed since the snapshot, the trimmed copy has audit ERRORs, or the name changed. After the user confirms, re-run with `--yes`: it backs up the target to `<workspace>/backups/<time>/` with SHA-256 hashes, applies, and verifies. Give the user the undo command it prints (`safe_apply.py restore <backup> <target> --yes`).

## Decided conflicts between sources

- **Description**: what it does + when to use it, with trigger words (SPEC, BP, CC). No step-by-step procedure (WS).
- **Emphasis**: plain imperative by default. Keep `MUST`/`NEVER`/bold only where it guards a rule observed to be broken, a fragile step, or safety; those are ledger entries.
- **Reasons**: keep a reason only when it decides edge cases. Drop explanation that changes nothing (CC: "what, not how or why"; SC: explain the why).

## Do not

- Rename the skill, change script logic, or remove safety rules. Report them instead.
- Overwrite the original by hand. Only `safe_apply.py` replaces it, so a backup and an undo always exist.
- Give test subagents more permission than the task needs. Grant a narrow tool list; never bypass permission checks.
- Trim rationalization tables or red-flag lists of discipline skills without a pressure test.
- Count a trim as done without the regression test, or claim a test ran when it did not.

## Report (in the user's language)

1. Numbers: the `compare` table (lines, tokens, description length, emphasis), before → after.
2. Findings: table of ID / where / problem / action.
3. Changes grouped as cut, moved, merged, kept-on-purpose, each with the reason.
4. Verification: ledger X/X kept, trigger test result, behavior test result, or "not run" with the reason.
5. Not read / not verified.
6. Where the trimmed copy is, and that applying it is a separate step (10).
