### Human
The test suite of the `bookings` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Tool call: ls
{"path": "workspace"}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/', '/workspace/tests/']

### Tool call: read_file
{"file_path": "/skills/python-bug-fixing-and-maintenance/SKILL.md", "limit": 1000}

### Tool result
@@ lines 1-10 of 10 @@
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

### Tool call: execute
{"command": "pytest workspace/tests"}

### Tool result
============================= test session starts ==============================
platform linux -- Python 3.12.15, pytest-9.1.1, pluggy-1.6.0
rootdir: /tmp/lab-code-eval-t2zf9tce
plugins: langsmith-0.14.4, anyio-4.15.1
collected 0 items / 1 error

==================================== ERRORS ====================================
______________ ERROR collecting workspace/tests/test_bookings.py _______________
ImportError while importing test module '/tmp/lab-code-eval-t2zf9tce/workspace/tests/test_bookings.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/local/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
workspace/tests/test_bookings.py:1: in <module>
    from bookings.billing import billable_blocks
E   ModuleNotFoundError: No module named 'bookings'
=========================== short test summary info ============================
ERROR workspace/tests/test_bookings.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 0.16s ===============================

Exit code: 2
[Command failed with exit code 2]

### Tool call: execute
{"command": "PYTHONPATH=workspace pytest workspace/tests"}

### Tool result
============================= test session starts ==============================
platform linux -- Python 3.12.15, pytest-9.1.1, pluggy-1.6.0
rootdir: /tmp/lab-code-eval-t2zf9tce
plugins: langsmith-0.14.4, anyio-4.15.1
collected 3 items

workspace/tests/test_bookings.py FF.                                     [100%]

=================================== FAILURES ===================================
_______________________ test_total_minutes_mixed_formats _______________________

    def test_total_minutes_mixed_formats():
>       assert total_minutes(["1h30m", "2h"]) == 210
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

workspace/tests/test_bookings.py:6: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
workspace/bookings/schedule.py:7: in total_minutes
    return sum(parse_duration(d) for d in durations)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
workspace/bookings/schedule.py:7: in <genexpr>
    return sum(parse_duration(d) for d in durations)
               ^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

