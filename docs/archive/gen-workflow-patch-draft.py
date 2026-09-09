# -*- coding: utf-8 -*-
"""Sinh trang HTML 'Bản vá workflow đích' — SVG swimlane hand-authored qua danh sách node/edge."""
import html
def esc(x): return html.escape(x, quote=True)

W, H = 2640, 1400
DY = 96   # băng 3 pha AI-DLC ở trên, sơ đồ dịch xuống
LANE_X0 = 200
PHASES = [("Intent", 200, 830), ("Plan", 830, 1370), ("Execution", 1370, 2130), ("Verify", 2130, 2640)]
LANES = [("BA & APM", "dẫn Intent · phản hồi Showcase", 70, 290, "human"),
         ("Đội AI", "Claude Code (· Codex nếu #14)", 290, 620, "ai"),
         ("Engineer", "dẫn Plan · Execution", 620, 850, "human"),
         ("Backlog", "Nulab · hệ ghi nhận", 850, 1010, "tool"),
         ("Repo · Memory · Tower", "control plane", 1010, 1280, "tool")]
ZONE_TAG = {"human":"NGƯỜI — quyết, phản hồi, ký", "ai":"TỰ ĐỘNG — AI chạy, không chờ người", "tool":"CÔNG CỤ — ghi nhận, không quyết"}
# chỗ NGƯỜI chạm vào bên trong vùng tự động / công cụ
HUMAN = {"n03":"BA trả lời khi rảnh · không chặn", "b1":"người bấm Confirm", "b2":"người bấm Confirm", "b3":"người bấm Confirm",
         "mem":"Lead ký (mốc chờ)", "n02":"người xác nhận kind ở Gate 1", "n07":"người xem thứ tự ở Gate 2",
         "n13":"specialist người chỉ khi trigger", "hof":"người giao nghiệm result_check", "pr":"đội review PR"}
PH3 = [("INCEPTION", 200, 1370, "Vì sao làm, cho ai, đích đo được là gì · xây chính xác gì, cắt ra sao?", "điểm dừng: ◇ CP-01 chờ đích · ◇⏱ thứ tự Unit"),
       ("CONSTRUCTION", 1370, 2130, "Thiết kế, code, kiểm chứng thế nào — Lead đã nhìn nó chạy chưa?", "điểm dừng: ◉ Showcase mỗi unit · Team Agreement · ■ Ranh đỏ"),
       ("OPERATIONS", 2130, 2640, "Đưa lên, quan sát, học được gì để mở intent kế?", "điểm dừng: ■ Gate R · ■ Ranh đỏ deploy · ◇ LL")]


