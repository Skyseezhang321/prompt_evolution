# Prompt 优化建议助手（对话式 · 扎根 LLM + 确定性兜底）

面向用户的、**扎根本仓库证据分级知识库**的 prompt 优化建议**对话助手**。聊天形式描述你的场景（任务类型、有无评测集、单/多 agent…），系统挑出适用的洞见，给出**分层、具体、可追溯到出处**的建议。

这是 [跨渠道综合报告 v4](../docs/analysis_report_v4_20260611.html) 从「文档」走向「能用」的落地（v3 已冻结，洞见 01–12 两版同源同编号，13/14 为 v4 新增）。

## 两种运行形态（同一套前端、同一份知识库）

| 形态 | 怎么跑 | 智能来源 | 依赖 |
|---|---|---|---|
| **确定性内核（v1）** | 直接打开 `advisor.html` | 引导问答 + 触发规则映射；自由追问为关键词匹配（中文 bigram） | 无（静态、免费、零幻觉、100% 可追溯） |
| **扎根 LLM 问答（v2）** | 起 FastAPI 后端，浏览器开 `http://localhost:8000/` | 自由文本任意提问 → 后端检索知识库 → OpenRouter 作答，**强制引用洞见编号 + 证据等级、不编造** | `.env` 里的 OpenRouter key + `fastapi/uvicorn` |

前端启动时探测 `api/health`：**后端在且 key 就绪 → 自动切「LLM 模式」**；否则回退确定性模式（LLM 调用失败也自动回退关键词匹配）。无论哪种形态，回答底部都附**「可追溯到的知识库条目」**，可追溯性不依赖模型自觉。

### 单入口三栏控制台

页面是一个三栏布局，一个入口看全部内容：**左**＝知识库导览（文档/报告链接 + 分渠道详细报告（arXiv/GitHub/其它平台/Twitter/知乎，与主报告 v4 证据金字塔同口径）+ 14 洞见分组（A–G）+ 反模式 + 首批实验，点条目→右侧看详情）；**中**＝对话；**右**＝详情面板（默认证据等级图例 + 诚实声明；点左侧条目显示其全文卡；每次回答后显示「本轮回答引用的来源」，可点洞见再展开）。窄屏（<1180/<860）左右面板收为抽屉，由顶栏「📚 知识库 / 📄 详情」按钮唤出。

### 与阅读 skill 的集成（方案 A+B）

三个阅读 skill（`read-paper` / `github-repo-audit` / `article-deep-read`）是知识库的**内容供应链**——它们把论文/仓库/文章读成带证据等级的笔记。问答**检索它们的产出，而不是运行时实时跑它们**（实时跑会破坏「只用 vetted 材料」的可追溯保证）：

- **A 扩检索语料**：LLM 模式下，除 14 条洞见外，后端还检索 `corpus_index.json`（43 篇笔记）作补充扎根，回答可引用如 `[paper-vista-reflection-dark-2026·A]`，保留证据等级与出处。
- **B 来源指引**：若洞见与笔记都未覆盖用户问到的具体来源，回答（及确定性模式的无命中提示）会建议用对应 skill 把它读进库。

新读了笔记后，跑 `python advisor/build_corpus.py && python advisor/build_vectors.py` 重建语料与向量即可被问答检索到。

### 召回方式：向量优先，关键词兜底

LLM 模式下后端默认用**语义向量召回**（`baai/bge-m3` via OpenRouter）：查询嵌入一次 → 与 `vector_index.json` 的 57 条归一化向量做余弦 → 取 top 洞见 + top 笔记（笔记设相似度下限 `ADVISOR_NOTE_FLOOR`，默认 0.30）。能命中关键词漏掉的语义相关项（如「死记硬背、泛化变差」→ 洞见06 过拟合）。**无向量索引或运行时嵌入失败 → 自动回退 bigram 关键词召回**；确定性（file://）模式始终用关键词。`/api/health` 的 `retrieval` 字段标明当前用的是 `vector` 还是 `keyword`。

> 设计取舍与目标架构（扎根 LLM + 确定性兜底、先引导后自由、确定性内核先上线再叠 LLM）记录在项目记忆与 [CHANGELOG](../CHANGELOG.md)。

## 文件

