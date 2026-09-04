# RACI — ai được quyết gate nào (workspace AWS v2 · phương án A)

> Đặt tại `<workspace>/.ai-dlc/governance/raci.md`. Engine AWS v2 chỉ kiểm "có người tại gate", **không kiểm ai** —
> `tower_approve.ts` và tower đọc file này để (1) chỉ hiện thẻ *Cần tôi quyết* cho đúng người, (2) từ chối bấm sai vai.
> Cột **gate** = slug stage (`intent-capture`, `units-generation`, `code-generation`…) hoặc glob (`*`, `units-*`).
> Cột **quyết** = email git (hoặc tên) — dòng đầu khớp thắng, `*` là mặc định. Cột **kiểm** (tuỳ chọn) = người soát trước
> khi người quyết bấm (Tester, tech lead) — hiện thẻ *Cần tôi kiểm*. Vai không có người ⇒ ghi Lead, không để trống.
> Không thêm điểm dừng: file này chỉ điền TÊN vào gate đã có của engine.

| gate | quyết | kiểm |
|---|---|---|
| intent-capture | pm@example.com | — |
| requirements-analysis | pm@example.com | apo@example.com |
| user-stories | pm@example.com | tester@example.com |
| units-generation | lead@example.com | tester@example.com |
| delivery-planning | lead@example.com | — |
| code-generation | lead@example.com | dev2@example.com |
| build-and-test | lead@example.com | tester@example.com |
| * | lead@example.com | — |
