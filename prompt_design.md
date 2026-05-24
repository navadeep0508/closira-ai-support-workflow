# Prompt Design Documentation

This document explains the prompt and workflow design behind the Closira AI customer support workflow built for Bloom Aesthetics Clinic. It covers the four areas the assignment asks for: the full system prompt, hallucination prevention, confidence-based escalation, and tone & persona — with the reasoning behind each choice.

---

## Objective

Build a safe, SOP-grounded customer support assistant that:

- answers FAQs strictly from `app/sop_data.json`
- qualifies leads with natural follow-up questions
- escalates risky or out-of-scope conversations to a human
- never invents information
- produces a structured end-of-session summary

The design is a **hybrid workflow**: deterministic Python code owns session state, escalation keyword detection, and the post-call confidence/risk checks; the LLM owns the natural-language reply, intent classification, and follow-up question generation. This split keeps safety-critical decisions out of the model's hands while letting the model do what it's good at.

---

## 1. System Prompt

The system prompt is composed in two layers:

**Layer A — fixed system role**, set when calling the model in `app/agents/faq_agent.py`:

```text
You are a safe customer support AI.
Always respond ONLY with valid JSON.
```

**Layer B — task prompt** built per-request, combining `SYSTEM_PROMPT` from `app/utils/prompts.py`, the full SOP data, the running conversation context, and dynamic qualification guidance:

```text
You are a safe AI customer support assistant
for Bloom Aesthetics Clinic.

You must answer ONLY using the provided SOP DATA.

Rules:
- Never invent information
- Never hallucinate
- Never assume unavailable services
- If information is not explicitly present:
  escalate instead of guessing

Conversation Rules:
- Respond naturally
- Avoid robotic qualification
- Ask follow-up questions only if relevant
- Do not ask unnecessary questions
- Service-related users should receive service-related follow-ups
- Business users should receive business-related follow-ups
- Stop asking questions once enough information is collected

Escalate:
- medical advice requests
- pricing negotiation
- complaints
- legal threats
- unsafe requests
- unsupported services
- low confidence responses

Always return valid JSON only.
```

The runtime prompt then appends:

```text
SOP DATA: { ...full sop_data.json... }
Conversation Context: { ...session state... }
Dynamic Qualification Context: { ...business or individual goals... }
Customer Message: { ...latest user message... }

Required JSON format:
{
  "answer": "string",
  "confidence": 0.0,
  "escalate": false,
  "reason": "string",
  "next_question": "string",
  "qualification_complete": false,
  "detected_intent": "string",
  "detected_customer_type": "string",
  "predicted_risk": "string"
}
```

### Why this structure

- **Two-layer prompt.** The minimal system role enforces JSON-only output even if the task prompt is malformed. The task prompt carries everything the model needs to answer.
- **SOP injected inline, not summarised.** The model never reasons about a paraphrased SOP — it reasons about the source of truth. This is the simplest way to keep answers grounded for a SOP of this size.
- **Conversation context injected.** The model sees prior turns and `lead_data`, so follow-ups stay coherent and qualification doesn't repeat itself.
- **Dynamic qualification context.** A small `build_dynamic_context(session)` function in `faq_agent.py` swaps in a business-lead goal list or an individual-customer goal list depending on the detected `customer_type`. This avoids asking a clinic patient about their "team size" and asking a business lead about "treatment options".
- **Structured JSON output.** Every reply must conform to a fixed schema. The Python layer can then make safety decisions (escalate, log, store) without parsing free-form text.

---

## 2. Hallucination Prevention

Hallucinations are the highest-risk failure mode for a clinic assistant. The design uses **four overlapping defences**:

### 2a. Explicit SOP-only instruction
The prompt states three times, in different forms, that the model must answer *only* from `SOP DATA` and *escalate* — not guess — when information is missing. Repeating the rule in three different framings ("Never invent", "Never assume", "If information is not explicitly present: escalate") is intentional: it raises the chance the model attends to it even when the user's question is leading.

### 2b. Out-of-scope guard before the LLM call
A small allowlist of *clearly* out-of-scope topics (`heart surgery`, `brain surgery`, `cancer treatment`, `insurance`, `hospital admission`, etc.) short-circuits the call in `faq_agent.py` before the LLM ever sees the input. This is faster, cheaper, and impossible for the model to override.

### 2c. Confidence threshold
The model emits a `confidence` score between 0.0 and 1.0 alongside its answer. If `confidence < 0.4`, the Python layer flips `escalate=true` regardless of what the model said. This catches cases where the model produced an answer but knew it was uncertain.

### 2d. Predicted-risk override
The model also emits `predicted_risk ∈ {medical, complaint, pricing, legal, unsafe, none}`. Any of the first five categories forces an escalation, and the user-visible reply is replaced with a category-specific message (`I'm unable to provide medical advice…`, `I'm unable to negotiate pricing directly…`, etc.). The model's free-form answer is never shown for these categories.

### 2e. Graceful fallback
If the model is unreachable, returns invalid JSON, or returns an empty answer, `safe_fallback()` returns a fixed apology + escalate-true response. Better to hand off than to bluff.

