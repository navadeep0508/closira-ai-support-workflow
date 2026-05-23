# Summary Endpoint Test

## Endpoint

GET /summary/demo-session

---

## Example Conversation

Customer:
What are your Botox prices?

Customer:
Business

Customer:
Dental clinic

Customer:
12

Customer:
WhatsApp and Gmail

Customer:
Reduce customer response time

---

## Example API Response

```json
{
  "customer_intent":
    "Botox services",

  "services_discussed": [
    "Botox services"
  ],

  "lead_details": {

    "customer_type":
      "Business",

    "business_type":
      "Dental clinic",

    "team_size":
      "12",

    "current_tools":
      "WhatsApp and Gmail",

    "main_goal":
      "Reduce customer response time"
  },

  "qualification_complete": true,

  "escalation_reason": "",

  "sop_gaps_identified": [],

  "recommended_next_action":
    "Continue automated support",

  "conversation_statistics": {

    "total_messages": 12,

    "user_messages": 6,

    "assistant_messages": 6
  }
}
```

---

## Expected Behavior

- Summarizes customer intent
- Stores lead qualification data
- Detects SOP gaps
- Tracks escalation state
- Provides next recommended action