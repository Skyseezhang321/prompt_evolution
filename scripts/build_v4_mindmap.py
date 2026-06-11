# -*- coding: utf-8 -*-
"""Generate the v4 panoramic mind-map SVG and inject it into the v4 report.

Why this script exists: the v3 report's inline mind-map SVG was produced by a
layout script that never entered the repo, so the map could not be regenerated
when the structure changed (flagged in CHANGELOG as 遗留待拍板 item 4). This
script fixes that for v4: the map content lives in BRANCHES below as plain
data; rerun the script after any structural change and the SVG between the
V4MINDMAP markers in docs/analysis_report_v4_20260611.html is rebuilt.

Usage:  python scripts/build_v4_mindmap.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "docs" / "analysis_report_v4_20260611.html"
BEGIN, END = "<!-- V4MINDMAP:BEGIN -->", "<!-- V4MINDMAP:END -->"

TITLE = "Prompt 优化与自进化 · v4 全景脑图（四层知识体系）"
SUBTITLE = ("一句话总论：自动优化 prompt 是「先判断值不值得 → 选对方法与部件 → 失败变可编辑证据 → "
            "多候选 + 验证集筛选 → 带版本与回滚地运营」的工程纪律，不是让模型润色一遍。")
ROOT_LINES = ["Prompt 优化", "与自进化"]
ROOT_SUB = "v4 · 四层知识体系"

# (branch label, accent color, leaf fill, [leaf texts])
BRANCHES = [
    ("证据底座 · 5 个渠道", "#2d67ad", "#e9f0fb", [
        "arXiv · A：方法机制 + 效应数字（37 篇深读笔记）",
        "GitHub · B：工程结构 / 治理（core4 已审，正典 5 仓待审）",
        "其它平台 · B：生产工具闭环 / 治理是前提",
        "Twitter/X · B*：采纳信号 / 研究→工具映射（追溯 pending）",
        "知乎 · D：社区理解 / 误区集中点（线索非证据）",
    ]),
    ("第 1 层 · 方法地图（怎么选）", "#257d72", "#e8f3ee", [
        "七法主线：APE→ProTeGi→OPRO→DSPy→TextGrad→MIPROv2→GEPA",
        "暗线一：反馈信息密度 标量→批评→轨迹（决定样本效率）",
        "暗线二：优化对象升维 单指令→指令+示例→多模块程序",
        "六法同框：仅结构化任务全胜；跨模型脆弱（Haiku→Nova 崩盘）",
        "选型六问 + 7 方法簇；打不过 APE/OPRO 下限就别上复杂方法",
    ]),
    ("第 2 层 · 工作流洞见 14 条（怎么做）", "#665bb4", "#eceaf6", [
        "A 值不值得：01 headroom 体检 · 02 选客观打分任务",
        "B 从失败学：03 失败变可编辑证据 · 04 先列根因假设",
        "C 别被骗：05 多候选+验证集 · 06 卫生门防膨胀",
        "D 改什么：07 示例优先 · 08 标清部件 · 09 工具 schema",
        "E 记忆/多 agent：10 过滤记忆 · 11 credit assignment",
        "F 听来的：12 社媒 / 二手 = 线索，不是证据",
        "G 新增：13 零成本结构变换 · 14 optimizer/judge 版本化",
    ]),
    ("第 3 层 · 工程落地（怎么运营）", "#af6b08", "#fbf0dc", [
        "五件套：prompt + dataset + metric + trace + constraints",
        "工具三阶段：Promptfoo → Langfuse/LangSmith → OPIK/Arize",
        "研究→工具映射：GEPA / DSPy / versioning / 产品化 APO",
        "发布门与账本：frozen evaluator · 回滚点 · optimizer/judge 入账",
    ]),
    ("第 4 层 · 误区与边界（怎么不被骗）", "#b44a5c", "#fbe8ed", [
        "12 个误区：GEPA≠替代 RL · DSPy≠自动改写 · 梯度是比喻…",
        "反模式 9 条：reward hacking · 无界记忆 · 只看平均分…",
        "刻意边界：soft prompt / multimodal / 完整 context 系统不做",
        "frontier 缺口：bi-level（最优先）· online · constrained",
    ]),
    ("可复用方法（HM）", "#4f7e33", "#eaf1e3", [
        "HM-01 体检门（+洞见 13 零成本对照）",
        "HM-02 Trace-First 批评改写（失败多时用代码聚合）",
        "HM-03 示例优化基线（MIPROv2 分诊规则）",
        "HM-04 Artifact 账本（optimizer / judge 也入账）",
        "HM-05 候选 Context-First 诊断 + 线索分流（I-12）",
    ]),
    ("首批最小验证 P0–P2", "#46525f", "#eceef1", [
        "P0：零成本三臂 A/B · 优化前体检 · 示例 vs 指令",
        "P1：根因假设改写 · 卫生门",
        "P2：工具 schema · 过滤记忆",
    ]),
]

# 几何参数与 v3 脑图同口径
W = 1190
Y0, PITCH, LEAF_H = 139.0, 41.0, 30
LEAF_X, LEAF_W = 542, 630
BR_X, BR_W, BR_H = 262, 250, 34
ROOT_X, ROOT_W, ROOT_H = 18, 214, 96


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg() -> str:
    leaves, branches = [], []  # (y, fill, color, text) / (cy, color, label)
    y = Y0
    for label, color, fill, items in BRANCHES:
        first = y
        for t in items:
            leaves.append((y, fill, color, t))
            y += PITCH
        last = y - PITCH
        branches.append(((first + last) / 2 + LEAF_H / 2, color, label))
    height = int(leaves[-1][0] + LEAF_H + 25)
    root_cy = (leaves[0][0] + leaves[-1][0] + LEAF_H) / 2

    p = []
    p.append(
        f'<svg viewBox="0 0 {W} {height}" xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-label="Prompt 优化与自进化 v4 全景脑图" '
        f'font-family="Microsoft YaHei, PingFang SC, Segoe UI, Arial, sans-serif" '
        f'style="width:100%;height:auto;display:block">')
    p.append(f'<rect x="0" y="0" width="{W}" height="{height}" fill="#ffffff"/>')
    p.append(f'<text x="18" y="36" font-size="21" font-weight="760" fill="#202329">{esc(TITLE)}</text>')
    p.append(f'<text x="18" y="62" font-size="13.5" fill="#626b74">{esc(SUBTITLE)}</text>')

    for cy, color, _ in branches:  # root → branch connectors
        p.append(f'<path d="M{ROOT_X + ROOT_W},{root_cy} C247,{root_cy} 247,{cy} {BR_X},{cy}" '
                 f'fill="none" stroke="{color}" stroke-width="2" opacity="0.55"/>')
    bi = 0
    for label, color, fill, items in BRANCHES:  # branch → leaf connectors
        cy = branches[bi][0]
        for j in range(len(items)):
            ly = leaves[sum(len(b[3]) for b in BRANCHES[:bi]) + j][0] + LEAF_H / 2
            p.append(f'<path d="M{BR_X + BR_W},{cy} C527,{cy} 527,{ly} {LEAF_X},{ly}" '
                     f'fill="none" stroke="{color}" stroke-width="1.4" opacity="0.42"/>')
        bi += 1

    p.append(f'<rect x="{ROOT_X}" y="{root_cy - ROOT_H / 2}" width="{ROOT_W}" height="{ROOT_H}" rx="10" fill="#202329"/>')
    cx = ROOT_X + ROOT_W / 2
    p.append(f'<text x="{cx}" y="{root_cy - 20}" text-anchor="middle" font-size="16" font-weight="760" fill="#ffffff">{esc(ROOT_LINES[0])}</text>')
    p.append(f'<text x="{cx}" y="{root_cy + 2}" text-anchor="middle" font-size="16" font-weight="760" fill="#ffffff">{esc(ROOT_LINES[1])}</text>')
    p.append(f'<text x="{cx}" y="{root_cy + 26}" text-anchor="middle" font-size="11.5" fill="#cdd3da">{esc(ROOT_SUB)}</text>')

    for cy, color, label in branches:
        p.append(f'<rect x="{BR_X}" y="{cy - BR_H / 2}" width="{BR_W}" height="{BR_H}" rx="7" fill="{color}"/>')
        p.append(f'<text x="{BR_X + BR_W / 2}" y="{cy + 4.5}" text-anchor="middle" font-size="13.5" '
                 f'font-weight="700" fill="#ffffff">{esc(label)}</text>')

    for ly, fill, color, text in leaves:
        p.append(f'<rect x="{LEAF_X}" y="{ly}" width="{LEAF_W}" height="{LEAF_H}" rx="6" fill="{fill}" '
                 f'stroke="{color}" stroke-width="1" stroke-opacity="0.5"/>')
        p.append(f'<rect x="{LEAF_X}" y="{ly}" width="4" height="{LEAF_H}" rx="2" fill="{color}"/>')
        p.append(f'<text x="{LEAF_X + 14}" y="{ly + 19.5}" font-size="12.5" fill="#2a2f36">{esc(text)}</text>')

    p.append("</svg>")
    return "\n".join(p)


def main():
    html = REPORT.read_text(encoding="utf-8")
    i, j = html.index(BEGIN), html.index(END)
    out = html[: i + len(BEGIN)] + "\n" + build_svg() + "\n" + html[j:]
    REPORT.write_text(out, encoding="utf-8")
    n_leaves = sum(len(b[3]) for b in BRANCHES)
    print(f"已注入 v4 全景脑图：{len(BRANCHES)} 个分支 / {n_leaves} 个叶节点 → {REPORT}")


if __name__ == "__main__":
    main()
