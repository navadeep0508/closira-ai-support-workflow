import os
import re
import json
import time

from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from app.utils.prompts import SYSTEM_PROMPT


env_path = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    .parent
    / ".env"
)

load_dotenv(
    dotenv_path=env_path
)

client = OpenAI(

    api_key=os.getenv(
        "NVIDIA_API_KEY"
    ),

    base_url=
        "https://integrate.api.nvidia.com/v1"
)

MODEL_NAME = (
    "meta/llama-3.1-8b-instruct"
)

with open(
    "app/sop_data.json",
    "r",
    encoding="utf-8"
) as f:

    SOP_DATA = json.load(f)

GREETINGS = [

    "hi",

    "hello",

    "hey",

    "good morning",

    "good afternoon",

    "good evening"
]


def safe_fallback(
    reason="Unknown error"
):

    return {

        "answer": (
            "I’m sorry, but I’m "
            "unable to process "
            "your request right now."
        ),

        "confidence": 0.0,

        "escalate": True,

        "reason": reason,

        "next_question": "",

        "qualification_complete": False,

        "detected_intent": "",

        "detected_customer_type": "",

        "predicted_risk": "none"
    }


def clean_json_response(
    text
):

    if not text:

        return ""

    text = text.strip()

    text = re.sub(
        r"```json",
        "",
        text
    )

    text = re.sub(
        r"```",
        "",
        text
    )

    text = (
        text
        .replace("\n", " ")
        .replace("\r", " ")
        .strip()
    )

    return text


def detect_customer_type(
    text: str
):

    text = text.lower()

    business_keywords = [

        "business",

        "company",

        "clinic",

        "startup",

        "agency",

        "customer support",

        "ai support",

        "automation"
    ]

    individual_keywords = [

        "botox",

        "filler",

        "consultation",

        "appointment",

        "laser",

        "hydrafacial",

        "chemical peel",

        "services"
    ]

    for keyword in (
        business_keywords
    ):

        if keyword in text:

            return "business"

    for keyword in (
        individual_keywords
    ):

        if keyword in text:

            return "individual"

    return ""


def build_dynamic_context(
    session
):

    lead_data = session.get(
        "lead_data",
        {}
    )

    customer_type = (
        lead_data.get(
            "customer_type",
            ""
        )
    )

    if customer_type == "business":

        return """

Business Lead Qualification Goals:
- understand business type
- understand support workflow
- understand team size
- understand customer support tools
- understand AI automation goals

Ask questions naturally.
Avoid sounding robotic.
Stop once enough information is collected.
"""

    return """

Customer Service Goals:
- help customer choose services
- help with consultation booking
- answer treatment questions naturally

Avoid unnecessary business qualification.
"""


def call_model(
    prompt
):

    for attempt in range(3):

        try:

            completion = (
                client.chat.completions.create(

                    model=MODEL_NAME,

                    messages=[

                        {
                            "role": "system",

                            "content": (
                                "You are a safe "
                                "customer support AI. "
                                "Always respond ONLY "
                                "with valid JSON."
                            )
                        },

                        {
                            "role": "user",

                            "content": prompt
                        }
                    ],

                    temperature=0.2,

                    max_tokens=700
                )
            )

            return completion

        except Exception as e:

            error_text = (
                str(e)
                .lower()
            )

            if (

                "quota" in error_text

                or "429" in error_text

                or "limit" in error_text
            ):

                break

            time.sleep(2)

    return None


