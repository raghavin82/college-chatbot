import os

from dotenv import load_dotenv
from google import genai

from backend.semantic_search import search


load_dotenv()


def generate_answer(question, history = None):

    if history is None:
        history = []

    # Retrieve relevant syllabus information
    results = search(question)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    # No relevant information found
    if not documents:
        return {
            "answer": "I couldn't find this information in the available syllabus.",
            "sources": []
        }

    # Build syllabus context
    context_parts = []

    for i in range(len(documents)):

        metadata = metadatas[i]

        context_parts.append(
            f"Subject Code: {metadata['course_code']}\n"
            f"Subject: {metadata['course_name']}\n"
            f"Module: {metadata['module']}\n"
            f"Topic: {metadata['topic']}"
        )

    context = "\n\n".join(context_parts)

    history_text = ""

    if history:
        history_parts = []

        for message in history:
            history_parts.append(
                f"{message['role']}: {message['content']}"
            )

        history_text = "\n".join(history_parts)

    # Create Gemini client
    api_key = os.getenv("GEMINI_API_KEY")

    client = genai.Client(api_key=api_key)

    # Ask Gemini using only retrieved syllabus context
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=f"""
You are a college syllabus assistant for IPS Academy,
Institute of Engineering & Science.

Your job is to answer questions using ONLY the syllabus
context provided below.

STRICT RULES:


1. Use ONLY the syllabus context provided below.
2. Do NOT use outside knowledge, even if you know the answer.
3. Do NOT invent, assume, or infer syllabus information.
4. If the requested information is not supported by the context, say exactly:
"I couldn't find this information in the available syllabus."
5. Preserve the exact subject code, subject name, module number, and topic names from the context.
6. If the user asks for a list of topics, return only the relevant topics as clear bullet points.
7. If the user asks where a topic is covered, mention the subject code, subject name, and module for each matching result.
8. If multiple subjects contain the requested topic, group the results by subject.
9. If the user asks for an explanation or definition that is NOT present in the context, do not provide an outside explanation. Use the exact fallback sentence instead.
10. Do not claim that a topic is explained, defined, or discussed beyond what the provided context actually contains.
11. Avoid unnecessary introductory or concluding text. Answer the user's question directly.
12. Do not repeat the same topic unless it appears as a genuinely separate syllabus entry.
13. For topic-list questions, preserve the syllabus terminology exactly rather than rewriting topic names.
14. Keep answers concise and student-friendly.
15. Use conversation history only to understand references or follow-up questions. All factual answers must still be supported by the syllabus context.

CONVERSATION HISTORY:
{history_text}

SYLLABUS CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:
"""
    )

    return {
        "answer" : response.text,
        "sources" : [
            {
                "subject_code": metadatas[i]["course_code"],
                "subject": metadatas[i]["course_name"],
                "module": metadatas[i]["module"],
                "topic": metadatas[i]["topic"]
            }
            for i in range(len(metadatas))
        ]
    }


if __name__ == "__main__":

    question = input("Ask a syllabus question: ")

    answer = generate_answer(question)

    print("\nAnswer:\n")
    print(answer)