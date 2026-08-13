/* AI-DLC tower — markdown renderer tối giản, không phụ thuộc CDN ngoài.
   Đủ cho tài liệu gate: frontmatter, heading, list (kể cả checkbox), bảng, code fence,
   blockquote, hr, bold/italic/code/link. Escape HTML trước, chỉ sinh thẻ do chính mình tạo. */
(function () {
  const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

  function inline(s) {
    let t = esc(s);
    t = t.replace(/`([^`]+)`/g, '<code class="md-code">$1</code>');
    t = t.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    t = t.replace(/(^|[\s(])\*([^*\n]+)\*/g, '$1<em>$2</em>');
    t = t.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (m, a, b) => /^(https?:|#|\.|\/)/.test(b) ? '<a href="' + b + '" target="_blank" rel="noopener">' + a + '</a>' : a);
    // nhãn quy ước của AI-DLC — tô màu để đập vào mắt
    t = t.replace(/\[(CONFLICT|OPEN|ASSUMED|INFERRED|ADDED|MUST|SHOULD)\]/g, '<span class="md-tag md-tag-$1">[$1]</span>');
    // ID truy vết
    t = t.replace(/\b((?:INT|UOW|BOLT|TSK|MSG|RV|DEC|LL|REV|AC|US|S)-?\d+[\w-]*)\b/g, '<span class="md-id">$1</span>');
    return t;
  }

  function frontmatter(text) {
    const m = /^---\n([\s\S]*?)\n---\n?/.exec(text);
    if (!m) return { meta: null, body: text };
    const meta = {};
    m[1].split('\n').forEach(l => {
      const mm = /^([\w-]+):\s*(.*)$/.exec(l);
      if (mm) meta[mm[1]] = mm[2];
    });
    return { meta, body: text.slice(m[0].length) };
  }

  function render(text) {
    const fmres = frontmatter(text || '');
    const lines = fmres.body.split('\n');
    const out = [];
    let i = 0, listStack = [];

    const closeLists = (toDepth) => {
      while (listStack.length > toDepth) out.push('</' + listStack.pop() + '>');
    };

    while (i < lines.length) {
      const line = lines[i];

      // code fence
      const fence = /^```(\w*)/.exec(line);
      if (fence) {
        closeLists(0);
        const buf = [];
        i++;
        while (i < lines.length && !/^```/.test(lines[i])) buf.push(lines[i++]);
        i++;
        out.push('<pre class="md-pre"><code>' + esc(buf.join('\n')) + '</code></pre>');
        continue;
      }

      // bảng
      if (/^\s*\|/.test(line) && i + 1 < lines.length && /^\s*\|?[\s:*-]*-{2,}[\s|:-]*$/.test(lines[i + 1])) {
        closeLists(0);
        const cells = l => l.trim().replace(/^\||\|$/g, '').split('|').map(c => c.trim());
        const head = cells(line);
        i += 2;
        const body = [];
        while (i < lines.length && /^\s*\|/.test(lines[i])) body.push(cells(lines[i++]));
        out.push('<div class="md-tablewrap"><table class="md-table"><thead><tr>' +
          head.map(h => '<th>' + inline(h) + '</th>').join('') + '</tr></thead><tbody>' +
          body.map(r => '<tr>' + r.map(c => '<td>' + inline(c) + '</td>').join('') + '</tr>').join('') +
          '</tbody></table></div>');
        continue;
      }

      // heading
      const h = /^(#{1,6})\s+(.*)$/.exec(line);
      if (h) {
        closeLists(0);
        const lv = Math.min(h[1].length, 4);
        out.push('<h' + lv + ' class="md-h md-h' + lv + '">' + inline(h[2]) + '</h' + lv + '>');
        i++;
        continue;
      }

      if (/^\s*(---|\*\*\*|___)\s*$/.test(line)) { closeLists(0); out.push('<hr class="md-hr">'); i++; continue; }

      // blockquote (gộp nhiều dòng)
      if (/^\s*>/.test(line)) {
        closeLists(0);
        const buf = [];
        while (i < lines.length && /^\s*>/.test(lines[i])) buf.push(lines[i++].replace(/^\s*>\s?/, ''));
        out.push('<blockquote class="md-quote">' + inline(buf.join(' ')) + '</blockquote>');
        continue;
      }

      // list item
      const li = /^(\s*)([-*+]|\d+[.)])\s+(.*)$/.exec(line);
      if (li) {
        const depth = Math.floor(li[1].length / 2) + 1;
        const kind = /^\d/.test(li[2]) ? 'ol' : 'ul';
        while (listStack.length > depth) out.push('</' + listStack.pop() + '>');
        while (listStack.length < depth) { out.push('<' + kind + ' class="md-list">'); listStack.push(kind); }
        let body = li[3];
        const box = /^\[([ xX])\]\s*(.*)$/.exec(body);
        if (box) {
          const done = box[1].toLowerCase() === 'x';
          out.push('<li class="md-li md-check"><span class="md-box' + (done ? ' on' : '') + '">' +
            (done ? '✓' : '') + '</span>' + inline(box[2]) + '</li>');
        } else {
          out.push('<li class="md-li">' + inline(body) + '</li>');
        }
        i++;
        continue;
      }

      if (!line.trim()) { closeLists(0); i++; continue; }

      closeLists(0);
      const buf = [line];
      i++;
      while (i < lines.length && lines[i].trim() && !/^(\s*[-*+]|\s*\d+[.)]|#{1,6}\s|\s*\||\s*>|```)/.test(lines[i])) buf.push(lines[i++]);
      out.push('<p class="md-p">' + inline(buf.join(' ')) + '</p>');
    }
    closeLists(0);
    return { html: out.join('\n'), meta: fmres.meta };
  }

  /* Mục lục từ heading cấp 1–3 — để người duyệt nhảy thẳng tới phần cần soi */
  function outline(text) {
    const body = frontmatter(text || '').body;
    const items = [];
    body.split('\n').forEach(l => {
      const h = /^(#{1,3})\s+(.*)$/.exec(l);
      if (h) items.push({ level: h[1].length, text: h[2].replace(/[*`]/g, '').trim() });
    });
    return items;
  }

  const CSS = `
.md{color:var(--ink);font-family:var(--sans);font-size:15px;line-height:1.65;max-width:none}
.md .md-h{font-weight:700;letter-spacing:-0.01em;margin:22px 0 8px;line-height:1.25}
.md .md-h1{font-size:23px;border-bottom:2px solid var(--ink);padding-bottom:8px;margin-top:0}
.md .md-h2{font-size:18px;border-bottom:1px solid var(--line);padding-bottom:6px;margin-top:28px}
.md .md-h3{font-size:15.5px;color:var(--accent)}
.md .md-h4{font-size:14px;color:var(--muted);text-transform:uppercase;letter-spacing:0.08em}
.md .md-p{margin:8px 0}
.md .md-list{margin:6px 0 6px 0;padding-left:20px}
.md .md-li{margin:3px 0}
.md .md-check{list-style:none;margin-left:-18px;display:flex;gap:8px;align-items:flex-start}
.md .md-box{flex:none;width:14px;height:14px;border:1px solid var(--line);border-radius:3px;font-size:10px;
  line-height:13px;text-align:center;color:var(--ok);margin-top:3px}
.md .md-box.on{border-color:var(--ok)}
.md .md-quote{margin:10px 0;padding:8px 12px;border-left:2px solid var(--accent);background:var(--accent-bg);
  color:var(--ink);border-radius:0 var(--radius-sm) var(--radius-sm) 0}
.md .md-hr{border:none;border-top:1px solid var(--line);margin:20px 0}
.md .md-code{font-family:var(--mono);font-size:12.5px;background:var(--surface-2);padding:1px 5px;border-radius:4px}
.md .md-pre{background:var(--surface-2);border:1px solid var(--line);border-radius:var(--radius-md);
  padding:12px 14px;overflow-x:auto;margin:10px 0}
.md .md-pre code{font-family:var(--mono);font-size:12.5px;line-height:1.55;color:var(--ink)}
.md .md-tablewrap{overflow-x:auto;margin:12px 0;border:1px solid var(--line);border-radius:var(--radius-md)}
.md .md-table{border-collapse:collapse;width:100%;font-size:13px}
.md .md-table th{background:var(--surface-2);text-align:left;font-family:var(--mono);font-size:11px;
  letter-spacing:0.06em;text-transform:uppercase;color:var(--muted);padding:8px 10px;border-bottom:1px solid var(--line);white-space:nowrap}
.md .md-table td{padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
.md .md-table tr:last-child td{border-bottom:none}
.md .md-id{font-family:var(--mono);font-size:12.5px;color:var(--blue)}
.md .md-tag{font-family:var(--mono);font-size:11px;padding:1px 5px;border-radius:4px;border:1px solid;letter-spacing:0.04em}
.md .md-tag-CONFLICT,.md .md-tag-MUST{color:var(--danger);border-color:var(--danger);background:var(--danger-bg)}
.md .md-tag-OPEN,.md .md-tag-ASSUMED,.md .md-tag-SHOULD{color:var(--accent);border-color:var(--accent);background:var(--accent-bg)}
.md .md-tag-INFERRED,.md .md-tag-ADDED{color:var(--blue);border-color:var(--blue);background:var(--blue-bg)}
.md a{color:var(--blue)}
`;

  if (!document.getElementById('md-css')) {
    const st = document.createElement('style');
    st.id = 'md-css';
    st.textContent = CSS;
    document.head.appendChild(st);
  }

  window.MD = { render, outline, frontmatter, escape: esc };
})();
