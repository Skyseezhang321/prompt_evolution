# Source Audit: humanlayer/12-factor-agents

本笔记是源码审计草稿，不是最终 insight。只能用于记录可追溯观察和后续核验问题。

## Source Fixation

- source_id: `repo-humanlayer-12-factor-agents`
- repository: https://github.com/humanlayer/12-factor-agents
- local_path: `local_sources\raw\github_repo_clones\repo-humanlayer-12-factor-agents`
- commit_sha: `d20c728368bf9c189d6d7aab704744decb6ec0cc`
- branch: `main`
- generated_at: `2026-06-08T14:10:29+00:00`
- audit_json: `local_sources\raw\github_repo_audits\repo-humanlayer-12-factor-agents\audit.json`
- audit_json_sha256: `45DC0CD2C4A456C5EF27F99515357FC14FFED59E1D11C28E89EE7A883C577395`

## Structure Signals

- total_files_seen: 499
- text_files_scanned: 55
- readme_files: README.md, hack/contributors_markdown/README.md, packages/create-12-factor-agent/template/README.md, packages/walkthroughgen/readme.md, workshops/2025-05-17/sections/00-hello-world/README.md, workshops/2025-05-17/sections/01-cli-and-agent/README.md, workshops/2025-05-17/sections/02-calculator-tools/README.md, workshops/2025-05-17/sections/03-tool-loop/README.md, workshops/2025-05/sections/00-hello-world/README.md, workshops/2025-05/sections/01-cli-and-agent/README.md, workshops/2025-05/sections/02-calculator-tools/README.md, workshops/2025-05/sections/03-tool-loop/README.md, workshops/2025-05/sections/04-baml-tests/README.md, workshops/2025-05/sections/05-human-tools/README.md, workshops/2025-05/sections/06-customize-prompt/README.md, workshops/2025-05/sections/07-context-window/README.md, workshops/2025-05/sections/08-api-endpoints/README.md, workshops/2025-05/sections/09-state-management/README.md, workshops/2025-05/sections/10-human-approval/README.md, workshops/2025-05/sections/11-humanlayer-approval/README.md, workshops/2025-05/sections/12-humanlayer-webhook/README.md, workshops/2025-05/sections/final/README.md
- license_files: LICENSE
- package_files: hack/contributors_markdown/pyproject.toml, hack/contributors_markdown/uv.lock, packages/create-12-factor-agent/template/package.json, packages/walkthroughgen/package.json, workshops/2025-05-17/package.json, workshops/2025-05/final/package.json, workshops/2025-05/sections/01-cli-and-agent/package.json, workshops/2025-05/sections/02-calculator-tools/package.json, workshops/2025-05/sections/03-tool-loop/package.json, workshops/2025-05/sections/04-baml-tests/package.json, workshops/2025-05/sections/05-human-tools/package.json, workshops/2025-05/sections/06-customize-prompt/package.json, workshops/2025-05/sections/07-context-window/package.json, workshops/2025-05/sections/08-api-endpoints/package.json, workshops/2025-05/sections/09-state-management/package.json, workshops/2025-05/sections/10-human-approval/package.json, workshops/2025-05/sections/11-humanlayer-approval/package.json, workshops/2025-05/sections/12-humanlayer-webhook/package.json, workshops/2025-05/sections/final/package.json, workshops/2025-07-16/pyproject.toml, workshops/2025-07-16/uv.lock
- path_tag_counts: `{"prompt": 20, "eval": 7, "agent": 61, "memory_context": 6, "versioning": 2}`
- content_tag_counts: `{"evaluation": 2, "iteration_loop": 29, "memory_context": 11, "agent_workflow": 37, "risk_failure": 2}`

## Evidence File Signals

### `packages/create-12-factor-agent/template/README.md`

- sha256: `D3A258AAF6FEF2BDAA4F64CB7E6F77F2DA0D24F1AB2E81504E66F609C1445364`
- tags: agent, agent_workflow, iteration_loop, memory_context, prompt
- excerpts:
  - L7: There are many checkpoints between the every file edit in theworkshop steps,
  - L9: you should be able to keep up and run each example.
  - L55: # Chapter 1 - CLI and Agent Loop
  - L57: Now let's add BAML and create our first agent with a CLI interface.
  - L73: Add our starter agent, a single baml prompt that we'll build on
  - L75: cp ./walkthrough/01-agent.baml baml_src/agent.baml
  - L93: Add the agent implementation
  - L95: cp ./walkthrough/01-agent.ts src/agent.ts

