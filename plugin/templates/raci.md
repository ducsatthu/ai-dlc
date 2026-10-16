# RACI: ai được quyết gate nào (gói ai-dlc, engine `contracts`, 7.0.0-a)

Đặt tại `<workspace>/.ai-dlc/governance/raci.md`.

Engine của đội (`approvals.py`) ghi tên người vào `approvals.json` nhưng không kiểm ai được quyết gate nào. File này là chỗ đội khai điều đó. Tower (lát sau) dùng nó để chỉ hiện thẻ "cần tôi quyết" cho đúng người. Doctor dùng nó để đối chiếu `by:` trong `approvals.json` với cột quyết. Gói không gọi `approvals.py` thay ai.

Cột gate là gate của engine `contracts`: `intent`, `plan`, `contract` (Intent và Plan một lần, cho bugfix và refactor), `outcome`, hoặc `*`. Cột quyết là tên đúng như sẽ ghi `--by` (hoặc email git); dòng đầu khớp thắng. Cột kiểm (tuỳ chọn) là người soát trước khi người quyết nói approve, ví dụ Tester hay tech lead. Vai không có người thì ghi Lead, không để trống. File này không thêm điểm dừng, chỉ điền tên vào gate đã có của engine.

Bản 6.3.0 cho engine AWS v2 (cột gate là slug stage) nằm ở `docs/archive/aws-v2/`.

| gate | quyết | kiểm |
|---|---|---|
| intent | pm@example.com | |
| plan | lead@example.com | tester@example.com |
| contract | lead@example.com | |
| outcome | lead@example.com | tester@example.com |
| * | lead@example.com | |
