# Mô hình workspace · tri thức · vai người — đưa "Phase Atlas" của team vào gói `ai-dlc`

> Trạng thái: **ĐỀ XUẤT — chờ chủ gói chọn** · Ngày: 2026-08-27
> Nguồn: `docs/explore-aidlc-phases-v2.html` (**AI-DLC Phase Atlas**, team dựng 2026-08-19 từ AWS `aidlc-workflows` nhánh `v2` 2.6.16 — 8 mục: mental model · map 33 stage · phase profiles · human control · typical routes · **workspace model** · **bên trong space** · hooks/sensors/skills).
> Hai bản đối chiếu đã có: `aws-aidlc-workflows-v2-vs-ai-dlc.md` (engine + 8 cơ chế máy) và `anthropic-ai-native-sdlc-playbook-vs-ai-dlc.md` (chỗ đặt con người + 10 cơ chế). File này **không nhắc lại** hai bản đó; nó lấy phần **team tự nghĩ** trong Atlas — thứ không nằm trong repo AWS — và trả lời: *cái đó đi vào đâu trong gói.*
> Tài liệu chuẩn vẫn là `whitepaper-ai-dlc-vi.md` (v2 Human-Lead). Mọi đề xuất dưới đây phải giữ ba điểm dừng của v2, không thêm gate.

---

## 0 · Kết luận một trang

1. **Atlas có hai phần.** Phần mô tả 33 stage/gate/hook/sensor là **của AWS** — đã đối chiếu, không mượn mô hình dừng. Phần **team tự nghĩ** là bốn thứ: (a) *quy tắc chốt* "Team ổn định → Space · Feature → Intent · Phần code → Unit · Rule bắt buộc → memory · Tham khảo → knowledge"; (b) mô hình workspace **monorepo trước, space sau**, một team nhiều repo vẫn một space, bảng 5 dòng "có tách space không"; (c) **lớp governance tổ chức** với *controlled projection* thay vì inheritance (Atlas ghi rõ: *không built-in* — AWS không có); (d) bảng **8 vai người theo loại quyết định** + lưu ý "tổ chức phải tự ánh xạ RACI". Bốn thứ này gói **chưa có hình dạng nào**.
2. **Gói hiện tại là "một `.ai-dlc/` = một space ngầm định, một repo"** — `workspace-map.md` chỉ có `code.frontend/backend`, không có `repos:`/`areas:`; AS-IS dựng lại **mỗi intent** (không có `codekb/` tái dùng); không có lớp `knowledge/`; không có `kind` cho intent (bugfix chạy y hệt feature 8 stage); Lead là một người, không có bảng ai-ký-mục-nào. Đây là những lỗ mà Atlas lấp được **mà không đụng luật gate**.
3. **Đề xuất 6 việc** (mục 2–8), gom thành **7.0.0 phần "workspace & tri thức"** đi cùng phương án B: từ vựng chốt · `workspace-map` v2 (`repos` + `areas` + Unit `areas:`) · bốn lớp `governance/ knowledge/ codekb/ intents/` · `governance/raci.md` · `intent.kind` với bảng tuyến · governance projection qua plugin org. Hai việc làm được ngay trên 6.x: `workspace-map` v2 (additive) và `codekb/` promote từ `as-is/` (chỉ thêm thư mục + một bước ở `dlc-discover`).
4. **Một chỗ Atlas và v2 phải hoà giải**: Atlas liệt kê 8 vai người ký ở ~30 gate; v2 có **một Lead, năm việc**. Hoà giải ở mục 6: Lead vẫn là người dẫn duy nhất của flow; RACI chỉ nói **ai ký mục nào trong hồ sơ Gate R / Ranh đỏ** và **ai là `owner:` của ASM** — không sinh thêm điểm dừng.
5. **Một chỗ Atlas cảnh báo đúng thứ gói đang làm**: ví dụ HRM cắt Unit theo code area (`u1-domain`, `u2-api`, `u3-web`, `u4-mobile`) — §4.9 của gói cho phép nhưng bắt khai `releasable: no · released_with:`. Đề xuất giữ **cắt dọc (walking skeleton) là mặc định**, cắt theo area chỉ khi Bolt đã có `contract.md`.

---

## 1 · Trong Atlas, cái gì của AWS, cái gì của team

