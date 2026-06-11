# -*- coding: utf-8 -*-
"""Render the main "说明" markdown docs into themed, self-contained HTML pages.

Why: the综合论述报告 (analysis_report_v3) links out to markdown files; opening a
`.md` directly in a browser shows raw text. This script converts a curated set of
channel/middle-layer docs into polished HTML that matches the v3 visual theme, so
clicking from the report lands on a readable page instead of plain markdown.

Single source of truth stays the `.md`; re-run this script after editing any source
doc. Output `.html` sits next to its `.md`. Internal links among the converted set
are rewritten `.md` -> `.html`; links to non-converted docs are left untouched.

Usage:  python scripts/build_doc_html.py
"""
import html
import os
import re
from datetime import datetime, timezone, timedelta

import markdown

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(REPO, "docs")
REPORT = "analysis_report_v3_20260610.html"  # back-link target (lives in docs/)

# (path relative to docs/, channel/layer label, human title)
PAGES = [
    ("apo_seven_methods_primer_20260611.md", "中间层", "APO 七法主线详解"),
    ("insight_handbook_20260609.md", "中间层", "读者向洞见手册"),
    ("insight_method_catalog_20260609.md", "中间层", "Insight / Conclusion / Method 候选清单"),
    ("insight_field_standard.md", "中间层", "字段定义规范"),
    ("final_report_outline.md", "中间层", "最终报告结构"),
    ("experiment_plan.md", "中间层", "实验计划"),
    ("prompt_evolution_mindmap_20260610.md", "中间层", "全景脑图（Mermaid 源）"),
    ("popsci_prompt_evolution_story_20260610.md", "中间层", "小说体科普《别让 AI 自己改作业》"),
    ("arxiv_deep_reading_batch3_synthesis.md", "arXiv 渠道", "arXiv 深读 Batch 3 综合"),
    ("arxiv_top80_taxonomy.md", "arXiv 渠道", "arXiv top80 分类 taxonomy"),
    ("github_repo_channel_synthesis_20260609.md", "GitHub 渠道", "GitHub 渠道洞见综合"),
    ("source_batches/web_search_platform_insight_cards_20260609.md", "其它平台渠道", "其它平台 insight / method cards"),
    ("source_batches/twitter_web_insight_cards_20260609.md", "Twitter/X 渠道", "Twitter/X 社媒线索洞见卡"),
    ("source_batches/zhihu_insight_cards_20260609.md", "知乎渠道", "知乎洞见与方法卡片"),
]

CONVERTED = {p[0] for p in PAGES}

LABEL_COLOR = {
    "中间层": "#4d5246",
    "arXiv 渠道": "#176a5e",
    "GitHub 渠道": "#4a742f",
    "其它平台渠道": "#94660f",
    "Twitter/X 渠道": "#2d5fa8",
    "知乎渠道": "#a84055",
}

