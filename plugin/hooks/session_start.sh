#!/bin/bash
# AI-DLC SessionStart hook: nạp binding rules + báo inbox tồn đọng.
# Chỉ hoạt động khi project đã init (.ai-dlc/ tồn tại) — nếu chưa, im lặng.
ROOT="$(pwd)"
# 6.3.0: state ở đâu / engine nào do scripts/layout.py trả lời (env · ai-dlc.config.json · fence ```ai-dlc trong
# CLAUDE.md/AGENTS.md · tự dò). Không có python3 ⇒ luật cũ 6.2.0: tìm .ai-dlc/context-memory từ cwd đi lên 2 cấp.
_LAYOUT="$(dirname "$0")/../scripts/layout.py"
AI_DLC_L_ENGINE=""; AI_DLC_L_ROOT=""; AI_DLC_L_STATE=""; AI_DLC_L_SPACE=""; AI_DLC_L_GOVERNANCE=""; AI_DLC_L_TOWER_PORT=""; AI_DLC_L_SOURCE=""
if command -v python3 >/dev/null 2>&1 && [ -f "$_LAYOUT" ]; then
  eval "$(python3 "$_LAYOUT" --env 2>/dev/null)"
fi
case "$AI_DLC_L_ENGINE" in
  off) exit 0 ;;
  aws-v2)
    echo "# AI-DLC (plugin ai-dlc) — workspace AWS aidlc-workflows v2 tại $AI_DLC_L_ROOT (space: $AI_DLC_L_SPACE; cấu hình: $AI_DLC_L_SOURCE)"
    echo "Gói là LỚP CHÍNH SÁCH + TOWER trên engine AWS v2 (\${CLAUDE_PLUGIN_ROOT}/references/aws-v2-workspace.md):"
    echo "- Lifecycle do engine AWS giữ (/aidlc, aidlc-orchestrate.ts) — gói KHÔNG tạo .ai-dlc/context-memory ở đây."
    echo "- Luật gói (RACI, test-viewpoints, im lặng = mặc định): $AI_DLC_L_GOVERNANCE/"
    echo "- Tower: python3 \${CLAUDE_PLUGIN_ROOT}/scripts/tower_aws_v2.py --serve (hoặc /ai-dlc:dlc-tower serve, port $AI_DLC_L_TOWER_PORT)."
    echo "- Người duyệt ngoài phiên: bun \${CLAUDE_PLUGIN_ROOT}/scripts/tower_approve.ts --stage <slug> --result approved|rejected --input \"...\""
    exit 0 ;;
  ai-dlc)
    ROOT="$AI_DLC_L_ROOT"; AIDLC="$AI_DLC_L_STATE" ;;
  *)
    _cur="$ROOT"; _found=""
    for _i in 0 1 2; do
      if [ -d "$_cur/.ai-dlc/context-memory" ]; then _found="$_cur"; break; fi
      _parent="$(dirname "$_cur")"; [ "$_parent" = "$_cur" ] && break; _cur="$_parent"
    done
    [ -n "$_found" ] && ROOT="$_found"
    AIDLC="$ROOT/.ai-dlc" ;;
esac
[ -d "$AIDLC" ] || exit 0
[ "$ROOT" != "$(pwd)" ] && echo "(state của space này nằm ở $AIDLC — path trong workspace-map tương đối với $ROOT)"
[ -n "$AI_DLC_L_SOURCE" ] && [ "$AI_DLC_L_SOURCE" != "none" ] && echo "(cấu hình layout: $AI_DLC_L_SOURCE)"

