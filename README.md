# ai-dlc

> **[EXPERIMENTAL]** Plugin đang trong giai đoạn thử nghiệm. API, luật gate và format có thể thay đổi giữa các phiên bản.

**AI-DLC** (AI-Driven Development Lifecycle) — Claude Code plugin đóng gói phương pháp phát triển phần mềm AI-native theo white paper AWS. AI khởi xướng và dẫn dắt, con người phê duyệt tại các điểm then chốt (gates).

## Tại sao dùng AI-DLC?

- **AI đề xuất, người quyết định** — không agent nào vượt gate mà chưa có người duyệt
- **Cấm approve mù** — mỗi gate có tài liệu markdown tự đủ, đọc toàn văn trước khi duyệt
- **Luật kiểm được** — mỗi luật có trường để điền và KPI để đối chiếu; luật không kiểm được sẽ bị gỡ
- **Control Tower LIVE** — dashboard real-time theo dõi vị trí agent, gate queue, hoạt động gần đây
- **Không mất bối cảnh** — agent giao việc bằng file (handoff), phiên kết thúc giữa chừng vẫn tiếp tục được

## Yêu cầu

- [Claude Code](https://claude.ai/code) (CLI, desktop app, hoặc IDE extension)
- Plugin support đã bật

## Cài đặt

```bash
# Thêm marketplace
/plugin marketplace add ducsatthu/ai-dlc

# Cài plugin
/plugin install ai-dlc@ai-dlc
```

## Bắt đầu nhanh

```bash
# 1. Vào thư mục dự án
cd <your-project>

# 2. Khởi tạo AI-DLC cho dự án (seed .ai-dlc/ + Workspace Map)
/dlc-init

# 3. Bắt đầu một Intent mới — flow dừng ở Gate A chờ bạn duyệt
/dlc-intent "mô tả yêu cầu của bạn"

# 4. Phiên sau: vào lại đúng chỗ dừng, không đọc lại từ đầu
/dlc-resume
```

## Flow chính

```
/dlc-intent → /dlc-discover → /dlc-validate → /dlc-units → /dlc-bolt → /dlc-accept → /dlc-retro
```

| Stage | Skill | Mô tả |
|-------|-------|-------|
| 1. Request | `/dlc-intent` | Biến yêu cầu thành Intent Plan + Source Reading Plan + Unit Map |
| 2. Discovery | `/dlc-discover` | Đọc nguồn, dựng AS-IS model |
| 3–4. Validation | `/dlc-validate` | Trình bày AS-IS, sinh open questions tách business/tech |
| 5. Planning | `/dlc-units` | Refine Unit Map → Unit Plan chốt |
| 6. Construction | `/dlc-bolt` | Code theo Bolt: Domain Design → Logical Design → Code + Test |
| 7. Acceptance | `/dlc-accept` | Gom Acceptance Evidence, verify chuỗi truy vết |
| 8. Retro | `/dlc-retro` | Rút lesson learned, đề xuất patch plugin |

## Tất cả commands

| Command | Mục đích |
|---------|----------|
| `/dlc-init` | Khởi tạo `.ai-dlc/` cho dự án |
| `/dlc-intent` | Bắt đầu Intent mới |
| `/dlc-discover` | Chạy Discovery (đọc nguồn, dựng AS-IS) |
| `/dlc-validate` | Validation + sinh open questions |
| `/dlc-units` | Lập Unit Plan |
| `/dlc-bolt` | Điều phối Construction cho một Unit |
| `/dlc-tasks` | Xem/quản lý task board |
| `/dlc-accept` | Gom bằng chứng Acceptance |
| `/dlc-retro` | Retrospective + lesson learned |
| `/dlc-resume` | Vào lại dự án ở phiên mới |
| `/dlc-revise` | Xử lý yêu cầu chỉnh sửa từ tower |
| `/dlc-status` | Xem trạng thái hiện tại |
| `/dlc-map` | Xem/cập nhật Workspace Map |
| `/dlc-tower` | Sinh Control Tower dashboard |
| `/dlc-tower serve` | Chạy Control Tower LIVE (auto-refresh) |
| `/dlc-doctor` | Kiểm tra sức khỏe dự án |
| `/dlc-contribute` | Đóng gói lesson learned thành PR lên plugin |

## Gates

7 gates bắt buộc, mỗi gate do **người** duyệt — không có cách nào để agent tự vượt:

| Gate | Vị trí | Duyệt cái gì |
|------|--------|---------------|
| **A** | Sau Intent Plan | Intent + Source Reading Plan + Unit Map |
| **B** | Sau Discovery | AS-IS model + source ledger |
| **C** | Sau Validation (business) | Open questions business |
| **D** | Sau Planning | Unit Plan + open questions tech |
| **E** | Trong Construction | Design review (a) + code review (b) |
| **F** | Sau Acceptance | Acceptance evidence |
| **G** | Sau Retro | Lesson learned + patch proposal |

## Agents (16)

| Nhóm | Agents |
|-------|--------|
| Pipeline (9) | `orchestrator` · `intent-analyst` · `source-planner` · `context-archaeologist` · `context-validator` · `unit-planner` · `bolt-coordinator` · `acceptance-recorder` · `retro-keeper` |
| Dev (2) | `be-dev` · `fe-dev` |
| Review on-demand (5) | `ba-reviewer` · `pm-po-reviewer` · `qa-reviewer` · `security-reviewer` · `tech-lead-reviewer` |

Từ v6.0.0, review theo **tầng rủi ro** (§4.17): mặc định dev tự soát bằng checklist + bằng chứng (`self-verify`), peer review trong cùng bolt, specialist chỉ khi trigger bắn (auth/PII, migration, public API...).

## Control Tower

```bash
/dlc-tower serve
```

Mở browser tại `http://localhost:8642`. Dashboard tự cập nhật mỗi 5 giây:

- **Mission Control** — gate queue, vị trí agent đang làm việc, hoạt động gần đây
- **Dòng chảy 3 pha** — Inception / Construction / Operations, mỗi Unit là một mạch
- **Intent Detail** — Units, nguồn, open questions, decisions, tài liệu
- **Bolt Board** — task board cho Construction
- **Comms & Reviews** — tin nhắn, review requests, verdicts
- **Governance** — decisions log, KPI

Quyết định (Approve/Reject/Yêu cầu chỉnh sửa) ghi durable vào `.ai-dlc/inbox/` — phiên Claude Code drain tự động.

## Custom per project

Mỗi dự án có thể override luật plugin bằng `.ai-dlc/overrides/`:

```
.ai-dlc/
├── overrides/          # Thắng bản plugin
│   ├── checklists/     # Override checklist
│   └── templates/      # Override template
├── workspace-map.md    # Map output paths
├── governance/
│   └── sizing.md       # Núm dự án (unit_max_hours, ...)
└── ...
```

## Cấu trúc repo

```
.claude-plugin/
└── marketplace.json        # Marketplace metadata
plugin/
├── .claude-plugin/
│   └── plugin.json         # Plugin metadata (version, description)
├── agents/                 # 16 agent definitions
├── skills/                 # 16 skills (dlc-*)
│   └── checklists/         # 8 checklists có version
├── templates/              # Templates cho intent, unit, handoff, ...
├── references/
│   └── protocol.md         # Giao thức chung — luật của mọi agent/skill
├── hooks/                  # SessionStart + PreToolUse gate guard
├── scripts/                # tower_generate, tower_serve, session_brief
├── tower-ui/               # React UI cho Control Tower
├── CHANGELOG.md
├── MIGRATION.md
└── README.md
docs/
└── whitepaper-ai-dlc-vi.md # White paper gốc (SSOT)
```

## Contributing

### Nguyên tắc

1. **Mọi thay đổi luật/checklist phải đi từ Lesson Learned (LL)** đã qua Gate G của một dự án thật. CHANGELOG entry bắt buộc link LL. Không sửa chay.
2. **Semver**:
   - **patch** — sửa checklist/wording
   - **minor** — thêm agent/command
   - **major** — đổi luật gate/format/layout `.ai-dlc/` (kèm `MIGRATION.md`)
3. **Command mới** phải prefix `dlc-`
4. **Checklist** có `version` trong frontmatter + changelog trong file

### Quy trình đóng góp

#### Cách 1: Từ trong dự án đang chạy plugin (khuyến khích)

```bash
# Sau khi retro sinh LL-NNN và Gate G approve
/dlc-contribute
```

Skill tự động:
1. Gom LL + override diff liên quan + ngữ cảnh
2. **Sanitize** — bỏ tên khách hàng, số liệu nội bộ, URL riêng (thay bằng placeholder)
3. In preview cho bạn duyệt
4. Tạo branch + PR lên repo plugin (body link LL nguồn)

#### Cách 2: PR thủ công

1. Fork repo
2. Tạo branch từ `main`
3. Sửa đổi, đảm bảo:
   - Entry CHANGELOG link LL nguồn
   - Checklist có bump version
   - Chạy lint: `python3 -m py_compile plugin/scripts/*.py plugin/hooks/*.py` và `bash -n plugin/hooks/session_start.sh`
4. Mở PR với mô tả rõ LL nguồn và lý do thay đổi

### Sau khi merge

Maintainer:
- Bump version trong `plugin/.claude-plugin/plugin.json`
- Cập nhật CHANGELOG
- Tag release

### Báo lỗi / đề xuất

Mở issue trên GitHub với:
- Mô tả vấn đề hoặc đề xuất
- Context: dự án đang ở stage nào, gate nào
- Nếu là bug: bước tái hiện + output thật (ẩn thông tin nhạy cảm)

## License

MIT

## Links

- [White paper AWS AI-DLC](docs/whitepaper-ai-dlc-vi.md) — tài liệu phương pháp gốc (SSOT)
- [Protocol](plugin/references/protocol.md) — giao thức chung cho mọi agent/skill
- [Changelog](plugin/CHANGELOG.md) — lịch sử thay đổi
- [Migration](plugin/MIGRATION.md) — hướng dẫn nâng version