### `workshops/2025-05-17/sections/01-cli-and-agent/README.md`

- sha256: `C3A10D87A11C975A9FF759DDF1004D886C2B1C5D5484D342C9D6830FE382A391`
- tags: agent, agent_workflow, iteration_loop
- excerpts:
  - L1: # Chapter 1 - CLI and Agent Loop
  - L3: Now let's add BAML and create our first agent with a CLI interface.
  - L19: Add our starter agent, a single baml prompt that we'll build on
  - L21: cp ./walkthrough/01-agent.baml baml_src/agent.baml
  - L27: // ./walkthrough/01-agent.baml
  - L98: // cli.ts lets you invoke the agent loop from the command line
  - L100: import { agentLoop, Thread, Event } from "./agent";
  - L117: // Run the agent loop with the thread

### `workshops/2025-05-17/sections/02-calculator-tools/README.md`

- sha256: `92B81D8A908CB79A4357A89F8F52E8D27CF10546C224057D14C2B4589A656BB5`
- tags: agent, agent_workflow, iteration_loop
- excerpts:
  - L3: Let's add some calculator tools to our agent.
  - L8: return as a "next step" in the agentic loop.
  - L48: Now, let's update the agent's DetermineNextStep method to
  - L53: baml_src/agent.baml
  - L65: cp ./walkthrough/02-agent.baml baml_src/agent.baml
  - L77: You should see a tool call to the calculator

### `workshops/2025-05-17/sections/03-tool-loop/README.md`