echo "# AI-DLC (plugin ai-dlc) — project đã init"
echo ""
echo "BINDING RULES (bắt buộc cho mọi agent/skill dlc-*):"
echo "1. Đọc \${CLAUDE_PLUGIN_ROOT}/references/protocol.md trước khi làm việc AI-DLC."
echo "2. Override thắng: kiểm tra .ai-dlc/overrides/ trước khi dùng checklist/governance."
echo "3. Agent trong một intent đọc checklist/governance từ intents/INT-xxx/pinned/."
echo "4. Output (code/docs) resolve path qua .ai-dlc/workspace-map.md — KHÔNG đoán path."
echo "5. Không stage/gate nào được vượt khi chưa có DEC. AI đề xuất trước — con người xác nhận trước khi đi tiếp."
echo "6. Giao việc cho agent bằng file handoffs/HOF-NNNN.md, KHÔNG nhồi bối cảnh vào prompt (protocol §9)."
echo "7. Đọc ít, tra đúng chỗ: dùng context-memory/session/INDEX.md; KHÔNG nạp toàn văn intent-plan/unit-plan/as-is (§10)."
echo ""
echo "VÀO LẠI DỰ ÁN: chạy /ai-dlc:dlc-resume — dựng bảng vị trí từ handoffs, in briefing gọn, tiếp tục đúng chỗ dừng."

# codekb (6.2.0): bản đồ code dùng lại — nhắc trạng thái tươi
for fr in "$AIDLC"/codekb/*/freshness.md; do
  [ -f "$fr" ] || continue
  RP=$(grep -m1 '^repo:' "$fr" | sed 's/repo: *//'); ST=$(grep -m1 '^status:' "$fr" | sed 's/status: *//; s/ *#.*//')
  echo "codekb/$RP: $ST — dlc-discover phải kiểm lại với HEAD trước khi reuse (ghi mục 0 của source-ledger)."
done

# Vị trí đang treo (HOF chưa đóng)
HOFS=$(grep -l '^status: accepted' "$AIDLC"/context-memory/handoffs/HOF-*.md 2>/dev/null | head -10)
if [ -n "$HOFS" ]; then
  echo ""
  echo "VỊ TRÍ CÒN TREO (handoff đang accepted — có thể là phiên trước dừng giữa chừng):"
  for f in $HOFS; do
    TO=$(grep -m1 '^to:' "$f" | sed 's/to: *//')
    RE=$(grep -m1 '^re:' "$f" | sed 's/re: *//')
    echo "- $(basename "$f" .md) · $TO · $RE"
  done
  echo "Tiếp tục từ chính file HOF đó (mục 'Còn treo'), không dựng lại bối cảnh từ đầu."
fi

# Drain inbox: liệt kê quyết định từ tower chưa xử lý
PENDING=$(ls "$AIDLC/inbox/"*.json 2>/dev/null | head -20)
if [ -n "$PENDING" ]; then
  echo ""
  echo "INBOX CÓ VIỆC NGƯỜI ĐÃ GỬI TỪ CONTROL TOWER, CHƯA ÁP — orchestrator phải drain NGAY đầu phiên:"
  for f in $PENDING; do echo "- $f"; done
  echo "gate-*.json: đối chiếu gate đang chờ trong status.md → ghi DEC → move sang inbox/processed/ → chạy tiếp flow."
  echo "answer-*.json: áp NGUYÊN VĂN câu trả lời vào file open-questions (Trạng thái đã chốt + bảng Đã trả lời + changelog); câu blocking → gỡ chặn, tiếp tục HOF đang đứng. direction-*.json: ghi mục 'Chỉ đạo' + owner/status vào escalations/ESC-NNN.md. Xong mới move sang processed/ (protocol §5)."
fi

# Gate đang mở
for st in "$AIDLC"/context-memory/intents/*/status.md; do
  [ -f "$st" ] || continue
  GO=$(grep -m1 '^gate_open:' "$st" | sed 's/gate_open: *//')
  IN=$(grep -m1 '^intent:' "$st" | sed 's/intent: *//')
  if [ -n "$GO" ] && [ "$GO" != "null" ]; then
    echo ""
    echo "GATE ĐANG MỞ: $IN chờ quyết định tại Gate $GO — không chạy stage sau của intent này."
  fi
done
exit 0
