# Prompt Design Documentation

# Objective

The goal of this project is to build a safe AI-powered customer support workflow for Bloom Aesthetics Clinic.

The assistant must:
- answer FAQs using SOP data
- collect lead qualification details
- escalate risky conversations
- avoid hallucinations
- generate conversation summaries

---

# Core System Prompt

```text
You are a safe AI customer support assistant for Bloom Aesthetics Clinic.

You must answer ONLY using the provided SOP DATA.

The SOP may include:
- services
- pricing
- booking policies
- cancellation rules
- payment methods
- aftercare instructions
- FAQs

Rules:
- Never invent information
- Never hallucinate
- Never assume unavailable services
- If information is not explicitly present:
    - do not guess
    - do not assume
    - escalate instead

Escalate:
- medical questions
- customer complaints
- legal threats
- pricing negotiation
- unsupported services
- low confidence responses

Always respond in valid JSON format.

Required JSON format:

{
    "answer": "string",
    "confidence": 0.0,
    "escalate": false,
    "reason": "string"
}
```

---

# Prompt Engineering Strategy

The prompting strategy focuses on:

1. SOP grounding
2. hallucination prevention
3. structured outputs
4. safe escalation handling
5. workflow consistency

The model is explicitly restricted from generating information outside the SOP.

---

# Why SOP Grounding Was Used

SOP grounding ensures:
- factual consistency
- safer business responses
- reduced hallucinations
- predictable outputs

Instead of open-ended generation, the assistant only uses information available in the provided SOP data.

The SOP data is dynamically injected into the prompt during runtime.

Example:

```python
SOP DATA:
{json.dumps(SOP_DATA, indent=2)}
```

This creates grounded and controlled responses.

---

# Hallucination Prevention

Hallucination prevention is a core design goal.

The assistant is instructed to:
- never invent services
- never assume unavailable treatments
- escalate unknown questions
- avoid unsupported claims

Example:

Customer:
Do you provide heart surgery?

Correct behavior:
Escalate to a human agent.

Incorrect behavior:
“We do not offer heart surgery.”

The second response is considered hallucination because the SOP never explicitly states it.

The workflow prioritises escalation over uncertainty.

---

# Confidence Threshold Logic

The workflow uses confidence-based escalation.

If the model confidence score falls below:

```python
0.4
```

the system automatically escalates the conversation.

Reason:
- reduces unreliable responses
- prevents hallucinated answers
- improves workflow safety

Example:

```json
{
  "answer": "I am not fully confident in this response.",
  "confidence": 0.2,
  "escalate": true,
  "reason": "Low confidence response"
}
```

---

# Escalation Design

Escalation logic handles risky or unsupported conversations.

The system escalates:
- medical advice requests
- angry customers
- complaints
- refund requests
- legal threats
- unsupported services
- low-confidence answers

Examples:
- “Is Botox safe during pregnancy?”
- “I want a refund.”
- “Can you lower the price?”
- “I will sue your clinic.”

Escalation prioritises safety over incorrect automation.

The assistant intentionally escalates uncertain or risky situations instead of generating potentially unsafe responses.

---

# Structured JSON Responses

The assistant always returns structured JSON.

Benefits:
- reliable frontend integration
- easier parsing
- production-style API behavior
- safer automation

Structured JSON was selected because it:
- simplifies frontend integration
- enables workflow automation
- improves parsing reliability
- supports future API integrations
- creates production-style AI pipelines

Example:

```json
{
  "answer": "Our Botox treatments start at £200.",
  "confidence": 0.95,
  "escalate": false,
  "reason": ""
}
```

---

# Lead Qualification Workflow

The system collects:
- customer type
- business type
- team size
- current support tools
- AI support goals

The workflow maintains:
- session memory
- question tracking
- qualification completion state

This creates a multi-step AI workflow instead of a simple chatbot.

---

# Session Memory Design

Conversation memory is stored using:
- session_id-based tracking
- in-memory Python dictionary

Stored data includes:
- conversation messages
- lead details
- escalation state
- qualification progress

This allows the workflow to maintain conversational context across multiple interactions.

---

# Summary Generation

The summary system extracts:
- customer intent
- services discussed
- lead information
- SOP gaps
- escalation reasons
- next recommended action

This simulates real CRM/support workflows.

Example outputs:
- customer intent
- qualification status
- escalation details
- unsupported SOP areas
- recommended follow-up actions

---

# Safety Decisions

The assistant avoids:
- medical recommendations
- unsupported claims
- fabricated pricing
- unsafe advice
- assumptions beyond SOP data

Escalation is preferred over uncertain responses.

The workflow intentionally prioritises safety and reliability over creativity.

---

# Workflow Architecture

The workflow architecture separates:
- FAQ answering
- escalation handling
- qualification logic
- summarisation

into modular agents for maintainability and scalability.

Main workflow components:
- FAQ Agent
- Escalation Agent
- Qualification Agent
- Summary Agent

This modular architecture improves:
- readability
- maintainability
- scalability
- testing

---

# Limitations

Current limitations:
- in-memory storage only
- keyword-based escalation
- free model rate limits
- no persistent database
- no authentication system

The current implementation is designed as an MVP workflow prototype.

---

# Future Improvements

Potential future upgrades:
- Redis/PostgreSQL storage
- vector database retrieval
- semantic search
- sentiment analysis
- streaming responses
- authentication
- analytics dashboard
- multilingual support
- retrieval-augmented generation (RAG)
- admin monitoring dashboard

---

# Conclusion

This project demonstrates:
- AI workflow orchestration
- safe LLM integration
- SOP-grounded customer support
- escalation handling
- session memory
- structured AI systems design
- prompt engineering
- workflow modularisation

The workflow was intentionally designed to prioritise:
- safety
- reliability
- predictable behaviour
- maintainability

over unrestricted generative responses.

The final system behaves more like a controlled production support workflow rather than an unrestricted chatbot.