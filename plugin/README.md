# ai-dlc — AI-Driven Development Lifecycle plugin

Agent team theo white paper AWS AI-DLC (bản dịch nội bộ Mynavi TechTus Vietnam).
Phân cấp **Intent → Unit → Bolt → Task** · 3 pha Inception/Construction/Operations ·
gates A–G · Control Tower · override per project · learning loop qua retro.

## Cài đặt
```
/plugin marketplace add <org-hoặc-path>/ai-dlc
/plugin install ai-dlc@ai-dlc
cd <project> && /dlc-init        # seed .ai-dlc/ + dựng Workspace Map
/dlc-intent "yêu cầu của bạn"    # bắt đầu — flow dừng ở Gate A chờ bạn
/dlc-resume                      # phiên sau: vào lại đúng chỗ dừng, không đọc lại từ đầu
```

## Commands
`/dlc-init` `/dlc-map` `/dlc-intent` `/dlc-discover` `/dlc-validate` `/dlc-units`
`/dlc-bolt` `/dlc-tasks` `/dlc-accept` `/dlc-retro` `/dlc-revise` `/dlc-resume` `/dlc-status`
`/dlc-tower [serve]` `/dlc-doctor` `/dlc-contribute`

## Nhiều phiên, nhiều vị trí — không mất bối cảnh (v2.1)

Agent giao việc cho nhau bằng **file**, không bằng prompt: mỗi lần spawn là một
`context-memory/handoffs/HOF-NNNN.md` (nhiệm vụ 1 câu · `read_first` trỏ `path#mục` + vì sao · DoD của lượt ·
trả về gì), prompt spawn chỉ là *"đọc HOF-NNNN, làm theo, cập nhật lại file đó khi xong"*.

- Phiên kết thúc giữa chừng → HOF vẫn ở `accepted`; `/dlc-resume` chỉ ngay ra ai đang giữ gì và tiếp tục từ
  chính file đó. Không hỏi lại, không dựng lại bối cảnh.
- `session/board.md` (bảng vị trí) **sinh ra từ** `handoffs/` — phiên chính nhìn thấy các vị trí khác đang ở đâu.
- Chuỗi HOF là nguồn bằng chứng của retro: việc đi qua tay ai, tắc ở đâu, trả lại mấy lần.
- Đọc ít: `/dlc-resume` chỉ nạp stdout của `session_brief.py` + tối đa 1 HOF; cần chi tiết thì tra
  `session/INDEX.md` rồi mở **đúng mục** (protocol §10).

## Hỏi đúng người, hỏi bằng ngôn ngữ của họ (v3)

Stage 4 sinh **hai** file câu hỏi, tách theo **người trả lời** chứ không theo chủ đề:

| File | Cho ai | Luật |
|---|---|---|
| `open-questions-business.md` | owner/PO/BA/PMO/vận hành | **gate_doc của Gate C** · viết bằng lời, **cấm** đường dẫn file · tên bảng · tên hàm · route |
| `open-questions-tech.md` | tech lead/architect/QA/devops | không ra Gate C · câu `CHẶN UOW-NN` là điều kiện chặn **Gate D** · mọi khẳng định kèm `path:line` |

Mỗi câu là **một** quyết định, có mã, có **một** người trả lời cụ thể (vai + tên), có phương án chọn sẵn kèm
cái giá, có đề xuất của AI, và **có phương án mặc định nếu không ai trả lời** — im lặng không được phép làm
tắc dự án. Quyết định chạm cả hai phía thì viết **cặp** `OQT-NN` ↔ `OQB-NN` nối bằng dòng *soi chiếu*, thay vì
ném nguyên câu kỹ thuật cho người nghiệp vụ. Chi tiết: protocol §4.10.

## Ba luật chống sai từ gốc (v2)

1. **Stage 1 sinh `intent-plan.md`** — Intent + **Source Reading Plan** (sẽ đọc nguồn nào, lấy
   thông tin gì cụ thể) + **Provisional Unit Map**. Gate A duyệt chính tài liệu này, đọc toàn văn
   trên Control Tower. Kế hoạch đọc được chốt TRƯỚC khi ai đó bắt đầu đọc.
2. **No-unread-source** (§4.8) — mọi nguồn đã cam kết phải kết thúc ở trạng thái cuối (`read` có
   evidence / `missing` / `deferred` / `superseded`) trong `as-is/source-ledger.md`. Còn `planned`
   là chặn Gate B/D. Agent chỉ được kết luận từ nguồn có trong ledger.