# node: id, kind, x, y, w, h, patch, title, lines   (mỗi dòng ≤ 32 ký tự)
NODES = [
 # ---- Intent
 ("n01","keep",225,95,205,88,[],"01 · Human nói outcome",["/ai-dlc:dlc-intent \"<outcome>\"","không cần viết sẵn spec"]),
 ("n02","change",225,345,230,118,[5],"02 · AI đề xuất kind · intent.md",["đọc memory · knowledge · codekb","+ Source Reading Plan","+ sổ cái nguồn: planned → read","tag nguồn phải trỏ dòng đã đọc"]),
 ("n03","change",480,345,225,118,[4],"03 · Câu hỏi → Sổ giả định",["mỗi giả định 4 trường:","mặc định nếu im lặng · đảo tốn gì","nhìn thấy ở đâu · đã soát nguồn nào","đảo rẻ → đi tiếp · đắt → mốc chờ"]),
 ("g1","gate",480,95,225,100,[],"■ Gate 1 · Intent approval",["đích · AC · ASM đảo đắt","bugfix/refactor: gộp cả Plan","preview toàn văn rồi mới bấm"]),
 ("b1","change",480,880,225,100,[7],"05/06 · Story / child issue",["Preview → Confirm → Publish (giữ)","+ Story mang SHA của intent.md","+ SoT: repo=intent · Backlog=status"]),
 # ---- Plan
 ("n06","keep",865,345,215,88,[],"05/06 · Engineer + AI: plan.md",["pull docs · get story · sources","(giữ nguyên)"]),
 ("n07","change",1105,345,245,118,[9],"07 · Work Unit",["role · owner · dependency · AC","verification · halting (giữ)","+ releasable · session_fit có số","+ areas · cắt DỌC mặc định"]),
 ("g2","wait",1105,660,245,118,[1],"◇⏱ Gate 2 → Mốc chờ có hạn",["Lead quyết: thứ tự Unit +","Unit nào bấm thử trước","im lặng N giờ = theo đề xuất","publish task vẫn cần Confirm"]),
 ("b2","keep",1105,880,245,88,[],"09 · Task theo Work Unit",["Preview → Confirm → Publish","(chỉ feature/infra)"]),
 # ---- Execution
 ("n10","add",1400,345,225,118,[10],"+ Chặng thiết kế trong đội",["Domain/Logical mini + ADR nháp","TRƯỚC commit code đầu","đội tự chốt (Team Agreement)","không gate người"]),
 ("n11","keep",1650,345,215,118,[],"11 · Execution UNIT",["chỉ nạp unit đó, đúng contract","code đi vào sources/<area>","(giữ nguyên)"]),
 ("n11b","change",1890,345,230,118,[6],"Loop verify AC ≤ 3",["verifier CONTEXT TƯƠI, report-only","hook cấm sửa file test khi fix","lần 4 → ESC có chủ, unit CHẶN","không âm thầm sang unit kế"]),
 ("n13","change",1890,495,230,102,[3],"13 · Máy kiểm — TRƯỚC người",["tất định (lint·SAST·hook): mọi unit","agent LLM: chỉ specialist theo trigger","verdict có receipt fingerprint"]),
 ("sc","show",1650,660,225,102,[2],"◉ Showcase SC-NN · mỗi unit",["≤ 10 bước bấm · giả định đang hiện","KHÔNG chặn — Lead FB khi rảnh","FB đổi/làm lại → Bolt sửa"]),
 ("hof","add",1400,1040,225,102,[11],"+ HOF · heartbeat · result_check",["mỗi unit một handoff file","nhịp sống kiểm chéo mtime","người giao nghiệm trước khi dùng"]),
 ("pr","keep",1650,1040,215,88,[],"Commit & PR · đội review",["= tầng peer (giữ)","[TSD-158] trên mọi commit"]),
 ("red","red",1890,1040,230,102,[1],"■ Ranh đỏ — AI dừng thật",["migration phá dữ liệu","contract có consumer ngoài đội","ghi ra ngoài (Backlog = Confirm)"]),
 ("str","add",1400,95,470,88,[12],"+ Bẻ lái STR-NNN · Bản tin ca",["Lead đổi hướng bất cứ lúc nào, không chờ gate","một trang/ngày: đã làm · cần bạn quyết · ranh đỏ"]),
 # ---- Verify
 ("g3","gate",2160,660,240,135,[2],"■ Gate 3 = Gate R · 9 mục",["evidence + LEAD TỰ DÙNG (giữ)","+ ledger ASM còn mở · FB đã đóng","+ rollback · ghi chú cho khách","+ khoảng trống trung thực","+ ai ký mục nào (raci)"]),
 ("n14","change",2160,345,240,102,[10],"14 · Đối chiếu, không viết ngược",["ADR đã có ↔ code (không tạo mới)","promote as-is → codekb + freshness","mark STALE area chạm"]),
 ("mem","change",2160,1040,240,102,[8],"Memory update cần source LL",["diff rule phải trỏ LL-NNN (ca thật)","không LL → knowledge/, không memory/","Lead ký (Mốc chờ)"]),
 ("b3","keep",2160,880,240,88,[],"15/16 · Comment evidence · Close",["Confirm = chữ ký Gate R","(giữ nguyên)"]),
 ("kpi","add",2420,1165,205,102,[13],"+ KPI đo từ máy",["lead.wait_hours · showcase.fb_rate","asm.overridden · units.reviewed","self_fix.exhausted · stop.unjust."]),
]
NM = {n[0]: n for n in NODES}

def side_pt(nid, side, off=0):
    _,_,x,y,w,h,_,_,_ = NM[nid]
    cx, cy = x+w/2, y+h/2
    return {"l":(x, cy+off), "r":(x+w, cy+off), "t":(cx+off, y), "b":(cx+off, y+h)}[side]

# edge: dict(f, fs, fo, t, ts, to, label, kind, wp, lp)
def E(f,fs,t,ts,label="",kind="",fo=0,to=0,wp=None,lp=None):
    return dict(f=f,fs=fs,fo=fo,t=t,ts=ts,to=to,label=label,kind=kind,wp=wp or [],lp=lp)
