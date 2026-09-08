# OpsAgent – AI-Powered Incident Triage & Runbook Assistant

OpsAgent is an AI-powered incident management system built with **LangGraph** and **Next.js**. It ingests incoming alerts, classifies severity, matches relevant runbooks, escalates critical issues, and generates stakeholder summaries.

**Started** on Oct 2025

---

## Features

- **Multi-Provider LLM Support**: Choose between **OpenAI**, **Anthropic**, or **Google Gemini**.
- **Dual Configuration**: Configure API keys via environment variables (`.env`) or interactively in the Web UI **Settings** modal.
- **Concurrent Alert Processing**: Triage multiple incoming alerts in parallel using `ThreadPoolExecutor`.
- **Stateful Incident Management**: Bidirectional state synchronization for incident triage, runbook matching, and step execution.
- **Rule-Based Fallbacks**: Gracefully falls back to rule-based logic if LLM keys are missing or API calls fail.

---

## API Key Options & Configuration

OpsAgent supports three primary LLM providers. You can configure your preferred provider and API keys either via environment variables or directly inside the Web UI.

### Option 1: Configure via `.env`

Copy `.env.example` to `.env` and set your preferred provider and API keys:

```bash
# Set active provider: openai, anthropic, or gemini
LLM_PROVIDER=openai

# 1. OpenAI Key
OPENAI_API_KEY=sk-...

# 2. Anthropic Key
ANTHROPIC_API_KEY=sk-ant-...

# 3. Gemini Key
GEMINI_API_KEY=AIzaSy...
```

### Option 2: Configure via Web UI Settings Modal

1. Start the web app (`npm run dev`).
2. Click **⚙️ Settings** in the top navigation bar.
3. Select your active LLM provider (**OpenAI**, **Anthropic**, or **Gemini**).
4. Enter your API key(s) in the input fields and click **Save Configuration**. Keys are persisted securely in your browser's `localStorage`.

---

## Supported Providers & Models

| Provider | Models Supported | Key Environment Variable |
|---|---|---|
| **OpenAI** | `gpt-4o-mini`, `gpt-3.5-turbo` | `OPENAI_API_KEY` |
| **Anthropic** | `claude-3-5-sonnet`, `claude-3-haiku` | `ANTHROPIC_API_KEY` |
| **Gemini** | `gemini-1.5-flash`, `gemini-pro` | `GEMINI_API_KEY` or `GOOGLE_API_KEY` |

---

## Quick Start

### 1. Install Dependencies

**Python Backend:**
```bash
pip install -r agent/requirements.txt
```

**Frontend:**
```bash
npm install
```

### 2. Run the Application

**Run Web UI & Python Agent:**
```bash
npm run dev
```

**Run LangGraph Agent Standalone:**
```bash
python agent/graph.py
```

---

## Project Structure

```
OpsAgent/
├── agent/
│   ├── graph.py                 # LangGraph workflow definition
│   ├── state.py                 # TypedDict definitions for AgentState
│   ├── requirements.txt         # Python dependencies (LangChain, OpenAI, Anthropic, Gemini)
│   └── tools/
│       ├── llm_factory.py       # Dynamic LLM Provider Factory (OpenAI / Anthropic / Gemini)
│       ├── classification_tool.py# Severity & category classification
│       ├── summarization_tool.py# Incident summary generator
│       ├── alert_tool.py        # Alert ingestion tool
│       ├── runbook_matching_tool.py # Runbook lookup tool
│       └── incident_updater_tool.py # Incident status manager
├── src/
│   ├── app/                     # Next.js app routes
│   └── components/
│       ├── settings/
│       │   └── api-key-modal.tsx# Modal for OpenAI, Anthropic, and Gemini API keys
│       └── layout/
│           └── shell.tsx        # Shell layout with Settings button
├── .env.example                 # Environment variable template with 3 API key options
└── README.md                    # Documentation
```

---

## License

MIT License.