# Source Audit: linshenkx/prompt-optimizer

本笔记是源码审计草稿，不是最终 insight。只能用于记录可追溯观察和后续核验问题。

## Source Fixation

- source_id: `repo-linshenkx-prompt-optimizer`
- repository: https://github.com/linshenkx/prompt-optimizer
- local_path: `local_sources\raw\github_repo_clones\repo-linshenkx-prompt-optimizer`
- commit_sha: `d7cde6c2fc5c56a579d803d485ad170788a4141e`
- branch: `develop`
- generated_at: `2026-06-08T14:10:29+00:00`
- audit_json: `local_sources\raw\github_repo_audits\repo-linshenkx-prompt-optimizer\audit.json`
- audit_json_sha256: `B2760215750FC67EBFCF1A9B716AD4DBF93308465FB660125448D088998D40E2`

## Structure Signals

- total_files_seen: 1857
- text_files_scanned: 80
- readme_files: README.md, README.zh-CN.md, docs/README.md, docs/archives/101-singleton-refactor/README.md, docs/archives/102-web-architecture-refactor/README.md, docs/archives/103-desktop-architecture/README.md, docs/archives/104-test-panel-refactor/README.md, docs/archives/105-output-display-v2/README.md, docs/archives/106-template-management/README.md, docs/archives/107-component-standardization/README.md, docs/archives/108-layout-system/README.md, docs/archives/109-theme-system/README.md, docs/archives/110-desktop-indexeddb-fix/README.md, docs/archives/111-electron-preference-architecture/README.md, docs/archives/112-desktop-ipc-fixes/README.md, docs/archives/114-desktop-file-storage/README.md, docs/archives/115-ipc-serialization-fixes/README.md, docs/archives/116-desktop-packaging-optimization/README.md, docs/archives/117-import-export-architecture-refactor/README.md, docs/archives/117-pinia-refactoring/README.md, docs/archives/118-desktop-auto-update-system/README.md, docs/archives/119-csp-safe-template-processing/README.md, docs/archives/120-mcp-server-module/README.md, docs/archives/121-context-editor-refactor/README.md, docs/archives/121-multi-custom-models-support/README.md, docs/archives/122-docker-api-proxy/README.md, docs/archives/122-naive-ui-migration/README.md, docs/archives/123-advanced-features-implementation/README.md, docs/archives/124-advanced-mode-toggle-migration/README.md, docs/archives/124-navigation-optimization/README.md, docs/archives/125-test-area-refactor/README.md, docs/archives/126-submode-persistence/README.md, docs/archives/127-multi-turn-dialogue-mode-optimization/README.md, docs/archives/128-context-ui-and-variable-system-refactor/README.md, docs/archives/129-session-store-single-source-refactor/README.md, docs/archives/130-test-area-version-model-selection/README.md, docs/archives/131-testing-redesign/README.md, docs/archives/132-architecture-migration-and-session-persistence-plans/README.md, docs/archives/README.md, docs/developer/README.md, docs/developer/troubleshooting/README.md, docs/project/README.md, docs/testing/README.md, docs/testing/ai-automation/README.md, docs/testing/ai-automation/storage-key-consistency/README.md, docs/testing/ai-automation/test-scenarios/normal-flow/README.md, docs/user/README.md, docs/workspace/compare-evaluation-analysis/README.md, docs/workspace/compare-evaluation-analysis/history/README.md, docs/workspace/compare-evaluation-analysis/real-api-samples/README.md, docs/workspace/compare-evaluation-analysis/structured-compare-calibration/README.md, docs/workspace/image-reference-prompt-optimization/README.md, docs/workspace/test-area-auto-iterate-one-round/README.md, mkdocs/README.md, packages/core/tests/fixtures/README.md, packages/core/tests/helpers/README.md, packages/desktop/README-env-config.md, packages/desktop/README.md, packages/mcp-server/README.md, packages/ui/README.md, packages/ui/docs/README.md, packages/ui/src/i18n/README.md, site/README.md
- license_files: LICENSE
- package_files: mkdocs/requirements.txt, package.json, packages/core/package.json, packages/desktop/package.json, packages/extension/package.json, packages/mcp-server/package.json, packages/ui/package.json, packages/web/package.json, pnpm-lock.yaml, site/package.json, site/pnpm-lock.yaml
- path_tag_counts: `{"prompt": 9, "eval": 68, "agent": 1, "memory_context": 15, "versioning": 13}`
- content_tag_counts: `{"prompt_optimization": 8, "evaluation": 39, "iteration_loop": 27, "memory_context": 11, "agent_workflow": 9, "risk_failure": 11}`

## Evidence File Signals

### `docs/testing/ai-automation/README.md`

