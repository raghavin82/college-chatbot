const chatBox = document.getElementById("chat-box");
const questionInput = document.getElementById("question-input");
const sendButton = document.getElementById("send-button");

let conversationHistory = [];


function addMessage(message, type) {

    const messageDiv = document.createElement("div");

    messageDiv.classList.add("message");

    if (type === "user") {
        messageDiv.classList.add("user-message");
    } else {
        messageDiv.classList.add("bot-message");
    }

    const paragraph = document.createElement("p");

    paragraph.innerHTML = message
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/(^|\n)\s*\*\s+/g, "$1• ")
        .replace(/\n/g, "<br>");

    messageDiv.appendChild(paragraph);

    chatBox.appendChild(messageDiv);

    chatBox.scrollTop = chatBox.scrollHeight;
}


async function sendMessage() {

    const question = questionInput.value.trim();

    if (!question) {
        return;
    }

    // Display user's question
    addMessage(question, "user");

    // Clear input
    questionInput.value = "";

    // Disable controls while processing
    sendButton.disabled = true;
    questionInput.disabled = true;

    // Show thinking message
    const thinkingMessage = document.createElement("div");

    thinkingMessage.classList.add("message", "bot-message");
    thinkingMessage.id = "thinking-message";

    thinkingMessage.innerHTML = "<p>🤖 Thinking...</p>";

    chatBox.appendChild(thinkingMessage);

    chatBox.scrollTop = chatBox.scrollHeight;


    try {

        const response = await fetch("http://127.0.0.1:8000/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question: question,
                history: conversationHistory
            })

        });


        const data = await response.json();

        let answer = data.answer;


        // Add sources if available
        if (data.sources && data.sources.length > 0) {

            answer += "\n\nSources:";

            data.sources.forEach((source) => {

                answer += `\n• ${source.subject_code} — ${source.subject} — Module ${source.module} — ${source.topic}`;

            });
        }


        // Remove thinking message
        const thinkingMessage = document.getElementById("thinking-message");

        if (thinkingMessage) {
            thinkingMessage.remove();
        }


        // Display chatbot answer
        addMessage(answer, "bot");

        conversationHistory.push({
            role: "user",
            content: question
        });

        conversationHistory.push({
            role: "assistant",
            content: data.answer
        });


        // Re-enable controls
        sendButton.disabled = false;
        questionInput.disabled = false;
        questionInput.focus();


    } catch (error) {

        // Remove thinking message
        const thinkingMessage = document.getElementById("thinking-message");

        if (thinkingMessage) {
            thinkingMessage.remove();
        }


        // Display error
        addMessage(
            "Sorry, I couldn't connect to the chatbot server.",
            "bot"
        );


        // Re-enable controls
        sendButton.disabled = false;
        questionInput.disabled = false;
        questionInput.focus();


        console.error(error);
    }
}


// Send button
sendButton.addEventListener("click", sendMessage);


// Enter key
questionInput.addEventListener("keydown", function(event) {

    if (event.key === "Enter") {
        sendMessage();
    }

});