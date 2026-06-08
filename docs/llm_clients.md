# LLM API 客户端与 smoke test

本仓库提供最小依赖的 LLM API 调用入口，用于后续 prompt optimization baseline、optimizer 和配置连通性检查。当前实现只使用 Python 标准库，避免在第一阶段引入额外依赖。

## 支持范围

| Provider | 入口 | 默认模型 | API |
| --- | --- | --- | --- |
| OpenAI | `scripts.llm_clients.call_openai_response` | `gpt-5.2` | Responses API |
| OpenRouter | `scripts.llm_clients.call_openrouter_chat` | `openai/gpt-5.2` | Chat Completions API |

## 配置

复制 `.env.example` 为本地 `.env`，再填入需要使用的 key。真实 API key 只能保存在本地 `.env`，不得提交。

```dotenv
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-5.2

OPENROUTER_API_KEY=
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=openai/gpt-5.2
```

完整可配置项以 `.env.example` 为准，包括超时、输出 token 上限、OpenAI reasoning effort、OpenAI text verbosity、OpenRouter temperature 和 OpenRouter app headers。

## Dry-run 检查

默认不发送真实网络请求，只打印即将发送的请求结构，并隐藏 `Authorization`：

```bash
python scripts/llm_smoke_test.py
```

单独检查某个 provider：

```bash
python scripts/llm_smoke_test.py --provider openai
python scripts/llm_smoke_test.py --provider openrouter
```

## Live 检查

填好 `.env` 后，可以发送真实请求：

```bash
python scripts/llm_smoke_test.py --provider openai --live
python scripts/llm_smoke_test.py --provider openrouter --live
```

Live smoke test 只用于验证 key、base URL、模型名和基础响应解析是否正常，不构成实验结果。正式实验仍需记录数据集版本、prompt 版本、模型参数、评分器、成本和失败案例。

## Python 调用

```python
from scripts.llm_clients import call_openai_response, extract_openai_text, load_dotenv

load_dotenv()

response = call_openai_response(
    prompt="请用一句话回复：LLM API 配置正常。",
    instructions="你是一个用于验证 API 配置的测试助手。",
)
text = extract_openai_text(response)
```

## 研究约束

- 每次实验必须显式记录 provider、model、base URL、参数和 token 预算。
- 更换模型或 provider 视为实验变量变化，不能和 prompt 改写混在同一轮单变量结论中。
- `dry_run` 只能验证请求结构，不能作为质量、延迟或成本指标。
- API 错误应记录为环境或配置问题，不能混入 prompt 质量失败案例。
