# Blind comparisons

A comparator agent (skill-creator's `agents/comparator.md`, Read/Write/Glob/Grep only) saw two outputs labeled A and B and did not know which skill produced which. The key was opened only afterwards.

| Round | Task | A | B | Winner |
|---|---|---|---|---|
| 1 | t1 create a skill | original r1 | trimmed r1 | A: original |
| 1 | t2 grade, aggregate, present | trimmed r1 | original r1 | B: original |
| 1 | t3 trigger eval set | original r1 | trimmed r1 | B: trimmed |
| noise | t1 | original r1 | original r2 | A: original r1 |
| noise | t2 | original r1 | original r2 | A: original r1 |
| 2 | t1 | original r2 | trimmed r1 | A: original r2 |
| 2 | t2 | trimmed r1 | original r2 | A: trimmed r1 |
| 3 | t1 | original r2 | trimmed r2 | B: trimmed r2 |

Reading: the original loses to itself on both tasks where it beat the trimmed copy, and the trimmed copy wins later pairs on both. No task shows a consistent winner, so the round-1 losses are counted as run-to-run variation, not regressions.
