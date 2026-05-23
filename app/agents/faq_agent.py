import os
import re
import json
import time

from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from app.utils.prompts import SYSTEM_PROMPT


# =========================================
# LOAD ENV
# =========================================

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


# =========================================
# NVIDIA CLIENT
# =========================================

client = OpenAI(

    api_key=os.getenv(
        "NVIDIA_API_KEY"
    ),

    base_url=
        "https://integrate.api.nvidia.com/v1"
)


# =========================================
# MODEL
# =========================================

MODEL_NAME = (
    "meta/llama-3.1-70b-instruct"
)


# =========================================
# LOAD SOP DATA
# =========================================

with open(
    "app/sop_data.json",
    "r",
    encoding="utf-8"
) as f:

    SOP_DATA = json.load(f)


# =========================================
# GREETINGS
# =========================================

GREETINGS = [

    "hi",

    "hello",

    "hey",

    "good morning",

    "good afternoon",

    "good evening"
]


# =========================================
# SAFE FALLBACK
# =========================================

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

        "reason": reason
    }


# =========================================
# CLEAN RESPONSE
# =========================================

def clean_json_response(
    text
):

    if not text:

        return ""

    text = text.strip()

    # Remove markdown wrappers

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

    # Remove line breaks

    text = (
        text
        .replace("\n", " ")
        .replace("\r", " ")
        .strip()
    )

    return text


# =========================================
# MODEL CALL
# =========================================

def call_model(
    prompt
):

    for attempt in range(3):

        try:

            print(
                "\nUSING NVIDIA MODEL\n"
            )

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

                    max_tokens=400
                )
            )

            return completion

        except Exception as e:

            print(
                f"\nMODEL RETRY {attempt + 1}:\n",
                e
            )

            error_text = (
                str(e)
                .lower()
            )

            # Stop useless retries

            if (

                "quota" in error_text

                or "429" in error_text

                or "limit" in error_text
            ):

                print(
                    "\nQUOTA EXCEEDED\n"
                )

                break

            time.sleep(2)

    return None


# =========================================
# FAQ AGENT
# =========================================

def faq_agent(
    user_message: str
):

    text = (
        user_message
        .lower()
        .strip()
    )

    # =====================================
    # GREETING HANDLER
    # =====================================

    if text in GREETINGS:

        return {

            "answer": (
                "Hello! Welcome to "
                "Bloom Aesthetics Clinic. "
                "How can we assist you today?"
            ),

            "confidence": 1.0,

            "escalate": False,

            "reason": "Greeting"
        }

    # =====================================
    # HARD SAFETY FILTER
    # =====================================

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
                "I’m sorry, but we "
                "do not provide that "
                "service. I am escalating "
                "this conversation to a "
                "human support agent."
            ),

            "confidence": 0.1,

            "escalate": True,

            "reason":
                "Out of scope question"
        }

    # =====================================
    # PROMPT
    # =====================================

    prompt = f"""
{SYSTEM_PROMPT}

SOP DATA:
{json.dumps(SOP_DATA, indent=2)}

Customer Message:
{user_message}

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
    "reason": "string"
}}
"""

    try:

        # =====================================
        # MODEL CALL
        # =====================================

        completion = call_model(
            prompt
        )

        if not completion:

            return safe_fallback(
                "Model unavailable"
            )

        # =====================================
        # EXTRACT CONTENT
        # =====================================

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

        print(
            "\nRAW MODEL RESPONSE:\n"
        )

        print(content)

        # =====================================
        # CLEAN RESPONSE
        # =====================================

        content = clean_json_response(
            content
        )

        # =====================================
        # PARSE JSON
        # =====================================

        parsed = json.loads(
            content
        )

        # =====================================
        # REQUIRED FIELDS
        # =====================================

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

        # =====================================
        # TYPE SAFETY
        # =====================================

        parsed["answer"] = str(
            parsed["answer"]
        )

        parsed["reason"] = str(
            parsed["reason"]
        )

        parsed["escalate"] = bool(
            parsed["escalate"]
        )

        try:

            parsed["confidence"] = (
                float(
                    parsed["confidence"]
                )
            )

        except:

            parsed["confidence"] = 0.0

        # =====================================
        # LOW CONFIDENCE
        # =====================================

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

        # =====================================
        # EMPTY ANSWER PROTECTION
        # =====================================

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

    # =====================================
    # JSON ERROR
    # =====================================

    except json.JSONDecodeError as e:

        print(
            "\nJSON ERROR:\n",
            e
        )

        return safe_fallback(
            "Invalid JSON response"
        )

    # =====================================
    # GENERAL ERROR
    # =====================================

    except Exception as e:

        print(
            "\nFAQ AGENT ERROR:\n",
            e
        )

        return safe_fallback(
            str(e)
        )


# =========================================
# TEST
# =========================================

if __name__ == "__main__":

    result = faq_agent(
        "What are your Botox prices?"
    )

    print(
        "\nFINAL OUTPUT:\n"
    )

    print(
        json.dumps(
            result,
            indent=2
        )
    )