3. **Unit = một phiên · tự ra được sản phẩm** (§4.9 v5) — mỗi Unit khai `releasable` (nếu `no` thì kèm
   `released_with`) và `session_fit` có con số; ước lượng vẫn cần breakdown nhưng **không còn trần giờ**
   (trần 5h của v2 đã bỏ — nó bắt cắt theo đồng hồ thay vì theo đường ra sản phẩm).
   Mỗi Unit bắt buộc đủ **User Story · NFR · Rủi ro**.

## Luật kiểm được (v4 — sinh từ retro thật, không từ suy đoán)

Một dự án chạy plugin này đóng **17 unit code** với **13 review-request gửi đi và 0 verdict quay lại**, trong
khi DoD v1 *đã* yêu cầu "reviewer approve" từ ngày đầu. Không ai nói dối — câu chữ đó không có gì để đối
chiếu. Bài học chung: **luật không kiểm được là luật sẽ trượt**. Vì vậy mỗi luật dưới đây có một *trường để
điền* và một *KPI để đối chiếu*:

| Luật | Trường | KPI trên tower |
|---|---|---|
| §4.12 review có địa chỉ | `rv:` trỏ RV có thật, hoặc `review_waived_by: DEC` | `units.reviewed` |
| §4.14 unit lỗi thời vào `units/_trash/` + `TOMBSTONE.md` | `status: obsolete` | bỏ khỏi mọi thống kê |
| §4.13 phát hiện ngoài phạm vi | `escalations/ESC-NNN.md` có `owner` | panel *chờ người nhận* |
| bolt tồn tại thật (LL-003) | `bolts/BOLT-NN/` · `tasks.md` · `evidence/` | `units.artifacts` |

Kèm hai luật về cách làm việc: **phép đo phải có ca đối chứng** trước khi tin nó (§4.15 — đo hỏng cho kết quả
*ngược*, không phải kết quả trống), và **thu hẹp union thì grep mọi so sánh bằng** (§4.16 — compiler lẫn test
đều im). Và một luật về khoảng trống: **không dựng bù hồ sơ** — hồ sơ trống trung thực hơn hồ sơ dựng lại.

## Nguyên tắc
- AI đề xuất trước — con người xác nhận trước khi đi tiếp. Không agent nào vượt gate.
- **Cấm approve mù**: mỗi gate có một tài liệu markdown tự đủ; Approve chỉ mở sau khi người duyệt
  xác nhận đã đọc toàn văn (server chặn lần nữa). Verdict thứ ba là *Yêu cầu chỉnh sửa* → `/dlc-revise`.
- Output resolve path qua `.ai-dlc/workspace-map.md` — không đoán.
- Custom per project: `.ai-dlc/overrides/` thắng bản plugin; retro (Gate G) là đường
  duy nhất sửa chuẩn; `/dlc-contribute` đưa lesson lên gói chung.
- Giao thức đầy đủ: `references/protocol.md`. Phương pháp gốc: white paper
  (`docs/whitepaper-ai-dlc-vi.md` ở repo).

## Control Tower — LIVE
`/dlc-tower serve` chạy chế độ **LIVE**: trang poll `/state` mỗi 5 giây, server tự sinh lại dashboard khi
`.ai-dlc/` đổi. Bạn thấy ngay: vị trí nào đang có agent (kèm `progress` + nhịp sống), file thật nào vừa được
ghi trong 2 giờ qua, và cảnh báo khi có agent chạy mà chưa khai `status: accepted` (protocol §9.4).

Màn: Mission Control (gate queue · vị trí đang làm việc · hoạt động gần đây) · **Dòng chảy 3 pha** (Inception · Construction ·
Operations, mỗi Unit là một mạch chạy xuyên ba khối) · Intent Detail (Units · Nguồn · Open questions tách
nghiệp vụ/kỹ thuật ·
Decisions · Chỉnh sửa · Tài liệu) · Bolt board · Comms & Reviews · Governance.
Quyết định ghi durable vào `.ai-dlc/inbox/` — phiên Claude Code drain và ghi DEC.

## Model tiers
opus = phân rã/kiến trúc/rủi ro (orchestrator, intent-analyst, source-planner, archaeologist,
unit-planner, ba/tech-lead/security reviewer) · sonnet = thực thi & review ·
haiku = acceptance-recorder (cơ học). Xem protocol §6.

## Hàng rào cứng
- PreToolUse hook chặn Write/Edit vào code roots khi intent chưa qua Gate D
  (tắt khẩn: `AI_DLC_GUARD=off`).
- SessionStart hook nạp binding rules + drain inbox (quyết định từ tower không bao giờ rơi).
