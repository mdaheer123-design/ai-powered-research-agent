<div align="center">

# 🔬 ResearchAgent

**An autonomous AI agent that plans, searches, verifies, and writes cited research reports — end to end, no human in the loop.**

Powered by **Groq** (Llama 3.3 70B) with automatic fallback to **Gemini** — both free tier, no paid APIs required.

[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Groq](https://img.shields.io/badge/LLM-Groq%20%2F%20Llama%203.3-orange.svg)](https://console.groq.com)
[![Gemini](https://img.shields.io/badge/Fallback-Gemini%202.0%20Flash-4285F4.svg)](https://aistudio.google.com)
[![Live Demo](https://img.shields.io/badge/Live-Demo-success.svg?style=flat&logo=render)](https://ai-powered-research-agent-0nm3.onrender.com/)

[Live Demo](https://ai-powered-research-agent-0nm3.onrender.com/) • [Features](#features) • [How It Works](#how-it-works) • [Quick Start](#quick-start) • [Architecture](#architecture)

</div>

---

## Overview

Most "AI agent" demos are a single prompt-response with a search tool bolted on. **ResearchAgent** is different — it is a genuine multi-step orchestration loop:

> **Plan** the sub-questions → **Act** by calling tools → **Observe** the results → **Reflect** on what is missing → repeat until the research is actually done → **write a structured, cited report**.

Give it a question. It comes back with a verified, source-linked Markdown report — flagging anything it could not confirm instead of guessing.

## Features

- **Genuine agentic loop** — Plan → Act → Observe → Reflect, not a single-shot RAG call.
- **Dual-LLM resilience** — Groq primary, Gemini automatic fallback on error/rate-limit, zero paid API keys required.
- **Real tool orchestration** — `search_web`, `read_webpage`, and `calculator` with robust dual-format parsing (handles both JSON and XML tool call formats).
- **Fact verification** — Cross-checks claims across multiple sources and explicitly flags conflicts.
- **Structured, cited output** — Every claim traces to a source URL; final report follows a consistent Markdown schema.
- **Live streaming UI** — Real-time Server-Sent Events (SSE) stream the agent's thought process to a polished React frontend.
- **Portfolio-ready design** — Clean, dark-mode UI with tool activity visualization, copy-to-clipboard, and responsive layout.

## How It Works

```
┌─────────────┐     ┌──────────────────────────────────────────────┐     ┌─────────────┐
│   User asks │ --> │            AGENT REASONING LOOP              │ --> │   Report.md │
│  a question │     │                                              │     │  (cited,    │
└─────────────┘     │  1. PLAN    → break into sub-questions       │     │  verified)  │
                    │  2. ACT     → search_web / read_webpage /    │     └─────────────┘
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

Create a `.env` file in the project root:

```
GROQ_API_KEY=gsk_...
GEMINI_API_KEY=AIza...
```

### 4. Run

**Web UI (recommended):**
```bash
python server.py
```
Then open [http://localhost:8000](http://localhost:8000) in your browser.

**CLI mode:**
```bash
python main.py "your research question here"
```

## Architecture

```
AI-powered-research-agent/
├── server.py             # FastAPI server — SSE streaming endpoint
├── agent.py              # Core agent — LLM orchestration, tool loop, dual-engine fallback
├── tools.py              # Tool implementations — search_web, read_webpage, calculator
├── main.py               # CLI entry point with Rich console output
├── index.html            # React frontend — live agent activity UI
├── requirements.txt      # Python dependencies
├── .env                  # API keys (not committed)
└── README.md
```

**Key design decisions:**
- **Fallback over single point of failure** — If Groq errors or rate-limits (common on free tiers), the agent automatically falls back to Gemini rather than failing the whole task.
- **Robust tool call parsing** — A dual-format parser handles both JSON `{"tool": ...}` and XML `<function=...>` formats, making the system resilient to LLM output variations.
- **Explicit uncertainty over confident hallucination** — The system prompt requires the agent to label unresolved or conflicting findings rather than smoothing them over.

## Tech Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI, Uvicorn |
| Primary LLM | Groq (Llama 3.3 70B Versatile) |
| Fallback LLM | Google Gemini 2.0 Flash |
| Web Search | DuckDuckGo (via ddgs) |
| Web Scraping | Requests + BeautifulSoup4 |
| Frontend | React 18, Tailwind CSS, Lucide Icons |
| Streaming | Server-Sent Events (SSE) |

## Contributing

Issues and Pull Requests are welcome.

## License

MIT

---

<div align="center">
<sub>Built by <a href="https://github.com/senthamizhvelan04">Senthamizh Velan</a> — a demonstration of agentic reasoning and tool orchestration, not just single-shot LLM calls.</sub>
</div>
