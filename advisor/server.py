# -*- coding: utf-8 -*-
"""FastAPI 后端：扎根知识库的 Prompt 优化建议 LLM 问答（v2）。

为什么要后端：静态页里**不能放 API key**（会随页面暴露/被提交）。后端从本地
`.env` 读 OpenRouter key（经 `scripts/llm_clients.py`），对 `knowledge_base.json`
做检索增强，构造**受约束**的系统提示（只用知识库作答、每条标注洞见编号与证据等级、
不编造、论文数字=该论文设置下成立），再调 OpenRouter，把回答与引用条目返回前端。

同源托管：根路由直接发 `advisor.html`，前端用相对 `api/*` 调本后端，无 CORS。
LLM 不可用或调用失败时，前端自动回退到确定性关键词匹配（见 advisor.html）。

启动：
    python -m uvicorn advisor.server:app --reload --port 8000
    # 然后浏览器打开 http://localhost:8000/
依赖：fastapi, uvicorn（见 advisor/requirements.txt）。LLM 模型/凭证见 .env。
"""
from __future__ import annotations

import json
import math
import os
import sys
from dataclasses import replace
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from scripts import llm_clients as llm  # noqa: E402  复用现成 OpenRouter 客户端

# ---- 启动期加载 ----
llm.load_dotenv(ROOT / ".env")  # 不覆盖已存在的环境变量
KB = json.loads((HERE / "knowledge_base.json").read_text(encoding="utf-8"))
INSIGHTS = KB["insights"]

# 阅读 skill 产出的 vetted 笔记语料（方案 A：扩检索语料）。由 build_corpus.py 生成；
# 缺失则退化为只检索 12 条洞见。
_corpus_path = HERE / "corpus_index.json"
CORPUS = json.loads(_corpus_path.read_text(encoding="utf-8")).get("docs", []) if _corpus_path.exists() else []

INSIGHT_BY_ID = {i["id"]: i for i in INSIGHTS}
NOTE_BY_ID = {n["id"]: n for n in CORPUS}

# 向量索引（bge-m3，由 build_vectors.py 生成）。缺失或运行时嵌入失败 → 回退关键词召回。
_vec_path = HERE / "vector_index.json"
_VEC = json.loads(_vec_path.read_text(encoding="utf-8")) if _vec_path.exists() else {}
VECTORS = _VEC.get("items", [])
VECTOR_MODEL = _VEC.get("model", "")
NOTE_SIM_FLOOR = float(os.getenv("ADVISOR_NOTE_FLOOR", "0.30"))

# 建议答案需要篇幅；deepseek-v4-pro 等推理模型还会用掉部分 token 做推理，
# 故为本场景单独调高输出上限（不改用户 .env 的全局 OPENROUTER_MAX_TOKENS）。
# 可用环境变量 ADVISOR_MAX_TOKENS 覆盖。
ADVISOR_MAX_TOKENS = int(os.getenv("ADVISOR_MAX_TOKENS", "3000"))


# ---------- 检索（与前端确定性匹配同口径：空格词 + 中文 bigram）----------
def shingles(text: str) -> list[str]:
    out: set[str] = set()
    seps = "\t\n ，。、,.?？!！~…:：;；()（）"
    for tok in "".join(c if c not in seps else " " for c in text.lower()).split():
        if len(tok) >= 2:
            out.add(tok)
    clean = "".join(c for c in text.lower() if c not in seps)
    for i in range(len(clean) - 1):
        out.add(clean[i:i + 2])
    return list(out)


def _blob(ins: dict) -> str:
    return (ins["title"] + ins["hook"] + ins["diagnosis"]
            + "".join(ins["steps"]) + ins.get("cross_channel", "")).lower()


