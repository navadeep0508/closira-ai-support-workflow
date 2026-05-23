from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.models.schemas import ChatRequest

from app.agents.faq_agent import (
    faq_agent
)

from app.agents.escalation_agent import (
    detect_escalation
)

from app.agents.summary_agent import (
    generate_summary
)

from app.utils.memory import sessions


app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)

templates = Jinja2Templates(
    directory="app/templates"
)

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


def create_session():

    return {

        "messages": [],

        "lead_data": {},

        "qualification_started": False,

        "qualification_complete": False,

        "escalation_reason": ""
    }


def build_response(
    answer="",
    confidence=1.0,
    escalate=False,
    reason="",
    next_question="",
    session=None
):

    if session is None:

        session = create_session()

    return {

        "answer": answer,

        "confidence": confidence,

        "escalate": escalate,

        "reason": reason,

        "next_question":
            next_question,

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


@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.post("/chat")
def chat(request: ChatRequest):

    try:

        session_id = (
            request.session_id
            .strip()
        )

        user_message = (
            request.message
            .strip()
        )

        if session_id not in sessions:

            sessions[session_id] = (
                create_session()
            )

        session = sessions[session_id]

        store_message(
            session,
            "user",
            user_message
        )

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

                next_question="",

                session=session
            )

        response = faq_agent(
            user_message,
            session
        )

        store_message(
            session,
            "assistant",
            response.get(
                "answer",
                ""
            )
        )

        if response.get(
            "detected_customer_type"
        ):

            session["lead_data"][
                "customer_type"
            ] = response.get(
                "detected_customer_type"
            )

        if response.get(
            "qualification_complete",
            False
        ):

            session[
                "qualification_complete"
            ] = True

        print("\nSESSION STATE:\n")

        print(session)

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

            next_question=response.get(
                "next_question",
                ""
            ),

            session=session
        )

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

            next_question="",

            session=create_session()
        )


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