- sha256: `7E0CC34E8E36C8F180C7AE9F4992BF39189D41FDE387A647E60E1CE1D907168A`
- tags: eval, iteration_loop, memory_context, risk_failure
- excerpts:
  - L39: │ │ ├── network-failures.md
  - L41: │ │ ├── storage-failures.md
  - L44: │ ├── memory-stress.md
  - L51: │ └── memory-leaks.md
  - L52: ├── regression/ # 回归测试
  - L53: │ ├── feature-regression.md
  - L54: │ └── performance-regression.md
  - L142: browser_type(element, ref, "x".repeat(10000));

### `docs/testing/ai-automation/storage-key-consistency/README.md`

- sha256: `2209C038D8F7F3EBE09042A899C314823269EA25951816E8889BA3FB19650928`
- tags: eval, memory_context
- excerpts:
  - L142: - [存储键常量定义](../../../../packages/ui/src/constants/storage-keys.ts)
  - L143: - [核心服务存储键](../../../../packages/core/src/constants/storage-keys.ts)

### `docs/testing/ai-automation/test-scenarios/normal-flow/README.md`

- sha256: `F2022DAA0B813410AE49F3945C4361EA7D71CEED5F57E6C44654717D846A271D`
- tags: eval

### `docs/testing/README.md`

- sha256: `6C4EEAAA3DF4C4985F31680FE17FDDC6B75DDC31D85543520DC9639DA04E6917`
- tags: eval, evaluation
- excerpts:
  - L27: # 扩展 E2E（analysis / optimize / compare 等长链路）

### `docs/workspace/compare-evaluation-analysis/history/README.md`

- sha256: `51DF2D9CAA4A8C1646676AA4D91367E5DE21ED3142BEFC98D93043B71D27A4B7`
- tags: eval, evaluation, versioning
- excerpts:
  - L20: - compare 默认继续带 `## 当前工作区提示词`
  - L38: - `evaluation-redesign-overview.md`
  - L40: - `evaluation-prompt-rubric-spec.md`

### `docs/workspace/compare-evaluation-analysis/README.md`

- sha256: `F42B6E250937A5D98FF58AA1A12A60EF0F206B08FD198F660A91593FAEA1CE4E`
- tags: eval, evaluation, iteration_loop
- excerpts:
  - L1: # compare-evaluation-analysis
  - L13: 5. [auto-compare-rewrite-effect-analysis.md](./auto-compare-rewrite-effect-analysis.md)
  - L27: 如果你要逐步验证 compare 阶段功能，优先看这份。
  - L29: compare / rewrite 从 Markdown 协议层迁移到 JSON payload 协议层的最小实现方案与落地说明。
  - L31: - `auto-compare-rewrite-effect-analysis.md`
  - L48: - compare / rewrite 的 LLM 协议层已经迁移为“规则说明 + JSON payload”，Markdown 现在主要保留给 docs / calibration 调试视图。
  - L58: \| `prompt-iterate + focus` \| 有 \| 暂无 \| 暂无 \| 暂无 \|
  - L66: \| `compare` \| 有 \| 有 \| 有 \| 有 \|

### `docs/workspace/compare-evaluation-analysis/real-api-samples/README.md`

- sha256: `BAE052547C4584DE75CF784729AB8330CA4CE48CE58EABABDC08FDDC61D6EE01`
- tags: eval, evaluation, iteration_loop
- excerpts:
  - L8: - `basic-system-compare`
  - L9: request: [request.md](./basic-system-compare/request.md)
  - L10: rendered: [rendered-messages.md](./basic-system-compare/rendered-messages.md)
  - L11: response: [response.md](./basic-system-compare/response.md)
  - L12: - `basic-system-compare-focus`
  - L13: request: [request.md](./basic-system-compare-focus/request.md)
  - L14: rendered: [rendered-messages.md](./basic-system-compare-focus/rendered-messages.md)
  - L15: response: [response.md](./basic-system-compare-focus/response.md)

### `docs/workspace/compare-evaluation-analysis/structured-compare-calibration/README.md`

- sha256: `25477B0F81EF6F64C71D2531DD8FE3845195B3DF9B8C515E15A62F556D3BEB1E`
- tags: eval, evaluation, risk_failure
- excerpts:
  - L1: # Structured Compare Calibration
  - L3: > 这一组样本不是为了证明 compare 功能“能跑”，而是为了校准我们新引入的 structured compare judge / synthesis / rewrite 提示词。
  - L7: - 为 `pairwise judge` 提供少量但高价值的校准场景。
  - L8: - 让 `synthesis` 在这些场景下暴露出是否存在“过度乐观”“忽略 overfit 风险”“把单次好运当稳定收益”等问题。
  - L9: - 让 `rewrite-from-evaluation` 接收到的上游证据足够清晰、可压缩、可复用。
  - L21: 使用真实模型执行 4 个快照，观察 structured compare 是否能识别“只输出 JSON、不要解释”的边界控制收益。
  - L22: - `synthetic-medical-latent-trigger-overfit`
  - L25: 电商商品抽取场景。目标是校准 compare 是否会坚持 schema / contract 优先，不会因为 teacher 输出更流畅就放过字段改名和 wrapper 漂移。

