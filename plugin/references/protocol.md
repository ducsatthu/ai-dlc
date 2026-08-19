# AI-DLC Protocol — giao thức chung (v6)

> MỌI agent và skill của plugin PHẢI tuân thủ file này. Tài liệu phương pháp gốc: white paper AI-DLC
> (`docs/whitepaper-ai-dlc-vi.md` trong repo plugin). Mâu thuẫn → white paper thắng.

## 1. Phân cấp & pha

**Project → Intent → Unit → Bolt → Task.** Một Unit chạy qua một hoặc nhiều Bolt, song song hoặc tuần tự.
Mỗi Bolt: `Domain Design → Logical Design + ADR → Code + Unit Test`.

Ba pha (white paper) ↔ 8 stage:
- **Inception** = stage 1 Request → 2 Discovery → 3 Validation → 4 Clarify → 5 Units (nghi thức Mob Elaboration).
  Artefact per Unit: user-stories, NFR, risks, (PR-FAQ tùy chọn), Bolt đề xuất.
- **Construction** = stage 6 (Mob Construction). Brown-field: stage 2–3 nâng mã lên mô hình tĩnh + động trước.
- **Operations** = stage 7 Acceptance → 8 Release → Deployment Unit, telemetry, runbook.

**Nguyên tắc xuyên suốt: ở mọi điểm phân rã, AI đề xuất trước — con người xác nhận trước khi đi tiếp.**

### 1.0 Bolt nằm TRONG Unit — và bolt là bốn chặng, không phải một cái nhãn

```
units/UOW-NN/
└── bolts/BOLT-01/          # 1..n bolt cho MỘT unit — chạy song song hoặc tuần tự
    ├── domain-design.md    # ① mô hình nghiệp vụ của phạm vi bolt, độc lập hạ tầng
    ├── logical-design.md   # ② áp NFR + pattern
    ├── adr/ADR-NN.md       #   mỗi quyết định kiến trúc một file
    ├── contract.md         #   freeze trước khi FE/BE chạy song song
    ├── tasks.md            # ③ TSK-NN có approver + depends_on
    └── evidence/           # ④ bằng chứng AC đã pass — nguồn của Gate F
```

- **Không có bolt = các chặng đó không xảy ra.** Bolt không phải thư mục hình thức: nó là chỗ bốn chặng
  `Domain Design → Logical Design + ADR → Code + Unit Test` để lại dấu vết. Một Unit đi thẳng từ spec sang
  code là một Unit **bỏ qua thiết kế**, và việc bỏ qua đó phải là một quyết định có DEC, không phải một
  chuyện tự xảy ra. *(Ca thật: 14/18 unit không có thư mục bolt nào, không DEC nào nói bỏ bước design.)*
- **Tên bolt trong HOF không chứng minh bolt tồn tại.** `scope: …/BOLT-01` là chuỗi tự do; coordinator phải
  tạo thư mục **trước** khi phát HOF (§4.13 · doctor kiểm chéo hai chỗ này).
- Unit chạy nhiều bolt thì `unit-plan.md` phải nói rõ **song song hay tuần tự**, và bolt nào freeze contract
  nào — đó là thứ quyết định task nào chờ task nào.
- Control Tower hiện từng chặng của từng bolt kèm trạng thái có/không, đọc thẳng từ đĩa.

### 1.0c Điểm dừng trong Bolt — chỗ công việc PHẢI đứng lại chờ ai đó ký

Bolt không chạy một mạch từ design tới xong. Giữa các chặng có **điểm dừng**, và mỗi điểm dừng phải nói rõ
**ai giữ**: agent (một reviewer khác góc nhìn) hay **người** (thứ agent không được tự quyết).

| # | Điểm dừng | Sau chặng | Ai giữ | Đã dừng thật = có gì trên đĩa |
|---|---|---|---|---|
| 1 | **Soát thiết kế** | Logical Design + ADR | theo **tầng review** của Unit (§4.17): `none` = dev tự đối chiếu checklist, dừng thật ở Gate E(a) · `peer`/`specialist` = agent đúng vai | tier `none`: mục design trong `evidence/self-verify.md` · tier khác: `RV-NNN` verdict `approve*` |
| 2 | **Freeze contract** | contract.md | agent ↔ agent (BE ↔ FE) | `contract.md` có `FROZEN vN`; sau đó đổi = DEC |
| 3 | **Gate E(a) checkpoint design** | trước khi code | **người** | `gate_open: E` → `gates_passed` có `E` |
| 4 | **Soát code** | Code + Unit Test | theo **tầng review** của Unit (§4.17): `none` = self-verify có bằng chứng · `peer` = dev còn lại trong bolt · `specialist` = đúng MỘT vai theo trigger | tier `none`: `evidence/self-verify.md` đủ mục, có con trỏ · tier khác: `RV-NNN` verdict `approve*` |
| 5 | **Gate E(b) demo** | sau fix | **người** | `gate_open: E` lần hai |

> Điểm dừng 1 và 4 **có điều kiện theo tầng** từ v6 (§4.17) — nhưng điểm dừng 3 và 5 (của NGƯỜI) thì
> **không bao giờ** bị tầng nào bỏ: unit tier `none` vẫn dừng ở Gate E(a) và E(b) như mọi unit khác.
| + | **Escalation** | bất kỳ lúc nào | **người** (qua tech-lead) | `escalations/ESC-NNN.md` `status: open`, hoặc MSG `type: escalation` |
| + | **Câu hỏi CHẶN Unit** | bất kỳ lúc nào | **người** | câu `CHẶN UOW-NN` còn mở trong `open-questions-tech.md` |

**Năm trạng thái của một điểm dừng** — Control Tower vẽ đúng năm cái này, suy từ `reviews/` · `comms/` ·
`escalations/` · `gate_open`, **không suy từ trạng thái tự khai của agent**:

- `chưa tới` — chặng trước chưa xong.
- `đang chờ agent` — đã gửi review-request, chưa có verdict. *(Đây là trạng thái, KHÔNG phải "xong": HOF
  không được đóng `done` ở đây — §4.12.)*
- `đang chờ NGƯỜI` — gate mở, escalation chưa có chủ, hoặc câu hỏi chặn chưa chốt. Việc đứng im hợp lệ,
  nhưng phải nhìn thấy được là **đang đứng ở người nào**.
- `bị trả lại` — verdict `request-changes`. Hai lần trả lại cùng một điểm ⇒ chuyển thành escalation của người.
- **`đã đi qua mà không dừng`** — chặng sau đã xong nhưng không có dấu vết nào ở điểm dừng. Đây là trạng
  thái đắt nhất và im lặng nhất: mọi thứ khác vẫn chạy, sản phẩm vẫn dùng được, chỉ khả năng truy vết là
  mất. *(Ca thật: 17 unit đi qua cả hai điểm review và cả hai checkpoint Gate E mà không dừng lần nào.)*

Agent **không được tự quyết** ở điểm dừng của người. Gặp một trong bốn ca sau là dừng và mở đường cho người:
bất đồng hai lần cùng một điểm · phát hiện logic sai từ gốc · tài liệu thiếu gây hiểu nhầm · thay đổi chạm
scope/business. Không tự vá, không "chọn phương án hợp lý nhất rồi đi tiếp".

### 1.0b Brownfield: đầu pha có thêm chặng NÂNG MÃ LÊN MÔ HÌNH

Dự án brownfield (`brownfield_type` khác rỗng) bắt buộc thêm hai artefact ở stage 2–3, **trước** khi bàn tới
thay đổi: `as-is/static-model.md` (cấu trúc mã hiện có) và `as-is/dynamic-model.md` (luồng chạy thật, không
phải luồng mô tả trong tài liệu). Greenfield không có chặng này. Thiếu hai file này ở dự án brownfield =
đang thiết kế trên trí nhớ về hệ thống, không phải trên hệ thống.

### 1.1 Stage 1 KHÔNG chỉ là intent — là INTENT PLAN (bắt buộc, v2)

Nguyên nhân hỏng phổ biến nhất của flow này: agent hạ nguồn (FE/BE) làm sai vì **khâu đọc bối cảnh ở đầu
đọc thiếu nguồn, đọc sai nguồn, hoặc đọc nguồn cũ**. Sai ở stage 1 lan xuống toàn bộ hạ nguồn và chỉ lộ ra
lúc code. Vì vậy stage 1 phải sinh **một tài liệu markdown hoàn chỉnh, tự đủ** — `intent-plan.md` — gồm
đúng 3 phần, và Gate A duyệt chính tài liệu này (không duyệt bằng tóm tắt miệng):