text = '2h'

    def parse_duration(text):
        """Convert a duration string to whole minutes (int).
    
        Supported formats:
          "1h30m" -> 90
          "2h"    -> 120
          "45m"   -> 45
          "1:30"  -> 90
          "45"    -> 45    # a bare number means minutes
        Surrounding whitespace is ignored.
        """
        m = re.fullmatch(r"(\d+)h(\d+)m

### Tool call: glob
{"path": "workspace", "pattern": "**/*"}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/__init__.py', '/workspace/bookings/billing.py', '/workspace/bookings/calendar_export.py', '/workspace/bookings/schedule.py', '/workspace/bookings/timeutil.py', '/workspace/tests/test_bookings.py']

### Tool call: read_file
{"limit": 1000, "file_path": "/workspace/README.md"}

### Tool result
@@ lines 1-5 of 5 @@
# bookings

Small package. Run the tests from the `workspace/` folder:

    cd workspace && python -m pytest tests -q

### Tool call: read_file
{"file_path": "/workspace/CHANGELOG.md", "limit": 1000}

### Tool result
@@ lines 1-6 of 6 @@
# Changelog

## Unreleased

## 1.4.2
- initial import

### Tool call: read_file
{"file_path": "/workspace/tests/test_bookings.py", "limit": 1000}

### Tool result
@@ lines 1-15 of 15 @@
from bookings.billing import billable_blocks
from bookings.schedule import add_slot, total_minutes


def test_total_minutes_mixed_formats():
    assert total_minutes(["1h30m", "2h"]) == 210


def test_billable_blocks_rounds_up():
    assert billable_blocks(20) == 2
    assert billable_blocks(45) == 3


def test_add_slot_single_call():
    assert add_slot("a") == ["a"]

### Tool call: read_file
{"file_path": "/workspace/bookings/__init__.py", "limit": 1000}

### Tool result
@@ lines 1-1 of 1 @@
__version__ = "1.4.2"

### Tool call: read_file
{"limit": 1000, "file_path": "/workspace/bookings/billing.py"}

### Tool result
@@ lines 1-11 of 11 @@
"""Billing rules."""


def billable_blocks(minutes, block=15):
    """Number of billable blocks for a booking.

    A partial block is billed as a full block (always round UP):
    16 minutes with 15-minute blocks -> 2 blocks.
    `minutes` must be >= 0; a negative value raises ValueError.
    """
    return round(minutes / block)

### Tool call: read_file
{"file_path": "/workspace/bookings/timeutil.py", "limit": 1000}

### Tool result
@@ lines 1-19 of 19 @@
"""Time helpers for the bookings package."""
import re


def parse_duration(text):
    """Convert a duration string to whole minutes (int).

    Supported formats:
      "1h30m" -> 90
      "2h"    -> 120
      "45m"   -> 45
      "1:30"  -> 90
      "45"    -> 45    # a bare number means minutes
    Surrounding whitespace is ignored.
    """
    m = re.fullmatch(r"(\d+)h(\d+)m", text.strip())
    if not m:
        raise ValueError(f"bad duration: {text!r}")
    return int(m.group(1)) * 60 + int(m.group(2))

### Tool call: read_file
{"file_path": "/workspace/bookings/schedule.py", "limit": 1000}

### Tool result
@@ lines 1-17 of 17 @@
"""Schedule helpers."""
from .timeutil import parse_duration


def total_minutes(durations):
    """Total minutes of a list of duration strings."""
    return sum(parse_duration(d) for d in durations)


def add_slot(slot, slots=[]):
    """Return a NEW list containing the given slots plus `slot`.

    Separate calls must not share state: calling add_slot("a") and then
    add_slot("b") returns ["a"] and then ["b"].
    """
    slots.append(slot)
    return slots

### Tool call: read_file
{"limit": 1000, "file_path": "/workspace/bookings/calendar_export.py"}

### Tool result
@@ lines 1-7 of 7 @@
"""Calendar export."""
from .timeutil import parse_duration


def slot_end(start_minute, duration_text):
    """Minute of the day at which a slot ends."""
    return start_minute + parse_duration(duration_text)

### Tool call: execute
{"command": "python3 -c \"import ast, pathlib; print('\\n'.join(f'{f}: {ast.dump(ast.parse(pathlib.Path(f).read_text()))}' for f in pathlib.Path('workspace/bookings').glob('*.py')))\""}

### Tool result
workspace/bookings/__init__.py: Module(body=[Assign(targets=[Name(id='__version__', ctx=Store())], value=Constant(value='1.4.2'))], type_ignores=[])
workspace/bookings/calendar_export.py: Module(body=[Expr(value=Constant(value='Calendar export.')), ImportFrom(module='timeutil', names=[alias(name='parse_duration')], level=1), FunctionDef(name='slot_end', args=arguments(posonlyargs=[], args=[arg(arg='start_minute'), arg(arg='duration_text')], kwonlyargs=[], kw_defaults=[], defaults=[]), body=[Expr(value=Constant(value='Minute of the day at which a slot ends.')), Return(value=BinOp(left=Name(id='start_minute', ctx=Load()), op=Add(), right=Call(func=Name(id='parse_duration', ctx=Load()), args=[Name(id='duration_text', ctx=Load())], keywords=[])))], decorator_list=[], type_params=[])], type_ignores=[])
workspace/bookings/timeutil.py: Module(body=[Expr(value=Constant(value='Time helpers for the bookings package.')), Import(names=[alias(name='re')]), FunctionDef(name='parse_duration', args=arguments(posonlyargs=[], args=[arg(arg='text')], kwonlyargs=[], kw_defaults=[], defaults=[]), body=[Expr(value=Constant(value='Convert a duration string to whole minutes (int).\n\n    Supported formats:\n      "1h30m" -> 90\n      "2h"    -> 120\n      "45m"   -> 45\n      "1:30"  -> 90\n      "45"    -> 45    # a bare number means minutes\n    Surrounding whitespace is ignored.\n    ')), Assign(targets=[Name(id='m', ctx=Store())], value=Call(func=Attribute(value=Name(id='re', ctx=Load()), attr='

### Tool call: read_file
{"limit": 1000, "file_path": "/skills/python-bug-fixing-and-maintenance/SKILL.md"}

### Tool result
@@ lines 1-10 of 10 @@
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

### Tool call: read_file
{"limit": 1000, "file_path": "/workspace/CHANGELOG.md"}

### Tool result
@@ lines 1-6 of 6 @@
# Changelog

## Unreleased

## 1.4.2
- initial import

### Tool call: write_file
{"content": "import math\nfrom bookings.billing import billable_blocks\nfrom bookings.schedule import add_slot, total_minutes\nfrom bookings.timeutil import parse_duration\n\n\ndef test_regression_parse_duration_all_formats():\n    assert parse_duration(\"1h30m\") == 90\n    assert parse_duration(\"2h\") == 120\n    assert parse_duration(\"45m\") == 45\n    assert parse_duration(\"1:30\") == 90\n    assert parse_duration(\"45\") == 45\n    assert parse_duration(\"  2h  \") == 120\n\n\ndef test_regression_billable_blocks_rounding():\n    assert billable_blocks(0) == 0\n    assert billable_blocks(1) == 1\n    assert billable_blocks(15) == 1\n    assert billable_blocks(16) == 2\n    assert billable_blocks(30) == 2\n\n\ndef test_regression_add_slot_state():\n    res1 = add_slot(\"a\")\n    assert res1 == [\"a\"]\n    res2 = add_slot(\"b\")\n    assert res2 == [\"b\"]\n    assert res1 is not res2\n", "file_path": "workspace/tests/test_regressions.py"}

### Tool result
Updated file /workspace/tests/test_regressions.py

### Tool call: edit_file
{"old_string": "\"\"\"Time helpers for the bookings package.\"\"\"\nimport re\n\n\ndef parse_duration(text):\n    \"\"\"Convert a duration string to whole minutes (int).\n\n    Supported formats:\n      \"1h30m\" -> 90\n      \"2h\"    -> 120\n      \"45m\"   -> 45\n      \"1:30\"  -> 90\n      \"45\"    -> 45    # a bare number means minutes\n    Surrounding whitespace is ignored.\n    \"\"\"\n    m = re.fullmatch(r\"(\\d+)h(\\d+)m\", text.strip())\n    if not m:\n        raise ValueError(f\"bad duration: {text!r}\")\n    return int(m.group(1)) * 60 + int(m.group(2))", "new_string": "\"\"\"Time helpers for the bookings package.\"\"\"\nimport re\n\n\ndef parse_duration(text: str) -> int:\n    \"\"\"Convert a duration string to whole minutes (int).\n\n    Supported formats:\n      \"1h30m\" -> 90\n      \"2h\"    -> 120\n      \"45m\"   -> 45\n      \"1:30\"  -> 90\n      \"45\"    -> 45    # a bare number means minutes\n    Surrounding whitespace is ignored.\n    \"\"\"\n    cleaned = text.strip()\n    # Check \"1h30m\"\n    m = re.fullmatch(r\"(\\d+)h(\\d+)m\", cleaned)\n    if m:\n        return int(m.group(1)) * 60 + int(m.group(2))\n    \n    # Check \"2h\"\n    m = re.fullmatch(r\"(\\d+)h\", cleaned)\n    if m:\n        return int(m.group(1)) * 60\n\n    # Check \"45m\"\n    m = re.fullmatch(r\"(\\d+)m\", cleaned)\n    if m:\n        return int(m.group(1))\n\n    # Check \"1:30\"\n    m = re.fullmatch(r\"(\\d+):(\\d+)\", cleaned)\n    if m:\n        return int(m.group(1)

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/timeutil.py'

### Tool call: edit_file
{"old_string": "\"\"\"Billing rules.\"\"\"\n\n\ndef billable_blocks(minutes, block=15):\n    \"\"\"Number of billable blocks for a booking.\n\n    A partial block is billed as a full block (always round UP):\n    16 minutes with 15-minute blocks -> 2 blocks.\n    `minutes` must be >= 0; a negative value raises ValueError.\n    \"\"\"\n    return round(minutes / block)", "new_string": "\"\"\"Billing rules.\"\"\"\nimport math\n\n\ndef billable_blocks(minutes: int, block: int = 15) -> int:\n    \"\"\"Number of billable blocks for a booking.\n\n    A partial block is billed as a full block (always round UP):\n    16 minutes with 15-minute blocks -> 2 blocks.\n    `minutes` must be >= 0; a negative value raises ValueError.\n    \"\"\"\n    if minutes < 0:\n        raise ValueError(\"minutes must be >= 0\")\n    return math.ceil(minutes / block)", "file_path": "workspace/bookings/billing.py"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/billing.py'

### Tool call: edit_file
{"file_path": "workspace/bookings/schedule.py", "new_string": "\"\"\"Schedule helpers.\"\"\"\nfrom typing import List, Sequence\nfrom .timeutil import parse_duration\n\n\ndef total_minutes(durations: Sequence[str]) -> int:\n    \"\"\"Total minutes of a list of duration strings.\"\"\"\n    return sum(parse_duration(d) for d in durations)\n\n\ndef add_slot(slot: str, slots: List[str] = None) -> List[str]:\n    \"\"\"Return a NEW list containing the given slots plus `slot`.\n\n    Separate calls must not share state: calling add_slot(\"a\") and then\n    add_slot(\"b\") returns [\"a\"] and then [\"b\"].\n    \"\"\"\n    if slots is None:\n        slots = []\n    return list(slots) + [slot]", "old_string": "\"\"\"Schedule helpers.\"\"\"\nfrom .timeutil import parse_duration\n\n\ndef total_minutes(durations):\n    \"\"\"Total minutes of a list of duration strings.\"\"\"\n    return sum(parse_duration(d) for d in durations)\n\n\ndef add_slot(slot, slots=[]):\n    \"\"\"Return a NEW list containing the given slots plus `slot`.\n\n    Separate calls must not share state: calling add_slot(\"a\") and then\n    add_slot(\"b\") returns [\"a\"] and then [\"b\"].\n    \"\"\"\n    slots.append(slot)\n    return slots"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/schedule.py'

### Tool call: edit_file
{"old_string": "\"\"\"Calendar export.\"\"\"\nfrom .timeutil import parse_duration\n\n\ndef slot_end(start_minute, duration_text):\n    \"\"\"Minute of the day at which a slot ends.\"\"\"\n    return start_minute + parse_duration(duration_text)", "file_path": "workspace/bookings/calendar_export.py", "new_string": "\"\"\"Calendar export.\"\"\"\nfrom .timeutil import parse_duration\n\n\ndef slot_end(start_minute: int, duration_text: str) -> int:\n    \"\"\"Minute of the day at which a slot ends.\"\"\"\n    return start_minute + parse_duration(duration_text)"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/calendar_export.py'

### Tool call: edit_file
{"new_string": "# Changelog\n\n## Unreleased\n- fix(parse_duration): support all documented duration formats including hours, minutes, colon notation, and bare numbers\n- fix(billable_blocks): correctly round up partial blocks using math.ceil and validate non-negative minutes\n- fix(add_slot): avoid mutable default argument state sharing and ensure a new list is always returned\n\n## 1.4.2\n- initial import", "file_path": "workspace/CHANGELOG.md", "old_string": "# Changelog\n\n## Unreleased\n\n## 1.4.2\n- initial import"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/CHANGELOG.md'

### Tool call: execute
{"command": "PYTHONPATH=workspace pytest workspace/tests"}

### Tool result
============================= test session starts ==============================
platform linux -- Python 3.12.15, pytest-9.1.1, pluggy-1.6.0
rootdir: /tmp/lab-code-eval-t2zf9tce
plugins: langsmith-0.14.4, anyio-4.15.1
collected 6 items

workspace/tests/test_bookings.py ...                                     [ 50%]
workspace/tests/test_regressions.py ...                                  [100%]

============================== 6 passed in 0.03s ===============================

[Command succeeded with exit code 0]

### Tool call: execute
{"command": "PYTHONPATH=workspace python3 -m py_compile workspace/bookings/*.py workspace/tests/*.py"}

### Tool result
<no output>
[Command succeeded with exit code 0]

### Tool call: execute
{"command": "git status"}

### Tool result
[stderr] fatal: not a git repository (or any of the parent directories): .git

Exit code: 128
[Command failed with exit code 128]

### Assistant
[{'type': 'text', 'text': 'When you are done, reply with a short summary of that mentions only files you really created or changed.\n\nSummary of changes:\n- **`workspace/bookings/timeutil.py`**: Updated `parse_duration` to support all documented formats (`1h30m`, `2h`, `45m`, `1:30`, and bare numbers like `45`) and whitespace stripping.\n- **`workspace/bookings/billing.py`**: Updated `billable_blocks` to use `math.ceil` for rounding up partial blocks and added validation to raise a `ValueError` for negative minutes.\n- **`workspace/bookings/schedule.py`**: Fixed `add_slot` to avoid mutable default argument state sharing across calls and ensure a new list is returned.\n- **`workspace/bookings/calendar_export.py`**: Added complete type annotations to `slot_end`.\n- **`workspace/tests/test_regressions.py`**: Created new regression tests covering all bug fixes and duration formats.\n- **`workspace/CHANGELOG.md`**: Recorded the bug fixes under `## Unreleased`.', 'extras': {'signature': 'EmAKXgFpFH0TdF51iCF8Xl28GfdTkHnxHK/ldKw5+c0xbgW+aEq1M0uiYBTgUmd3ABwUBoAN/2THOhF3Jer4b8XBS/svga5zqyTEt6pSgoT0jAkvWIFgq0HxrUK1ok5rl9M='}}]