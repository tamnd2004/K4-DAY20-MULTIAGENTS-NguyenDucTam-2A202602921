# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| | | |

- Mô hình (tên deployment hoặc `LAB_MODEL`), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`:
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker:
- Số lần chạy tác vụ đã dùng / ngân sách:
- Commit của tag `freeze`:

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

> Dự đoán điều kiện nào đạt điểm cao nhất trên **tác vụ đánh giá** và vì sao. Nêu căn cứ từ phân loại lỗi (mục 4) và từ tài liệu tham khảo. Điền cả ba dòng; `verify_freeze.py` kiểm tra điều này.

- H1 (subagents so với baseline):
- H2 (skills-auto so với baseline):
- H3 (tác vụ học so với tác vụ đánh giá):

## 3. Làm quen Deep Agents (Phần 0.3)

Nguồn: `python scripts/tour.py` (mô hình giả, 0 token), mã `src/lab/agent.py` và `src/lab/subagents.py`, lần chạy `results/baseline/data-learn` (`gemini-3.5-flash-lite`). Ba câu hỏi Phần 0.3 của GUIDE (công cụ mặc định, subagent `general-purpose`, câu trích từ mô tả `task` và `execute`) được trả lời trong câu 2 và câu 3.

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

Có worker không có nghĩa là worker được dùng: ở lần chạy `baseline` của `data-learn`, `subagent_calls = 0`, tác tử chính tự làm hết bằng 18 tool call.

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
- `execute`: "You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search. Use read_file rather than cat/head/tail." Mô tả này còn khuyên "Use absolute paths and avoid `cd`", trái với quy ước đường dẫn tương đối của lab; vì vậy `BASE_PROMPT` nêu rõ `PATHS_NOTE`. Trong lần chạy `data-learn`, tác tử vẫn dùng `execute` (`python3 -c ...`) cho cả việc đọc dữ liệu: 15/18 tool call là `execute`, chỉ 1 lần `read_file`.

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

> Chỉ dùng tác vụ học. Mỗi dòng là một check thất bại.

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| | | | |

Nhận xét: nhóm lỗi nào chiếm đa số? Skill có thể phòng ngừa nhóm đó không?

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa (tên, vai trò, lý do thiết kế):
- `subagent_calls` ở từng tác vụ và nhận xét (kể cả trường hợp bằng 0):
- Thông tin thiếu hoặc thừa khi giao việc (nếu có giao việc):
- Ảnh hưởng đến token và thời gian:

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do:

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| | | | |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