- sha256: `EBC8B4ECEF08E9A1643F5F57BE5D81032AC4E56149BC95DEA7AD4EB151FE0C2E`
- tags: agent, agent_workflow, iteration_loop
- excerpts:
  - L1: # Chapter 3 - Process Tool Calls in a Loop
  - L3: Now let's add a real agentic loop that can run the tools and get a final answer from the LLM.
  - L5: First, lets update the agent to handle the tool call
  - L9: src/agent.ts
  - L13: -// we'll update this function to handle all the agent logic
  - L14: -export async function agentLoop(thread: Thread): Promise<AgentResponse> {
  - L19: +export async function agentLoop(thread: Thread): Promise<string> {
  - L52: cp ./walkthrough/03-agent.ts src/agent.ts

### `workshops/2025-05/sections/01-cli-and-agent/README.md`

- sha256: `593D2C9DF41BCC8FF7D8711010CD55572D682361969573B914AB304F399A0B2A`
- tags: agent, agent_workflow, iteration_loop
- excerpts:
  - L1: # Chapter 1 - CLI and Agent Loop
  - L3: Now let's add BAML and create our first agent with a CLI interface.
  - L19: Add our starter agent, a single baml prompt that we'll build on
  - L21: cp ./walkthrough/01-agent.baml baml_src/agent.baml
  - L27: // ./walkthrough/01-agent.baml
  - L87: // cli.ts lets you invoke the agent loop from the command line
  - L89: import { agentLoop, Thread, Event } from "./agent";
  - L106: // Run the agent loop with the thread

### `workshops/2025-05/sections/02-calculator-tools/README.md`

- sha256: `B060CFB9CE242B86DC37CA748F64DEE64EDB82DEE1C00D05F16B00960C4F70AE`
- tags: agent, agent_workflow, iteration_loop
- excerpts:
  - L3: Let's add some calculator tools to our agent.
  - L8: return as a "next step" in the agentic loop.
  - L48: Now, let's update the agent's DetermineNextStep method to
  - L53: baml_src/agent.baml
  - L65: cp ./walkthrough/02-agent.baml baml_src/agent.baml
  - L77: You should see a tool call to the calculator

### `workshops/2025-05/sections/03-tool-loop/README.md`

- sha256: `2C07E1F4218FA50B6593FB80862EE085D291B8410EDCCD8B64C8D25EA595C102`
- tags: agent, agent_workflow, iteration_loop
- excerpts:
  - L1: # Chapter 3 - Process Tool Calls in a Loop
  - L3: Now let's add a real agentic loop that can run the tools and get a final answer from the LLM.
  - L5: First, lets update the agent to handle the tool call
  - L9: src/agent.ts
  - L13: -// we'll update this function to handle all the agent logic
  - L14: -export async function agentLoop(thread: Thread): Promise<AgentResponse> {
  - L19: +export async function agentLoop(thread: Thread): Promise<string> {
  - L52: cp ./walkthrough/03-agent.ts src/agent.ts

### `workshops/2025-05/sections/04-baml-tests/README.md`

- sha256: `655E6AF5971C22B16303459B2571C39D3C906DD4D15F825BC5427A5A47C8EA2A`
- tags: agent_workflow, eval, iteration_loop, memory_context
- excerpts:
  - L1: # Chapter 4 - Add Tests to agent.baml
  - L3: Let's add some tests to our BAML agent.
  - L9: next, let's add some tests to the agent
  - L11: We'll start with a simple test that checks the agent's ability to handle
  - L16: baml_src/agent.baml
  - L37: cp ./walkthrough/04-agent.baml baml_src/agent.baml
  - L47: Assertions are a great way to make sure the agent is working as expected,
  - L52: baml_src/agent.baml

### `workshops/2025-05/sections/05-human-tools/README.md`

- sha256: `F7CA6F3726905D04F62A41866B9DEA583DE79F96E8F0C4D3C907346B9BBDDA3E`
- tags: agent, agent_workflow, iteration_loop
- excerpts:
  - L15: in your agent.
  - L19: baml_src/agent.baml
  - L51: cp ./walkthrough/05-agent.baml baml_src/agent.baml
  - L64: now, let's update the agent to use the new tool
  - L68: src/agent.ts
  - L71: -export async function agentLoop(thread: Thread): Promise<string> {
  - L72: +export async function agentLoop(thread: Thread): Promise<Thread> {
  - L89: cp ./walkthrough/05-agent.ts src/agent.ts

### `workshops/2025-05/sections/06-customize-prompt/README.md`

- sha256: `BF0FFF0CD8F80330B7BB34AC5B6E05E08558E0F2DF26AFC363B20D5D4215E1D0`
- tags: agent_workflow, prompt
- excerpts:
  - L3: In this section, we'll explore how to customize the prompt of the agent
  - L6: this is core to [factor 2 - own your prompts](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-2-own-your-prompts.md)
  - L15: update the agent prompt to include a reasoning step
  - L19: baml_src/agent.baml
  - L41: cp ./walkthrough/06-agent.baml baml_src/agent.baml

### `workshops/2025-05/sections/07-context-window/README.md`

- sha256: `56F9BDBFC8B8110501231A787671017D49F1750809668F8A6418109BA28421CE`
- tags: agent_workflow, memory_context
- excerpts:
  - L1: # Chapter 7 - Customize Your Context Window
  - L3: In this section, we'll explore how to customize the context window
  - L4: of the agent.
  - L6: this is core to [factor 3 - own your context window](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-3-own-your-context-window.md)
  - L9: update the agent to pretty-print the Context window for the model
  - L13: src/agent.ts
  - L15: // e.g. https://github.com/got-agents/agents/blob/59ebbfa236fc376618f16ee08eb0f3bf7b698892/linear-assistant-ts/src/agent.ts#L66-L105
  - L25: cp ./walkthrough/07-agent.ts src/agent.ts

### `content/brief-history-of-software.md`

- sha256: `63D3854273B4E9CE50D85CE36C11BF68D308AF31AA42C3E13A0004AAA3F00A85`
- tags: agent_workflow, iteration_loop, memory_context, risk_failure, versioning
- excerpts:
  - L1: [← Back to README](https://github.com/humanlayer/12-factor-agents/blob/main/README.md)
  - L7: Whether you're new to agents or an ornery old veteran like me, I'm going to try to convince you to throw out most of what you think about AI Agents, take a step back, and rethink t
  - L10: ## Agents are software, and a brief history thereof
  - L18: ![010-software-dag](https://github.com/humanlayer/12-factor-agents/blob/main/img/010-software-dag.png)
  - L24: ![015-dag-orchestrators](https://github.com/humanlayer/12-factor-agents/blob/main/img/015-dag-orchestrators.png)
  - L30: ![020-dags-with-ml](https://github.com/humanlayer/12-factor-agents/blob/main/img/020-dags-with-ml.png)
  - L34: ### The promise of agents
  - L36: I'm not the first [person to say this](https://youtu.be/Dc99-zTMyMg?si=bcT0hIwWij2mR-40&t=73), but my biggest takeaway when I started learning about agents, was that you get to thr

### `content/factor-01-natural-language-to-tool-calls.md`

- sha256: `A9D5C640E587A5C930C5C5A6896D6BFC98F72252275765C91320550D4CBC5680`
- tags: agent, agent_workflow, iteration_loop, memory_context
- excerpts:
  - L1: [← Back to README](https://github.com/humanlayer/12-factor-agents/blob/main/README.md)
  - L3: ### 1. Natural Language to Tool Calls
  - L5: One of the most common patterns in agent building is to convert natural language to structured tool calls. This is a powerful pattern that allows you to build agents that can reaso
  - L7: ![110-natural-language-tool-calls](https://github.com/humanlayer/12-factor-agents/blob/main/img/110-natural-language-tool-calls.png)
  - L31: **Note**: in reality the stripe API is a bit more complex, a [real agent that does this](https://github.com/dexhorthy/mailcrew) ([video](https://www.youtube.com/watch?v=f_cKnoPC_Oo
  - L33: From there, deterministic code can pick up the payload and do something with it. (More on this in [factor 3](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor
  - L56: **NOTE**: While a full agent would then receive the API call result and loop with it, eventually returning something like
  - L62: [← How We Got Here](https://github.com/humanlayer/12-factor-agents/blob/main/content/brief-history-of-software.md) \| [Own Your Prompts →](https://github.com/humanlayer/12-factor-ag

### `content/factor-02-own-your-prompts.md`

- sha256: `B83FB28553D64CE1A92CA75D274DC8BD8680601BFF8357DF3DC25564EE185CF7`
- tags: agent_workflow, evaluation, iteration_loop, memory_context, prompt
- excerpts:
  - L1: [← Back to README](https://github.com/humanlayer/12-factor-agents/blob/main/README.md)
  - L7: ![120-own-your-prompts](https://github.com/humanlayer/12-factor-agents/blob/main/img/120-own-your-prompts.png)
  - L16: agent = Agent(
  - L28: result = agent.run(task)
  - L71: If the signature looks a little funny, we'll get to that in [factor 4 - tools are just structured outputs](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-0
  - L79: 1. **Full Control**: Write exactly the instructions your agent needs, no black box abstractions
  - L80: 2. **Testing and Evals**: Build tests and evals for your prompts just like you would for any other code
  - L81: 3. **Iteration**: Quickly modify prompts based on real-world performance

### `content/factor-03-own-your-context-window.md`

- sha256: `A6953B0F3252E683961760785F2D9217C502363B9C4028789C975C543BB7245C`
- tags: agent_workflow, memory_context
- excerpts:
  - L1: [← Back to README](https://github.com/humanlayer/12-factor-agents/blob/main/README.md)
  - L3: ### 3. Own your context window
  - L7: > #### At any given point, your input to an LLM in an agent is "here's what's happened so far, what's the next step"
  - L10: <!-- ![130-own-your-context-building](https://github.com/humanlayer/12-factor-agents/blob/main/img/130-own-your-context-building.png) -->
  - L12: Everything is context engineering. [LLMs are stateless functions](https://thedataexchange.media/baml-revolution-in-ai-engineering/) that turn inputs into outputs. To get the best o
  - L17: - Any documents or external data you retrieve (e.g. RAG)
  - L18: - Any past state, tool calls, results, or other history
  - L19: - Any past messages or events from related but separate histories/conversations (Memory)

### `content/factor-04-tools-are-structured-outputs.md`

- sha256: `4BF9A19BF264632435F3286789C03EF519D312DDEC98A2F35C8A777B69905EF9`
- tags: agent, agent_workflow, memory_context
- excerpts:
  - L1: [← Back to README](https://github.com/humanlayer/12-factor-agents/blob/main/README.md)
  - L7: ![140-tools-are-just-structured-outputs](https://github.com/humanlayer/12-factor-agents/blob/main/img/140-tools-are-just-structured-outputs.png)
  - L48: **Note**: there has been a lot said about the benefits of "plain prompting" vs. "tool calling" vs. "JSON mode" and the performance tradeoffs of each. We'll link some resources to t
  - L50: The "next step" might not be as atomic as just "run a pure function and return the result". You unlock a lot of flexibility when you think of "tool calls" as just a model outputtin
  - L52: [← Own Your Context Window](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-03-own-your-context-window.md) \| [Unify Execution State →](https://github.com/hu

### `content/factor-07-contact-humans-with-tools.md`

- sha256: `FC695ACB695685A583C1D584E52975B0E3C44A1AA43FA3E230C6D3D5CCA940A8`
- tags: agent, agent_workflow, iteration_loop, memory_context
- excerpts:
  - L1: [← Back to README](https://github.com/humanlayer/12-factor-agents/blob/main/README.md)
  - L3: ### 7. Contact humans with tool calls
  - L7: ![170-contact-humans-with-tools](https://github.com/humanlayer/12-factor-agents/blob/main/img/170-contact-humans-with-tools.png)
  - L35: # Example usage in the agent loop
  - L43: return # Break loop and wait for response to come back with thread ID
  - L64: # todo - loop or break or whatever you want
  - L69: The above includes patterns from [factor 5 - unify execution state and business state](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-05-unify-execution-st
  - L71: If we were using the XML-y formatted from [factor 3 - own your context window](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-03-own-your-context-window.md

### `content/factor-1-natural-language-to-tool-calls.md`

- sha256: `B0E13F9D94C54C7E7176E3A8035331083537F6C9F10C1CBBA57BBCAEBB99EED0`
- tags: agent

### `content/factor-10-small-focused-agents.md`

- sha256: `6489D4593C1FD8092CFFC36D2C924D52040F05C655EC8F90581DC23CC64F4A0C`
- tags: agent, agent_workflow, iteration_loop, memory_context
- excerpts:
  - L1: [← Back to README](https://github.com/humanlayer/12-factor-agents/blob/main/README.md)
  - L3: ### 10. Small, Focused Agents
  - L5: Rather than building monolithic agents that try to do everything, build small, focused agents that do one thing well. Agents are just one building block in a larger, mostly determi
  - L7: ![1a0-small-focused-agents](https://github.com/humanlayer/12-factor-agents/blob/main/img/1a0-small-focused-agents.png)
  - L9: The key insight here is about LLM limitations: the bigger and more complex a task is, the more steps it will take, which means a longer context window. As context grows, LLMs are m
  - L13: Benefits of small, focused agents:
  - L15: 1. **Manageable Context**: Smaller context windows mean better LLM performance
  - L16: 2. **Clear Responsibilities**: Each agent has a well-defined scope and purpose

### `content/factor-2-own-your-prompts.md`

- sha256: `70AFF542FD35E036926B1FFD42147616DF78BFD3D86283B1207880BD3D3077A4`
- tags: prompt

## Manual Pass 1 Observations

- 该仓库在 `d20c728368bf7f4299068c1791f4b5ec432f1e415` 固定到 `main` 分支；主体是 `content/factor-*.md` 文档和 `packages/create-12-factor-agent/` 示例生成器。
- `content/factor-02-own-your-prompts.md` 的核心主张是不要把 prompt engineering 完全外包给黑盒框架，而是把 prompt 当作 first-class code。该文件把收益列为 full control、testing/evals、iteration、transparency 等。
- `content/factor-03-own-your-context-window.md` 把 context 定义为 prompt/instructions、retrieved docs、past state/tool calls/history、memory 和 structured output instructions 的组合。它明确把 context engineering 从模型参数、训练和微调中区分出来。
- `content/factor-04-tools-are-structured-outputs.md`、`factor-05-unify-execution-state.md`、`factor-06-launch-pause-resume.md`、`factor-07-contact-humans-with-tools.md` 等文件显示它的关注点是 agent workflow 的工程边界，而不是自动 prompt search。
- `packages/create-12-factor-agent/template/` 提供了可生成的 agent template（如 `src/agent.ts`、`src/state.ts`、BAML 文件），说明它不只是文章集合，也有最低限度的实现模板。
- 第一轮源码观察支持“该仓库可作为 agent prompt/context governance 的原则来源”；暂不支持“某个 prompt 优化方法有效”的实证结论。它更适合转化为 eval 维度和失败模式检查清单。

## Claims To Verify Manually

- README 中关于 optimization / eval / memory / agent loop 的说法是否有代码或配置支撑？
- 是否存在固定样本、测试集、benchmark、grader 或人工评审流程？
- 是否能定位核心 prompt、optimizer prompt、evaluator prompt、template 或 agent context 文件？
- 是否记录版本、diff、失败案例、回滚点、成本或模型参数？
- 哪些观察可以转成可测假设，哪些只是产品或 README 叙述？

## Human Notes

- TODO: 人工阅读核心文件后补充观察。
- TODO: 标注可迁移方法、机制解释、反例和最小实验候选。
