# Control Tower v2 — màn hình của Lead (decision-first)

> Trạng thái: **SPEC — thay cho design prompt đã gỡ** · Ngày: 2026-08-21 · Tuân theo `whitepaper-ai-dlc-vi.md` v2 (§II ba loại điểm dừng, §III Sổ giả định, §IV Showcase, §V Gate R, §VII.3 Bản tin ca).
>
> Một câu: **mở tower lên chỉ thấy những gì cần tôi quyết. Mọi hoạt động của AI ẩn; chỉ khi tôi muốn mới tra cứu.**

---

## 0 · Vì sao tower hiện tại loạn

*Mission Control* của 6.0.0 đặt **chín panel trên một màn**: Gate queue · Pipeline board · Vị trí đang làm việc · Agent team phiên sống · Hoạt động gần đây · Live feed · Phát hiện ngoài phạm vi · Tin chết · ô KPI. Trong chín cái đó, **chỉ Gate queue là việc của Lead**; tám cái còn lại là telemetry để *gỡ lỗi đội AI*. Đặt chung ⇒ Lead phải tự lọc "cái nào là của tôi" mỗi lần mở — đó là việc tower phải làm thay.

Ba lỗi thiết kế cụ thể:
1. **Trộn hai người dùng**: Lead (quyết) và người vận hành gói (soi agent, heartbeat, tin chết). v2 chỉ có một người dùng chính là Lead; người vận hành tra cứu khi cần.
2. **Hiển thị theo nguồn dữ liệu**, không theo câu hỏi: panel = thư mục trong `.ai-dlc/` (handoffs → Vị trí, comms → Live feed…). Lead không nghĩ theo thư mục.
3. **Không có mặc định**: mỗi mục chờ đều "chờ", không nói *nếu tôi không làm gì thì sao*.

## 1 · Ba tầng — và chỉ tầng 0 hiện mặc định

| Tầng | Tên | Khi nào thấy | Chứa gì |
|---|---|---|---|
| **0** | **Cần tôi quyết** (Hộp quyết định) | **màn mặc định, duy nhất khi mở tower** | chỉ thẻ cần Lead hành động (§2). Trống ⇒ một dòng *"Không có gì cần bạn. Đội đang làm việc — Bản tin ▸"* và **không hiện gì khác** |
| **1** | **Bản tin ca** | bấm một nút, hoặc khi Hộp trống | một trang §VII.3: đã làm · giả định mới · sẵn để nhìn · cần quyết · ranh đỏ · Gate R. Bằng lời, không bảng |
| **2** | **Tra cứu** | **ẩn** sau menu "Tra cứu…" hoặc link *Xem thêm ▸* từ một thẻ | mọi thứ còn lại: Intents · Bolt/Task Board · Comms & Reviews · Agents & HOF (vị trí, heartbeat, tin chết) · Hoạt động gần đây · Dòng chảy 3 pha · Sổ giả định đầy đủ · KPI · Governance |

Luật: **không panel nào của tầng 2 được xuất hiện trên tầng 0**, kể cả dạng "tóm tắt nhỏ". Muốn xem agent đang làm gì ⇒ đi sang Tra cứu. Đây là luật cứng, vì mọi "tóm tắt nhỏ" đều lớn dần.

## 2 · Hộp quyết định — năm loại thẻ, theo thứ tự

| # | Loại | Ký hiệu | Nguồn dữ liệu | Hành động trên thẻ |
|---|---|---|---|---|
| 1 | **Ký Gate R** | ■ | `gates/GATE-R-NN.md` `status: open` | *Đọc hồ sơ* (preview toàn văn bắt buộc) → `release` / `hold` |
| 2 | **Ranh đỏ** | ■ | `red-lines/RED-NN.md` `status: open` | chọn phương án → ghi `DEC` |
| 3 | **Mốc chờ sắp hết hạn** | ◇⏱ | `checkpoints/CP-NN.md` có `wait_until` chưa qua | *Giữ mặc định* / *Đổi: …* (ghi `STR`) — countdown hiện rõ |
| 4 | **Showcase chờ phản hồi** | ◉ | `showcases/SC-NN/` chưa có `feedback.md` | *Mở sản phẩm* (URL/lệnh) + bảng giả định với nút ba trạng thái từng dòng → `FB` |
| 5 | **Câu hỏi cần bạn** | ? | mục 3 của Showcase Pack, hoặc `ASM` `reversal_cost: vừa` chưa nhìn | trả lời một dòng hoặc *Dùng mặc định* — **ngay trên thẻ** (6.1.0: `POST /answer` → `inbox/answer-*.json`, phiên Claude Code áp nguyên văn rồi làm tiếp; thẻ ■ escalation có ô *Chỉ đạo* → `inbox/direction-*.json`) |

