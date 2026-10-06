---
name: log-parsing-and-triage
description: Use when parsing application logs, filtering error levels, aggregating metrics, and exporting JSON reports.
---
1. Read the log file and parse entries matching the expected log format (timestamp, log level, service name, message, and optional multiline exception traces).
2. Handle repetition lines (e.g., `-- last message repeated N times --`) by calculating `repeat_count = 1 + N`.
3. Filter entries to retain only error-level logs (`ERROR` and `CRITICAL`) regardless of original case.
4. Normalize service names to lower-case and replace hyphens with underscores (e.g., `payment-service` becomes `payment_service`).
5. Sort the resulting error entries strictly by service name, then by `timestamp_utc` ascending.
6. Write the output to `workspace/errors.json` with the top-level object containing `"schema_version": 2`, `"generated_by": "log-triage"`, the sorted array of error objects, and `"counts_by_service"` aggregated with service-name normalization.
7. Verify the output JSON structure against all schema and sorting rules before completion.
