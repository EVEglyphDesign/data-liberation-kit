# LLM chat-history export

Cross-model export from ChatGPT, Claude, Perplexity, Copilot, and Gemini into your own repo. Whatever model you use next, your history stays yours.

## What it does

- Pulls conversation history from each supported model via its documented export path.
- Normalises every conversation to a single JSONL schema (one message per line).
- Stores under `history/llm/<model>/YYYY/MM/<conversation-id>.jsonl`.
- Emits manifest entries so tools can find and index everything.
- Runs on a schedule or on demand.

## Supported models (initial cut)

| Model | Path | Status |
|---|---|---|
| ChatGPT | OpenAI data export request | working |
| Claude | Anthropic data export request | working |
| Perplexity | Threads API (authenticated user) | working |
| Copilot (chat) | Microsoft data export request | working |
| Gemini | Google Takeout (Gemini section) | working |

Other models are on the [`WANTED.md`](../../WANTED.md) list. Contributions welcome.

## Configuration

```yaml
llm-history:
  enabled: true
  models:
    chatgpt: true
    claude: true
    perplexity: true
    copilot: true
    gemini: true
  schedule: "0 4 * * *"   # daily at 4am local
```

## Storage layout

```
history/llm/
├── chatgpt/YYYY/MM/<conv-id>.jsonl
├── claude/YYYY/MM/<conv-id>.jsonl
├── perplexity/YYYY/MM/<conv-id>.jsonl
├── copilot/YYYY/MM/<conv-id>.jsonl
├── gemini/YYYY/MM/<conv-id>.jsonl
└── manifests/YYYY-MM.jsonl
```

## Normalised message schema

Each line in a conversation JSONL:

```json
{
  "conversation_id": "provider-conv-id",
  "message_id": "provider-msg-id",
  "timestamp_utc": "2026-07-15T21:03:17Z",
  "role": "user | assistant | system | tool",
  "content": "the exact text",
  "model": "gpt-5-2 | claude-sonnet-5 | ...",
  "tokens_in": null,
  "tokens_out": null,
  "attachments": [],
  "source": {"module": "llm-history", "provider": "openai"}
}
```

## Running

```bash
./modules/llm-history/run.sh              # all enabled providers
./modules/llm-history/run.sh --provider chatgpt
```

## References

- OpenAI data export — https://help.openai.com/en/articles/7260999
- Anthropic data export — https://support.anthropic.com/
- Google Takeout (Gemini section) — https://takeout.google.com/
- Microsoft data export — https://account.microsoft.com/privacy