Tối đa **7 thẻ** hiện; còn lại gấp thành *"và N việc khác ▸"* (ưu tiên theo thứ tự bảng, rồi theo hạn). Lead không bao giờ thấy danh sách 40 dòng.

### 2.1 Giải phẫu một thẻ

```
┌─ ◇⏱ Mốc chờ · còn 2h10 ───────────────────────────────── UOW-03 ─┐
│ Ai được phép đóng RFE case?                                        │
│                                                                    │
│ Nếu bạn im lặng tới 15:00 → chỉ APM được đóng (ASM-017)            │
│                                                                    │
│ ○ Chỉ APM (mặc định)                          + 0h                 │
│ ○ APM và Paralegal                            + 2h · thêm quyền+test│
│ ○ Khác: [__________]                                               │
│                                                                    │
│ [ Giữ mặc định ]   [ Chọn & bẻ lái ]              Xem thêm ▸ ASM-017│
└────────────────────────────────────────────────────────────────────┘
```

Bắt buộc có đủ năm phần, thiếu một là thẻ **không được lên Hộp** (trưởng ca phải bổ sung):
1. **Câu hỏi một dòng, bằng lời** — không mã, không tên file, không thuật ngữ agent.
2. **"Nếu bạn im lặng"** + hạn (Gate R và Ranh đỏ ghi *"không có mặc định — flow đang đứng"*).
3. **2–3 phương án, mỗi cái có giá** (giờ hoặc Bolt) — lấy từ `alternatives` + `reversal_cost` của ASM.
4. **Nút quyết ngay trên thẻ** — không chuyển màn, không mở terminal.
5. **Xem thêm ▸** lazy: mở đúng **một** artefact (ASM · Showcase Pack · hồ sơ Gate R · RED) trong drawer bên phải. Không bao giờ dẫn sang board/agents/feed.

### 2.2 Thẻ Showcase — dạng đặc biệt

```
┌─ ◉ Showcase · UOW-03 Đóng RFE/NOID case · sẵn từ 11:40 ───────────┐
│ Dùng thử ~10 phút:  http://localhost:3000/cases?demo=sc-03         │
│                      (hoặc: make demo-sc-03)                       │
│ Bấm gì, nhìn gì ▸  (10 bước, gấp)                                   │
│                                                                    │
│ Giả định đang hiện ở đây — bạn thấy đúng không?                    │
│  ASM-014 chỉ một trạng thái đóng          [giữ] [đổi] [làm lại]    │
│  ASM-015 case đóng vẫn tính KPI tháng     [giữ] [đổi] [làm lại]    │
│  ASM-017 chỉ APM được đóng                [giữ] [đổi] [làm lại]    │
│                                                                    │
│ [ Xong — gửi phản hồi ]                      Bằng chứng máy ▸ (gấp)│
└────────────────────────────────────────────────────────────────────┘
```

## 3 · Sidebar — của Lead, không phải của phương pháp

### 3.1 Sidebar 6.0.0 đang nói gì với Lead

```
◇ Control Tower
  AI-DLC · 18 AGENTS · GATES A–G          ← thông tin về gói, không về việc của tôi
◇ Mission Control                   (2)   ← tên màn bằng tiếng Anh phương pháp
≡ Dòng chảy 3 pha
INTENT → UNIT → BOLT            bảng 3    ← tên cấp bậc của phương pháp
▾ ● INT-003 Nối backend Quality…  gate E  ← mã + chấm màu không chú giải + mã gate
    ● UOW-01 Lifecycle Rules        △     ← mã, chấm, tam giác không rõ nghĩa
    ● UOW-02 Case Sync
      BOLT-02  2/4 chặng · 5 task         ← chi tiết thi công
    … (28 dòng nữa)
    +2 unit ngoài phạm vi                 ← thuật ngữ nội bộ
    +1 unit lỗi thời (_trash)             ← tên thư mục
XUYÊN SUỐT
→ Comms & Reviews
△ Governance & Learning
supervisor · Human                        ← tôi là "supervisor · Human"?
```

