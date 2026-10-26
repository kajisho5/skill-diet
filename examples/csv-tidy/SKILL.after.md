---
name: csv-tidy
description: Cleans messy CSV files into tidy.csv (normalised headers and dates, exact duplicates removed) without touching the input. Use when the user has a CSV file and wants it cleaned or tidied, mentions CSV data, or says the data is messy.
---

# CSV Tidy

## Rules

- NEVER overwrite the input file. Write the result to `tidy.csv` in the same folder.
- NEVER drop a row with an empty `order_id`; move it to `rejected.csv`.
- Write every date as ISO 8601 (YYYY-MM-DD), in all output files.
- Files over 50 MB: process in chunks of 100,000 rows.

## Steps

1. Read with Python. Detect the encoding: try `utf-8-sig`, then `cp932` (Japanese Excel exports). If both fail, stop and ask the user.
2. Headers: strip whitespace, convert to lower snake_case (`Order ID` → `order_id`).
3. Dates: most exports use DD/MM/YYYY; files exported before March 2024 use MM/DD/YYYY. If a date cannot be parsed, leave the cell empty and add the row number to `warnings.txt`.
4. Duplicates: remove rows identical in every value to an earlier row; keep the first. Rows with the same `order_id` but different values are not duplicates: keep them and flag them in `warnings.txt`.
5. Write `tidy.csv`: UTF-8, header row, comma separator.

If the user asks for a summary, report the number of rows read, written, rejected and warned.

## Example

Input:

```
Order ID, Customer Name ,Date
A1,Rin Example,03/04/2025
A1,Rin Example,03/04/2025
,Sora Sample,05/04/2025
```

`tidy.csv`:

```
order_id,customer_name,date
A1,Rin Example,2025-04-03
```

`rejected.csv` gets the Sora Sample row.
