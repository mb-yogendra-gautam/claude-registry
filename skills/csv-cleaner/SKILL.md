---
name: csv-cleaner
description: Use when the user has a messy CSV and wants it cleaned — duplicate headers, mixed types, stray whitespace, inconsistent date formats.
---

# CSV Cleaner

## Workflow

1. Read the first 50 rows to detect: delimiter, header presence, encoding.
2. Normalize column names to snake_case.
3. Trim whitespace, standardize null markers ("N/A", "-", "" → NaN).
4. Infer column types and flag any row that doesn't conform.
5. Write the cleaned CSV with a `_cleaning_report.md` describing what changed.