Ba lỗi: **(1) nói bằng mã thay vì bằng tên** (`UOW-03` thay vì "Đóng RFE/NOID case"); **(2) đưa cấu trúc thi công lên điều hướng** (bolt, chặng, task, _trash — Lead không điều hướng theo bolt); **(3) trạng thái bằng màu và ký hiệu** (● △ gate E) thay vì bằng lời ("chờ bạn", "đang làm").

### 3.2 Sidebar v2

```
┌──────────────────────────┐
│ PILOT                       │   ← tên dự án, chữ thường, không logo phương pháp
│                           │
│ ▸ Cần tôi quyết       (3) │   ← mặc định; badge = số thẻ
│   Bản tin hôm nay         │
│                           │
│ VIỆC ĐANG LÀM             │
│   Nối backend Quality Gate│   ← tên yêu cầu, không mã
│   đang xây 12/30 · 1 chờ bạn      ← một dòng trạng thái bằng lời
│   Khung UI Quality Gate   │
│   đã xong · 20/20         │
│                           │
│ ────────────────────────  │
│   Tra cứu ▾               │   ← mọi thứ khác ở đây, gấp
│                           │
│ cập nhật 2 phút trước     │
└──────────────────────────┘
```

Luật:

1. **Tên, không mã.** Dòng chính là tên yêu cầu bằng lời; mã (`INT-003`) chỉ hiện khi hover hoặc trong Tra cứu. Trên mọi thẻ/màn của tầng 0–1 cũng vậy: *"Đóng RFE/NOID case"* trước, `UOW-03` nhỏ mờ sau.
2. **Chỉ tới cấp Yêu cầu (Intent).** Unit hiện **trong** màn của yêu cầu đó dưới dạng danh sách phần việc bằng lời; Bolt / chặng / task / `_trash` / "ngoài phạm vi" **không bao giờ** lên sidebar — chúng thuộc Tra cứu.
3. **Trạng thái bằng lời, một dòng, tối đa hai ý**: `đang xây 12/30 · 1 chờ bạn` · `đã xong` · `đang đứng — ranh đỏ` · `sẵn để bạn xem`. Màu chỉ *phụ hoạ* chữ (hổ phách cho "chờ bạn", xanh cho "xong") — không có chấm đứng một mình, không tam giác, không chữ `gate E`.
4. **Tối đa 5 yêu cầu** hiện; yêu cầu đã xong > 30 ngày gấp vào "đã xong (N) ▸".
5. **Tra cứu là một mục gấp**, mở ra danh sách: *Phần việc & vòng xây* (Bolt/Task Board) · *Trao đổi & soát* (Comms & Reviews) · *Đội AI* (Agents & HOF — Mission Control cũ) · *Dòng chảy 3 pha* · *Sổ giả định* · *Số liệu* (KPI) · *Luật & bài học* (Governance & Learning). Tên tiếng Việt trước, tên cũ trong ngoặc nhỏ để người quen 6.0.0 không lạc.
6. **Chân sidebar**: chỉ "cập nhật N phút trước" bằng lời. Bỏ `supervisor · Human`, bỏ `18 agents · gates A–G`.
7. **Rộng 220px**, chữ 13.5px sans cho tên, 11px cho dòng trạng thái; mono chỉ cho badge số.

### 3.3 Từ vựng hiện trên tầng 0–1 (Lead nhìn) ↔ thuật ngữ gói (Tra cứu)

| Lead thấy | Thuật ngữ gói (giữ nguyên trong Tra cứu, file, HOF) |
|---|---|
| Yêu cầu | Intent |
| Phần việc | Unit |
| Vòng xây | Bolt |
| Chờ bạn ký | Gate R / Gate mở |
| Đang đứng — cần bạn | Ranh đỏ / Escalation |
| Bạn xem thử được | Showcase |
| Giả định | ASM |
| Bẻ lái | Steer / STR |
| Đội AI | Agents / HOF / heartbeat |
| Trao đổi & soát | Comms & Reviews (MSG/RV) |
| Luật & bài học | Governance & Learning (DoR/DoD/LL) |

