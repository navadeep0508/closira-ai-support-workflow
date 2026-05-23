def detect_customer_type(
    text: str
):

    text = text.lower()

    business_keywords = [

        "business",

        "company",

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

        "chemical peel"
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


