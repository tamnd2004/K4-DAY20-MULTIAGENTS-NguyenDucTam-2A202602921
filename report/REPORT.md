# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Nguyễn Đức Tâm | 2A202602921 | Làm cá nhân: toàn bộ mã, các lần chạy và báo cáo |

- Mô hình: `LAB_MODEL=google_genai:gemini-3.5-flash-lite` (Google AI Studio, khóa free tier). `LAB_TEMPERATURE=0` nhưng mô hình này dùng tham số lấy mẫu cố định và bỏ qua `temperature` (cảnh báo của `langchain-google-genai`: "uses fixed sampling defaults; the sampling parameter(s) temperature will be ignored"), nên mỗi lần chạy không tất định. `recursion_limit = 60` (mặc định của `lab.runner`).
- Deep Agents 0.7.21 (`langchain` 1.4.3, `langgraph` 1.2.13). Máy chủ Windows 11; mọi lần chạy tác vụ dùng trong báo cáo chạy trong Docker (`Dockerfile` của lab, `python:3.12-slim`, Python 3.12.15) để shell của tác tử là `/bin/sh` như máy chấm. Test ngoại tuyến đạt 29/29 cả trên Windows (Python 3.11.4) lẫn trong Docker.
- Số lần chạy tác vụ đã dùng / ngân sách: xem Phụ lục (không có ngân sách cố định; giới hạn thực tế là quota free tier của Gemini).
- Commit của tag `freeze`: `82e72bc` (2026-10-06T12:21:38+07:00); commit giả thuyết `04d6acf` đứng ngay trước.

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): trên tác vụ đánh giá, `subagents` KHÔNG cao hơn `baseline` (điểm trung bình chênh trong khoảng ±0,10) nhưng tốn token nhiều hơn (ít nhất 1,3 lần). Căn cứ: trên tác vụ học hai điều kiện có cùng 16/18 check kỹ thuật và 0/9 check quy ước (điểm trung bình 0,580 so với 0,597); worker không biết quy ước Acme nhiều hơn coordinator; lời giao việc làm rơi thông tin (data-learn: lời giao cho `implementer` thiếu ranh giới Q1 theo UTC nên `north_q1_revenue` và `north_q1_orders` sai, `reviewer` vẫn xác nhận); token trung bình 384k so với 277k; bài viết về hệ đa tác tử của Anthropic ghi nhận đa tác tử tốn khoảng 15 lần token so với hội thoại thường.
- H2 (skills-auto so với baseline): `skills-auto` đạt điểm trung bình cao nhất trên tác vụ đánh giá, cao hơn `baseline` khoảng 0,10 đến 0,25, nhờ các quy ước của tác vụ học được dùng lại; nhưng không đạt tối đa vì quy ước MỚI của tác vụ đánh giá không có trong skill và tác tử chỉ làm theo skill một phần khi đề bài nói khác (Phần 3.4: logs-learn vẫn ghi `payment-service` như ví dụ trong đề). Căn cứ: 9/11 check thất bại của baseline trên tác vụ học là quy ước ẩn (nhóm E); ở Phần 3.4 skill nâng điểm trung bình tác vụ học từ 0,597 lên 0,813 và mỗi lần chạy đều đọc đúng skill (`skills_read = 1`). SkillsBench cho thấy skill tự sinh trung bình không có lợi, nhưng skill ở đây chép lại quy ước cụ thể từ phản hồi nên gần với skill do con người biên soạn (+16 điểm phần trăm).
- H3 (tác vụ học so với tác vụ đánh giá): mức cải thiện của `skills-auto` so với `baseline` trên tác vụ đánh giá NHỎ hơn trên tác vụ học (+0,216), và check quy ước mới của tác vụ đánh giá trượt ở cả ba điều kiện. Căn cứ: SkillEvolBench ghi nhận lợi ích trên tác vụ học thường không chuyển sang tác vụ mới; skill dữ liệu có chi tiết riêng của tác vụ học (giá trị `-999`, chuẩn hóa tên vùng) và thiếu tên cột của `clean.csv`, dấu hiệu quá khớp; dữ liệu đánh giá khác dữ liệu học.

## 3. Làm quen Deep Agents (Phần 0.3)

Nguồn: `python scripts/tour.py` (mô hình giả, 0 token), mã `src/lab/agent.py` và `src/lab/subagents.py`, lần chạy `results/baseline/data-learn` (`gemini-3.5-flash-lite`, trong Docker). Ba câu hỏi Phần 0.3 của GUIDE (công cụ mặc định, subagent `general-purpose`, câu trích từ mô tả `task` và `execute`) được trả lời trong câu 2 và câu 3.

**Câu 1. Bài lab này có bao nhiêu agent? Mỗi agent làm gì?**

Kiến trúc gồm một tác tử chính đóng vai coordinator và các subagent đóng vai worker, được gọi qua công cụ `task`. Số agent phụ thuộc điều kiện thí nghiệm:

| Agent | Có ở điều kiện | Vai trò |
|---|---|---|
| Tác tử chính (coordinator) | cả 3 | Nhận đề bài (`instruction.md`) làm tin nhắn người dùng, system prompt là `BASE_PROMPT` (cộng `SUBAGENTS_NOTE` hoặc `SKILLS_NOTE`). Tự đọc, sửa tệp và chạy shell, quyết định có giao việc hay không, viết tóm tắt cuối. |
| `general-purpose` | cả 3 (Deep Agents luôn thêm) | Worker đa năng cho việc nhiều bước hoặc tìm kiếm; "This agent has access to all tools as the main agent." |
| `explorer` | `subagents` | Chỉ đọc: README, docstring, CHANGELOG, mẫu dữ liệu, test có sẵn. Báo cáo sự thật, quy ước và đặc điểm dữ liệu bẩn; không sửa tệp. |
| `implementer` | `subagents` | Thực hiện thay đổi đã được đặc tả đủ: sửa nguyên nhân gốc, ghi tệp đầu ra đúng tên và định dạng, chạy test, báo cáo các tệp thật sự đã đổi. |
| `reviewer` | `subagents` | Kiểm tra độc lập, chỉ đọc: tính lại số liệu, chạy test, đối chiếu từng yêu cầu và quy ước; trả danh sách PASS/FAIL kèm bằng chứng. |

