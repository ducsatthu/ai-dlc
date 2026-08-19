# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Repo **plugin `ai-dlc`** (kiêm marketplace — 1 repo duy nhất): đóng gói phương pháp **AI-DLC** (AI-Driven Development Lifecycle, theo white paper AWS) thành Claude Code plugin cài được, có Control Tower, override per project và learning loop qua retro. **Status: EXPERIMENTAL.**

- **Tài liệu chuẩn (SSOT) của phương pháp**: `docs/whitepaper-ai-dlc-vi.md` — mọi mâu thuẫn giữa tài liệu giải quyết theo file này.
- **Phân cấp**: Project → Intent → Unit → Bolt → Task. Một Unit chạy qua một hoặc nhiều Bolt (song song/tuần tự); mỗi Bolt: Domain Design → Logical Design + ADR → Code + Unit Test.
- **Nguyên tắc**: AI đề xuất trước — con người xác nhận trước khi đi tiếp. Gates A–G, không agent nào được vượt.
- **Handoff (§9)**: mọi lần spawn agent phải có `context-memory/handoffs/HOF-NNNN.md`; prompt spawn chỉ trỏ tới file. Agent nhận việc phải đặt `status: accepted` ngay và cập nhật `heartbeat`/`progress` ở mỗi mốc (§9.4) — không làm thì Control Tower mù. `session/board.md` sinh ra từ `handoffs/` — không sửa tay. Vào lại dự án bằng `/dlc-resume`.
- **Tower LIVE**: `/dlc-tower serve` tự sinh lại khi `.ai-dlc/` đổi, UI poll `/state` mỗi 5s; panel *Hoạt động gần đây* quét mtime nên vẫn thấy agent kể cả khi nó quên khai báo HOF.
- **Ngân sách context (§10)**: đọc frontmatter trước, tra qua `session/INDEX.md`, mở đúng mục — không nạp toàn văn intent-plan/unit-plan/as-is.
- **Ba luật v2 (chống sai từ gốc)**: stage 1 sinh `intent-plan.md` (Intent + Source Reading Plan + Provisional Unit Map, duyệt toàn văn tại Gate A) · **No-unread-source** (§4.8: mọi nguồn phải có trạng thái cuối + evidence trong `source-ledger.md`; còn `planned` là chặn Gate B/D) · **Unit = một phiên · tự ra được sản phẩm** (§4.9 **v5** — trần 5h ĐÃ BỎ ở 5.0.0: cắt theo `releasable` + `session_fit` có con số, không theo đồng hồ; `estimate_hours` vẫn cần breakdown nhưng không còn ngưỡng; trần giờ thành núm dự án `governance/sizing.md`. Mỗi Unit vẫn đủ User Story · NFR · Rủi ro). Gate duyệt bằng tài liệu markdown đọc toàn văn trên Control Tower — approve mù bị chặn ở cả UI lẫn server.
- **Open questions tách theo người trả lời (§4.10, v3)**: `open-questions-business.md` (gate_doc của C, viết bằng lời, cấm thuật ngữ code) và `open-questions-tech.md` (câu `CHẶN UOW-NN` chặn Gate D). Mỗi câu: một quyết định · một người cụ thể · phương án chọn sẵn kèm giá · mặc định nếu im lặng · **dòng "đã soát nguồn nào mà không thấy đáp án"** (§4.10.9 — thiếu là chưa đủ điều kiện gửi). Quyết định chạm cả hai phía → cặp mã `OQB-NN` ↔ `OQT-NN`.
- **Luật kiểm được (v4, từ retro thật `LL-001`/`LL-002` — Gate G DEC-0027)**: §4.12 Unit chỉ `done` khi có `rv:` trỏ RV **tồn tại thật** hoặc `review_waived_by: DEC` (ca gốc: 13 review-request, 0 verdict, 17 unit vẫn đóng) · §4.13 phát hiện ngoài phạm vi vào `escalations/`, không nằm chết trong HOF · §4.14 unit lỗi thời vào `units/_trash/` + `TOMBSTONE.md`, **không xoá**, mọi thống kê bỏ qua `_*` · §4.15 phép đo phải có ca đối chứng + mutation test · §4.16 thu hẹp union ⇒ grep mọi so sánh bằng. Nguyên tắc chung: **luật không kiểm được là luật sẽ trượt**, nên mỗi luật mới đều có một trường để điền và một KPI để đối chiếu (`units.reviewed`, `units.artifacts`).
- **Nhịp sống kiểm chéo được (v4.1, §9.4)**: `heartbeat:` là *lời khai*, mtime của chính file HOF là *dấu vết* — tower so hai cái và gắn cờ `placeholder`/`future`/`drift`/`unreadable`, bị cờ thì **thôi hiện "im lặng N phút"**. KPI `handoffHealth.trusted/accepted`. Ca gốc: PCT `HOF-0039` ghi file lúc 18:13 mà khai `heartbeat: …T00:00:00Z` → bảng báo "im lặng 1099 phút" cho agent đang chạy.
- **Teammate (v4.1, §9.5 — hướng dẫn, chưa qua Gate G nên doctor chỉ WARN)**: mặc định sub-agent; teammate (phiên Claude riêng, agent team) chỉ cho việc cần hỏi đi hỏi lại hoặc cần bẻ lái giữa chừng. Teammate **không** thay HOF (hộp thư team mất khi phiên kết thúc), đặt tên `<vai>-<mã việc>` + khai `teammate:` trong HOF, và tin nhắn giữa agent **không** đóng được gate — chỉ RV/DEC mới đóng. Bật bằng `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` + `teammateMode`; muốn thấy pane thì chạy claude trong tmux.
- **Không dựng bù hồ sơ**: thiếu bolt/evidence thì ghi khoảng trống vào LL. Design viết ngược từ code đã chạy là mô tả code đội lốt quyết định thiết kế — hồ sơ trống trung thực hơn hồ sơ dựng lại.

