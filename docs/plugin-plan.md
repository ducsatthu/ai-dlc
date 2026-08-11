# Kế hoạch triển khai — Plugin `ai-dlc` (đóng gói · cài ngay · override · update qua retro)

> Trạng thái: **BẢN KẾ HOẠCH — CHỜ DUYỆT** · Ngày: 2026-08-11
> Mục tiêu: biến toàn bộ mô hình agent team (blueprint v3) thành một **Claude Code plugin** — team nào cũng `install` là dùng ngay, tự custom được, và mọi cải tiến từ retro của từng dự án chảy ngược về gói chung có kiểm soát.

---

## 0 · Tài liệu chuẩn & phân cấp (chốt 2026-08-11, theo white paper)

**Tài liệu chuẩn của phương pháp là white paper AI-DLC bản dịch nội bộ đã biên tập** — lưu tại `docs/whitepaper-ai-dlc-vi.md`. Mọi mâu thuẫn giữa các tài liệu thiết kế giải quyết theo white paper.

**Phân cấp** (đúng white paper): **Project → nhiều Intent → Intent phân rã thành các Unit (Inception · Mob Elaboration) → mỗi Unit chạy qua MỘT hoặc NHIỀU Bolt, song song hoặc tuần tự (Construction) → mỗi Bolt: Domain Design → Logical Design + ADR → Code + Unit Test → Deployment Unit (Operations).** Task board nằm trong từng Bolt. *(Thay thế chốt trước đó "Bolt gom nhiều Unit" — follow white paper theo chỉ đạo mới nhất.)*

**Ba pha & nghi thức** ánh xạ vào flow 8 stage của blueprint: Inception = stage 1–5 (Mob Elaboration ≈ Validation Mob + Gate A–D; artefact: PR-FAQ tùy chọn · User Stories · NFR · Rủi ro · Bolt đề xuất) · Construction = stage 6 (Mob Construction; brown-field thêm bước nâng mã lên mô hình tĩnh + động — chính là stage 2–3 reverse engineering của blueprint) · Operations = stage 7–8 + vận hành (Deployment Unit, telemetry, runbook chờ Developer phê duyệt). Nguyên tắc xuyên suốt: **"Ở mọi điểm phân rã, AI đề xuất trước và con người xác nhận trước khi đi tiếp."** Control Tower có màn **Bản đồ AI-DLC** tái hiện Hình 1 của white paper ở trạng thái sống (đã ghi trong design prompt).

## 1 · Nguyên tắc thiết kế

1. **Plugin là SSOT của quy trình chung** — 17 agents, các skill/command, checklist review, template DoR/DoD, luật gate. Không dự án nào sửa trực tiếp vào gói.
2. **Project override THẮNG plugin default** — mỗi dự án custom bằng file override tại repo của mình, có hiệu lực ngay, không chờ plugin release. (Đúng pattern binding-rule PCT đang dùng: *"Project override THẮNG generic default khi mâu thuẫn. Generic chỉ là fallback."*)
3. **Retro là nguồn cải tiến duy nhất của gói chung** — muốn đổi checklist/agent trong plugin phải đi từ một Lesson Learned (LL) đã qua Gate G của một dự án thật, không sửa chay.
4. **Update không phá dự án đang chạy** — semver + changelog + migration note; override của team luôn sống sót qua update.
5. **Nội bộ vs deliverable tách bạch** — `.ai-dlc/` chỉ chứa phần quản lý nội bộ (comms, reviews, decisions, drafts, state); output thật (code, tài liệu BA/Technical, wiki) đi vào **cấu trúc thật của dự án** theo Workspace Map — agent không bao giờ tự đoán path.

## 2 · Kiến trúc gói

**Một repo duy nhất** (đã chốt) — repo vừa là marketplace vừa chứa gói, marketplace.json trỏ source tương đối vào thư mục plugin:

