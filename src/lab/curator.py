"""GUIDE Phần 3 - Người tuyển chọn skill (skill curator): tự viết skill từ các lần chạy thất bại.   >>> SINH VIÊN CÀI ĐẶT curate_skills <<<

Pseudo-code: guides/pseudocode/04_curator.md
Kiểm tra:    pytest tests/test_04_curator.py
Chạy thật:   python -m lab.curator
"""
import json
import re
from pathlib import Path

from .tasks import ROOT, eval_markers   # có sẵn: định danh của tác vụ đánh giá, tính lúc chạy

# ---- CÓ SẴN, KHÔNG SỬA: kiểm tra và tách khối skill (phần dễ sai và liên quan bảo mật) ----------------
SAFE_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def validate_skill(text: str, expected_name: str | None = None) -> list[str]:
    """Kiểm tra nội dung một SKILL.md. Trả về danh sách vấn đề (rỗng = hợp lệ).

    Quy tắc: có khối YAML frontmatter; `name` chữ thường/số/gạch ngang (tối đa 64 ký tự) và bằng `expected_name`
    nếu được truyền; có `description` (tối đa 1024 ký tự); phần thân tối đa 80 dòng; không chứa chuỗi nào của
    `eval_markers()`. Quy tắc về `name` cũng là biện pháp bảo mật: tên khối do LLM sinh ra được dùng để tạo
    đường dẫn, nên `../evil` không được lọt qua.
    """
    problems = []
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text.strip() + "\n", re.S)
    if not m:
        return ["missing YAML frontmatter"]
    front, body = m.groups()
    name = re.search(r"^name:\s*(.+)$", front, re.M)
    desc = re.search(r"^description:\s*(.+)$", front, re.M)
    n = name.group(1).strip() if name else ""
    if not SAFE_NAME.fullmatch(n) or len(n) > 64:
        problems.append("invalid name")
    elif expected_name is not None and n != expected_name:
        problems.append("name differs from the block name")
    if not desc or len(desc.group(1).strip()) > 1024:
        problems.append("missing or too long description")
    if len(body.strip().splitlines()) > 80:
        problems.append("body longer than 80 lines")
    low = text.lower()
    for marker in eval_markers():
        if marker in low:
            problems.append(f"mentions evaluation material: {marker}")
    return problems


def parse_skill_blocks(reply: str) -> list[tuple[str, str]]:
    """Tách câu trả lời của LLM thành danh sách (name, nội dung SKILL.md).

    Khuôn dạng: `=== SKILL: <name> ===` ... `=== END ===`. Một khối kết thúc ở điểm nào đến trước trong ba điểm:
    `=== END ===`, tiêu đề `=== SKILL:` kế tiếp, hoặc cuối văn bản (LLM đôi khi quên dòng END).
    """
    pattern = re.compile(r"^=== SKILL: (\S+) ===[ \t]*\n(.*?)(?=^=== END ===|^=== SKILL: |\Z)", re.S | re.M)
    return [(name, text.strip()) for name, text in pattern.findall(str(reply))]
# --------------------------------------------------------------------------------------------------

# Mẫu prompt theo guides/pseudocode/04_curator.md (tiếng Anh vì tác vụ và mô hình dùng tiếng Anh).
TRACE_CHARS = 6000
CURATOR_PROMPT = """You write SKILLS for a coding and data-analysis agent.
Below are the checks that failed (name and the feedback of the review bot) and the end of the trace of each run on a
LEARNING task. Find the general PROCESS mistakes (not task-specific answers) and write at most {max_skills} short skills
that would prevent those mistakes on NEW tasks of the same kind.

Rules:
- A skill must be general: never mention a task id, the name of a data file, function or column that exists only in
  one task, an answer or a number from these runs. Names that a house convention itself requires (an output file name,
  a JSON key, a header) are allowed, because they are the rule.
- Feedback that starts with "RULE:" is a house convention that the task text never states, so the agent cannot guess
  it. Write every such convention into a skill precisely and completely (exact output file names, JSON keys and
  values, headers, formats, units, sort orders, minimum counts). Generic advice such as "read the instructions
  carefully" does not help; every line must be an action the agent can carry out and check.
- Group the conventions by the kind of work they apply to (for example changing a Python package, producing a report
  from tabular data, triaging a log file), one skill per kind.
- Each skill starts with YAML frontmatter with `name` (lower case letters, digits and hyphens) and `description`
  (one sentence that starts with "Use when" and names the broad kind of task that should trigger it), followed by at
  most 40 lines of imperative instructions (a numbered checklist works well, ending with a self-check).
- Output format, character for character:
=== SKILL: <name> ===
---
name: <name>
description: <when to use>
---
<instructions>
=== END ===

{runs}
"""


