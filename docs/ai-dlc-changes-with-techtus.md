# AI-DLC — Thay đổi khi áp dụng với TechTus

> Nguồn: AWS — AI-DLC Method Definition. Trích xuất từ slide deck `AI-DLC-changes-with-techtus.html` (Engineering process · 2026).
>
> Thông điệp chính: **AI-DLC thay đổi đơn vị công việc, không chỉ tốc độ sinh code.** So sánh với Agile / Sprint và với cách nhận một ticket lớn từ khách hàng — kèm quy trình cho dự án cần reverse engineering.

## 1. Bảng so sánh: Agile / Ticket-driven / AI-DLC

So sánh 3 cách chia việc từ 1 feature:

| | Agile / Sprint | Ticket-driven | AI-DLC |
|---|---|---|---|
| **Input** | Backlog / User Stories | Ticket khách hàng | Business Intent |
| **Planning** | Sprint Planning | BA / Tech Lead phân tích | AI tạo plan + hỏi clarification |
| **Breakdown** | Epic → Story → Task | Ticket → Subtasks | Unit of Work |
| **Cycle** | 1–2 tuần | Tùy ticket | **Bolt: giờ → vài ngày** |
| **Dev** | Dev chủ động code | Dev chủ động code | AI generate solution / code / test |
| **Human role** | Thực thi chính | Thực thi chính | **Review + quyết định** |
| **Delivery** | Cuối sprint / release | Khi ticket xong | Continuous, mỗi Unit of Work |

Tóm tắt: **Sprint → Bolt · Epic → Unit of Work.** Hai hàng khác biệt nhất là *Cycle* và *Human role*.

## 2. Đảo chiều hội thoại — AI-DLC không phải "Agile + AI agents"

**Agile hiện tại** — AI hỗ trợ trong từng bước, quy trình giữ nguyên:

1. Customer Request
2. BA analyze *(AI hỗ trợ phân tích)*
3. Create Epic / Story *(AI draft story)*
4. Sprint Planning
5. Dev code *(AI generate code)*
6. QA test *(AI generate tests)*
7. Review
8. Release

→ AI là công cụ hỗ trợ cho các đơn vị công việc hiện tại; nhịp độ và vai trò chưa thay đổi.

**AI-DLC** — hội thoại đảo chiều giữa AI và người:

| # | Bước | Lane |
|---|---|---|
| 1 | Business Intent | Human |
| 2 | Phân tích intent | AI |
| 3 | Hỏi những gì chưa rõ | AI |
| 4 | BA / PO / Dev quyết định | Human |
| 5 | Tạo requirements / design | AI |
| 6 | Team validate phương án, kế hoạch thực thi; xác định goal và DoD với quality gate và security gate | Human |
| 7 | Code + test | AI |
| 8 | Team review output | Human |
| 9 | Sửa theo review | AI |
| 10 | Deploy | Human |

→ **AI là execution engine. Người giữ context, trade-off và quyết định.**

## 3. Ví dụ: cùng một yêu cầu "Foreign National Onboarding"

**Ticket-driven (cách hiện tại):**

- Ticket: *Add Foreign National Onboarding*
- BA 1–2 ngày · hỏi customer · requirement · AC
- Tech Lead design solution · breakdown tasks
- Sprint 1: FE · BE · DB migration · Test
- Sprint 2: Bugs · Change request · Deploy
- → **2–4 tuần** trước khi khách hàng nhìn thấy bất kỳ phần nào chạy được.

**AI-DLC:**

- Intent: *"We want Foreign Nationals to complete onboarding before starting their immigration case."*
- AI discovers questions → Human decides → Requirements · User Stories · Acceptance Criteria
- Chia thành Units of Work:
  - UOW-01 Invitation → Mon (Bolt 1)
  - UOW-02 Personal Info → Tue (Bolt 2)
  - UOW-03 Immigration Info → Wed (Bolt 3)
  - UOW-04 Documents → Thu (Bolt 4)
  - UOW-05 Completion
- → **Mỗi Unit of Work deliver được ngay.**

## 4. Brown-field · Reverse engineering

> System đã có (code cũ) cho biết hệ thống **đang làm gì**, không cho biết business **muốn gì**. → AS-IS trước, TO-BE sau.

### Bốn dạng brown-field (theo paper)

