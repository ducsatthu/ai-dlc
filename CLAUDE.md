# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Repo **plugin `ai-dlc`** (kiêm marketplace — 1 repo duy nhất): đóng gói phương pháp **AI-DLC** (AI-Driven Development Lifecycle, theo white paper AWS — bản dịch nội bộ Mynavi TechTus Vietnam) thành Claude Code plugin cài được, có Control Tower, override per project và learning loop qua retro.

- **Tài liệu chuẩn (SSOT) của phương pháp**: `docs/whitepaper-ai-dlc-vi.md` — mọi mâu thuẫn giữa tài liệu giải quyết theo file này.
- **Phân cấp**: Project → Intent → Unit → Bolt → Task. Một Unit chạy qua một hoặc nhiều Bolt (song song/tuần tự); mỗi Bolt: Domain Design → Logical Design + ADR → Code + Unit Test.
- **Nguyên tắc**: AI đề xuất trước — con người xác nhận trước khi đi tiếp. Gates A–G, không agent nào được vượt.

## Cấu trúc

| Đường dẫn | Nội dung |
|---|---|
| `.claude-plugin/marketplace.json` | Marketplace trỏ `./plugin` |
| `plugin/` | Gói chính: 17 agents (`agents/`), 14 skills `dlc-*` (`skills/`), 7 checklists có version (`skills/checklists/`), templates, hooks (SessionStart + PreToolUse gate guard), scripts tower |
| `plugin/references/protocol.md` | **Giao thức chung — mọi agent/skill tuân theo** (gates, layout `.ai-dlc/`, format MSG/RV/DEC/LL, binding rules, model tiers) |
| `docs/` | White paper, blueprint HTML, plugin plan, dry-run PCT, design prompt Control Tower |

## Commands (khi plugin đã cài)

```
claude plugin marketplace add <path-repo-này>   # hoặc org/ai-dlc trên GitHub
claude plugin install ai-dlc@ai-dlc
/dlc-init → /dlc-intent "..." → /dlc-discover → /dlc-validate → /dlc-units → /dlc-bolt → /dlc-accept → /dlc-retro
/dlc-status · /dlc-tower [serve] · /dlc-map · /dlc-tasks · /dlc-doctor · /dlc-contribute
```

Test scripts: `python3 -m py_compile plugin/scripts/*.py plugin/hooks/*.py` · `bash -n plugin/hooks/session_start.sh`.

## Quy ước khi sửa gói

- Sửa checklist/luật trong plugin **phải** đi từ một LL (lesson learned) đã qua Gate G của dự án thật — CHANGELOG entry bắt buộc link LL. Không sửa chay.
- Command mới phải prefix `dlc-`. Checklist có `version` trong frontmatter + changelog trong file.
- Semver: patch = sửa checklist/wording · minor = thêm agent/command · major = đổi luật gate/format/layout `.ai-dlc/` (kèm MIGRATION.md).
- Dự án dùng plugin custom qua `.ai-dlc/overrides/` (thắng bản gói) — không khuyến khích fork.

## Pilot đang chạy

PCT (`../portal-hub/spoke-apps/spoke-project-control-tower`) — INT-001 "Phase 2 (Release + Milestone + Backlog)" đang mở **Gate A**; state tại `.ai-dlc/` của repo đó; tower serve port 8642.
