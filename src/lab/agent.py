"""GUIDE Phần 1 - Dựng tác tử (agent) bằng Deep Agents.   >>> SINH VIÊN CÀI ĐẶT make_backend VÀ build_agent <<<

Pseudo-code: guides/pseudocode/01_agent.md
Kiểm tra:    pytest tests/test_02_agent.py
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import LocalShellBackend
from deepagents.backends.protocol import ExecuteResponse

from .model import make_model
from .subagents import get_subagents

# ---- CÓ SẴN, KHÔNG SỬA: system prompt dùng chung cho mọi sinh viên (để đường cơ sở so sánh được) ----
PATHS_NOTE = (
    "PATHS: every path is relative to the sandbox root and never starts with '/'. "
    "The task files are in the folder workspace/ (for example workspace/app.log). "
    "Use exactly this relative form both in the file tools and in the shell (execute); "
    "the shell starts in the sandbox root. "
)
BASE_PROMPT = (
    "You are an engineering assistant working in a sandbox. "
    + PATHS_NOTE
    + "Use the shell to run Python and tests. "
    "When you are done, reply with a short summary that mentions only files you really created or changed."
)
SKILLS_NOTE = (
    " Skills are in the folder skills/ (one sub-folder per skill with a SKILL.md). "
    "As your FIRST action, read the SKILL.md of every skill whose description could apply to the task, "
    "then follow them. Never modify skills/."
)
SUBAGENTS_NOTE = (
    " You have specialised subagents (see the description of the task tool). "
    "For anything beyond a trivial step, delegate to a suitable subagent and put ALL the task rules and file paths "
    "in the delegation message, because a subagent sees only what you send. "
    "Check what a subagent returns before you rely on it."
)
# --------------------------------------------------------------------------------------------------


def make_backend(sandbox: Path):
    """Tạo backend (môi trường thực thi) cho tác tử.

    Yêu cầu:
      - Thư mục gốc (root_dir) là `sandbox`; đường dẫn tương đối `workspace/...` và `skills/...`
        phải dùng được ở CẢ công cụ tệp lẫn shell (shell chạy với thư mục làm việc = `sandbox`).
      - Tác tử chạy được lệnh shell và gọi được `python` (cần đặt PATH).
      - KHÔNG chuyển biến môi trường của bạn vào shell của tác tử (khóa API không được lộ).
    """
    python_dir = str(Path(sys.executable).parent)
    env = {
        "PATH": python_dir + ":/usr/local/bin:/usr/bin:/bin",
        "HOME": str(sandbox),
        "PYTHONDONTWRITEBYTECODE": "1",          # không sinh __pycache__ trong workspace
    }
    options = {"root_dir": sandbox, "virtual_mode": True, "inherit_env": False, "timeout": 120}
    if os.name != "nt":
        return LocalShellBackend(env=env, **options)
    # Windows: chỉ thêm các biến hệ thống (không bí mật) mà python cần; vẫn không kế thừa môi trường của tiến trình cha.
    system_root = os.environ.get("SYSTEMROOT", r"C:\Windows")
    env.update({
        "PATH": os.pathsep.join([python_dir, system_root + r"\System32"]),
        "SYSTEMROOT": system_root,
        "TEMP": tempfile.gettempdir(),
        "TMP": tempfile.gettempdir(),
        "PYTHONUTF8": "1",                       # open()/print mặc định UTF-8 như trên Linux
    })
    return _GitBashBackend(env=env, **options)


def _find_git_bash() -> Path:
    """Tìm bash.exe của Git for Windows (không dùng `bash` trong System32: đó là trình khởi chạy WSL)."""
    roots = [Path(os.environ[v]) / sub for v, sub in (("ProgramFiles", "Git"), ("ProgramW6432", "Git"),
                                                       ("LOCALAPPDATA", "Programs/Git")) if os.environ.get(v)]
    git = subprocess.run(["where", "git"], capture_output=True, text=True).stdout.splitlines()
    roots += [p for g in git if g.strip() for p in Path(g.strip()).parents]
    for root in roots:
        if (root / "bin" / "bash.exe").is_file():
            return root / "bin" / "bash.exe"
    raise RuntimeError("Git Bash not found: install Git for Windows, or run the lab in WSL/Docker (README section 4)")


class _GitBashBackend(LocalShellBackend):
    """Chỉ dùng trên Windows. LocalShellBackend chạy lệnh bằng subprocess(shell=True), tức cmd.exe, nên các lệnh kiểu
    /bin/sh của tác tử (which, cat, ls, |, &&) không chạy. Lớp này chạy đúng lệnh đó bằng Git Bash và giữ nguyên
    định dạng kết quả của LocalShellBackend (stdout, dòng `[stderr]`, cắt bớt, `Exit code`, hết giờ = 124)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._bash = str(_find_git_bash())

    def execute(self, command: str, *, timeout: int | None = None) -> ExecuteResponse:
        if not command or not isinstance(command, str):
            return ExecuteResponse(output="Error: Command must be a non-empty string.", exit_code=1, truncated=False)
        limit = timeout if timeout is not None else self._default_timeout
        if limit <= 0:
            raise ValueError(f"timeout must be positive, got {limit}")
        # Ghi lệnh ra tệp .sh (ngoài sandbox) để tránh lỗi trích dẫn tham số giữa Windows và bash.
        # venv trên Windows không có `python3`, nên định nghĩa hàm thay thế như trên Linux.
        fd, script = tempfile.mkstemp(suffix=".sh")
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write('python3() { python "$@"; }\n' + command + "\n")
        try:
            proc = subprocess.Popen([self._bash, "--noprofile", "--norc", script], cwd=str(self.cwd), env=self._env,
                                    stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                out, err = proc.communicate(timeout=limit)
            except subprocess.TimeoutExpired:
                # Giết cả cây tiến trình: tiến trình con của bash giữ pipe và làm communicate() treo.
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
                proc.communicate()
                return ExecuteResponse(output=f"Error: Command timed out after {limit} seconds.", exit_code=124,
                                       truncated=False)
        finally:
            os.unlink(script)
        stdout = out.decode("utf-8", "replace").replace("\r\n", "\n")
        stderr = err.decode("utf-8", "replace").replace("\r\n", "\n")
        parts = [stdout] if stdout else []
        parts += [f"[stderr] {line}" for line in stderr.strip().split("\n")] if stderr else []
        output = "\n".join(parts) if parts else "<no output>"
        truncated = len(output) > self._max_output_bytes
        if truncated:
            output = output[: self._max_output_bytes] + f"\n\n... Output truncated at {self._max_output_bytes} bytes."
        if proc.returncode != 0:
            output = f"{output.rstrip()}\n\nExit code: {proc.returncode}"
        return ExecuteResponse(output=output, exit_code=proc.returncode, truncated=truncated)


def build_agent(sandbox: Path, mode: str = "single", use_skills: bool = False, model=None):
    """Tạo tác tử Deep Agents.

    Tham số:
      sandbox:    thư mục chứa `workspace/` (và `skills/` nếu có).
      mode:       "single"    -> tác tử mặc định (có subagent `general-purpose` sẵn của Deep Agents)
                  "subagents" -> thêm các subagent từ `get_subagents()` (nối PATHS_NOTE vào `system_prompt` của MỖI subagent,
                                 vì subagent không nhận BASE_PROMPT) và thêm SUBAGENTS_NOTE vào prompt chính
      use_skills: True -> nạp thư mục "/skills/" qua tham số `skills=` của create_deep_agent
                  và thêm SKILLS_NOTE vào prompt.
      model:      mô hình ngôn ngữ; None -> dùng `make_model()`.
    mode không hợp lệ -> ném ValueError.
    Trả về: đồ thị (graph) đã biên dịch, gọi bằng `.invoke({"messages": [...]})`.
    """
    if mode not in ("single", "subagents"):
        raise ValueError(f"unknown mode: {mode!r} (expected 'single' or 'subagents')")

    kwargs = {}
    prompt = BASE_PROMPT
    if mode == "subagents":
        # subagent không nhận BASE_PROMPT -> nối quy ước đường dẫn vào system_prompt của từng subagent
        kwargs["subagents"] = [{**sub, "system_prompt": sub["system_prompt"] + " " + PATHS_NOTE} for sub in get_subagents()]
        prompt += SUBAGENTS_NOTE
    if use_skills:
        kwargs["skills"] = ["/skills/"]                # đường dẫn ảo, tính từ root_dir của backend
        prompt += SKILLS_NOTE

    return create_deep_agent(
        model=model if model is not None else make_model(),     # make_model() có sẵn trong model.py
        system_prompt=prompt,
        backend=make_backend(sandbox),
        **kwargs,
    )