THEME_CSS = """
/* 视觉语言：学术期刊 / 研究档案。暖纸面 + 墨色 + 茶青主色 + 朱砂点缀；
   宋体衬线作标题、黑体正文、等宽作编号——全部系统字体，离线可用。 */
:root{--bg:#edeadd;--paper:#fbfaf3;--card:#fffefa;--ink:#232820;--muted:#6e7263;--faint:#999d8b;
--line:#d9d5c1;--line-soft:#e7e4d4;--soft:#f3f1e4;
--teal:#176a5e;--teal-deep:#0d4c43;--teal-soft:#e4efe9;--seal:#b23f2e;--seal-soft:#f8ece6;
--blue:#2d5fa8;--amber:#94660f;--rose:#a84055;--violet:#5e54a8;--green:#4a742f;--slate:#4d5246;
--serif:"Source Han Serif SC","Noto Serif SC","Songti SC","STSong",Georgia,"SimSun",serif;
--sans:"Source Han Sans SC","Noto Sans SC","PingFang SC","Microsoft YaHei","Segoe UI",sans-serif;
--mono:"Cascadia Code","JetBrains Mono",Consolas,"Courier New",monospace;
--radius:10px;}
*{box-sizing:border-box;} html{scroll-behavior:smooth;}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:16px;line-height:1.8;}
body::before{content:"";position:fixed;inset:0;z-index:0;pointer-events:none;opacity:.55;
background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 0.14 0 0 0 0 0.15 0 0 0 0 0.12 0 0 0 0.05 0'/%3E%3C/filter%3E%3Crect width='180' height='180' filter='url(%23n)'/%3E%3C/svg%3E");}
a{color:var(--teal-deep);text-underline-offset:3px;text-decoration-thickness:1px;}
a:hover{color:var(--seal);}
.topbar{position:sticky;top:0;z-index:20;display:flex;flex-wrap:wrap;align-items:center;gap:12px;
padding:10px 22px;background:rgba(253,252,245,.92);backdrop-filter:saturate(160%) blur(8px);
border-bottom:3px double var(--line);}
.topbar a.back{display:inline-flex;align-items:center;gap:6px;padding:5px 13px;border:1px solid var(--line);
border-radius:999px;background:var(--card);color:var(--ink);font-size:13px;font-weight:600;text-decoration:none;transition:.15s;}
.topbar a.back:hover{border-color:var(--teal);color:var(--teal-deep);}
.topbar a.home{background:var(--teal);border-color:var(--teal);color:#fff;}
.topbar a.home:hover{background:var(--teal-deep);border-color:var(--teal-deep);color:#fff;}
.topbar .chip{padding:3px 11px;border-radius:4px;color:#fff;font-size:12px;font-weight:700;letter-spacing:.02em;}
.topbar .doctitle{color:var(--muted);font-size:13.5px;font-weight:600;}
.topbar .mark{margin-left:auto;font-family:var(--mono);font-size:10px;font-weight:600;
letter-spacing:.22em;text-transform:uppercase;color:var(--faint);}
.wrap{position:relative;z-index:1;max-width:1180px;margin:0 auto;padding:30px 24px 88px;display:grid;
grid-template-columns:minmax(0,1fr) 248px;gap:38px;align-items:start;}
.content{background:var(--paper);border:1px solid var(--line);border-radius:var(--radius);
box-shadow:0 1px 2px rgba(35,40,32,.05),0 26px 50px -30px rgba(35,40,32,.35);padding:46px 52px 40px;min-width:0;}
.toc{position:sticky;top:72px;align-self:start;font-size:13.2px;padding:2px 0;max-height:calc(100vh - 100px);overflow:auto;}
.toc h4{margin:0 0 10px;font-family:var(--mono);font-size:10px;letter-spacing:.22em;text-transform:uppercase;color:var(--faint);}
.toc a{display:block;padding:4px 0 4px 12px;color:#4a5042;text-decoration:none;line-height:1.5;border-left:2px solid var(--line);transition:color .12s,border-color .12s;}
.toc a:hover{color:var(--teal-deep);border-left-color:var(--teal);}
.toc a.lv3{padding-left:24px;font-size:12.4px;color:#6a705f;}
.toc a.on{color:var(--teal-deep);border-left-color:var(--seal);font-weight:600;}
.content h1{margin:0 0 10px;font-family:var(--serif);font-size:31px;line-height:1.25;font-weight:700;}
.content h1::after{content:"";display:block;width:58px;height:3px;background:var(--seal);margin-top:16px;}
.content h2{margin:40px 0 14px;padding-bottom:8px;font-family:var(--serif);font-size:23px;font-weight:700;
border-bottom:1px solid var(--line);scroll-margin-top:72px;}
.content h3{margin:26px 0 10px;font-family:var(--serif);font-size:18.5px;color:#2c3227;scroll-margin-top:72px;}
.content h4{margin:20px 0 7px;font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);}
.content p{margin:0 0 14px;}
.content ul,.content ol{margin:0 0 14px;padding-left:24px;}
.content li{margin-bottom:5px;}
.content li>p{margin:0;}
.content a{font-weight:500;}
.content hr{border:0;border-top:3px double var(--line);margin:30px 0;}
.content blockquote{margin:0 0 15px;padding:12px 18px;border-left:3px solid var(--seal);
background:var(--seal-soft);border-radius:0 var(--radius) var(--radius) 0;color:#4a3a30;}
.content blockquote p:last-child{margin-bottom:0;}
.content table{width:100%;border-collapse:collapse;border:1px solid var(--line);
margin:6px 0 20px;font-size:14px;display:block;overflow-x:auto;background:var(--card);
font-variant-numeric:tabular-nums;}
.content thead th{background:var(--soft);color:var(--slate);font-weight:700;text-align:left;}
.content th,.content td{padding:10px 13px;border:1px solid var(--line-soft);vertical-align:top;line-height:1.62;}
.content tbody tr:nth-child(even){background:#faf8ef;}
.content code{font-family:var(--mono);font-size:.88em;
background:var(--soft);border:1px solid var(--line-soft);border-radius:4px;padding:1px 5px;}
.content pre{margin:0 0 16px;padding:14px 16px;border:1px solid var(--line-soft);border-left:3px solid var(--teal);
border-radius:6px;background:var(--card);overflow-x:auto;}
.content pre code{display:block;background:none;border:0;padding:0;font-size:12.8px;line-height:1.6;white-space:pre;color:#2c3227;}
.content pre.mermaid{background:#fff;border-left:1px solid var(--line-soft);text-align:center;}
.genfoot{margin-top:32px;padding-top:14px;border-top:3px double var(--line);color:var(--muted);font-size:12.3px;}
@media (max-width:980px){.wrap{grid-template-columns:1fr;}.toc{position:static;max-height:none;order:-1;}}
@media (max-width:640px){.content{padding:26px 20px;}.wrap{padding:16px 12px 48px;}.content h1{font-size:25px;}
.topbar .mark{display:none;}}
"""

