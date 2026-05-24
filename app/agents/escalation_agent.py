import re


ESCALATION_KEYWORDS = {

    "complaint": [

        "bad service",
        "terrible",
        "not happy",
        "complaint",
        "refund",
        "refund request",
        "poor service",
        "very disappointed",
        "worst clinic",
        "unacceptable",
        "manager",
        "supervisor"
    ],

    "medical": [

        "side effects",
        "is botox safe",
        "medical advice",
        "pain",
        "swelling",
        "pregnant",
        "pregnancy",
        "allergic reaction",
        "infection",
        "bleeding",
        "bruising",
        "doctor",
        "medical emergency",
        "safe during pregnancy",
        "health issue"
    ],

    "pricing": [

        "discount",
        "cheaper",
        "negotiate",
        "lower price",
        "best price",
        "special offer",
        "price match",
        "too expensive",
        "reduce the price",
        "can you lower"
    ],

    "angry": [

        "angry",
        "frustrated",
        "useless",
        "worst",
        "hate",
        "awful",
        "ridiculous",
        "waste of money",
        "very upset",
        "annoyed"
    ],

    "legal": [

        "lawsuit",
        "sue",
        "legal action",
        "lawyer",
        "court",
        "report you",
        "consumer rights",
        "legal notice"
    ],

    "out_of_scope": [

        "heart surgery",
        "brain surgery",
        "insurance claim",
        "hospital admission",
        "x ray",
        "mri scan",
        "ambulance",
        "emergency surgery"
    ]
}


ESCALATION_MESSAGES = {

    "medical": (
        "I’m unable to provide medical advice regarding that "
        "request. I am escalating this conversation to a human "
        "support specialist."
    ),

    "pricing": (
        "I’m unable to negotiate pricing directly. I am "
        "escalating this conversation to a human support "
        "representative."
    ),

    "legal": (
        "I’m sorry, but I’m unable to assist with legal "
        "concerns. I am escalating this conversation to a "
        "human support representative."
    ),

    "complaint": (
        "I’m sorry you’ve had this experience. I am "
        "escalating your case to a human support "
        "representative who can help."
    ),

    "angry": (
        "I understand this is frustrating. I am escalating "
        "this conversation to a human support "
        "representative."
    ),

    "out_of_scope": (
        "I’m sorry, but I cannot assist with that request. "
        "I am escalating this conversation to a human "
        "support agent."
    ),
}


DEFAULT_ESCALATION_MESSAGE = (
    "I’m sorry, but I’m not able to assist with that. "
    "I am escalating this conversation to a human support "
    "agent."
)


_COMPILED_PATTERNS = {
    category: [
        re.compile(
            rf"\b{re.escape(keyword)}\b"
        )
        for keyword in keywords
    ]
    for category, keywords
    in ESCALATION_KEYWORDS.items()
}


def detect_escalation(
    message: str
):

    text = (
        message
        .lower()
        .strip()
    )

    for category, patterns in (
        _COMPILED_PATTERNS.items()
    ):

        for pattern in patterns:

            if pattern.search(text):

                return {

                    "escalate": True,

                    "category": category,

                    "reason":
                        f"{category} detected"
                }

    return {

        "escalate": False,

        "category": "",

        "reason": ""
    }


def escalation_message(
    category: str
) -> str:

    return ESCALATION_MESSAGES.get(
        category,
        DEFAULT_ESCALATION_MESSAGE,
    )
