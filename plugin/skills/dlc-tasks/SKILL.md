---
name: dlc-tasks
description: Xem/cập nhật task board của một Bolt (args UOW-NN [BOLT-NN]) — trạng thái, claim, approver, comms links. Enforce luật claim khi cập nhật.
---

> Engine `contracts` (template đội): không có task board. Unit và trạng thái nằm ở `plan.md` và bảng Work Units của
> `evidence.md`; xem bằng `/ai-dlc:dlc-status`.

1. In board `tasks.md` gọn: TSK · tên · status · claimed_by · approver · depends_on · số MSG.
2. Cập nhật theo yêu cầu user nhưng enforce protocol §4.7 (claim khi depends done+ký; một task một người). Thay đổi trạng thái đáng kể → MSG note.