| 文件 | 作用 |
|---|---|
| `knowledge_base.json` | **单一事实来源**：14 条洞见（含触发规则、证据等级、演示性上手示例、真实数字与出处）、9 个引导问题、反模式表、首批实验。忠实摘自 v4 报告（01–12 与读者向洞见手册同源，13/14 为 v4 新增）。 |
| `build_advisor.py` | 读 KB → 校验 → 把 KB 内联进自包含 `advisor.html`。 |
| `advisor.html` | **生成产物**（勿手改）。对话式聊天页，可双击打开（确定性）或经后端托管（LLM 模式）。 |
| `server.py` | **FastAPI 后端**（v2）。复用 `scripts/llm_clients.py` 调 OpenRouter；对知识库做检索增强、构造受约束系统提示；同源托管 `advisor.html` 与 `/api/chat`、`/api/chat/stream`（SSE 流式）、`/api/health`。 |
| `requirements.txt` | 后端依赖（`fastapi`、`uvicorn`）。 |
| `build_corpus.py` | 扫描阅读 skill 产出的 vetted 笔记（`docs/paper_notes/` A、`docs/github_repo_audit_notes/` B、`docs/industry_notes/` 取自标证据等级）→ 生成 `corpus_index.json`。 |
| `corpus_index.json` | **生成产物**（勿手改）。LLM 模式的补充检索语料：每篇笔记的 id/类型/证据等级/一句话摘要/出处路径。 |
| `build_vectors.py` | 把 14 洞见 + 43 笔记用 `baai/bge-m3`（OpenRouter）嵌入、L2 归一化 → 生成 `vector_index.json`，供语义向量召回。 |
| `vector_index.json` | **生成产物**（勿手改）。57 条归一化向量（1024 维）+ 模型名；查询时嵌入一次问题做余弦排序。 |
| `test_advisor.py` | KB 完整性 + 出处文件存在 + 触发 DSL 的 golden 场景测试。 |
| `test_server.py` | 后端检索 / 扎根提示构造 / 端点契约测试（LLM 调用打桩，不触网、不花钱）。 |

## 怎么用

```bash
# 1) 改知识库（唯一应手改的内容）→ 重新生成页面
python advisor/build_advisor.py
#    读了新笔记 → 重建 LLM 模式的补充检索语料 + 向量索引（向量步骤需 OpenRouter key）
python advisor/build_corpus.py
python advisor/build_vectors.py

# 2) 跑测试（改 KB / 逻辑 / 后端后必跑）
python -m pytest advisor/ -q

# 3a) 确定性形态：直接浏览器打开 advisor/advisor.html

# 3b) 扎根 LLM 形态：装依赖、起后端（key 读自仓库根 .env）
pip install -r advisor/requirements.txt
python -m uvicorn server:app --app-dir advisor --port 8000
#    然后浏览器打开 http://localhost:8000/
```

### 远程服务器部署

`advisor.html` / `corpus_index.json` / `vector_index.json` 都是已入库的生成产物，**服务器上不需要跑任何 build 脚本**，拉代码即可启动：

```bash
git clone https://github.com/Skyseezhang321/prompt_evolution.git && cd prompt_evolution
pip install -r advisor/requirements.txt
# 仓库根手工创建 .env（OPENROUTER_API_KEY=...、OPENROUTER_MODEL=...；key 绝不入库）
python -m uvicorn server:app --app-dir advisor --host 0.0.0.0 --port 8784   # 端口自定

# 部署后验证
curl http://localhost:8784/api/health
#    预期 insights=14、corpus=43、retrieval=vector、llm_available=true
#    llm_available=false → 仓库根缺 .env，服务可跑但前端回退确定性模式
```

- **Python 版本**：≥3.8（3.8 兼容问题已于 2026-06-12 修复——pydantic 模型注解不能用内置泛型 `list[dict]`，新增模型字段请沿用 `typing.List/Dict` 写法）；3.8 已 EOL，长期建议 3.9+。
- **常驻运行**：生产环境建议 systemd / nohup 托管（崩溃自动拉起），不要裸前台进程。
- **公网暴露**：`/api/chat` 会消耗 OpenRouter 余额，公开部署务必加访问控制（nginx 反代 + 鉴权），避免 key 被刷。

LLM 形态调参（可选，不改 `.env` 全局值）：`ADVISOR_MAX_TOKENS`（默认 1600，推理模型需要较大输出预算）。模型由 `.env` 的 `OPENROUTER_MODEL` 决定。

