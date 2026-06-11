# -*- coding: utf-8 -*-
"""Build a vector index (bge-m3 via OpenRouter) for semantic retrieval.

为什么：关键词/bigram 召回只能命中字面词；向量召回能按语义找到相关洞见/笔记
（如「怎么防止 AI 乱编规则」→ 洞见06 防膨胀，即使没有共享词）。本脚本离线把 12 条
洞见 + `corpus_index.json` 的 42 篇笔记嵌入成向量，L2 归一化后写 `vector_index.json`；
查询时只需嵌入一次问题再做点积（=余弦）。知识库/语料变了就重跑。

模型：`OPENROUTER_EMBED_MODEL`（默认 `baai/bge-m3`，1024 维），走 OpenRouter。

Usage:  python advisor/build_vectors.py
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from scripts import llm_clients as llm  # noqa: E402

llm.load_dotenv(ROOT / ".env")
OUT = HERE / "vector_index.json"
BATCH = 32


def _norm(v):
    s = math.sqrt(sum(x * x for x in v)) or 1.0
    return [round(x / s, 6) for x in v]


def _insight_text(ins):
    return f"{ins['title']}。{ins['hook']} {ins['diagnosis']} {' '.join(ins.get('steps', []))}"


def _note_text(n):
    return f"{n['title']}。{n.get('summary', '')}"


def build():
    insights = json.loads((HERE / "knowledge_base.json").read_text(encoding="utf-8"))["insights"]
    corpus_path = HERE / "corpus_index.json"
    notes = json.loads(corpus_path.read_text(encoding="utf-8"))["docs"] if corpus_path.exists() else []

    items = [{"id": i["id"], "kind": "insight", "text": _insight_text(i)} for i in insights]
    items += [{"id": n["id"], "kind": "note", "text": _note_text(n)} for n in notes]

    model = llm._read_str_env(llm.ENV_OPENROUTER_EMBED_MODEL, llm.DEFAULT_OPENROUTER_EMBED_MODEL)
    vecs = []
    for s in range(0, len(items), BATCH):
        chunk = [it["text"] for it in items[s:s + BATCH]]
        vecs.extend(llm.embed_openrouter(chunk, model=model))
    if len(vecs) != len(items):
        raise SystemExit(f"嵌入数量不匹配: {len(vecs)} vs {len(items)}")

    dim = len(vecs[0]) if vecs else 0
    out_items = [{"id": it["id"], "kind": it["kind"], "vec": _norm(v)}
                 for it, v in zip(items, vecs)]
    OUT.write_text(json.dumps({"model": model, "dim": dim, "items": out_items},
                              ensure_ascii=False), encoding="utf-8")
    n_ins = sum(1 for it in out_items if it["kind"] == "insight")
    print(f"已生成 {OUT} （{len(out_items)} 向量：洞见 {n_ins} + 笔记 {len(out_items) - n_ins}，dim={dim}，model={model}）")


if __name__ == "__main__":
    build()
