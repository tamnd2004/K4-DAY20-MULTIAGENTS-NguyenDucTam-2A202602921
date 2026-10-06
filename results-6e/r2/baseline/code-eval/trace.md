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

### Tool call: glob
{"pattern": "**/*", "path": "workspace"}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/__init__.py', '/workspace/bookings/billing.py', '/workspace/bookings/calendar_export.py', '/workspace/bookings/schedule.py', '/workspace/bookings/timeutil.py', '/workspace/tests/test_bookings.py']

### Tool call: execute
{"command": "pytest workspace/tests/test_bookings.py"}

### Tool result
============================= test session starts ==============================
platform linux -- Python 3.12.15, pytest-9.1.1, pluggy-1.6.0
rootdir: /tmp/lab-code-eval-y810fqwd
plugins: langsmith-0.14.4, anyio-4.15.1
collected 0 items / 1 error

==================================== ERRORS ====================================
______________ ERROR collecting workspace/tests/test_bookings.py _______________
ImportError while importing test module '/tmp/lab-code-eval-y810fqwd/workspace/tests/test_bookings.py'.
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
=============================== 1 error in 0.23s ===============================

Exit code: 2
[Command failed with exit code 2]

### Tool call: execute
{"command": "PYTHONPATH=workspace pytest workspace/tests/test_bookings.py"}

### Tool result
============================= test session starts ==============================
platform linux -- Python 3.12.15, pytest-9.1.1, pluggy-1.6.0
rootdir: /tmp/lab-code-eval-y810fqwd
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

### Tool call: read_file
{"file_path": "workspace/tests/test_bookings.py"}

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
{"file_path": "workspace/bookings/__init__.py"}

### Tool result
@@ lines 1-1 of 1 @@
__version__ = "1.4.2"

### Tool call: read_file
{"file_path": "workspace/bookings/billing.py"}

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
{"file_path": "workspace/bookings/calendar_export.py"}

### Tool result
@@ lines 1-7 of 7 @@
"""Calendar export."""
from .timeutil import parse_duration


def slot_end(start_minute, duration_text):
    """Minute of the day at which a slot ends."""
    return start_minute + parse_duration(duration_text)

### Tool call: read_file
{"file_path": "workspace/bookings/schedule.py"}

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
{"file_path": "workspace/bookings/timeutil.py"}

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
{"file_path": "workspace/CHANGELOG.md"}

### Tool result
@@ lines 1-6 of 6 @@
# Changelog

## Unreleased

## 1.4.2
- initial import

### Tool call: read_file
{"file_path": "workspace/README.md"}

### Tool result
@@ lines 1-5 of 5 @@
# bookings

Small package. Run the tests from the `workspace/` folder:

    cd workspace && python -m pytest tests -q

