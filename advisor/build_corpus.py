# -*- coding: utf-8 -*-
"""Build a retrieval corpus index from the vetted notes the reading skills produce.

为什么：三个阅读 skill（read-paper / github-repo-audit / article-deep-read）的产出是
带证据等级的结构化笔记，它们是知识库的「内容供应链」。本脚本把这些笔记扫成一个轻量
索引 `corpus_index.json`，让 LLM 问答后端（server.py）在 12 条洞见之外，还能检索到
这些一手笔记作为**补充扎根**（保留证据等级与出处路径）。

这是「方案 A：扩检索语料」的离线步骤——笔记变了就重跑。问答仍然只检索/引用 vetted
笔记，不在运行时实时跑 skill。

来源 → 笔记目录 → 证据等级（沿用 v3 证据金字塔的渠道定位）：
  read-paper         → docs/paper_notes/paper-*.md          → A（论文并已结构化笔记）
  github-repo-audit  → docs/github_repo_audit_notes/repo-*.md → B（工程审计草稿）
  article-deep-read  → docs/industry_notes/practice-*.md     → 取笔记自标「证据等级」，默认 D（线索）

Usage:  python advisor/build_corpus.py
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DOCS = ROOT / "docs"
OUT = HERE / "corpus_index.json"

# 行业笔记自标「证据等级」→ A/B/C/D（单篇社交/行业文章默认线索层）
INDUSTRY_LEVEL_MAP = {"strong": "B", "medium": "C", "weak": "D", "a": "A", "b": "B", "c": "C", "d": "D"}

SUMMARY_CAP = 600


def _first_title(text: str, strip_prefixes=("Paper Note:", "Source Audit:")) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            t = line[2:].strip()
            for p in strip_prefixes:
                if t.startswith(p):
                    t = t[len(p):].strip()
            return t
    return ""


def _section(text: str, heading: str) -> str:
    """抓 `## heading` 到下一个 `## ` 之间的正文。"""
    m = re.search(rf"^##\s*{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    if not m:
        return ""
    return m.group(1).strip()


def _field(text: str, key: str) -> str:
    """抓 `key：value` 或 `- key: value`（中英文冒号）。"""
    m = re.search(rf"^[-\s]*{re.escape(key)}\s*[:：]\s*(.+)$", text, re.M)
    return m.group(1).strip().strip("`") if m else ""


def _clean(s: str) -> str:
    s = re.sub(r"`[0-9A-Fa-f]{32,}`", "", s)        # 去掉 sha256 噪声
    s = re.sub(r"\s+", " ", s).strip()
    return s[:SUMMARY_CAP]


def _paper(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    summary = _section(text, "一句话结论") or _section(text, "一句话总结")
    return {
        "id": path.stem, "type": "paper", "level": "A",
        "title": _first_title(text) or path.stem,
        "summary": _clean(summary),
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
    }


def _industry(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    grade = _field(text, "证据等级").lower()
    level = INDUSTRY_LEVEL_MAP.get(grade, "D")
    summary = _section(text, "一句话结论") or _section(text, "一句话总结")
    return {
        "id": path.stem, "type": "industry", "level": level,
        "title": _first_title(text) or path.stem,
        "summary": _clean(summary),
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
    }


def _github(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    repo = _field(text, "repository")
    tags = _field(text, "content_tag_counts")
    # 审计草稿没有「一句话结论」，用 repo + 内容标签作为检索摘要
    summary = _clean(f"GitHub 源码审计草稿。仓库 {repo}。内容信号 {tags}")
    return {
        "id": path.stem, "type": "github", "level": "B",
        "title": _first_title(text) or path.stem,
        "summary": summary,
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
    }


def build():
    docs = []
    for p in sorted((DOCS / "paper_notes").glob("paper-*.md")):
        docs.append(_paper(p))
    for p in sorted((DOCS / "industry_notes").glob("practice-*.md")):
        docs.append(_industry(p))
    audit_dir = DOCS / "github_repo_audit_notes"
    if audit_dir.exists():
        for p in sorted(audit_dir.glob("repo-*.md")):
            docs.append(_github(p))

    # 丢掉没有任何摘要的条目（避免空噪声进检索）
    docs = [d for d in docs if d["summary"]]
    OUT.write_text(json.dumps({"docs": docs}, ensure_ascii=False, indent=2), encoding="utf-8")
    by_type = {}
    for d in docs:
        by_type[d["type"]] = by_type.get(d["type"], 0) + 1
    print(f"已生成 {OUT} （{len(docs)} 篇：{by_type}）")


if __name__ == "__main__":
    build()