## Cấu trúc

| Đường dẫn | Nội dung |
|---|---|
| `.claude-plugin/marketplace.json` | Marketplace trỏ `./plugin` |
| `plugin/` | Gói chính: 18 agents (`agents/`), 16 skills `dlc-*` (`skills/`), 8 checklists có version (`skills/checklists/`), templates, hooks (SessionStart + PreToolUse gate guard), scripts (`tower_generate` · `tower_serve` · `session_brief`), `MIGRATION.md` |
| `plugin/references/protocol.md` | **Giao thức chung — mọi agent/skill tuân theo** (gates, layout `.ai-dlc/`, format MSG/RV/DEC/LL, binding rules, model tiers) |
| `docs/` | White paper, blueprint HTML, plugin plan, dry-run PCT, design prompt Control Tower |

## Commands (khi plugin đã cài)

```
claude plugin marketplace add <path-repo-này>   # hoặc org/ai-dlc trên GitHub
claude plugin install ai-dlc@ai-dlc
/dlc-init → /dlc-intent "..." → /dlc-discover → /dlc-validate → /dlc-units → /dlc-bolt → /dlc-accept → /dlc-retro
/dlc-resume (vào lại dự án ở phiên mới) · /dlc-revise (khi tower gửi "yêu cầu chỉnh sửa") · /dlc-status · /dlc-tower [serve] · /dlc-map · /dlc-tasks · /dlc-doctor · /dlc-contribute
```

Test scripts: `python3 -m py_compile plugin/scripts/*.py plugin/hooks/*.py` · `bash -n plugin/hooks/session_start.sh`.

## Quy ước khi sửa gói

- Sửa checklist/luật trong plugin **phải** đi từ một LL (lesson learned) đã qua Gate G của dự án thật — CHANGELOG entry bắt buộc link LL. Không sửa chay. *(Nợ `LL-PENDING` của 2.0.0–3.1.0 đã trả ở **4.0.0**: retro INT-001 của PCT — `LL-001` + `LL-002`, Gate G · DEC-0027. `LL-003` chưa qua Gate G nên phần áp từ nó chỉ là chẩn đoán, không phải luật chặn gate. **4.1.0** đi từ quan sát hiện trường INT-003 (`HOF-0039`, 13/08), chưa có LL: phần §9.4 là siết luật đã có nên kiểm mức FIX, phần §9.5 teammate chỉ WARN — phải trả bằng `LL-004` ở retro INT-003 hoặc gỡ. **5.0.0** bỏ trần 5h/Unit theo quyết định chủ gói — căn cứ: white paper không có trần đó (SSOT nói "giờ hoặc ngày"), `MIGRATION.md` v2 đã treo sẵn câu hỏi, và `DEC-0052` của PCT tách unit chỉ để lọt trần. Vẫn nợ một LL.)*
- Command mới phải prefix `dlc-`. Checklist có `version` trong frontmatter + changelog trong file.
- Semver: patch = sửa checklist/wording · minor = thêm agent/command · major = đổi luật gate/format/layout `.ai-dlc/` (kèm MIGRATION.md).
- Dự án dùng plugin custom qua `.ai-dlc/overrides/` (thắng bản gói) — không khuyến khích fork.

## Pilot đang chạy

PCT (`../portal-hub/spoke-apps/spoke-project-control-tower`) — **INT-003** "Nối backend Quality Gate (W0 + W1)" đang chạy ở **stage 6 Construction**: Gates A–D đóng (DEC-0053), unit-plan v4 = 30 Unit · 113.25h, mang theo **RV-019/RV-020 chưa có** (MSG-0033/0034 `unfulfilled`). INT-002 đã đóng ở stage 8 (20 unit). INT-001 "Khung UI Quality Gate (mock-first)" đã **đóng ở stage 8 (Operations)**: gates A–G qua hết, retro sinh `LL-001`/`LL-002` (Gate G · DEC-0027) và `LL-003` (chờ Gate G của intent kế). State tại `.ai-dlc/` của repo đó; tower serve port 8642. Đây là dự án đã trả nợ `LL-PENDING` cho gói. Nợ còn lại của chính nó, đo bằng KPI mới: `units.reviewed` **0/17** · `units.artifacts` **0/17** — intent kế phải mở đầu bằng việc đó, không phải bằng dựng bù hồ sơ.