Như vậy `baseline` và `skills-auto` có 2 agent (1 coordinator, 1 worker mặc định), `subagents` có 5 (1 coordinator, 4 worker). Vai trò "evaluator" ở bài này không phải agent: điểm do `tasks/<id>/check.py` chấm tất định (deterministic). Curator (Phần 3) cũng không phải agent: đó là một lần gọi `model.invoke` để viết skill, không có công cụ.

Có worker không có nghĩa là worker được dùng: ở lần chạy `baseline` của `data-learn`, `subagent_calls = 0`, tác tử chính tự làm hết bằng 20 tool call.

**Câu 2. Coordinator giao tiếp với worker agents bằng cách nào?**

Không có message queue hay API mạng; tất cả chạy trong cùng một tiến trình Python (đồ thị LangGraph):

1. Coordinator gọi công cụ `task(description=..., subagent_type=...)`, với `subagent_type` là `explorer`, `implementer`, `reviewer` hoặc `general-purpose`. Mô tả của `task` liệt kê các worker kèm `description` của chúng; việc định tuyến do LLM quyết định dựa trên các mô tả này, không có bảng định tuyến cứng.
2. Deep Agents tạo một phiên bản worker mới với ngữ cảnh cô lập: "Each invocation is stateless by default: the agent sees only the prompt you give it and returns a single final report." Worker không thấy lịch sử hội thoại và không nhận `BASE_PROMPT`, nên `build_agent` nối `PATHS_NOTE` vào `system_prompt` của từng worker. Worker tự định nghĩa không thừa kế skill của coordinator (chỉ `general-purpose` thừa kế).
3. Worker chạy vòng lặp công cụ riêng rồi trả một báo cáo cuối, quay về coordinator dưới dạng `ToolMessage` của lệnh gọi `task`. Coordinator phải tự kiểm chứng ("Check what a subagent returns before you rely on it.", trong `SUBAGENTS_NOTE`) rồi giao bước tiếp theo hoặc kết thúc.
4. Kênh gián tiếp là hệ thống tệp dùng chung: implementer ghi `workspace/answer.json`, reviewer đọc lại chính tệp đó.
5. Song song: nhiều lệnh `task` trong cùng một message có thể chạy đồng thời ("Launch multiple agents concurrently when their tasks are independent, using a single message with multiple tool calls.").

Hệ quả cho đo đạc: `trace.md` chỉ ghi luồng chính (lệnh `task` và báo cáo cuối), còn token của worker vẫn được cộng đủ nhờ `UsageMetadataCallbackHandler`. Lỗi của worker hoặc của API (kể cả vượt `recursion_limit`) không làm dừng chương trình: `run_task` ghi vào trường `error` và vẫn chấm workspace hiện có; mỗi lệnh shell bị giới hạn 120 giây (`timeout` của backend).

**Câu 3. Có những công cụ (tools) nào được chia sẻ giữa các agent?**

