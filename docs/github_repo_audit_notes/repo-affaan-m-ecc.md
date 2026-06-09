# Source Audit: affaan-m/ECC

本笔记是源码审计草稿，不是最终 insight。只能用于记录可追溯观察和后续核验问题。

## Source Fixation

- source_id: `repo-affaan-m-ecc`
- repository: https://github.com/affaan-m/ECC
- local_path: `local_sources\raw\github_repo_clones\repo-affaan-m-ecc`
- commit_sha: `90dfd9505dc860714cf3cc8216ad7bbb96d93365`
- branch: `main`
- generated_at: `2026-06-08T14:10:28+00:00`
- audit_json: `local_sources\raw\github_repo_audits\repo-affaan-m-ecc\audit.json`
- audit_json_sha256: `710DE5BE2394A459E59527D03681ACBF7C1D4692EC83F127FD96A7FD0217961D`

## Structure Signals

- total_files_seen: 3141
- text_files_scanned: 79
- readme_files: .claude-plugin/README.md, .codebuddy/README.md, .codebuddy/README.zh-CN.md, .codex-plugin/README.md, .kiro/README.md, .kiro/hooks/README.md, .opencode/README.md, .trae/README.md, .trae/README.zh-CN.md, README.md, README.zh-CN.md, docs/de-DE/README.md, docs/es/README.md, docs/es/examples/README.md, docs/es/rules/README.md, docs/ja-JP/README.md, docs/ja-JP/commands/README.md, docs/ja-JP/hooks/README.md, docs/ja-JP/plugins/README.md, docs/ja-JP/rules/README.md, docs/ja-JP/skills/README.md, docs/ja-JP/skills/visa-doc-translate/README.md, docs/ko-KR/README.md, docs/pt-BR/README.md, docs/ru/README.md, docs/th/README.md, docs/tr/README.md, docs/tr/examples/README.md, docs/tr/rules/README.md, docs/ur/README.md, docs/vi-VN/README.md, docs/zh-CN/README.md, docs/zh-CN/hooks/README.md, docs/zh-CN/plugins/README.md, docs/zh-CN/rules/README.md, docs/zh-CN/skills/visa-doc-translate/README.md, docs/zh-TW/README.md, ecc2/README.md, examples/gan-harness/README.md, hooks/README.md, hooks/memory-persistence/README.md, integrations/aura/README.md, legacy-command-shims/README.md, plugins/README.md, rules/README.md, skills/visa-doc-translate/README.md
- license_files: LICENSE
- package_files: .opencode/package.json, ecc2/Cargo.toml, package.json, pyproject.toml, skills/skill-comply/pyproject.toml
- path_tag_counts: `{"prompt": 4, "eval": 16, "agent": 62, "memory_context": 1, "versioning": 1}`
- content_tag_counts: `{"evaluation": 20, "iteration_loop": 58, "memory_context": 34, "agent_workflow": 54, "risk_failure": 59}`

## Evidence File Signals

### `docs/ja-JP/skills/README.md`

- sha256: `9251B427D95EFB5FD0CF991477AD490DB0F8654D9506FF76672C40AF64DB21F7`
- tags: agent, agent_workflow, evaluation, memory_context, risk_failure
- excerpts:
  - L21: - `django-security/` - Django セキュリティ
  - L23: - `quarkus-security/` - Quarkus セキュリティ: JWT/OIDC、RBAC、バリデーション
  - L28: - `springboot-security/` - Spring Boot セキュリティ
  - L35: - `security-review/` - セキュリティチェックリスト
  - L36: - `security-scan/` - セキュリティスキャン
  - L39: - `tdd-workflow/` - テスト駆動開発ワークフロー
  - L43: - `eval-harness/` - 評価ハーネス
  - L44: - `iterative-retrieval/` - 反復的検索

### `docs/ja-JP/skills/visa-doc-translate/README.md`

- sha256: `6F83D814A8B08368853EEF25045E3BFC2A7245549B6E4B174E4D57A3034C9897`
- tags: agent

