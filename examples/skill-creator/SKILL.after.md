---
name: skill-creator
description: Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy.
---
<!-- Modified from anthropics/skills (skills/skill-creator, commit dbd4588f9e1033efb41dad4bef2f7947c8993d44, Apache-2.0) by skill-diet as a published example. Changes: see examples/skill-creator/README.md. -->

# Skill Creator

The process:

1. Decide what the skill should do and roughly how.
2. Write a draft.
3. Create a few test prompts and run claude-with-access-to-the-skill on them.
4. Help the user evaluate the results qualitatively and quantitatively: while runs go, draft quantitative evals (or review existing ones) and explain them; show results with `eval-viewer/generate_review.py`, plus the quantitative metrics.
5. Rewrite the skill from the user's feedback (and any glaring flaws in the benchmarks).
6. Repeat until satisfied, then expand the test set and try again at larger scale.
7. Optionally optimize the description, then package the skill and return it to the user.

Figure out where the user is in this process and help them progress. "I want to make a skill for X" → narrow down the intent, draft, write test cases, agree how to evaluate, run, repeat. An existing draft → go straight to eval/iterate. Stay flexible: if the user says "I don't need a bunch of evaluations, just vibe with me", do that. Description optimization comes after the skill is done (order is flexible); in Cowork, wait until the user agrees the skill is in good shape.

Add these steps to your todo list if you have one; in Cowork, include "Create evals JSON and run `eval-viewer/generate_review.py` so human can review test cases". In every environment, after running tests, generate the viewer with `generate_review.py` (no custom HTML) and get results in front of the human *before* evaluating outputs or revising the skill yourself. This step has been skipped in practice, so: GENERATE THE EVAL VIEWER *BEFORE* evaluating inputs yourself.

## Communicating with the user

Users range from people new to terminals to experienced developers; read context cues. By default "evaluation" and "benchmark" are OK; use "JSON" and "assertion" unexplained only with serious cues that the user knows them. When in doubt, add a short definition.

---

## Creating a skill

### Capture intent

Start by understanding the user's intent. If the conversation already contains a workflow to capture ("turn this into a skill"), first extract answers to the questions below from it: tools used, sequence of steps, corrections the user made, input/output formats. The user fills gaps and confirms before you proceed.

1. What should this skill enable Claude to do?
2. When should it trigger (user phrases/contexts)?
3. What's the expected output format?
4. Should we set up test cases? Objectively verifiable outputs (file transforms, data extraction, code generation, fixed workflow steps) benefit; subjective ones (writing style, art) often don't. Suggest a default for the skill type; the user decides.

### Interview and research

Proactively ask about edge cases, input/output formats, example files, success criteria and dependencies. Wait to write test prompts until this is ironed out. Check available MCPs; if useful for research (docs, similar skills, best practices), research in parallel via subagents if available, otherwise inline, so you come prepared.

### Write the SKILL.md

- **name**: skill identifier.
- **description**: the primary triggering mechanism: what the skill does AND specific contexts for when to use it. All "when to use" info goes here, not in the body. Claude tends to undertrigger skills, so make descriptions a little "pushy". Instead of "How to build a simple fast dashboard to display internal Anthropic data.", write "How to build a simple fast dashboard to display internal Anthropic data. Make sure to use this skill whenever the user mentions dashboards, data visualization, internal metrics, or wants to display any kind of company data, even if they don't explicitly ask for a 'dashboard.'"
- **compatibility**: required tools, dependencies (optional, rarely needed).
- the rest of the skill.

#### Anatomy and progressive disclosure

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/    - Executable code for deterministic/repetitive tasks
    ├── references/ - Docs loaded into context as needed
    └── assets/     - Files used in output (templates, icons, fonts)
```

Loading levels (approximate; going longer is fine if needed):
1. Metadata (name + description): always in context (~100 words).
2. SKILL.md body: in context whenever the skill triggers (<500 lines ideal).
3. Bundled resources: as needed (unlimited; scripts can execute without loading).

- Approaching 500 lines → add a layer of hierarchy with clear pointers to where the model should go next.
- Reference files from SKILL.md with guidance on when to read them. Reference files >300 lines get a table of contents.
- Multiple domains/frameworks → organize by variant; Claude reads only the relevant file:
  ```
  cloud-deploy/
  ├── SKILL.md (workflow + selection)
  └── references/
      ├── aws.md
      ├── gcp.md
      └── azure.md
  ```

#### Principle of lack of surprise

Skills must not contain malware, exploit code, or anything that could compromise system security. A skill's contents should not surprise the user in their intent if described. Don't go along with requests for misleading skills or skills meant to facilitate unauthorized access, data exfiltration or other malicious activities. Things like "roleplay as an XYZ" are OK.

#### Writing patterns and style

Use the imperative form. Output formats can be defined with a template:
```markdown
## Report structure
ALWAYS use this exact template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

