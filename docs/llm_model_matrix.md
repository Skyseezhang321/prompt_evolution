# LLM Model Matrix

Updated: 2026-06-08

This project keeps provider model choices in `.env` so prompt optimization
experiments can run the same prompt across a small, representative matrix.

## OpenAI

Source checks:
- Official docs identify GPT-5.5 as the latest frontier GPT-5 model.
- The local `OPENAI_API_KEY` was checked against `GET /v1/models`.

Configured `OPENAI_MODELS`:
- `gpt-5.5`
- `gpt-5.5-pro`
- `gpt-5.4`
- `gpt-5.4-pro`
- `gpt-5.4-mini`
- `gpt-5.4-nano`

Smoke-test note: `gpt-5.5-pro` and `gpt-5.4-pro` reject
`reasoning.effort=none`, so `scripts/llm_smoke_test.py` uses `medium` for
`*-pro` models.

## OpenRouter

Source checks:
- OpenRouter `GET /api/v1/models?output_modalities=text` was used to inspect
  current model ids, names, creation timestamps, context windows, pricing, and
  supported parameters.

Configured `OPENROUTER_MODELS`:
- `deepseek/deepseek-v4-pro`
- `qwen/qwen3.7-max`
- `z-ai/glm-5.1`
- `minimax/minimax-m3`
- `moonshotai/kimi-k2.6`

## Live Smoke Test

Command:

```powershell
python scripts\llm_smoke_test.py --provider all --live
```

Result: all configured models returned a non-empty response.

OpenAI:
- `gpt-5.5`: ok
- `gpt-5.5-pro`: ok
- `gpt-5.4`: ok
- `gpt-5.4-pro`: ok
- `gpt-5.4-mini`: ok
- `gpt-5.4-nano`: ok

OpenRouter:
- `deepseek/deepseek-v4-pro`: ok
- `qwen/qwen3.7-max`: ok
- `z-ai/glm-5.1`: ok
- `minimax/minimax-m3`: ok
- `moonshotai/kimi-k2.6`: ok
