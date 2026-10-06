---
name: tabular-data-analysis-and-export
description: Use when processing tabular data files, cleaning CSVs, and generating summary JSON reports.
---
1. Read the input dataset and inspect all columns, data types, missing values, and duplicate rows.
2. Remove duplicate rows as required and count how many rows were removed.
3. Handle missing or invalid values (such as sentinel values like `-999` or empty fields) by excluding them from calculations where specified, and track the count of missing records.
4. Normalize and canonicalize text fields (e.g., stripping whitespace, standardizing case for region names).
5. Write the cleaned data to `workspace/clean.csv` with the exact specified header order and one row per distinct valid record, formatting timestamps as `YYYY-MM-DDTHH:MM:SSZ` in UTC, and monetary values in integer cents (e.g., 1606.67 USD written as `160667`).
6. Generate `workspace/answer.json` containing all required summary statistics and a `meta` object with keys `"source"` (input file name), `"rows_in"` (total input rows including duplicates), and `"rows_used"` (number of distinct records with known valid amounts).
7. Validate that all keys, formats, unit types, and file paths match instructions exactly.
