<div align="center">

# ResearchAgent

**An autonomous AI agent that plans, searches, verifies, and writes cited research reports — end to end, no human in the loop.**

Powered by **Groq** (Llama 3.3 70B) with automatic fallback to **Gemini** — both free tier, no paid APIs required.

[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Groq](https://img.shields.io/badge/LLM-Groq%20%2F%20Llama%203.3-orange.svg)](https://console.groq.com)
[![Gemini](https://img.shields.io/badge/Fallback-Gemini%202.0%20Flash-4285F4.svg)](https://aistudio.google.com)

[Features](#features) • [How It Works](#how-it-works) • [Quick Start](#quick-start) • [Architecture](#architecture) • [Roadmap](#roadmap)

</div>

---

## Overview

Most "AI agent" demos are a single prompt-response with a search tool bolted on. **ResearchAgent** is different — it is a genuine multi-step orchestration loop:

> **Plan** the sub-questions → **Act** by calling tools → **Observe** the results → **Reflect** on what is missing → repeat until the research is actually done → **write a structured, cited report**.

Give it a question. It comes back with a verified, source-linked Markdown report — flagging anything it could not confirm instead of guessing.

```bash
python agent.py "What are the leading approaches to small modular nuclear reactors in 2026, and who are the key companies?"
```

## Features

- **Genuine agentic loop** — Plan → Act → Observe → Reflect, not a single-shot RAG call.
- **Dual-LLM resilience** — Groq primary, Gemini automatic fallback on error/rate-limit, zero paid API keys.
- **Real tool orchestration** — native function/tool calling (not prompt-hacked), with `web_search`, `fetch_page`, and `calculator`.
- **Fact verification** — cross-checks claims across multiple sources and explicitly flags conflicts or unresolved points instead of hallucinating a confident answer.
- **Structured, cited output** — every claim traces to a source URL; final report follows a consistent Markdown schema.
- **Configurable guardrails** — hard iteration cap, retry limits per sub-question, and graceful "here is what is incomplete" termination instead of silent partial answers.
- **Premium UI prompt included** — a ready-to-use design brief for building a polished, animated frontend on top of the agent (see [`UI_PROMPT.md`](./UI_PROMPT.md)).

## How It Works

```
┌─────────────┐     ┌──────────────────────────────────────────────┐     ┌─────────────┐
│   User asks │ --> │            AGENT REASONING LOOP              │ --> │   Report.md │
│  a question │     │                                              │     │  (cited,    │
└─────────────┘     │  1. PLAN    → break into 3-6 sub-questions   │     │  verified)  │
                    │  2. ACT     → web_search / fetch_page /      │     └─────────────┘
                    │               calculator                     │
                    │  3. OBSERVE → extract facts + source + date  │
                    │  4. REFLECT → resolved? conflicting? retry?  │
                    │                                              │
                    │  repeats until plan complete or limit reached│
                    └──────────────────────────────────────────────┘
                              ↑                          ↓
                        ┌──────────┐              ┌─────────────┐
                        │   Groq   │──fallback──→ │   Gemini    │
                        │ (primary)│              │ (fallback)  │
                        └──────────┘              └─────────────┘
```

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/senthamizhvelan04/AI-powered-research-agent.git
cd AI-powered-research-agent
pip install -r requirements.txt
```

### 2. Get Free API Keys

| Provider | Link | Notes |
|---|---|---|
| Groq | [console.groq.com/keys](https://console.groq.com/keys) | Primary reasoning engine, generous free rate limits |
| Gemini | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) | Optional but recommended fallback |

### 3. Set Environment Variables

```bash
export GROQ_API_KEY="gsk_..."
export GEMINI_API_KEY="AIza..."   # optional
```

### 4. Run the Agent

```bash
python agent.py "your research question here"
```

The report prints to the console and is saved to `report.md` in the working directory.

## Architecture

```
research-agent/
├── agent.py              # Core agent: LLM orchestration, tool loop, fallback logic
├── requirements.txt      # groq, google-generativeai, ddgs, requests, beautifulsoup4
├── SYSTEM_PROMPT.md      # Full production system prompt used by the agent
├── UI_PROMPT.md          # Design brief for building a premium frontend on top
├── README.md
└── report.md             # Generated on each run (gitignored recommended)
```

**Key design decisions:**
- **Fallback over single point of failure** — if Groq errors or rate-limits (common on free tiers), the agent automatically retries then falls back to Gemini rather than failing the whole task.
- **Tool calls are native, not parsed from text** — uses OpenAI-style structured function calling on both backends (via an adapter for Gemini's function-call format), which is far more reliable than regex-parsing a "Thought/Action" text format.
- **Explicit uncertainty over confident hallucination** — the system prompt requires the agent to label unresolved or conflicting findings rather than smoothing them over.

## Configuration

Key tunables at the top of `agent.py`:

| Variable | Default | Purpose |
|---|---|---|
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Primary reasoning model |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Fallback model |
| `MAX_ITERATIONS` | `18` | Hard cap on reasoning/tool-call loops |
| `MAX_SEARCH_RESULTS` | `5` | Results returned per `web_search` call |
| `MAX_FETCH_CHARS` | `6000` | Truncation limit for fetched page text |
| `RETRY_ATTEMPTS` | `3` | Retries on Groq before falling back to Gemini |

## Roadmap

- [ ] Swap DuckDuckGo for a paid search API (Serper/Tavily/Bing) as an optional higher-reliability backend.
- [ ] Persistent cache of fetched pages (SQLite or Chroma) to avoid re-fetching across runs.
- [ ] FastAPI wrapper for an HTTP endpoint and SSE streaming of live agent steps.
- [ ] Frontend implementation from [`UI_PROMPT.md`](./UI_PROMPT.md) — live agent-activity visualization.
- [ ] Structured tracing/observability (LangSmith or Helicone).
- [ ] Per-user step and cost budgets for public deployment.

## Contributing

Issues and Pull Requests are welcome. If you add a new tool, update both `TOOL_IMPLEMENTATIONS` and `TOOL_SCHEMAS` in `agent.py`, and reflect it in `SYSTEM_PROMPT.md` so the model knows when to use it.

## License

MIT — see [LICENSE](./LICENSE).

---

<div align="center">
<sub>Built as a demonstration of agentic reasoning and tool orchestration, not just single-shot LLM calls.</sub>
</div>