Quy ước của Design System ("thuật ngữ tiếng Anh không dịch") **vẫn đúng cho tầng Tra cứu và mọi file trong `.ai-dlc/`** — đó là ngôn ngữ làm việc của đội AI và của người vận hành gói. Tầng 0–1 là ngôn ngữ của Lead; hai tầng nối nhau bằng mã nhỏ mờ và hover.

### 3.4 Thanh trên

```
┌──────────────────────────────────────────────────────────────┐
│ Cần tôi quyết                                  [sáng/tối]     │
│ 3 việc · việc gần hạn nhất: 2h10                              │
└──────────────────────────────────────────────────────────────┘
```

Không breadcrumb mã (`INT-003 › UOW-03 › BOLT-02`) ở tầng 0–1; breadcrumb chỉ có trong Tra cứu.

## 4 · Thông báo

| Sự kiện | Push (desktop/phone) | Badge | Bản tin |
|---|---|---|---|
| Gate R mở · Ranh đỏ | có | có | có |
| Mốc chờ còn < 1h | có | có | có |
| Showcase sẵn | không (trừ khi Lead bật) | có | có |
| Câu hỏi cần bạn | không | có | có |
| Agent im lặng / tin chết / HOF drift / CP thường | **không** | **không** | một dòng trong mục "Sức khoẻ đội" cuối Bản tin |

## 5 · Áp lên tower 6.0.0 ngay — không cần chờ 7.0.0

> **Đã làm ở 6.1.0 (2026-08-22)**: `LeadInbox.jsx` (tầng 0) · `Brief.jsx` (tầng 1) · sidebar §3.2 · Tra cứu gấp · hàng chọn phần việc trong Bolt Board. Kiểm trên dữ liệu thật PILOT: 19 thẻ (12 đang đứng · 5 câu chặn · 2 bó câu không chặn), 0 lỗi console. Còn nợ 7.0.0: Showcase Pack thật, Mốc chờ, ghi `FB` từ tower.

Dữ liệu của 6.0.0 đã đủ để dựng tầng 0 theo cách ánh xạ sau (một ngày làm, không đổi luật gate):

| Thẻ v2 | Nguồn 6.0.0 hiện có |
|---|---|
| ■ Gate | Gate queue A–G (`status.md` `gate_open`) — giữ luật preview |
| ■ Ranh đỏ | `escalations/ESC-NNN.md` `status: open` + MSG `type: escalation` |
| ? Câu hỏi | `open-questions-business.md` / `-tech.md` dòng chưa chốt — **đã có sẵn "phương án chọn sẵn kèm giá" và "mặc định nếu im lặng"** (§4.10 cũ) ⇒ đổ thẳng vào thẻ |
| ◉ Showcase | Gate E(b) đang mở ⇒ thẻ Showcase (tạm thời link tới `evidence/`) |
| ◇⏱ Mốc chờ | chưa có ở 6.0.0 — bỏ trống |

Việc: thêm `LeadInbox.jsx` làm màn mặc định; viết lại `Sidebar` trong `Shell.jsx` theo §3.2 (tên thay mã, chỉ tới cấp yêu cầu, trạng thái bằng lời, Tra cứu gấp, bỏ header/footer kỹ thuật); `MissionControl.jsx` đổi tên thành *Đội AI* và nằm trong Tra cứu; `IntentDetail.jsx` liệt kê phần việc bằng tên. Generator chỉ cần thêm `intents[].name` dạng lời và một dòng `summary` ("đang xây 12/30 · 1 chờ bạn") — các trường còn lại đã có. Đây là bước đi được **trước** khi chốt phương án A/B/C của transition plan, và dùng được cho INT-003 đang chạy.

## 6 · Đo

- `tower.inbox_size` — số thẻ trung bình khi Lead mở (đích ≤ 5).
- `tower.time_to_decide` — từ lúc thẻ lên tới lúc có quyết định (đích: Mốc chờ < hạn; Showcase < 1 ngày).
- `tower.lookup_rate` — tỉ lệ phiên Lead mở Tra cứu (đích: thấp; cao ⇒ thẻ thiếu thông tin, sửa thẻ chứ không kéo panel lên tầng 0).
- `tower.card_rejected` — thẻ bị trưởng ca trả vì thiếu một trong năm phần (§2.1) — đích → 0.
