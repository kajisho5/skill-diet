# Audit checklist

## Contents
- Sources
- F: Frontmatter validity
- D: Description (triggering)
- L: Length and loading budget
- C: Cuttable content
- E: Emphasis and guidance form
- S: Structure and workflow
- R: References and bundled files
- X: Scripts
- P: Portability
- Keep list (never cut)

`(auto)` = `scripts/skill_audit.py` measures it; confirm heuristic hits by reading the line.

## Sources

| Tag | Source |
|---|---|
| SPEC | Agent Skills specification — https://agentskills.io/specification |
| BP | Anthropic, Skill authoring best practices — https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices |
| CC | Claude Code skills docs — https://code.claude.com/docs/en/skills |
| SC | Anthropic `skill-creator` skill |
| WS | `writing-skills` skill (obra/superpowers), community guidance |

When sources disagree, SPEC > BP > CC > SC > WS, except where a lower source reports a tested failure the higher one does not address.

## F: Frontmatter validity

| ID | Check | Source | Fix |
|---|---|---|---|
| F1 | `---` on line 1, closing `---`, parseable YAML (auto) | CC | Invalid YAML in Claude Code loads the skill with no fields set. |
| F2 | No unknown keys (auto) | CC | Unknown keys are ignored silently in Claude Code, hard errors elsewhere. |
| F3 | `name`: 1–64 chars, `a-z 0-9 -`, no leading/trailing/double hyphen, no "anthropic"/"claude", no XML (auto) | SPEC, BP | Report only. Renaming breaks `/name` and cross-references; ask the user. |
| F4 | `name` matches folder name (auto) | SPEC | Report only. |
| F5 | `compatibility` ≤ 500 chars, only if real requirements (auto) | SPEC | Delete if it states nothing an agent needs. |

## D: Description (triggering)

The description is in context on every turn for every installed skill; the body is not seen until the skill triggers.

| ID | Check | Source | Fix |
|---|---|---|---|
| D1 | 1–1024 chars, no `<` `>` (auto) | SPEC, BP | |
| D2 | `description` + `when_to_use` ≤ 1,536 chars; key use case first (auto) | CC | Claude Code cuts the listing at 1,536. |
| D3 | Third person (auto, heuristic) | BP | "Processes X…", not "I can…" / "You can…". |
| D4 | States what it does AND when to use it, with concrete trigger words (file types, phrases, symptoms) (auto, heuristic) | SPEC, BP, CC | Missing triggers cause undertriggering. |
| D5 | No step-by-step procedure (auto, heuristic) | WS | A tested failure: agents followed a procedure summary in the description and skipped the body. "What" = capability, not steps. |
| D6 | Body "When to use" sections that repeat the description | SC | The body is read only after triggering. Cut trigger lists from the body; keep a short "do not use for X" only if it makes the agent hand off mid-task. |
| D7 | Near-miss coverage: if a neighbouring skill competes, the description says which side of the line this skill takes | SC | Add one clause. |
| D8 | Shortening the description never removes a trigger keyword without a trigger test | SC | See regression-test.md §2. |

## L: Length and loading budget

| ID | Check | Source | Fix |
|---|---|---|---|
| L1 | Body < 500 lines (auto) | SPEC, BP, CC | Move detail to `references/`. |
| L2 | Body < ~5,000 tokens (auto, estimate) | SPEC | Same. |
| L3 | Critical rules sit in the first 5,000 tokens (auto) | CC | After compaction Claude Code re-attaches only the first 5,000 tokens of each skill (25,000 shared). Move hard constraints up. |
| L4 | Always-loaded or very frequent skills are far below the limits | WS | WS suggests < 200 words for frequently loaded skills; treat as a target, not a rule. |

## C: Cuttable content

Cut test for every sentence: "If this is gone, would a capable model do anything differently?" No → cut. Unsure → keep and list as a candidate.

