---
name: python-bug-fixing-and-maintenance
description: Use when fixing bugs, adding features, and maintaining Python packages with tests and documentation.
---
1. Read all instructions, specifications, and test files thoroughly before modifying or creating any code.
2. Ensure every public function (any name not starting with an underscore `_`) has complete type annotations on all parameters and on the return value.
3. Never modify any original files located in the `tests/` directory; add any new tests in separate, new test files (e.g., `tests/test_regressions.py`).
4. Add at least one regression test function in `tests/test_regressions.py` for each bug fixed (minimum 3 regression test functions total).
5. Record each bug fix in `CHANGELOG.md` under the heading `## Unreleased` as a bullet point in the format `- fix(<function name>): <short description>` (at least 3 bullets).
6. Run the test suite using `pytest` and verify that all tests pass successfully before finishing.
