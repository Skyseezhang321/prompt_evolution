# -*- coding: utf-8 -*-
"""Tests for the prompt-advice knowledge base and trigger logic.

Run:  python -m pytest advisor/test_advisor.py -q
   or python advisor/test_advisor.py   (falls back to a tiny runner)

Covers, per CLAUDE.md「每个结论必须有证据 / 修改 Python 代码时运行相关测试」:
  - KB structural integrity (required fields, valid evidence levels).
  - Every source / evidence path actually exists in the repo (traceability).
  - The trigger DSL is mirrored from build_advisor.py and matches golden scenarios.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
KB_PATH = os.path.join(HERE, "knowledge_base.json")

VALID_LEVELS = {"A", "B", "C", "D", "recent-preprint"}
REQUIRED_INSIGHT_FIELDS = [
    "id", "group", "title", "hook", "evidence_level",
    "triggers", "diagnosis", "steps", "evidence", "boundary", "sources",
]


def load_kb():
    with open(KB_PATH, encoding="utf-8") as f:
        return json.load(f)


KB = load_kb()
QIDS = {q["id"] for q in KB["questions"]}
OPT_IDS = {q["id"]: {o["id"] for o in q["options"]} for q in KB["questions"]}


# ---------- trigger DSL (must mirror build_advisor.py / advisor.html JS) ----------
def eval_cond(c, a):
    if "any" in c:
        return any(eval_cond(x, a) for x in c["any"])
    if "all" in c:
        return all(eval_cond(x, a) for x in c["all"])
    q = c.get("q")
    if q is None:
        return False
    v = a.get(q)
    if v is None:
        return False
    if "eq" in c:
        return v == c["eq"]
    if "in" in c:
        return v in c["in"]
    return False


def matched(ins, a):
    return any(eval_cond(t, a) for t in ins.get("triggers", []))


def hits(answers):
    return {i["id"] for i in KB["insights"] if matched(i, answers)}


# ---------- structural integrity ----------
def test_insight_ids_unique():
    ids = [i["id"] for i in KB["insights"]]
    assert len(ids) == len(set(ids)), "洞见 id 重复"


def test_required_fields_present():
    for ins in KB["insights"]:
        for f in REQUIRED_INSIGHT_FIELDS:
            assert ins.get(f) not in (None, "", []), f"{ins.get('id')} 缺字段 {f}"


def test_evidence_levels_valid():
    for ins in KB["insights"]:
        assert ins["evidence_level"] in VALID_LEVELS, f"{ins['id']} 等级非法"
        for ev in ins["evidence"]:
            assert ev["level"] in VALID_LEVELS, f"{ins['id']} evidence 等级非法"


def test_triggers_reference_known_questions_and_options():
    def leaves(conds):
        out = []
        for c in conds:
            if "any" in c:
                out += leaves(c["any"])
            elif "all" in c:
                out += leaves(c["all"])
            elif "q" in c:
                out.append(c)
        return out

    for ins in KB["insights"]:
        for c in leaves(ins["triggers"]):
            assert c["q"] in QIDS, f"{ins['id']} 触发引用未知问题 {c['q']}"
            vals = [c["eq"]] if "eq" in c else c.get("in", [])
            for v in vals:
                assert v in OPT_IDS[c["q"]], f"{ins['id']} 触发引用未知选项 {c['q']}={v}"


def test_all_source_paths_exist():
    """Traceability: every cited doc must really be in the repo."""
    missing = []
    for ins in KB["insights"]:
        paths = list(ins.get("sources", []))
        paths += [e["source"] for e in ins.get("evidence", []) if e.get("source")]
        for p in paths:
            # sources may carry an #anchor; strip it before checking the file
            fp = os.path.join(REPO, p.split("#", 1)[0])
            if not os.path.exists(fp):
                missing.append(f"{ins['id']} -> {p}")
    assert not missing, "引用的文档不存在:\n  " + "\n  ".join(missing)


def test_experiments_reference_real_insights():
    ids = {i["id"] for i in KB["insights"]}
    for e in KB["experiments"]:
        for iid in e["insights"]:
            assert iid in ids, f"实验 {e['priority']} 引用未知洞见 {iid}"


# ---------- golden scenarios: 场景 -> 必须命中的洞见 ----------
GOLDEN = [
    # (描述, answers, 必须包含的洞见)
    ("无评测集 + 想直接优化 -> 体检+失败证据+多候选",
     {"has_evalset": "no", "tried_autopolish": "planning_to"}, {"I01", "I03", "I05"}),
    ("开放写作 + 只能评委打分 -> 选任务",
     {"task_type": "open", "has_evalset": "judge_only"}, {"I02"}),
    ("prompt 越改越长 -> 防膨胀",
     {"prompt_growing": "yes"}, {"I06"}),
    ("多 agent -> credit assignment + 标部件",
     {"architecture": "multi_agent"}, {"I08", "I11"}),
    ("工具调用 -> 改 schema + 标部件",
     {"task_type": "toolcall"}, {"I08", "I09"}),
    ("无界记忆 -> 过滤记忆 + 标部件",
     {"uses_memory": "unbounded"}, {"I08", "I10"}),
    ("抽取 + 有客观评测集 -> 示例优化",
     {"task_type": "extract", "has_evalset": "yes_objective"}, {"I07"}),
    ("思路来自社媒 -> 线索分流",
     {"idea_source": "social"}, {"I12"}),
    ("优化后变差 -> 体检 + 根因假设",
     {"tried_autopolish": "got_worse"}, {"I01", "I04"}),
]


def test_golden_scenarios():
    for desc, ans, expect in GOLDEN:
        got = hits(ans)
        assert expect <= got, f"场景[{desc}] 期望命中 {expect}，实际 {got}（缺 {expect - got}）"


def test_exemplar_needs_both_conditions():
    """I07 用了 all：抽取任务但没有客观评测集时不应命中（避免误导）。"""
    assert "I07" not in hits({"task_type": "extract"})
    assert "I07" not in hits({"has_evalset": "yes_objective"})
    assert "I07" in hits({"task_type": "extract", "has_evalset": "yes_objective"})


def test_empty_answers_only_match_nothing_or_spine_safely():
    """没有任何回答时不应炸，且不强行命中（spine 由 UI 单独兜底展示）。"""
    assert hits({}) == set()


if __name__ == "__main__":
    # 轻量自跑：无 pytest 也能验证
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for fn in fns:
        fn()
        passed += 1
        print(f"  ok  {fn.__name__}")
    print(f"\n{passed}/{len(fns)} 通过")