Theo `scripts/tour.py`, tác tử mặc định có 9 công cụ: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep` (công cụ tệp), `execute` (shell, công cụ duy nhất chạy được lệnh) và `task` (giao việc cho subagent). System prompt mặc định của Deep Agents rỗng (`''`).

- Dùng chung: mỗi worker nhận `FilesystemMiddleware` gắn với cùng một backend (`make_backend(sandbox)`), nên có cùng 7 công cụ tệp và `execute`, cùng thư mục gốc là sandbox (`workspace/`, `skills/`), cùng môi trường shell (`PATH` chỉ có `python` của môi trường ảo, không có khóa API vì `inherit_env=False`; trên Windows lệnh chạy qua Git Bash). Các agent cũng dùng chung mô hình (`make_model()`) và bộ đếm token.
- Không chia sẻ: `task` chỉ có ở coordinator, nên worker không gọi được worker khác; skill chỉ đến coordinator và `general-purpose`.
- Giới hạn "chỉ đọc" của explorer và reviewer chỉ nằm trong `system_prompt`, không được cưỡng chế: không thể dùng `permissions=` cùng backend có shell (Deep Agents ném `NotImplementedError`), nên về kỹ thuật hai worker này vẫn có công cụ ghi.

Câu hướng dẫn hành vi trích từ mô tả công cụ:

- `task`: "Put full detail in the prompt and state exactly what it should return".
- `execute`: "You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search. Use read_file rather than cat/head/tail." Mô tả này còn khuyên "Use absolute paths and avoid `cd`", trái với quy ước đường dẫn tương đối của lab; vì vậy `BASE_PROMPT` nêu rõ `PATHS_NOTE`. Trong lần chạy `data-learn`, tác tử vẫn dùng `execute` (`python3 -c ...`) cho cả việc đọc dữ liệu: 17/20 tool call là `execute`, chỉ 1 lần `read_file`.

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

Nguồn: `results/baseline/{data,code,logs}-learn` (lần chạy đầu tiên còn lưu sau khi loại một lần chạy lỗi hạ tầng, xem mục 7).

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| data-learn | `rule_money_in_cents` | E | `detail`: "RULE: money values in answer.json are integer cents (1606.67 USD is written 160667)". Vết: `write_file` ghi `"north_q1_revenue": 3130.24` (USD), đúng với đề ("(number): sum of `amount`") nhưng sai quy ước. |
| data-learn | `rule_meta_block` | E | `detail`: "answer.json has an object `meta` = {"source", "rows_in", "rows_used"}". `answer.json` chỉ có đúng 5 khóa đề liệt kê; đề chỉ nói "plus whatever the Acme reporting conventions require". |
| data-learn | `rule_clean_csv` | E | `detail`: "write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents ...". Tác tử không tạo `clean.csv` (chỉ có 1 lần `write_file`, cho `answer.json`). |
| logs-learn | `rule_service_names` | E | `detail`: "service names in the output are lower-case with '-' replaced by '_'". Vết: đầu ra giữ `"service": "inventory-service"`, giống ví dụ `payment-service` trong đề. |
| logs-learn | `rule_sorted_errors` | E | `detail`: "`errors` is sorted by service, then by timestamp_utc, ascending". Đề không nêu thứ tự; script giữ thứ tự dòng trong log. |
| logs-learn | `rule_schema_header` | E | `detail`: "the top-level object has "schema_version": 2 and "generated_by": "log-triage"". Đầu ra chỉ có `errors` và `counts_by_service` như cấu trúc mẫu trong đề. |
| code-learn | `rule_type_hints` | E | `detail`: "every public function ... has type annotations on all parameters and on the return value". Không lệnh `edit_file` nào thêm chú thích kiểu. |
| code-learn | `rule_regression_tests` | E | `detail`: "add tests/test_regressions.py with one test function per bug you fixed (at least 3)". Tác tử thêm test vào `tests/test_report.py` thay vì tạo tệp mới. |
| code-learn | `rule_changelog` | E | `detail`: "record each fix in CHANGELOG.md under the heading '## Unreleased' ...". Tác tử có `read_file` `workspace/CHANGELOG.md` nhưng không sửa. |
| code-learn | `tests_not_modified` | A | `detail`: "the original files in tests/ must not be modified". Đề ghi rõ "Do not modify the existing files in `tests/`", nhưng vết có `edit_file` trên `workspace/tests/test_report.py` (thêm `test_low_stock_edge_cases`). |
| code-learn | `visible_suite_passes` | G | `detail`: "1 failed, 9 passed". Test do chính tác tử thêm có kỳ vọng sai (`assert low_stock(items) == ["Apple", "cat", "zebra"]`, trong khi hàm đã sửa trả `['Apple']`); tác tử sửa đi sửa lại đến khi hết `recursion_limit` (`GraphRecursionError` ở 60 bước, 30 tool call, 593k token). Nhóm G: không hội tụ do tự tạo test sai. |

Nhận xét:

- Nhóm E chiếm đa số: 9/11 check thất bại là quy ước Acme (tên bắt đầu bằng `rule_`, `detail` bắt đầu bằng `RULE:`). Nguyên nhân chung: đề chỉ nói "plus whatever the Acme ... conventions require" mà không nêu quy ước, và workspace không có tài liệu quy ước; tác tử không có cách nào biết, nên đây không phải lỗi quy trình mà là thiếu tri thức.
- Bằng chứng phủ định cho A đến D (`python scripts/check_breakdown.py`): `baseline` đạt 16/18 check kỹ thuật trên tác vụ học. Hai check kỹ thuật trượt đều ở code-learn (A và G ở trên); mọi check về dữ liệu bẩn và định dạng (trùng lặp, giá trị thiếu `-999`, ba định dạng ngày, múi giờ, traceback nhiều dòng, dòng lặp) đều đạt, nên không có lỗi nhóm D. Ở data-learn và logs-learn, tác tử đọc `workspace/README.md` trước khi làm (không phải nhóm A) và đọc lại tệp đầu ra trước khi kết thúc (không phải nhóm B). Không có câu trả lời cuối nào nhắc tệp không tồn tại (không có nhóm F).
- Skill có thể phòng ngừa nhóm E, vì `detail` của tác vụ học phát biểu chính xác quy ước; tác vụ đánh giá dùng lại các quy ước này nên skill chép lại quy ước có thể chuyển giao. Skill không giúp được quy ước MỚI chỉ có ở tác vụ đánh giá.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa (`src/lab/subagents.py`): `explorer` (chỉ đọc: README, docstring, CHANGELOG, mẫu dữ liệu, test; báo cáo sự thật và quy ước tìm thấy), `implementer` (thực hiện thay đổi, sửa nguyên nhân gốc, chạy test, báo cáo tệp thật sự đã đổi), `reviewer` (chỉ đọc, kiểm tra độc lập từng yêu cầu, trả PASS/FAIL kèm bằng chứng). Lý do: tách đọc, làm, kiểm tra để nhắm vào nhóm lỗi A (bỏ qua đặc tả), C (vá triệu chứng) và B (không kiểm chứng). `description` của mỗi subagent nói KHI NÀO gọi (explorer "FIRST", reviewer "LAST") và nhắc tác tử chính gửi đủ quy tắc vì subagent chỉ thấy lời giao việc.
- `subagent_calls` (luồng chính) trên tác vụ học: data-learn 4 (`explorer` 2, `implementer` 1, `reviewer` 1), code-learn 5 (`explorer` 1, `general-purpose` 2, `implementer` 1, `reviewer` 1), logs-learn 4 (`explorer` 1, `implementer` 2, `reviewer` 1). Tác tử chính luôn giao việc và gọi đủ ba vai trò, nhưng vẫn tự đọc lại các tệp mà explorer vừa đọc (code-learn: 4 `read_file` trên đúng các tệp nguồn sau hai lần giao việc khám phá; logs-learn: tự đọc README và `app.log` sau khi explorer báo cáo), tức một phần việc bị làm hai lần.
- Thông tin thiếu khi giao việc: data-learn là ví dụ rõ nhất. Lời giao cho `implementer` chỉ ghi "Write a Python script to compute all required values for workspace/answer.json ... following README.md and Acme reporting conventions", bỏ mất định nghĩa của đề (Q1 tính từ 2024-01-01 00:00 UTC đến 2024-03-31 23:59:59 UTC). Implementer báo "sum of valid order amounts in the North region for months 1, 2, and 3" và ra `north_q1_revenue = 3189.59`, `north_q1_orders = 13`, hai check kỹ thuật mà `baseline` đạt. `reviewer` cũng chỉ nhận lời giao "verify all calculations ... against the task prompt and README.md conventions" mà không có đề, nên báo "Verified" cho cả hai giá trị sai. Ngược lại, ở logs-learn lời giao thứ hai cho `implementer` chép đủ 7 quy tắc của đề. Lời giao việc nào cũng không thể chứa quy ước Acme vì chính tác tử chính không biết; `reviewer` báo PASS ở cả ba tác vụ trong khi 9/9 check quy ước trượt.
- Ảnh hưởng đến token và thời gian (tác vụ học, `subagents` so với `baseline`): data-learn 381.471 so với 166.713 token (2,3 lần), 188,9 so với 41,5 giây; logs-learn 456.038 so với 70.954 (6,4 lần), 206,1 so với 26,0 giây; code-learn 315.655 so với 593.074 (0,53 lần) vì lần chạy `baseline` lặp đến hết `recursion_limit`, còn `subagents` kết thúc bình thường và đạt 7/10 (cả 7 check kỹ thuật). Trung bình 384.388 so với 276.913 token cho cùng 16/18 check kỹ thuật và 0/9 check quy ước.
- Trên tác vụ đánh giá (sau `freeze`): `subagent_calls` data-eval 3, code-eval 5 (`explorer` 3, `implementer` 1, `reviewer` 1), logs-eval 6. Điểm 5/9, 6/11, 6/10 so với 5/9, 7/11, 6/10 của `baseline`; token trung bình 334.339 so với 125.637 (2,7 lần), thời gian trung bình 218,3 so với 51,9 giây. Check kỹ thuật duy nhất bị mất là `tests_not_modified` ở code-eval, lại do thông tin rơi khi giao việc: đề ghi "Do not modify the existing files in `tests/`", nhưng lời giao cho `implementer` chỉ ghi "fix `bookings/billing.py`, `bookings/schedule.py`, and `bookings/timeutil.py` ... and run pytest", và implementer báo "`tests/test_bookings.py`: Added comprehensive unit tests"; `reviewer` vẫn báo PASS.
- Ở `baseline`, tác tử chính dùng subagent mặc định trong đúng một lần chạy: code-learn gọi `general-purpose` 3 lần (`subagent_calls = 3`) trong lần chạy hết `recursion_limit`; 5/6 lần chạy `baseline` có `subagent_calls = 0`.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator: 2 (1 lần đầu, 1 lần chạy lại; còn 1 lần được phép nhưng không dùng). Số skill bị xóa: 2, cả hai từ lần chạy 1.
  - Lần 1 sinh `python-type-annotations-and-tests` (5 dòng thân) và `thorough-requirements-compliance` (4 dòng thân). Skill thứ nhất đúng hướng nhưng thiếu chính xác: không nêu tên tệp `tests/test_regressions.py`, số lượng tối thiểu 3, và định dạng `- fix(<function name>): ...` mà `detail` yêu cầu. Skill thứ hai chỉ là lời khuyên chung ("Read the instructions and all specific formatting rules ... multiple times", "Maintain a checklist of every explicit rule mentioned in the task description"); nó bỏ sót toàn bộ quy ước của data và logs, trong khi quy ước không nằm trong đề nên "đọc kỹ đề" không giúp được. Cả hai bị xóa vì kém chất lượng theo `05_skill_quality.md` (thiếu chính xác, không mệnh lệnh kiểm chứng được).
  - Trước lần chạy 2, prompt của curator (`CURATOR_PROMPT` trong `src/lab/curator.py`) được bổ sung hai quy tắc: phản hồi bắt đầu bằng "RULE:" là quy ước mà đề không nêu, phải được ghi chính xác và đầy đủ (tên tệp, khóa JSON, tiêu đề, định dạng, đơn vị, thứ tự); và nhóm quy ước theo loại công việc, mỗi loại một skill. Nội dung skill vẫn hoàn toàn do mô hình viết; không sửa tay tệp nào trong `skills/auto/`. Kết quả lần 2 được giữ:

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `python-bug-fixing-and-maintenance` | Tổng quát cho việc sửa một gói Python; chỉ nêu tên do quy ước yêu cầu (`tests/test_regressions.py`, `CHANGELOG.md`, `## Unreleased`), không nêu tên hàm hay tệp nguồn của code-learn. | Đúng: chép đủ 3 quy ước (type hint cho mọi hàm public; ít nhất 3 test hồi quy trong tệp mới; mục `- fix(<function name>): ...` dưới `## Unreleased`) và nhắc không sửa tệp có sẵn trong `tests/` (lỗi A ở mục 4). Dòng 1 ("Read all instructions ... thoroughly") là lời khuyên chung, thừa. | 6 dòng thân. `description`: "Use when fixing bugs, adding features, and maintaining Python packages with tests and documentation" (nêu đúng loại tác vụ rộng). Được đọc ở code-learn (`skills_read = 1`). |
| `tabular-data-analysis-and-export` | Phần lớn tổng quát, nhưng có chi tiết riêng của dữ liệu học: giá trị thiếu `-999` và chuẩn hóa "region names" (cột của `sales.csv`). | Đúng một phần: có khối `meta` (`source`, `rows_in`, `rows_used`), `clean.csv` với thời gian `YYYY-MM-DDTHH:MM:SSZ` và tiền bằng cent nguyên. Thiếu: không nêu tiêu đề `order_id,timestamp_utc,region,amount_cents` mà chỉ ghi "with the exact specified header order" (đề không nêu tiêu đề nào); quy ước cent của `answer.json` bị gộp vào câu về `clean.csv` nên mơ hồ. | 7 dòng thân. `description`: "Use when processing tabular data files, cleaning CSVs, and generating summary JSON reports". Được đọc ở data-learn (`skills_read = 1`). |
| `log-parsing-and-triage` | Tổng quát cho phân tích log thành JSON; chỉ nêu tên do quy ước (`schema_version`, `generated_by`) và ví dụ `payment-service` có trong `detail`. | Đúng: chép đủ 3 quy ước (tên service viết thường và đổi `-` thành `_`, sắp xếp theo service rồi `timestamp_utc`, `"schema_version": 2` và `"generated_by": "log-triage"`), kèm các quy tắc của đề (lọc ERROR/CRITICAL, `repeat_count`). | 7 dòng thân. `description`: "Use when parsing application logs, filtering error levels, aggregating metrics, and exporting JSON reports". Được đọc ở logs-learn (`skills_read = 1`). |

