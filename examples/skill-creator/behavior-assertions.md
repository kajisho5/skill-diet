# Behavior-test assertions (from the ledger)

## t1: create a new skill (fictional Glimmerbrook Bakery), stop after saving test cases
- A1 (I12) SKILL.md frontmatter has `name` and a `description` that states what it does AND when to use it, with trigger contexts ("pushy").
- A2 (I22/I23) 2-3 realistic test prompts saved to `glimmerbrook-orders/evals/evals.json` with `skill_name` and `evals[].id/prompt/expected_output/files`.
- A3 (I23) evals.json has no assertions/expectations yet (prompts only).
- A4 (I8/I9/I22) notes.md records the intent questions / interview (edge cases, formats) and that test prompts would be shared with the user before running.

## t2: grade iteration-1, aggregate, present results (headless)
- B1 (I33) `grading.json` in each run dir with expectations fields exactly `text`, `passed`, `evidence`.
- B2 (I34) `benchmark.json` and `benchmark.md` produced by `scripts.aggregate_benchmark` (transcript shows the command), with_skill and without_skill configs present.
- B3 (I36/I37/I38/I67) viewer generated with `eval-viewer/generate_review.py --static <path>` (headless) including `--benchmark`; no hand-written HTML.
- B4 (I39/I37) final message tells the user about the Outputs and Benchmark tabs / leaving feedback, and that Submit All Reviews downloads feedback.json.

## t3: build trigger eval set and present for review (no loop)
- C1 (I51) ~20 queries saved as JSON `[{"query", "should_trigger"}]`.
- C2 (I53/I54) 8-10 should-trigger and 8-10 should-not-trigger; negatives are near-misses (labels/shipping/PDF adjacent), not obviously irrelevant.
- C3 (I55) review HTML built from `assets/eval_review.html` with all three placeholders replaced (no `__..._PLACEHOLDER__` left), data inserted as a raw JS array.
- C4 (I56/I57 not violated) `run_loop` not started; message tells user to review/edit and click "Export Eval Set".