| ID | Check | Source | Fix |
|---|---|---|---|
| C1 | Explains what the model already knows (what a PDF is, how pip works, generic best practice) | BP | Delete. |
| C2 | Filler phrases ("please note", "make sure to", "in order to", "なお、") (auto) | — | Delete the phrase, keep the instruction. |
| C3 | Hedges with no real condition ("if possible", "as needed", "適宜") (auto) | WS | Replace with the actual condition, or delete. |
| C4 | Repeated lines (auto) | WS | Keep the copy in the most specific place. |
| C5 | Same rule stated in several places, incl. closing recaps ("repeating the core loop…") (auto, partial) | WS | Keep one statement where it is acted on. |
| C6 | Time-sensitive wording ("currently", "before Aug 2025") (auto) | BP | If the date describes the skill's own guidance going stale, state the current method and move the old one to an "old patterns" note or delete it. If the date is a condition the agent applies to data ("files exported before March 2024 use MM/DD"), it is an invariant: keep it. |
| C7 | Several examples of the same pattern | WS, BP | Keep the one best example. Keep all examples only when output style depends on seeing variety. |
| C8 | Many alternative tools/approaches with no default | BP | One default + one escape hatch. |
| C9 | Narrative or history ("in session X we found…") | WS | Keep the resulting rule, drop the story. |
| C10 | "Why" paragraphs | CC, SC | Keep a reason only if it decides edge cases (one clause). Drop explanation that changes nothing. |
| C11 | Full flag/option lists for a CLI the agent can query | WS | Point to `--help`. |
| C12 | Content needed only for some tasks sits in the body | SPEC, BP | Move to `references/<topic>.md` with "read when …". |
| C13 | Restates another skill's instructions | WS | Name the skill instead. |
| C14 | Pep talk, chatter, sign-offs ("Cool? Cool.", "Good luck!") | — | Delete. |
| C15 | Formatting overhead: a heading per two lines, tables for 2 items, decorative bold | — | Flatten. |
| C16 | Prose describing a deterministic algorithm | BP | Replace with a bundled script; scripts run without loading into context. |

## E: Emphasis and guidance form

| ID | Check | Source | Fix |
|---|---|---|---|
| E1 | Emphasis density (MUST/NEVER/ALWAYS/IMPORTANT, all caps, bold) (auto, heuristic) | SC, BP | Plain imperative by default. |
| E2 | Each remaining emphasis guards a rule that was observed to be broken, a fragile operation, or safety | BP, SC | Such emphasis is an invariant: keep it. Remove the rest. |
| E3 | Form matches the failure: discipline lapses → explicit prohibition + rationalization counters; wrong output shape → positive recipe/template; omitted element → required slot in the template; condition-dependent → conditional on an observable predicate | WS | Rewrite, do not just delete. |
| E4 | Nuance clauses that reopen a rule ("don't X unless it matters") | WS | Turn the exception into its own conditional. |
| E5 | Degree of freedom matches fragility: exact commands for fragile steps, heuristics for open tasks | BP | |

## S: Structure and workflow

| ID | Check | Source | Fix |
|---|---|---|---|
| S1 | Multi-step work is a numbered list, complex work has a copyable checklist | BP | |
| S2 | Quality-critical work has a validate → fix → repeat loop | BP | |
| S3 | One term per concept throughout | BP | |
| S4 | Order follows execution order; nothing needed early is buried late | — | |

## R: References and bundled files

| ID | Check | Source | Fix |
|---|---|---|---|
| R1 | Every link resolves inside the skill folder (auto) | SPEC | |
| R2 | References one level deep from SKILL.md (auto) | SPEC, BP | Agents may only partially read nested files. |
| R3 | Reference files > 100 lines start with a table of contents (auto) | BP | |
| R4 | Forward slashes only (auto) | BP | |
| R5 | Every bundled file is mentioned in SKILL.md with when to read/run it (auto) | BP | Unmentioned files are never used: mention or delete. Exempt: modules imported by another script (the script reports them as imported). |
| R6 | Clear intent: "Run X" vs "Read X" | BP | |
| R7 | Descriptive file names | BP | |

## X: Scripts

| ID | Check | Source | Fix |
|---|---|---|---|
| X1 | Scripts handle errors instead of punting to the agent | BP | |
| X2 | No unexplained constants | BP | |
| X3 | Dependencies stated and available on the target surface | BP | Skills API has no network or package install. |

## P: Portability

| ID | Check | Source | Fix |
|---|---|---|---|
| P1 | Claude Code-only keys (`when_to_use`, `context`, `paths`, …) only if the skill is Claude Code-only (auto) | CC | claude.ai and the Skills API reject them. |
| P2 | Exactly one SKILL.md (auto) | SC | |
| P3 | MCP tools named `Server:tool` | BP | |

## Keep list (never cut)

These are invariants. Moving them is allowed; losing them is a regression.

- Numbers, limits, versions, thresholds
- Paths, file names, commands, flags actually used
- Output formats, templates, required fields
- Conditions, edge cases, ordering constraints ("before X", "only after Y")
- Safety, permission and confirmation rules
- Trigger keywords in the description
- Rationalization tables and red-flag lists in discipline skills (they come from observed failures)
- The only example of a format
