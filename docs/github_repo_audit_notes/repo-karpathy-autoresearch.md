# Source Audit: karpathy/autoresearch

本笔记是源码审计草稿，不是最终 insight。只能用于记录可追溯观察和后续核验问题。

## Source Fixation

- source_id: `repo-karpathy-autoresearch`
- repository: https://github.com/karpathy/autoresearch
- local_path: `local_sources\raw\github_repo_clones\repo-karpathy-autoresearch`
- commit_sha: `228791fb499afffb54b46200aca536f79142f117`
- branch: `master`
- generated_at: `2026-06-08T14:10:29+00:00`
- audit_json: `local_sources\raw\github_repo_audits\repo-karpathy-autoresearch\audit.json`
- audit_json_sha256: `0A8BE4593EEC80C258C47371B99FA0920C3D2EC6510D35CE3D73FDD03C05BFA3`

## Structure Signals

- total_files_seen: 10
- text_files_scanned: 5
- readme_files: README.md
- license_files: none
- package_files: pyproject.toml, uv.lock
- path_tag_counts: `{"versioning": 1}`
- content_tag_counts: `{"evaluation": 4, "iteration_loop": 3, "memory_context": 3, "agent_workflow": 1, "risk_failure": 1}`

## Evidence File Signals

### `.python-version`

- sha256: `2C6BB7B4A0CC70E45E866DC579BEC9F0B5C843C42FD6ED7391DF7F5CD7859F14`
- tags: versioning

### `README.md`

- sha256: `6D76890344339551005A5DC1FB56F70FC8963F74644F73D503387168ABA7A728`
- tags: agent_workflow, evaluation, iteration_loop
- excerpts:
  - L5: *One day, frontier AI research used to be done by meat computers in between eating, sleeping, having other fun, and synchronizing once in a while using sound wave interconnect in t
  - L7: The idea: give an AI agent a small but real LLM training setup and let it experiment autonomously overnight. It modifies the code, trains for 5 minutes, checks if the result improv
  - L13: - **`prepare.py`** — fixed constants, one-time data prep (downloads training data, trains a BPE tokenizer), and runtime utilities (dataloader, evaluation). Not modified.
  - L14: - **`train.py`** — the single file the agent edits. Contains the full GPT model, optimizer (Muon + AdamW), and training loop. Everything is fair game: architecture, hyperparameters
  - L15: - **`program.md`** — baseline instructions for one agent. Point your agent here and let it go. **This file is edited and iterated on by the human**.
  - L17: By design, training runs for a **fixed 5-minute time budget** (wall clock, excluding startup/compilation), regardless of the details of your compute. The metric is **val_bpb** (val
  - L42: ## Running the agent
  - L56: train.py — model, optimizer, training loop (agent modifies this)

### `prepare.py`

- sha256: `F3FF54F2271DF15144F0674A6234306E350004FC1AE3F9237AA176E6D3BA9944`
- tags: evaluation, memory_context
- excerpts:
  - L32: EVAL_TOKENS = 40 * 524288 # number of tokens for val eval
  - L184: # --- Build token_bytes lookup for BPB evaluation ---
  - L298: cpu_buffer = torch.empty(2 * B * T, dtype=torch.long, pin_memory=True)
  - L340: # Evaluation (DO NOT CHANGE — this is the fixed metric)
  - L344: def evaluate_bpb(model, tokenizer, batch_size):
  - L346: Bits per byte (BPB): vocab size-independent evaluation metric.
  - L354: steps = EVAL_TOKENS // (batch_size * MAX_SEQ_LEN)

### `program.md`

- sha256: `DD676076BA8AB905D6CC196F69DD223754237510593C7927465D06A36BF98622`
- tags: evaluation, iteration_loop, memory_context, risk_failure
- excerpts:
  - L13: - `prepare.py` — fixed constants, data prep, tokenizer, dataloader, evaluation. Do not modify.
  - L14: - `train.py` — the file you modify. Model architecture, optimizer, training loop.
  - L26: - Modify `train.py` — this is the only file you edit. Everything is fair game: model architecture, optimizer, hyperparameters, training loop, batch size, model size, etc.
  - L29: - Modify `prepare.py`. It is read-only. It contains the fixed evaluation, data loading, tokenizer, and training constants (time budget, sequence length, etc).
  - L31: - Modify the evaluation harness. The `evaluate_bpb` function in `prepare.py` is the ground truth metric.
  - L37: **Simplicity criterion**: All else being equal, simpler is better. A small improvement that adds ugly complexity is not worth it. Conversely, removing something and getting equal o
  - L71: commit val_bpb memory_gb status description
  - L76: 3. peak memory in GB, round to .1f (e.g. 12.3 — divide peak_vram_mb by 1024) — use 0.0 for crashes

### `train.py`

- sha256: `5277FE091D302C6536BB86ED69B3EAEBD7B821203EA3E5CEFBAD2E8949231772`
- tags: evaluation, iteration_loop, memory_context
- excerpts:
  - L26: from prepare import MAX_SEQ_LEN, TIME_BUDGET, Tokenizer, make_dataloader, evaluate_bpb
  - L325: X = X / (X.norm(dim=(-2, -1), keepdim=True) * 1.02 + 1e-6)
  - L339: v_mean = g.float().square().mean(dim=red_dim, keepdim=True)
  - L341: v_norm_sq = v_mean.sum(dim=(-2, -1), keepdim=True) * red_dim_size
  - L346: v_norm_new = scaled_sq_sum.sum(dim=(-2, -1), keepdim=True).sqrt()
  - L535: # Training loop
  - L610: # Final eval
  - L611: model.eval()

## Manual Pass 1 Observations

- 该仓库在 `228791fb499afffb54b46200aca536f79142f117` 固定到 `master` 分支；仓库很小，核心文件只有 `README.md`、`program.md`、`prepare.py`、`train.py`、`pyproject.toml` 等。
- `program.md` 明确规定了可变对象和冻结对象：agent 只能修改 `train.py`，不能修改 `prepare.py`、依赖或 evaluation harness。
- `prepare.py` 中的 `evaluate_bpb` 被 `program.md` 明确指定为 ground truth metric；这形成了“优化对象”和“评估器”隔离的源代码证据。
- `program.md` 要求每次实验写入 `results.tsv`，字段包括 commit、val_bpb、memory_gb、status 和 description；status 可为 `keep`、`discard` 或 `crash`。
- `program.md` 明确循环流程：改 `train.py`、commit、运行训练、读 `val_bpb` / `peak_vram_mb`、记录结果、若改善则保留，否则 reset 回起点。
- 第一轮源码观察支持“该仓库实现了一个可审计的 autonomous experiment loop 规范”这一结论；但它优化的是训练代码，不是 prompt。后续归纳到 prompt self-evolution 时必须说明这是结构迁移，不是同类任务证据。

## Claims To Verify Manually

- README 中关于 optimization / eval / memory / agent loop 的说法是否有代码或配置支撑？
- 是否存在固定样本、测试集、benchmark、grader 或人工评审流程？
- 是否能定位核心 prompt、optimizer prompt、evaluator prompt、template 或 agent context 文件？
- 是否记录版本、diff、失败案例、回滚点、成本或模型参数？
- 哪些观察可以转成可测假设，哪些只是产品或 README 叙述？

## Human Notes

- TODO: 人工阅读核心文件后补充观察。
- TODO: 标注可迁移方法、机制解释、反例和最小实验候选。