| Phần | Nội dung | Ai viết |
|---|---|---|
| 1 · Intent | problem, outcome đo được, priority, brownfield type, vùng ảnh hưởng, mâu thuẫn cần confirm | `dlc-intent-analyst` |
| 2 · Source Reading Plan | **bảng liệt kê từng nguồn sẽ đọc**: path/địa chỉ · loại · vì sao cần · **thông tin cụ thể cần lấy** · ai sở hữu · độ ưu tiên · rủi ro nếu thiếu · trạng thái | `dlc-source-planner` |
| 3 · Provisional Unit Map | phân rã tạm thành Units, mỗi Unit: User Story · NFR · Rủi ro · **`releasable` + `session_fit` có con số** (§4.9) · ước lượng có breakdown · nguồn nào chứng minh · AC nháp | `dlc-intent-analyst` (dựa phần 2) |

Phần 2 phải **quét thật** (Glob/Grep/ls trên workspace-map) — không được liệt kê nguồn theo trí nhớ hay
theo suy đoán. Nguồn không tồn tại phải ghi `missing` kèm hệ quả, không im lặng bỏ.

Phần 3 là **provisional** (dự kiến): nó chốt "sẽ chia theo trục nào và mỗi mảnh nặng bao nhiêu", còn bản
Unit cuối cùng chốt tại Gate D sau khi đã đọc AS-IS. Provisional ≠ nháp cẩu thả: vẫn phải đủ US/NFR/risk/ước lượng.

## 2. Gates (điểm dừng bắt buộc — không agent nào được vượt)

| Gate | Vị trí | Người quyết | Tài liệu bắt buộc (gate_doc) |
|---|---|---|---|
| A | sau stage 1 | Duyệt **intent-plan.md**: outcome đúng? nguồn đọc đã đủ chưa? unit map hợp lý? | `intent-plan.md` |
| B | sau stage 3 | AS-IS model đúng thực tế? coverage nguồn đủ? | `as-is/source-ledger.md` |
| C | sau stage 4 | Chốt open questions **nghiệp vụ** (câu kỹ thuật đi lối khác — §4.10) | `open-questions-business.md` |
| D | sau stage 5 | Approve **unit-plan.md** (Units + Bolt plan + DoD/DoR version); câu tech `CHẶN` phải đã chốt | `unit-plan.md` |
| E | trong mỗi Bolt | (a) OK design + ADR + contract; (b) OK demo sau review | `bolts/BOLT-NN/logical-design.md` |
| F | sau stage 7 | UAT / approve deploy (cần: QC evidence đủ + security MUST = 0) | `acceptance.md` |
| G | sau retro | Duyệt lesson + patch skill | `lessons-learned/LL-NNN.md` |
| động | bất kỳ | Escalation: 2× request-changes, logic sai từ gốc, tài liệu thiếu chạm scope | MSG escalation |

Khi gate mở: orchestrator ghi gate vào `status.md` (kèm `gate_doc:` trỏ tới tài liệu), tạo entry Gate Queue,
cập nhật tower, gửi PushNotification (nếu có), rồi **KẾT THÚC LƯỢT** với thông báo rõ cần người quyết gì.

### 2.1 Luật preview — approve mù bị cấm

- Mỗi gate PHẢI có `gate_doc` là **một file markdown hoàn chỉnh, tự đủ**: người đọc quyết được mà không
  phải mở file khác. Không có gate_doc → không được mở gate.
- Control Tower render **toàn văn** gate_doc. Nút Approve chỉ bật sau khi người dùng đã mở và xác nhận
  đã đọc bản preview; tower gửi kèm cờ `previewed: true` và server từ chối approve thiếu cờ này.
- Ba verdict hợp lệ: `approve` · `request-changes` (kèm nội dung cần sửa — BẮT BUỘC) · `reject` (kèm lý do).

### 2.2 Vòng điều chỉnh (request-changes)

`request-changes` KHÔNG đóng gate. Xử lý:
1. Ghi `revisions/REV-NN.md` trong thư mục intent: ai yêu cầu, yêu cầu gì, gate nào, doc nào.
2. Agent chủ artifact sửa **đúng phần được nêu**, bump `version:` trong frontmatter của gate_doc, ghi mục
   "Changelog" cuối file (`vN: sửa gì · theo REV-NN`).
3. Gate mở lại với bản mới; tower hiển thị diff-note (mục changelog) trên đầu preview.
4. 2 vòng request-changes cùng một gate_doc mà chưa hội tụ → escalation (protocol §4.6), không sửa vòng 3 im lặng.

## 3. Layout state trong project

```
.ai-dlc/
├── workspace-map.md            # code/docs/wiki nằm đâu — NGUỒN DUY NHẤT để resolve path output
├── context-memory/
│   ├── governance/dor.md dod.md decisions-log.md changelog.md risks.md tech-debt-register.md
│   ├── comms/MSG-NNNN.md       # message bus (trao đổi ngắn)
│   ├── handoffs/HOF-NNNN.md    # GÓI GIAO VIỆC — mọi lần spawn agent phải có một file (§9)
│   ├── session/
│   │   ├── board.md            # bảng vị trí: ai đang giữ việc gì (SINH RA từ handoffs — không sửa tay)
│   │   ├── INDEX.md            # bản đồ tra cứu: cần biết X → đọc file nào, mục nào
│   │   └── log/SES-NNN.md      # nhật ký phiên: phiên này làm gì, dừng ở đâu
│   ├── reviews/RV-NNN.md
│   ├── escalations/ESC-NNN.md   # phát hiện NGOÀI phạm vi unit — sống tới khi có người nhận (§4.13)
│   ├── lessons-learned/LL-NNN.md
│   └── intents/INT-NNN/
│       ├── intent.md           # phần 1 dạng chuẩn (nguồn máy đọc)
│       ├── intent-plan.md      # GATE A DOC — hợp nhất phần 1+2+3, tự đủ để duyệt
│       ├── unit-plan.md        # GATE D DOC — bản Units cuối, hợp nhất mọi UOW
│       ├── open-questions-business.md   # GATE C DOC — hỏi người nghiệp vụ, cấm thuật ngữ code (§4.10)
│       ├── open-questions-tech.md       # hỏi người kỹ thuật — câu CHẶN phải chốt trước Gate D
│       ├── status.md  decision-briefs/  revisions/REV-NN.md
│       ├── as-is/              # static-model.md dynamic-model.md decisions-inventory.md source-ledger.md
│       ├── pinned/             # snapshot checklists + governance lúc intent bắt đầu
│       └── units/
│           ├── UOW-NN/
│           │   ├── spec.md user-stories.md nfr.md risks.md (pr-faq.md)
│           │   └── bolts/BOLT-NN/  # domain-design.md logical-design.md adr/ contract.md tasks.md evidence/
│           ├── DESCOPED.md     # unit bị đưa ra ngoài phạm vi (chỉ file này mới quyết định descoped)
│           └── _trash/UOW-NN/  # unit lỗi thời + TOMBSTONE.md — bằng chứng cho retro, KHÔNG tính vào số (§4.14)
├── inbox/                      # durable queue từ tower (processed/ sau khi xử lý)
├── overrides/                  # OVERRIDES.md + checklists/ agents/ governance/
└── tower/                      # HTML generated
```

## 4. Binding rules (bắt buộc, thứ tự kiểm tra)

1. **Override thắng**: trước khi dùng checklist/governance X, kiểm tra `.ai-dlc/overrides/**/X` — có thì dùng bản đó
   (kiểu `patch` = áp lên bản gốc; `replace` = thay hẳn). Override phải có frontmatter `reason`, `source`.
2. **Pinned thắng bản sống**: agent làm việc trong INT-NNN đọc checklist/governance từ `pinned/` của intent đó.
3. **Workspace map — không đoán path**: mọi output (code, docs) resolve đích qua `workspace-map.md`.
   Map thiếu mục cần dùng → HỎI, không đoán.
4. **No silent change**: đổi bất kỳ artifact đã qua duyệt → DEC mới + dòng changelog; chạm scope → mở lại gate.
5. **Đóng handoff bắt buộc**: kết thúc lượt làm việc, agent **đóng HOF của mình** (điền *Đã làm* + *Còn treo*,
   đặt `status`) — xem §9. Việc phát sinh ngoài phạm vi HOF thì thêm MSG type `note`, không tự làm.
