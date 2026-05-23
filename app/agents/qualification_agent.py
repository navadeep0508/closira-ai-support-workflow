QUALIFICATION_FLOW = {

    "individual": [

        {
            "key": "service_interest",

            "question":
                "Which treatment are you interested in?"
        },

        {
            "key": "booking_interest",

            "question":
                "Would you like help booking a consultation?"
        }
    ],

    "business": [

        {
            "key": "business_type",

            "question":
                "What type of business do you run?"
        },

        {
            "key": "team_size",

            "question":
                "How many team members do you have?"
        },

        {
            "key": "current_tools",

            "question":
                "What tools do you currently use for customer support?"
        },

        {
            "key": "main_goal",

            "question":
                "What is your main goal with AI customer support?"
        }
    ]
}


def detect_customer_type(
    answer: str
):

    text = answer.lower()

    individual_keywords = [

        "individual",

        "alone",

        "personal",

        "myself",

        "customer"
    ]

    for keyword in (
        individual_keywords
    ):

        if keyword in text:

            return "individual"

    return "business"


def get_next_question(
    session
):

    customer_type = session[
        "lead_data"
    ].get(
        "customer_type"
    )

    if not customer_type:

        return (
            "Are you an individual "
            "customer or a business?"
        )

    flow = QUALIFICATION_FLOW[
        customer_type
    ]

    asked = session.get(
        "questions_asked",
        0
    )

    if asked < len(flow):

        return flow[
            asked
        ]["question"]

    return None


def get_current_key(
    session
):

    customer_type = session[
        "lead_data"
    ].get(
        "customer_type"
    )

    if not customer_type:

        return "customer_type"

    flow = QUALIFICATION_FLOW[
        customer_type
    ]

    asked = session.get(
        "questions_asked",
        0
    )

    if 0 < asked <= len(flow):

        return flow[
            asked - 1
        ]["key"]

    return None