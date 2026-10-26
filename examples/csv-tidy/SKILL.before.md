---
name: csv-tidy
description: I can help you clean CSV files. First read the file, then normalise the headers, then fix the dates, then remove duplicates and finally write tidy.csv.
---

# CSV Tidy

## Introduction

CSV (Comma-Separated Values) is a very common file format that stores tabular data as plain text. Each line is a row and the values are separated by commas. It is important to note that CSV files can come from many different sources such as spreadsheets, databases and exports from web services. Because of this, they are often messy. This skill basically helps you clean them up.

## When to use this skill

Use this skill when the user has a CSV file and wants it cleaned. Use this skill when the user mentions CSV. Use this skill when the user says the data is messy. You should probably use this skill whenever a CSV file is involved, if possible.

## IMPORTANT RULES

- You MUST ALWAYS keep the original file. NEVER overwrite the input file. ALWAYS write the result to `tidy.csv` in the same folder.
- You MUST NEVER drop a row that has an empty `order_id`. Instead move it to `rejected.csv`.
- IMPORTANT: Dates MUST be written as ISO 8601 (YYYY-MM-DD).
- CRITICAL: Do not process files larger than 50 MB in one go. Split them into chunks of 100,000 rows.

## Step-by-step process

### Step 1: Read the file

First of all, you should read the file. In order to read the file, you can use Python. Python is a programming language that is very good at processing data. There are many libraries available, such as pandas, polars, the built-in csv module, duckdb and others. You might want to use pandas, or perhaps the csv module, or maybe polars. Just make sure to detect the encoding first; files are usually UTF-8 but can be Shift_JIS (cp932) when exported from Japanese Excel.

### Step 2: Normalise the headers

Please note that headers should be normalised. This means converting them to lower snake_case. For example `Order ID` becomes `order_id` and `Customer Name` becomes `customer_name`. Make sure to strip whitespace from the headers as well. Keep in mind that the headers should be in lower snake_case.

### Step 3: Fix the dates

Dates should be converted. As mentioned above, dates MUST be written as ISO 8601 (YYYY-MM-DD). Currently, most exports use the format DD/MM/YYYY, but before March 2024 the exporter used MM/DD/YYYY. If a date cannot be parsed, leave the cell empty and add the row number to `warnings.txt`.

### Step 4: Remove duplicates

Duplicates should be removed. A duplicate is a row where every value is the same as another row. Keep the first occurrence. Note that rows with the same `order_id` but different values are NOT duplicates; flag them in `warnings.txt` instead.

### Step 5: Write the output

Write the result to `tidy.csv`. Remember, NEVER overwrite the input file. ALWAYS write to `tidy.csv`. The output must be UTF-8 with a header row. Use a comma as the separator.

## Example

Here is an example. Suppose the input is:

```
Order ID, Customer Name ,Date
A1,Rin Example,03/04/2025
A1,Rin Example,03/04/2025
,Sora Sample,05/04/2025
```

The output `tidy.csv` would be:

```
order_id,customer_name,date
A1,Rin Example,2025-04-03
```

And `rejected.csv` would contain the row for Sora Sample.

## Another example

Here is another example that shows the same thing. Suppose the input is:

```
Order ID,Customer Name,Date
B7,Kai Placeholder,11/12/2025
B7,Kai Placeholder,11/12/2025
```

The output would be:

```
order_id,customer_name,date
B7,Kai Placeholder,2025-12-11
```

## Summary

To summarise: keep the original file, never overwrite it, write to tidy.csv, move rows with empty order_id to rejected.csv, write dates as ISO 8601, remove exact duplicates and keep the first, flag same order_id with different values in warnings.txt, and split files over 50 MB into 100,000-row chunks. Good luck!

For more details see [details.md](details.md).