```
ai-dlc/                              # 1 REPO duy nhất
├── .claude-plugin/marketplace.json  # danh mục: plugin "ai-dlc" · source: ./plugin
├── docs/                            # blueprint, plan, dry-run (tài liệu thiết kế này)
└── plugin/                          # gói chính
    └── (cấu trúc dưới đây)

plugin/
├── .claude-plugin/plugin.json       # name: ai-dlc · version: 1.0.0
├── agents/                          # 17 agent definitions (blueprint v3)
│   ├── orchestrator.md  intent-analyst.md  context-archaeologist.md ...
│   ├── ba-reviewer.md  pm-po-reviewer.md  tech-lead-reviewer.md
│   ├── security-reviewer.md  backend-reviewer.md  frontend-reviewer.md
│   ├── qa-reviewer.md  be-dev.md  fe-dev.md  bolt-coordinator.md
│   └── retro-keeper.md
├── skills/                          # commands + checklists — TẤT CẢ prefix `dlc-`
│   │                                # (tránh va chạm: môi trường thường có sẵn /retro, /status,
│   │                                #  /review của plugin khác — vd gstack đã chiếm /retro)
│   ├── dlc-intent/  dlc-discover/  dlc-validate/  dlc-units/
│   ├── dlc-bolt/  dlc-tasks/  dlc-accept/  dlc-retro/  dlc-status/  dlc-tower/
│   ├── checklists/                  # ~20 checklist, MỖI FILE CÓ version riêng
│   │   ├── review-approach.md       # frontmatter: version: 3, changelog trong file
│   │   └── ...
│   ├── dlc-init/                 # seed .ai-dlc/ (context-memory + overrides) vào project
│   ├── dlc-contribute/           # đóng gói override → đề xuất lên gói chung
│   └── dlc-doctor/               # so khớp override vs bản plugin hiện tại
├── templates/                       # context-memory skeleton, dor.md v1, dod.md v1,
│   │                                # tasks.md, MSG/RV/DEC/LL templates
├── hooks/hooks.json                 # SessionStart: nạp governance + binding rule + DRAIN INBOX (§5)
│                                    # PreToolUse: hàng rào cứng gate (§3) — chặn ghi vào code roots
│                                    #   (theo workspace map) khi intent chưa có DEC Gate D
├── scripts/tower-generate.*         # generator Control Tower (đọc context-memory → HTML)
└── CHANGELOG.md                     # theo semver, mỗi entry link về LL nguồn
```

Cài đặt (dùng ngay, đúng yêu cầu):

```
/plugin marketplace add <org>/ai-dlc
/plugin install ai-dlc@ai-dlc
/dlc-init             # seed .ai-dlc/ (context-memory + overrides) vào project
/dlc-intent "..."     # bắt đầu chạy flow
```

Mọi thứ plugin ghi vào project nằm gọn trong **một thư mục ẩn `.ai-dlc/`** — muốn ignore chỉ cần một dòng, muốn commit chọn lọc cũng dễ.

## 3 · Cơ chế override 3 lớp (custom per team, hiệu lực ngay)

Thứ tự ưu tiên khi agent load một checklist/định nghĩa: **Project > Org > Plugin default**.

```
<project>/.ai-dlc/                   # TOÀN BỘ state NỘI BỘ của plugin trong project — 1 chỗ duy nhất
├── workspace-map.md                 # bản đồ dự án: code/docs/wiki nằm đâu (xem §4)
├── context-memory/                  # comms/ reviews/ lessons-learned/ governance/ ...
│   └── intents/INT-xxx/             # phân cấp §0 (white paper): Intent → Unit → Bolt → task board
│       ├── pinned/                  # SNAPSHOT checklist + governance lúc intent bắt đầu (§7, §9)
│       └── units/UOW-01/            # spec.md · user-stories.md · nfr.md · risks.md · (pr-faq.md)
│           └── bolts/BOLT-01/       # domain-design.md · logical-design.md + ADR · tasks.md · evidence/
├── inbox/                           # durable queue: quyết định/comment từ tower (§5)
├── tower/                           # output generator Control Tower (volatile)
└── overrides/
    ├── OVERRIDES.md                 # index: override nào đang bật, vì sao, từ LL nào
    ├── checklists/review-api.md     # thay/patch checklist cùng tên trong plugin
    ├── agents/fe-dev.md             # thêm quy ước riêng cho agent (append-style)
    └── governance/dod.md            # DoD riêng của dự án (nếu khác chuẩn chung)
```