Examples help (adapt the layout if "Input"/"Output" already appear in them):
```markdown
## Commit message format
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

Explain to the model why things matter instead of heavy-handed MUSTs. Use theory of mind; keep the skill general, not narrow to specific examples. Write a draft, then reread it with fresh eyes and improve it.

### Test cases

After the draft, write 2-3 realistic test prompts, the kind a real user would say. Share them with the user before running (e.g. "Here are a few test cases I'd like to try. Do these look right, or do you want to add more?").

Save them to `evals/evals.json`, prompts only; you'll draft assertions while the runs are in progress:

```json
{"skill_name": "example-skill",
 "evals": [{"id": 1, "prompt": "User's task prompt", "expected_output": "Description of expected result", "files": []}]}
```

Full schema, including the assertions field added later: `references/schemas.md`.

## Running and evaluating test cases

This is one continuous sequence; don't stop partway. Do NOT use `/skill-test` or any other testing skill.

Put results in `<skill-name>-workspace/`, a sibling of the skill directory, organized by iteration (`iteration-1/`, `iteration-2/`, …) and one directory per test case inside. Create directories as you go.

### Step 1: Spawn all runs (with-skill AND baseline) in the same turn

For each test case spawn two subagents in the same turn, one with the skill and one baseline. Don't launch the with-skill runs first and come back for baselines; launch everything at once.

With-skill run:
```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what the user cares about — e.g., "the .docx file", "the final CSV">
```

Baseline run (same prompt):
- Creating a new skill: no skill at all; save to `without_skill/outputs/`.
- Improving an existing skill: the old version. Before editing, snapshot it (`cp -r <skill-path> <workspace>/skill-snapshot/`) and point the baseline at the snapshot; save to `old_skill/outputs/`.

Write an `eval_metadata.json` for each test case (assertions may be empty for now). Give each eval a descriptive name based on what it tests, not just "eval-0", and use it for the directory too. New or modified eval prompts in an iteration need these files in each new eval directory; they don't carry over.

```json
{"eval_id": 0, "eval_name": "descriptive-name-here", "prompt": "The user's task prompt", "assertions": []}
```

### Step 2: While runs are in progress, draft assertions

Draft quantitative assertions for each test case and explain them to the user; if `evals/evals.json` already has assertions, review and explain those. Good assertions are objectively verifiable and have descriptive names that read clearly in the benchmark viewer. Evaluate subjective skills (writing style, design quality) qualitatively; don't force assertions onto things that need human judgment. Update the `eval_metadata.json` files and `evals/evals.json` with the assertions, and explain what the user will see in the viewer: the qualitative outputs and the quantitative benchmark.

### Step 3: As runs complete, capture timing data

Each subagent completion notification contains `total_tokens` and `duration_ms`. Save them immediately to `timing.json` in the run directory:

```json
{"total_tokens": 84852, "duration_ms": 23332, "total_duration_seconds": 23.3}
```

This is the only opportunity: the data is not persisted anywhere else. Process each notification as it arrives instead of batching.

### Step 4: Grade, aggregate, and launch the viewer

Once all runs are done:

1. **Grade each run**: spawn a grader subagent (or grade inline) that reads `agents/grader.md` and evaluates each assertion against the outputs. Save `grading.json` in each run directory. Its expectations array must use the fields `text`, `passed` and `evidence` (not `name`/`met`/`details` or other variants); the viewer depends on these exact names. Check programmatically checkable assertions with a script rather than by eye.
2. **Aggregate**: from the skill-creator directory run
   ```bash
   python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
   ```
   It writes `benchmark.json` and `benchmark.md` (pass_rate, time and tokens per configuration, mean ± stddev, delta). If writing benchmark.json by hand, follow the exact schema in `references/schemas.md`. Put each with_skill version before its baseline counterpart.
3. **Analyst pass**: read the benchmark data and surface patterns the aggregates hide, per `agents/analyzer.md` ("Analyzing Benchmark Results"): assertions that always pass regardless of skill (non-discriminating), high-variance evals (possibly flaky), time/token tradeoffs.
4. **Launch the viewer** with both qualitative outputs and quantitative data:
   ```bash
   nohup python <skill-creator-path>/eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json \
     > /dev/null 2>&1 &
   VIEWER_PID=$!
   ```
   For iteration 2+, also pass `--previous-workspace <workspace>/iteration-<N-1>`.
   No display, or `webbrowser.open()` unavailable (Cowork, headless): use `--static <output_path>` to write a standalone HTML file instead of starting a server, and give the user a link to it. "Submit All Reviews" then downloads `feedback.json`; copy it into the workspace for the next iteration (you may have to request access to read it).
5. **Tell the user**, e.g.: "I've opened the results in your browser. There are two tabs — 'Outputs' lets you click through each test case and leave feedback, 'Benchmark' shows the quantitative comparison. When you're done, come back here and let me know."

The Outputs tab shows one test case at a time: prompt, output files rendered inline, previous output and previous feedback (iteration 2+), formal grades (if graded), and a feedback box that auto-saves. The Benchmark tab shows pass rates, timing and tokens per configuration with per-eval breakdowns and analyst notes. Navigation: prev/next buttons or arrow keys; "Submit All Reviews" saves everything to `feedback.json`.

### Step 5: Read the feedback

When the user says they're done, read `feedback.json`:

```json
{"reviews": [
  {"run_id": "eval-0-with_skill", "feedback": "the chart is missing axis labels", "timestamp": "..."},
  {"run_id": "eval-1-with_skill", "feedback": "", "timestamp": "..."}],
 "status": "complete"}
