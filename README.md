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