---
name: source-plan
version: 1
---
# Checklist Source Reading Plan · v1
> Dùng cho phần 2 của `intent-plan.md` (Gate A) và cho `as-is/source-ledger.md` (Gate B).
> Đây là hàng rào chống lỗi tốn kém nhất của flow: **đọc thiếu / đọc sai / đọc nguồn cũ ở đầu luồng**.

## plan-completeness (Gate A)
- [ ] Bảng nguồn được dựng bằng **quét thật** (có ghi lệnh/pattern đã quét ở mục 2.5), không phải liệt kê theo trí nhớ
- [ ] Mọi vùng ảnh hưởng ở mục 1.6 đều có **ít nhất một nguồn P0** phủ; vùng không có nguồn được nêu đích danh ở 2.5
- [ ] Đủ 5 họ nguồn khi có liên quan: doc-SSOT · code · api-spec/schema · test · decision/tracker
- [ ] Có nguồn **ngoài repo** (người, hệ thống ngoài, data thật) nếu intent chạm tới — không giả vờ mọi thứ nằm trong repo
- [ ] Mỗi dòng nêu **thông tin cụ thể phải lấy ra**, không phải "đọc để hiểu"
- [ ] Mỗi dòng có ưu tiên P0/P1/P2 và **rủi ro nếu bỏ qua**
- [ ] Nguồn biết trước là không có → trạng thái `missing` + đã thành câu hỏi ở 2.4, không im lặng
- [ ] Mục 2.3 nêu rõ vùng **cố ý không đọc** + lý do (chống đọc tràn lan lẫn chống bỏ sót ngầm)
- [ ] Thứ tự đọc (2.2) đặt SSOT và decision trước code — không kết luận business từ code

## ledger-completeness (Gate B)
- [ ] **Không còn dòng `planned`** — mọi nguồn có trạng thái cuối (`read`/`missing`/`deferred`/`superseded`)
- [ ] Mỗi dòng `read` có **vùng đã đọc** (dòng/section) + **phát hiện 1 câu** — thiếu evidence = coi như chưa đọc
- [ ] Nguồn `[ADDED]` ngoài plan đều có ghi phát hiện lúc nào, từ nguồn nào
- [ ] `deferred` có chủ + mốc + rủi ro chấp nhận, `missing` có ghi đã hỏi ai ngày nào
- [ ] Mâu thuẫn giữa nguồn ghi ở mục 3 và đã thành câu hỏi Gate C — agent KHÔNG tự chọn bên
- [ ] Mục 4 (vùng chưa có nguồn phủ) đã chuyển thành risk có chủ hoặc câu hỏi cho người
- [ ] Khẳng định suy luận gắn `[INFERRED]` và không bị dùng làm căn cứ AC

## trace (mọi lúc)
- [ ] Mỗi Unit liệt kê được nguồn nào chứng minh cho nó (`sources:` trong spec.md khớp ledger)
- [ ] Không có kết luận nào trong AS-IS/Unit mà không truy được về một dòng ledger

## Changelog
- v1: bản đầu — sinh cùng protocol v2 (stage 1 sinh Source Reading Plan, Gate B soi ledger)