6. **Escalation**: 2× request-changes cùng artifact, hoặc phát hiện logic sai từ gốc / tài liệu thiếu gây hiểu
   nhầm → KHÔNG tự vá; tạo MSG escalation → tech-lead-reviewer → gate động nếu chạm scope/business.
7. **Claim**: task chỉ được claim khi mọi `depends_on` đã `done` VÀ được approver ký. Một task một người claim.

### 4.8 No-unread-source (v2 — luật chống đọc thiếu)

- Mọi nguồn có trong Source Reading Plan phải có **trạng thái cuối** trong `as-is/source-ledger.md`:
  `read` · `missing` · `deferred` (kèm lý do + ai chịu) · `superseded` (kèm nguồn thay thế).
  Còn nguồn `planned` chưa xử lý → **CẤM mở Gate B**.
- Mỗi dòng `read` phải kèm **evidence**: đường dẫn + vùng đã đọc (dòng/section) + phát hiện rút ra 1 câu.
  Không có evidence = chưa đọc.
- Agent hạ nguồn (context-archaeologist, unit-planner, be-dev, fe-dev) **chỉ được kết luận từ nguồn có trong
  ledger**. Phát hiện nguồn mới ngoài plan → thêm dòng `[ADDED]` vào ledger + ghi MSG note, KHÔNG dùng thầm.
- Hai nguồn mâu thuẫn → `[CONFLICT]` trong ledger + câu hỏi Gate C. Agent không tự chọn bên nào.
- Kết luận không truy được về một dòng ledger phải gắn `[INFERRED]` và không được dùng làm căn cứ AC.

### 4.9 Unit = một phiên · tự ra được sản phẩm (v5 — thay trần 5h)

**Trần 5h đã bỏ.** Nó là phát minh của gói ở v2, không có trong white paper — SSOT chỉ nói chu kỳ tính bằng
"**giờ hoặc ngày**" và bounded context "độc lập, **đúng kích thước**". Một con số cứng đo sai thứ cần đo:
nó bắt tách theo *đồng hồ* thay vì theo *đường ra sản phẩm*, nên sinh ra unit vụn không tự release được
(ca thật: `DEC-0052` tách một unit thành 3.5h + 2.75h chỉ để lọt trần — hai mảnh phải ra chung mới có nghĩa).

Thay bằng **hai điều kiện**, cả hai đều phải khai thành trường và đều kiểm được:

**(1) Tự ra được sản phẩm.** Unit là một lát cắt **dọc**: xong Unit là có thứ đưa ra được, không phải chờ
unit khác mới có nghĩa.

```yaml
releasable: yes            # xong là ra được (có thể sau cờ tính năng)
release_note: "sau cờ qg_v2"   # cách đưa ra nếu cần cờ/route riêng
depends_on: []             # unit phải xong TRƯỚC nó
```

`releasable: no` được phép, nhưng khi đó **bắt buộc** `released_with: UOW-NN` — nói rõ nó ra chung với ai.
Không khai được `released_with` nghĩa là nó không có đường ra sản phẩm nào cả: đó là **pseudo-unit kỹ thuật**
("Update DB", "Add API"), phải gộp lại hoặc cắt theo trục khác (theo actor · theo luồng nghiệp vụ · theo
trạng thái dữ liệu · happy-path trước, edge-case sau).

**(2) Vừa một phiên.** Một agent làm trọn Unit trong một phiên: một HOF, không phải chia nhiều lượt, không
phải compact giữa chừng.

```yaml
session_fit: "3 màn + 2 endpoint, đọc 4 nguồn (S12,S13,S20,S21), vùng code quen"
```

Câu này phải có **con số thật** (mấy màn/endpoint/bảng · mấy nguồn phải đọc · vùng code quen hay lạ) — đó là
thứ quyết định một phiên có ôm nổi không, chứ không phải số giờ. Viết "vừa một phiên" mà không có con số =
chưa khai.

**`estimate_hours` vẫn giữ** — cần cho đường găng và cho retro — **nhưng không còn ngưỡng chặn**, và vẫn
phải có breakdown theo bolt kèm căn cứ. Dự án nào muốn trần riêng thì tự đặt, gói không áp:

```yaml
# .ai-dlc/governance/sizing.md
unit_max_hours: null       # null = không trần (mặc định). Đặt số thì tower/doctor cảnh báo khi vượt.
```

**Ai chặn gì ở Gate D**: chặn khi Unit thiếu `releasable` (hoặc `no` mà không có `released_with`), thiếu
`session_fit` có con số, thiếu breakdown, hoặc thiếu một trong ba khối bắt buộc bên dưới. **Không chặn theo
giờ nữa.** Vượt `unit_max_hours` (nếu dự án có đặt) chỉ là WARN.

**Kiểm sau, bằng dấu vết — vì lời khai lúc lập kế hoạch luôn lạc quan** (§9.4 đã dạy một lần):
- `units.oneSession` — Unit đóng bằng **đúng một chuỗi HOF**. Cần ≥2 HOF, hoặc có HOF `returned`, nghĩa là
  thực tế **không** vừa một phiên. Đây không phải để phạt: đó là dữ liệu để intent sau cắt khác.
- `units.releasable` — bao nhiêu Unit trong phạm vi khai hợp lệ.

Một Unit vẫn BẮT BUỘC có đủ ba khối: **User Story** (`user-stories.md`), **NFR** (`nfr.md`), **Rủi ro**
(`risks.md`). Thiếu bất kỳ khối nào → không đạt DoR, không vào Bolt.

> Rủi ro ngược của việc bỏ trần là unit phình to nuốt cả intent. Chốt chặn không phải đồng hồ mà là hai câu
> hỏi trên: *ra được sản phẩm một mình không* và *một phiên có ôm nổi không*. Thêm một cảnh báo mềm: AC quá
> 8 mục, hoặc Unit chạm hơn hai bounded context → nhiều khả năng đó là hai Unit.

### 4.10 Open questions — tách theo NGƯỜI TRẢ LỜI, hỏi bằng ngôn ngữ của họ (v3)

Stage 4 sinh **hai** file, không phải một:

| File | Cho ai | Gate | Được dùng thuật ngữ kỹ thuật? |
|---|---|---|---|
| `open-questions-business.md` | người nghiệp vụ (owner/PO/BA/PMO/vận hành) | **gate_doc của C** | **KHÔNG** |
| `open-questions-tech.md` | tech lead / architect / QA lead / devops | chặn **D** (§4.10.4) | CÓ, bắt buộc kèm bằng chứng |

1. **Trục tách là người trả lời, không phải chủ đề.** Câu chỉ người nghiệp vụ quyết được → file business.
   Câu người kỹ thuật quyết được một mình → file tech. Sai trục = hỏi nhầm người = câu hỏi nằm chết.
2. **Luật hai phút** (file business): mỗi câu phải trả lời được trong ~2 phút, **không cần mở file khác,
   không cần biết code**. CẤM trong file business: đường dẫn file, tên bảng/cột, tên lớp/hàm/kiểu, tên route,
   viết tắt nội bộ chưa giải thích. Sự thật kỹ thuật cần thiết phải **dịch ra lời**
   ("danh sách vai trò hiện dùng chung cho cả công ty, chưa tách theo từng dự án").
3. **Cặp mã khi một quyết định chạm cả hai phía**: viết `OQT-NN` (đủ chi tiết kỹ thuật + bằng chứng) và
   `OQB-NN` (bản hỏi bằng lời, kèm phương án và hệ quả), nối hai chiều bằng dòng *soi chiếu*. Không bao giờ
   ném nguyên câu kỹ thuật cho người nghiệp vụ và bảo họ tự hiểu.
4. **Luật chặn**: câu `CHẶN UOW-NN` còn `open` trong file tech → Unit đó không được vào **Gate D**;
   trong file business → không được đóng **Gate C**. Muốn đi tiếp: chốt, hoặc hạ `[ASSUMED]` + ghi rủi ro vào
   `units/UOW-NN/risks.md` (im lặng không được phép làm tắc, xem điểm 6).
5. **Mỗi câu là một quyết định**, có: mã · nhóm · **người cụ thể** (vai + tên, không phải "BA/TL/Test Lead"
   chung chung) · hạn · ảnh hưởng · bối cảnh · **các phương án chọn sẵn kèm cái giá** · đề xuất của AI.
   Câu mở kiểu "X là gì?" bị cấm — phải là chọn A/B/C hoặc Có/Không.