EDGES = [
 E("n01","b","n02","t","1"),
 E("n02","r","n03","l","2"),
 E("n03","t","g1","b","3"),
 E("g1","r","n06","t","4 · đích đã chốt", fo=-20),
 E("g1","r","b1","r","Story / child", fo=25, wp=[(732,170),(732,930)], lp=(780,540)),
 E("n06","r","n07","l","5"),
 E("n07","b","g2","t","6"),
 E("g2","b","b2","t","confirm task"),
 E("g2","r","n10","l","7 · từng unit / danh sách", wp=[(1385,719),(1385,404)], lp=(1385,560)),
 E("n10","r","n11","l","8"),
 E("n11","r","n11b","l","9"),
 E("n11b","t","n11","t","≤3 · sửa","loop", fo=-45, to=45, wp=[(1960,318),(1802,318)], lp=(1881,318)),
 E("n11b","b","n13","t","10"),
 E("n13","l","n11","b","fix","loop", fo=-25, to=65, wp=[(1822,521)]),
 E("n13","b","sc","r","11 · unit xanh", fo=-40, to=-25, wp=[(1965,686)], lp=(1965,640)),
 E("sc","t","n11","b","FB đổi → Bolt sửa","loop", fo=-60, to=-30, wp=[(1702,560),(1727,560)], lp=(1715,590)),
 E("sc","r","g3","l","12 · mọi FB đóng", fo=25, to=25, lp=(2015,770)),
 E("g3","t","n14","b","13 · release"),
 E("n14","r","mem","r","14", wp=[(2445,396),(2445,1091)], lp=(2445,740)),
 E("g3","b","b3","t","confirm"),
 E("n11","l","pr","l","commit", fo=40, wp=[(1637,444),(1637,1084)], lp=(1637,900)),
 E("pr","b","g3","l","merged", to=55, wp=[(1757,1185),(2140,1185),(2140,782)], lp=(1950,1185)),
 E("n13","b","red","t","chạm → dừng","stop", fo=70, to=60, wp=[(2075,820),(2065,820)], lp=(2075,700)),
 E("str","l","g2","r","đổi thứ tự","steer", to=-35, wp=[(1360,139),(1360,684)], lp=(1360,400)),
 E("str","b","n11","t","đổi hướng","steer", fo=130, to=-60, wp=[(1765,265),(1697,265)], lp=(1731,265)),
 E("hof","t","n10","b","1 HOF / unit","steer"),
]

def draw_edge(e):
    x1,y1 = side_pt(e["f"], e["fs"], e["fo"]); x2,y2 = side_pt(e["t"], e["ts"], e["to"])
    pts = [(x1,y1)] + [tuple(p) for p in e["wp"]]
    if not e["wp"]:
        fs,ts = e["fs"], e["ts"]
        if fs in "lr" and ts in "tb": pts.append((x2,y1))
        elif fs in "tb" and ts in "lr": pts.append((x1,y2))
        elif fs in "lr" and ts in "lr" and abs(y1-y2)>2:
            mx=(x1+x2)/2; pts += [(mx,y1),(mx,y2)]
        elif fs in "tb" and ts in "tb" and abs(x1-x2)>2:
            my=(y1+y2)/2; pts += [(x1,my),(x2,my)]
    pts.append((x2,y2))
    d = "M" + " L".join(f"{px:.0f} {py:.0f}" for px,py in pts)
    cls = {"":"edge","loop":"edge edge-loop","steer":"edge edge-steer","stop":"edge edge-stop"}[e["kind"]]
    mk = {"":"ah","loop":"ah-loop","steer":"ah-steer","stop":"ah-stop"}[e["kind"]]
    o(f'<path d="{d}" class="{cls}" marker-end="url(#{mk})"/>')
    if e["label"]:
        if e["lp"]: mx,my = e["lp"]
        else:
            # đoạn dài nhất
            best=max(range(len(pts)-1), key=lambda i: abs(pts[i+1][0]-pts[i][0])+abs(pts[i+1][1]-pts[i][1]))
            mx=(pts[best][0]+pts[best+1][0])/2; my=(pts[best][1]+pts[best+1][1])/2
        tw = 6.9*len(e["label"])+14
        o(f'<rect x="{mx-tw/2:.0f}" y="{my-10:.0f}" width="{tw:.0f}" height="20" rx="4" class="elabel-bg"/>')
        o(f'<text x="{mx:.0f}" y="{my+4:.0f}" text-anchor="middle" class="elabel">{esc(e["label"])}</text>')