### `docs/zh-CN/skills/visa-doc-translate/README.md`

- sha256: `EC7A06105DBC8CB3B4F98F1C9AA77AC592EE3F1A4D0D4777DF19B6A668B5307A`
- tags: agent

### `hooks/memory-persistence/README.md`

- sha256: `FAADC3386EBC5ED7FB4B1300440520C62DB92AC0BC7ADAEC4272A286F791D939`
- tags: iteration_loop, memory_context, risk_failure
- excerpts:
  - L1: # Memory Persistence Hooks
  - L3: These lifecycle hook definitions document ECC's memory persistence contract for Claude Code plugin and manual installs.
  - L24: \| `Stop` \| `stop:format-typecheck` \| Batch quality gate after edits \| yes on hook failure \|
  - L29: - Keep persistence local by default.
  - L33: - Keep lifecycle hooks profile-gated through `ECC_HOOK_PROFILE` and `ECC_DISABLED_HOOKS`.

### `skills/visa-doc-translate/README.md`

- sha256: `781865E79491F216FEDAF7A17A3C9B2DCDFFF52CEB7B40A2EE99FCF9EA0D854D`
- tags: agent

### `docs/COMMAND-AGENT-MAP.md`

- sha256: `0A30A898CC8B27AC3832B406989B205EE9243E2E08BF158B375AB5C11A3E64EA`
- tags: agent, agent_workflow, evaluation, iteration_loop, memory_context, risk_failure
- excerpts:
  - L1: # Command → Agent / Skill Map
  - L3: This document lists each slash command and the primary agent(s) or skills it invokes, plus notable direct-invoke agents. Use it to discover which commands use which agents and to k
  - L5: \| Command \| Primary agent(s) \| Notes \|
  - L9: \| `/code-review` \| code-reviewer \| Quality and security review \|
  - L16: \| `/go-test` \| tdd-guide \| Go TDD workflow \|
  - L19: \| `/harness-audit` \| — \| Harness scorecard (no single agent) \|
  - L20: \| `/loop-start` \| loop-operator \| Start autonomous loop \|
  - L21: \| `/loop-status` \| loop-operator \| Inspect loop status \|

### `docs/MEGA-PLAN-REPO-PROMPTS-2026-03-12.md`

- sha256: `613AAB63611CEBA1150D476A5830CC11B1045E510F0FC2CC07C1178D7D9F07F7`
- tags: agent_workflow, iteration_loop, memory_context, prompt, risk_failure
- excerpts:
  - L6: They are written for parallel agents and assume the March 12 orchestration and
  - L11: - `everything-claude-code` has finished the orchestration, Codex baseline, and
  - L18: - `agentshield`, `ECC-website`, and `skill-creator-app` all have dirty
  - L32: self-loop observations") against the actual loop problem described in issue
  - L40: automated-session observation, and runaway recursive loops.
  - L48: - If you make code changes, keep them tightly scoped to observe behavior and
  - L71: 4. governance past the tool call
  - L75: 1. Read the March 11 mega plan and March 12 handoff.

### `docs/skill-adaptation-policy.md`

- sha256: `188CF672DF995C458385FF5BCAE51FC7D92149186C2992338034B310092FB03E`
- tags: agent, agent_workflow, iteration_loop
- excerpts:
  - L9: - copy the underlying idea, workflow, or structure
  - L15: ## When To Keep The Original Name
  - L17: Keep the original skill name only when all of the following are true:
  - L36: - the original name is vendor-forward or community-brand-forward instead of workflow-forward
  - L38: - the contribution now fits as a capability, operator workflow, or policy layer rather than a literal port
  - L42: - keep a reusable graph primitive as `social-graph-ranker`, but make broader workflow layers `lead-intelligence` or `connections-optimizer`
  - L50: - `skills/` for on-demand workflows
  - L57: If external functionality is worth keeping:

### `docs/SKILL-DEVELOPMENT-GUIDE.md`