6. **Bắt buộc có đường thoát**: mỗi câu ghi *Nếu không trả lời trước hạn* → phương án mặc định + `[ASSUMED]`
   + chi phí đổi muộn. Không câu nào được để dự án đứng im chờ vô thời hạn.
7. Nhóm câu hỏi có sẵn (xoá nhóm rỗng): business **B1** phạm vi & ưu tiên · **B2** quy tắc nghiệp vụ ·
   **B3** vai trò & quyền · **B4** dữ liệu & nguồn sự thật · **B5** quy trình & vận hành · **B6** tuân thủ &
   rủi ro kinh doanh · **B7** trình bày & điều hướng (menu, vị trí, nhãn, cách người dùng tìm thấy màn).
   Tech **T1** kiến trúc & ranh giới · **T2** mô hình dữ liệu & migration · **T3** tích hợp
   & hợp đồng API · **T4** phi chức năng · **T5** kiểm thử & môi trường · **T6** nợ kỹ thuật & quy trình.
8. Vẫn giữ luật cũ: chỉ hỏi cái **chưa có quyết định ở đâu cả** (đối chiếu `decisions-inventory.md` trước),
   và mọi `[CONFLICT]` trong ledger phải trở thành một câu hỏi ở đúng một trong hai file.
9. **Không hỏi trước khi đọc** (LL-001, mẫu lỗi tái phát 6 lần). Mỗi câu hỏi BẮT BUỘC mang một dòng
   *"đã soát: `<nguồn>` · `<nguồn>` — không thấy đáp án"*. Thiếu dòng đó ⇒ **chưa đủ điều kiện gửi đi**.
   Ba ràng buộc cụ thể, mỗi cái sinh ra từ một lần đã sai thật:
   - Câu nhắc tới một màn có mã (`SCR-*`, `SCREEN-*`) ⇒ phải trích **chính file spec của màn đó**.
   - Câu dạng *"màn X hiện Y không / dùng con số nào"* là câu về **hiện trạng**, không phải về quyết định ⇒
     grep code trước. Code đã trả lời rồi thì viết *"hiện đang là Z — xác nhận giữ nguyên?"*, không hỏi mở.
   - Soát **registry feature** (`specification/features/…`) trước screen spec: screen spec thường chỉ mirror
     rút gọn, luật đầy đủ nằm ở registry.
10. **Sổ cái cập nhật ⇒ soát ngược câu đang mở.** Mỗi lần thêm dòng `[ADDED]` vào `source-ledger.md`, đối
    chiếu lại toàn bộ câu hỏi còn `open` — nguồn mới thường trả lời câu cũ. Câu nào có đáp án thì đóng ngay
    kèm trích dẫn, đừng để nó nằm chờ người.
11. **Không bịa nhãn.** Mọi giá trị/trạng thái nêu trong câu hỏi phải chép từ nguồn hoặc từ code, không được
    tự nghĩ ra cho "dễ hiểu" — người trả lời sẽ phải đi sửa lại câu hỏi trước khi trả lời được, tức việc bị
    đẩy ngược từ AI sang người.

### 4.11 Số trên Control Tower phải truy được (v3.1)

Dashboard nói dối âm thầm còn tệ hơn dashboard trống. Vì vậy:

1. **Mỗi con số hiển thị phải mở ra được**: đếm cái gì · đọc từ file/mục nào · và **đúng những dòng đã đếm**.
   Generator sinh `metricsByIntent`, UI bấm vào số là thấy bảng dòng thật. Số không giải thích được thì không
   được hiển thị.
2. **Đọc tài liệu bằng TÊN, không bằng vị trí**: nhận bảng bằng tên cột (`#` · `Nguồn` · `Trạng thái`), nhận
   mục bằng tên tiêu đề ("Mâu thuẫn…"). Bám số mục (`§3` = mâu thuẫn) là nguồn gốc của số rác khi dự án viết
   sổ cái theo bố cục khác.
3. **Không hiểu thì nói không hiểu**: ô trạng thái viết lạ → `unknown` + cảnh báo trên chính con số đó, KHÔNG
   âm thầm tính là 0 hay là `read`.
4. **Cùng một tập, cùng một phép đếm**: đếm số unit và cộng giờ phải trên cùng tập unit. Unit ngoài phạm vi
   hiện riêng, không trộn vào tổng.
5. **Số 0 phải phân biệt được hai nghĩa**: "đếm được và bằng 0" ≠ "không có gì để đếm". Trường hợp thứ hai
   phải nói rõ (ví dụ: *"chưa unit nào có `tasks.md`"*, không phải *"0 task done"* trơ trọi).
6. **Chỉ `units/DESCOPED.md` (hoặc `status: descoped`) mới đưa unit ra ngoài phạm vi** — không suy diễn từ
   việc unit vắng mặt trong `unit-plan.md`, vì unit sinh sau Gate D là chuyện bình thường.
7. **Chuẩn hoá từ vựng, đừng so chuỗi**: `status:` của Unit — `done` · `approved` · `accepted` ·
   `completed` · `closed` · `xong` · `đã nghiệm thu` đều là **xong**; `in-bolt` · `wip` · `đang làm` là
   đang chạy. Tài liệu con người viết không bao giờ dùng đúng một chữ; đếm bằng so chuỗi cứng là tự tạo
   số sai.