The combined effect: for a request to receive an LLM-generated answer, it has to (a) pass the keyword guard, (b) pass the SOP-grounded prompt, (c) clear the 0.4 confidence floor, and (d) not be flagged as risky.

---

## 3. Confidence-Based Escalation

Escalation is the most safety-relevant decision, so it's deliberately overdetermined — multiple independent signals can each trigger it, and any one of them is enough.

### Signal A — keyword pre-filter (rule-based, deterministic)
`app/agents/escalation_agent.py` runs first. Word-boundary regexes match against six categories:

| Category | Examples |
|---|---|
| `complaint` | "refund", "very disappointed", "worst clinic", "manager" |
| `medical` | "side effects", "pregnant", "bleeding", "allergic reaction" |
| `pricing` | "discount", "negotiate", "lower price", "too expensive" |
| `angry` | "frustrated", "useless", "waste of money" |
| `legal` | "lawsuit", "sue", "lawyer", "court" |
| `out_of_scope` | "heart surgery", "ambulance", "mri scan" |

A match returns the category and short-circuits the LLM call with a category-specific message (`escalation_message(category)` in `escalation_agent.py`). This makes escalation **fast**, **deterministic**, and **testable** for the clearest cases.

### Signal B — confidence threshold (model-emitted)
`faq_agent.py` enforces a hard floor:

```python
if parsed["confidence"] < 0.4:
    parsed["escalate"] = True
    parsed["reason"] = "Low confidence response"
```

The 0.4 threshold was chosen empirically — high enough to catch hedging answers, low enough not to escalate every borderline reply.

### Signal C — predicted risk (model-emitted)
Even if the keyword filter missed it and confidence is high, the model itself is asked to label the request:

```python
high_risk_categories = ["medical", "complaint", "pricing", "legal", "unsafe"]
if parsed["predicted_risk"] in high_risk_categories:
    parsed["escalate"] = True
```

For `medical`, `pricing`, and `legal`, the model's answer is also replaced with a category-specific canned reply so the model can't accidentally give bad advice while flagging itself.

### Signal D — JSON parse / model failure
If the model returns invalid JSON or is unreachable, `safe_fallback()` escalates with `reason="Invalid JSON response"` or `reason="Model unavailable"`. Failure modes never become silent successes.

### Logging
Every escalation is captured on the session at `session["escalation_reason"]` and surfaced in the summary endpoint (`/summary/{session_id}`), satisfying the "log the reason" requirement.

### Why both rule-based and model-based
Rules are cheap, instant, and explainable but brittle to novel phrasing. The model catches paraphrases and sentiment the keywords miss, but is non-deterministic. Stacking the two means new attack surface (e.g. "I'd like to argue about the cost" — no keyword match, but the model can flag it as `pricing`) is still caught.

---

## 4. Tone and Persona

The target user is a customer of a small aesthetics clinic — typically anxious, sometimes price-sensitive, occasionally upset. The tone choices reflect that:

- **Warm but neutral.** Greeting: *"Hello! Welcome to Bloom Aesthetics Clinic. How can we assist you today?"* No exclamations, no emoji, no over-familiar phrasing.
- **Concise.** SMB customers want answers, not paragraphs. The prompt asks for natural responses, but the JSON schema implicitly caps length via the structure of a single `answer` field.
- **De-escalating apologies on escalation.** All escalation messages start with `"I'm sorry…"` or `"I understand this is frustrating…"`. The model never argues, never explains the policy, and never asks the user to clarify a complaint before handing off.
- **Plural first-person ("we", "our clinic")** when answering as the business; **singular first-person ("I'm sorry", "I'm unable to")** when declining or escalating. The plural creates business presence; the singular owns the limitation.
- **No clinical advice voice.** The prompt explicitly forbids the model from sounding like a medical professional. The safest reply for any medical question is to escalate.
- **No robotic qualification.** The prompt tells the model to "avoid sounding robotic" and "stop once enough information is collected." This is the difference between a CRM form and a conversation — the assignment asks for the latter.
- **British English context.** Prices in GBP, "£200", "WhatsApp or website" booking — matches the SOP and the target SMB locale.

The persona is deliberately *not* given a name. A named persona ("Hi, I'm Bloom!") tends to invite chitchat and makes escalation feel like a betrayal; a neutral clinic voice keeps the boundary clean.

---

## Summary of design decisions

| Decision | Reasoning |
|---|---|
| Hybrid rule + LLM workflow | Safety-critical decisions stay deterministic; the LLM only generates language. |
| SOP injected verbatim into every prompt | Smallest, simplest grounding for a SOP of this size. Retrieval is the natural next step. |
| Structured JSON output | Lets Python enforce safety checks without parsing free text. |
| Confidence threshold of 0.4 | Catches hedged replies without flooding the human queue. |
| Three independent escalation signals | Defence in depth — one missed signal doesn't bypass safety. |
| Category-specific escalation replies | Medical / pricing / legal each get a tailored message instead of one generic hand-off. |
| Word-boundary keyword matching | Avoids false positives like `pain` matching `painting`. |
| In-memory session store with TTL | Sufficient for the assignment; documented as a known limitation for production. |
| Neutral, unnamed persona | Sets boundaries cleanly; makes escalation feel like a feature, not a failure. |
