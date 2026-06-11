# -*- coding: utf-8 -*-
"""Tests for the FastAPI LLM backend (advisor/server.py).

不触网、不花钱：LLM 调用被 monkeypatch 打桩；只验证检索、扎根提示构造与端点契约。
Run:  python -m pytest advisor/test_server.py -q
"""
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))  # 让 `import server` 生效
# 测试用占位 key，避免依赖真实 .env / 触网（resolve 需要非空 key）
os.environ.setdefault("OPENROUTER_API_KEY", "test-key")

import server  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

client = TestClient(server.app)


def _boom_embed(*args, **kwargs):
    raise server.llm.LLMRequestError("test: no network embeddings")


@pytest.fixture(autouse=True)
def _no_network_embeddings(monkeypatch):
    """默认让向量召回的查询嵌入失败 → 回退关键词，保证测试不触网。

    需要真正测向量排序的用例在体内自行 monkeypatch 覆盖。
    """
    monkeypatch.setattr(server.llm, "embed_openrouter", _boom_embed)


def test_retrieve_toolcall_hits_I09():
    ids = [i["id"] for i in server.retrieve("我的工具调用老是填错参数怎么办")]
    assert "I09" in ids


def test_retrieve_multi_agent_hits_I11():
    ids = [i["id"] for i in server.retrieve("多个 agent 协作出错怎么定位责任")]
    assert "I11" in ids


def test_retrieve_pads_with_spine_when_vague():
    # 极泛问题命中少 → 用 spine（通用纪律）兜底，保证 LLM 有底座
    got = server.retrieve("你好")
    assert len(got) >= 3


def test_system_prompt_has_constraints():
    sp = server.build_system_prompt(server.retrieve("多个 agent 出错怎么定位"))
    assert "只能依据" in sp           # 扎根约束
    assert "证据等级" in sp           # 引用要求
    assert "该论文设置下成立" in sp    # 诚实口径
    assert "I11" in sp                # 相关洞见进了上下文
    assert "read-paper" in sp         # 方案 B：未覆盖来源指引


def test_corpus_loaded():
    # build_corpus.py 应已生成语料；论文笔记是主力
    assert len(server.CORPUS) >= 10
    assert any(d["type"] == "paper" for d in server.CORPUS)


def test_retrieve_corpus_hits_relevant_note():
    ids = [d["id"] for d in server.retrieve_corpus("coin flip 优化是抛硬币")]
    assert any("coin-flip" in i for i in ids)


def test_system_prompt_includes_notes_block():
    notes = server.retrieve_corpus("memory 记忆优化")
    sp = server.build_system_prompt(server.retrieve("记忆"), notes)
    if notes:  # 命中笔记时应出现「相关一手笔记」块且带来源 id
        assert "相关一手笔记" in sp
        assert notes[0]["id"] in sp


def test_build_messages_shape():
    msgs = server.build_messages("怎么防止过拟合", [{"role": "user", "content": "上一句"}],
                                 server.retrieve("过拟合"), context="task_type=信息抽取")
    assert msgs[0]["role"] == "system"
    assert msgs[-1]["role"] == "user"
    assert "已知场景" in msgs[-1]["content"]


def test_health():
    d = client.get("/api/health").json()
    assert d["ok"] and d["insights"] == len(server.INSIGHTS)
    assert d["retrieval"] in ("vector", "keyword")


def test_vector_index_loaded():
    assert len(server.VECTORS) >= 50          # 14 洞见 + 43 笔记
    assert server.VECTOR_MODEL                 # 如 baai/bge-m3