8. **Pha và Unit là hai nguồn khác nhau, phải đối chiếu**: pha hiển thị đến từ `stage:` trong `status.md`
   (một con số do orchestrator ghi), trạng thái Unit đến từ N file `spec.md`. Không có gì tự ràng buộc hai
   thứ đó. Khi `stage` ≥6 mà còn Unit chưa đóng, tower phải **nói ra** ("stage 7 nhưng 5/18 unit chưa đóng
   hồ sơ") thay vì để người xem tự phát hiện — nguyên nhân có thể là quên cập nhật, cũng có thể là pha bị
   đẩy sớm, và máy không phân biệt được.

### 4.12 Review phải có địa chỉ, không phải lời hứa (v4 — LL-002 P-2)

DoD từ v1 đã ghi *"reviewer BE/FE approve"*. Một dự án thật vẫn đóng **17 unit code liên tiếp** với 13
review-request gửi đi và **0 verdict nhận về** — không ai nói dối, chỉ là câu chữ đó không có gì để đối chiếu.
Luật không thiếu; luật **không kiểm được**. Vì vậy:

- `spec.md` của Unit phải mang **một trong ba**, nếu không thì **không được `done`/`approved`**:
  - `reviewed_by: <agent>` + `rv: RV-NNN` — file `reviews/RV-NNN.md` phải **tồn tại thật** và `re:` khớp Unit
    (bắt buộc với tier `peer`/`specialist` — §4.17); hoặc
  - `self_verify: <path>` — **chỉ hợp lệ khi Unit khai `review: none` đã được duyệt ở Gate D** (§4.17):
    file `evidence/self-verify.md` phải tồn tại thật, đủ mục checklist, mỗi mục có **con trỏ bằng chứng**; hoặc
  - `review_waived_by: DEC-NNNN` — một quyết định nêu rõ **vì sao cố ý bỏ review lượt này**
    (đường cũ trước v6, vẫn hợp lệ cho ca ngoại lệ ngoài bảng tầng).
- **Gửi review-request rồi đóng HOF trong cùng lượt là vi phạm.** HOF chỉ được `done` khi verdict đã về, hoặc
  khi đã ghi `review_waived_by`. "Đã gửi, chờ verdict" là trạng thái *đang chờ*, không phải *xong*.
- `approved` do chính agent làm unit tự đặt **không phải bằng chứng nghiệm thu độc lập**. Hồ sơ Gate F chỉ
  được dùng nó khi nói rõ đó là **tự khai**.
- Ai cố ý chạy không review để đổi lấy tốc độ thì ghi thành một DEC công khai — đừng để nó là mặc định im lặng.

### 4.13 Phát hiện ngoài phạm vi phải thành VIỆC, không thành ghi chú (v4 — LL-002 P-3)

Luật "không sửa ngoài phạm vi Unit" giữ cho các Unit song song không giẫm chân nhau — **giữ nguyên**. Nhưng nó
biến agent thành nhân chứng không có quyền hành động: cùng một lỗi id-space bị 4 HOF ghi nhận rồi vẫn tới tay
người dùng dưới dạng link 404, vì HOF đóng lại là phát hiện chìm theo.

- Agent gặp lỗi/nguy cơ **ngoài Unit của mình** ⇒ mở một mục trong `context-memory/escalations/ESC-NNN.md`
  (frontmatter: `found_by` · `where` · `severity` · `owner: —` · `status: open`), **rồi** mới ghi vào HOF.
- Chỉ ghi trong HOF là **chưa đủ** — HOF có vòng đời của một lượt việc, escalation sống tới khi có người nhận.
- Control Tower hiện hàng đợi này; `status: open` không có `owner` quá 2 phiên → nhắc ở `/dlc-doctor`.
- Escalation chạm scope/business ⇒ vẫn theo §4 điểm 6 (gate động), không tự vá.

### 4.14 Unit lỗi thời vào `units/_trash/`, không xoá (v4 — LL-002 P-6)

Unit bị **viết đè khi replan**, hoặc **trượt review mà không được viết lại**, thì chuyển vào
`units/_trash/UOW-NN/`, hạ `status: obsolete`, kèm `TOMBSTONE.md` (vì sao · DEC/RV nào quyết · thay bằng gì).

- Unit **được viết lại** sau khi trượt thì **không** vào đây — nó đã được sửa, không phải rác.
- **Không xoá**: retro sống bằng chính đống dấu vết này (phát hiện "13 lần xin review, 0 lần được review" tìm
  ra bằng cách đối chiếu `comms/` với `reviews/` — xoá đi thì phát hiện đó không tồn tại).
- Mọi thống kê (tower, doctor, acceptance) **bỏ qua `units/_*`**: unit lỗi thời đứng lẫn trong kế hoạch đang
  chạy và đeo trạng thái nói dối là cách nhanh nhất để mọi con số của intent sai.

### 4.15 Phép đo phải tự chứng minh trước khi tin (v4 — LL-002 P-5)

Một dự án thật có **4 lần đo hỏng cho kết quả NGƯỢC** (không phải kết quả trống): redirect RSC làm `curl` báo
"guard không chạy" trong khi guard chạy đúng; `grep` trúng payload i18n; vòng lặp `zsh` mất `PATH` nên mọi
request rỗng bị đọc thành "vào được". Ba trong bốn lần suýt được báo cáo ra ngoài.

- Trước khi kết luận từ một phép đo, chạy **một ca đối chứng đã biết chắc kết quả ngược lại**. Ca đối chứng
  không ra như mong đợi ⇒ **công cụ đo hỏng**, không phải hệ thống hỏng.
- Áp cả cho test bảo vệ: test chưa từng thấy đỏ thì chưa chứng minh được gì ⇒ **mutation-test** (bỏ nhánh
  được bảo vệ, test phải đỏ). Một lần làm thật cho kết quả: bỏ allow-list chỉ làm 1/8 test đỏ.
- **Smoke HTTP 200 không chứng minh gì về hành vi**: nút render ra vẫn có thể là nút chết. Phải bấm thử các
  affordance chính, hoặc có test tương tác cho từng nút.

### 4.16 Thu hẹp một union kiểu ⇒ grep mọi so sánh bằng (v4 — LL-002 P-4)

Xoá một giá trị khỏi union (`persona`, `status`, `role`…) làm mọi điều kiện `=== '<giá trị đã xoá>'` **vĩnh
viễn sai** mà **cả compiler lẫn test đều im**: kiểu vẫn hợp lệ, còn test đặt giá trị đó thì rơi về mặc định.
Bắt buộc grep toàn repo mọi so sánh bằng với giá trị bị xoá, và ghi kết quả vào evidence của Unit.

### 4.17 Review theo tầng rủi ro — reviewer là ngoại lệ có địa chỉ, không phải mặc định (v6)

Review Board agent bắt buộc mọi nơi là **phát minh của gói**, không có trong white paper — SSOT chỉ nói
**con người** rà soát artefact do AI tạo (mob rà soát ở Inception, "Developer rà soát mã và kịch bản kiểm
thử" ở Construction). Và nó đã trượt trên thực địa theo đúng cách luật không kiểm được vẫn trượt: LL-002
ghi 13 review-request gửi đi, **0 verdict** nhận về, 17 unit vẫn đóng. §4.12 vá phần *kiểm được*; mục này
vá phần *chi phí*: mỗi lượt reviewer là một phiên lạnh phải nạp lại bối cảnh, và bắt buộc nó ở mọi nơi
chỉ sinh ra hàng đợi nghẽn hoặc một đống DEC waiver hình thức.

Thay bằng: **mỗi Unit khai một tầng review trong `spec.md` (`review:`), bảng tầng nằm trong `unit-plan.md`,
và NGƯỜI duyệt cả bảng một lần tại Gate D.** `review: none` được duyệt ở Gate D **chính là** waiver có địa
chỉ — không cần DEC riêng cho từng unit nữa.

| Tầng | Trigger (kiểm được — dính một cái là phải lên tầng đó) | Ai soát | Bằng chứng đóng Unit (§4.12) |
|---|---|---|---|
| `none` | mặc định — không dính trigger nào bên dưới | chính dev, theo checklist | `self_verify:` trỏ `evidence/self-verify.md` |
| `peer` | bolt có cả FE lẫn BE (có contract) · `session_fit` khai vùng code **lạ** · Unit đầu tiên của intent chạm một bounded context | **dev còn lại trong cùng bolt** | `rv: RV-NNN`, reviewer là dev kia |
| `specialist` | chạm auth/authz/session/token/crypto/PII/secret ⇒ **security** · migration phá hủy / đổi public API / ADR trái pattern hiện có ⇒ **tech-lead** · NFR có ngưỡng đo trong `nfr.md` ⇒ **qa** | đúng **MỘT** vai theo trigger (nhiều trigger khác loại ⇒ nhiều vai, vẫn không phải cả board) | `rv: RV-NNN` của specialist |

Luật:

1. **Khai trước, duyệt một lần.** `review:` là trường bắt buộc của `spec.md` từ v6; thiếu ⇒ chặn Gate D
   (như thiếu `releasable`). Người duyệt Gate D thấy cả cột Review trong unit-plan — muốn nâng tầng unit
   nào thì `request-changes` đúng dòng đó, một dòng là đủ.
2. **Trigger là để đối chiếu, không phải để cảm nhận.** `/dlc-doctor` và tower grep dấu vết thật
   (diff/bolt chạm pattern security, có file migration, bolt có cả FE+BE…) và so với tầng đã khai — chạm
   trigger mà khai `none` là **FIX**, không phải chuyện khẩu vị.
3. **Đổi tầng giữa chừng có chiều.** Đang code mà phát hiện trigger (đụng auth ngoài dự kiến…) ⇒ **nâng
   tầng ngay**, ghi MSG note, không cần mở lại Gate D. Chiều ngược lại — hạ tầng đã duyệt — thì phải DEC.
4. **Checklist đi trước code (shift-left).** Checklist BE/FE không còn là công cụ riêng của reviewer: nó
   nằm trong `read_first` của HOF dev — dev đọc **trước khi code** (pre-flight) và điền **sau khi code**.
   Reviewer (khi có) *verify* chứ không *discover*: HOF review chỉ cần diff + checklist, vì peer đã đọc
   design/contract cho task của chính mình — đó là lý do peer rẻ hơn một reviewer lạnh.
5. **Self-verify không phải dấu ✓.** `evidence/self-verify.md` (template của gói): từng mục checklist kèm
   **con trỏ bằng chứng** (file test + output, kết quả grep, dòng ledger). Mục "n/a" phải có lý do. Và vì
   tier `none` không có reviewer, hai lưới thay thế đều bắt buộc: **§4.15** (ca đối chứng + mutation test —
   máy kiểm hộ những gì máy kiểm được) và **§9.6** (người giao nghiệm kết quả: mở 1–2 con trỏ trong
   self-verify kiểm thật trước khi cho unit đóng — mắt thứ hai không tốn phiên mới).
6. **Điểm dừng của NGƯỜI không đổi.** Gate E(a)/E(b) vẫn dừng cho MỌI unit, tier nào cũng vậy (§1.0c).
   Bỏ reviewer agent không phải là bỏ giám sát — giám sát nằm ở gates A–G, đúng như white paper.
7. **Peer review giữ nguyên khung RV**: format `RV-NNN` không đổi, 2× `request-changes` cùng một điểm vẫn
   thành escalation của người (§4.6). Người review ≠ người viết phần code đó.
8. **Giới hạn nói thật**: dev và peer chạy cùng model, cùng điểm mù. Lưới đỡ là trigger specialist +
   mutation test + KPI lỗi lọt (điểm 9) — không phải niềm tin.
9. **KPI đối chiếu** (luật không kiểm được là luật sẽ trượt): `units.reviewed` mở rộng đếm cả ba đường
   bằng chứng (RV thật · self-verify thật · DEC miễn), kèm cột tầng; retro đối chiếu **lỗi lọt theo tầng**
   (escalation/LL phát sinh sau khi unit đóng, quy về tầng của unit đó) — tier `none` sinh lỗi lọt là dữ
   liệu để nâng trigger ở intent kế, có số làm căn cứ thay vì cãi nhau bằng cảm giác.

> Nguồn gốc mục này: quyết định chủ gói (6.0.0), cùng vị thế với việc bỏ trần 5h ở 5.0.0 — ba căn cứ kiểm
> được ghi trong CHANGELOG; **nợ một LL**, retro có dữ liệu tầng đầu tiên phải trả.

## 5. Định dạng bản ghi

`comms/MSG-NNNN.md`:
```
---
from: <agent>  to: <agent|HUMAN>  re: INT-NNN[/UOW-NN[/BOLT-NN[/TSK-NN]]]
type: review-request|finding|question|answer|clarification|handoff|note|escalation
status: open|answered|closed
---
<nội dung>
```

`handoffs/HOF-NNNN.md` (v2.2 — xem §9):
```
---
id: HOF-0007        from: <agent|HUMAN>   to: <agent>
re: INT-NNN[/UOW-NN[/BOLT-NN[/TSK-NN]]]
kind: assign|review|return|escalate|takeover
status: open|accepted|done|returned|superseded
created: <ISO>      accepted: <ISO|->     closed: <ISO|->
heartbeat: <ISO|->  progress: <1 câu đang làm gì|->      # §9.4 — cập nhật ở mỗi mốc
result_check: -     # §9.6 — NGƯỜI GIAO điền khi nghiệm: "pass · <ISO> · <đã kiểm gì>" | "returned · ..."
read_first: ["<path#mục> — vì sao", ...]     # tối đa 8; trỏ, không chép
blocked_by: [HOF-NNNN|TSK-NN|-]
---
## Nhiệm vụ (1 câu)
## Ràng buộc / cấm
## Xong lượt này nghĩa là gì (DoD của lượt)
## Trả về gì (file nào, format nào)
## Đã làm            # agent nhận điền khi đóng — trỏ path, không chép nội dung
## Còn treo / bàn giao tiếp
```

`session/log/SES-NNN.md`:
```
---
id: SES-003   started: <ISO>   ended: <ISO|->   by: HUMAN+<agents>
---
- Vào phiên thấy: <1 dòng>          - Đã làm: <gạch đầu dòng, trỏ HOF/DEC/RV>
- Dừng ở: <trạng thái>              - Việc kế tiếp: <1–3 gạch đầu dòng>
```

`reviews/RV-NNN.md`:
```
---
reviewer: <agent>  target: <đường dẫn artifact>
verdict: approve|approve-with-notes|request-changes
checklist: <tên> v<N>
---
[MUST] ... / [SHOULD] ...
```

`governance/decisions-log.md` — append entry:
```
## DEC-NNNN · <ngày> · <Gate X | thay đổi> · INT-NNN
- Quyết định: ...   - Người quyết: HUMAN|<agent đề xuất>
- Căn cứ: RV-xxx · MSG-xxxx   - Ảnh hưởng: ...
```

`revisions/REV-NN.md` (v2):
```
---
gate: A|B|C|D|E|F|G   doc: intent-plan.md   doc_version: 2
from: HUMAN           at: <ISO>             status: open|addressed
---
<yêu cầu sửa, nguyên văn từ tower>
## Đã xử lý
- <sửa gì · ở đâu · version mới>
```

`tasks.md` — mỗi task:
```
## TSK-NN · <tên>
perspective: BE|FE|shared   status: todo|claimed|in-progress|blocked|review|done
claimed_by: <agent|->   approver: <reviewer — assign lúc tạo board>
depends_on: [...]   comms: [MSG-...]   notes: ...
```

`status.md` (per intent):
```
---
intent: INT-NNN   stage: 1..8   phase: inception|construction|operations
gates_passed: [A, B, ...]   gate_open: <A..G|escalation|null>
gate_doc: <đường dẫn tương đối tới markdown gate đang chờ|null>
plan_version: 1
plugin_version: 2.0.0
---
```

Inbox quyết định từ tower (`inbox/gate-INT-NNN-X-<ts>.json`):
```json
{"gate":"A","intent":"INT-001","verdict":"approve|request-changes|reject",
 "comment":"...","doc":"intent-plan.md","doc_version":1,
 "previewed":true,"decided_at":"<ISO>"}
```

## 6. Phân tầng model (ai chạy bằng model nào)

| Tier | Model | Agents | Lý do |
|---|---|---|---|
| Sâu | opus | orchestrator, intent-analyst, **source-planner**, context-archaeologist, unit-planner, ba-reviewer†, tech-lead-reviewer†, security-reviewer† | phân rã, kiến trúc, rủi ro — sai ở đây lan xuống toàn hạ nguồn |
| Thực thi | sonnet | context-validator, bolt-coordinator, be-dev, fe-dev, pm-po-reviewer†, qa-reviewer†, retro-keeper | code, review theo checklist, điều phối |
| Cơ học | haiku | acceptance-recorder | gom evidence, trace link, persist — theo khuôn |

† = **on-demand từ v6** (§4.17): reviewer chỉ được spawn khi trigger specialist bắn, khi người yêu cầu tại
gate, hoặc khi escalation cần (tech-lead). Không còn spawn mặc định theo flow. `backend-reviewer` và
`frontend-reviewer` đã **gỡ khỏi gói** ở 6.0.0 — checklist BE/FE chuyển thành pre-flight + self-verify của
dev, review code (khi tầng cần) do dev còn lại trong bolt (peer) hoặc specialist đảm nhận.
Reviewer chỉ được gọi cho phần thuộc góc nhìn của mình, và chỉ khi tầng review của Unit cần vai đó.

## 7. ID & đánh số

INT/UOW/BOLT: 2–3 chữ số, tăng dần trong phạm vi cha. MSG/RV/DEC/LL: đếm toàn cục trong project,
lấy số kế tiếp bằng cách liệt kê file/entry hiện có. REV: đếm trong phạm vi intent. Không tái sử dụng ID.

## 8. Dòng chảy hiển thị trên Control Tower

Tower trình bày state theo **ba khối pha, mỗi Unit là một mạch chạy xuyên suốt ba khối**:

```
INCEPTION            CONSTRUCTION              OPERATIONS
intent-plan (A) ──┐
source-ledger (B) ─┼─ per Unit ──► bolt(s) (E) ──► acceptance (F) ──► release ──► retro (G)
OQ business (C) ───┤   (OQ tech: chặn D, không có gate riêng)
unit-plan (D) ─────┘
```

Mỗi khối hiển thị: các artefact của khối, gate của khối (kèm trạng thái), và **trạng thái từng Unit trong
khối đó**. Người dùng bấm một Unit là thấy được toàn mạch của nó: US/NFR/risk → nguồn đã đọc → bolt → task
→ evidence → DEC. Generator có nhiệm vụ dựng dữ liệu này; agent không phải tự vẽ.

## 9. Handoff — agent giao việc cho nhau bằng FILE, không bằng prompt

Lý do tồn tại: prompt biến mất khi phiên kết thúc. Nếu bối cảnh giao việc chỉ nằm trong prompt thì
(a) agent bị spawn lại sau khi mất ngữ cảnh phải đoán lại, (b) không có gì để retro khi nhiều người/nhiều
phiên cùng làm. Vì vậy:

> **Mọi lần spawn một agent PHẢI có một file `handoffs/HOF-NNNN.md`.**
> Prompt spawn chỉ được chứa đúng một câu: *"Đọc `.ai-dlc/context-memory/handoffs/HOF-NNNN.md`, làm theo,
> cập nhật lại chính file đó khi xong."* Không nhồi bối cảnh vào prompt.

### 9.1 Vòng đời một HOF

| Trạng thái | Ai đổi | Nghĩa |
|---|---|---|
| `open` | người giao | đã viết xong gói việc, chưa ai nhận |
| `accepted` | agent nhận | đang làm — đây là "vị trí đang có người" trên board |
| ↑ kèm `heartbeat` + `progress` | agent nhận | dấu hiệu còn sống: cập nhật ở mỗi mốc, xem §9.4 |
| `done` | agent nhận | lời khai xong (*Đã làm* + *Còn treo* đã điền) — kết quả chỉ được DÙNG sau khi người giao nghiệm, §9.6 |
| `returned` | agent nhận | trả lại vì thiếu điều kiện (nêu rõ thiếu gì) — không phải thất bại, là tín hiệu |
| `superseded` | người giao | bị thay bởi HOF khác (trỏ tới HOF mới) |

Phiên chết giữa chừng → HOF vẫn nằm ở `accepted`. Phiên sau `/dlc-resume` nhìn thấy ngay "việc này đang
treo ở ai, từ lúc nào, đang chờ gì" và tiếp tục **từ chính file đó** — không mất thông tin, không hỏi lại.

### 9.2 Luật viết HOF

1. **Trỏ, đừng chép.** Mục `read_first` liệt kê `path#mục` + **một dòng vì sao phải đọc**. Cấm dán nội dung
   tài liệu vào HOF — tài liệu đã có chỗ của nó; chép lại là tạo bản sao sẽ lệch.
2. **`read_first` phải đủ và tối thiểu**: đủ để làm việc mà không phải đi lục; tối thiểu để không nuốt hết
   context. Quá 8 mục là dấu hiệu gói việc quá to → tách HOF.
3. Mỗi HOF có **DoD của riêng lượt đó** (xong lượt này nghĩa là gì) và **trả về gì** (file nào, format nào).
4. Agent nhận **không được mở rộng phạm vi** trong HOF. Thấy việc ngoài phạm vi → ghi vào *Còn treo* +
   MSG note, để người giao quyết định.
5. Đóng HOF là **bắt buộc** trước khi kết thúc lượt (thay cho MSG note ở §4.5 — HOF đã bao gồm phần đó).
6. HOF là **bằng chứng retro**: retro-keeper đọc chuỗi HOF để thấy việc đi qua tay ai, tắc ở đâu, phải làm
   lại mấy lần. Đừng viết HOF cho có.

### 9.3 Bảng vị trí (station board)

`session/board.md` là **bản kết xuất** từ thư mục `handoffs/` — sinh lại bởi `/dlc-resume`, `/dlc-status` và
tower generator. **Không sửa tay** (sửa tay là tạo nguồn sự thật thứ hai). Mỗi dòng: vị trí (agent) · đang giữ
HOF nào · thuộc INT/UOW/BOLT/TSK nào · từ lúc nào · đang chờ gì.

Phiên chính (nơi bạn ngồi) nhìn board để biết các vị trí khác đang ở đâu; các phiên/agent được spawn không
cần biết về nhau — chúng chỉ cần HOF của mình.

### 9.4 Nhận việc & báo còn sống (bắt buộc — nếu không, Control Tower mù)

Control Tower chỉ thấy những gì được ghi xuống đĩa. Một agent đang chạy mà không cập nhật HOF của mình thì
với người giám sát nó **không tồn tại** — board vẫn ghi "chờ nhận" trong khi thực tế đã chạy 30 phút.

Vì vậy agent nhận HOF PHẢI:

1. **Ngay khi bắt đầu** (trước khi đọc `read_first`): đặt `status: accepted`, `accepted: <ISO>` vào
   frontmatter HOF của mình. Đây là hành động đầu tiên, không phải việc làm sau.
2. **Ở mỗi mốc** (đọc xong bối cảnh · xong thiết kế · xong file/màn/endpoint · gửi review · sửa xong):
   cập nhật `heartbeat: <ISO>` và `progress: <1 câu đang làm gì>`. Rẻ: hai dòng frontmatter.
3. **Khi kết thúc**: điền *Đã làm* / *Còn treo*, đặt `status: done|returned`, `closed: <ISO>`.

Board và tower hiển thị **khoảng im lặng** = now − `heartbeat`. Im lặng quá 15 phút ở một HOF `accepted`
được đánh dấu — có thể agent chết, có thể đang chạy tác vụ dài; người giám sát cần biết để hỏi.

Nhiều agent chạy song song thì **mỗi agent một HOF riêng** — không dùng chung một file (ghi đè lẫn nhau,
và không phân biệt được vị trí nào đang ở đâu).

**Nhịp phải kiểm chéo được.** `heartbeat` là *lời khai*; mtime của chính file HOF là *dấu vết*. Tower so hai
con số đó và gắn cờ ba ca — không đoán ý, chỉ so số:

| Cờ | Điều kiện | Người giám sát đọc ra gì |
|---|---|---|
| `placeholder` | `heartbeat` đúng `T00:00:00` (bất kể múi giờ) | giá trị điền cho có, không phải giờ thật |
| `future` | `heartbeat` > giờ máy + 5 phút | đồng hồ sai hoặc số bịa |
| `drift` | mtime(HOF) − `heartbeat` > 30 phút | agent **có** sửa file mà không cập nhật nhịp |

Bị gắn cờ thì tower **không hiện "im lặng N phút"** nữa (con số đó vô nghĩa khi mốc gốc đã sai) mà hiện thẳng
lý do + "file vừa đổi N phút trước". Ca gốc (PCT · `HOF-0039` · 13/08): agent ghi file lúc 18:13 nhưng khai
`heartbeat: …T00:00:00Z` và `progress` trễ ba vòng — bảng hiện "im lặng 1099 phút" cho một agent **đang chạy**.
Một con số sai nguy hơn không có con số: nó khiến người giám sát đi hỏi nhầm chuyện.

> `heartbeat` chỉ có giá trị khi nó là **giờ thật tại lúc ghi dòng đó**. Không copy giờ cũ, không để nửa đêm,
> không làm tròn cho đẹp. KPI đối chiếu: `handoffHealth.trusted / handoffHealth.accepted` trên tower.

### 9.5 Teammate (Claude Code agent team) — khi nào dùng, và cái gì KHÔNG đổi

Một lượt việc có thể chạy bằng **sub-agent** (phiên con, chỉ báo cáo về nơi gọi) hoặc **teammate** (một phiên
Claude Code độc lập trong agent team: có hộp thư riêng, nhắn thẳng cho nhau, người ngồi ngoài mở ra xem và
chen vào giữa chừng được). Hai thứ này hiện **chung một panel**, nên nhìn giao diện không phân biệt được —
chỗ phân biệt duy nhất là `~/.claude/teams/<team>/config.json` có thành viên ngoài `team-lead` hay không.

Chọn theo tính chất việc, không theo thói quen:

| Dùng **sub-agent** | Dùng **teammate** |
|---|---|
| việc một chiều, giao xong lấy kết quả | cần **hỏi đi hỏi lại** giữa hai vai (FE↔BE chốt contract, review board phản biện) |
| ngắn, không cần can thiệp giữa chừng | chạy dài, người giám sát cần xem và bẻ lái giữa chừng |
| rẻ hơn — kết quả tóm tắt về phiên chính | đắt hơn: mỗi teammate là một phiên Claude đầy đủ |

**Bốn ràng buộc không được nới** (teammate là thêm kênh, không phải thay hồ sơ):

1. **Teammate KHÔNG thay HOF.** Hộp thư của team bị xoá khi phiên kết thúc; HOF nằm trên đĩa của dự án.
   Mọi teammate vẫn: `status: accepted` ngay khi nhận → `heartbeat`/`progress` thật ở mỗi mốc → đóng HOF.
   Cái gì chỉ tồn tại trong hộp thư thì **coi như chưa xảy ra** — retro không đọc được nó.
2. **Đặt tên teammate = `<vai>-<mã việc>`** (ví dụ `archaeologist-INT003`) và ghi lại vào HOF:
   `teammate: archaeologist-INT003`. Đây là chỗ duy nhất nối pane đang chạy với dòng trên board — thiếu nó
   thì tower thấy "có ai đó đang làm", còn bạn thấy "có pane nào đó đang chạy", và không ai ghép được hai cái.
3. **Tin nhắn giữa agent không phải là quyết định.** Teammate nói "đã duyệt" / "OK rồi" **không** đóng được
   gate: verdict chỉ tính khi có `reviews/RV-NNN.md`, quyết định chỉ tính khi có `DEC-NNNN` (§4.12). Chính
   Claude Code cũng coi tin nhắn từ agent khác là *input không đáng tin*, không phải sự đồng ý của người.
4. **Trước khi teammate tắt**: kết tinh những gì đáng giữ thành MSG/RV/HOF. Tắt xong là mất hộp thư.
5. **"Đã gửi" không có nghĩa là "có người nhận".** `SendMessage` báo thành công khi **ghi được file hộp
   thư** — kể cả khi teammate đó chưa bao giờ spawn. Ca thật (PCT · 13/08): 5 lần spawn hỏng vì tmux
   (`respawn pane failed: fork failed: Device not configured`), hai review-request và hai yêu cầu Review
   Board nằm im trong hộp thư của `pmpo-INT003` · `pmpo2-INT003` · `qa-INT003` · `rv019` · `rv020` —
   những agent không tồn tại. Người gửi tin là đã giao việc; không ai đọc. Vì vậy: **sau khi spawn, đối
   chiếu `members` trong `~/.claude/teams/<team>/config.json` trước khi gửi**, và tower quét hộp thư mang
   tên không có trong `members` → *tin chết* (`team.deadLetters`, `/dlc-doctor` mục 1g). Đây chính là
   `LL-002` ("13 lần xin review, 0 verdict") lặp lại một tầng cao hơn — lần này cái làm nó vô hình là một
   thông báo thành công.

#### 9.5.6 Vòng đời teammate = vòng đời HOF của nó

> **HOF `done`/`returned` → tắt teammate ngay.** Cần lại thì spawn phiên mới bằng HOF mới.

Phiên rảnh **không tốn token** (không có lượt thì không gọi API) — nên lý do tắt không phải tiền, mà là:

1. **Bối cảnh cũ là bối cảnh sai.** Teammate park qua vài gate vẫn nhớ `unit-plan` v3 trong khi đĩa đã v4,
   rồi hành động theo bản trong đầu nó. Trong một hệ mà sự thật nằm trên đĩa, một phiên sống lâu là **nguồn
   sự thật thứ hai** — đúng thứ §9.3 cấm với `board.md`.
2. **Gọi lại đắt hơn spawn mới.** Gọi lại thì cả bối cảnh nó đang mang bị gửi lại; spawn mới thì prompt chỉ
   là một dòng trỏ HOF (§9.2) và nó nạp đúng `read_first`.
3. Mỗi phiên giữ một pty + một pane. Cạn pty là ca đã xảy ra: 5 lần spawn hỏng
   (`fork failed: Device not configured`) và sinh ra 5 tin chết ở §9.5.5.

**`/compact` cho teammate gần như luôn sai**: compact tự nó tốn token để đọc lại rồi tóm tắt, và thứ giữ
được là bản tóm tắt do model viết — trong khi bản tóm tắt **tốt hơn** đã nằm trên đĩa (HOF · MSG · artifact).
Chỉ compact khi teammate **đang giữa chừng** một HOF dài và sắp chạm trần context. Xong HOF thì tắt thẳng.
*(Bẫy thao tác: ở chế độ in-process, lệnh built-in gõ khi đang xem teammate vẫn chạy ở lead — muốn compact
đúng phiên đó phải vào pane riêng của nó.)*

Cơ chế tắt (Claude Code đã có sẵn, không cần dựng thêm): lead **gọi tên** teammate và yêu cầu shutdown —
nó có quyền từ chối kèm lý do (đang dở việc); hoặc chọn nó trên panel rồi bấm `x`. Vì teammate được phép từ
chối, **đừng tắt bằng cách giết pane** — mất phần *Đã làm* / *Còn treo* chưa kịp ghi vào HOF.

Vòng đời theo vai: **reviewer ngắn nhất** — spawn theo từng review, tắt ngay sau khi `RV-NNN` được ghi,
không park qua gate. Dev/planner/archaeologist sống đúng bằng HOF đang giữ. Chỉ giữ sống khi lượt kế đến
trong vài phút, hoặc khi nó đang giữ trạng thái chưa ghi xuống đĩa — mà đó chính là dấu hiệu **phải ghi
xuống đĩa trước đã**.

Tower đối chiếu `members` (phiên đang sống) với `teammate:` trong HOF và gắn ba trạng thái: `working` (còn
việc) · `zombie` (HOF đã đóng mà phiên còn sống) · `unknown` (không HOF nào khai tên nó). `team.zombies`
là danh sách lead cần tắt; `/dlc-doctor` mục 1f nhắc lại.

Ghi chú vận hành (đúng với bản Claude Code hiện tại): địa chỉ của phiên chính là **`team-lead`**, không phải
`main`; teammate **không** thừa kế `/model` của lead (khai `model:` trong HOF nếu tier quan trọng); spawn
bằng đúng agent definition của gói (`ai-dlc:dlc-*`) để teammate thừa hưởng tools/model của vai đó.

> Trạng thái của mục này: **hướng dẫn, chưa phải luật chặn gate.** Nó sinh ra từ quan sát thực tế
> (PCT · INT-003 · 13/08) chứ chưa qua một LL được Gate G duyệt — nên `/dlc-doctor` chỉ **WARN**, không FIX.
> Qua Gate G ở retro kế thì nâng thành luật.

### 9.6 Nghiệm kết quả — người giao đánh giá TRƯỚC khi kết quả được dùng (v6)

Agent nhận đóng HOF `done` mới chỉ là **lời khai xong**. Từ v6, kết quả của một HOF chỉ được dùng tiếp —
đánh dấu task `done`, đóng Unit, mở gate, hay spawn lượt sau phụ thuộc nó — sau khi **người giao**
(mainlead: coordinator/orchestrator/phiên chính — đang sống, có sẵn bối cảnh, nghiệm rẻ hơn mọi reviewer
lạnh) đã nghiệm ba bước:

1. **Đối chiếu** mục *Đã làm* với *DoD của lượt* trong chính HOF — từng điều kiện, không đọc lướt.
2. **Mở ít nhất một bằng chứng thật** (chạy một test, mở một file output, xem diff) — nghiệm bằng dấu vết,
   không nghiệm bằng lời khai. Với Unit tier `none` (§4.17): mở **1–2 con trỏ trong `self-verify.md`** và
   kiểm chúng có thật — nghiệm việc của lead chính là mắt thứ hai của tier này.
3. **Ghi xuống đĩa**: `result_check: pass · <ISO> · <1 câu đã kiểm gì>` vào frontmatter HOF. Không đạt →
   `result_check: returned · <thiếu gì>` + đặt `status: returned` (agent nhận sửa tiếp từ chính file đó).

Ràng buộc:
- **HOF `done` mà `result_check` trống = kết quả chưa được nghiệm** — doctor FIX (áp cho HOF tạo từ v6;
  HOF cũ chỉ ghi chú), và Unit không được đóng dựa trên nó.
- **Không tự nghiệm việc của chính mình**: HOF có `from` = `to` (tự giao) thì `result_check` không có giá
  trị mắt thứ hai — phải nói rõ là tự khai ở hồ sơ Gate F.
- Nghiệm là đánh giá **kết quả của lượt**, không phải review lại code — có trigger §4.17 thì tầng review
  vẫn chạy như thường; §9.6 không thay §4.17, nó bịt đúng cái khe "dev tự đóng, không ai nhìn lại".
- KPI đối chiếu: `handoffHealth.checked / handoffHealth.closed` trên tower — luật có trường để điền và
  con số để soi, như mọi luật khác của gói.

## 10. Ngân sách context (đọc ít, tra đúng chỗ)

Mục tiêu: một phiên mới **không nạp lại cả dự án**. Luật:

1. **Đọc theo tầng**: frontmatter trước (status.md, spec.md, ledger) → chỉ mở toàn văn khi frontmatter không
   đủ trả lời. `/dlc-resume` chỉ được đọc: `workspace-map.md`, frontmatter các `status.md`, thư mục
   `handoffs/` (frontmatter), danh sách `inbox/`. Không đọc `intent-plan.md`, `unit-plan.md`, `as-is/*` toàn văn.
2. **Tra cứu qua `session/INDEX.md`** — bản đồ "cần biết X → file Y, mục Z". Cần chi tiết thì đọc **đúng mục**
   (Grep/section), không đọc cả file dài.
3. **Không nhắc lại nội dung tài liệu trong MSG/HOF/câu trả lời** — trỏ `path#mục`. Người/agent cần thì mở.
4. **Kết thúc lượt là ghi ra file**, không giữ trong hội thoại: HOF đóng lại, `session/log/SES-NNN.md` một
   đoạn ngắn (làm gì, dừng ở đâu, ai đang giữ gì, việc kế tiếp).
5. Khi phải tóm tắt, tóm tắt **vào file**, và ghi rõ nguồn của bản tóm tắt để lần sau kiểm được.