def retrieve(message: str, k: int = 6) -> list[dict]:
    """挑出与问题最相关的洞见作为扎根上下文；命中太少时用 spine（通用纪律）兜底。"""
    toks = shingles(message)
    scored = sorted(
        ((sum(1 for t in toks if t in _blob(ins)), ins) for ins in INSIGHTS),
        key=lambda x: -x[0],
    )
    top = [ins for s, ins in scored if s > 0][:k]
    if len(top) < 3:  # 问题太泛 → 补通用纪律，保证 LLM 有底座可依
        have = {i["id"] for i in top}
        for ins in INSIGHTS:
            if ins.get("spine") and ins["id"] not in have:
                top.append(ins)
    return top


def retrieve_corpus(message: str, k: int = 3) -> list[dict]:
    """从阅读 skill 产出的 vetted 笔记里挑相关的，作为补充扎根（保留证据等级与出处）。"""
    if not CORPUS:
        return []
    toks = shingles(message)
    scored = sorted(
        ((sum(1 for t in toks if t in (d.get("title", "") + " " + d.get("summary", "")).lower()), d)
         for d in CORPUS),
        key=lambda x: -x[0],
    )
    return [d for s, d in scored if s > 0][:k]


# ---------- 向量召回（bge-m3 语义相似）----------
def _embed_query(message: str) -> list[float]:
    vec = llm.embed_openrouter(message)[0]
    s = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / s for x in vec]  # 归一化；索引向量已归一化 → 余弦=点积


def retrieve_vector(message: str, k_ins: int = 6, k_note: int = 3):
    """对问题做语义召回：返回 (insights, notes)。命中向量索引按余弦排序。"""
    q = _embed_query(message)
    ranked = sorted(
        ((sum(a * b for a, b in zip(q, it["vec"])), it) for it in VECTORS),
        key=lambda x: -x[0],
    )
    ins, notes = [], []
    for score, it in ranked:
        if it["kind"] == "insight" and len(ins) < k_ins:
            obj = INSIGHT_BY_ID.get(it["id"])
            if obj:
                ins.append(obj)
        elif it["kind"] == "note" and len(notes) < k_note and score >= NOTE_SIM_FLOOR:
            obj = NOTE_BY_ID.get(it["id"])
            if obj:
                notes.append(obj)
    return ins, notes


def retrieve_grounding(message: str):
    """优先向量召回；无向量索引或嵌入失败则回退关键词召回。返回 (insights, notes)。"""
    if VECTORS:
        try:
            ins, notes = retrieve_vector(message)
            if ins:
                return ins, notes
        except (llm.LLMRequestError, llm.LLMConfigError, KeyError, IndexError):
            pass
    return retrieve(message), retrieve_corpus(message)


# ---------- 受约束的扎根系统提示 ----------
def _insight_block(ins: dict) -> str:
    ev = "；".join(f"{e['num']}—{e['note']}（{e['level']}）" for e in ins.get("evidence", []))
    steps = " / ".join(ins.get("steps", []))
    example = ins.get("example", "").replace("\n", "\n    ")
    example_line = f"  上手示例（演示性，数字非实验结论，回答时应改写贴合用户场景）：\n    {example}\n" if example else ""
    return (
        f"[{ins['id']} · {ins['evidence_level']}] {ins['title']}\n"
        f"  反直觉点：{ins['hook']}\n"
        f"  诊断：{ins['diagnosis']}\n"
        f"  步骤：{steps}\n"
        f"{example_line}"
        f"  证据：{ev}\n"
        f"  边界：{ins['boundary']}"
    )