def curate_skills(results_dir="results", source_condition="baseline", out_dir=None, model=None, max_skills: int = 3) -> list[Path]:
    """Đọc các lần chạy của TÁC VỤ HỌC (role == "learn") trong `source_condition`, nhờ LLM viết skill, ghi file.

    Các bước: nạp run.json + trace.md -> (nếu không có check nào thất bại: in cảnh báo và trả về [] mà KHÔNG gọi LLM)
    -> dựng prompt -> model.invoke(prompt) -> parse_skill_blocks -> validate_skill(text, expected_name=name)
    -> ghi `<out_dir>/<name>/SKILL.md`. Mặc định `out_dir` = <gốc lab>/skills/auto (dùng `ROOT` từ lab.tasks).
    Giữ tối đa `max_skills` skill hợp lệ; skill không hợp lệ bị bỏ qua.
    Prompt chứa, với mỗi check thất bại, TÊN và trường `detail` (lời nhận xét của bot đánh giá: phát biểu quy tắc bị vi phạm)
    cùng phần cuối của vết (trace). Với tác vụ học, `detail` chỉ phát biểu quy tắc, không chứa đáp án.
    Tuyệt đối KHÔNG đưa dữ liệu của tác vụ đánh giá (role == "eval") vào prompt.
    model mặc định: make_model() (lab.model).
    Trả về: danh sách đường dẫn SKILL.md đã ghi.
    """
    out_dir = Path(out_dir) if out_dir is not None else ROOT / "skills" / "auto"

    runs = []
    for f in sorted((Path(results_dir) / source_condition).glob("*/run.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        if r.get("role") != "learn":                 # tuyệt đối không dùng dữ liệu tác vụ đánh giá
            continue
        trace_file = f.parent / "trace.md"
        trace = trace_file.read_text(encoding="utf-8")[-TRACE_CHARS:] if trace_file.exists() else ""
        failed = [(c["name"], c.get("detail", "")) for c in r.get("checks", []) if not c.get("passed")]
        runs.append({"task": r.get("task", f.parent.name), "failed": failed, "trace": trace})

    runs = [r for r in runs if r["failed"]]
    if not runs:
        print(f"WARNING: no failed check in the learning runs of '{source_condition}' - nothing to learn, model not called")
        return []

    blocks = []
    for r in runs:
        checks = "\n".join(f"- {name}: {detail}" for name, detail in r["failed"])
        blocks.append(f"## Run of task {r['task']}\nFailed checks (name: review bot feedback):\n{checks}\n"
                      f"Trace (last part):\n{r['trace']}")
    prompt = CURATOR_PROMPT.format(max_skills=max_skills, runs="\n\n".join(blocks))

    if model is None:
        from .model import make_model
        model = make_model()
    reply = model.invoke(prompt)
    reply = reply.text if hasattr(reply, "text") else str(reply.content)

    written = []
    for name, text in parse_skill_blocks(reply):
        problems = validate_skill(text, expected_name=name)
        if problems or len(written) >= max_skills:
            print(f"skipped skill {name!r}: {', '.join(problems) or 'max_skills reached'}")
            continue
        path = out_dir / name / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + "\n", encoding="utf-8", newline="\n")     # LF cả trên Windows: hash skill giống máy chấm
        written.append(path)
    return written


if __name__ == "__main__":
    for p in curate_skills():
        print("wrote", p)
