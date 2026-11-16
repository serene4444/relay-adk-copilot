# FieldKit evaluation results

Model: `gemini-3.5-flash` · Questions: 20 · "Today" pinned to 2026-11-14

| Metric | How it's measured | Result |
|---|---|---|
| Answer accuracy | LLM judge vs. expected answer | 18 / 20 |
| Routing accuracy | Called exactly the expected specialists | 19 / 20 |
| Safety | Trick questions refused safely | 4 / 4 |
| Fixes from self-review | Drafts the reviewer sent back | 3 |
| Median latency | Question to final answer | 8.9 s |
| Tokens per second | Output tokens / model generation time | 144 |
| Cost per request | Tokens x list price (median) | $0.0179 |

Orders database unchanged by the run: **yes** (SHA-256 898bfe22b561 before, 898bfe22b561 after)
Errors: 0
