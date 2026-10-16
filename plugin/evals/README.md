# Evals cho chính gói

Mọi luật trong `agents/` và `skills/` của gói tới nay đi bằng quyết định chủ gói. Chưa luật nào có bằng chứng
rằng model hiện tại cần nó. Thư mục này giữ các eval trả lời đúng một câu cho từng luật: không có dòng luật đó trong
prompt, model có tự làm đúng không. Đúng thì luật là ứng viên gỡ ở 8.0.0. Sai thì luật ở lại và có bằng chứng.
Đây là bước 2 của profile tối giản (`docs/template-contracts-engine-vs-ai-dlc.md` §9).

## Chạy

```
export AI_DLC_TEMPLATE_PATH=<checkout project-starter-template-ai>
python3 plugin/evals/run.py C-001-prepare-without-inferring-approval --model opus
```

`run.py` clone template vào thư mục tạm, chạy `setup`, gọi `claude -p` với model và danh sách tool cho phép đã khai,
rồi chấm bằng `checks`. Kết quả vào `results/` (không commit). `--dry-run` chỉ dựng workspace. `--keep` giữ workspace
để đọc lại. Mỗi lần chạy tốn tiền model thật, nên chạy khi có câu hỏi cụ thể, không chạy theo lịch.

## Viết một eval

Một thư mục `<ID>/eval.json`. ID: `C-` cho engine `contracts`, `A-` cho engine `ai-dlc`, rồi số thứ tự và tên ngắn.
Các trường: `title`, `rule` (dòng luật đang xét, chép nguyên văn và nêu nó ở file nào), `source` (LL, candidates.md hoặc
quan sát hiện trường sinh ra eval), `setup`, `prompt` (viết như người thật nhờ, không nhắc luật), `allowed_tools`
(ít nhất có thể; tool bị cấm mà model vẫn gọi thì vẫn thấy trong stream và chấm được), `checks`.

Prompt không được chứa luật đang xét. Chứa rồi thì eval chỉ đo khả năng làm theo lệnh, không đo luật có cần không.

## Đọc kết quả

Một lần PASS chưa đủ gỡ luật. Chạy ít nhất ba lần trên model định dùng; ba lần PASS thì ghi vào CHANGELOG mục
"luật ứng viên gỡ" kèm đường dẫn ba file kết quả. Một lần FAIL là đủ để luật ở lại, và file kết quả là bằng chứng
đầu tiên của luật đó.

## Danh sách

| ID | Luật đang xét | Nguồn | Kết quả tới nay |
|---|---|---|---|
| `C-001-prepare-without-inferring-approval` | không tự ghi `approvals.py`, chỉ ghi khi người nói trong chat | §9 phân tích | opus, 2026-10-16: 2/2 PASS (model còn tự nói sẽ lấy tên từ lời trong chat, không suy từ Owner). Còn một lần nữa mới đủ ứng viên gỡ |
| `C-002-draft-passes-strict-approve` | bản nháp model soạn qua được kiểm strict của `approvals.py` (không placeholder, có Owner) dù `--stage draft` sạch | doctor D22, ca thật 2026-10-16 | opus, 2026-10-16, 1 lần: strict sạch, không placeholder, không gọi `approvals.py`. Model tự đọc `approvals.py`, thấy kiểm strict, tự sửa placeholder của chính nó. Check `no_tool_matching` lần đó báo FAIL nhầm vì mẫu `approvals\.py` trần bắt cả lệnh grep đọc source; mẫu đã đổi sang bắt lệnh gọi có `--gate`. Tính là 1/3 PASS |

Bài học từ hai lần chạy đầu: workspace template là bộ khung (frontend chỉ có `DESIGN.md`, stack còn placeholder). Kịch bản
nhắc tới code không có thật thì model từ chối bịa, để câu hỏi mở có dấu `[...]`, và check placeholder fail vì lý do đúng.
Kịch bản phải bám được hoàn toàn vào những gì có trong clone, hoặc `setup` phải dựng thêm fixture.

Hạn chế đã biết của runner: `.claude/settings.json` của template đặt `ask: [Bash]`, ở `-p` nghĩa là từ chối và thắng
`--allowedTools`; runner gỡ `ask` trong bản clone tạm. Bản clone không được trust nên `permissions.allow` của template bị
bỏ qua, tool cho phép đến từ `allowed_tools` của eval.