Gợi ý `.gitignore` (team tự quyết mức độ):

```gitignore
.ai-dlc/                             # cách đơn giản nhất: ignore tất cả
# — hoặc commit chọn lọc phần đáng giữ lịch sử:
# .ai-dlc/tower/
# .ai-dlc/context-memory/comms/
# (giữ lại overrides/ + governance/ + decisions + lessons — đó là tài sản truy vết của team)
```

Luật vận hành (ghi trong hook SessionStart của plugin — bắt buộc như binding rule của PCT):

- Mọi agent **trước khi dùng** checklist/governance nào phải kiểm tra `.ai-dlc/overrides/` — có file cùng tên thì **override thắng**; không có thì dùng bản plugin.
- Override có 2 kiểu: `replace` (thay cả file) và `patch` (chỉ thêm/sửa mục — mặc định, để update plugin vẫn hưởng phần chung).
- Mỗi override **bắt buộc có frontmatter**: `reason`, `source: LL-xxx` (hoặc DEC), `created`, `expires_hint` — override không nguồn gốc bị `/dlc-doctor` cảnh báo.
- Org overlay (tùy chọn, cho nhiều team cùng công ty): một repo `ai-dlc-org-overlay` cài như plugin thứ hai, đứng giữa project và default.

Đây chính là cơ chế "**overwrite sớm** trước khi plugin update": retro hôm nay → override hôm nay → dùng ngay ngày mai, không đợi release.

**Hàng rào cứng — gate không chỉ enforce bằng prompt.** Luật "chưa qua gate thì không được làm" nằm trong instruction của agent là chưa đủ (prompt có thể trượt); plugin cứng hóa bằng **PreToolUse hook**:

- Chặn Edit/Write vào các **code roots theo workspace map** khi intent chưa có DEC Gate D trong `context-memory/` — workspace map vốn biết code nằm đâu, tận dụng làm hàng rào gần như miễn phí.
- Chặn ghi vào `governance/` (DoR/DoD) khi không kèm DEC hợp lệ — không ai sửa luật ngoài luồng.
- Hook chỉ đọc file state, không gọi LLM → nhanh, deterministic, không tốn token.

## 4 · Workspace Map — output của agents đi đâu (không hardcode, không đoán)

Mỗi dự án có layout riêng (FE ở đâu, BE ở đâu, wiki ở đâu, tài liệu BA nằm chỗ nào) — plugin không được giả định. Bản đồ này sống ở `.ai-dlc/workspace-map.md` và là **nguồn duy nhất** để agent resolve đường dẫn output.

**Dựng map lúc `/dlc-init` (3 bước):**
1. Agent **scan repo** và đề xuất map: nhận diện code roots (app-fe/, app-be/…), wiki/docs, swagger, test dirs, quy ước ngôn ngữ.
2. **Hỏi user xác nhận/sửa từng mục** — user mô tả bằng ngôn ngữ tự nhiên ("tài liệu BA khi release thì đưa vào wiki/docs/business, theo chuẩn Docusaurus"), agent ghi thành map.
3. Sau init, bất kỳ lúc nào user mô tả thêm → `/dlc-map` cập nhật (map có changelog riêng, đổi map là một DEC).

Ví dụ map cho PCT:

```yaml
code:
  frontend: app-fe/              # Next.js — pattern component + next-intl
  backend:  app-be/              # FastAPI — router → service → model
docs:
  wiki: wiki/docs/               # SSOT của dự án — chuẩn Docusaurus, tiếng Việt
  ba_artifacts: wiki/docs/business/
  technical: wiki/docs/technical/
  api_spec: swagger/
conventions:
  language: vi
  rules: "wiki phải tự đủ; file điều phối không bắt buộc commit"
```

