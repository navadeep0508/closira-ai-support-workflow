from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.models.schemas import ChatRequest

from app.agents.faq_agent import (
    faq_agent
)

from app.agents.qualification_agent import (
    get_next_question,
    get_current_key,
    detect_customer_type
)

from app.agents.escalation_agent import (
    detect_escalation
)

from app.agents.summary_agent import (
    generate_summary
)

from app.utils.memory import sessions

# ==========================================
# APP
# ==========================================

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)

templates = Jinja2Templates(
    directory="app/templates"
)

# ==========================================
# CONSTANTS
# ==========================================

QUESTION_WORDS = [

    "what",
    "how",
    "why",
    "when",
    "where",
    "can",
    "do",
    "does",
    "is",
    "are"
]

GREETINGS = [

    "hi",
    "hello",
    "hey",
    "good morning",
    "good evening",
    "good afternoon"
]

# ==========================================
# HELPERS
# ==========================================


def create_session():

    return {

        "messages": [],

        "lead_data": {},

        "questions_asked": 0,

        "qualification_started": False,

        "qualification_complete": False,

        "awaiting_qualification_answer": False,

        "escalation_reason": ""
    }


def build_response(
    answer="",
    confidence=1.0,
    escalate=False,
    reason="",
    qualification_question=None,
    session=None
):

    if session is None:

        session = create_session()

    return {

        "answer": answer,

        "confidence": confidence,

        "escalate": escalate,

        "reason": reason,

        "qualification_question":
            qualification_question,

        "lead_data":
            session.get(
                "lead_data",
                {}
            ),

        "qualification_complete":
            session.get(
                "qualification_complete",
                False
            )
    }


def looks_like_question(
    text: str
):

    text = text.lower().strip()

    return (

        "?" in text

        or any(

            text.startswith(word)

            for word in QUESTION_WORDS
        )
    )


def is_greeting(
    text: str
):

    text = text.lower().strip()

    return text in GREETINGS


def store_message(
    session,
    role,
    content
):

    session["messages"].append({

        "role": role,

        "content": content
    })

# ==========================================
# HOME
# ==========================================


@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

# ==========================================
# CHAT
# ==========================================


@app.post("/chat")
def chat(request: ChatRequest):

    try:

        # ==========================================
        # INPUTS
        # ==========================================

        session_id = (
            request.session_id
            .strip()
        )

        user_message = (
            request.message
            .strip()
        )

        # ==========================================
        # SESSION
        # ==========================================

        if session_id not in sessions:

            sessions[session_id] = (
                create_session()
            )

        session = sessions[session_id]

        # ==========================================
        # STORE USER MESSAGE
        # ==========================================

        store_message(
            session,
            "user",
            user_message
        )

        # ==========================================
        # ESCALATION DETECTION
        # ==========================================

        escalation = detect_escalation(
            user_message
        )

        if escalation["escalate"]:

            session[
                "escalation_reason"
            ] = escalation["reason"]

            answer = (

                "I’m sorry, but I’m not "
                "able to assist with that. "
                "I am escalating this "
                "conversation to a human "
                "support agent."
            )

            store_message(
                session,
                "assistant",
                answer
            )

            return build_response(

                answer=answer,

                confidence=1.0,

                escalate=True,

                reason=escalation["reason"],

                qualification_question=None,

                session=session
            )

        # ==========================================
        # QUALIFICATION ANSWERS
        # ==========================================

        if (

            session.get(
                "awaiting_qualification_answer",
                False
            )

           
        ):

            key = get_current_key(
                session
            )

            if key:

                session["lead_data"][
                   "customer_type"
                ] = detect_customer_type(
                  user_message
                )
            elif key:

                session["lead_data"][
                key
                ] = user_message

            session[
                "awaiting_qualification_answer"
            ] = False

            # ==========================================
            # NEXT QUESTION
            # ==========================================

            question = get_next_question(
                session
            )

            if question:

                session[
                    "questions_asked"
                ] += 1

                session[
                    "awaiting_qualification_answer"
                ] = True

                answer = "Thank you."

                store_message(
                    session,
                    "assistant",
                    answer
                )

                return build_response(

                    answer=answer,

                    confidence=1.0,

                    escalate=False,

                    reason="",

                    qualification_question=
                        question,

                    session=session
                )

            else:

                session[
                    "qualification_complete"
                ] = True

                session[
                   "awaiting_qualification_answer"
                 ] = False

                answer = (
                    "Thank you for providing "
                    "the information."
                )

                store_message(
                    session,
                    "assistant",
                    answer
                )

                return build_response(

                    answer=answer,

                    confidence=1.0,

                    escalate=False,

                    reason="",

                    qualification_question=None,

                    session=session
                )

        # ==========================================
        # FAQ AGENT
        # ==========================================

        response = faq_agent(
            user_message
        )

        # ==========================================
        # STORE ASSISTANT MESSAGE
        # ==========================================

        store_message(
            session,
            "assistant",
            response.get(
                "answer",
                ""
            )
        )

        # ==========================================
        # START QUALIFICATION FLOW
        # ==========================================

        if (

            not session[
                "qualification_started"
            ]

            and not response.get(
                "escalate",
                False
            )

            and not is_greeting(
                user_message
            )
        ):

            question = (
                get_next_question(
                    session
                )
            )

            if question:

                response[
                    "qualification_question"
                ] = question

                session[
                    "qualification_started"
                ] = True

                session[
                    "awaiting_qualification_answer"
                ] = True

                session[
                    "questions_asked"
                ] += 1

        # ==========================================
        # DEBUG
        # ==========================================

        print("\nSESSION STATE:\n")

        print(session)

        # ==========================================
        # FINAL RESPONSE
        # ==========================================

        return build_response(

            answer=response.get(
                "answer",
                ""
            ),

            confidence=response.get(
                "confidence",
                0.0
            ),

            escalate=response.get(
                "escalate",
                False
            ),

            reason=response.get(
                "reason",
                ""
            ),

            qualification_question=response.get(
                "qualification_question",
                None
            ),

            session=session
        )

    # ==========================================
    # ERROR HANDLING
    # ==========================================

    except Exception as e:

        print(
            "\nMAIN ERROR:\n",
            str(e)
        )

        return build_response(

            answer=(
                "Internal server error"
            ),

            confidence=0.0,

            escalate=True,

            reason=str(e),

            qualification_question=None,

            session=create_session()
        )

# ==========================================
# SUMMARY
# ==========================================


@app.get("/summary/{session_id}")
def get_summary(
    session_id: str
):

    try:

        if (
            session_id
            not in sessions
        ):

            return {

                "error":
                    "Session not found"
            }

        session = sessions[
            session_id
        ]

        summary = generate_summary(

            session,

            session.get(
                "escalation_reason",
                ""
            )
        )

        return summary

    except Exception as e:

        print(
            "\nSUMMARY ERROR:\n",
            str(e)
        )

        return {

            "error": str(e)
        }
@app.post("/reset/{session_id}")
def reset_session(
    session_id: str
):

    if session_id in sessions:

        del sessions[
            session_id
        ]

    return {
        "message":
            "Session reset successful"
    }