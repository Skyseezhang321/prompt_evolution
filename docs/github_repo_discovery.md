# GitHub 仓库发现脚本

本页记录 GitHub 渠道的第一轮自动化搜集方式。目标是尽可能多地发现与 prompt optimization、prompt self-evolution、eval-driven prompt iteration、prompt management 和 agent/context prompt optimization 相关的候选仓库。

## 搜索策略

- 使用 GitHub 官方 REST Search API，不爬取 HTML 页面。
- 搜索范围覆盖 `name`、`description`、`readme`，并按 stars、forks、更新时间等元数据辅助排序。
- 内置查询词覆盖 automatic prompt optimization、PromptBreeder、OPRO、ProTeGi、TextGrad、DSPy/MIPRO、GEPA、prompt eval、prompt management、context engineering、agent prompt optimization 等方向。
- 输出结果只表示候选线索。任何仓库进入 `docs/source_inventory.md`、行业笔记或结论前，都必须人工快筛并记录证据来源。

## 运行方式

建议在本地 `.env` 中配置 `GITHUB_TOKEN` 或 `GH_TOKEN`，否则 GitHub Search API 的匿名 rate limit 很低。

```bash
python scripts/github_repo_discovery.py --max-pages 2 --per-page 100 --min-score 8
```

快速验证可限制查询数量：

```bash
python scripts/github_repo_discovery.py --query-limit 8 --max-pages 1 --per-page 30 --sleep-seconds 0
```

查看查询计划但不访问网络：

```bash
python scripts/github_repo_discovery.py --dry-run
```

## 输出文件

默认输出到本地忽略目录：

```text
local_sources/raw/github_repo_discovery/
```

每次运行生成三个文件：

- `.json`：完整候选仓库、查询元数据、错误记录和 SHA256 可追踪信息。
- `.csv`：便于人工快筛的表格。
- `.md`：按相关性分数排序的摘要报告。

这些文件不提交到 git。若某个候选仓库通过人工快筛，再把单个来源登记到 `docs/source_inventory.md`，必要时固定 commit、release 或文档版本。

## 字段口径

脚本会为每个仓库生成以下研究字段：

- `status`: 初始为 `candidate`。
- `novelty_status`: 初始为 `unknown`。
- `method_category`: 自动分类，供快筛使用，不作为结论。
- `optimization_object`: 粗略判断优化对象，如 `prompt_text`、`system_prompt`、`agent_prompt_or_tool_policy`。
- `feedback_signal`: 粗略判断反馈来源，如 metric/test、LLM feedback、human feedback。
- `selection_method`: 粗略判断候选选择方式，如 search、evolutionary、optimizer。
- `relevance_score`: 基于关键词、已知方法名、stars/forks、fork/archive 状态的轻量评分。

## 最近验证运行

2026-06-08 运行了一次无 token 的受限验证批次：

```bash
python scripts/github_repo_discovery.py --query-limit 8 --max-pages 1 --per-page 30 --sleep-seconds 0 --run-id github_repo_discovery_validation_20260608_v4
```

结果：

- 原始结果：240 条。
- 去重仓库：85 个。
- 高分保留：6 个，`min_score=8.0`。
- API 错误：0 个。
- JSON 路径：`local_sources/raw/github_repo_discovery/github_repo_discovery_validation_20260608_v4.json`。
- CSV 路径：`local_sources/raw/github_repo_discovery/github_repo_discovery_validation_20260608_v4.csv`。
- Markdown 路径：`local_sources/raw/github_repo_discovery/github_repo_discovery_validation_20260608_v4.md`。
- JSON SHA256：`23f49c1ff390f2bec3f247e2443f4a52c4d49160851abd18c14b21ae0053e33b`。

已知限制：

- GitHub Search 可以匹配 README，但 Search API 返回的仓库结果不包含 README 命中片段；脚本当前只用仓库名、描述、语言和 topics 打分，因此会把“只在 README 中相关”的仓库降为低优先级。
- 未配置 token 时 rate limit 很低；完整批量搜集应配置 `GITHUB_TOKEN`，并提高 `--max-pages` 与 `--per-page`。
- 高分候选适合优先深读；完整 JSON 中的 `all_unique_repositories` 和完整 CSV 适合人工补扫，不应直接作为研究结论。

本批次的人工快筛见 [GitHub 仓库候选快筛：2026-06-08](github_repo_triage_20260608.md)。
