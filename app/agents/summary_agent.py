def generate_summary(
    session,
    escalation_reason=""
):

    messages = session.get(
        "messages",
        []
    )

    lead_data = session.get(
        "lead_data",
        {}
    )

    customer_intent = ""

    sop_gaps = []

    discussed_services = []

    detected_risks = []

    booking_detected = False

    # ==========================================
    # CUSTOMER INTENT DETECTION
    # ==========================================

    service_mapping = {

        "botox":
            "Botox services",

        "filler":
            "Dermal fillers",

        "consultation":
            "Consultations",

        "laser":
            "Laser hair removal",

        "hydrafacial":
            "Hydrafacial treatments",

        "chemical peel":
            "Chemical peel treatments",

        "appointment":
            "Appointment booking",

        "booking":
            "Appointment booking",

        "cancel":
            "Cancellation policy",

        "payment":
            "Payment methods",

        "parking":
            "Parking availability"
    }

    for message in messages:

        if message["role"] != "user":

            continue

        text = (
            message["content"]
            .lower()
        )

        for keyword, intent in (
            service_mapping.items()
        ):

            if keyword in text:

                discussed_services.append(
                    intent
                )

        if (

            "book" in text

            or "appointment" in text

            or "consultation" in text
        ):

            booking_detected = True

    discussed_services = list(
        set(discussed_services)
    )

    if discussed_services:

        customer_intent = (
            ", ".join(
                discussed_services
            )
        )

    else:

        customer_intent = (
            "General customer enquiry"
        )

    # ==========================================
    # RISK DETECTION
    # ==========================================

    risk_mapping = {

        "pregnancy":
            "medical",

        "safe":
            "medical",

        "side effects":
            "medical",

        "refund":
            "complaint",

        "complaint":
            "complaint",

        "lower price":
            "pricing",

        "discount":
            "pricing",

        "sue":
            "legal",

        "lawyer":
            "legal",

        "heart surgery":
            "unsafe",

        "brain surgery":
            "unsafe"
    }

    for message in messages:

        if message["role"] != "user":

            continue

        text = (
            message["content"]
            .lower()
        )

        for keyword, risk in (
            risk_mapping.items()
        ):

            if keyword in text:

                detected_risks.append(
                    risk
                )

    detected_risks = list(
        set(detected_risks)
    )

    # ==========================================
    # SOP GAP DETECTION
    # ==========================================

    unsupported_keywords = [

        "heart surgery",

        "brain surgery",

        "insurance",

        "hospital",

        "ambulance",

        "x ray",

        "mri",

        "pregnancy",

        "emergency surgery",

        "blood test"
    ]

    for message in messages:

        if message["role"] != "user":

            continue

        text = (
            message["content"]
            .lower()
        )

        for keyword in (
            unsupported_keywords
        ):

            if keyword in text:

                sop_gaps.append(

                    f"Missing SOP "
                    f"information about "
                    f"'{keyword}'"
                )

    sop_gaps = list(
        set(sop_gaps)
    )

    # ==========================================
    # NEXT ACTION
    # ==========================================

    if escalation_reason:

        next_action = (

            "Human support "
            "follow-up required"
        )

    elif booking_detected:

        next_action = (

            "Proceed with "
            "consultation booking"
        )

    elif (
        not session.get(
            "qualification_complete",
            False
        )
    ):

        next_action = (

            "Continue customer "
            "engagement"
        )

    else:

        next_action = (

            "Continue automated "
            "support"
        )

    # ==========================================
    # CONVERSATION STATS
    # ==========================================

    total_messages = len(
        messages
    )

    user_messages = len([

        m for m in messages

        if m["role"] == "user"
    ])

    assistant_messages = len([

        m for m in messages

        if m["role"] == "assistant"
    ])

    # ==========================================
    # LAST USER MESSAGE
    # ==========================================

    last_user_message = ""

    for message in reversed(
        messages
    ):

        if message["role"] == "user":

            last_user_message = (
                message["content"]
            )

            break

    # ==========================================
    # FINAL SUMMARY
    # ==========================================

    return {

        "customer_intent":
            customer_intent,

        "services_discussed":
            discussed_services,

        "lead_details":
            lead_data,

        "qualification_complete":
            session.get(
                "qualification_complete",
                False
            ),

        "escalation_reason":
            escalation_reason,

        "detected_risks":
            detected_risks,

        "sop_gaps_identified":
            sop_gaps,

        "recommended_next_action":
            next_action,

        "booking_detected":
            booking_detected,

        "last_user_message":
            last_user_message,

        "conversation_statistics": {

            "total_messages":
                total_messages,

            "user_messages":
                user_messages,

            "assistant_messages":
                assistant_messages
        }
    }