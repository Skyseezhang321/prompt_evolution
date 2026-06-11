# Prompt 优化与自进化 · 跨渠道全景脑图（Mermaid 源）

日期：2026-06-10（2026-06-11 按主报告 v4 结构更新：新增 G 组与洞见 13/14 节点，A–F 未动）

本文件最初是 [`analysis_report_v3_20260610.html`](./analysis_report_v3_20260610.html) 内嵌 SVG 脑图的**可编辑文本版**，现已按 [`analysis_report_v4_20260611.html`](./analysis_report_v4_20260611.html) 的 14 洞见结构更新（v3 内嵌 SVG 仍为 12 洞见旧结构，随 v3 一起冻结）。Mermaid 在 GitHub / 多数 Markdown 预览器中可直接渲染；改这里即可重排脑图，再按需重绘 SVG。

一句话总论：自动优化 prompt 是「先判断值不值得 → 把失败变成可编辑证据 → 多候选 + 验证集筛选 → 可回滚」的**工程纪律**，不是让模型把 prompt 润色一遍。

---

## 1. 全景脑图（mindmap）

```mermaid
mindmap
  root((Prompt 优化<br/>与自进化<br/>工程纪律))
    证据底座 · 5 渠道
      arXiv · A：机制 + 效应数字（31+ 深读）
      GitHub · B：工程结构 / 治理（core4）
      其它平台 · B：生产工具 / 可观测闭环
      Twitter/X · B*：采纳信号 / 去炒作（待验证）
      知乎 · D：社区理解 / 误区（线索非证据）
    A 值不值得优化
      洞见01 先体检 headroom vs noise floor
      洞见02 首批选能客观打分的任务
    B 从失败里学
      洞见03 把失败变成可编辑证据
      洞见04 先列根因假设再改
    C 别被模型骗
      洞见05 多候选 + 验证集筛选
      洞见06 变长变复杂 ≈ 过拟合
    D 改哪个部件
      洞见07 示例选择是一等变量
      洞见08 标清 artifact（mutable/frozen）
      洞见09 工具调错改 schema
    E 记忆与多 agent
      洞见10 只用过滤后的记忆
      洞见11 多 agent 先做 credit assignment
    F 听来的方法
      洞见12 社媒/二手 = 线索非证据
    G 搜索之外 · v4 新增
      洞见13 先试零成本结构变换（整 prompt 重复 ×2）
      洞见14 optimizer/judge 也要版本化
    可复用方法 HM
      HM-01 Pre-Optimization Gate
      HM-02 Trace-First Critique Rewrite
      HM-03 Exemplar Optimization Baseline
      HM-04 Prompt Artifact Ledger
      Source Evidence Triage（I-12）
    反模式 / 风险防线
      只看平均分 / prompt 越改越长
      改 evaluator 或 test（reward hacking）
      raw memory 无界追加（跨任务污染）
      多 agent 出错就整体重写
      用社媒热度 / vendor % 当证据
      工具调用只改 system prompt
    覆盖、偏差与诚实边界
      GitHub 受限召回 + 正典 optimizer 待审
      其它平台 真实失败案例 / 事故复盘不足
      Twitter 候选追溯链待验证（pending）
      2026 新稿需独立复现（recent-preprint）
      本项目尚无 C 级实验证据
    首批最小验证 P0–P2
      P0 优化前体检（含洞见13 零成本变换对照） + 示例 vs 指令
      P1 直接改写 vs 根因假设 / 卫生门
      P2 工具 schema 优化 / 过滤记忆
```

---

## 2. 跨渠道证据金字塔（证据怎么叠起来）

越靠下越接近一手机制证据（最强、最可追溯），越靠上越偏传播信号。一条洞见越能被多层独立支撑越可信；上层单独不足以支撑强结论。

```mermaid
flowchart TB
  ZH["知乎 · D（线索）<br/>社区理解 / 误区集中点 / 问题框定"]
  TW["Twitter/X · B*（待验证）<br/>采纳信号 / 研究→工具映射 / 去炒作"]
  WEB["其它平台 web_search · B<br/>生产工具闭环 / 可观测治理"]
  GH["GitHub 源码 · B（部分 D）<br/>工程结构 / frozen evaluator / artifact ledger"]
  ARX["arXiv 论文 · A（地基）<br/>方法机制 / 消融 / 效应数字"]

  ZH --> TW --> WEB --> GH --> ARX
  classDef d fill:#fbe8ed,stroke:#b44a5c,color:#202329;
  classDef b fill:#e9f0fb,stroke:#2d67ad,color:#202329;
  classDef bb fill:#fbf0dc,stroke:#af6b08,color:#202329;
  classDef gg fill:#eaf1e3,stroke:#4f7e33,color:#202329;
  classDef a fill:#e8f3ee,stroke:#257d72,color:#202329;
  class ZH d; class TW b; class WEB bb; class GH gg; class ARX a;
```

---

## 3. 工程纪律闭环（一条 prompt 优化运行的最小骨架）

```mermaid
flowchart LR
  A["① 优化前体检<br/>headroom vs noise floor<br/>(HM-01)"] -->|有空间| B["② 失败变可编辑证据<br/>error_type + critique + trace<br/>(HM-02)"]
  A -->|无空间| STOP["止损：回到任务定义 / eval"]
  B --> C["③ 列根因假设<br/>2–3 个互斥假设"]
  C --> D["④ 多候选生成<br/>每假设一候选"]
  D --> E["⑤ 验证集筛选<br/>dev + 格式错 + 长度<br/>Pareto + best_seen"]
  E --> F{"⑥ 卫生门<br/>膨胀 / 过拟合 / 污染?"}
  F -->|通过| G["⑦ 记入 artifact ledger<br/>mutable/frozen + 回滚点<br/>(HM-04)"]
  F -->|不通过| D
  G -->|回滚| E
  G --> H["⑧ 上线 + 可观测<br/>regression / critical-failure set"]
```

---

## 维护说明

- 全景脑图已按 v4 报告（③ 工作流洞见 A–G 共 14 条）口径组织；证据金字塔与工程纪律闭环两图与 v3/v4 同口径未变。改动后请同步报告对应小节。
- 节点文案应与 [`insight_method_catalog_20260609.md`](./insight_method_catalog_20260609.md) 的 I-01..I-14 / HM-01..04 / C-01..06 命名保持一致，避免「各说各话」。
- 内嵌 SVG 由一次性布局脚本生成；如需重绘，按本文件结构重排节点即可。