- sha256: `1A421CC4FFCBF7CA33D0F3170251CF3A9D2F889BF345665F58B16EF6A38E847B`
- tags: agent, agent_workflow, iteration_loop, memory_context, risk_failure
- excerpts:
  - L25: - **Workflow definitions**: Step-by-step processes for common tasks
  - L29: Unlike **agents** (specialized subassistants) or **commands** (user-triggered actions), skills are passive knowledge that Claude Code references when relevant.
  - L37: - An agent needs domain knowledge
  - L39: ### Skill vs Agent vs Command
  - L44: \| **Agent** \| Task executor \| Explicit delegation \|
  - L251: ### Workflow Skills
  - L255: **Examples:** `tdd-workflow`, `code-review-workflow`, `deployment-checklist`
  - L259: name: code-review-workflow

### `docs/SKILL-PLACEMENT-POLICY.md`

- sha256: `6E30066749131AB1BAE10920CB6344C8D9B7782D1F3DF62D5AA48CBE0283D316`
- tags: agent, evaluation
- excerpts:
  - L28: Created by continuous-learning (evaluate-session hook, /learn command). Default path is configurable via `skills/continuous-learning/config.json` → `learned_skills_path`.
  - L101: 2. Add provenance validation to learned-skill write paths (evaluate-session, /learn output) so new learned skills always get `.provenance.json`.

### `tests/__init__.py`

- sha256: `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`
- tags: eval

### `tests/codex-config.test.js`

