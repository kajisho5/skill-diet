<!-- Modified from anthropics/skills (skills/skill-creator, commit dbd4588f9e1033efb41dad4bef2f7947c8993d44, Apache-2.0) by skill-diet as a published example. Changes: see examples/skill-creator/README.md. -->

# Description optimization

The description field in SKILL.md frontmatter is the primary mechanism that decides whether Claude invokes a skill.

## How skill triggering works

Skills appear in Claude's `available_skills` list with name + description, and Claude decides from the description whether to consult one. Claude only consults skills for tasks it can't easily handle on its own: simple one-step queries like "read this PDF" may not trigger a skill even with a perfectly matching description. Complex, multi-step or specialized queries reliably trigger when the description matches. So eval queries must be substantive enough that Claude would benefit from a skill; "read file X" is a poor test case.

## Step 1: Generate trigger eval queries

Create 20 eval queries, a mix of should-trigger and should-not-trigger, saved as JSON:

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

Queries must be realistic, something a Claude Code or Claude.ai user would actually type: concrete, specific and detailed (file paths, personal context about the user's job or situation, column names and values, company names, URLs, a little backstory). Some in lowercase, with abbreviations, typos or casual speech. Mix lengths, and focus on edge cases rather than clear-cut ones (the user signs off on them in Step 2).

Bad: `"Format this data"`, `"Extract text from PDF"`, `"Create a chart"`

Good: `"ok so my boss just sent me this xlsx file (its in my downloads, called something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a column that shows the profit margin as a percentage. The revenue is in column C and costs are in column D i think"`

**Should-trigger (8-10)**: different phrasings of the same intent, some formal, some casual; cases where the user doesn't name the skill or file type but clearly needs it; uncommon use cases; cases where this skill competes with another but should win.

**Should-not-trigger (8-10)**: near-misses that share keywords or concepts but need something different: adjacent domains, ambiguous phrasing where a naive keyword match would trigger but shouldn't, cases where another tool is more appropriate. Not obviously irrelevant: "Write a fibonacci function" as a negative for a PDF skill tests nothing.

## Step 2: Review with the user

Bad eval queries lead to bad descriptions, so present the set with the HTML template:

1. Read `assets/eval_review.html`.
2. Replace the placeholders:
   - `__EVAL_DATA_PLACEHOLDER__` → the JSON array of eval items (no quotes around it — it's a JS variable assignment)
   - `__SKILL_NAME_PLACEHOLDER__` → the skill's name
   - `__SKILL_DESCRIPTION_PLACEHOLDER__` → the skill's current description
3. Write it to a temp file (e.g. `/tmp/eval_review_<skill-name>.html`) and open it: `open /tmp/eval_review_<skill-name>.html`
4. The user edits queries, toggles should-trigger, adds/removes entries, then clicks "Export Eval Set".
5. The file downloads to `~/Downloads/eval_set.json`; take the most recent version if there are several (e.g. `eval_set (1).json`).

## Step 3: Run the optimization loop

Tell the user: "This will take some time — I'll run the optimization loop in the background and check on it periodically."

Save the eval set to the workspace, then run in the background (from the skill-creator directory):

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 \
  --verbose
```

Use the model ID from your system prompt (the one powering this session) so the test matches what the user experiences. Periodically tail the output and tell the user which iteration it's on and the scores.

The loop splits the eval set into 60% train and 40% held-out test, evaluates the current description (each query run 3 times for a reliable trigger rate), asks Claude for improvements based on failures, and re-evaluates each new description on train and test, up to 5 iterations. It then opens an HTML report in the browser and returns JSON with `best_description`, selected by test score rather than train score to avoid overfitting.

## Step 4: Apply the result

Put `best_description` from the JSON output into the skill's SKILL.md frontmatter. Show the user before/after and report the scores.