def build_system_prompt(insights: list[dict], notes: list[dict] = (), lang: str = "zh") -> str:
    kb = "\n\n".join(_insight_block(i) for i in insights)
    anti = "；".join(p["name"] for p in KB.get("anti_patterns", []))
    closing = " ".join(KB.get("closing", []))
    # 仅输出语言随 UI 切换；知识库片段保持中文，模型跨语种作答即可。
    lang_rule = (
        "5. Answer in English, concise and specific, no padding (the knowledge base is in Chinese; "
        "translate the substance faithfully and keep the bracketed citations as-is). If the question is "
        "unrelated to prompt optimization, politely state this assistant's scope.\n"
        if lang == "en" else
        "5. 用简体中文，简洁具体，不堆砌。若问题与 prompt 优化无关，礼貌说明本助手范围。\n"
    )
    notes_block = ""
    if notes:
        lines = "\n".join(f"- [{n['id']}·{n['level']}] {n['title']}：{n['summary']}" for n in notes)
        notes_block = (
            "\n\n【相关一手笔记（补充扎根，可在适用时引用，注明来源 id 与等级，如 "
            f"[paper-coin-flip-2026·A]）】\n{lines}"
        )
    return (
        "你是「Prompt 优化建议助手」。只能依据下面【知识库片段】与【相关一手笔记】回答用户"
        "关于 prompt 优化与自进化的问题。\n\n"
        "硬性要求：\n"
        "1. 只用所给材料里的结论、数字、方法作答；材料没覆盖的内容，明确说「知识库未覆盖」，"
        "不要编造数字或结论。\n"
        "2. 每条建议结尾用方括号标注引用来源与证据等级：洞见如 [I06·recent-preprint]、[I01·A]；"
        "一手笔记用其 id 如 [paper-coin-flip-2026·A]。\n"
        "3. 论文数字一律视为「该论文设置下成立」，不得说成普适或本项目结论；"
        "本项目尚未复现这些洞见。\n"
        "4. 结合用户的具体场景给出分层、可执行的建议（诊断→步骤→示例→证据→边界），不要泛泛而谈：\n"
        "   每条核心建议都要落到一个贴合用户场景的具体例子或方向——可直接套用的 prompt 片段、字段表、\n"
        "   before/after 改写、记录格式等，优先把知识库里的「上手示例」改写成用户任务和数据的版本，\n"
        "   不要原样照搬。示例是演示性内容、不算证据：不得在示例里编造实验数字，也不得把演示数字说成结论。\n"
        f"{lang_rule}"
        "6. 若所给材料都未覆盖用户问到的**具体论文/仓库/文章**，明确说未覆盖，并建议把它读进库："
        "论文→read-paper、GitHub 仓库→github-repo-audit、社交/行业文章→article-deep-read。\n\n"
        f"【知识库片段】\n{kb}{notes_block}\n\n"
        f"【通用三句】{closing}\n"
        f"【常见反模式（要劝阻用户避开）】{anti}"
    )


def build_messages(message: str, history: list[dict], insights: list[dict],
                   notes: list[dict] = (), context: str = "", lang: str = "zh") -> list[dict]:
    msgs = [{"role": "system", "content": build_system_prompt(insights, notes, lang)}]
    for h in history[-6:]:  # 仅带最近几轮，控制 token
        role = h.get("role")
        content = (h.get("content") or "").strip()
        if role in ("user", "assistant") and content:
            msgs.append({"role": role, "content": content})
    if not context:
        user = message
    else:
        prefix = "Known scenario" if lang == "en" else "已知场景"
        user = f"（{prefix}：{context}）\n{message}"
    msgs.append({"role": "user", "content": user})
    return msgs


# ---------- FastAPI ----------
app = FastAPI(title="Prompt 优化建议助手", docs_url=None, redoc_url=None)


class ChatIn(BaseModel):
    # pydantic 会在运行时求值字段注解，内置泛型 list[dict] 在 Python 3.8 上会抛
    # "'type' object is not subscriptable"，故这里必须用 typing.List/Dict。
    message: str
    history: List[Dict] = []
    context: str = ""
    lang: str = "zh"  # "en" → 用英文作答（仍扎根中文知识库、保留洞见编号与证据等级引用）


def _llm_status() -> tuple[bool, str]:
    try:
        cfg = llm.resolve_openrouter_config(require_api_key=False)
        return bool(cfg.api_key), cfg.model
    except Exception:
        return False, ""


@app.get("/api/health")
def health():
    available, model = _llm_status()
    return {"ok": True, "llm_available": available, "model": model,
            "insights": len(INSIGHTS), "corpus": len(CORPUS),
            "retrieval": "vector" if VECTORS else "keyword",
            "embed_model": VECTOR_MODEL}


