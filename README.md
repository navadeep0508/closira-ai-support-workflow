# Closira AI Support Workflow

An AI-powered customer support workflow built for Bloom Aesthetics Clinic using FastAPI and LLM-based agents.

The system demonstrates:
- SOP-grounded FAQ answering
- AI-driven lead qualification
- escalation handling
- hallucination prevention
- session memory
- conversation summarisation
- hybrid AI workflow orchestration

---

# Live Demo

Live Application:

https://closira-ai-support-workflow.onrender.com

GitHub Repository:

https://github.com/navadeep0508/closira-ai-support-workflow.git

---

# Features

## SOP-Grounded FAQ Answering

The assistant answers customer questions strictly using structured SOP data.

Examples:
- pricing
- services
- booking policies
- opening hours
- aftercare instructions

The workflow prevents unsupported or hallucinated responses.

---

## AI-Driven Lead Qualification

The workflow uses hybrid AI orchestration:
- backend-controlled session memory
- AI-generated contextual follow-up questions

Instead of rigid scripted questioning, the assistant dynamically:
- understands user intent
- asks natural follow-up questions
- avoids unnecessary qualification
- adapts conversation flow

Examples:
- consultation booking
- service interest
- business workflow discovery
- AI support goals

---

## Intelligent Escalation Detection

The workflow combines:
- rule-based escalation
- AI-based risk prediction

The assistant escalates:
- medical questions
- complaints
- refund requests
- pricing negotiations
- legal threats
- unsafe requests
- unsupported services
- low-confidence responses

Predicted risk categories:
- medical
- complaint
- pricing
- legal
- unsafe

---

## Conversation Summary

The system generates summaries including:
- customer intent
- lead details
- escalation reasons
- SOP gaps
- recommended next actions

This simulates real CRM and customer support workflows.

---

## Session Memory

The workflow stores:
- conversation messages
- lead details
- escalation state
- qualification progress

using session-based in-memory storage.

---

# Tech Stack

- FastAPI
- Python
- HTML
- CSS
- JavaScript
- NVIDIA NIM API
- OpenAI-compatible SDK
- Llama 3.1 Instruct Models

---

# Project Structure

```text
closira-ai-support-workflow/

│
├── app/
│   ├── agents/
│   │   ├── escalation_agent.py
│   │   ├── faq_agent.py
│   │   └── summary_agent.py
│   │
│   ├── models/
│   │   └── schemas.py
│   │
│   ├── static/
│   │   ├── app.js
│   │   └── style.css
│   │
│   ├── templates/
│   │   └── index.html
│   │
│   ├── utils/
│   │   ├── memory.py
│   │   └── prompts.py
│   │
│   ├── main.py
│   │
│   └── sop_data.json
│
├── test_transcripts/
├── prompt_design.md
├── README.md
├── requirements.txt
└── .env.example
```

---

# Setup

Requirements:
- Python 3.10+
- An NVIDIA NIM API key (free tier works) — https://build.nvidia.com

Clone and install:

```bash
git clone https://github.com/navadeep0508/closira-ai-support-workflow.git
cd closira-ai-support-workflow

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file in the project root (see `.env.example`):

```text
NVIDIA_API_KEY=your_api_key_here
```

The key is loaded in `app/agents/faq_agent.py` and used against the OpenAI-compatible NVIDIA NIM endpoint (`https://integrate.api.nvidia.com/v1`) with the `meta/llama-3.1-8b-instruct` model.

---

# Running locally

Start the FastAPI server:

```bash
uvicorn app.main:app --reload --port 8000
```

Then open `http://localhost:8000` in a browser to use the chat UI, or call the API directly:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "demo-1", "message": "What are your Botox prices?"}'
```

Endpoints:

| Method | Path | Purpose |
|---|---|---|
| `GET`  | `/`                       | Chat UI |
| `POST` | `/chat`                   | Send a customer message, get the AI reply + escalation flags |
| `GET`  | `/summary/{session_id}`   | Generate a structured end-of-session summary |
| `POST` | `/reset/{session_id}`     | Clear a session |

The assignment notes that a CLI is sufficient — a minimal one is also available by running the FAQ agent directly:

```bash
python -m app.agents.faq_agent
```

---

# Dependencies

Pinned in `requirements.txt`:

- `fastapi` — HTTP framework
- `uvicorn` — ASGI server
- `jinja2` — HTML templating for the demo UI
- `python-dotenv` — load `NVIDIA_API_KEY` from `.env`
- `openai` — OpenAI-compatible SDK, pointed at NVIDIA NIM
- `python-multipart` — form parsing for FastAPI

No external database, vector store, or background worker is required.

---

# Trade-offs and known limitations

- **In-memory sessions.** Session state lives in a process-local dict (`app/utils/memory.py`) with a 1-hour TTL and a 50-message cap. Restarting the server clears all sessions, and the app does not scale horizontally without a shared store (Redis, etc.).
- **Single LLM provider.** Wired to NVIDIA NIM via the OpenAI SDK. Swapping to OpenAI or Anthropic only requires changing `base_url` / `model` in `faq_agent.py`, but no abstraction layer is in place.
- **Hybrid escalation.** A keyword-based escalator (`escalation_agent.py`) runs first for fast, deterministic catches (medical, pricing, legal, complaint, angry, out-of-scope). The LLM provides a second layer via `predicted_risk` and a confidence threshold (0.4). Keywords use word-boundary regex to avoid false positives like `pain` matching `painting`.
- **No retrieval over SOP.** The full `sop_data.json` is included in every prompt. This is fine for the demo SOP size but will cost tokens as the SOP grows; a small retrieval step would be the next step.
- **No automated tests.** `test_transcripts/` contains hand-written sample conversations per expected behaviour rather than executable tests.
- **Lead qualification is LLM-driven.** Instead of a fixed 2–3 question script, the LLM generates contextual follow-ups guided by `build_dynamic_context()` in `faq_agent.py`. This is more natural but less deterministic than a hard-coded flow — sometimes the model decides one good question is enough.
- **No authentication or rate-limiting.** The deployed demo is open; treat it as a public sandbox, not production.
- **English-only.** Keywords, prompt, and tests are English only.

---

# Test transcripts

`test_transcripts/` covers the five expected behaviours from the assignment plus extras:

| File | Behaviour |
|---|---|
| `faq_test.md` | In-SOP question |
| `out_of_scope_test.md` | Out-of-scope question, escalated |
| `complaint_test.md` | Escalation trigger (frustration / complaint) |
| `medical_escalation_test.md` | Escalation trigger (medical) |
| `pricing_negotiation_test.md` | Escalation trigger (pricing) |
| `qualification_test.md` | Lead qualification flow |
| `summary_test.md` | End-of-session structured summary |
| `hallucination_prevention_test.md` | SOP-boundary guardrail |