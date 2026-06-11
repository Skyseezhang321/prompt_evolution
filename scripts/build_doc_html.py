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
    ("insight_handbook_20260609.md", "中间层", "读者向洞见手册"),
    ("insight_method_catalog_20260609.md", "中间层", "Insight / Conclusion / Method 候选清单"),
    ("insight_field_standard.md", "中间层", "字段定义规范"),
    ("final_report_outline.md", "中间层", "最终报告结构"),
    ("experiment_plan.md", "中间层", "实验计划"),
    ("prompt_evolution_mindmap_20260610.md", "中间层", "全景脑图（Mermaid 源）"),
    ("arxiv_deep_reading_batch3_synthesis.md", "arXiv 渠道", "arXiv 深读 Batch 3 综合"),
    ("arxiv_top80_taxonomy.md", "arXiv 渠道", "arXiv top80 分类 taxonomy"),
    ("github_repo_channel_synthesis_20260609.md", "GitHub 渠道", "GitHub 渠道洞见综合"),
    ("source_batches/web_search_platform_insight_cards_20260609.md", "其它平台渠道", "其它平台 insight / method cards"),
    ("source_batches/twitter_web_insight_cards_20260609.md", "Twitter/X 渠道", "Twitter/X 社媒线索洞见卡"),
    ("source_batches/zhihu_insight_cards_20260609.md", "知乎渠道", "知乎洞见与方法卡片"),
]

CONVERTED = {p[0] for p in PAGES}

LABEL_COLOR = {
    "中间层": "#46525f",
    "arXiv 渠道": "#257d72",
    "GitHub 渠道": "#4f7e33",
    "其它平台渠道": "#af6b08",
    "Twitter/X 渠道": "#2d67ad",
    "知乎渠道": "#b44a5c",
}

THEME_CSS = """
:root{--bg:#f5f7f5;--paper:#fff;--ink:#202329;--muted:#626b74;--line:#d8ded8;--soft:#edf1ed;
--teal:#257d72;--blue:#2d67ad;--amber:#af6b08;--rose:#b44a5c;--violet:#665bb4;--green:#4f7e33;--slate:#46525f;
--shadow:0 14px 34px rgba(29,35,40,.08);--radius:8px;}
*{box-sizing:border-box;} html{scroll-behavior:smooth;}
body{margin:0;background:var(--bg);color:var(--ink);
font-family:"Microsoft YaHei","PingFang SC","Segoe UI",Arial,sans-serif;font-size:16px;line-height:1.78;}
a{color:var(--blue);text-underline-offset:3px;}
.topbar{position:sticky;top:0;z-index:20;display:flex;flex-wrap:wrap;align-items:center;gap:12px;
padding:11px 22px;background:rgba(255,255,255,.94);backdrop-filter:saturate(180%) blur(6px);
border-bottom:1px solid var(--line);box-shadow:0 1px 0 rgba(0,0,0,.02);}
.topbar a.back{display:inline-flex;align-items:center;gap:6px;padding:5px 12px;border:1px solid var(--line);
border-radius:999px;background:#fff;color:var(--ink);font-size:13.5px;font-weight:650;text-decoration:none;}
.topbar a.back:hover{border-color:var(--teal);color:var(--teal);}
.topbar .chip{padding:3px 11px;border-radius:999px;color:#fff;font-size:12.5px;font-weight:700;}
.topbar .doctitle{color:var(--muted);font-size:13.5px;font-weight:600;}
.wrap{max-width:1180px;margin:0 auto;padding:26px 24px 80px;display:grid;
grid-template-columns:minmax(0,1fr) 244px;gap:34px;align-items:start;}
.content{background:var(--paper);border:1px solid var(--line);border-radius:var(--radius);
box-shadow:var(--shadow);padding:36px 40px;min-width:0;}
.toc{position:sticky;top:64px;align-self:start;font-size:13.5px;border:1px solid var(--line);
border-radius:var(--radius);background:#fbfcfa;padding:16px 16px;max-height:calc(100vh - 90px);overflow:auto;}
.toc h4{margin:0 0 10px;font-size:12px;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);}
.toc a{display:block;padding:3px 0;color:#3d444b;text-decoration:none;line-height:1.45;border-left:2px solid transparent;padding-left:10px;margin-left:-2px;}
.toc a:hover{color:var(--teal);border-left-color:var(--teal);}
.toc a.lv3{padding-left:22px;font-size:12.8px;color:#5a626b;}
.content h1{margin:0 0 6px;font-size:30px;line-height:1.2;font-weight:760;}
.content h2{margin:34px 0 12px;padding-bottom:7px;font-size:23px;border-bottom:2px solid var(--soft);scroll-margin-top:64px;}
.content h3{margin:24px 0 9px;font-size:18.5px;color:#2a2f36;scroll-margin-top:64px;}
.content h4{margin:18px 0 6px;font-size:15px;color:var(--slate);}
.content p{margin:0 0 13px;}
.content ul,.content ol{margin:0 0 13px;padding-left:24px;}
.content li{margin-bottom:5px;}
.content li>p{margin:0;}
.content a{font-weight:500;}
.content hr{border:0;border-top:1px solid var(--line);margin:26px 0;}
.content blockquote{margin:0 0 14px;padding:11px 16px;border-left:4px solid var(--blue);
background:#eef4fc;border-radius:0 var(--radius) var(--radius) 0;color:#2c3a4d;}
.content blockquote p:last-child{margin-bottom:0;}
.content table{width:100%;border-collapse:collapse;border:1px solid var(--line);border-radius:var(--radius);
overflow:hidden;margin:6px 0 18px;font-size:14px;display:block;overflow-x:auto;}
.content thead th{background:#eef1ed;color:#3d444b;font-weight:720;text-align:left;}
.content th,.content td{padding:10px 13px;border:1px solid var(--line);vertical-align:top;line-height:1.6;}
.content tbody tr:nth-child(even){background:#fbfcfa;}
.content code{font-family:"Cascadia Code","Consolas","SFMono-Regular",monospace;font-size:.9em;
background:#eef1ed;border:1px solid var(--line);border-radius:4px;padding:1px 5px;}
.content pre{margin:0 0 16px;padding:14px 16px;border:1px solid var(--line);border-left:3px solid var(--teal);
border-radius:6px;background:#fbfcfa;overflow-x:auto;}
.content pre code{display:block;background:none;border:0;padding:0;font-size:12.8px;line-height:1.6;white-space:pre;color:#2a2f36;}
.content pre.mermaid{background:#fff;border-left:1px solid var(--line);text-align:center;}
.genfoot{margin-top:26px;padding-top:14px;border-top:1px solid var(--line);color:var(--muted);font-size:12.5px;}
@media (max-width:980px){.wrap{grid-template-columns:1fr;}.toc{position:static;max-height:none;order:-1;}}
@media (max-width:640px){.content{padding:24px 20px;}.wrap{padding:16px 12px 48px;}.content h1{font-size:25px;}}
"""

MD_EXT = ["extra", "toc", "sane_lists", "admonition"]


def rel_back_to_report(md_relpath: str) -> str:
    depth = md_relpath.count("/")
    return ("../" * depth) + REPORT


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
            f"<a class=\"back\" href=\"{back}\">← 返回综合论述报告 v3</a>"
            f"<span class=\"chip\" style=\"background:{color}\">{html.escape(label)}</span>"
            f"<span class=\"doctitle\">{html.escape(title)}</span>"
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