Kết quả Phần 3.4 (`results/skills-auto-dev`, chạy trước `freeze`): data-learn 6/8, code-learn 8/10 (`GraphRecursionError` ở 29 tool call), logs-learn 8/9; điểm trung bình tác vụ học 0,813 so với 0,597 của `baseline`. Mỗi tác vụ đọc đúng một skill phù hợp, không đọc skill của họ khác. Skill được làm theo một phần: logs-learn đạt sắp xếp và tiêu đề nhưng vẫn giữ `payment-service` (ví dụ trong đề nói khác skill); data-learn đạt `meta` nhưng vẫn ghi tiền bằng USD trong `answer.json` (câu trả lời cuối: "`north_q1_revenue` ... ($3,130.24)"; đề ghi "(number): sum of `amount`") và `rule_clean_csv` vẫn trượt (câu trả lời cuối chỉ liệt kê `answer.json` là tệp đã tạo; vết cắt mỗi lệnh ở 1500 ký tự nên không xác định được `clean.csv` có được ghi hay không); code-learn đạt `rule_regression_tests` nhưng hết `recursion_limit` trước khi thêm type hint và CHANGELOG.

## 7. Kết quả so sánh (Phần 4.3, 4.4)

`report/table.md` (`python -m lab.compare`):

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 5/10 | 7/10 | 9/10 |
| data-learn | 5/8 | 3/8 | 6/8 |
| logs-learn | 6/9 | 6/9 | 8/9 |
| code-eval | 7/11 | 6/11 | 10/11 |
| data-eval | 5/9 | 5/9 | 6/9 |
| logs-eval | 6/10 | 6/10 | 9/10 |
| **Mean score - learning tasks** | 0.60 | 0.58 | 0.85 |
| **Mean score - evaluation tasks** | 0.60 | 0.57 | 0.83 |
| **Mean tokens per run** | 201,275 | 359,363 | 141,695 |
| **Runs that read a skill** | 0/6 | 0/6 | 6/6 |

