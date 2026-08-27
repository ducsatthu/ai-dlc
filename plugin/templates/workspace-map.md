---
type: workspace-map
version: 2
updated: <ngày>
updated_by: <DEC-xxx | dlc-init>
---
# Workspace Map — output đi đâu (agents KHÔNG được đoán path)

> **Một `.ai-dlc/` = một space** (một đội ổn định, một bộ luật, một tower). Space **không** đại diện cho
> frontend/backend/mobile — đó là *code area*. Một đội làm nhiều repo vẫn là một space: đặt `.ai-dlc/` ở
> thư mục cha chứa các repo. Hai đội có người duyệt, practice và approval riêng ⇒ hai `.ai-dlc/`, mỗi cái ở
> thư mục đội đó sở hữu. Không có `spaces/` trong gói.
>
> Mọi `path` dưới đây **tương đối với thư mục chứa `.ai-dlc/`** (kể cả khi repo nằm ở thư mục con).

```yaml
repos:                        # nơi code sống — một hoặc nhiều git repo
  - id: main
    path: .                   # "." = chính thư mục chứa .ai-dlc/
areas:                        # code area = thư mục thật. Tên tự do: domain/api/web/mobile/infra/…
  backend:                    # (6.x đọc `code:` bên dưới — giữ cả hai tới 7.0.0)
    repo: main
    path: <path|null>
    tests: <path|null>
  frontend:
    repo: main
    path: <path|null>
    tests: <path|null>
code:                         # tương thích 6.x — suy từ areas; đừng để lệch
  frontend: <path|null>
  backend: <path|null>
docs:
  wiki: <path|null>
  ba_artifacts: <path|null>
  technical: <path|null>
  api_spec: <path|null>
tests:                        # tương thích 6.x
  backend: <path|null>
  frontend: <path|null>
conventions:
  language: vi
  rules: "<quy ước riêng của dự án>"
```

Unit khai `areas: [api, web]` trong `spec.md` — gate guard chặn theo area của Unit đang mở, tower vẽ
Unit → area, doctor cảnh báo khi Bolt ghi file ngoài area đã khai. Area không có trong map ⇒ doctor FIX.

## Changelog
- <ngày>: khởi tạo bởi /ai-dlc:dlc-init (map v2 — repos + areas, gói 6.2.0)
