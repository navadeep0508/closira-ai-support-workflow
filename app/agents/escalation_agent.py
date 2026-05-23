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


def detect_escalation(
    message: str
):

    text = (
        message
        .lower()
        .strip()
    )

    for category, keywords in (
        ESCALATION_KEYWORDS.items()
    ):

        for keyword in keywords:

            if keyword in text:

                return {

                    "escalate": True,

                    "reason":
                        f"{category} detected"
                }

    return {

        "escalate": False,

        "reason": ""
    }