### Tool call: edit_file
{"old_string": "def billable_blocks(minutes, block=15):\n    \"\"\"Number of billable blocks for a booking.\n\n    A partial block is billed as a full block (always round UP):\n    16 minutes with 15-minute blocks -> 2 blocks.\n    `minutes` must be >= 0; a negative value raises ValueError.\n    \"\"\"\n    return round(minutes / block)", "new_string": "import math\n\ndef billable_blocks(minutes, block=15):\n    \"\"\"Number of billable blocks for a booking.\n\n    A partial block is billed as a full block (always round UP):\n    16 minutes with 15-minute blocks -> 2 blocks.\n    `minutes` must be >= 0; a negative value raises ValueError.\n    \"\"\"\n    if minutes < 0:\n        raise ValueError(\"minutes must be >= 0\")\n    return math.ceil(minutes / block)", "file_path": "workspace/bookings/billing.py"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/billing.py'

### Tool call: edit_file
{"old_string": "def add_slot(slot, slots=[]):\n    \"\"\"Return a NEW list containing the given slots plus `slot`.\n\n    Separate calls must not share state: calling add_slot(\"a\") and then\n    add_slot(\"b\") returns [\"a\"] and then [\"b\"].\n    \"\"\"\n    slots.append(slot)\n    return slots", "file_path": "workspace/bookings/schedule.py", "new_string": "def add_slot(slot, slots=None):\n    \"\"\"Return a NEW list containing the given slots plus `slot`.\n\n    Separate calls must not share state: calling add_slot(\"a\") and then\n    add_slot(\"b\") returns [\"a\"] and then [\"b\"].\n    \"\"\"\n    if slots is None:\n        slots = []\n    return list(slots) + [slot]"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/schedule.py'

### Tool call: edit_file
{"old_string": "def parse_duration(text):\n    \"\"\"Convert a duration string to whole minutes (int).\n\n    Supported formats:\n      \"1h30m\" -> 90\n      \"2h\"    -> 120\n      \"45m\"   -> 45\n      \"1:30\"  -> 90\n      \"45\"    -> 45    # a bare number means minutes\n    Surrounding whitespace is ignored.\n    \"\"\"\n    m = re.fullmatch(r\"(\\d+)h(\\d+)m\", text.strip())\n    if not m:\n        raise ValueError(f\"bad duration: {text!r}\")\n    return int(m.group(1)) * 60 + int(m.group(2))", "file_path": "workspace/bookings/timeutil.py", "new_string": "def parse_duration(text):\n    \"\"\"Convert a duration string to whole minutes (int).\n\n    Supported formats:\n      \"1h30m\" -> 90\n      \"2h\"    -> 120\n      \"45m\"   -> 45\n      \"1:30\"  -> 90\n      \"45\"    -> 45    # a bare number means minutes\n    Surrounding whitespace is ignored.\n    \"\"\"\n    cleaned = text.strip()\n    \n    # \"1h30m\"\n    m = re.fullmatch(r\"(\\d+)h(\\d+)m\", cleaned)\n    if m:\n        return int(m.group(1)) * 60 + int(m.group(2))\n        \n    # \"2h\"\n    m = re.fullmatch(r\"(\\d+)h\", cleaned)\n    if m:\n        return int(m.group(1)) * 60\n        \n    # \"45m\"\n    m = re.fullmatch(r\"(\\d+)m\", cleaned)\n    if m:\n        return int(m.group(1))\n        \n    # \"1:30\"\n    m = re.fullmatch(r\"(\\d+):(\\d+)\", cleaned)\n    if m:\n        return int(m.group(1)) * 60 + int(m.group(2))\n        \n    # \"45\" (bare number)\n    m = re.fullmatch(r\"(\\d+)\",

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/timeutil.py'

### Tool call: execute
{"command": "PYTHONPATH=workspace pytest workspace/tests/test_bookings.py"}

### Tool result
============================= test session starts ==============================
platform linux -- Python 3.12.15, pytest-9.1.1, pluggy-1.6.0
rootdir: /tmp/lab-code-eval-y810fqwd
plugins: langsmith-0.14.4, anyio-4.15.1
collected 3 items

workspace/tests/test_bookings.py ...                                     [100%]

============================== 3 passed in 0.01s ===============================

[Command succeeded with exit code 0]

### Tool call: write_file
{"file_path": "workspace/tests/test_extra_bookings.py", "content": "from bookings.billing import billable_blocks\nfrom bookings.calendar_export import slot_end\nfrom bookings.schedule import add_slot, total_minutes\nfrom bookings.timeutil import parse_duration\nimport pytest\n\n\ndef test_parse_duration_comprehensive():\n    assert parse_duration(\"1h30m\") == 90\n    assert parse_duration(\"2h\") == 120\n    assert parse_duration(\"45m\") == 45\n    assert parse_duration(\"1:30\") == 90\n    assert parse_duration(\"45\") == 45\n    assert parse_duration(\"  2h  \") == 120\n    with pytest.raises(ValueError):\n        parse_duration(\"invalid\")\n\n\ndef test_billable_blocks_validation():\n    assert billable_blocks(0) == 0\n    assert billable_blocks(1) == 1\n    assert billable_blocks(16) == 2\n    with pytest.raises(ValueError):\n        billable_blocks(-1)\n\n\ndef test_slot_end():\n    assert slot_end(60, \"1h30m\") == 150\n\n\ndef test_add_slot_isolated():\n    res1 = add_slot(\"a\")\n    res2 = add_slot(\"b\")\n    assert res1 == [\"a\"]\n    assert res2 == [\"b\"]\n    \n    lst = [\"x\"]\n    assert add_slot(\"y\", lst) == [\"x\", \"y\"]\n    assert lst == [\"x\"]\n"}

### Tool result
Updated file /workspace/tests/test_extra_bookings.py

### Tool call: execute
{"command": "PYTHONPATH=workspace pytest workspace/tests/"}

### Tool result
============================= test session starts ==============================
platform linux -- Python 3.12.15, pytest-9.1.1, pluggy-1.6.0
rootdir: /tmp/lab-code-eval-y810fqwd
plugins: langsmith-0.14.4, anyio-4.15.1
collected 7 items

workspace/tests/test_bookings.py ...                                     [ 42%]
workspace/tests/test_extra_bookings.py ....                              [100%]

============================== 7 passed in 0.04s ===============================

[Command succeeded with exit code 0]

### Tool call: delete
{"file_path": "workspace/tests/test_extra_bookings.py"}

### Tool result
Deleted /workspace/tests/test_extra_bookings.py

### Tool call: execute
{"command": "PYTHONPATH=workspace pytest workspace/tests/test_bookings.py"}

### Tool result
============================= test session starts ==============================
platform linux -- Python 3.12.15, pytest-9.1.1, pluggy-1.6.0
rootdir: /tmp/lab-code-eval-y810fqwd
plugins: langsmith-0.14.4, anyio-4.15.1
collected 3 items

workspace/tests/test_bookings.py ...                                     [100%]

============================== 3 passed in 0.01s ===============================

[Command succeeded with exit code 0]

### Assistant
[{'type': 'text', 'text': 'I have fixed the source code so that all tests pass and every function conforms to its docstring specification:\n\n1. **`workspace/bookings/timeutil.py` (`parse_duration`)**: Updated `parse_duration` to support all formats specified in its docstring (`"1h30m"`, `"2h"`, `"45m"`, `"1:30"`, and bare minutes `"45"`), handling surrounding whitespace correctly.\n2. **`workspace/bookings/billing.py` (`billable_blocks`)**: Fixed rounding to always round up (`math.ceil`) and added validation to raise a `ValueError` if `minutes` is negative.\n3. **`workspace/bookings/schedule.py` (`add_slot`)**: Fixed the default mutable argument bug (`slots=[]`) to prevent state sharing across separate function calls, ensuring a new list is returned.', 'extras': {'signature': 'EmAKXgFpFH0TXFauuSaHB+u77BJyOq6lAC99ojDgwFWuMY+9dPHbH7052BLbTXbj3kqHexBexPiz5kNZ6wYee0DEMSW4BIWETGmxb9D2W27MaH3prr5gV3vklHzCqfIVr0g='}}]