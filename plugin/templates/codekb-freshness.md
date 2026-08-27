---
type: codekb-freshness
repo: <repo-id trong workspace-map>
promoted_from: INT-NNN          # intent đã dựng AS-IS này (đóng ở stage 8)
promoted_at: <ngày>
git_head: <sha đầy đủ lúc AS-IS được đọc>
areas_scanned: [api, web]       # area của workspace-map mà AS-IS này phủ
ledger: intents/INT-NNN/as-is/source-ledger.md   # bằng chứng đã đọc gì
status: CURRENT                 # CURRENT | STALE | UNKNOWN_SCOPE — chỉ dlc-discover/doctor được đổi
checked_at: <ngày>
checked_head: <sha lúc kiểm gần nhất>
---
# codekb/<repo> — bản đồ code bền vững, dùng lại qua nhiều intent

Ba file bên cạnh (`static-model.md` · `dynamic-model.md` · `decisions-inventory.md`) là `as-is/` của
`promoted_from` được **promote nguyên văn** khi intent đó đóng — không viết lại, không "làm đẹp".
Mỗi khẳng định trong đó vẫn trỏ về dòng ledger của intent gốc.

## Cách intent kế dùng (dlc-discover, protocol §4.8)

1. So `git_head` với HEAD hiện tại: `git diff --name-only <git_head>..HEAD -- <path của areas_scanned>`.
   - Không có file đổi trong area intent chạm ⇒ `CURRENT` ⇒ **reuse**: mỗi file codekb dùng là một
     dòng `read` trong ledger mới, evidence = `codekb/<repo>/freshness.md CURRENT @<head>`.
   - Có file đổi ⇒ `STALE` ⇒ quét **delta** (chỉ file đổi) → `as-is/delta.md`; codekb vẫn reuse cho phần
     không đổi, ledger ghi rõ dòng nào từ codekb, dòng nào từ delta.
   - Area intent chạm không nằm trong `areas_scanned` ⇒ `UNKNOWN_SCOPE` ⇒ quét area đó như chưa có codekb.
2. Quyết định reuse/rescan ghi ở mục **0** của `source-ledger.md` intent mới — người duyệt Gate B nhìn
   thấy, không phải tin lời "đã đọc rồi".
3. **Không** sửa tay ba file model ở đây giữa intent. Cập nhật duy nhất là promote lại khi intent kế đóng.

## Lịch sử promote
| Ngày | Từ intent | HEAD | Areas |
|---|---|---|---|
| <ngày> | INT-NNN | <sha7> | api, web |
