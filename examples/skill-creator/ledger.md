# Invariants ledger: skill-creator

Source: `original/skill-creator/SKILL.md` (anthropics/skills @ dbd4588). Line numbers are file lines (frontmatter included).
Files left byte-identical (their invariants are kept by construction): `agents/grader.md`, `agents/comparator.md`, `agents/analyzer.md`, `references/schemas.md`, `scripts/*`, `eval-viewer/*`, `assets/eval_review.html`, `LICENSE.txt`.

| ID | Kind | Original (file:line, quote) | Trimmed location |
|---|---|---|---|
| I1 | trigger | SKILL.md:3 description (create, modify, improve, measure; evals, benchmark, variance, triggering accuracy) || SKILL.md:3 (unchanged) |
| I2 | order | SKILL.md:12-20 stages: intent → draft → test prompts → evaluate (qual + quant) → rewrite → repeat → "Expand the test set and try again at larger scale" || SKILL.md:10-16 |
| I3 | condition | SKILL.md:22-24 "figure out where the user is in this process"; existing draft → "go straight to the eval/iterate part" || SKILL.md:18 |
| I4 | condition | SKILL.md:26 user says "just vibe with me" / no evals → do that || SKILL.md:18 |
| I5 | order | SKILL.md:28 description improver after the skill is done (order flexible); SKILL.md:454 "save it until you've fully finished making the skill and the user agrees" || SKILL.md:16, 18 (Cowork-scoped wait) |
| I6 | format | SKILL.md:36-41 "evaluation"/"benchmark" OK; "JSON"/"assertion" need serious cues; briefly define terms when unsure || SKILL.md:24 |
| I7 | condition | SKILL.md:49 "turn this into a skill" → extract tools, steps, corrections, I/O formats from history; user fills gaps and confirms before next step || SKILL.md:32 |
| I8 | format | SKILL.md:51-54 four questions (enable, trigger, output format, test cases?); verifiable outputs benefit, subjective often don't; suggest default, user decides || SKILL.md:34-37 |
| I9 | order | SKILL.md:58 ask about edge cases, I/O formats, example files, success criteria, dependencies; "Wait to write test prompts until you've got this part ironed out" || SKILL.md:41 |
| I10 | condition | SKILL.md:60 check available MCPs; research in parallel via subagents if available, otherwise inline || SKILL.md:41 |
| I11 | format | SKILL.md:66-69 components: name, description, compatibility (optional, rarely needed), rest of skill || SKILL.md:45-48 |
| I12 | format/example | SKILL.md:67 description = what + when; all "when to use" info in description, not body; undertriggering → "pushy"; dashboard before/after example || SKILL.md:46 |
| I13 | example | SKILL.md:75-84 anatomy tree (SKILL.md required; scripts/, references/, assets/ with purposes) || SKILL.md:52-61 |
| I14 | limit | SKILL.md:88-93 three loading levels: metadata ~100 words always; body <500 lines when triggered; resources unlimited, scripts run without loading; approximate || SKILL.md:63-66 |
| I15 | limit | SKILL.md:96-98 approaching 500 lines → extra hierarchy with pointers; reference files with when-to-read; >300 lines → TOC || SKILL.md:68-69 |
| I16 | example | SKILL.md:100-109 domain organization: cloud-deploy/ references/aws.md, gcp.md, azure.md; read only the relevant one || SKILL.md:70-78 |
| I17 | safety | SKILL.md:113 no malware/exploit/compromising content; contents must not surprise the user; refuse misleading skills or ones for unauthorized access, exfiltration, malicious activity; roleplay OK || SKILL.md:82 |
| I18 | format | SKILL.md:117 imperative form || SKILL.md:86 |
| I19 | example | SKILL.md:119-127 output-format template example (Report structure, ALWAYS use this exact template) || SKILL.md:87-94 |
| I20 | example | SKILL.md:129-135 examples pattern (Commit message format, Input/Output) || SKILL.md:96-102 |
| I21 | format | SKILL.md:139 explain why instead of heavy-handed MUSTs; theory of mind; general, not narrow to examples; draft then fresh eyes || SKILL.md:104 |
| I22 | order | SKILL.md:143 2-3 realistic test prompts; share with user ("Here are a few test cases...") before running || SKILL.md:108 |
| I23 | path/format | SKILL.md:145-159 save to `evals/evals.json`; prompts only, no assertions yet; JSON example (skill_name, evals[].id/prompt/expected_output/files) || SKILL.md:110-115 |
| I24 | path | SKILL.md:161 full schema in `references/schemas.md` || SKILL.md:117 |
| I25 | safety/order | SKILL.md:165 one continuous sequence, don't stop partway; "Do NOT use `/skill-test` or any other testing skill" || SKILL.md:121 |
| I26 | path | SKILL.md:167 `<skill-name>-workspace/` sibling of skill dir; `iteration-<N>/`; one dir per eval; create as you go || SKILL.md:123 |
| I27 | order | SKILL.md:171 spawn with-skill AND baseline runs in the same turn, not baselines later || SKILL.md:125-127 |
| I28 | format | SKILL.md:175-182 with-skill prompt template (Skill path, Task, Input files, Save outputs to `<workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/`, Outputs to save) || SKILL.md:129-137 |
| I29 | condition/path | SKILL.md:185-186 baseline: new skill → no skill, `without_skill/outputs/`; existing skill → `cp -r <skill-path> <workspace>/skill-snapshot/` before editing, `old_skill/outputs/` || SKILL.md:139-141 |
| I30 | format | SKILL.md:188-197 `eval_metadata.json` per eval (eval_id, eval_name, prompt, assertions[]); descriptive name used for dir too; create for new/modified evals each iteration || SKILL.md:143-147 |
| I31 | order/format | SKILL.md:201-205 draft assertions while runs go; review/explain existing ones; objectively verifiable, descriptive names; subjective → qualitative; update eval_metadata.json and evals/evals.json; explain viewer || SKILL.md:151 |
| I32 | format/order | SKILL.md:209-219 on each completion save `total_tokens`, `duration_ms` (+ total_duration_seconds) to `timing.json` in the run dir immediately; only opportunity, not persisted; process each, don't batch || SKILL.md:155-161 |
| I33 | format | SKILL.md:225 grade via grader subagent or inline with `agents/grader.md`; `grading.json` per run dir; expectations fields exactly `text`, `passed`, `evidence` (not name/met/details); programmatic checks by script || SKILL.md:167 |
| I34 | command | SKILL.md:227-232 from skill-creator dir `python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>`; benchmark.json + .md (pass_rate, time, tokens, mean ± stddev, delta); manual → schemas.md; each with_skill before its baseline || SKILL.md:168-172 |
| I35 | path | SKILL.md:234 analyst pass per `agents/analyzer.md` "Analyzing Benchmark Results": non-discriminating assertions, high variance, time/token tradeoffs || SKILL.md:173 |
| I36 | command | SKILL.md:236-245 `nohup python <skill-creator-path>/eval-viewer/generate_review.py <workspace>/iteration-N --skill-name "my-skill" --benchmark <...>/benchmark.json > /dev/null 2>&1 &`, `VIEWER_PID=$!`; iteration 2+ `--previous-workspace <workspace>/iteration-<N-1>` || SKILL.md:174-183 |
| I37 | condition | SKILL.md:247 no display / no `webbrowser.open()` → `--static <output_path>`; feedback downloads as `feedback.json` on "Submit All Reviews"; copy it into the workspace for the next iteration || SKILL.md:184 |
| I38 | condition | SKILL.md:249 use generate_review.py; no custom HTML || SKILL.md:20 |
| I39 | format | SKILL.md:251 tell the user: results opened, 'Outputs' tab (click through, leave feedback), 'Benchmark' tab, come back when done || SKILL.md:185 |
| I40 | format | SKILL.md:255-265 viewer contents: Prompt, Output, Previous Output (2+), Formal Grades, Feedback (auto-saves), Previous Feedback; Benchmark tab stats + analyst notes; prev/next or arrow keys; Submit All Reviews → feedback.json || SKILL.md:187 |
| I41 | format/condition | SKILL.md:269-282 read `feedback.json` (reviews[].run_id/feedback/timestamp, status); empty = fine; focus on specific complaints || SKILL.md:191-200 |
| I42 | command | SKILL.md:284-288 `kill $VIEWER_PID 2>/dev/null` when done || SKILL.md:200 |
| I43 | format | SKILL.md:298 generalize from feedback; skill used across many prompts; no overfitty changes or oppressive MUSTs; for stubborn issues try different metaphors/patterns || SKILL.md:206 |
| I44 | format | SKILL.md:300 keep the prompt lean; read transcripts, not just outputs; remove parts that cause unproductive work || SKILL.md:207 |
| I45 | format | SKILL.md:302 explain the why, even for terse/frustrated feedback; ALWAYS/NEVER in caps or rigid structure = yellow flag, reframe with reasoning || SKILL.md:208 |
| I46 | format | SKILL.md:304 repeated helper scripts across test cases (e.g. `create_docx.py`) → bundle in `scripts/` and tell skill to use it || SKILL.md:209 |
| I47 | format | SKILL.md:306 take your time; draft revision, then look anew; get into the user's head || SKILL.md:211 |
| I48 | order/condition | SKILL.md:310-321 apply → rerun all into `iteration-<N+1>/` incl. baselines (new skill: always without_skill; existing: original or previous iteration, judgment) → viewer with `--previous-workspace` → wait for user → read feedback, repeat; stop when user happy / feedback all empty / no meaningful progress || SKILL.md:215-221 |
| I49 | condition/path | SKILL.md:327-329 blind comparison for "is the new version actually better?": read `agents/comparator.md`, `agents/analyzer.md`; optional, needs subagents || SKILL.md:227 |
| I50 | order | SKILL.md:335 after creating/improving, offer description optimization || SKILL.md:231 |
| I51 | limit/format | SKILL.md:339-346 20 queries, mix; JSON `[{"query", "should_trigger"}]` || references/description-optimization.md:11-18 |
| I52 | example | SKILL.md:348-352 realistic, concrete, detailed (paths, job context, columns, company names, URLs, backstory, casual/typos, mixed lengths, edge cases); Bad / Good examples || references/description-optimization.md:20-24 |
| I53 | limit | SKILL.md:354 should-trigger 8-10: phrasings, implicit need, uncommon, competing-but-should-win || references/description-optimization.md:26 |
| I54 | limit/condition | SKILL.md:356-358 should-not 8-10: near-misses; not obviously irrelevant (fibonacci for PDF skill too easy) || references/description-optimization.md:28 |
| I55 | path/format | SKILL.md:362-373 `assets/eval_review.html`; replace `__EVAL_DATA_PLACEHOLDER__` (raw JSON, no quotes), `__SKILL_NAME_PLACEHOLDER__`, `__SKILL_DESCRIPTION_PLACEHOLDER__`; write `/tmp/eval_review_<skill-name>.html`, `open` it; user edits, "Export Eval Set"; `~/Downloads/eval_set.json`, most recent (e.g. `eval_set (1).json`); step matters || references/description-optimization.md:30-41 |
| I56 | format | SKILL.md:377 tell user it takes time, runs in background, you'll check periodically || references/description-optimization.md:45 |
| I57 | command | SKILL.md:379-390 save eval set to workspace; background `python -m scripts.run_loop --eval-set ... --skill-path ... --model <model-id-powering-this-session> --max-iterations 5 --verbose`; model ID from system prompt || references/description-optimization.md:47-58 |
| I58 | order | SKILL.md:392 periodically tail output; update user on iteration and scores || references/description-optimization.md:58 |
| I59 | limit | SKILL.md:394 60% train / 40% held-out test; each query 3 times; up to 5 iterations; HTML report; JSON `best_description` chosen by test score || references/description-optimization.md:60 |
| I60 | condition | SKILL.md:398-400 skills consulted only for tasks Claude can't easily do alone; simple one-step queries won't trigger; eval queries must be substantive || references/description-optimization.md:5-7 |
| I61 | order | SKILL.md:404 put `best_description` into frontmatter; show before/after and scores || references/description-optimization.md:64 |
| I62 | condition/command | SKILL.md:408-416 only if `present_files` tool exists: `python -m scripts.package_skill <path/to/skill-folder>`, point user to the `.skill` file || SKILL.md:233-239 |
| I63 | condition | SKILL.md:422-436 Claude.ai: no subagents → run tests yourself one at a time, skip baselines; no browser → show prompt+output inline, save files for download, ask feedback inline; skip benchmarking; loop without viewer; skip description optimization (needs `claude -p`); skip blind comparison; packaging works || SKILL.md:245-250 |
| I64 | safety/condition/path | SKILL.md:438-441 updating: preserve dir name and `name` (`research-helper` → `research-helper.skill`, not `-v2`); copy to writeable location `/tmp/skill-name/`, edit and package from copy; manual packaging: stage in `/tmp/` then copy || SKILL.md:254-257 |
| I65 | condition | SKILL.md:449 Cowork: subagents work; severe timeouts → run test prompts in series || SKILL.md:252 |
| I66 | condition | SKILL.md:450 Cowork: no display → `--static <output_path>`, give the user a link to the HTML || SKILL.md:252 + 184 |
| I67 | order/safety | SKILL.md:451 Cowork AND Claude Code: always generate the eval viewer with `generate_review.py` before evaluating/revising yourself; observed failure, all-caps kept: "GENERATE THE EVAL VIEWER *BEFORE* evaluating inputs yourself" || SKILL.md:20 (all-caps kept) |
| I68 | condition | SKILL.md:452 Cowork: Submit All Reviews downloads `feedback.json`; read it from there (may need to request access) || SKILL.md:184 |
| I69 | condition | SKILL.md:453 Cowork: packaging works || SKILL.md:252 |
| I70 | condition | SKILL.md:454 Cowork: description optimization works (`claude -p` via subprocess) || SKILL.md:252 |
| I71 | condition | SKILL.md:455 Cowork: updating a skill → same update guidance as Claude.ai || SKILL.md:254 (scoped Claude.ai and Cowork) |
| I72 | path | SKILL.md:459-468 reference list: agents/grader.md, comparator.md, analyzer.md (read when spawning that subagent); references/schemas.md || SKILL.md:259-267 |
| I73 | order | SKILL.md:472-481 recap ends with "Package the final skill and return it to the user" || SKILL.md:16 |
| I74 | format | SKILL.md:483 add steps to TodoList; in Cowork the item "Create evals JSON and run `eval-viewer/generate_review.py` so human can review test cases" || SKILL.md:20 |


All 74 rows have a trimmed location. No removals.