```

Empty feedback means the user thought it was fine; focus on test cases with specific complaints. Kill the viewer when done: `kill $VIEWER_PID 2>/dev/null`.

---

## Improving the skill

1. **Generalize from the feedback.** The skill will be used across many different prompts; you are iterating on a few examples only for speed. A skill that works only for those examples is useless. Avoid fiddly overfitted changes and oppressively constrictive MUSTs; for a stubborn issue, try different metaphors or recommend different patterns of working.
2. **Keep the prompt lean.** Remove what isn't pulling its weight. Read the transcripts, not just the final outputs: if the skill makes the model waste time on unproductive work, remove the parts causing it and see what happens.
3. **Explain the why.** Even when feedback is terse or frustrated, understand the task and why the user wrote what they wrote, and put that understanding into the instructions. ALWAYS/NEVER in caps or rigid structures are a yellow flag: reframe and explain the reasoning instead.
4. **Bundle repeated work.** If the test-run transcripts show subagents independently writing similar helper scripts (e.g. every run wrote a `create_docx.py` or `build_chart.py`) or taking the same multi-step approach, write that script once in `scripts/` and tell the skill to use it.

Take your time: write a draft revision, then look at it anew and improve it, from inside the user's head.

### The iteration loop

1. Apply your improvements to the skill.
2. Rerun all test cases into a new `iteration-<N+1>/` directory, including baselines. New skill: the baseline is always `without_skill`. Existing skill: use judgment between the original version the user came in with and the previous iteration.
3. Launch the reviewer with `--previous-workspace` pointing at the previous iteration.
4. Wait for the user to review and tell you they're done.
5. Read the new feedback, improve again, repeat.

Stop when the user is happy, the feedback is all empty, or you're no longer making meaningful progress.

---

## Advanced: blind comparison

For a more rigorous comparison of two versions (e.g. "is the new version actually better?"), give two outputs to an independent agent without saying which is which, let it judge, then analyze why the winner won. Read `agents/comparator.md` and `agents/analyzer.md`. Optional, needs subagents; the human review loop is usually enough.

## Description optimization

After creating or improving a skill, offer to optimize its description for triggering accuracy. When the user accepts, read `references/description-optimization.md` and follow it (trigger eval queries, review template, `scripts.run_loop`, applying `best_description`).

## Package and present (only if the `present_files` tool is available)

If you have `present_files`, package the skill and point the user to the resulting `.skill` file so they can install it:

```bash
python -m scripts.package_skill <path/to/skill-folder>
```

---

## Environment differences

**Claude.ai** (no subagents): the core loop is the same (draft → test → review → improve → repeat), with these changes:
- Run test cases yourself, one at a time: read the skill's SKILL.md and follow it for each prompt. Skip baseline runs. Less rigorous, since you wrote the skill, but the human review compensates.
- If you can't open a browser (no display, remote server), skip the browser reviewer: show each prompt and output in the conversation, save files the user must inspect (e.g. .docx, .xlsx) and tell them where, and ask for feedback inline ("How does this look? Anything you'd change?").
- Skip quantitative benchmarking (baselines aren't meaningful without subagents) and blind comparison. Iteration directories are still fine if you have a filesystem.
- Skip description optimization: it needs the `claude` CLI (`claude -p`), only in Claude Code.
- Packaging works anywhere with Python and a filesystem; the user downloads the `.skill` file.

**Cowork**: subagents work, so the full workflow runs (if timeouts are severe, run test prompts in series). There is no display: use the `--static` viewer as in Step 4. Packaging works. Description optimization works (`run_loop.py` / `run_eval.py` call `claude -p` via subprocess).

**Updating an existing skill** (Claude.ai and Cowork):
- Preserve the original name: keep the directory name and `name` field unchanged. E.g. installed `research-helper` → output `research-helper.skill`, not `research-helper-v2`.
- The installed path may be read-only: copy to a writeable location such as `/tmp/skill-name/`, edit there, and package from the copy.
- If packaging manually, stage in `/tmp/` first, then copy to the output directory; direct writes may fail due to permissions.

## Reference files

Read an agents/ file when you spawn that subagent:
- `agents/grader.md`: evaluate assertions against outputs.
- `agents/comparator.md`: blind A/B comparison of two outputs.
- `agents/analyzer.md`: why one version beat another; benchmark analysis.

- `references/schemas.md`: JSON structures for evals.json, grading.json, benchmark.json, etc.
- `references/description-optimization.md`: description optimization workflow.