- sha256: `18023220174B1811CF2A1AD187176AAC0F72EF9C2994854F29AF5B3DE19B2905`
- tags: agent_workflow, eval
- excerpts:
  - L26: const codexAgentsDir = path.join(repoRoot, '.codex', 'agents');
  - L67: test('reference config enables Codex multi-agent support', () => {
  - L69: /^\s*multi_agent\s*=\s*true\s*$/m.test(config),
  - L70: 'Expected `.codex/config.toml` to opt into Codex multi-agent collaboration',
  - L80: const rolePath = path.join(codexAgentsDir, roleFile);
  - L82: const sectionBody = getTomlSection(config, `agents.${roleSection}`);
  - L86: new RegExp(`^\\s*config_file\\s*=\\s*"agents\\/${escapeRegExp(roleFile)}"\\s*$`, 'm').test(
  - L89: `Expected \`.codex/config.toml\` to reference ${roleFile} inside [agents.${roleSection}]`,

### `tests/conftest.py`

- sha256: `5EFB08E8C6131AB1426AB320CAF93568A8D5BDBF5918E55074FEE69C730535F5`
- tags: eval

### `tests/opencode-config.test.js`

- sha256: `0D894C8CEDC0377DA2E50510F2B07BF2D0DB38AB50923E73515F3907DD898E46`
- tags: agent_workflow, eval
- excerpts:
  - L80: test('command markdown frontmatter uses plugin-scoped agent ids', () => {
  - L85: const match = body.match(/^agent:\s*(.+)$/m);
  - L93: `Expected plugin-scoped agent id in ${entry}, got: ${match[1]}`

### `tests/opencode-plugin-hooks.test.js`

- sha256: `B15760D1D77A1D5DEE61FF958197FC9277887842ECF958D01E8691EA652C7BDC`
- tags: eval

### `tests/plugin-manifest.test.js`

- sha256: `9FB1A9DD2B184B55D9BA9359BA285081BD5459A97494792A88EB2332A540571B`
- tags: agent_workflow, eval, iteration_loop, memory_context
- excerpts:
  - L6: * - .agents/plugins/marketplace.json (Codex marketplace discovery)
  - L24: const rootAgentsPath = path.join(repoRoot, 'AGENTS.md');
  - L25: const trAgentsPath = path.join(repoRoot, 'docs', 'tr', 'AGENTS.md');
  - L26: const zhCnAgentsPath = path.join(repoRoot, 'docs', 'zh-CN', 'AGENTS.md');
  - L30: const agentYamlPath = path.join(repoRoot, 'agent.yaml');
  - L109: test('AGENTS.md version line matches package.json', () => {
  - L110: const agentsSource = fs.readFileSync(rootAgentsPath, 'utf8');
  - L111: const match = agentsSource.match(new RegExp(`^\\*\\*Version:\\*\\* (${semverPattern})$`, 'm'));

### `tests/run-all.js`

- sha256: `371DBAEA5B71321E3EBB9F16FF35EDA13D57698AEDD929E95936FD39CF50E2DE`
- tags: eval, iteration_loop
- excerpts:
  - L51: console.log('╔' + '═'.repeat(BOX_W) + '╗');
  - L53: console.log('╚' + '═'.repeat(BOX_W) + '╝');
  - L120: console.log('\n╔' + '═'.repeat(BOX_W) + '╗');
  - L122: console.log('╠' + '═'.repeat(BOX_W) + '╣');
  - L126: console.log('╚' + '═'.repeat(BOX_W) + '╝');

### `tests/test_astraflow_provider.py`

- sha256: `DA40F77C00047979CF99B22D4558630FCEC0868ACCE08BAB915ABE53C4859B83`
- tags: eval

### `tests/test_builder.py`

- sha256: `8BFF543B5CE33F3882F3AE805B432C4A3169220FA27EF17985657CFAF8E28469`
- tags: eval

### `tests/test_claude_provider.py`

- sha256: `A036526F20B7EE059BF86B4866353E323BBDE49156C6B61567A8CA409CA22889`
- tags: eval

## Manual Pass 1 Observations

- 该仓库在 `90dfd9505dc8eed476003016a645cb0ee2f1897a` 固定到 `main` 分支；`package.json` 显示 package name 为 `ecc-universal`、version 为 `2.0.0-rc.1`、license 为 `MIT`，根目录存在 `LICENSE`。
- README 中关于 Token Optimization、Memory Persistence、Verification Loops、Subagent Orchestration 的强叙述，在文件结构中能找到部分对应路径：
  - `hooks/memory-persistence/README.md`
  - `examples/evaluator-rag-prototype/`
  - `tests/hooks/*`
  - `tests/lib/skill-evolution.test.js`
  - `tests/hooks/evaluate-session.test.js`
  - `tests/docs/evaluator-rag-prototype.test.js`
  - `tests/scripts/harness-audit.test.js`
- `examples/evaluator-rag-prototype/` 下存在 `scenario.json`、`trace.json`、`verifier-result.json`、`report.json` 和 `candidate-playbook.md` 等文件，说明 README 中的 evaluator / verification loop 叙述至少有一个原型样例支撑，后续应深读该目录。
- 该仓库测试面很大，包含 hooks、lib、scripts、docs、ci 等多类测试。第一轮文件结构支持“它是一个跨 harness 工程系统”，但不等同于证明其方法有效。
- README 的高 star / contributor / ecosystem 表述仍需谨慎。虽然当前 clone 和 GitHub API 元数据能确认仓库高热度，但热度不是研究证据；必须核验具体 eval 原型、skill evolution 流程和失败/回滚记录。
- 第一轮源码观察支持“该仓库值得作为 verification loop / memory / harness governance 候选继续审计”；暂不支持把它作为强 insight 来源。

## Claims To Verify Manually

- README 中关于 optimization / eval / memory / agent loop 的说法是否有代码或配置支撑？
- 是否存在固定样本、测试集、benchmark、grader 或人工评审流程？
- 是否能定位核心 prompt、optimizer prompt、evaluator prompt、template 或 agent context 文件？
- 是否记录版本、diff、失败案例、回滚点、成本或模型参数？
- 哪些观察可以转成可测假设，哪些只是产品或 README 叙述？

## Human Notes

- TODO: 人工阅读核心文件后补充观察。
- TODO: 标注可迁移方法、机制解释、反例和最小实验候选。