**Luật cứng:** mọi agent tạo output (code, docs) PHẢI resolve đích qua map — *"không tự đoán path"* (kế thừa binding rule PCT đang dùng). Map thiếu mục cần dùng → agent **hỏi**, không đoán.

**Xuất bản khi release (stage 8):** trong lúc làm việc, draft tài liệu BA/Technical nằm trong `.ai-dlc/` (nội bộ, ignore được). Khi Unit qua Gate F, acceptance-recorder **publish**: format bản chính thức theo chuẩn của đích (ví dụ Docusaurus frontmatter cho wiki) và ghi vào đúng vị trí theo map, kèm changelog của dự án. `.ai-dlc/` giữ bản trace, wiki/docs giữ bản chính thức — hai bản link nhau qua ID (INT/UOW/DEC).

## 5 · Tower tương tác 2 chiều — approve/reject ngay trên UI, không cần gõ terminal

Yêu cầu: thay vì trả lời trong terminal/IDE, người duyệt bấm **Approve / Reject / để lại comment** ngay trên Control Tower, và session Claude Code đang chờ ở gate **tự tiếp tục**. Khả thi — 3 tầng, làm dần:

### Tầng 1 — Local bridge qua `.ai-dlc/inbox/` (đưa vào v1, ~0.5 ngày)

```
[Tower — local web app]                    [Claude Code session]
  gate card + decision brief                 orchestrator mở gate
  nút Approve / Reject / 💬 comment            → arm Monitor watch .ai-dlc/inbox/
        │ (POST → server nhỏ của tower)        → PushNotification (desktop/phone)
        ▼                                            │ (chờ, không tốn gì)
  ghi .ai-dlc/inbox/gate-D.decision.json  ───────────┘
  { verdict, comment, decided_by, at }     Monitor bắn event → session TỰ TỈNH DẬY
                                           → ghi DEC chính thức → flow chạy tiếp
```

- Tower generator nâng từ static HTML → web app local nhỏ (serve UI + nhận POST, ghi file vào inbox). Không hạ tầng ngoài, chạy offline.
- Cơ chế chờ dùng primitive sẵn có của Claude Code: **Monitor** (watch file xuất hiện trong inbox — session ngủ, tỉnh ngay khi có quyết định, không polling tốn token) + **PushNotification** khi gate mở (lên cả điện thoại nếu bật Remote Control).
- "Trao đổi nhanh": ô comment trên gate card ghi vào inbox dạng `note/question` — session đọc như phản hồi của anh/chị, trả lời lại bằng cách cập nhật tower (regenerate). Reject bắt buộc kèm lý do → thành nội dung DEC.
- **Inbox là durable queue — không phụ thuộc session còn sống.** Monitor chỉ nghe khi session đang mở; nếu anh/chị Approve lúc terminal đã đóng, file vẫn nằm trong `.ai-dlc/inbox/`. Hook **SessionStart drain inbox**: mở session mới là orchestrator đọc mọi quyết định chưa xử lý (đối chiếu gate đang chờ trong context-memory), ghi DEC và chạy tiếp — nút Approve không bao giờ "rơi vào khoảng không". File đã xử lý move sang `inbox/processed/` (giữ trace).
- **Bảo mật local**: server tower bind `127.0.0.1` mặc định + token ngẫu nhiên sinh lúc khởi động (in vào URL mở tower) — mở ra LAN là lựa chọn chủ động, không phải mặc định; POST không token bị từ chối → "Approve" không thể bị giả từ máy khác.
- Giới hạn: tower truy cập được từ máy đang chạy session (hoặc LAN khi chủ động mở). Đủ cho v1.

### Tầng 2 — Duyệt từ xa không cần build hạ tầng (tùy chọn, khi cần approve ngoài văn phòng)