| Mục Atlas | Nguồn | Đã xử lý ở đâu |
|---|---|---|
| 01 Mental model: *mỗi phase một câu hỏi*, "kết thúc khi" | team viết lại từ stage docs | **mục 7** file này |
| 02 Map 33 stage · dependency `requires_stage` · scope grid | AWS | file AWS §1.2–1.3, không mượn |
| 03 Phase profiles (dùng để · kích hoạt · kết thúc · human) | team tổng hợp | mục 7 |
| 04 Human control: 8 vai theo loại quyết định + "tổ chức phải ánh xạ RACI, segregation-of-duties" | **team** | **mục 6** |
| 05 Typical routes: feature 33 · bugfix 7 · infra 13 · security-patch 10 | AWS scope, team chọn 4 tuyến | **mục 5** (`intent.kind`) |
| 06 Workspace model: Space/Intent/Unit/Code area · monorepo HRM · một team ba repo · nhiều space · **governance projection** · bảng 5 dòng · 4 quy tắc knowledge · **quy tắc chốt** | **team** (AWS chỉ có `spaces/` thô) | **mục 2, 3, 8** |
| 07 Bên trong space: memory/knowledge/codekb/intents — dùng để · load khi nào | AWS layout, team diễn giải "bốn vai trò" | **mục 4** |
| 08 Hooks · Sensors · Skills: chủ động / phản xạ / đồng hồ đo | AWS, team đặt tên | file AWS #4 (sensor); một dòng ở mục 4.5 |

---

## 2 · Quy tắc chốt của team → từ vựng của gói

Atlas: *"Team ổn định → Space · Feature/task → Intent · Phần code → Unit · Rule bắt buộc → memory · Thông tin tham khảo → knowledge. Ít space nhưng ranh giới rõ thường tốt hơn nhiều space rồi phải đồng bộ tài liệu bằng tay."*