def test_retrieve_vector_ranks_by_cosine(monkeypatch):
    monkeypatch.setattr(server, "VECTORS", [
        {"id": "I06", "kind": "insight", "vec": [1.0, 0.0]},
        {"id": "I11", "kind": "insight", "vec": [0.0, 1.0]},
        {"id": "paper-x", "kind": "note", "vec": [0.9, 0.1]},
    ])
    monkeypatch.setattr(server, "INSIGHT_BY_ID", {"I06": {"id": "I06"}, "I11": {"id": "I11"}})
    monkeypatch.setattr(server, "NOTE_BY_ID", {"paper-x": {"id": "paper-x"}})
    monkeypatch.setattr(server, "NOTE_SIM_FLOOR", 0.0)
    # 查询向量贴近 [1,0] → I06 排第一；笔记 paper-x 余弦 0.9 入选
    monkeypatch.setattr(server.llm, "embed_openrouter", lambda *a, **k: [[2.0, 0.0]])
    ins, notes = server.retrieve_vector("x")
    assert ins[0]["id"] == "I06"
    assert any(n["id"] == "paper-x" for n in notes)


def test_retrieve_grounding_falls_back_to_keyword_on_embed_error():
    # autouse fixture 已让 embed 失败 → 回退关键词，仍应命中 I09
    ins, _ = server.retrieve_grounding("我的工具调用老是填错参数")
    assert "I09" in [i["id"] for i in ins]


def test_chat_grounded_stub(monkeypatch):
    seen = {}

    def stub(messages=None, config=None, **kw):
        seen["messages"] = messages
        return {"choices": [{"message": {"content": "先做优化前体检 [I01·A]"}}]}

    monkeypatch.setattr(server.llm, "call_openrouter_chat", stub)
    d = client.post("/api/chat", json={"message": "coin flip 论文说优化没有评测集能直接做吗"}).json()
    assert d["ok"] is True
    assert "I01" in d["answer"]
    assert d["cited"]                                   # 返回可追溯引用
    assert any("知识库片段" in m["content"] for m in seen["messages"])  # 确实扎根了
    # cited 应同时含洞见(I..)与一手笔记(paper-/repo-/practice-)
    assert any(c["id"].startswith("I") for c in d["cited"])
    assert any(c["id"].startswith(("paper-", "repo-", "practice-")) for c in d["cited"])


def test_chat_stream_emits_meta_delta_done(monkeypatch):
    def stub_stream(messages, config=None, model=None):
        assert any("知识库片段" in m["content"] for m in messages)  # 流式也扎根
        yield "先做"
        yield "体检 [I01·A]"

    monkeypatch.setattr(server.llm, "stream_openrouter_chat", stub_stream)
    body = client.post("/api/chat/stream",
                       json={"message": "没有评测集能直接优化吗"}).text
    assert "event: meta" in body
    assert "event: delta" in body
    assert "event: done" in body
    assert "I01" in body            # 文本片段确实流出
    assert '"cited"' in body        # meta 带引用清单


def test_chat_stream_emits_error_on_failure(monkeypatch):
    def boom(messages, config=None, model=None):
        raise server.llm.LLMRequestError("HTTP 400: bad model")
        yield  # pragma: no cover  (使其成为生成器)

    monkeypatch.setattr(server.llm, "stream_openrouter_chat", boom)
    body = client.post("/api/chat/stream", json={"message": "工具调用出错"}).text
    assert "event: error" in body
    assert "request_failed" in body


def test_chat_handles_llm_failure(monkeypatch):
    def boom(messages=None, config=None, **kw):
        raise server.llm.LLMRequestError("HTTP 400: bad model")

    monkeypatch.setattr(server.llm, "call_openrouter_chat", boom)
    d = client.post("/api/chat", json={"message": "工具调用出错"}).json()
    assert d["ok"] is False and d["code"] == "request_failed"
    assert d["cited"]  # 失败也带回引用，前端可回退展示


def test_chat_empty_message():
    r = client.post("/api/chat", json={"message": "   "})
    assert r.status_code == 400


def test_advisor_alias_serves_chat_page():
    """文档页「💬 对话助手主页」的相对链接（../advisor/advisor.html）在后端托管时可达。"""
    r = client.get("/advisor/advisor.html")
    assert r.status_code == 200
    assert "Prompt 优化建议助手" in r.text


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