Dùng **Slack làm transport**: khi gate mở, orchestrator post decision brief vào channel `#ai-dlc-gates` (session đã có Slack connector); anh/chị bấm/reply `approve` / `reject + lý do` ngay trên Slack (điện thoại); session đọc quyết định qua vòng poll (`/loop` hoặc ScheduleWakeup) rồi tiếp tục. Latency vài chục giây–phút, đổi lại zero hạ tầng. (Trang artifact tower cũng có thể gắn capability `mcp` để bấm nút → ghi vào Slack qua connector của người xem — nhưng Slack thuần túy đơn giản hơn, nên làm trước.)

### Tầng 3 — Control Tower thành sản phẩm thật (giai đoạn sau, khi làm UI)

Tower là web app đầy đủ, backend chạy session qua **Claude Agent SDK** (headless — không cần terminal); Approve/Reject/chat là API call đẩy thẳng vào session, realtime 2 chiều qua WebSocket (Monitor của session cũng subscribe được ws). Cloud routine + RemoteTrigger webhook dùng cho luồng chạy nền theo lịch. Đây là hình hài cuối của Control Tower — làm sau khi plugin v1 chạy ổn và UI được thiết kế (design prompt đã có).

**Khuyến nghị:** v1 ship Tầng 1 (nằm trong roadmap bước 3, +0.5 ngày); Tầng 2 bật khi có nhu cầu duyệt từ xa; Tầng 3 gắn với dự án UI tower sau này.

## 6 · Vòng cải tiến: retro dự án → gói chung (mạch máu của kế hoạch)

```
[Dự án A] retro-keeper phân tích → LL-xxx + patch đề xuất
        → ◇ Gate G (team A duyệt)
        → APPLY LOCAL: ghi vào .ai-dlc/overrides/ (hiệu lực NGAY cho team A)
        → /dlc-contribute
              đóng gói: LL + override diff + ngữ cảnh (ẩn thông tin nội bộ dự án)
              → tạo PR vào repo ai-dlc
        → [Maintainer gói chung] review PR:
              - Chuẩn chung? → merge → bump version checklist + plugin semver + CHANGELOG (link LL)
              - Đặc thù dự án? → reject có ghi chú → team giữ làm override vĩnh viễn
        → Release vX.Y.Z
        → [Mọi team] /plugin update ai-dlc (chạy /plugin marketplace update để nhận bản mới)
        → /dlc-doctor sau update:
              - Override đã được upstream (nội dung ⊆ bản mới) → gợi ý XÓA override (hết trùng)
              - Override xung đột bản mới → báo diff, team tự quyết giữ/bỏ
              - Checklist plugin lên version → nhắc các RV sau dùng version mới
```

Vai trò cần chốt: **1 maintainer gói chung** (gatekeeper "chuẩn chung vs đặc thù") — đề xuất: anh/chị hoặc PMO, review PR theo nhịp tuần.

## 7 · Versioning & tương thích

| Thay đổi | Bump | Ví dụ |
|---|---|---|
| Sửa wording, thêm mục checklist, template mới | **patch** 1.0.x | LL-002 thêm mục batch-limit vào review-approach |
| Thêm agent/command/checklist mới, thêm gate động | **minor** 1.x.0 | thêm `data-reviewer` |
| Đổi luật gate, đổi cấu trúc context-memory, đổi format MSG/RV/DEC | **major** x.0.0 + migration note | đổi schema tasks.md |

- Mỗi checklist giữ version riêng trong frontmatter (đúng blueprint v3) — RV ghi lại đã review theo version nào, không phụ thuộc version plugin.
- **Pin per-intent có cơ chế thật**: lúc `/dlc-intent` khởi tạo, snapshot copy toàn bộ checklist + governance đang hiệu lực (sau khi resolve override) vào `intents/INT-xxx/pinned/`; mọi agent của intent đó **đọc từ pinned**, không đọc bản sống. Plugin update giữa chừng không đổi luật chơi của intent đang chạy, và RV truy vết được đúng văn bản đã dùng — kể cả khi bản gốc đã bị thay.
- `CHANGELOG.md` của plugin: mỗi entry bắt buộc link `LL-xxx@<dự án>` nguồn — truy vết được "luật này sinh ra từ bài học nào".
- Major release kèm `MIGRATION.md`; `/dlc-doctor` đọc file này để hướng dẫn từng bước cho dự án đang chạy giữa chừng.