`python scripts/check_breakdown.py` (sau `freeze`):

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval     18/18         0/12         125,637      0/3
baseline      learn    16/18         0/9          276,913      0/3
subagents     eval     17/18         0/12         334,339      0/3
subagents     learn    16/18         0/9          384,388      0/3
skills-auto   eval     18/18         7/12         101,771      3/3
skills-auto   learn    18/18         5/9          181,620      3/3
```

`python scripts/verify_freeze.py` (chạy trong container Linux): `checked 6 runs of skill conditions: OK`. Không lần chạy nào có `skills_modified = true`.

Các lần chạy có `error` và cách xử lý:

- `baseline/code-learn`: `GraphRecursionError` (60 bước, 30 tool call, 593.074 token). Đây là hành vi của tác tử (lặp sửa test tự thêm, mục 4), nên được GIỮ làm kết quả chính thức; điểm chấm trên workspace tại thời điểm dừng.
- Hai lần chạy lỗi hạ tầng bị loại và chạy lại, bản gốc lưu trong `results/_failed/` (`lab.compare` và `check_breakdown` không đọc thư mục này):
  - `results/_failed/baseline/code-learn-1`: mô hình trả một tin nhắn rỗng sau 10 tool call nên đồ thị kết thúc với điểm 1/10 và `final_message` rỗng (lỗi phía API). Sau sự cố này `run_task` được bổ sung: lần chạy kết thúc bằng tin nhắn rỗng được ghi `error = "EmptyModelResponse ..."` và trường `finish_reason`.
  - `results/_failed/subagents/data-eval-1`: `GoogleRateLimitError ... 429 RESOURCE_EXHAUSTED` (hết quota 500 request/ngày của free tier giữa lần chạy). Chạy lại bằng khóa của một project khác, cùng mô hình `gemini-3.5-flash-lite`.
- Phần 3.4 (`results/skills-auto-dev/code-learn`, trước `freeze`): `GraphRecursionError` ở 29 tool call; chỉ dùng để ước lượng nhiễu (mục 8.6).

## 8. Phân tích

**1. Điều kiện nào cải thiện tác vụ học, tác vụ đánh giá?**
Điểm trung bình (3 chữ số, tính từ `run.json`): `baseline` 0,597 (học) và 0,597 (đánh giá); `subagents` 0,581 và 0,567; `skills-auto` 0,846 và 0,825. Chỉ `skills-auto` cải thiện, và cải thiện ở cả hai vai trò: +0,249 trên tác vụ học, +0,228 trên tác vụ đánh giá. `subagents` không cải thiện vai trò nào (−0,016 và −0,030, nhỏ hơn độ nhiễu ở câu 6). Không có điều kiện nào cải thiện tác vụ học mà không cải thiện tác vụ đánh giá, nên không thấy dấu hiệu quá khớp rõ rệt; mức cải thiện trên tác vụ đánh giá chỉ thấp hơn tác vụ học 0,021, nhỏ hơn chênh lệch do nhiễu (0,033). Lý do: phần lớn lợi ích đến từ các quy ước mà tác vụ đánh giá dùng lại nguyên vẹn.

**2. Check kỹ thuật và check quy ước.**
Check kỹ thuật: `baseline` 16/18 (học), 18/18 (đánh giá); `subagents` 16/18, 17/18; `skills-auto` 18/18, 18/18. Check quy ước: `baseline` 0/9, 0/12; `subagents` 0/9, 0/12; `skills-auto` 5/9, 7/12. Skill chủ yếu giúp nhóm check quy ước (+5 trên tác vụ học, +7 trên tác vụ đánh giá) và giúp thêm hai check kỹ thuật ở code-learn (`tests_not_modified`, `visible_suite_passes`), nhờ dòng "Never modify any original files located in the `tests/` directory" của skill code. Theo họ tác vụ, trên tác vụ đánh giá: code đạt cả 3 quy ước dùng lại, logs đạt cả 3, data chỉ đạt 1/3 (`rule_meta_block`). Ba quy ước MỚI (`rule_sorted_keys_format` ở data-eval, `rule_version_bump` ở code-eval, `rule_source_line` ở logs-eval) trượt ở cả ba điều kiện (0/3 mỗi điều kiện): curator chỉ thấy phản hồi của tác vụ học nên skill không thể chứa quy ước chỉ xuất hiện ở tác vụ đánh giá, và đề không nêu chúng.

**3. Một check skill giúp đạt, một check skill không giúp.**
- Giúp: `rule_changelog` ở code-eval (`baseline` trượt, `skills-auto` đạt). `skills_read = 1`: tác tử đọc `skills/python-bug-fixing-and-maintenance/SKILL.md`, có dòng "Record each bug fix in `CHANGELOG.md` under the heading `## Unreleased` as a bullet point in the format `- fix(<function name>): <short description>`". Vết cho thấy tác tử ghi đúng dạng đó: "## Unreleased\n- fix(parse_duration): support all documented duration formats ...". Tương tự, `rule_type_hints` và `rule_regression_tests` cũng chuyển từ trượt sang đạt.
- Không giúp, dù đã đọc: `rule_money_in_cents` ở data-learn và data-eval. Skill `tabular-data-analysis-and-export` được đọc ở cả hai lần chạy, nhưng quy ước cent chỉ nằm trong câu về `clean.csv` ("and monetary values in integer cents"), còn đề ghi rõ `march_revenue_utc` "(number): sum of `total`". Tác tử theo đề: câu trả lời cuối ở data-eval báo "total revenue of **52,957.19**" (đơn vị USD). Đây là kiểu "đọc nhưng không làm theo" khi skill mơ hồ và mâu thuẫn với đề.
- Đối chứng cùng một quy tắc: `rule_service_names` trượt ở logs-learn (cả Phần 3.4 lẫn sau `freeze`) nhưng đạt ở logs-eval, dù cùng một skill. Ví dụ JSON trong đề logs-learn dùng `"service": "payment-service"` (mâu thuẫn với skill) nên tác tử chép theo ví dụ; ví dụ trong đề logs-eval dùng `"service": "mailer"` (không có dấu `-`, không mâu thuẫn) nên tác tử làm theo skill. Khi đề và skill nói khác nhau, đề thắng.