MD_EXT = ["extra", "toc", "sane_lists", "admonition"]

# 阅读位置 -> 右侧目录高亮（无依赖、渐进增强：无 JS 时目录仍可用）
SCROLLSPY_JS = """<script>
(function(){
  var links = Array.prototype.slice.call(document.querySelectorAll('.toc a'));
  if (!links.length || !('IntersectionObserver' in window)) return;
  var byId = {};
  links.forEach(function(a){ byId[decodeURIComponent(a.getAttribute('href')).slice(1)] = a; });
  var obs = new IntersectionObserver(function(es){
    es.forEach(function(e){
      if (!e.isIntersecting) return;
      var a = byId[e.target.id];
      if (!a) return;
      links.forEach(function(x){ x.classList.remove('on'); });
      a.classList.add('on');
    });
  }, {rootMargin: '-12% 0px -72% 0px'});
  document.querySelectorAll('.content h2[id], .content h3[id]').forEach(function(h){ obs.observe(h); });
})();
</script>"""


def rel_back_to_report(md_relpath: str) -> str:
    depth = md_relpath.count("/")
    return ("../" * depth) + REPORT


def rel_to_advisor(md_relpath: str) -> str:
    """相对路径指向对话助手主页：file:// 与任意静态托管直接可达；
    advisor 后端托管时由 server.py 的 /advisor/advisor.html 别名路由兜住。"""
    depth = md_relpath.count("/")
    return ("../" * (depth + 1)) + "advisor/advisor.html"


def rewrite_internal_links(body: str, page_dir: str) -> str:
    """Rewrite href to converted .md -> .html (only when target is in CONVERTED)."""
    def repl(m):
        pre, target, frag = m.group(1), m.group(2), m.group(3) or ""
        if target.startswith(("http://", "https://", "mailto:", "#", "//")):
            return m.group(0)
        norm = os.path.normpath(os.path.join(page_dir, target)).replace("\\", "/")
        if norm in CONVERTED:
            return f'{pre}{target[:-3]}.html{frag}'
        return m.group(0)
    return re.sub(r'(href=")([^"#]+\.md)(#[^"]*)?', repl, body)