## 8 · Roadmap triển khai (5 bước, mỗi bước ra thứ dùng được)

| # | Việc | Kết quả nghiệm thu | Ước lượng |
|---|---|---|---|
| 1 | **Skeleton plugin + marketplace** — plugin.json, marketplace.json, cấu trúc thư mục, hook SessionStart nạp governance + binding rule; `/dlc-init` gồm bước dựng **workspace map** (scan repo → đề xuất → hỏi user chốt) | `/plugin install ai-dlc` chạy được; init trên PCT ra map đúng (app-fe/, app-be/, wiki/docs/) | 0.5–1 ngày |
| 2 | **Port blueprint v3 vào gói** — 17 agents, 14 commands prefix `dlc-`, ~20 checklists (có version), templates DoR/DoD/MSG/RV/DEC/LL; `/dlc-intent` gồm bước snapshot `pinned/` | chạy `/dlc-intent` → dừng đúng Gate A trên project trắng; pinned/ được tạo đủ | 1–1.5 ngày |
| 3 | **Override + doctor + hàng rào cứng + inbox bridge** — resolver 3 lớp, `/dlc-doctor`, PreToolUse hook chặn code-write trước Gate D (theo workspace map), inbox durable + drain SessionStart + token localhost (Tầng 1 §5) | override được dùng đúng; cố Edit code trước Gate D bị hook chặn; Approve lúc session đóng vẫn được xử lý khi mở session mới | 1–1.5 ngày |
| 4 | **Vòng contribute** — `/dlc-contribute` (đóng gói LL + diff → PR), quy ước review PR, CHANGELOG kỷ luật link-LL | 1 LL giả lập đi trọn vòng: override → PR → merge → release 1.0.1 → update → doctor gợi ý xóa override | 1 ngày |
| 5 | **Pilot với PCT Phase 2** — cài plugin vào PCT, chạy intent thật tới Gate D, retro thật ra LL đầu tiên | LL thật đầu tiên được upstream vào 1.1.0 | theo tiến độ PCT |

Tổng phần build (bước 1–4): **~4–5 ngày làm việc** (đã gồm hàng rào cứng + inbox bridge). Control Tower UI để sau như anh/chị đã chốt — bước 1–4 chỉ cần `/status` + `/tower` bản text/HTML tối giản từ generator sẵn có trong kế hoạch cũ.

## 9 · Rủi ro & đối sách

- **Override mọc hoang, mỗi team một kiểu** → doctor cảnh báo override không nguồn LL/DEC; báo cáo quarterly "override nào phổ biến → nên upstream".
- **Plugin update phá luồng đang chạy giữa intent** → giải quyết bằng snapshot `pinned/` (§7): intent đang chạy dùng bản copy đã chốt lúc bắt đầu, intent mới dùng bản mới — update lúc nào cũng an toàn.
- **PR contribute lộ thông tin nội bộ dự án** → `/dlc-contribute` có bước sanitize (bỏ tên khách hàng, số liệu) + preview cho người gửi duyệt trước khi tạo PR.
- **Maintainer nghẽn cổ chai** → SLA review 1 tuần; quá hạn team cứ dùng override (không ai bị chặn).

## 10 · Ba quyết định cần anh/chị chốt trước khi làm bước 1

1. **Repo đặt đâu?** — ✅ đã chốt: **1 repo duy nhất**. Còn lại: đặt ở GitHub org công ty (private) hay repo cá nhân trước, chuyển sau?
2. **Maintainer gói chung là ai?** — anh/chị, hay PMO, hay luân phiên?
3. **Có cần lớp Org overlay ngay không**, hay chỉ 2 lớp (plugin + project) cho gọn ở v1? — đề xuất: **2 lớp ở v1**, thêm org overlay khi có ≥2 team dùng thật.