**4. Chi phí.**
Token trung bình mỗi lần chạy: `baseline` 201.275, `subagents` 359.363 (1,79 lần `baseline`), `skills-auto` 141.695 (0,70 lần). Riêng tác vụ đánh giá: 125.637, 334.339 (2,66 lần), 101.771 (0,81 lần). Điểm trên 100k token (điểm trung bình 6 tác vụ chia token trung bình): `baseline` 0,30, `subagents` 0,16, `skills-auto` 0,59. `skills-auto` hiệu quả nhất: điểm cao hơn mà token ít hơn, vì tác tử biết định dạng đích từ đầu (data-eval: 58.116 so với 169.645 token); một phần chênh lệch trên tác vụ học đến từ lần chạy `baseline` code-learn lặp đến giới hạn (593.074 token), nhưng trên tác vụ đánh giá (không có ngoại lệ đó) `skills-auto` vẫn ít hơn 19%. Đa tác tử KHÔNG đáng chi phí trong thí nghiệm này: điểm bằng hoặc thấp hơn `baseline`, tốn 1,8 đến 2,7 lần token và khoảng 4 lần thời gian (218 so với 52 giây trên tác vụ đánh giá), và cả ba check kỹ thuật bị mất (hai ở data-learn, một ở code-eval) đều do lời giao việc làm rơi một ràng buộc của đề (mục 5).

**5. Rò rỉ dữ liệu và quá khớp.**
Không thấy rò rỉ: mọi skill qua `validate_skill` (không chứa định danh nào trong `eval_markers()`); `curate_skills` bỏ qua mọi `run.json` có `role != "learn"` (kiểm bởi `test_04`); skill được đóng băng bằng tag `freeze` trước mọi lần chạy đánh giá và không bị sửa tay. Có dấu hiệu quá khớp nhẹ ở skill dữ liệu: nó nhắc giá trị thiếu `-999` và chuẩn hóa "region names" của `sales.csv`. Ở data-eval giá trị thiếu là `-1` và tác tử vẫn xử lý đúng (`missing_total_orders` đạt), nên chi tiết này không gây hại quan sát được. Một nguồn thiên lệch khác do người làm thí nghiệm: prompt của curator được sửa một lần sau khi đọc skill lần 1 (mục 6); việc sửa dựa trên phản hồi tác vụ học và diễn ra trước `freeze`. Trong lúc chuẩn bị, danh sách tên tệp của repo (gồm tên tệp trong `tasks/*-eval/workspace`) có hiện ra khi liệt kê thư mục, nhưng nội dung đề, dữ liệu và `check.py` của tác vụ đánh giá không được mở trước `freeze`, và không skill nào nhắc tới các tên đó.

