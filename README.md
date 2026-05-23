# Closira AI Support Workflow

An AI-powered customer support workflow built for Bloom Aesthetics Clinic using FastAPI and LLM-based agents.

The system demonstrates:
- FAQ answering using SOP grounding
- lead qualification workflows
- escalation handling
- hallucination prevention
- session memory
- conversation summarisation

---

# Features

## FAQ Answering
The assistant answers customer questions using structured SOP data.

Examples:
- pricing
- services
- booking policies
- opening hours
- aftercare instructions

The workflow prevents unsupported or hallucinated responses.

---

## Lead Qualification

The assistant collects lead details such as:
- customer type
- business type
- team size
- support tools
- AI support goals

The qualification flow is session-aware and multi-step.

---

## Escalation Detection

The workflow escalates:
- medical questions
- complaints
- angry customers
- refund requests
- legal threats
- unsupported services
- low-confidence responses

---

## Conversation Summary

The system generates summaries including:
- customer intent
- lead details
- escalation reasons
- SOP gaps
- recommended next actions

---

## Session Memory

The workflow stores:
- messages
- qualification progress
- escalation state
- lead information

using session-based memory.

---

# Tech Stack

- FastAPI
- Python
- HTML
- CSS
- JavaScript
- NVIDIA API / LLM APIs
- OpenAI-compatible SDK

---

# Project Structure

```text
closira-ai-agent/

│
├── app/
│   ├── agents/
│   │   ├── escalation_agent.py
│   │   ├── faq_agent.py
│   │   ├── qualification_agent.py
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
│   └── sop_data.json
│
├── test_transcripts/
├── prompt_design.md
├── README.md
├── requirements.txt
└── .env.example
```

---

# Installation

## 1. Clone Repository

```bash
git clone <your_repo_url>
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate:

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file.

Example:

```env
NVIDIA_API_KEY=your_api_key
```

---

# Running The Application

Start FastAPI server:

```bash
uvicorn app.main:app --reload
```

Open browser:

```text
http://127.0.0.1:8000
```

---

# API Endpoints

## Home

```http
GET /
```

---

## Chat Endpoint

```http
POST /chat
```

Example request:

```json
{
  "session_id": "session-123",
  "message": "What are your Botox prices?"
}
```

---

## Conversation Summary

```http
GET /summary/{session_id}
```

---

## Session Data

```http
GET /session/{session_id}
```

---

# Example Workflow

## Customer

```text
What are your Botox prices?
```

## Assistant

```text
Our Botox treatments start at £200.
```

---

## Customer

```text
I want a refund.
```

## Assistant

Escalates conversation to human support.

---

# Hallucination Prevention

The assistant:
- only answers using SOP data
- avoids unsupported claims
- escalates uncertain responses
- blocks dangerous assumptions

The workflow prioritises safety over unrestricted generation.

---

# Frontend Features

- modern chat UI
- left/right message bubbles
- loading animation
- session tracking
- summary viewer
- responsive design

---

# Limitations

Current limitations:
- in-memory storage only
- keyword-based escalation
- no authentication
- no database persistence
- no vector search

---

# Future Improvements

Potential upgrades:
- PostgreSQL / Redis
- vector database retrieval
- semantic search
- admin dashboard
- streaming responses
- analytics
- authentication
- multilingual support

---

# Demo Files

Included:
- prompt_design.md
- test_transcripts/
- frontend UI
- workflow agents
- conversation summaries

---

# License

This project was created for educational and assessment purposes.