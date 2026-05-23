# Summary Endpoint Test

Endpoint:
GET /summary/demo-session

Example Response:

{
  "customer_intent":
    "Botox services, Appointment booking",

  "services_discussed": [
    "Botox services",
    "Appointment booking"
  ],

  "lead_details": {
    "customer_type": "Business",
    "business_type": "Dental clinic",
    "team_size": "12",
    "current_tools": "WhatsApp and Gmail",
    "main_goal": "Reduce customer response time"
  },

  "qualification_complete": true,

  "escalation_reason": "",

  "sop_gaps_identified": [],

  "recommended_next_action":
    "Continue automated support"
}