def faq_agent(
    user_message: str,
    session=None
):

    text = (
        user_message
        .lower()
        .strip()
    )

    if session is None:

        session = {

            "messages": [],

            "lead_data": {},

            "qualification_started": False,

            "qualification_complete": False,

            "escalation_reason": ""
        }

    if (

    text in GREETINGS

    and len(
        session.get(
            "messages",
            []
        )
    ) <= 1
     ):

        return {

            "answer": (
                "Hello! Welcome to "
                "Bloom Aesthetics Clinic. "
                "How can we assist you today?"
            ),

            "confidence": 1.0,

            "escalate": False,

            "reason": "Greeting",

            "next_question": "",

            "qualification_complete": False,

            "detected_intent": "general",

            "detected_customer_type": "",

            "predicted_risk": "none"
        }

    dangerous_keywords = [

        "heart surgery",

        "brain surgery",

        "transplant",

        "cancer treatment",

        "insurance",

        "hospital admission"
    ]

    if any(

        keyword in text

        for keyword in (
            dangerous_keywords
        )
    ):

        return {

            "answer": (
                "I’m sorry, but I "
                "cannot assist with "
                "that request. "
                "I am escalating this "
                "conversation to a "
                "human support agent."
            ),

            "confidence": 0.1,

            "escalate": True,

            "reason":
                "Out of scope question",

            "next_question": "",

            "qualification_complete": False,

            "detected_intent": "unsupported",

            "detected_customer_type": "",

            "predicted_risk": "unsafe"
        }

    dynamic_context = (
        build_dynamic_context(
            session
        )
    )

    detected_customer_type = ""

    if session.get(
        "lead_data",
        {}
    ).get(
        "customer_type"
    ):

        detected_customer_type = (
            session["lead_data"][
                "customer_type"
            ]
        )

    else:

        detected_customer_type = (
            detect_customer_type(
                user_message
            )
        )

    prompt = f"""
{SYSTEM_PROMPT}

SOP DATA:
{json.dumps(SOP_DATA, indent=2)}

Conversation Context:
{json.dumps(session, indent=2)}

Dynamic Qualification Context:
{dynamic_context}

Customer Message:
{user_message}

Based on the conversation:

- detect whether user is:
  individual customer
  or business lead

- decide whether qualification is needed

- generate ONE natural follow-up question if appropriate

- avoid repetitive or robotic questioning

- stop asking once enough information is collected

- service customers should receive service-related follow-ups

- business leads should receive business qualification follow-ups

Detect whether the customer message involves:

- medical advice
- complaints
- angry sentiment
- pricing negotiation
- legal threats
- unsafe requests

If the customer is:
- negotiating prices
- requesting discounts
- asking for lower pricing

Then:
- set escalate=true
- avoid direct negotiation
- politely escalate to human support

If detected:
- set escalate=true
- provide reason
- avoid unsafe medical responses

Set:
"predicted_risk"

Possible values:
- medical
- complaint
- pricing
- legal
- unsafe
- none

IMPORTANT RULES:

- Return ONLY valid JSON
- Never return markdown
- Never use backticks
- Never explain your answer
- Never invent information
- Only answer using SOP DATA
- If information is unavailable:
  escalate instead of guessing

Required JSON format:

{{
    "answer": "string",
    "confidence": 0.0,
    "escalate": false,
    "reason": "string",
    "next_question": "string",
    "qualification_complete": false,
    "detected_intent": "string",
    "detected_customer_type": "string",
    "predicted_risk": "string"
}}
"""

    try:

        completion = call_model(
            prompt
        )

        if not completion:

            return safe_fallback(
                "Model unavailable"
            )

        content = (
            completion
            .choices[0]
            .message
            .content
        )

        if not content:

            return safe_fallback(
                "Empty AI response"
            )

        content = clean_json_response(
            content
        )

        parsed = json.loads(
            content
        )

        parsed.setdefault(
            "answer",
            ""
        )

        parsed.setdefault(
            "confidence",
            0.0
        )

        parsed.setdefault(
            "escalate",
            False
        )

        parsed.setdefault(
            "reason",
            ""
        )

        parsed.setdefault(
            "next_question",
            ""
        )

        parsed.setdefault(
            "qualification_complete",
            False
        )

        parsed.setdefault(
            "detected_intent",
            ""
        )

        parsed.setdefault(
            "detected_customer_type",
            detected_customer_type
        )

        parsed.setdefault(
            "predicted_risk",
            "none"
        )

        parsed["answer"] = str(
            parsed["answer"]
        )

        parsed["reason"] = str(
            parsed["reason"]
        )

        parsed["next_question"] = str(
            parsed["next_question"]
        )

        parsed["detected_intent"] = str(
            parsed["detected_intent"]
        )

        parsed["detected_customer_type"] = str(
            parsed["detected_customer_type"]
        )

        parsed["predicted_risk"] = str(
            parsed["predicted_risk"]
        )

        parsed["escalate"] = bool(
            parsed["escalate"]
        )

        parsed[
            "qualification_complete"
        ] = bool(
            parsed[
                "qualification_complete"
            ]
        )

        try:

            parsed["confidence"] = (
                float(
                    parsed["confidence"]
                )
            )

        except:

            parsed["confidence"] = 0.0

        if (
            parsed["confidence"]
            < 0.4
        ):

            parsed["escalate"] = True

            if not parsed[
                "reason"
            ]:

                parsed["reason"] = (
                    "Low confidence response"
                )

        high_risk_categories = [

            "medical",

            "complaint",

            "pricing",

            "legal",

            "unsafe"
        ]

        if parsed[
            "predicted_risk"
        ] in high_risk_categories:

            parsed["escalate"] = True

        if parsed[
            "predicted_risk"
        ] == "pricing":

            parsed["answer"] = (

                "I’m unable to negotiate "
                "pricing directly. "
                "I am escalating this "
                "conversation to a human "
                "support representative."
            )

        if parsed[
            "predicted_risk"
        ] == "legal":

            parsed["answer"] = (

                "I’m sorry, but I’m "
                "unable to assist with "
                "legal concerns. "
                "I am escalating this "
                "conversation to a human "
                "support representative."
            )

        if parsed[
            "predicted_risk"
        ] == "medical":

            parsed["answer"] = (

                "I’m unable to provide "
                "medical advice regarding "
                "that request. "
                "I am escalating this "
                "conversation to a human "
                "support specialist."
            )

        if not parsed[
            "answer"
        ].strip():

            parsed["answer"] = (
                "I’m sorry, but I "
                "could not find a "
                "reliable answer."
            )

            parsed["escalate"] = True

            parsed["reason"] = (
                "Empty AI answer"
            )

        return parsed

    except json.JSONDecodeError:

        return safe_fallback(
            "Invalid JSON response"
        )

    except Exception as e:

        return safe_fallback(
            str(e)
        )


if __name__ == "__main__":

    session = {

        "messages": [],

        "lead_data": {},

        "qualification_started": False,

        "qualification_complete": False,

        "escalation_reason": ""
    }

    result = faq_agent(
        "What services do you provide?",
        session
    )

    print(
        json.dumps(
            result,
            indent=2
        )
    )