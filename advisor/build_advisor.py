# -*- coding: utf-8 -*-
"""Build the self-contained Prompt 优化建议系统 page from the knowledge base.

Why: the advice system's single source of truth is ``knowledge_base.json``. This
script validates it and inlines it into a themed, self-contained ``advisor.html``
that runs with no server, no build step and no runtime LLM — open it directly or
host it statically. The same JSON later feeds the phase-2 grounded LLM RAG.

v1 ships a conversational (chat) UI driven by a deterministic state machine: the
assistant asks the guided questions one per turn, the user clicks chips or types,
and answers map through the trigger DSL ({q,eq}/{q,in}/{any}/{all}) to layered
advice. The DSL is mirrored in ``test_advisor.py`` for golden-scenario tests.

An "LLM 模式" is stubbed off in this build; phase 2 swaps the response engine to a
grounded OpenRouter call behind a small backend proxy (key stays server-side).

Usage:  python advisor/build_advisor.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
KB_PATH = os.path.join(HERE, "knowledge_base.json")
OUT_PATH = os.path.join(HERE, "advisor.html")

REQUIRED_INSIGHT_FIELDS = [
    "id", "group", "title", "hook", "evidence_level",
    "triggers", "diagnosis", "steps", "evidence", "boundary", "sources",
]
VALID_LEVELS = {"A", "B", "C", "D", "recent-preprint"}


def load_kb():
    with open(KB_PATH, encoding="utf-8") as f:
        return json.load(f)


def _flatten_conds(conds):
    """Yield leaf {q,...} conditions from a list of trigger condition objects."""
    out = []
    for c in conds:
        if "any" in c:
            out += _flatten_conds(c["any"])
        elif "all" in c:
            out += _flatten_conds(c["all"])
        elif "q" in c:
            out.append(c)
    return out


def validate(kb):
    """Light structural validation; deeper checks live in test_advisor.py."""
    errors = []
    if not kb.get("insights"):
        errors.append("knowledge_base.json 缺少 insights")
    qids = {q["id"] for q in kb.get("questions", [])}
    opt_ids = {q["id"]: {o["id"] for o in q["options"]} for q in kb.get("questions", [])}
    for ins in kb.get("insights", []):
        iid = ins.get("id", "<no-id>")
        for field in REQUIRED_INSIGHT_FIELDS:
            if field not in ins or ins[field] in (None, "", []):
                errors.append(f"{iid} 缺少必填字段: {field}")
        if ins.get("evidence_level") not in VALID_LEVELS:
            errors.append(f"{iid} 证据等级非法: {ins.get('evidence_level')}")
        for ev in ins.get("evidence", []):
            if ev.get("level") not in VALID_LEVELS:
                errors.append(f"{iid} evidence.level 非法: {ev.get('level')}")
        for cond in _flatten_conds(ins.get("triggers", [])):
            q = cond.get("q")
            if q not in qids:
                errors.append(f"{iid} 触发条件引用未知问题: {q}")
                continue
            vals = [cond["eq"]] if "eq" in cond else cond.get("in", [])
            for v in vals:
                if v not in opt_ids.get(q, set()):
                    errors.append(f"{iid} 触发条件 {q} 引用未知选项: {v}")
    if errors:
        raise SystemExit("知识库校验失败:\n  - " + "\n  - ".join(errors))


def build():
    kb = load_kb()
    validate(kb)
    kb_json = json.dumps(kb, ensure_ascii=False)
    html = TEMPLATE.replace("/*__KB__*/", kb_json).replace("__UPDATED__", kb["meta"]["updated"])
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"已生成 {OUT_PATH}（对话式 UI · {len(kb['insights'])} 条洞见 · {len(kb['questions'])} 个引导问题）")


TEMPLATE = r"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Prompt 优化建议助手 · 对话式 v1</title>
<style>
/* ---- 视觉语言：学术期刊 / 研究档案（与 scripts/build_doc_html.py 文档页同一套）——
        暖纸面 + 墨色 + 茶青主色 + 朱砂印章点缀；宋体衬线标题、黑体正文、等宽编号；
        全部系统字体 + 内联 SVG 纹理，无外部依赖，file:// 离线可用。 ---- */
:root{
  --bg:#edeadd;--paper:#fbfaf3;--card:#fffefa;--ink:#232820;--muted:#6e7263;--faint:#999d8b;
  --line:#d9d5c1;--line-soft:#e7e4d4;--soft:#f3f1e4;
  --teal:#176a5e;--teal-deep:#0d4c43;--teal-soft:#e4efe9;
  --seal:#b23f2e;--seal-soft:#f8ece6;
  --blue:#2d5fa8;--amber:#94660f;--rose:#a84055;--violet:#5e54a8;--green:#4a742f;--slate:#4d5246;
  --serif:"Source Han Serif SC","Noto Serif SC","Songti SC","STSong",Georgia,"SimSun",serif;
  --sans:"Source Han Sans SC","Noto Sans SC","PingFang SC","Microsoft YaHei","Segoe UI",sans-serif;
  --mono:"Cascadia Code","JetBrains Mono",Consolas,"Courier New",monospace;
  --shadow:0 1px 2px rgba(35,40,32,.05),0 18px 40px -26px rgba(35,40,32,.35);--radius:12px;
}
*{box-sizing:border-box;} html{scroll-behavior:smooth;}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:15.5px;line-height:1.7;}
body::before{content:"";position:fixed;inset:0;z-index:0;pointer-events:none;opacity:.55;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 0.14 0 0 0 0 0.15 0 0 0 0 0.12 0 0 0 0.05 0'/%3E%3C/filter%3E%3Crect width='180' height='180' filter='url(%23n)'/%3E%3C/svg%3E");}
a{color:var(--teal-deep);text-underline-offset:3px;text-decoration-thickness:1px;}
a:hover{color:var(--seal);}
.page{position:relative;z-index:1;max-width:1480px;margin:0 auto;padding:16px 16px 20px;}
.app{background:var(--paper);border:1px solid var(--line);border-radius:var(--radius);
  box-shadow:var(--shadow);overflow:hidden;display:flex;flex-direction:column;height:100%;min-height:0;}

/* ---- 三栏控制台外壳 ---- */
.topbar{display:flex;align-items:center;gap:13px;flex-wrap:wrap;padding:11px 16px;background:var(--card);
  border:1px solid var(--line);border-bottom:3px double var(--line);border-radius:var(--radius);
  box-shadow:var(--shadow);margin-bottom:13px;}
.topbar .dot{width:38px;height:38px;border-radius:7px;background:var(--seal);color:#fff;display:flex;
  align-items:center;justify-content:center;font-family:var(--serif);font-weight:700;font-size:19px;flex:none;
  transform:rotate(-2deg);box-shadow:inset 0 0 0 2px var(--seal),inset 0 0 0 3.5px rgba(255,253,245,.55);}
.ttl h1{margin:0;font-family:var(--serif);font-size:18px;font-weight:700;letter-spacing:.01em;}
.ttl .sub{margin:1px 0 0;color:var(--muted);font-size:12px;letter-spacing:.03em;}
.toggle{display:none;align-items:center;gap:5px;font-size:13px;padding:6px 12px;border:1px solid var(--line);
  border-radius:7px;background:var(--paper);color:var(--slate);cursor:pointer;font-family:var(--sans);transition:.15s;}
.toggle:hover{border-color:var(--teal);color:var(--teal-deep);background:var(--teal-soft);}
.shell{display:grid;grid-template-columns:266px minmax(0,1fr) 322px;gap:13px;height:calc(100vh - 98px);min-height:520px;}
.side{background:var(--paper);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);
  overflow-y:auto;padding:14px;}
.side::-webkit-scrollbar,.msgs::-webkit-scrollbar{width:10px;}
.side::-webkit-scrollbar-thumb,.msgs::-webkit-scrollbar-thumb{background:var(--line);
  border:3px solid var(--paper);border-radius:99px;}
.side::-webkit-scrollbar-track,.msgs::-webkit-scrollbar-track{background:transparent;}
.pan-h{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;
  color:var(--muted);margin:16px 0 8px;padding-bottom:6px;border-bottom:1px solid var(--line);}
.side .pan-h:first-child{margin-top:2px;}
.pan-p{font-size:12.8px;color:#474d3f;margin:0 0 8px;}
.reslink{display:block;font-size:13px;padding:7px 10px;border:1px solid var(--line-soft);border-radius:7px;
  margin-bottom:6px;background:var(--card);text-decoration:none;color:var(--teal-deep);transition:.14s;}
.reslink:hover{border-color:var(--teal);background:var(--teal-soft);color:var(--teal-deep);}
.nav-group{font-size:11.5px;color:var(--slate);font-weight:700;margin:10px 0 4px;}
.navitem{display:block;width:100%;text-align:left;font-size:12.8px;padding:6px 8px;border:1px solid transparent;
  border-radius:7px;background:none;cursor:pointer;color:var(--ink);line-height:1.45;font-family:var(--sans);transition:.12s;}
.navitem:hover{background:var(--soft);border-color:var(--line);}
.navitem:focus-visible,.toggle:focus-visible,.btn-restart:focus-visible{outline:2px solid var(--teal);outline-offset:1px;}
.navitem .lvl{margin-right:5px;}
.scrim{display:none;position:fixed;inset:0;background:rgba(30,33,26,.35);backdrop-filter:blur(2px);z-index:40;}
@media(max-width:1180px){
  .shell{grid-template-columns:266px minmax(0,1fr);}
  .side.right{position:fixed;top:0;right:0;height:100vh;width:344px;max-width:88vw;z-index:50;border-radius:0;
    transform:translateX(100%);transition:transform .22s;}
  body.dr-right .side.right{transform:none;}
  body.dr-right .scrim,body.dr-left .scrim{display:block;}
  .toggle.right{display:inline-flex;}
}
@media(max-width:860px){
  .shell{grid-template-columns:minmax(0,1fr);height:calc(100vh - 136px);}
  .side.left{position:fixed;top:0;left:0;height:100vh;width:300px;max-width:86vw;z-index:50;border-radius:0;
    transform:translateX(-100%);transition:transform .22s;}
  body.dr-left .side.left{transform:none;}
  .toggle.left{display:inline-flex;}
}
.pill{margin-left:auto;font-family:var(--mono);font-size:10.5px;font-weight:600;letter-spacing:.08em;
  padding:5px 11px;border-radius:4px;border:1px solid var(--line);background:var(--soft);color:var(--slate);}
.pill b{color:var(--amber);}
.btn-restart{font-size:12px;padding:6px 13px;border:1px solid var(--line);border-radius:7px;
  background:transparent;color:var(--muted);cursor:pointer;font-family:var(--sans);transition:.15s;}
.btn-restart:hover{border-color:var(--seal);color:var(--seal);}

.msgs{flex:1;overflow-y:auto;padding:21px 20px;display:flex;flex-direction:column;gap:15px;
  background:linear-gradient(180deg,#f4f2e6,#efedde);}
.row{display:flex;gap:10px;align-items:flex-end;max-width:100%;
  animation:rise .32s cubic-bezier(.21,.68,.32,1) both;}
.row.me{flex-direction:row-reverse;align-self:flex-end;}
@keyframes rise{from{opacity:0;transform:translateY(9px);}to{opacity:1;transform:none;}}
.av{width:30px;height:30px;border-radius:6px;flex:none;display:flex;align-items:center;justify-content:center;
  font-family:var(--serif);font-size:14px;font-weight:700;color:#fff;}
.av.bot{background:var(--seal);transform:rotate(-2deg);
  box-shadow:inset 0 0 0 1.5px var(--seal),inset 0 0 0 2.5px rgba(255,253,245,.5);}
.av.me{background:var(--slate);}
.msg{padding:12px 16px;border-radius:12px;max-width:78%;font-size:14.6px;}
.msg.bot{background:var(--card);border:1px solid var(--line);border-bottom-left-radius:3px;
  box-shadow:0 2px 10px -5px rgba(35,40,32,.18);}
.msg.me{background:var(--teal-deep);color:#f2f5ee;border-bottom-right-radius:3px;font-weight:500;
  box-shadow:0 2px 10px -5px rgba(13,76,67,.5);}
.msg.wide{max-width:100%;}
.msg .qh{color:var(--muted);font-size:12.5px;margin-top:5px;}
.typing{display:inline-flex;gap:5px;padding:5px 2px;}
.typing i{width:7px;height:7px;border-radius:50%;background:var(--teal);opacity:.4;animation:bl 1s infinite;}
.typing i:nth-child(2){animation-delay:.2s;} .typing i:nth-child(3){animation-delay:.4s;}
@keyframes bl{0%,80%,100%{opacity:.25;transform:translateY(0);}40%{opacity:.9;transform:translateY(-3px);}}

.chips{display:flex;flex-wrap:wrap;gap:8px;padding:12px 20px;border-top:1px solid var(--line-soft);background:var(--card);}
.chip{cursor:pointer;user-select:none;padding:7px 15px;border:1px solid var(--line);border-radius:999px;
  background:var(--paper);font-size:13.5px;color:#3e4336;transition:all .16s ease;}
.chip:hover{border-color:var(--teal);color:var(--teal-deep);background:var(--teal-soft);
  transform:translateY(-1px);box-shadow:0 4px 10px -6px rgba(23,106,94,.55);}
.chip.go{background:var(--teal);border-color:var(--teal);color:#fff;font-weight:600;}
.chip.go:hover{background:var(--teal-deep);border-color:var(--teal-deep);color:#fff;}
.chip.ghost{background:transparent;border-style:dashed;color:var(--muted);}
.chip.ghost:hover{box-shadow:none;transform:none;}
.composer{display:flex;gap:10px;padding:13px 20px 15px;border-top:1px solid var(--line);background:var(--card);}
.composer input{flex:1;padding:11px 15px;border:1px solid var(--line);border-radius:9px;font-size:14px;
  font-family:var(--sans);background:var(--paper);color:var(--ink);transition:border-color .15s,box-shadow .15s;}
.composer input::placeholder{color:var(--faint);}
.composer input:focus{outline:none;border-color:var(--teal);box-shadow:0 0 0 3px rgba(23,106,94,.14);}
.composer button{border:0;border-radius:9px;padding:0 22px;font-size:14px;font-weight:600;font-family:var(--sans);
  background:var(--teal);color:#fff;cursor:pointer;transition:background .15s;}
.composer button:hover{background:var(--teal-deep);}

/* ---- advice rich content (聊天宽气泡与右侧详情面板共用) ---- */
.banner{padding:10px 14px;border-left:3px solid var(--amber);background:#faf3e0;border-radius:0 8px 8px 0;
  font-size:12.5px;color:#5c4c22;margin-bottom:13px;}
.banner b{color:#7a5f14;}
.summary{padding:14px 17px;border-radius:0 10px 10px 0;border-left:3px solid var(--teal);background:var(--teal-soft);margin-bottom:14px;}
.summary h3{margin:0 0 8px;font-family:var(--serif);font-size:16px;}
.summary ul{margin:6px 0 0;padding-left:18px;}
.flag{padding:10px 14px;border-left:3px solid var(--rose);background:#f9ecef;border-radius:0 8px 8px 0;
  margin-bottom:9px;color:#7c2e40;font-weight:600;font-size:13.5px;}
.flag.ok{border-left-color:var(--green);background:#eef3e4;color:#3a5520;}
.group-label{display:block;margin:20px 0 11px;padding:0 0 7px;border-bottom:1px solid var(--line);
  font-family:var(--mono);font-size:10.5px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);}
.card{border:1px solid var(--line);border-radius:10px;background:var(--card);position:relative;overflow:hidden;
  padding:16px 18px 14px;margin-bottom:13px;box-shadow:0 1px 4px -2px rgba(35,40,32,.12);}
.card::before{content:"";position:absolute;top:0;left:0;bottom:0;width:3px;background:var(--teal);}
.card.A::before{background:var(--teal);} .card.B::before{background:var(--amber);}
.card.C::before{background:var(--rose);} .card.D::before{background:var(--violet);}
.card.E::before{background:var(--green);} .card.F::before{background:var(--slate);}
.card .cid{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-bottom:7px;}
.card .cid b{font-family:var(--mono);font-size:10.5px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--faint);}
.lvl{display:inline-flex;align-items:center;padding:1.5px 8px;border-radius:3px;
  font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.1em;
  border:1px solid var(--line);background:var(--soft);color:#565b4c;}
.lvl.A{background:#e6f1ea;border-color:#bcd7c8;color:#175e4b;}
.lvl.B{background:#e9effa;border-color:#bccbe8;color:#23508f;}
.lvl.pre{background:var(--seal-soft);border-color:#e2bdaf;color:#a03c28;}
.card h3{margin:0 0 6px;font-family:var(--serif);font-size:17px;line-height:1.45;}
.hook{color:#3a4034;font-weight:600;margin:0 0 11px;font-size:13.6px;}
.layer{margin-top:11px;}
.layer h4{margin:0 0 5px;font-family:var(--mono);font-size:10px;letter-spacing:.16em;color:var(--faint);font-weight:700;}
.layer ul{margin:4px 0 0;padding-left:18px;} .layer li{margin-bottom:3px;}
.ev{display:flex;flex-wrap:wrap;gap:9px;}
.ev .n{flex:1;min-width:190px;padding:9px 12px;border:1px solid var(--line-soft);border-radius:7px;background:var(--paper);}
.ev .n b{display:block;font-family:var(--mono);font-size:16.5px;font-weight:700;color:var(--teal-deep);font-variant-numeric:tabular-nums;}
.ev .n small{display:block;color:var(--muted);font-size:12px;margin-top:2px;line-height:1.55;}
.ev .n a{font-size:11.5px;}
.bound{margin-top:10px;padding:8px 12px;border-left:3px solid var(--amber);background:#faf3e0;border-radius:0 6px 6px 0;font-size:12.5px;color:#5c4c22;}
.corr{margin-top:7px;font-size:12px;color:var(--muted);}
.at-table{width:100%;border-collapse:collapse;border:1px solid var(--line);font-size:12.8px;background:var(--card);}
.at-table th,.at-table td{padding:9px 12px;border-bottom:1px solid var(--line-soft);text-align:left;vertical-align:top;}
.at-table th{background:var(--soft);font-family:var(--mono);font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--slate);}
.at-table tr:last-child td{border-bottom:0;}
.exp{padding:10px 13px;border:1px solid var(--line-soft);border-radius:8px;background:var(--paper);margin-bottom:8px;font-size:12.8px;}
.exp b{color:var(--teal-deep);font-family:var(--mono);}
.llm-ans{font-size:14.4px;line-height:1.82;}
.llm-ans b{font-family:var(--mono);font-weight:600;font-size:.86em;color:#175e4b;background:#e6f1ea;
  border:1px solid #bcd7c8;border-radius:4px;padding:0 5px;margin:0 1px;}
.cursor{display:inline-block;width:7px;height:15px;background:var(--teal);margin-left:2px;vertical-align:text-bottom;animation:blink 1s steps(2,start) infinite;}
@keyframes blink{50%{opacity:0;}}
.refs{margin-top:12px;border-top:1px dashed var(--line);padding-top:9px;}
.refs .group-label{margin:0 0 4px;border-bottom:0;padding-bottom:0;}
.refs ul{margin:6px 0 0;padding-left:18px;font-size:12.6px;} .refs li{margin-bottom:3px;}
@media(max-width:680px){.page{padding:8px 8px 12px;}.msg{max-width:88%;}.ttl h1{font-size:16.5px;}}
</style>
</head>
<body>
<div class="page">
  <header class="topbar">
    <div class="dot">优</div>
    <div class="ttl">
      <h1>Prompt 优化建议助手</h1>
      <p class="sub">扎根证据分级知识库 · 回答可追溯到出处 · 知识库更新 __UPDATED__</p>
    </div>
    <span class="pill" id="llmpill">LLM 模式：<b>未接入</b>（当前确定性）</span>
    <button class="toggle left" id="tgLeft">📚 知识库</button>
    <button class="toggle right" id="tgRight">📄 详情</button>
    <button class="btn-restart" id="restart">重新开始</button>
  </header>
  <div class="shell">
    <aside class="side left" id="leftPanel"></aside>
    <main class="app">
      <div class="msgs" id="msgs"></div>
      <div class="chips" id="chips"></div>
      <div class="composer">
        <input id="box" placeholder="直接打字提问（如：多个 agent 出错怎么定位？）" autocomplete="off">
        <button id="send">发送</button>
      </div>
    </main>
    <aside class="side right" id="rightPanel"></aside>
  </div>
  <div class="scrim" id="scrim"></div>
</div>

<script id="kb" type="application/json">/*__KB__*/</script>
<script>
const KB = JSON.parse(document.getElementById('kb').textContent);
const Q = KB.questions;
const state = { step: 0, answers: {}, phase: 'asking' };
const LLM = { available: false, model: '' };   // 由 api/health 探测填充
let llmHistory = [];                            // LLM 模式多轮上下文

// ---------- 触发 DSL（与 test_advisor.py 同口径）----------
function evalCond(c, a){
  if (c.any) return c.any.some(x => evalCond(x, a));
  if (c.all) return c.all.every(x => evalCond(x, a));
  if (c.q == null) return false;
  const v = a[c.q];
  if (v == null) return false;
  if ('eq' in c) return v === c.eq;
  if ('in' in c) return c.in.includes(v);
  return false;
}
function matched(ins, a){ return (ins.triggers||[]).some(t => evalCond(t, a)); }

// ---------- DOM 辅助 ----------
const msgs = document.getElementById('msgs');
const chipsEl = document.getElementById('chips');
function esc(s){ return String(s).replace(/[&<>]/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[m])); }
function scroll(){ msgs.scrollTop = msgs.scrollHeight; }

function bubble(who, html, wide){
  const row = document.createElement('div');
  row.className = 'row ' + (who === 'me' ? 'me' : 'bot');
  const av = `<div class="av ${who}">${who === 'me' ? '你' : '优'}</div>`;
  row.innerHTML = av + `<div class="msg ${who} ${wide?'wide':''}">${html}</div>`;
  msgs.appendChild(row); scroll();
  return row;
}
function botSay(html, wide){ return bubble('bot', html, wide); }
function meSay(text){ return bubble('me', esc(text)); }

function renderChips(items){
  chipsEl.innerHTML = '';
  items.forEach(it => {
    const c = document.createElement('span');
    c.className = 'chip ' + (it.cls || '');
    c.textContent = it.label;
    c.onclick = it.onClick;
    chipsEl.appendChild(c);
  });
}

// ---------- 渲染建议（与表单版同口径，装进一个宽气泡）----------
function lvlTag(lv){ const cls = lv === 'A' ? 'A' : lv === 'B' ? 'B' : 'pre'; return `<span class="lvl ${cls}">${lv}</span>`; }
function repoLink(p){ return '../' + p; }
function card(ins){
  const ev = (ins.evidence||[]).map(e =>
    `<div class="n"><b>${e.num}</b><small>${e.note}</small>${
      e.source ? `<a href="${repoLink(e.source)}">${e.source.split('/').pop()} ${lvlTag(e.level)}</a>` : lvlTag(e.level)
    }</div>`).join('');
  const steps = (ins.steps||[]).map(s => `<li>${s}</li>`).join('');
  const src = (ins.sources||[]).map(s => `<a href="${repoLink(s)}">${s.split('/').pop()}</a>`).join(' · ');
  return `<div class="card ${ins.group}">
    <div class="cid"><b>${ins.id} · 洞见</b>${lvlTag(ins.evidence_level)}${ins.spine?'<span class="lvl">通用纪律</span>':''}</div>
    <h3>${ins.title}</h3><p class="hook">${ins.hook}</p>
    <div class="layer"><h4>① 快速诊断</h4><div>${ins.diagnosis}</div></div>
    <div class="layer"><h4>② 可照抄步骤</h4><ul>${steps}</ul></div>
    <div class="layer"><h4>③ 真实证据（该论文设置下成立）</h4><div class="ev">${ev}</div></div>
    <div class="bound"><b>边界：</b>${ins.boundary}</div>
    ${ins.cross_channel?`<div class="corr"><b>跨渠道互证：</b>${ins.cross_channel}</div>`:''}
    <div class="corr">出处：${src}</div></div>`;
}
function topFlags(a){
  const f = [];
  if (a.has_evalset === 'no') f.push({cls:'', t:'你还没有评测集。这是第一道闸：没有它，你看到的「涨分」很可能只是噪声——先建一个能客观打分的留出集，再谈优化。'});
  if (a.tried_autopolish === 'planning_to') f.push({cls:'', t:'你打算直接让模型「优化一下 prompt」。这正是最危险的起点——先做优化前体检（洞见 01），别把润色当优化。'});
  if (a.tried_autopolish === 'got_worse') f.push({cls:'', t:'优化后反而更差，几乎是教科书现象：很可能在小样本噪声上过拟合，或反思猜错了根因（洞见 01 / 04 / 06）。'});
  if (a.task_type === 'open') f.push({cls:'', t:'开放写作任务因果最难看清。第一批建议先拿能客观打分的任务练手（洞见 02）。'});
  if (a.idea_source === 'social') f.push({cls:'', t:'你的思路来自社媒/二手。先把它当「线索」，抽六字段追溯到一手来源再采信（洞见 12）。'});
  if (!f.length) f.push({cls:'ok', t:'基础前提看起来不错。下面按你的场景给出适用洞见——仍建议先过一遍「通用纪律」那几条。'});
  return f;
}
function adviceHTML(a){
  const hit = KB.insights.filter(i => matched(i, a));
  const hitIds = new Set(hit.map(i => i.id));
  const spine = KB.insights.filter(i => i.spine && !hitIds.has(i.id));
  let h = `<div class="banner"><b>怎么读：</b>这是<b>确定性规则映射、非 LLM 生成</b>，每条都能追溯到出处。论文数字=<b>该论文设置下成立</b>，不等于在你的任务上一定成立；12 洞见<b>均尚未在本项目复现</b>。</div>`;
  h += '<div class="summary"><h3>总诊断</h3>' + topFlags(a).map(x => `<div class="flag ${x.cls}">${x.t}</div>`).join('') + '</div>';
  if (hit.length){ h += '<div class="group-label">高度相关（按你的场景命中）</div>' + hit.map(card).join(''); }
  else { h += '<div class="flag ok">还没有强命中——可能你回答得还少。下面是无论什么场景都该过一遍的「通用纪律」，也可以直接打字追问。</div>'; }
  if (spine.length){ h += '<div class="group-label">通用纪律（任何场景都建议过一遍）</div>' + spine.map(card).join(''); }
  h += '<div class="group-label">要避开的反模式</div><table class="at-table"><thead><tr><th>反模式</th><th>为什么危险</th><th>对应防线</th></tr></thead><tbody>'
    + KB.anti_patterns.map(p => `<tr><td><b>${p.name}</b></td><td>${p.why}</td><td>${p.defense}</td></tr>`).join('') + '</tbody></table>';
  const rel = KB.experiments.filter(e => e.insights.some(id => hitIds.has(id) || spine.some(s=>s.id===id)));
  const exps = rel.length ? rel : KB.experiments;
  h += '<div class="group-label">建议的首批最小验证</div>'
    + exps.map(e => `<div class="exp"><b>${e.priority}</b> · ${e.verify}（${e.insights.join('、')}）→ 最小任务：${e.task}；产出：${e.output}</div>`).join('');
  h += '<div class="summary" style="margin-top:14px"><h3>记住这三句就够</h3><ul>' + KB.closing.map(c => `<li>${c}</li>`).join('') + '</ul></div>';
  return h;
}

// ---------- 对话状态机 ----------
function askNext(){
  if (state.step >= Q.length){ return generate(); }
  const q = Q[state.step];
  botSay(`${esc(q.title)}<div class="qh">${esc(q.hint||'')}</div>`);
  const chips = q.options.map(o => ({ label: o.label, onClick: () => answer(q, o) }));
  chips.push({ label: '跳过这题', cls: 'ghost', onClick: () => { meSay('（跳过）'); state.step++; askNext(); } });
  chips.push({ label: '直接给建议 →', cls: 'go', onClick: generate });
  renderChips(chips);
}
function answer(q, o){
  meSay(o.label);
  state.answers[q.id] = o.id;
  state.step++;
  askNext();
}
function generate(){
  state.phase = 'free';
  botSay('好，根据你说的，我从知识库里挑了适用的洞见，给你分层建议 👇', false);
  botSay(adviceHTML(state.answers), true);
  botSay('建议看完了。你可以继续追问任意话题，我会从知识库里捞相关洞见（当前为关键词匹配，<b>非 LLM</b>；深度自然语言问答是第二阶段）。', false);
  freeChips();
}
function freeChips(){
  const chips = [
    {label:'工具调用出错', onClick:()=>freeReply('我的工具调用总是填错参数，该怎么优化？')},
    {label:'记忆 / 历史', onClick:()=>freeReply('该怎么给系统加记忆而不互相污染？')},
    {label:'多 agent 定位', onClick:()=>freeReply('多个 agent 协作出错，怎么定位是谁的责任？')},
    {label:'prompt 越改越长', onClick:()=>freeReply('prompt 优化后变得又长又复杂，是过拟合吗？')},
    {label:'没有评测集', onClick:()=>freeReply('我还没有评测集，能直接让模型优化 prompt 吗？')},
    {label:'走引导问答', cls:'ghost', onClick:startGuided},
    {label:'重新开始', cls:'ghost', onClick:restart},
  ];
  renderChips(chips);
}
function startGuided(){
  state.step = 0; state.answers = {}; state.phase = 'asking';
  botSay('好，我们走一遍引导问答，几个问题帮你精确定位 👇', false);
  askNext();
}

// ---------- 自由追问（关键词匹配，非 LLM）----------
// 中文不按空格分词：用「空格/拉丁词」+「二元字组(bigram)」双路 shingle，
// 让「记忆怎么办」也能切出「记忆」命中。深度语义匹配属于第二阶段。
function shingles(text){
  const out = new Set();
  text.toLowerCase().split(/[\s,，。、?？!！~…:：;；]+/).filter(t => t.length >= 2).forEach(t => out.add(t));
  const clean = text.toLowerCase().replace(/[\s,，。、?？!！~…:：;；()（）]+/g, '');
  for (let i = 0; i < clean.length - 1; i++) out.add(clean.slice(i, i + 2));
  return [...out];
}
// 分发：LLM 可用走后端，否则确定性关键词匹配
function freeReply(text){ return LLM.available ? llmAsk(text) : keywordReply(text); }

function keywordReply(text){
  const toks = shingles(text);
  const scored = KB.insights.map(i => {
    const blob = (i.title + i.hook + i.diagnosis + i.steps.join('') + (i.cross_channel||'')).toLowerCase();
    let s = 0; toks.forEach(t => { if (blob.includes(t)) s++; });
    return {i, s};
  }).filter(x => x.s > 0).sort((a,b) => b.s - a.s).slice(0, 3);
  if (!scored.length){
    botSay('这个问题我在知识库里没直接命中相关洞见。可以换个说法，或点「走引导问答」精确定位。<br><span class="corr">若你问的是某篇具体论文/仓库/文章，可用对应阅读流程把它读进库再来问：论文→read-paper、GitHub 仓库→github-repo-audit、社交/行业文章→article-deep-read。</span>', false);
    return;
  }
  botSay(`在知识库里找到 ${scored.length} 条相关洞见（关键词匹配，非 LLM）：`, false);
  botSay(scored.map(x => card(x.i)).join(''), true);
}

// LLM 模式：调后端流式接口，扎根知识库逐字作答，附可追溯引用；失败自动回退关键词匹配
function streamBubble(){
  const row = document.createElement('div'); row.className = 'row bot';
  row.innerHTML = '<div class="av bot">优</div><div class="msg bot wide"><span class="typing"><i></i><i></i><i></i></span></div>';
  msgs.appendChild(row); scroll();
  const box = row.querySelector('.msg');
  return { set(html){ box.innerHTML = html; scroll(); } };
}
function parseSSE(chunk){
  let event = 'message', data = '';
  chunk.split('\n').forEach(l => {
    if (l.startsWith('event:')) event = l.slice(6).trim();
    else if (l.startsWith('data:')) data += l.slice(5).trim();
  });
  if (!data) return null;
  try { return { event, data: JSON.parse(data) }; } catch(e){ return null; }
}
function contextFromAnswers(){
  const parts = [];
  Q.forEach(q => { const a = state.answers[q.id]; if (a){ const o = q.options.find(x => x.id === a); if (o) parts.push(q.id + '=' + o.label); } });
  return parts.join('; ');
}
function renderAnswer(text){
  let h = esc(text).replace(/\n/g, '<br>').replace(/\[(I\d{2}[^\]]*)\]/g, '<b>[$1]</b>');
  return `<div class="llm-ans">${h}</div>`;
}
function citedRefs(cited){
  if (!cited || !cited.length) return '';
  const items = cited.map(c => {
    const src = (c.sources && c.sources[0]) ? `<a href="${repoLink(c.sources[0])}">出处</a>` : '';
    return `<li><b>${c.id}</b> ${c.title} ${lvlTag(c.evidence_level)} ${src}</li>`;
  }).join('');
  return `<div class="refs"><div class="group-label">本回答可追溯到的知识库条目</div><ul>${items}</ul></div>`;
}
async function llmAsk(text){
  const bub = streamBubble();
  let acc = '', cited = null, errd = null;
  try{
    const res = await fetch('api/chat/stream', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ message: text, history: llmHistory, context: contextFromAnswers() })
    });
    if (!res.ok || !res.body) throw new Error('HTTP ' + res.status);
    const reader = res.body.getReader();
    const dec = new TextDecoder();
    let buf = '';
    while (true){
      const { value, done } = await reader.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });
      let i;
      while ((i = buf.indexOf('\n\n')) >= 0){
        const ev = parseSSE(buf.slice(0, i)); buf = buf.slice(i + 2);
        if (!ev) continue;
        if (ev.event === 'meta') cited = ev.data.cited;
        else if (ev.event === 'delta'){ acc += ev.data.text; bub.set(renderAnswer(acc) + '<span class="cursor"></span>'); }
        else if (ev.event === 'error') errd = ev.data;
      }
    }
    if (errd){
      bub.set(`LLM 调用失败：${esc(errd.error || errd.code || '未知错误')}<br>已回退到关键词匹配 👇`);
      keywordReply(text); return;
    }
    if (!acc.trim()){ bub.set('（模型没有返回内容，已回退到关键词匹配 👇）'); keywordReply(text); return; }
    bub.set(renderAnswer(acc) + citedRefs(cited));
    showCitedPanel(cited);
    llmHistory.push({ role: 'user', content: text });
    llmHistory.push({ role: 'assistant', content: acc });
  } catch(e){
    bub.set(`LLM 请求异常：${esc(String(e))}<br>已回退到关键词匹配 👇`);
    keywordReply(text);
  }
}

// ---------- 输入处理 ----------
function onSend(){
  const t = document.getElementById('box').value.trim();
  if (!t) return;
  document.getElementById('box').value = '';
  meSay(t);
  if (/^(给建议|建议|够了|结束|生成建议|直接给建议)/.test(t)) { generate(); return; }
  freeReply(t);  // 任何阶段都允许关键词追问
}
function restart(){
  state.step = 0; state.answers = {}; state.phase = 'asking'; llmHistory = [];
  msgs.innerHTML = '';
  greet();
}
function greet(){
  const tail = LLM.available
    ? `当前已接入 <b>LLM 模式</b>（${esc(LLM.model)}）：直接用自然语言问我任意 prompt 优化问题，我会<b>扎根知识库</b>作答并标注引用；也可以点「走引导问答」。`
    : `先回答几个问题（点选项即可，随时可「直接给建议」或打字追问）。`;
  botSay('你好，我是 Prompt 优化建议助手 👋 我会从我们整理的<b>证据分级知识库</b>里，按你的场景给出<b>分层、可追溯</b>的建议。<br>' + tail, false);
  if (LLM.available){ state.phase = 'free'; freeChips(); } else { askNext(); }
}
async function init(){
  try{
    const r = await fetch('api/health');
    const d = await r.json();
    if (d && d.ok && d.llm_available){
      LLM.available = true; LLM.model = d.model || '';
      const pill = document.getElementById('llmpill');
      if (pill) pill.innerHTML = 'LLM 模式：<b style="color:var(--green)">已接入</b>';
    }
  } catch(e){ /* file:// 或无后端 → 保持确定性模式 */ }
  greet();
}

// ---------- 左右面板：知识库导览 + 详情/引用 ----------
const RESOURCES = [
  { t: '综合报告 v3（主报告）', p: 'docs/analysis_report_v3_20260610.html' },
  { t: '读者向洞见手册（12 洞见）', p: 'docs/insight_handbook_20260609.html' },
  { t: 'Insight / Method 候选清单', p: 'docs/insight_method_catalog_20260609.html' },
  { t: '全景脑图（渲染版）', p: 'docs/prompt_evolution_mindmap_20260610.html' },
  { t: '小说体科普《别让 AI 自己改作业》', p: 'docs/popsci_prompt_evolution_story_20260610.html' },
];
const insightById = {}; KB.insights.forEach(i => insightById[i.id] = i);
const leftPanel = document.getElementById('leftPanel');
const rightPanel = document.getElementById('rightPanel');

function openRightIfSmall(){ if (window.innerWidth <= 1180) document.body.classList.add('dr-right'); }

function rightDefault(){
  rightPanel.innerHTML =
    '<div class="pan-h">怎么用</div>'
    + '<p class="pan-p">左侧点开任意<b>洞见 / 反模式 / 实验</b>，详情显示在这里；中间直接打字提问，回答会标注引用并把<b>本轮来源</b>列在这里。</p>'
    + '<div class="pan-h">证据等级</div>'
    + '<p class="pan-p">' + lvlTag('A') + ' 论文/源码并已结构化笔记　' + lvlTag('B') + ' 多源工程实践　' + lvlTag('recent-preprint') + ' 2026 新稿待复现</p>'
    + '<div class="banner" style="margin-top:10px">论文数字=<b>该论文设置下成立</b>，不等于在你的任务上一定成立；12 洞见<b>均尚未在本项目复现</b>。</div>';
}
function showInsight(id){ rightPanel.innerHTML = '<div class="pan-h">洞见详情</div>' + card(insightById[id]); openRightIfSmall(); rightPanel.scrollTop = 0; }
function showAnti(p){
  rightPanel.innerHTML = `<div class="pan-h">反模式</div><div class="card C"><h3>${p.name}</h3>`
    + `<div class="layer"><h4>为什么危险</h4><div>${p.why}</div></div>`
    + `<div class="layer"><h4>触发条件</h4><div>${p.trigger}</div></div>`
    + `<div class="layer"><h4>对应防线</h4><div>${p.defense}</div></div>`
    + `<div class="corr">证据渠道：${p.channels}</div></div>`;
  openRightIfSmall(); rightPanel.scrollTop = 0;
}
function showExp(e){
  rightPanel.innerHTML = `<div class="pan-h">首批最小验证</div><div class="card"><h3>${e.priority} · ${e.verify}</h3>`
    + `<div class="layer"><h4>对应洞见</h4><div>${e.insights.join('、')}</div></div>`
    + `<div class="layer"><h4>最小任务</h4><div>${e.task}</div></div>`
    + `<div class="layer"><h4>无论成败都能产出</h4><div>${e.output}</div></div></div>`;
  openRightIfSmall(); rightPanel.scrollTop = 0;
}
function showCitedPanel(cited){
  if (!cited || !cited.length){ return; }
  let h = '<div class="pan-h">本轮回答引用的来源</div>';
  cited.forEach(c => {
    if (insightById[c.id]){
      h += `<button class="navitem" data-ins="${c.id}">${lvlTag(c.evidence_level)} ${c.id} ${esc(c.title)}</button>`;
    } else {
      const src = (c.sources && c.sources[0]) ? repoLink(c.sources[0]) : '#';
      h += `<a class="reslink" href="${src}">${lvlTag(c.evidence_level)} ${esc(c.title)}</a>`;
    }
  });
  rightPanel.innerHTML = h;
  rightPanel.querySelectorAll('[data-ins]').forEach(el => el.onclick = () => showInsight(el.dataset.ins));
}
function navItem(label, onClick, lv){
  const b = document.createElement('button'); b.className = 'navitem'; b.onclick = onClick;
  b.innerHTML = (lv ? lvlTag(lv) + ' ' : '') + esc(label); return b;
}
function renderLeft(){
  leftPanel.innerHTML = '';
  const sec = (title) => { const h = document.createElement('div'); h.className = 'pan-h'; h.textContent = title; leftPanel.appendChild(h); };
  sec('文档与报告');
  RESOURCES.forEach(r => { const a = document.createElement('a'); a.className = 'reslink'; a.href = repoLink(r.p); a.textContent = r.t; leftPanel.appendChild(a); });
  sec('12 条核心洞见');
  let lastG = null;
  KB.insights.forEach(i => {
    if (i.group_title !== lastG){ const g = document.createElement('div'); g.className = 'nav-group'; g.textContent = i.group_title; leftPanel.appendChild(g); lastG = i.group_title; }
    leftPanel.appendChild(navItem(`${i.id} ${i.title}`, () => showInsight(i.id), i.evidence_level));
  });
  sec('要避开的反模式');
  KB.anti_patterns.forEach(p => leftPanel.appendChild(navItem(p.name, () => showAnti(p))));
  sec('首批最小验证');
  KB.experiments.forEach(e => leftPanel.appendChild(navItem(`${e.priority} ${e.verify}`, () => showExp(e))));
}

// 抽屉开关（小屏）
document.getElementById('tgLeft').onclick = () => document.body.classList.toggle('dr-left');
document.getElementById('tgRight').onclick = () => document.body.classList.toggle('dr-right');
document.getElementById('scrim').onclick = () => document.body.classList.remove('dr-left', 'dr-right');

document.getElementById('send').onclick = onSend;
document.getElementById('box').addEventListener('keydown', e => { if (e.key === 'Enter') onSend(); });
document.getElementById('restart').onclick = restart;
renderLeft(); rightDefault();
init();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    build()
