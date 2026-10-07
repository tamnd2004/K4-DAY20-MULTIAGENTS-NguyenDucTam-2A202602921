### Human
The test suite of the `bookings` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Tool call: task
{"description": "Explore the workspace folder, check the files in bookings package and tests, run pytest to see failures, and report facts.", "subagent_type": "explorer"}

### Tool result
Here are the facts gathered from exploring the workspace folder:

### Required Output Files & Exact Format
- No required output files are specified for this exploration task.

### Rules and Conventions Found
- **README.md (`workspace/README.md`)**:
  > Small package. Run the tests from the `workspace/` folder:
  > 
  >     cd workspace && python -m pytest tests -q

### Package Files & Data Quirks
- **`workspace/bookings/__init__.py`**: Version `"1.4.2"`
- **`workspace/bookings/billing.py`**: 
  - `billable_blocks(minutes, block=15)` uses `round(minutes / block)` instead of rounding up (e.g. `math.ceil`), causing `billable_blocks(20)` to return `1` instead of `2`.
- **`workspace/bookings/timeutil.py`**:
  - `parse_duration(text)` only matches the strict regex pattern `r"(\d+)h(\d+)m"`, failing to support `"2h"`, `"45m"`, `"1:30"`, or `"45"` despite the docstring claiming support for all of them.
- **`workspace/bookings/schedule.py`**:
  - `add_slot(slot, slots=[])` uses a mutable default argument (`slots=[]`), which can lead to shared state across function calls if `slots` is omitted.

### Failing Tests and Error Lines
Running `cd workspace && python -m pytest tests -q` results in 2 failures:
1. `FAILED tests/test_bookings.py::test_total_minutes_mixed_formats - ValueError: bad duration: '2h'`
   - **File**: `bookings/timeutil.py:18`
   - **Reason**: `parse_duration` does not parse single-unit or alternative duration formats like `"2h"`.
2. `FAILED tests/test_bookings.py::test_

### Tool call: task
{"description": "Read the full source files in workspace/bookings/ (`__init__.py`, `billing.py`, `schedule.py`, `timeutil.py`) and tests/ (`tests/test_bookings.py`), and analyze all docstrings, specifications, and implementations thoroughly.", "subagent_type": "explorer"}

### Tool result
- **Required output files and their exact format**: No specific output files requested (the prompt asks to read source files and tests, and analyze all docstrings, specifications, and implementations thoroughly).
- **Rules and conventions found**:
  - README.md: "Run the tests from the `workspace/` folder: `cd workspace && python -m pytest tests -q`"
  - `bookings/billing.py`:
    - Docstring for `billable_blocks(minutes, block=15)`:
      > Number of billable blocks for a booking.
      >
      > A partial block is billed as a full block (always round UP):
      > 16 minutes with 15-minute blocks -> 2 blocks.
      > `minutes` must be >= 0; a negative value raises ValueError.
    - Implementation uses `round(minutes / block)`, which rounds to nearest (rounding down for 20 with 15-minute blocks, i.e. `20 / 15 = 1.333` -> `1`), violating the "always round UP" specification.
  - `bookings/schedule.py`:
    - Docstring for `add_slot(slot, slots=[])`:
      > Return a NEW list containing the given slots plus `slot`.
      >
      > Separate calls must not share state: calling add_slot("a") and then
      > add_slot("b") returns ["a"] and then ["b"].
    - Implementation uses mutable default argument `slots=[]` and `slots.append(slot)` followed by returning `slots`, which mutates and shares state across calls, violating the default argument mutation pitfall and requirement for separate state.
  - `bookings/timeutil.py`:
    - Docstring for `parse_duration(text)`:
      > Convert a