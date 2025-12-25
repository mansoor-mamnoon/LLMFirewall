# Prompt Injection Lab — Day 1 Spec

## Goal (MVP)
Build a prompt-injection red-teaming + defense prototype for an LLM agent runtime.
By Day 5, we should be able to run a benchmark suite of attacks against:
1) no defense, and 2) a baseline defense middleware,
and report Attack Success Rate (ASR), False Positive Rate (FPR), and latency overhead.

## Threat Model
We defend an LLM agent that receives inputs from multiple channels:
- **System** (trusted)
- **User** (untrusted)
- **Retrieved documents (RAG)** (untrusted)
- **Tool outputs** (untrusted)
- **Conversation history** (mixed; treated as untrusted unless authored by system)

Attack classes:
1. **Direct prompt injection:** user tries to override system rules (e.g., "ignore previous instructions").
2. **Indirect prompt injection:** malicious instructions embedded in RAG documents or tool outputs.
3. **Multi-turn escalation:** attacker gradually induces the agent to adopt new goals or call tools.

Out of scope for MVP: model-side fine-tuning defenses, jailbreaks requiring model weight access, or OS-level sandboxing.

## Target System
A minimal agent runtime that can:
- take system + user + context docs + tool schemas,
- decide between returning an answer or calling a tool,
- log full traces for evaluation.

Tools (initial):
- `search_docs(query)` -> returns snippets from a local corpus
- `get_email(id)` -> returns text from local fixtures
- `post_message(channel, text)` -> writes to a local log (simulated side effect)

## Deliverables
1. **Benchmark runner** (`eval/`): replays attack cases against the runtime and records outcomes.
2. **Defender middleware** (`runtime_guard/`): detectors + policy engine with actions:
   - allow / block / rewrite / downgrade tools
3. **Dashboard/report**: at minimum, a generated Markdown/HTML report with metrics and example traces.

## Success Criteria
- Local: `make lint` and `make test` pass.
- CI: GitHub Actions runs lint + tests on push and is green.
- Spec: this document exists and clearly defines threat model, target, deliverables.
