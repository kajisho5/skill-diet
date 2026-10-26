# Invariants ledger: csv-tidy

| ID | Kind | Original (file:line, quote) | Trimmed location |
|---|---|---|---|
| I1 | safety | SKILL.md:18 "NEVER overwrite the input file" (+43, 84) | SKILL.md:10 |
| I2 | path | SKILL.md:18 "ALWAYS write the result to `tidy.csv` in the same folder" (+43) | SKILL.md:10 (+21) |
| I3 | safety/path | SKILL.md:19 "NEVER drop a row that has an empty `order_id`. Instead move it to `rejected.csv`" | SKILL.md:11 |
| I4 | format | SKILL.md:20 "Dates MUST be written as ISO 8601 (YYYY-MM-DD)" (+35) | SKILL.md:12 (now explicitly covers all output files) |
| I5 | limit | SKILL.md:21 "Do not process files larger than 50 MB in one go. Split them into chunks of 100,000 rows" | SKILL.md:13 |
| I6 | condition | SKILL.md:27 "detect the encoding first; ... UTF-8 but can be Shift_JIS (cp932) when exported from Japanese Excel" | SKILL.md:17 |
| I7 | order/condition | encodings.md:3 "Try UTF-8 first (with BOM handling: utf-8-sig), then cp932" | SKILL.md:17 (`utf-8-sig` then `cp932`) |
| I8 | safety | encodings.md:3 "If both fail, stop and ask the user." | SKILL.md:17 |
| I9 | format | SKILL.md:31 "lower snake_case ... `Order ID` becomes `order_id` ... strip whitespace" | SKILL.md:18 |
| I10 | condition | SKILL.md:35 "most exports use DD/MM/YYYY, but before March 2024 the exporter used MM/DD/YYYY" | SKILL.md:19 |
| I11 | condition/path | SKILL.md:35 "If a date cannot be parsed, leave the cell empty and add the row number to `warnings.txt`" | SKILL.md:19 |
| I12 | condition | SKILL.md:39 "A duplicate is a row where every value is the same as another row. Keep the first occurrence." | SKILL.md:20 |
| I13 | condition | SKILL.md:39 "rows with the same `order_id` but different values are NOT duplicates; flag them in `warnings.txt`" | SKILL.md:20 |
| I14 | format | SKILL.md:43 "UTF-8 with a header row. Use a comma as the separator." | SKILL.md:21 |
| I15 | order | SKILL.md:25-41 step order read → headers → dates → dedupe → write | SKILL.md:17-21 (numbered 1-5) |
| I16 | example | SKILL.md:47-63 the only example showing header stripping + rejected.csv | SKILL.md:25-43 |
| I17 | condition | details.md:5 "If the user asks for a summary, report the number of rows read, written, rejected and warned." | SKILL.md:23 |
| I18 | trigger | description: "clean CSV files", "tidy.csv" | SKILL.md:3 description ("Cleans messy CSV files into tidy.csv") |
| I19 | trigger | SKILL.md:14 (body, not seen before triggering) "has a CSV file and wants it cleaned", "mentions CSV", "data is messy" | SKILL.md:3 description ("has a CSV file and wants it cleaned or tidied, mentions CSV data, or says the data is messy") |

All 19 rows have a trimmed location. No removals.
