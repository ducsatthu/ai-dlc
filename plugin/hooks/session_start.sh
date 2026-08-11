#!/bin/bash
# AI-DLC SessionStart hook: nạp binding rules + báo inbox tồn đọng.
# Chỉ hoạt động khi project đã init (.ai-dlc/ tồn tại) — nếu chưa, im lặng.
ROOT="$(pwd)"
AIDLC="$ROOT/.ai-dlc"
[ -d "$AIDLC" ] || exit 0

echo "# AI-DLC (plugin ai-dlc) — project đã init"
echo ""
echo "BINDING RULES (bắt buộc cho mọi agent/skill dlc-*):"
echo "1. Đọc \${CLAUDE_PLUGIN_ROOT}/references/protocol.md trước khi làm việc AI-DLC."
echo "2. Override thắng: kiểm tra .ai-dlc/overrides/ trước khi dùng checklist/governance."
echo "3. Agent trong một intent đọc checklist/governance từ intents/INT-xxx/pinned/."
echo "4. Output (code/docs) resolve path qua .ai-dlc/workspace-map.md — KHÔNG đoán path."
echo "5. Không stage/gate nào được vượt khi chưa có DEC. AI đề xuất trước — con người xác nhận trước khi đi tiếp."

# Drain inbox: liệt kê quyết định từ tower chưa xử lý
PENDING=$(ls "$AIDLC/inbox/"*.json 2>/dev/null | head -20)
if [ -n "$PENDING" ]; then
  echo ""
  echo "INBOX CÓ QUYẾT ĐỊNH CHƯA XỬ LÝ (từ Control Tower) — orchestrator phải drain NGAY đầu phiên:"
  for f in $PENDING; do echo "- $f"; done
  echo "Với mỗi file: đối chiếu gate đang chờ trong status.md → ghi DEC vào governance/decisions-log.md → move file sang inbox/processed/ → chạy tiếp flow."
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