out = []
o = out.append
o(f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Workflow đích của team với 14 miếng vá theo tinh thần AI-DLC v2: hộp giữ nguyên, hộp đổi (hổ phách), hộp thêm (cam), gate người, mốc chờ, showcase và ranh đỏ" xmlns="http://www.w3.org/2000/svg">')
o('<defs>'
  '<marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="currentColor"/></marker>'
  '<marker id="ah-loop" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="f-loop"/></marker>'
  '<marker id="ah-steer" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="f-steer"/></marker>'
  '<marker id="ah-stop" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="f-stop"/></marker>'
  '</defs>')
# ---- băng 3 pha AI-DLC (trên cùng, không dịch)
o(f'<rect x="0" y="0" width="{W}" height="{DY-8}" class="ph3-band"/>')
o(f'<text x="18" y="30" class="lane-sub">AI-DLC · 3 pha</text><text x="18" y="50" class="lane-sub">↓ 4 cột của team</text>')
for name,x0,x1,q,stops in PH3:
    o(f'<rect x="{x0+6}" y="6" width="{x1-x0-12}" height="{DY-20}" rx="8" class="ph3-box"/>')
    o(f'<text x="{x0+18}" y="30" class="ph3-name">{esc(name)}</text>')
    o(f'<text x="{x0+18}" y="52" class="ph3-q">{esc(q)}</text>')
    o(f'<text x="{x0+18}" y="70" class="ph3-stops">{esc(stops)}</text>')
o(f'<g transform="translate(0,{DY})">')
for i,(name,sub,y0,y1,zone) in enumerate(LANES):
    o(f'<rect x="0" y="{y0}" width="{W}" height="{y1-y0}" class="lane zone-{zone}"/>')
    if zone=="ai":
        o(f'<rect x="4" y="{y0+4}" width="{W-8}" height="{y1-y0-8}" rx="10" class="zone-ai-frame"/>')
    o(f'<text x="18" y="{y0+34}" class="lane-name">{esc(name)}</text>')
    o(f'<text x="18" y="{y0+54}" class="lane-sub">{esc(sub)}</text>')
    tag = ZONE_TAG[zone]
    o(f'<rect x="18" y="{y0+66}" width="172" height="18" rx="9" class="ztag ztag-{zone}"/>')
    o(f'<text x="104" y="{y0+79}" text-anchor="middle" class="ztag-t ztag-t-{zone}">{esc(tag.split(" — ")[0])}</text>')
    o(f'<text x="18" y="{y0+104}" class="lane-sub zone-note">{esc(tag.split(" — ")[1])}</text>')
for name,x0,x1 in PHASES:
    o(f'<text x="{(x0+x1)/2}" y="42" text-anchor="middle" class="phase">{esc(name)}</text>')
    o(f'<line x1="{x0}" y1="60" x2="{x0}" y2="{H-DY-20}" class="sep"/>')
o(f'<line x1="0" y1="62" x2="{W}" y2="62" class="sep"/>')
o('<rect x="1385" y="298" width="735" height="500" rx="10" class="frame"/>')
o('<text x="1400" y="790" class="frame-label">khung lặp cho TỪNG unit — một HOF · một worktree · state do tool ghi (#11 · #14)</text>')
for e in EDGES: draw_edge(e)
for nid,kind,x,y,w,h,patch,title,lines in NODES:
    o(f'<g class="node n-{kind}">')
    o(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/>')
    o(f'<text x="{x+12}" y="{y+22}" class="ntitle">{esc(title)}</text>')
    for i,l in enumerate(lines):
        o(f'<text x="{x+12}" y="{y+43+i*16.5:.0f}" class="nline">{esc(l)}</text>')
    for j,p in enumerate(patch):
        cx, cy = x+w-14-j*30, y-2
        o(f'<circle cx="{cx}" cy="{cy}" r="13" class="badge"/><text x="{cx}" y="{cy+4}" text-anchor="middle" class="badge-t">#{p}</text>')
    if nid in HUMAN:
        lab = "✋ " + HUMAN[nid]; tw = 6.6*len(lab)+16
        o(f'<rect x="{x+w-tw-6:.0f}" y="{y+h-9}" width="{tw:.0f}" height="18" rx="9" class="hpill"/>')
        o(f'<text x="{x+w-tw/2-6:.0f}" y="{y+h+4}" text-anchor="middle" class="hpill-t">{esc(lab)}</text>')
    o('</g>')
o('</g>')
o('</svg>')
SVG = "\n".join(out)

PATCHES = [
 (1,"Gate 2 chặn cứng cho quyết định rẻ; quyết định đắt không có chốt","Gate 2 → Mốc chờ có hạn (thứ tự Unit); thêm Ranh đỏ (migration · contract ngoài · ghi ra ngoài)","hình + núm dự án","Gate D INT-003 30 unit/113h · DEC-0052"),
 (2,"Gate 3 nhìn sản phẩm một lần sau mọi unit","Showcase per unit không chặn; Gate 3 giữ vai Gate R nhưng đủ 9 mục","hình","INT-001: 17 unit qua điểm demo không dừng"),
 (3,"Máy kiểm (13) chạy sau người ký (12)","Đảo lên trước; tách máy tất định (chặn) với agent LLM (specialist theo trigger, có receipt)","hình + gói §4.17","LL-002: 13 request / 0 verdict"),
 (4,"Assumption chỉ ghi câu đã trả lời; chưa trả lời thì AI đứng hoặc tự trả lời thầm","ASM 4 trường: mặc định nếu im lặng · đảo tốn gì · nhìn thấy ở đâu · đã soát nguồn nào","gói (ASM)","38 OQ / 5 chặn ở PILOT"),
 (5,"Tag nguồn nhưng không có kế hoạch đọc và bằng chứng đã đọc","Source Reading Plan trước Gate 1 + sổ cái planned→read; sensor tag không resolve ⇒ FAIL","gói (đã có §4.8) + sensor","LL-001: hỏi thứ có sẵn trong nguồn"),
 (6,"“Tự sửa ≤3” không có hậu quả lần 4; verify cùng context; AI sửa được test","Lần 4 → ESC có chủ; verifier context tươi; hook cấm sửa test khi fix; ca đối chứng + mutation","gói (max_self_fix · dlc-verifier · hook)","LL-003: done không evidence"),
 (7,"Confirm không đảm bảo đọc toàn văn; intent.md đổi sau publish không có luật sync","previewed:true trên tower; SoT per artefact; Story mang SHA intent; doctor WARN drift","gói (dlc-backlog) + luật §2.1","approve mù đã bị chặn ở tower 6.x"),
 (8,"“Human accepts memory changes” ngay sau merge = Gate G mù","Diff rule phải trỏ LL-NNN; không LL → knowledge/, không memory/","gói (doctor) + núm","quy ước ‘sửa luật phải từ LL’"),
 (9,"Work Unit thiếu releasable / session_fit; dễ cắt theo tầng","Thêm 2 trường có số + areas; cắt dọc mặc định","gói (6.2.0 đã có areas)","DEC-0052 tách unit để lọt trần"),
 (10,"Không có chặng thiết kế; ADR ‘reconcile’ sau merge = viết ngược","Chặng Domain/Logical + ADR nháp trước code, đội tự chốt; bước 14 chỉ đối chiếu","hình + gói (Bolt)","‘không dựng bù hồ sơ’ · DDD ở lõi"),
 (11,"Không nhìn thấy đội AI giữa Gate 2 và Gate 3","HOF per unit · heartbeat kiểm chéo · result_check của người giao","gói (đã có §9)","HOF-0039 · RV-019/020 tin chết"),
 (12,"Không có Bẻ lái, không có Bản tin ca","STR-NNN mọi lúc · brief một trang mỗi ngày","gói (7.0.0)","v2 §II.2 · §VII.3"),
 (13,"Không có phép đo nào","6 KPI đo từ máy trên tower","gói (tower)","v2 §IX: luật không KPI không vào gói"),
 (14,"Claude + Codex ghi cùng repo không cô lập, state tự khai","Worktree per unit · state do tool ghi (dlc_state.py)","gói (AWS #2 · #8)","‘18 unit approved tự khai’"),
]

rows = "\n".join(
 f'<tr><td class="num">#{n}</td><td>{esc(a)}</td><td>{esc(b)}</td><td><span class="where">{esc(c)}</span></td><td class="ev">{esc(d)}</td></tr>'
 for n,a,b,c,d in PATCHES)

HTML = f'''<title>Bản vá workflow đích</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@500;600&family=IBM+Plex+Sans:ital,wght@0,400;0,500;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root {{
  --bg:#F2F3EF; --bg-2:#E9EBE5; --ink:#1E2622; --ink-2:#4E5A54; --line:#C9CFC8;
  --keep:#7C8A80; --keep-fill:#EDEFEA;
  --change:#B7791F; --change-fill:#FBF1DC;
  --add:#C2410C; --add-fill:#FDE6DA;
  --gate:#8B1E3F; --gate-fill:#F6DEE5;
  --wait:#2F6F8F; --wait-fill:#DCEAF1;
  --show:#2E7D5B; --show-fill:#DDF0E6;
  --red:#A61B1B; --red-fill:#F8DCDC;
  --label-bg:#F2F3EF; --frame:#7C8A80;
  --zh:#F6EEDF; --za:#E2EAF3; --zt:#ECEDE8; --za-line:#3F6E9E; --zh-line:#B08A4A; --zt-line:#9AA39C; --ph3:#E6E9E2;
}}
html, body {{ color-scheme: light; background:var(--bg); color:var(--ink); font-family:"IBM Plex Sans",system-ui,sans-serif; font-size:15px; line-height:1.5; margin:0; }}
.wrap {{ max-width:1380px; margin:0 auto; padding:32px 24px 64px; display:flex; flex-direction:column; gap:28px; }}
h1 {{ font-family:"IBM Plex Sans Condensed","IBM Plex Sans",sans-serif; font-weight:600; font-size:34px; letter-spacing:-.01em; margin:0; text-wrap:balance; }}
h2 {{ font-family:"IBM Plex Sans Condensed","IBM Plex Sans",sans-serif; font-weight:600; font-size:22px; margin:0 0 10px; }}
.eyebrow {{ font-family:"IBM Plex Mono",monospace; font-size:12px; letter-spacing:.08em; text-transform:uppercase; color:var(--ink-2); }}
.lede {{ max-width:70ch; color:var(--ink-2); margin:6px 0 0; }}
.legend {{ display:flex; flex-wrap:wrap; gap:10px 18px; font-size:13px; align-items:center; }}
.sw {{ display:inline-block; width:26px; height:14px; border-radius:3px; vertical-align:-2px; margin-right:6px; border:2px solid; }}
.figwrap {{ border:1px solid var(--line); border-radius:10px; background:var(--bg-2); padding:10px; overflow-x:auto; }}
figure {{ margin:0; }}
figure svg {{ width:2400px; max-width:none; height:auto; display:block; }}
figcaption {{ font-size:13px; color:var(--ink-2); padding:10px 4px 2px; max-width:110ch; }}
@media (min-width:1500px) {{ figure svg {{ width:100%; }} }}
/* SVG */
.lane {{ fill:var(--bg-2); }}
.zone-human {{ fill:var(--zh); }} .zone-ai {{ fill:var(--za); }} .zone-tool {{ fill:var(--zt); }}
.zone-ai-frame {{ fill:none; stroke:var(--za-line); stroke-width:3; }}
.ztag {{ stroke-width:1.5; }} .ztag-human {{ fill:var(--zh); stroke:var(--zh-line); }} .ztag-ai {{ fill:var(--za-line); stroke:var(--za-line); }} .ztag-tool {{ fill:var(--zt); stroke:var(--zt-line); }}
.ztag-t {{ font:600 10.5px "IBM Plex Mono",monospace; letter-spacing:.06em; fill:var(--ink); }} .ztag-t-ai {{ fill:#fff; }}
.zone-note {{ font-size:10.5px; }}
.ph3-band {{ fill:var(--ph3); }} .ph3-box {{ fill:var(--bg); stroke:var(--line); stroke-width:1.5; }}
.ph3-name {{ font:600 15px "IBM Plex Sans Condensed",sans-serif; letter-spacing:.08em; fill:var(--ink); }}
.ph3-q {{ font:italic 12px "IBM Plex Sans",sans-serif; fill:var(--ink); }} .ph3-stops {{ font:11px "IBM Plex Mono",monospace; fill:var(--ink-2); }}
.hpill {{ fill:var(--label-bg); stroke:var(--gate); stroke-width:1.5; }} .hpill-t {{ font:500 10.5px "IBM Plex Sans",sans-serif; fill:var(--gate); }}
.lane-name {{ font:600 15px "IBM Plex Sans Condensed",sans-serif; fill:var(--ink); }}
.lane-sub {{ font:11px "IBM Plex Sans",sans-serif; fill:var(--ink-2); }}
.phase {{ font:600 20px "IBM Plex Sans Condensed",sans-serif; fill:var(--ink); letter-spacing:.04em; text-transform:uppercase; }}
.sep {{ stroke:var(--line); stroke-width:1.5; }}
.frame {{ fill:none; stroke:var(--frame); stroke-width:1.5; stroke-dasharray:6 5; }}
.frame-label {{ font:11px "IBM Plex Mono",monospace; fill:var(--ink-2); }}
.node rect {{ fill:var(--keep-fill); stroke:var(--keep); stroke-width:1.5; }}
.node .ntitle {{ font:600 13px "IBM Plex Sans",sans-serif; fill:var(--ink); }}
.node .nline {{ font:11.5px "IBM Plex Sans",sans-serif; fill:var(--ink-2); }}
.n-change rect {{ fill:var(--change-fill); stroke:var(--change); stroke-width:3; stroke-dasharray:8 4; }}
.n-add rect {{ fill:var(--add-fill); stroke:var(--add); stroke-width:3; }}
.n-gate rect {{ fill:var(--gate-fill); stroke:var(--gate); stroke-width:3; }}
.n-wait rect {{ fill:var(--wait-fill); stroke:var(--wait); stroke-width:3; stroke-dasharray:8 4; }}
.n-show rect {{ fill:var(--show-fill); stroke:var(--show); stroke-width:3; }}
.n-red rect {{ fill:var(--red-fill); stroke:var(--red); stroke-width:3; }}
.n-change .ntitle {{ fill:var(--change); }} .n-add .ntitle {{ fill:var(--add); }} .n-gate .ntitle {{ fill:var(--gate); }}
.n-wait .ntitle {{ fill:var(--wait); }} .n-show .ntitle {{ fill:var(--show); }} .n-red .ntitle {{ fill:var(--red); }}
.n-change .nline, .n-add .nline, .n-gate .nline, .n-wait .nline, .n-show .nline, .n-red .nline {{ fill:var(--ink); }}
.badge {{ fill:var(--add); stroke:var(--bg); stroke-width:2; }} .n-change .badge {{ fill:var(--change); }}
.n-wait .badge, .n-red .badge {{ fill:var(--add); }} .n-show .badge, .n-gate .badge {{ fill:var(--add); }}
.badge-t {{ font:600 11px "IBM Plex Mono",monospace; fill:#fff; }}
.edge {{ fill:none; stroke:currentColor; stroke-width:2; color:var(--ink); }}
.edge-loop {{ color:var(--change); stroke-dasharray:5 4; }} .f-loop {{ fill:var(--change); }}
.edge-steer {{ color:var(--wait); stroke-dasharray:2 4; }} .f-steer {{ fill:var(--wait); }}
.edge-stop {{ color:var(--red); stroke-dasharray:3 3; }} .f-stop {{ fill:var(--red); }}
.elabel-bg {{ fill:var(--label-bg); stroke:var(--line); stroke-width:1; }}
.elabel {{ font:11px "IBM Plex Mono",monospace; fill:var(--ink); }}
/* table */
table {{ border-collapse:collapse; width:100%; font-size:13.5px; }}
th {{ text-align:left; font-family:"IBM Plex Mono",monospace; font-size:11px; letter-spacing:.06em; text-transform:uppercase; color:var(--ink-2); padding:8px 10px; border-bottom:1.5px solid var(--line); }}
td {{ padding:10px; border-bottom:1px solid var(--line); vertical-align:top; }}
td.num {{ font-family:"IBM Plex Mono",monospace; font-weight:500; color:var(--add); white-space:nowrap; }}
td.ev {{ color:var(--ink-2); font-size:12.5px; }}
.where {{ font-family:"IBM Plex Mono",monospace; font-size:11.5px; background:var(--bg-2); border:1px solid var(--line); border-radius:4px; padding:2px 6px; white-space:nowrap; }}
.cols {{ display:grid; grid-template-columns:1fr 1fr; gap:24px; }}
@media (max-width:900px) {{ .cols {{ grid-template-columns:1fr; }} }}
.card {{ border:1px solid var(--line); border-radius:10px; padding:16px 18px; background:var(--bg-2); }}
.card ul {{ margin:6px 0 0; padding-left:18px; }} .card li {{ margin:4px 0; }}
.mono {{ font-family:"IBM Plex Mono",monospace; font-size:12.5px; }}
.tblwrap {{ overflow-x:auto; }}
</style>
<div class="wrap">
  <header>
    <div class="eyebrow">ai-dlc · draft v0.2 · 2026-08-27 · chưa qua team</div>
    <h1>Workflow đích của team — bản vá theo tinh thần AI-DLC v2</h1>
    <p class="lede">Giữ đúng 4 pha, 5 lane và 3 gate của hình gốc (<span class="mono">team-aidlc-workflow-viewer.html</span>). Hộp xám là của team, giữ nguyên. Hộp <b>hổ phách nét đứt</b> là hộp gốc bị đổi luật; hộp <b>cam</b> là thêm mới. Số <span class="mono">#N</span> trỏ tới 14 điểm lủng ở bảng dưới. Ba màu nền lane là ba <b>vùng</b>: người (sand) · tự động (xanh, viền đậm — AI chạy liền mạch, không chờ) · công cụ (xám — chỉ ghi nhận). Nhãn ✋ đánh dấu chỗ người vẫn phải chạm vào bên trong vùng tự động hay công cụ. Băng trên cùng khoanh 4 cột của team vào 3 pha AI-DLC, mỗi pha một câu hỏi và loại điểm dừng. Nguyên tắc vá: hàm mất mát của người đặt ở chỗ đảo ngược đắt, mọi thứ khác AI tự chốt có địa chỉ, luật nào cũng phải có trường để điền và KPI để soi.</p>
  </header>

  <div class="legend">
    <span><i class="sw" style="background:var(--keep-fill);border-color:var(--keep)"></i>giữ nguyên</span>
    <span><i class="sw" style="background:var(--change-fill);border-color:var(--change);border-style:dashed"></i>đổi luật</span>
    <span><i class="sw" style="background:var(--add-fill);border-color:var(--add)"></i>thêm mới</span>
    <span><i class="sw" style="background:var(--gate-fill);border-color:var(--gate)"></i>■ gate người — flow đứng thật</span>
    <span><i class="sw" style="background:var(--wait-fill);border-color:var(--wait);border-style:dashed"></i>◇⏱ mốc chờ có hạn</span>
    <span><i class="sw" style="background:var(--show-fill);border-color:var(--show)"></i>◉ showcase — không chặn</span>
    <span><i class="sw" style="background:var(--red-fill);border-color:var(--red)"></i>■ ranh đỏ — AI tự dừng</span>
    <span style="margin-left:8px"><i class="sw" style="background:var(--zh);border-color:var(--zh-line)"></i>vùng NGƯỜI</span>
    <span><i class="sw" style="background:var(--za);border-color:var(--za-line)"></i>vùng TỰ ĐỘNG (AI)</span>
    <span><i class="sw" style="background:var(--zt);border-color:var(--zt-line)"></i>vùng CÔNG CỤ</span>
    <span><i class="sw" style="background:var(--label-bg);border-color:var(--gate);border-radius:9px"></i>✋ người chạm vào khâu tự động/công cụ</span>
    <span class="mono" style="color:var(--change)">- - -</span><span>vòng sửa</span>
    <span class="mono" style="color:var(--wait)">· · ·</span><span>bẻ lái / handoff</span>
  </div>

  <div class="figwrap">
  <figure>
  {SVG}
  <figcaption>Đọc theo chiều dọc: mọi thứ trong vùng xanh chạy tự động và chỉ dừng ở ranh đỏ; vùng sand là nơi người quyết (2 gate, 1 mốc chờ, Showcase); vùng xám không quyết gì, chỉ ghi nhận sau khi người Confirm. Đọc theo chiều ngang: Inception gồm cả Intent lẫn Plan của team, Construction là Execution, Operations là Verify. Ba gate người của team vẫn ở đúng chỗ, nhưng chỉ Gate 1 và Gate 3 còn là chốt chặn; Gate 2 thành mốc chờ có hạn. Mỗi unit trong khung Execution có thêm một chặng thiết kế trước code, một verifier context tươi, máy kiểm đứng trước người, và một Showcase không chặn — nên Lead nhìn thấy sản phẩm từ unit đầu tiên thay vì ở Gate 3. Ranh đỏ là nơi duy nhất ngoài Gate mà AI dừng thật.</figcaption>
  </figure>
  </div>

  <div class="cols">
    <div class="card">
      <h2>Đổi gì so với hình gốc — đọc trong 1 phút</h2>
      <ul>
        <li><b>Gate 2</b> từ chặn cứng → mốc chờ có hạn; Lead chỉ quyết <i>thứ tự</i> và <i>unit nào bấm thử trước</i>. Publish task vẫn phải Confirm.</li>
        <li><b>Bước 13</b> (máy kiểm) đảo lên <i>trước</i> Gate 3; tách máy tất định (chặn) với agent LLM (specialist theo trigger).</li>
        <li><b>Gate 3</b> giữ nguyên vai chốt chặn cuối, nhưng thành Gate R đủ 9 mục — có mục “Lead tự dùng”, ledger giả định, rollback.</li>
        <li>Thêm 6 hộp: chặng thiết kế trong đội · Showcase mỗi unit · HOF/nhịp sống · Bẻ lái + Bản tin ca · Ranh đỏ · KPI.</li>
        <li>Đổi luật 7 hộp: ASM thay [ans:A1] · Source Reading Plan + sổ cái · Work Unit có releasable/session_fit/areas · verify ≤3 có hậu quả · Story mang SHA · bước 14 đối chiếu không viết ngược · memory update cần LL.</li>
      </ul>
    </div>
    <div class="card">
      <h2>Cái không vá — trông như lủng nhưng đúng tinh thần</h2>
      <ul>
        <li>Bỏ gate AS-IS và gate câu hỏi — v2 cũng bỏ.</li>
        <li>PR review của đội thay reviewer agent — đúng LL-002.</li>
        <li>Bugfix/refactor gộp Intent + Plan một gate — đúng <span class="mono">intent.kind</span>.</li>
        <li>Preview → Confirm → Publish cho Backlog — chính là ranh đỏ “ghi ra ngoài đội” đã có hình.</li>
        <li>Ba gate thay bảy — đúng hướng; chỉ một trong ba (Gate 2) đổi từ chặn sang chờ.</li>
      </ul>
      <p style="margin:12px 0 0;color:var(--ink-2)">Điểm kém chắc nhất: <b>#1</b>. Nếu team cần Gate 2 chặn vì đó là lúc tạo task Backlog, tách hai luật: thứ tự unit = mốc chờ, publish task = confirm.</p>
    </div>
  </div>

  <section>
    <h2>14 điểm lủng và miếng vá</h2>
    <div class="tblwrap">
    <table>
      <thead><tr><th>#</th><th>Điểm lủng trong hình gốc</th><th>Miếng vá</th><th>Vá ở đâu</th><th>Ca thật / căn cứ</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    </div>
  </section>
</div>
'''
open('/private/tmp/claude-502/-Users-nals-macbook-250-company-research-rd-ai-dlc/c2549021-0e10-4c1b-a00c-00765e82b950/scratchpad/workflow-patch-draft.html','w',encoding='utf-8').write(HTML)
print("ok", len(HTML))
