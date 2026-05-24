const sessionId =
    "session-" +
    Math.random()
    .toString(36)
    .substring(2, 10);

window.onload = function () {

    document.getElementById(
        "sessionText"
    ).innerText =
        "Session: " + sessionId;
};

const chatBox =
    document.getElementById(
        "chatBox"
    );

const input =
    document.getElementById(
        "messageInput"
    );

const sendBtn =
    document.getElementById(
        "sendBtn"
    );

const loading =
    document.getElementById(
        "loading"
    );

const summaryBtn =
    document.getElementById(
        "summaryBtn"
    );

const summaryBox =
    document.getElementById(
        "summaryBox"
    );

const closeSummary =
    document.getElementById(
        "closeSummary"
    );

const summaryContent =
    document.getElementById(
        "summaryContent"
    );


function addMessage(
    text,
    sender
) {

    if (!text) {

        return;
    }

    const div =
        document.createElement(
            "div"
        );

    div.classList.add(
        "message"
    );

    div.classList.add(
        sender
    );

    div.innerText = text;

    chatBox.appendChild(div);

    chatBox.scrollTop =
        chatBox.scrollHeight;
}


async function sendMessage() {

    const message =
        input.value.trim();

    if (!message) {

        return;
    }

    addMessage(
        message,
        "user"
    );

    input.value = "";

    loading.style.display =
        "block";

    try {

        const response =
            await fetch(
                "/chat",

                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        session_id:
                            sessionId,

                        message:
                            message
                    })
                }
            );

        const data =
            await response.json();

        loading.style.display =
            "none";

        addMessage(
            data.answer,
            "bot"
        );

        if (
            data.next_question
        ) {

            addMessage(

                data.next_question,

                "bot"
            );
        }

    } catch (error) {

        loading.style.display =
            "none";

        console.error(error);

        addMessage(

            "Server error occurred.",

            "bot"
        );
    }
}


sendBtn.addEventListener(
    "click",
    sendMessage
);


input.addEventListener(
    "keypress",

    function (e) {

        if (e.key === "Enter") {

            sendMessage();
        }
    }
);


summaryBtn.addEventListener(

    "click",

    async () => {

        try {

            const response =
                await fetch(

                    `/summary/${sessionId}`
                );

            const data =
                await response.json();

            summaryBox.style.display =
                "block";
            summaryContent.innerHTML = `

    <h2>
        Conversation Summary
    </h2>

    <br>

    <div class="summary-item">

        <span class="summary-label">
            Customer Intent:
        </span>

        <br>

        ${data.customer_intent}

    </div>

    <div class="summary-item">

        <span class="summary-label">
            Services Discussed:
        </span>

        <pre>

${JSON.stringify(
    data.services_discussed,
    null,
    2
)}

        </pre>

    </div>

    <div class="summary-item">

        <span class="summary-label">
            Detected Risks:
        </span>

        <pre>

${JSON.stringify(
    data.detected_risks,
    null,
    2
)}

        </pre>

    </div>

    <div class="summary-item">

        <span class="summary-label">
            Escalation Reason:
        </span>

        <br>

        ${data.escalation_reason || "None"}

    </div>

    <div class="summary-item">

        <span class="summary-label">
            Booking Detected:
        </span>

        <br>

        ${data.booking_detected}

    </div>

    <div class="summary-item">

        <span class="summary-label">
            Last User Message:
        </span>

        <br>

        ${data.last_user_message}

    </div>

    <div class="summary-item">

        <span class="summary-label">
            Recommended Action:
        </span>

        <br>

        ${data.recommended_next_action}

    </div>

    <div class="summary-item">

        <span class="summary-label">
            Lead Details:
        </span>

        <pre>

${JSON.stringify(
    data.lead_details,
    null,
    2
)}

        </pre>

    </div>

    <div class="summary-item">

        <span class="summary-label">
            SOP Gaps:
        </span>

        <pre>

${JSON.stringify(
    data.sop_gaps_identified,
    null,
    2
)}

        </pre>

    </div>

    <div class="summary-item">

        <span class="summary-label">
            Conversation Statistics:
        </span>

        <pre>

${JSON.stringify(
    data.conversation_statistics,
    null,
    2
)}

        </pre>

    </div>
`;
           


        } catch (error) {

            console.error(error);

            alert(
                "Failed to load summary"
            );
        }
    }
);


closeSummary.addEventListener(

    "click",

    () => {

        summaryBox.style.display =
            "none";
    }
);