**6. Nhiễu.**
Cùng bộ skill đóng băng, cùng tác vụ học: Phần 3.4 (`results/skills-auto-dev`) đạt 6/8, 8/10, 8/9 (trung bình 0,813); sau `freeze` đạt 6/8, 9/10, 8/9 (0,846). Chênh lệch +0,033, do đúng một check (`rule_changelog` ở code-learn: lần Phần 3.4 hết `recursion_limit` trước khi sửa CHANGELOG). Token của cùng tác vụ dao động mạnh hơn điểm (data-learn 222.840 so với 286.940, +29%; logs-learn 96.790 so với 67.535, −30%). `baseline` code-learn cho 1/10 (lỗi API) rồi 5/10 ở hai lần thử. Do đó chênh lệch cỡ một check (khoảng 0,03 đến 0,1 trên một tác vụ) nằm trong nhiễu: khác biệt giữa `subagents` và `baseline` (−0,02 đến −0,03) không có ý nghĩa, còn khác biệt của `skills-auto` (+0,23 đến +0,25, tương ứng 5 đến 7 check quy ước trên mỗi vai trò) lớn hơn nhiều lần mức nhiễu này. Phụ lục (thử thách 6e) đo thêm độ dao động trên tác vụ đánh giá.

**Đối chiếu giả thuyết (mục 2).**
- H1 được ủng hộ: `subagents` thấp hơn `baseline` 0,030 trên tác vụ đánh giá (trong khoảng ±0,10) và tốn 2,66 lần token (≥ 1,3).
- H2 được ủng hộ: `skills-auto` cao nhất (0,825), hơn `baseline` 0,228 (trong khoảng 0,10 đến 0,25), và không đạt tối đa.
- H3 chỉ được ủng hộ một phần: đúng là cả ba quy ước mới trượt ở mọi điều kiện; nhưng mức cải thiện trên tác vụ đánh giá (+0,228) chỉ nhỏ hơn mức trên tác vụ học sau `freeze` (+0,249) có 0,021, nhỏ hơn nhiễu, và còn lớn hơn mức dự đoán dựa trên Phần 3.4 (+0,216). Không thấy sự suy giảm chuyển giao mà SkillEvolBench mô tả, vì tác vụ đánh giá ở đây dùng lại nguyên các quy ước đã học.

## 9. Hạn chế và tính hợp lệ

1. **Mẫu nhỏ, mỗi cấu hình chạy một lần (bảng chính).** Chỉ 3 tác vụ mỗi vai trò, mỗi tác vụ 8 đến 11 check, nên một check đổi kết quả làm điểm tác vụ đổi 0,09 đến 0,125. Ảnh hưởng: chỉ kết luận được các hiệu ứng lớn (`skills-auto` +0,23 đến +0,25); không kết luận được `subagents` tốt hơn hay kém hơn `baseline` (chênh −0,02 đến −0,03), cũng như không khẳng định được mức chuyển giao từ tác vụ học sang tác vụ đánh giá thấp hơn (0,021 < nhiễu 0,033). Thử thách 6e (Phụ lục) chỉ lặp lại tác vụ đánh giá.
2. **Nhiễu và độ ổn định của mô hình.** `gemini-3.5-flash-lite` bỏ qua `temperature = 0`; cùng bộ skill cho 0,813 và 0,846 trên tác vụ học; token cùng tác vụ dao động ±30%; một lần chạy kết thúc bằng tin nhắn rỗng (lỗi API) và code-learn chạm `recursion_limit = 60` ở 2/3 lần chạy hoàn chỉnh không dùng điều kiện `subagents` (`baseline`, `skills-auto` Phần 3.4; lần sau `freeze` thì không). Ảnh hưởng: điểm code-learn phụ thuộc vào ngân sách bước, một phần chênh lệch ở họ code có thể do tác tử kịp hay không kịp làm hết trước giới hạn chứ không chỉ do skill.
3. **Tác vụ do giảng viên thiết kế với quy ước ẩn.** 21/21 check quy ước (tác vụ học và đánh giá của `baseline`) chỉ biết được qua phản hồi, trong khi check kỹ thuật gần như luôn đạt. Ảnh hưởng: lợi ích lớn của `skills-auto` ở đây chủ yếu là "truyền đạt quy tắc", không phải cải thiện suy luận; không suy ra được skill tự sinh có lợi khi lỗi chủ yếu là lỗi suy luận (SkillsBench: skill tự sinh trung bình không có lợi). Quy ước mới của tác vụ đánh giá luôn trượt cho thấy giới hạn này.
4. **Một mô hình, quota free tier.** Mọi kết luận chỉ cho `gemini-3.5-flash-lite`; hai khóa API thuộc hai project khác nhau (do hết quota 500 request/ngày) nhưng cùng mô hình, không có lý do để kết quả khác nhau. Ảnh hưởng: với mô hình mạnh hơn, đa tác tử có thể giao việc tốt hơn và kết luận về `subagents` có thể đổi.
5. **Bậc tự do của người làm thí nghiệm.** Prompt curator được sửa một lần sau khi đọc skill lần 1, và thiết kế subagent do nhóm chọn. Ảnh hưởng: chất lượng skill phản ánh một phần prompt của người làm thí nghiệm; một curator "ngây thơ" (lần 1) cho skill chung chung và nhiều khả năng không cải thiện được điểm.
6. **Đo đạc và môi trường.** `trace.md` chỉ có luồng chính và cắt mỗi mục ở 1500 ký tự, nên không thấy việc bên trong subagent và một số lệnh dài; các nhận định về subagent dựa trên lời giao việc và báo cáo cuối. Một số lần chạy tác vụ học (subagents, baseline code-learn lần chạy lại, Phần 3.4) có thư mục `__pycache__` do test ngoại tuyến trên máy chủ sinh ra trong `tasks/*/workspace`, bị sao chép vào sandbox; chúng không thuộc check nào và đã được dọn trước các lần chạy chính thức sau `freeze`.

## 10. Kết luận