def _prepare(msg: str, history: list[dict], context: str, lang: str = "zh"):
    """检索洞见 + 笔记 → (cited 引用清单, messages)，供流式/非流式端点共用。"""
    insights, notes = retrieve_grounding(msg)
    cited = [{"id": i["id"], "title": i["title"],
              "evidence_level": i["evidence_level"], "sources": i.get("sources", [])}
             for i in insights]
    cited += [{"id": n["id"], "title": n["title"],
               "evidence_level": n["level"], "sources": [n["path"]]}
              for n in notes]
    messages = build_messages(msg, history, insights, notes, context, lang)
    return cited, messages


def _resolve_cfg():
    cfg = llm.resolve_openrouter_config()  # 需要 key
    return replace(cfg, max_tokens=max(cfg.max_tokens, ADVISOR_MAX_TOKENS))


def _sse(event: str, obj: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(obj, ensure_ascii=False)}\n\n"


@app.post("/api/chat")
def chat(req: ChatIn):
    msg = (req.message or "").strip()
    if not msg:
        return JSONResponse({"ok": False, "code": "empty", "error": "message 为空"}, 400)
    cited, messages = _prepare(msg, req.history, req.context, req.lang)
    try:
        cfg = _resolve_cfg()
        resp = llm.call_openrouter_chat(messages=messages, config=cfg)
        text = llm.extract_openrouter_text(resp).strip()
    except llm.LLMConfigError as e:
        return {"ok": False, "code": "no_key", "error": str(e), "cited": cited}
    except llm.LLMRequestError as e:
        return {"ok": False, "code": "request_failed", "error": str(e), "cited": cited}
    if not text:
        return {"ok": False, "code": "empty_answer",
                "error": "模型返回空内容", "cited": cited}
    return {"ok": True, "answer": text, "cited": cited, "model": cfg.model}


@app.post("/api/chat/stream")
def chat_stream(req: ChatIn):
    """流式版：SSE 推送 meta(引用) → 多个 delta(文本片段) → done / error。"""
    msg = (req.message or "").strip()
    if not msg:
        return JSONResponse({"ok": False, "code": "empty", "error": "message 为空"}, 400)
    cited, messages = _prepare(msg, req.history, req.context, req.lang)

    def gen():
        yield _sse("meta", {"cited": cited})
        try:
            cfg = _resolve_cfg()
            got = False
            for chunk in llm.stream_openrouter_chat(messages, config=cfg):
                got = True
                yield _sse("delta", {"text": chunk})
            if got:
                yield _sse("done", {"model": cfg.model})
            else:
                yield _sse("error", {"code": "empty_answer", "error": "模型返回空内容"})
        except llm.LLMConfigError as e:
            yield _sse("error", {"code": "no_key", "error": str(e)})
        except llm.LLMRequestError as e:
            yield _sse("error", {"code": "request_failed", "error": str(e)})

    return StreamingResponse(gen(), media_type="text/event-stream")


# 让卡片里的 ../docs/* 出处链接在后端托管时也可点（关掉了 Swagger 的 /docs 以避免冲突）
app.mount("/docs", StaticFiles(directory=str(ROOT / "docs")), name="repo-docs")


@app.get("/")
def index():
    return FileResponse(str(HERE / "advisor.html"))


# 文档/报告页顶部「💬 对话助手主页」用相对链接 ../advisor/advisor.html（file:// 与
# 静态托管直接可达）；后端托管时该路径不在 /docs 挂载内，这里重定向回根路由。
# 不能直接 FileResponse：页面里 api/* 为相对路径，在 /advisor/ 下会解析成
# /advisor/api/* → 404，导致 LLM 模式静默失效（实跑日志已踩中）。
@app.get("/advisor/advisor.html", include_in_schema=False)
def advisor_alias():
    return RedirectResponse("/", status_code=302)