1. **Add feature** — thêm chức năng vào hệ thống đang chạy
2. **Optimize NFR** — performance, scale, security
3. **Technical debt** — refactor, modernization
4. **Fix defect** — sửa lỗi trên hành vi hiện tại

Cả bốn dạng đều sửa lên một hệ thống đã tồn tại, nên AI luôn cần AS-IS trước khi bàn TO-BE.

### Dấu hiệu trong dự án outsourcing

- Không có tài liệu cập nhật
- Tiếp nhận từ vendor hoặc team trước
- Người viết code đã rời dự án
- Business rule chỉ nằm trong code
- Nhiều năm change request chồng lên nhau
- Test coverage thấp, khó biết regression

**Từ hai dấu hiệu trở lên, reverse engineering là bước bắt buộc — không phải tuỳ chọn.**

## 5. Context gap — chuẩn hóa context cho dự án đã chạy

Vấn đề của outsourcing không phải AI thiếu code, mà là **không ai ở vendor có đủ context**. Việc đầu tiên của AI không phải "generate code", mà là **"assemble the missing context"**:

| Nguồn | Context nắm giữ |
|---|---|
| Client | Why business needs it · Exceptions · Expected outcome |
| APM / BA | Ticket history · Scope · Customer discussion |
| Engineer | Current implementation · Architecture · Technical constraints |
| QA | Current behavior · Edge cases · Regression risks |
| Production | Real data · Logs · Actual usage |

> BA / APM không cần là người biết câu trả lời, mà là người đảm bảo **đúng người trả lời đúng câu hỏi**.

### Hierarchy thay cho ticket-driven

- **Customer Request** — thứ khách hàng gửi
- **Intent** — outcome đã được làm rõ
- **Unit** — business capability deliver được
- **Bolt** — vòng build–validate vài giờ tới vài ngày
- **Task** — technical action

Ticket của khách không còn là đơn vị execution — chỉ là đầu vào để khám phá context.

## 6. Flow 8 stage — từ Customer Request tới Context Memory

Ba lane: **Client · Delivery Team (Human tasks) · AI Agents (AI tasks)**. Stage 2–3 là phần thêm cho dự án cần reverse engineering (so với AI-DLC nguyên bản).

### Discovery

| Stage | Client | Delivery Team | AI Agents |
|---|---|---|---|
| **1 · Request** | "Change how RFE/NOID cases are closed." | PM/BA capture: problem · outcome · priority | Nhận diện Brownfield Enhancement + vùng ảnh hưởng |
| **2 · Context Discovery** | | | Đọc code · docs · tickets · tests · DB → AS-IS model (static + dynamic) |
| **3 · Context Validation** | Validation Mob — Client SME · BA/PM · Dev · QA | (cùng Validation Mob) | AI trình bày understanding về status hiện tại |
| **4 · Clarification** | Client quyết định business | BA facilitate: đúng người trả lời | AI generate open questions |

### Delivery

| Stage | Client | Delivery Team | AI Agents |
|---|---|---|---|
| **5 · Unit Definition** | Approve scope | Validate: Unit = observable outcome | AI chia Intent thành Units theo business capability |
| **6 · Construction** | | Dev validate từng bước | Domain Design → Logical Design → Code + Tests → Fix |
| **7 · Acceptance** | Business acceptance / UAT → approve deploy | Internal acceptance | Acceptance Evidence: AC · tests · screenshots · limitations |
| **8 · Release** | | Trace decision → requirement → design → code | Persist mọi artefact → **Context Memory** |

Ví dụ minh họa cho request "RFE/NOID cases":

- **Open questions:** tên terminal status? ai được close? case cũ có migrate? reporting có loại trừ?
- **Units:** Lifecycle Rules · Case Sync · Reporting Adjustment · Data Migration
- **Không phải Unit:** "Update DB" · "Add API" · "Update UI"

## 7. Kết — 4 thay đổi

Nếu team áp dụng AI-DLC, thứ đổi trước không phải công cụ mà là **cách chia và nghiệm thu công việc**:

1. **Sprint → Bolt**
2. **Epic → Unit of Work**
3. **Thực thi → Review và quyết định**
4. **Delivery cuối sprint → Liên tục**

*Không kết luận AI-DLC thay thế Agile — đây là so sánh để team tự quyết định áp dụng ở tầng nào.*
