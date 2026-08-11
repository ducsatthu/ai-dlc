# Changelog — ai-dlc plugin

## 1.0.0 (2026-08-11) — MVP
- 17 agents (9 pipeline · 7 review board · retro-keeper), model tiers opus/sonnet/haiku.
- 14 commands `dlc-*`; 7 checklists v1; templates (workspace-map, DoR/DoD v1, intent, unit, tasks, OVERRIDES).
- Gates A–G + gate động; protocol.md là luật chung.
- Control Tower: generator (Mission Control + Bản đồ AI-DLC theo Hình 1 white paper + task boards + comms) và serve 2 chiều (Approve/Reject → inbox durable, token localhost).
- Hooks: SessionStart (binding rules + drain inbox), PreToolUse gate guard (chặn code-write trước Gate D theo workspace map, fail-open).
- Cơ chế: overrides thắng plugin, pinned snapshot per intent, contribute → PR.
- Nguồn phương pháp: white paper AI-DLC bản dịch nội bộ (đã biên tập). Chưa có LL nào — thay đổi sau này bắt buộc link LL.