> **运维注意**：后端在**启动期**加载知识库 / 语料 / 向量索引——改了 KB、后端代码或重建索引后必须**重启后端**，否则旧进程会一直用旧知识库继续服务（曾出现残留进程带着 12 条洞见的旧 KB 跑了一天）。核对方法：`GET /api/health` 的 `insights`（当前应为 14）与 `corpus`（43）。另外 LLM 模式只在**经后端访问**（如 `http://localhost:8000/`）时激活；双击打开 `advisor.html`（file://）永远是确定性模式。

## 怎么加 / 改一条洞见

只动 `knowledge_base.json`：

1. 在 `insights[]` 加一条，字段见已有条目（必填：`id/group/title/hook/evidence_level/triggers/diagnosis/steps/example/evidence/boundary/sources`）。
2. `triggers` 用触发 DSL（见下）把它绑定到引导问题的某些答案。
3. `evidence[].source` 与 `sources[]` 必须指向**真实存在**的仓库文档（测试会校验）。
4. 数字一律标 `level`（`A` / `B` / `C` / `D` / `recent-preprint`），不得把论文数字写成本项目结论。
5. `example` 是**演示性上手示例**（贴场景的 prompt 片段 / 字段表 / before-after，`\n` 换行）：文案里必须带「演示」字样（测试会校验），演示数字不得与证据混写；确定性模式渲染成卡片第 ③ 层，LLM 模式作为改写素材进系统提示。
6. `python advisor/build_advisor.py && python -m pytest advisor/test_advisor.py -q`。

### 触发 DSL（JS 运行时与 Python 测试同口径）

```jsonc
{ "q": "task_type", "eq": "toolcall" }          // 等于
{ "q": "task_type", "in": ["extract","classify"] } // 属于
{ "any": [ <cond>, <cond> ] }                    // 任一为真
{ "all": [ <cond>, <cond> ] }                    // 全为真
```

一条洞见的 `triggers` 是条件数组，**任一**条件为真即命中。`spine: true` 的洞见是「通用纪律」，无论场景都会在结果里兜底展示。

## 怎么评测「建议好不好」

`test_advisor.py` 里的 `GOLDEN` 是一组 **场景 → 必须命中的洞见** 的黄金用例（如：多 agent 必含 I08/I11；prompt 变长必含 I06；无评测集必含 I01）。新增/调整洞见或触发规则时，先在这里补用例，保证系统在已知场景上**该说的没漏、不编造知识库里没有的结论**。这是把「建议质量」变成可回归测试的最小手段。

## 路线

- **v1**：对话式 UI + 确定性内核。✅
- **v2**：扎根 LLM 问答 + FastAPI 后端。✅ 已用 `deepseek/deepseek-v4-pro` 实跑验证：回答按场景引用洞见编号与证据等级、对知识库未覆盖处如实声明、口径诚实（论文数字=该论文设置下成立、12 洞见尚未在本项目复现）。
- **v2.1 阅读 skill 集成（A+B）**：✅ LLM 模式检索扩到 42 篇 vetted 笔记，回答可引用一手论文/仓库笔记；未覆盖来源时指引用对应 skill 入库。实跑验证（问 VISTA）回答同时引用 `[I04·recent-preprint]` 与 `[paper-vista-reflection-dark-2026·A]`。
- **v2.2 流式输出（SSE）**：✅ `/api/chat/stream` 用 SSE 推 `meta`(引用)→ `delta`(文本片段)→ `done`/`error`；前端 `fetch` 流式读取，逐字渲染 + 闪烁光标，结束后补引用区；失败/不支持时回退关键词匹配。底层新增 `scripts/llm_clients.stream_openrouter_chat` 生成器（复用现有 config/header）。实跑：单次回答 795 个片段、3083 字逐步到达。注意：推理模型（deepseek-v4-pro）首片前有 ~10s+ 推理停顿，由打字指示器覆盖。
- **v2.3 向量召回**：✅ `baai/bge-m3`（OpenRouter）语义召回替代关键词，离线 `build_vectors.py` 建索引、查询时余弦排序，向量不可用自动回退关键词。新增 `scripts/llm_clients.embed_openrouter`。
- **下一步候选**：① 把「建议质量」评测做成离线集（场景→是否只引用 vetted 材料、是否带未覆盖声明），让 LLM 回答也能回归测试；② 混合召回（向量 + 关键词加权）与召回质量评测；③ 多轮记忆裁剪与成本/延迟观测；④ 可选关闭推理（更快首字）或换更快模型。
