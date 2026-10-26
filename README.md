<h1 align="center">skill-diet</h1>

<p align="center"><b>Put your SKILL.md on a diet — without losing what it does.</b><br>
An Agent Skill that audits a skill, trims it, and proves the shorter version still behaves the same.<br>
Python standard library · No API keys · MIT</p>

<p align="center">
  <a href="https://github.com/kajisho5/skill-diet/actions/workflows/ci.yml"><img src="https://github.com/kajisho5/skill-diet/actions/workflows/ci.yml/badge.svg" alt="tests"></a>
  <a href="https://github.com/kajisho5/skill-diet/releases/latest"><img src="https://img.shields.io/github/v/release/kajisho5/skill-diet" alt="release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="MIT"></a>
</p>

<p align="center"><a href="#日本語">日本語はこちら</a></p>

Every installed skill costs context: its description on every turn, its body every time it triggers. Skills grow — intros the model doesn't need, the same rule three times, `MUST` on every line, a "when to use" section nobody reads after triggering. Shortening them by hand is risky: one deleted line can be the rule that mattered.

skill-diet makes trimming a checked process:

1. **Audit** against the [Agent Skills spec](https://agentskills.io/specification), Anthropic's [skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) and the [Claude Code skills docs](https://code.claude.com/docs/en/skills) — ID-numbered findings with file:line evidence.
2. **List what must not be lost** (numbers, paths, commands, formats, conditions, safety rules, trigger words) *before* changing a word.
3. **Trim a copy**, repeating review passes from new angles until three in a row find nothing.
4. **Test**: trigger test (does it still activate?) and behavior test (original vs trimmed on the same tasks, judged blind).
5. **Apply only on request**, after a hash-verified backup, with one-command undo.

## Example

A deliberately bloated sample skill (fictional CSV cleaner), trimmed end to end by an agent running skill-diet:

| | before | after |
|---|---|---|
| body lines | 83 | 40 |
| body tokens (est.) | 932 | 330 |
| `MUST`/`NEVER`/`IMPORTANT` | 13 | 2 (the two safety rules) |
| invariants kept | — | 19 / 19 |
| trigger test (18 queries, one run each) | 12 correct | 17 correct, 0 regressions |

The description got *longer*: the original had no "when to use" in it, so the skill under-triggered.

## Install

**claude.ai / Claude app**: download `skill-diet.skill` from the [latest release](https://github.com/kajisho5/skill-diet/releases/latest) open it in a chat and press *Save skill* (shown when your account or organization allows adding skills).

**Claude Code**:

```bash
git clone https://github.com/kajisho5/skill-diet ~/.claude/skills/skill-diet
```

**Other agents** that read `SKILL.md`: copy the folder into the agent's skills directory.

Then ask: *"audit and slim down my `pdf-report` skill"* or *「このスキル長いから監査して短くして」*.

## What it checks

`scripts/skill_audit.py` measures what can be measured; the agent reads the rest against [`references/checklist.md`](references/checklist.md).

| Group | Examples |
|---|---|
| F frontmatter | `---` on line 1, name rules (lowercase, ≤64, no "claude"/"anthropic", matches folder) |
| D description | ≤1024 chars, third person, says what *and* when, no step-by-step procedure, ≤1,536 chars with `when_to_use` in Claude Code |
| L budget | <500 lines, <~5,000 tokens, hard rules within the first 5,000 tokens (what survives compaction) |
| C cuttable | explanations the model already knows, filler, empty hedges, repeats, recaps, duplicate examples, pep talk |
| E emphasis | `MUST`/`NEVER` density; emphasis kept only where a rule was observed to break |
| R references | broken links, nested references, missing table of contents, files never mentioned |
| P portability | Claude Code-only keys that claude.ai / the Skills API reject |

```bash
python3 scripts/skill_audit.py audit path/to/skill
python3 scripts/skill_audit.py compare original/my-skill trimmed/my-skill
python3 scripts/safe_apply.py apply my-skill-trim path/to/skill        # plan only
python3 scripts/safe_apply.py apply my-skill-trim path/to/skill --yes  # backup + apply
```

## How it compares

Several tools touch part of this. skill-diet's difference is doing audit, invariant ledger, trigger test and behavior test together.

| Tool | Audits | Shortens | Behavior check |
|---|---|---|---|
| Anthropic `/skill-doctor` | context cost and usage | no | — |
| Anthropic plugin-dev `skill-reviewer` | structure, description | no (read-only) | no |
| [claude-world/skills-optimizer](https://github.com/claude-world/skills-optimizer) | — | yes, literals preserved | model reads both texts |
| [FreeAutomation-Tech/skill-optimizer](https://github.com/FreeAutomation-Tech/skill-optimizer) | — | yes, incl. synonym swaps | scored test prompts |
| **skill-diet** | spec + best practices, ID'd | yes, invariants ledger | runs both versions on tasks, blind compare + trigger test |

The backup-before-apply and undo design was inspired by claude-world/skills-optimizer.

## Limits

- Token counts are estimates (ASCII ≈ 4 chars/token, CJK ≈ 1 char/token), good for before/after comparison, not billing.
- Heuristic findings (filler, hedges, duplicates, first person) are candidates; the agent confirms each by reading the line.
- The trigger test uses skill-creator's `run_eval.py` when the `claude` CLI is available; otherwise it is an approximation, and the report says so. On claude.ai chat (no subagents) the behavior test is self-run and weaker, and the report says that too.

---

## 日本語

**skill-diet** は、SKILL.md を監査して、動きを変えずに短くする Agent Skill です。

スキルは入れているだけで場所を取ります。説明文は毎回、本文は呼ばれるたびに読み込まれます。前置き、同じルールの繰り返し、行ごとの `MUST` などで膨らみがちですが、手で削ると大事な1行を消してしまう危険があります。skill-diet はそれを確認つきの手順にします。

1. **監査**：公式仕様・Anthropic のベストプラクティス・Claude Code の資料に照らし、番号つきで指摘します（場所と根拠つき）
2. **消してはいけないものの一覧**：数字・パス・コマンド・出力形式・条件・安全ルール・発動のきっかけになる語を、書き換える前に洗い出します
3. **コピーを短くする**：新しい観点で見直し、3回続けて指摘ゼロになるまで繰り返します
4. **テスト**：ちゃんと呼ばれるかの発動テストと、原本と短縮版に同じ作業をさせて比べる動作テスト（どちらがどちらか伏せて判定）
5. **反映は頼まれたときだけ**：ハッシュ（ファイルの指紋）で確かめたバックアップを取ってから反映し、1コマンドで元に戻せます

**入れ方**
- claude.ai・Claudeアプリ：[最新リリース](https://github.com/kajisho5/skill-diet/releases/latest) から `skill-diet.skill` をダウンロードし、チャットで開いて「Save skill」を押す
- Claude Code：`git clone https://github.com/kajisho5/skill-diet ~/.claude/skills/skill-diet`

**使い方**：「このスキル長いから監査して短くして」と頼むだけです。報告は日本語で返ってきます。

## License

MIT
