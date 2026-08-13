---
name: dlc-revise
description: Xử lý verdict "Yêu cầu chỉnh sửa" (request-changes) từ Control Tower — ghi REV-NN, giao đúng agent sửa đúng phần, bump version tài liệu gate rồi mở lại gate với bản mới. Dùng khi inbox có verdict request-changes hoặc user nêu điểm cần sửa trong tài liệu gate.
---

Đọc `${CLAUDE_PLUGIN_ROOT}/references/protocol.md` §2.2. **`request-changes` KHÔNG đóng gate** — gate vẫn
mở, chỉ là tài liệu đi một vòng sửa.

1. **Lấy yêu cầu**: từ `.ai-dlc/inbox/*.json` (`verdict: request-changes`) hoặc từ lời user trong phiên.
   Xác định: intent nào · gate nào · `gate_doc` nào · yêu cầu sửa phần nào.
2. **Ghi vết**: tạo `intents/INT-NNN/revisions/REV-NN.md` theo format protocol §5 (nguyên văn yêu cầu,
   không diễn giải lại). Move file inbox sang `processed/`.
3. **Giao đúng người**:
   | gate_doc | agent sửa |
   |---|---|
   | `intent-plan.md` phần 1 hoặc 3 | `ai-dlc:dlc-intent-analyst` |
   | `intent-plan.md` phần 2 (nguồn) | `ai-dlc:dlc-source-planner` |
   | `as-is/source-ledger.md` | `ai-dlc:dlc-context-archaeologist` |
   | `open-questions-business.md` / `open-questions-tech.md` | `ai-dlc:dlc-context-validator` |
   | `unit-plan.md` + `units/**` | `ai-dlc:dlc-unit-planner` |
   | `bolts/**` | `ai-dlc:dlc-bolt-coordinator` |
   Yêu cầu dạng *"câu OQB-NN đọc không hiểu / toàn thuật ngữ"* → validator viết lại câu đó theo §4.10.2
   (dịch ra lời, thêm phương án + cái giá), **không** trả lời thay người quyết.
4. **Sửa có kỷ luật**: chỉ đụng phần được nêu; bump `version:` trong frontmatter gate_doc; thêm dòng cuối
   mục Changelog (`vN: sửa gì · theo REV-NN`). Không viết lại cả tài liệu — người duyệt cần thấy được cái gì đổi.
   Yêu cầu chạm scope/outcome → mở lại gate trước đó thay vì vá tại chỗ (protocol §4.4).
5. **Reviewer soi lại** đúng phần đã sửa (ba-reviewer cho gate A–D), cập nhật RV.
6. Đánh dấu `REV-NN` `status: addressed`, giữ nguyên `gate_open`, cập nhật `plan_version` trong `status.md`,
   chạy `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tower_generate.py` để tower hiển thị bản mới + changelog.
7. Trình lại gate cho người duyệt (nêu rõ **đã sửa gì so với bản trước**), rồi **KẾT THÚC LƯỢT**.
8. **Vòng thứ 3** cùng một gate_doc mà vẫn chưa hội tụ → dừng vòng sửa, tạo MSG `escalation` →
   `ai-dlc:dlc-tech-lead-reviewer`. Sửa vòng 3 im lặng là dấu hiệu vấn đề nằm ở chỗ khác (đề bài, scope,
   hoặc thiếu nguồn), không phải ở câu chữ tài liệu.