### `docs/workspace/image-reference-prompt-optimization/README.md`

- sha256: `9BFF7B52D993222D737F68119050ADE31F0871DED240FCA671505FB2DD141335`
- tags: agent_workflow, evaluation, prompt
- excerpts:
  - L283: - `Workflow`
  - L437: - [summary.json](/C:/Users/15588/.codex/worktrees/8453/prompt-optimizer/.codex/tmp/prompt-optimizer/20260401-langgpt-lite-eval/summary.json)
  - L438: - [summary.json](/C:/Users/15588/.codex/worktrees/8453/prompt-optimizer/.codex/tmp/prompt-optimizer/20260401-langgpt-lite-eval-v2/summary.json)

### `docs/workspace/test-area-auto-iterate-one-round/README.md`

- sha256: `12751176847723427E98598F682C3E7A0D90165B9B282768E4D7C8F38EB0BD8E`
- tags: eval, evaluation, iteration_loop
- excerpts:
  - L8: > 2. compare evaluation 的通用增强
  - L16: - 结构化对比评估与通用智能重写：`docs/architecture/structured-compare-and-evaluation-rewrite.md`
  - L17: - 薄 SPO：UI、交互与停止规则：`docs/architecture/spo-thin-loop-ui-and-stop-rules.md`
  - L18: - 实施拆分：Compare Stop Signals 与薄 SPO：`./implementation-split-compare-stop-signals-and-spo.md`
  - L22: - 架构设计：`docs/architecture/test-area-auto-iterate-one-round.md`
  - L23: - 架构补充：`docs/architecture/structured-compare-and-evaluation-rewrite.md`
  - L24: - SPO 架构补充：`docs/architecture/spo-thin-loop-ui-and-stop-rules.md`
  - L25: - 对比评估现状：`docs/workspace/compare-evaluation-analysis/current-spec.md`

### `packages/core/tests/fixtures/README.md`

- sha256: `3F142B70D4D870F6AEF7664D22CC6D6D52B031AC0A31C0A9EEF2C924B79AB37D`
- tags: eval

### `packages/core/tests/helpers/README.md`

- sha256: `AE01E54A0C8E00B4C7AEE49030F2AAF685D12582F7FB25EC540D34454731DF51`
- tags: eval

### `scripts/check-locale-parity.test.mjs`

