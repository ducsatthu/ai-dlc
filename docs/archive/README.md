# docs/archive — tài liệu v1 (mô hình bảy gate chặn)

Các file ở đây mô tả AI-DLC theo **bản v1**: bảy gate A–G chặn cứng, Review Board 17 agent, người duyệt bằng markdown toàn văn. Bản này đã bị thay bởi **white paper v2 — Human-Lead** (`../whitepaper-ai-dlc-vi.md`, 2026-08-21). Giữ lại để truy vết dòng dõi và để đối chứng KPI v1/v2, **không còn là SSOT** và không dùng để giải quyết mâu thuẫn.

| File | Là gì | Vì sao không còn là chuẩn |
|---|---|---|
| `whitepaper-ai-dlc-vi-v1.md` | Bản dịch nội bộ white paper AWS (Raja SP), biên tập 2026-08-09 | Phần nguyên tắc và framework được kế thừa vào v2; phần "con người xác nhận ở mọi điểm phân rã" và bộ prompt "chờ tôi phê duyệt rồi mới làm" là thứ v2 thay |
| `plugin-plan-v1.md` | Kế hoạch đóng gói plugin 2026-08-11 | Kiến trúc gói (override 3 lớp, workspace map, inbox, contribute, semver) vẫn đúng; phần gate/Review Board đã lỗi thời. Kế hoạch chuyển đổi: `../plugin-transition-plan.md` |
| `agent-team-blueprint-v1.html` | Blueprint agent team v3 + "Bảy điểm dừng bắt buộc" | Mô hình gác cổng; vẫn là nguồn token CSS cho `Control Tower Design System/` |
| `simulation-phase2-pilot-v1.html` | Dry-run PILOT Phase 2 qua 7 gate | Minh hoạ cho mô hình cũ; dữ liệu mẫu vẫn được design system tham chiếu |

`control-tower-design-prompt.md` (design prompt cho UI tower 5 màn, gate-centric) đã **gỡ khỏi repo** theo quyết định chủ gói 2026-08-21 — xem git history (`fc42411` trở về trước) nếu cần.