| Từ của team | Trong gói (hiện tại) | Đề xuất 7.0.0 |
|---|---|---|
| **Space** = team ổn định, có method · knowledge · state · authority riêng | ngầm định = một `.ai-dlc/` trong một repo | **Giữ ngầm định**: một `.ai-dlc/` = một space. Không thêm `spaces/`. Đa team ⇒ mỗi team một `.ai-dlc/` (mục 3.3) |
| **Intent** = một vòng đời có state, audit, artefact riêng | `INT-NNN` | giữ; thêm `kind:` (mục 5) và `repos:` lúc sinh |
| **Unit** = một lát code được thiết kế và sinh riêng | `UOW-NN` + `releasable`/`session_fit` | giữ; thêm `areas:` (mục 3.1) |
| **Code area** = thư mục/repo thật, *không tự động là space* | `workspace-map.md` `code.frontend/backend` | `areas:` tự do (domain/api/web/mobile/infra…) + `repos:` |
| **memory** = rule bắt buộc, org → team → project → phase | `governance/` + `overrides/` + `pinned/` | đặt tên 4 tầng rõ (mục 4.1); thêm `governance/phases/` tuỳ chọn |
| **knowledge** = tham khảo, không phải mệnh lệnh | không có — nguồn đọc per intent qua Source Reading Plan | `knowledge/` mới (mục 4.2) |
| **codekb** = bản đồ bền vững của code hiện có, per repo | `as-is/` **per intent** | `codekb/<repo>/` promote từ `as-is/` (mục 4.3) |
| **intents/** = hồ sơ vòng đời | `intents/INT-NNN/` | thêm `intents.json` registry + `active-intent` gitignored (mục 4.4) |

Ranh giới Atlas nhấn hai lần và gói phải ghi vào protocol §3: **memory áp đặt cách làm; knowledge cung cấp thông tin; code và test luôn nằm trong repo thật, `.ai-dlc/` chỉ giữ control plane và bằng chứng.** Câu thứ ba gói đã có (workspace map, plan v1 §4); hai câu đầu chưa.

---

## 3 · Workspace — ba cấu hình, một `.ai-dlc/`

### 3.1 Monorepo, một team (mặc định — ví dụ HRM của Atlas)

Atlas: một cross-functional team quản cả `apps/{web,mobile,admin}` · `services/{api,worker}` · `packages/{domain,contracts,api-client,ui}` · `infrastructure/` ⇒ **một space**; feature Leave Request = một intent; Units ghi code vào đúng vùng.

`workspace-map.md` **v2** (additive — 6.x đọc được, key cũ giữ):

```yaml
repos:                      # nơi code sống; một hoặc nhiều
  - id: hrm
    path: .                 # tương đối với thư mục chứa .ai-dlc/
areas:                      # code area — thư mục thật, KHÔNG phải space
  domain:   { repo: hrm, path: packages/domain,  tests: packages/domain/test }
  contracts:{ repo: hrm, path: packages/contracts }
  api:      { repo: hrm, path: services/api,     tests: services/api/tests }
  web:      { repo: hrm, path: apps/web,         tests: apps/web/tests }
  mobile:   { repo: hrm, path: apps/mobile,      tests: apps/mobile/test }
  infra:    { repo: hrm, path: infrastructure }
code:                       # giữ cho 6.x — suy từ areas khi thiếu
  frontend: apps/web
  backend: services/api
docs: { wiki: docs/wiki, api_spec: services/api/openapi.yaml }
```

Unit spec thêm `areas: [api, web]`. Hệ quả máy: `gate_guard`/red-line guard chặn theo `areas` của Unit đang mở thay vì hai path cứng; tower vẽ Unit → area; doctor WARN khi Bolt ghi file ngoài `areas` khai (trùng playbook #4 "kiểm trôi plan").

**Cắt Unit theo area hay cắt dọc?** Atlas ví dụ `u1-domain → u2-api → u3-web → u4-mobile`. Với §4.9: `u1-domain` một mình không `releasable` ⇒ phải khai `released_with: UOW-02` và Showcase chỉ mở ở Unit cuối chuỗi — Lead **không có gì để nhìn** cho tới đó, trái §IV. Đề xuất ghi vào `unit-plan.md` template: **mặc định cắt dọc** (một Unit chạm nhiều area, ra được một thứ để bấm — chính "walking skeleton" của AWS delivery-planning và "one change = one PR" của playbook); cắt theo area chỉ khi Bolt đầu đã chốt `contract.md` (Atlas 2.8 contract-design) và mọi Unit theo area khai `released_with:`.

### 3.2 Một team, nhiều repo (`hrm-web/ hrm-api/ hrm-mobile/` mỗi cái `.git` riêng)

Atlas: *"Repository là nơi code sống; space là nơi team giữ method, knowledge và workflow history."* Gói hiện không chạy được cấu hình này — `.ai-dlc/` nằm trong một repo, `gate_guard` resolve path theo `cwd`.

Đề xuất: `.ai-dlc/` nằm ở **thư mục workspace cha** (`hrm-workspace/.ai-dlc/`), `repos:` khai path tương đối `hrm-web/` `hrm-api/`…; intent ghi `repos: [web, api, mobile]` **lúc sinh** (Atlas: "intent registry giữ tập repo tại lúc birth"); Bolt ghi code vào repo của area; `dlc-resume` và hook chạy từ workspace cha (`session_start.sh` tìm `.ai-dlc/` đi lên tối đa 2 cấp). Commit `.ai-dlc/` ở đâu? Workspace cha là repo riêng (khuyến nghị — đúng "intent home" của playbook stage 1) hoặc không commit (mất truy vết — doctor WARN).

### 3.3 Nhiều team ổn định trên một monorepo

Atlas: tách **theo ownership tổ chức, không theo folder**; mỗi space state riêng; *"AI-DLC chưa tạo dependency graph xuyên space"* — nối bằng contract trong code, PR/CI, human handoff.

Đề xuất: **không** thêm `spaces/` vào gói. Mỗi team một `.ai-dlc/` đặt ở thư mục sở hữu (`apps/web/.ai-dlc/` cho employee-experience, `services/.ai-dlc/` cho hr-platform, `infrastructure/.ai-dlc/` cho platform-engineering); `session_start.sh` chọn `.ai-dlc/` gần `cwd` nhất. Liên kết xuyên team = **Ranh đỏ #3** (đổi public API/contract có consumer ngoài đội) → `RED` + `DEC` — đúng cái Atlas gọi là "human handoff" và gói đã có tên. Tower mỗi space một cổng; muốn xem chung thì `dlc-tower --all` gom (làm sau).

### 3.4 Bảng "có tách không" → câu hỏi ở `dlc-init`

Atlas cho 5 dòng; gói đưa thành **một câu hỏi duy nhất** ở bước 3 của `dlc-init`, trước khi dựng workspace map:

> Đội nào **duyệt** thay đổi ở vùng code này? Nếu cùng một nhóm người duyệt cho mọi vùng ⇒ một `.ai-dlc/`. Nếu hai nhóm khác nhau, có practice và approval riêng ⇒ mỗi nhóm một `.ai-dlc/` tại thư mục họ sở hữu.

Không hỏi "frontend hay backend", không hỏi "mấy repo" — hai câu đó Atlas đã chứng minh là câu sai.

---

## 4 · Bốn lớp trong space → layout `.ai-dlc/` 7.0.0

```
.ai-dlc/
├── workspace-map.md                 # repos · areas · docs (mục 3.1)
├── governance/                      # = memory: RULE BẮT BUỘC, 4 tầng (4.1)
│   ├── org/        (projection, read-only, sync qua PR — 4.1 & mục 8)
│   ├── dor.md dod.md sizing.md leadership.md red-lines.md raci.md
│   ├── phases/inception.md construction.md operations.md   (tuỳ chọn)
│   ├── decisions-log.md changelog.md risks.md tech-debt-register.md
│   └── review.md                    # REVIEW.md của playbook #7
├── overrides/                       # tầng dự án đè gói (giữ nguyên plan v1 §3)
├── knowledge/                       # = THAM KHẢO, không phải mệnh lệnh (4.2)
│   ├── shared/     glossary.md api-conventions.md …
│   ├── by-role/    ba/ be-dev/ fe-dev/ security/ tech-lead/ qa/
│   └── documents/  (bản gốc PDF/spec/policy — không ingest, chỉ trỏ)
├── codekb/<repo-id>/                # = BẢN ĐỒ CODE bền vững, per repo (4.3)
│   ├── static-model.md dynamic-model.md decisions-inventory.md
│   └── freshness.md                 # git HEAD · scope · ngày · CURRENT|STALE
├── context-memory/                  # như 6.x
│   ├── intents.json                 # registry (4.4)
│   ├── comms/ handoffs/ session/ reviews/ escalations/ lessons-learned/
│   ├── assumptions/ checkpoints/ showcases/ steer/ gates/ red-lines/   (v2)
│   └── intents/INT-NNN/  (pinned/ · as-is/ chỉ còn source-ledger.md + delta)
├── active-intent                    # gitignored, per clone (4.4)
├── inbox/ tower/
```

### 4.1 `governance/` = memory, bốn tầng có tên

Atlas: memory load *cộng dồn* org → team → project → phase; project **bổ sung, không âm thầm xoá** rule cấp trên; phase rules "chỉ cần trong một phase, giúp context gọn". Gói đã có ba tầng nhưng chưa gọi tên:

| Tầng Atlas | Trong gói | Ai đổi | Ghi chú |
|---|---|---|---|
| org | **`governance/org/`** (mới) — projection từ canonical của tổ chức, read-only trong dự án | chủ canonical, qua PR (mục 8) | AWS: "không bao giờ ghi org" — giữ |
| team ≈ gói | `plugin/templates/governance/*` + `skills/checklists/*` | chủ gói, qua LL → Gate G | tầng "framework" |
| project | `governance/*.md` + `overrides/` | Lead của dự án, qua DEC | đã có |
| phase | `governance/phases/<pha>.md` (tuỳ chọn) | Lead | orchestrator nạp **đúng file pha** vào `read_first` của HOF — thay vì nạp cả governance. Trả §10 ngân sách context |
| intent | `pinned/` | tự động lúc sinh intent | đã có; giữ luật "không đổi luật giữa intent" |

Luật thứ tự: tầng dưới **thêm hoặc siết**, không nới tầng trên; nới phải là `override` có `source: DEC` — doctor đã kiểm override mồ côi, thêm kiểm "override nới rule org" ⇒ FIX.

### 4.2 `knowledge/` = tham khảo (mới)

Atlas: *"Knowledge là điều AI cần biết về domain và team… Tài liệu chỉ thuộc một feature nên associate với intent thay vì khiến toàn space phải đọc."* Bốn quy tắc của team: shared thật mới để shared · một file một chủ đề · scope document theo intent · prune theo nhịp.

Trong gói:
- `knowledge/shared/` — nhỏ, ổn định, mọi vai đọc (glossary, API conventions). `session_start.sh` **không** in; `dlc-intent`/`dlc-discover` đưa vào **Source Reading Plan** như nguồn `type: knowledge` — nghĩa là vẫn qua **No-unread-source** (§4.8): đọc rồi phải có dòng trong `source-ledger.md`. Đây là chỗ gói chặt hơn Atlas và giữ.
- `knowledge/by-role/<vai>/` — chỉ vào `read_first` của HOF cho vai đó (Atlas: "tránh làm loãng context của agent không liên quan").
- `knowledge/documents/` — bản gốc; gói **không** ingest/DocumentKB (AWS có tool riêng; mình không có engine). Trỏ path trong Source Reading Plan là đủ.
- Tài liệu chỉ của một intent → để trong `intents/INT-NNN/sources/`, không lên `knowledge/`.
- Prune: `dlc-retro` thêm mục "knowledge nào không được ledger nào trỏ tới trong 2 intent gần nhất" → ứng viên xoá (Atlas: "knowledge cũ hoặc mâu thuẫn được đọc literal với trọng lượng ngang nhau").

### 4.3 `codekb/<repo>/` = bản đồ code bền vững (promote từ `as-is/`)

Vấn đề hiện tại: stage 2 dựng `as-is/static-model.md dynamic-model.md decisions-inventory.md` **mỗi intent**, trên cùng một codebase. INT-002 và INT-003 của PILOT đọc lại cùng backend. Atlas: codekb per repo, dùng lại qua nhiều intent, có `reverse-engineering-timestamp.md` với freshness CURRENT/STALE/UNKNOWN_SCOPE; người quyết **reuse hay rescan**.

Đề xuất:
- Khi intent **đóng** (stage 8), `dlc-accept`/`dlc-release` promote `as-is/*` lên `codekb/<repo>/` kèm `freshness.md` (git HEAD lúc đọc · areas đã quét · ngày · ledger nào chứng minh).
- `dlc-discover` của intent kế: đọc `freshness.md` trước; so HEAD hiện tại — nếu diff chạm `areas` của intent ⇒ `STALE` ⇒ quét **delta** (chỉ file đổi) và ghi `as-is/delta.md`; không chạm ⇒ `CURRENT` ⇒ reuse. Quyết định reuse/rescan là **`ASM`** có `reversal_cost: thấp` (Atlas đặt human gate ở đây — v2 không), Lead thấy ở `CP` stage 2.
- **No-unread-source giữ nguyên**: reuse codekb vẫn phải có dòng `source-ledger.md` trỏ `codekb/<repo>/static-model.md#mục` với `status: read` + evidence là `freshness: CURRENT`. Không có ledger ⇒ vẫn `planned` ⇒ doctor FIX.
- Làm được trên 6.x: chỉ thêm thư mục + bước promote + bước kiểm freshness; không đổi gate.

### 4.4 `intents/` = hồ sơ vòng đời — registry + con trỏ per clone

Atlas: `intents.json` (UUID · slug · scope · repos · status) · `active-intent` **gitignored** để "không tranh chấp khi cộng tác" · `audit/<host>-<clone>.md` append-only per clone.

Gói hiện: `dlc-resume` quét mọi `status.md`; nhiều intent song song thì "đang làm cái nào" nằm trong đầu người. Đề xuất:
- `context-memory/intents.json`: `{id, slug, kind, repos, areas, mode, status, created}` — `dlc_state.py` (AWS #2) là nơi duy nhất ghi; tower đọc registry thay vì glob.
- `.ai-dlc/active-intent` gitignored, per clone; `dlc-resume` đọc nó trước, không có thì hỏi.
- Đánh số `HOF/MSG/RV-NNNN` tuần tự **sẽ đụng nhau** khi hai người cùng commit `.ai-dlc/` — vấn đề thật khi đa clone (mục 3.2/3.3). Đề xuất tối thiểu: `session/log/` shard theo host (`SES-<host>-NNN`); ID còn lại cấp qua `dlc_state.py` trong cùng commit; đụng thì rebase. Không dùng UUID (mất tính đọc được của tower).

### 4.5 Skill · Hook · Sensor — gọi đúng tên trong gói

Atlas: *"gọi Skill khi chủ động muốn một outcome · dựa vào Hook khi enforcement phải tự xảy ra đúng event · dùng Sensor khi cần tín hiệu đo được, tái lập được."* Gói: `dlc-*` = skill; `gate_guard`/red-line/`session_start` = hook; **sensor = doctor chạy tại PostToolUse** (AWS #4). Ghi ba dòng này vào protocol §0 để người viết agent mới không nhét enforcement vào prompt.

---

## 5 · Tuyến theo loại intent (`kind`) — một gói, không phải một cỡ

Atlas mục 05: feature 33 · bugfix 7 (*"Hiểu code, khóa tiêu chí fix, sửa và kiểm thử; không ceremony sản phẩm/operation"*) · infra 13 · security-patch 10. Gói hiện chạy **8 stage cho mọi intent**; một bugfix ở PILOT vẫn phải qua intent-plan 3 phần, validate, unit-plan.

Đề xuất `intent.kind` khai ở `dlc-intent` (AWS #6 "mode per intent" đã đề xuất `leadership.mode` per intent — đây là trục thứ hai, độc lập):

| Stage của gói | `feature` (mặc định) | `bugfix` | `refactor` | `infra` | `security-patch` | `poc` |
|---|---|---|---|---|---|---|
| 1 Intent plan | đủ 3 phần · `CP-01` chờ đích | Intent + Source Plan **ngắn** (nguồn = codekb + repro) · `CP-01` | đủ | đủ | đủ + ranh đỏ #7 luôn bật | Intent + đích **đo được** · `CP-01` |
| 2 Discovery | as-is/codekb | codekb delta quanh lỗi | codekb | practices + NFR hiện trạng | codekb + threat | bỏ nếu greenfield |
| 3–4 Validate → ASM | có | **bỏ** (ASM ghi thẳng ở Bolt) | có | có | có | bỏ |
| 5 Unit plan | có · Mốc chờ thứ tự | **một Unit tự sinh** | có | có | một Unit | một Unit |
| 6 Bolt | đủ 4 chặng | Domain/Logical **gộp**; **test fail trước** (playbook #3) | đủ | Logical + IaC | Logical + test + security specialist bắt buộc | code + test tối thiểu |
| Showcase | có | Showcase = test đỏ→xanh + repro | có | có (bảng trước/sau) | có | có |
| 7–8 Gate R · Release | 9 mục | 9 mục, mục 1–2 thường rỗng | 9 mục | 9 mục + mục 7 rollback đã thử | 9 mục | **`hold` mặc định** — POC không release |

Luật máy: `status.md` ghi `route:` (danh sách stage RUN/SKIP suy từ `kind`); **stage bị skip không phải blocker** (Atlas: *"stage bị scope/condition bỏ qua không biến thành blocker giả"*); doctor kiểm `produces` chỉ trên stage RUN (AWS #7). Đổi `kind` giữa chừng ⇒ `STR` + tính lại route, không đổi ngầm.

Playbook #8 (`dlc-intent --from <incident>`) sinh intent `kind: bugfix` hoặc `security-patch` — hai trục khớp nhau.

---

## 6 · Vai người theo loại quyết định → `governance/raci.md`

Atlas (team): 8 vai — Sponsor/PO (value, scope, acceptance) · Business/Domain expert (rules, exception) · UX/Accessibility · Architect/Tech Lead (boundaries, ADR, blast radius) · Developer (khả thi, migration) · QA (Testing Posture, coverage) · Security/Compliance (threat, privacy, evidence) · Platform/SRE/Release (rollback, SLO, production approval). Và: *"Tổ chức vẫn phải ánh xạ sang RACI, segregation-of-duties và approval policy thực tế của mình."*

White paper v2: **một Lead, năm việc** — và Gate R có 9 mục, Ranh đỏ có 9 dòng, ASM có `owner:`. Hoà giải:

- **Lead vẫn là người duy nhất dẫn flow** (đặt đích · xác nhận `CP-01` · bẻ lái · Showcase · ký Gate R). Không thêm điểm dừng cho vai nào.
- `governance/raci.md` trả lời **ba câu** của máy, không hơn:
  1. Gate R mục *n* **ai ký** (mục 5 bảo mật → Security; mục 7 đường lùi → Release/SRE; mục 8 ghi chú cho khách → PO; các mục còn lại → Lead). Hồ sơ Gate R có cột `signed_by:` per mục; thiếu chữ ký của vai khai ⇒ `hold`.
  2. Ranh đỏ dòng *n* **ai ra `DEC`** (dòng 1 deploy → Release; dòng 2 migration phá huỷ → Tech Lead; dòng 4 chi tiền → Sponsor; dòng 7 auth/PII → Security…).
  3. `ASM.owner:` là **tên người**, chọn từ bảng theo loại quyết định (nghiệp vụ → PO/Domain; kỹ thuật → Tech Lead; kiểm thử → QA). Tower "Cần tôi quyết" **lọc theo người xem** — mỗi vai chỉ thấy thẻ của mình; Lead thấy tất cả.
- Segregation-of-duties tối thiểu, kiểm được: người ký Gate R mục 4 (kiểm thử) **không** là người ghi `result_check` cho Bolt đó — doctor so tên.
- Template `raci.md` ship với gói có 8 vai của Atlas làm **cột**, 9 mục Gate R + 9 dòng ranh đỏ + 3 loại ASM làm **hàng**; dự án điền tên. Vai không có người ⇒ ghi `Lead` — không để trống.

---

## 7 · Mỗi pha một câu hỏi — bảng cho protocol §1

Atlas: *"Initialization tạo đường ray. Ideation xác nhận lý do. Inception biến lý do thành hợp đồng xây dựng. Construction biến hợp đồng thành code đã kiểm thử. Operation đưa code vào đời thực và khép vòng học hỏi."* Gói có ba pha nhưng protocol §1 chưa nói *pha trả lời câu gì* và *kết thúc khi nào* — nên agent hay kéo dài Inception.

| Pha gói | Câu hỏi pha trả lời | Kết thúc khi | Điểm dừng v2 trong pha |
|---|---|---|---|
| **Inception** (stage 1–5) | *Vì sao làm, cho ai, đích đo được là gì — và xây chính xác cái gì, cắt ra sao?* | `unit-plan.md` có Unit đầu `releasable` + đủ điều kiện Showcase; mọi `ASM` đảo đắt đã qua Mốc chờ | `CP-01` chờ đích · `CP` stage 2–4 · Mốc chờ thứ tự Unit |
| **Construction** (stage 6) | *Thiết kế, code và kiểm chứng thế nào — và Lead đã nhìn thấy nó chạy chưa?* | mọi Unit `done` (Showcase ≥ 1, FB đóng, `rv:`/`self_verify` thật) | Showcase `SC` · Team Agreement nội bộ · Ranh đỏ nếu chạm |
| **Operations** (stage 7–8) | *Đưa lên, quan sát, và học được gì để mở intent kế?* | Gate R `release` + deploy + telemetry có người nhận + LL ghi (Mốc chờ) + (7.0.0) intent kế sinh từ finding nếu có | **Gate R** · Ranh đỏ #1 · Mốc chờ LL |

Kèm luật Atlas về dependency, viết lại cho gói: *"predecessor chỉ tính trên tuyến đã compile (`route:` của `kind`); stage SKIP không phải blocker."*

---

## 8 · Governance projection — org → space, controlled, không inheritance

Đây là phần **team nghĩ thêm ngoài AWS** và ghi rõ "*Không built-in*": `governance/organization-rules/{secure-coding,git-workflow,testing-baseline}.md` + `organization-knowledge/{architecture-principles,api-conventions,data-classification}.md` là canonical; mỗi space chỉ nhận phần phù hợp qua **PR hoặc CI có kiểm soát**; "*Không coi default là parent live*"; pipeline không overwrite `team.md`/`project.md`.

Gói có sẵn cơ chế gần nhất: **plugin marketplace**. Đề xuất:
- Tổ chức phát hành **plugin thứ hai `ai-dlc-org-<tên>`** (cùng marketplace hoặc marketplace nội bộ) chứa `governance/org/*.md` + `knowledge/shared/*.md` chuẩn của tổ chức + checklist override. `dlc-init` (và `dlc-doctor`) nếu thấy plugin org được cài ⇒ **copy** vào `.ai-dlc/governance/org/` và `.ai-dlc/knowledge/shared/` kèm `source: ai-dlc-org@<version>` — copy, không symlink (Atlas: "tránh symlink"); dự án đọc bản copy, không đọc live.
- Cập nhật = bump plugin org → `dlc-doctor` báo `governance/org/` lệch version ⇒ Lead chạy `dlc-init --sync-org` ⇒ diff hiện trên tower ⇒ DEC ghi nhận. Đây chính là "explicit PR / controlled CI sync" của Atlas, bằng công cụ có sẵn.
- Tầng org **không override được** bằng `overrides/` (doctor FIX) — khác với tầng gói (override được). Đây là điểm playbook gọi là managed settings và AWS gọi là "never write org".
- Chưa có tổ chức nào ship plugin org ⇒ mục này là **cơ chế**, chưa phải việc; ghi vào protocol §3 và để `governance/org/` rỗng với README.

---

## 9 · Nối với hai bản đối chiếu trước — không trùng, chỉ trỏ

| Việc ở file này | Dựa trên / trùng với | Quan hệ |
|---|---|---|
| `workspace-map` v2 `repos`/`areas`, Unit `areas:` | playbook #4 (plan drift), AWS #7 (produces/consumes) | cung cấp **dữ liệu** cho hai cơ chế đó |
| `codekb/` + freshness | AWS §1.2 reverse-engineering (không mượn engine), §4.8 của gói | giữ No-unread-source, chỉ tái dùng kết quả |
| `governance/` 4 tầng + `phases/` | AWS #5 diary/learnings (nơi LL sinh ra), §10 ngân sách context | tầng nào nhận LL: project mặc định, gói khi qua Gate G |
| `intents.json` + `active-intent` | AWS #2 (`dlc_state.py` là nơi ghi) | registry là một file nữa `dlc_state.py` sở hữu |
| `intent.kind` + `route:` | AWS #6 (mode per intent), playbook #8 (`--from incident`) | hai trục: `mode` (lead/gatekeeper) × `kind` (tuyến) |
| `raci.md` | white paper §V Gate R, §VI Ranh đỏ, §III `ASM.owner` | không thêm điểm dừng, chỉ điền tên |
| Governance projection qua plugin org | plan v1 §3 override 3 lớp, playbook managed settings | tầng thứ tư, không override được |

---

## 10 · Quyết định chủ gói — ĐÃ CHỐT 2026-08-27

| # | Câu hỏi | Quyết định | Đi vào |
|---|---|---|---|
| 1 | Một `.ai-dlc/` = một space, không thêm `spaces/` | **Chấp nhận** | 6.2.0: protocol §3, `dlc-init` hỏi một câu (3.4), template map v2 |
| 2 | Hai việc additive làm trên 6.x hay dồn 7.0.0 | **Làm 6.2.0 trước** | 6.2.0: `workspace-map` v2 + `codekb/` promote/freshness (CHANGELOG 6.2.0) |
| 3 | `intent.kind` 6 tuyến, `bugfix` bỏ stage 3–5 | **Theo đề xuất** — là đổi luật | 7.0.0 cùng phương án B; chưa thêm `kind` nào ngoài 6 tuyến mục 5 |
| 4 | `raci.md`: vai riêng ký Gate R mục 5/7/8 hay Lead ký thay | **Dự án nhỏ, người làm ký thay vẫn được** | 7.0.0: template `raci.md` mặc định `Lead`; doctor WARN khi mục bảo mật do Lead ký mà Unit chạm auth/PII |
| 5 | Đa repo (3.2) | **Theo đề xuất** — cho phép, không test kỹ | 6.2.0: hook/script tìm `.ai-dlc/` đi lên 2 cấp; path tương đối thư mục chứa `.ai-dlc/` |
| 6 | Plugin org cho governance projection | **Chưa có ý định** | protocol 7.0.0 chỉ ghi cơ chế (mục 8); `governance/org/` không tạo ở 6.2.0 |

Việc còn treo sang 7.0.0 từ file này: `governance/` 4 tầng có tên + `phases/` (4.1) · `knowledge/` (4.2) ·
`intents.json` + `active-intent` (4.4) · `intent.kind` + `route:` (5) · `raci.md` (6) · bảng "mỗi pha một câu
hỏi" vào protocol §1 (7).

---

## Phụ lục · Ví dụ HRM của Atlas viết bằng từ của gói

```
hrm-workspace/                          # 3.2: một team, ba repo → .ai-dlc/ ở cha
├── .ai-dlc/
│   ├── workspace-map.md                # repos: web, api, mobile · areas: web, api, mobile, domain(api)
│   ├── governance/  knowledge/shared/hrm-glossary.md  codekb/{web,api,mobile}/
│   └── context-memory/
│       ├── intents.json                # INT-001 leave-request · kind: feature · repos: [web, api, mobile]
│       └── intents/INT-001/
│           ├── intent-plan.md          # CP-01 chờ đích: "nhân viên tự nộp và theo dõi đơn nghỉ"
│           ├── assumptions/            # ASM-001 quyền duyệt đa cấp · owner: PO · default_if_silent: một cấp
│           ├── unit-plan.md            # cắt DỌC: UOW-01 "nộp đơn + xem trạng thái" (areas: domain, api, web)
│           │                           #          UOW-02 "duyệt đơn" (areas: api, web)
│           │                           #          UOW-03 "mobile" (areas: mobile · released_with: UOW-01)
│           └── units/UOW-01/bolts/BOLT-01/  contract.md tasks.md evidence/
│       └── showcases/SC-01/README.md   # chạy ở: hrm-web dev + hrm-api dev · bấm 6 bước
├── hrm-web/   .git   src/features/leave/  tests/leave/
├── hrm-api/   .git   src/modules/leave/   tests/leave/
└── hrm-mobile/.git   lib/features/leave/  test/leave/
```

So với Atlas (`u1-domain → u2-api → u3-web → u4-mobile`): cùng số area, khác cách cắt — `UOW-01` ra được thứ để bấm ngay sau Bolt đầu, Lead phản hồi trên sản phẩm ở ngày 1 thay vì sau Unit thứ 3.