def render_mermaid(body: str) -> (str, bool):
    """Turn ```mermaid fenced blocks into <pre class="mermaid"> with unescaped text."""
    pat = re.compile(r'<pre><code class="language-mermaid">(.*?)</code></pre>', re.S)
    has = bool(pat.search(body))
    body = pat.sub(lambda m: '<pre class="mermaid">' + html.unescape(m.group(1)) + "</pre>", body)
    return body, has


def build_toc(body: str) -> str:
    items = re.findall(r'<h([23]) id="([^"]+)">(.*?)</h\1>', body, re.S)
    if not items:
        return ""
    rows = []
    for lvl, hid, text in items:
        txt = re.sub(r"<[^>]+>", "", text).strip()
        cls = "lv3" if lvl == "3" else "lv2"
        rows.append(f'<a class="{cls}" href="#{hid}">{txt}</a>')
    return '<aside class="toc"><h4>本页目录</h4>' + "\n".join(rows) + "</aside>"


def main():
    stamp = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M CST")
    built = 0
    for relpath, label, title in PAGES:
        src = os.path.join(DOCS, relpath)
        if not os.path.exists(src):
            print("SKIP (missing):", relpath)
            continue
        text = open(src, encoding="utf-8").read()
        md = markdown.Markdown(extensions=MD_EXT, output_format="html5")
        body = md.convert(text)

        page_dir = os.path.dirname(relpath)
        body = rewrite_internal_links(body, page_dir)
        body, has_mermaid = render_mermaid(body)
        toc = build_toc(body)

        back = rel_back_to_report(relpath)
        advisor = rel_to_advisor(relpath)
        color = LABEL_COLOR.get(label, "#46525f")
        src_name = os.path.basename(relpath)

        mermaid_js = ""
        if has_mermaid:
            mermaid_js = (
                '<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>'
                '<script>mermaid.initialize({startOnLoad:true,theme:"neutral",'
                'themeVariables:{fontFamily:"Microsoft YaHei,PingFang SC,Segoe UI,Arial,sans-serif"}});</script>'
            )

        page = (
            "<!doctype html>\n<html lang=\"zh-CN\">\n<head>\n"
            "<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            f"<title>{html.escape(title)} · prompt_evolution</title>\n"
            "<style>" + THEME_CSS + "</style>\n</head>\n<body>\n"
            "<div class=\"topbar\">"
            f"<a class=\"back home\" href=\"{advisor}\">💬 对话助手主页</a>"
            f"<a class=\"back\" href=\"{back}\">← 返回综合论述报告 v3</a>"
            f"<span class=\"chip\" style=\"background:{color}\">{html.escape(label)}</span>"
            f"<span class=\"doctitle\">{html.escape(title)}</span>"
            "<span class=\"mark\">Prompt Evolution · 研究档案</span>"
            "</div>\n"
            "<div class=\"wrap\">\n"
            f"<article class=\"content\">\n{body}\n"
            "<div class=\"genfoot\">本页由 <code>scripts/build_doc_html.py</code> 从源文件 "
            f"<code>docs/{relpath}</code> 自动生成（{stamp}），请勿手改此 HTML；修改请改源 <code>.md</code> 后重跑脚本。"
            f"可视化综合见 <a href=\"{back}\">综合论述报告 v3</a>。</div>\n"
            "</article>\n"
            f"{toc}\n"
            "</div>\n"
            f"{mermaid_js}\n"
            f"{SCROLLSPY_JS if toc else ''}\n"
            "</body>\n</html>\n"
        )

        out = os.path.join(DOCS, relpath[:-3] + ".html")
        with open(out, "w", encoding="utf-8") as f:
            f.write(page)
        built += 1
        print("built:", os.path.relpath(out, REPO).replace("\\", "/"))
    print(f"\n{built}/{len(PAGES)} pages generated.")


if __name__ == "__main__":
    main()
