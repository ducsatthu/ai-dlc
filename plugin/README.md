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
```

## Commands
`/dlc-init` `/dlc-map` `/dlc-intent` `/dlc-discover` `/dlc-validate` `/dlc-units`
`/dlc-bolt` `/dlc-tasks` `/dlc-accept` `/dlc-retro` `/dlc-status` `/dlc-tower [serve]`
`/dlc-doctor` `/dlc-contribute`

## Nguyên tắc
- AI đề xuất trước — con người xác nhận trước khi đi tiếp. Không agent nào vượt gate.
- Output resolve path qua `.ai-dlc/workspace-map.md` — không đoán.
- Custom per project: `.ai-dlc/overrides/` thắng bản plugin; retro (Gate G) là đường
  duy nhất sửa chuẩn; `/dlc-contribute` đưa lesson lên gói chung.
- Giao thức đầy đủ: `references/protocol.md`. Phương pháp gốc: white paper
  (`docs/whitepaper-ai-dlc-vi.md` ở repo).

## Model tiers
opus = phân rã/kiến trúc/rủi ro (orchestrator, intent-analyst, archaeologist,
unit-planner, ba/tech-lead/security reviewer) · sonnet = thực thi & review ·
haiku = acceptance-recorder (cơ học). Xem protocol §6.

## Hàng rào cứng
- PreToolUse hook chặn Write/Edit vào code roots khi intent chưa qua Gate D
  (tắt khẩn: `AI_DLC_GUARD=off`).
- SessionStart hook nạp binding rules + drain inbox (quyết định từ tower không bao giờ rơi).