Skill do curator tự sinh từ phản hồi tác vụ học (`skills-auto`) là điều kiện duy nhất cải thiện điểm: +0,25 trên tác vụ học và +0,23 trên tác vụ đánh giá, với ít token hơn `baseline` 30%, nhờ chép lại các quy ước Acme mà đề không nêu. Lợi ích chuyển sang tác vụ đánh giá vì quy ước được dùng lại, nhưng dừng ở đó: ba quy ước mới của tác vụ đánh giá trượt ở mọi điều kiện, và quy ước nào mâu thuẫn với đề hoặc được viết mơ hồ thì tác tử theo đề. Đa tác tử (`subagents`) không cải thiện điểm, tốn 1,8 đến 2,7 lần token và 4 lần thời gian, và làm mất ba check kỹ thuật vì lời giao việc bỏ sót ràng buộc của đề. Các khác biệt cỡ một check nằm trong nhiễu (0,033 giữa hai lần chạy cùng bộ skill). Đề xuất tiếp theo: cho curator kiểm tra từng skill bằng cách đối chiếu với `detail` (mọi quy ước có đủ tên, định dạng, đơn vị) và nêu rõ thứ tự ưu tiên khi skill khác ví dụ trong đề, đồng thời bắt coordinator chép nguyên văn đề vào mọi lời giao việc.

## Phụ lục

**Lệnh đã chạy (theo thứ tự).** Môi trường: `pip install -e .` trong `.venv`; `docker build -t lab-deepagents .` và một image phụ `lab-deepagents-git` (thêm `git` để chạy `verify_freeze.py` trong container). Repo được checkout với `core.autocrlf=false` để tệp trên đĩa là LF như trên máy chấm. Mọi lệnh `lab.runner`/`lab.curator` chạy dạng `docker run --rm -v <repo>:/lab lab-deepagents-git <lệnh>`, mỗi lần một tác vụ, dừng ngay khi gặp lỗi quota.

```bash
pytest tests                                                   # 29 passed (Windows và Docker)
python scripts/tour.py
python -m lab.runner --condition baseline  --tasks data-learn code-learn logs-learn
python -m lab.runner --condition subagents --tasks data-learn code-learn logs-learn
python -m lab.runner --condition baseline  --tasks code-learn  # chạy lại sau EmptyModelResponse (bản lỗi: results/_failed)
python -m lab.curator                                          # lần 1: 2 skill, cả hai bị xóa (mục 6)
python -m lab.curator                                          # lần 2 (prompt bổ sung): 3 skill, giữ
python -m lab.runner --condition skills-auto --tasks data-learn code-learn logs-learn
mv results/skills-auto results/skills-auto-dev
git commit -m "hypotheses: H1-H3 before any evaluation run"    # 04d6acf
git commit --allow-empty -m "freeze skills" && git tag freeze  # 82e72bc
python -m lab.runner --condition baseline  --tasks data-eval code-eval logs-eval
python -m lab.runner --condition subagents --tasks data-eval code-eval logs-eval  # data-eval chạy lại sau 429 (khóa mới)
python -m lab.runner --condition skills-auto --tasks data-learn code-learn logs-learn data-eval code-eval logs-eval
python scripts/verify_freeze.py                                # OK, 6 runs
python -m lab.compare > report/table.md
python scripts/check_breakdown.py
```

**Số lần chạy tác vụ đã dùng:** 24 cho thí nghiệm chính: 18 lần chạy chính thức, 3 lần ở Phần 3.4, 2 lần lỗi hạ tầng đã loại (`results/_failed/`), và 1 lần chạy `baseline` data-learn đầu tiên trên Windows (Git Bash) bị thay bằng lần chạy trong Docker. Ngoài ra có 2 lần gọi curator. Không có ngân sách cố định; giới hạn thực tế là quota free tier (500 request/ngày mỗi project), đã dùng hết quota của hai khóa thuộc hai project.

**Thử thách mở rộng 6e (lặp để đo nhiễu): chưa hoàn thành.** Thiết kế: chạy lại mỗi điều kiện trên 3 tác vụ đánh giá thêm 2 lần, ghi vào `results-6e/r2` và `results-6e/r3` (tách khỏi `results/`); lần lặp 2 chạy đủ ba điều kiện trước khi sang lần lặp 3. Đã có: `baseline` lặp 2 cho data-eval 5/9, code-eval 7/11, logs-eval 6/10, giống hệt bảng chính về điểm, trong khi token khác nhiều (67.562 so với 169.645; 108.953 so với 127.776; 147.685 so với 79.490). Lần lặp 2 của `subagents` data-eval tiêu tốn 1.464.070 token trong 561,8 giây (7 lần giao việc) rồi dừng vì hết quota ngày của khóa thứ hai (`results-6e/_failed/r2/subagents/data-eval-1`). Còn thiếu 14 lần chạy (lần lặp 2: `subagents` 3 và `skills-auto` 3; lần lặp 3: 9).

**Ghi chú khác.**

- `run_task` dùng `agent.stream(..., stream_mode="values")` thay cho `invoke` (mở rộng tùy chọn ở `03_runner.md`, mục 8), nên lần chạy lỗi vẫn có vết và số tool call; ngoài các khóa bắt buộc, `run.json` có thêm `finish_reason`.
- `make_backend` trên Windows chạy lệnh của tác tử qua Git Bash (vì `LocalShellBackend` dùng `cmd.exe`), với môi trường tối thiểu không có khóa API; trên Linux là đúng `LocalShellBackend` theo pseudo-code. Mọi lần chạy trong báo cáo (trừ lần đầu đã bị thay) dùng Linux trong Docker.
- `scripts/verify_freeze.py` lỗi giải mã cp1252 khi chạy trên Windows vì `REPORT.md` có tiếng Việt (`git show` với `text=True`); chạy với `PYTHONUTF8=1` hoặc trong container Linux thì báo OK.