- sha256: `13DAFA0228A68BE733EE1CC99A4BC872599C60418286CB6B55F3041802CFC231`
- tags: eval, iteration_loop
- excerpts:
  - L47: const candidate = {
  - L54: assert.deepEqual(diffLocaleShape(base, candidate), {

### `scripts/check-no-chinese-runtime.test.mjs`

- sha256: `AA4EAA52B3EC68C626BA5DA68411302F08AE096CD76B5B7AEB929CA5151DD77F`
- tags: eval, evaluation, memory_context
- excerpts:
  - L112: shouldScanPath('packages/core/src/services/storage/dexieStorageProvider.ts'),
  - L116: shouldScanPath('packages/core/src/services/storage/fileStorageProvider.ts'),
  - L228: shouldScanPath('packages/ui/src/components/evaluation/compare-ui.ts'),
  - L232: shouldScanPath('packages/ui/src/components/image-mode/imageText2ImageEvaluation.ts'),
  - L300: shouldScanPath('packages/ui/src/composables/prompt/useEvaluationHandler.ts'),
  - L316: shouldScanPath('packages/ui/src/composables/prompt/useEvaluationContext.ts'),

### `scripts/desktop-ipc-handlers.test.mjs`

- sha256: `AC2330934CC5D00D16C3BE7093127EBEA163862170B022BA7FB0A765F5A4172B`
- tags: eval, memory_context
- excerpts:
  - L24: readText('packages/desktop/remote-storage.js'),
  - L53: test('desktop remote storage handler routes S3-compatible operations through AWS SDK commands', async () => {
  - L54: const { handleRemoteStorageOperation } = await import('../packages/desktop/remote-storage.js')
  - L74: const result = await handleRemoteStorageOperation({
  - L102: test('desktop remote storage S3 list operation follows continuation tokens', async () => {
  - L103: const { handleRemoteStorageOperation } = await import('../packages/desktop/remote-storage.js')
  - L138: const entries = await handleRemoteStorageOperation({
  - L172: test('desktop remote storage handler routes WebDAV operations through the WebDAV client library adapter', async () => {

### `scripts/package-scripts.test.mjs`

- sha256: `55F3A9DE183DC96D21E9CAB1617E39A48E9E3988DC8E6E34D96DD66CCB32CE42`
- tags: eval, memory_context
- excerpts:
  - L31: test('repo checks execute package script coverage tests', () => {

### `scripts/release-notes.test.mjs`

- sha256: `266AE0F8CB89FC4FA839EAE51BE3D2B1C828FD3DA1222A70A50B914C0239BD2D`
- tags: agent_workflow, eval, evaluation, prompt_optimization
- excerpts:
  - L65: - Text-to-image evaluation is now easier to review and compare.
  - L66: - Reference-image workflows are smoother and safer across the app.
  - L70: return `# Prompt Optimizer v${version}
  - L73: - Faster image prompt evaluation with clearer outputs.
  - L81: - Synced release messaging with the desktop workflow.
  - L106: return `# Prompt Optimizer v${version}
  - L139: assert.match(template, /^# Prompt Optimizer v2\.8\.0/m);
  - L154: assert.match(template, /^# Prompt Optimizer v2\.8\.0/m);

### `scripts/run-many.test.mjs`

- sha256: `3FA918586CFA6F1ADC354B8AA6F3B375D095034F2D46188DDD267A5C9EE9D8BD`
- tags: eval, risk_failure
- excerpts:
  - L35: test('runSequential executes scripts in order and stops on failure', async () => {

### `scripts/sync-versions.js`

- sha256: `7EED5216A094207B32D32590F9B21B3467AD894339098479E608474ECE18D71A`
- tags: versioning

### `docs/architecture/storage-key-architecture.md`

- sha256: `6DC91C51ED8C628AA5091771059FD1530DD29C5E05B9FE0A50E222C526BE8C01`
- tags: iteration_loop, memory_context
- excerpts:
  - L11: **用途：** 实际的数据存储操作（localStorage、Dexie、文件存储等）
  - L25: 'app:selected-iterate-template' -> 'pref:app:selected-iterate-template'
  - L52: "app:selected-iterate-template": "iterate"
  - L70: const value = await this.storage.getItem(key); // 查找 'app:settings:ui:theme-id'
  - L94: 'app:selected-iterate-template'
  - L98: const DIRECT_STORAGE_KEYS = [
  - L115: for (const key of DIRECT_STORAGE_KEYS) {
  - L116: const value = await this.storage.getItem(key);

## Manual Pass 1 Observations

- 该仓库在 `d7cde6c2fc5c56a579d803d485ad170788a4141e` 固定到 `develop` 分支；不是只读 README，已 clone 到 `local_sources/raw/github_repo_clones/repo-linshenkx-prompt-optimizer`。
- 当前源码中存在 compare / rewrite / structured judge 相关实现路径，至少包括：
  - `packages/core/src/services/evaluation/structured-compare-prompts.ts`
  - `packages/core/src/services/evaluation/rewrite-from-evaluation.ts`
  - `packages/core/src/services/template/default-templates/evaluation-structured-compare/`
- `docs/workspace/compare-evaluation-analysis/protocol-migration-minimal-plan.md` 显示该项目曾把 compare / rewrite 的 LLM 请求从 Markdown 拼接迁移到“规则说明 + JSON payload 证据层”。这是一条需要重点深读的工程线索：它不是单纯 prompt 改写，而是在降低 judge/rewrite 输入边界混淆、schema 漂移和消息包装漂移。
- `docs/workspace/compare-evaluation-analysis/structured-compare-calibration/README.md` 显示存在 synthetic/live calibration 样本，用于校准 pairwise judge、synthesis 和 rewrite-from-evaluation。该文件明确提到 overfit risk、schema/contract 边界和重复执行稳定性，值得进一步核验 runner 和样本。
- `tests/e2e/optimize/`、`tests/e2e/analysis/`、`tests/e2e/test/` 和 `tests/e2e/helpers/evaluation.ts` 等路径说明该项目有面向 optimize / analysis / compare 的 E2E 测试，但还不能说明 prompt 优化效果，只能说明功能链路被测试。
- 第一轮源码观察支持“该仓库有 compare evaluation 与 rewrite-from-evaluation 的工程闭环”这一低层观察；暂不支持“其 prompt optimizer 稳定提升任务表现”的结论。

## Claims To Verify Manually

- README 中关于 optimization / eval / memory / agent loop 的说法是否有代码或配置支撑？
- 是否存在固定样本、测试集、benchmark、grader 或人工评审流程？
- 是否能定位核心 prompt、optimizer prompt、evaluator prompt、template 或 agent context 文件？
- 是否记录版本、diff、失败案例、回滚点、成本或模型参数？
- 哪些观察可以转成可测假设，哪些只是产品或 README 叙述？

## Human Notes

- TODO: 人工阅读核心文件后补充观察。
- TODO: 标注可迁移方法、机制解释、反例和最小实验候选。
