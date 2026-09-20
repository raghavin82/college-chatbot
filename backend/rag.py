import os

from dotenv import load_dotenv
from google import genai

from backend.semantic_search import search


load_dotenv()


def generate_answer(question):

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

1. Use only the provided syllabus context.
2. Do not use outside knowledge.
3. Do not invent or assume syllabus information.
4. If the answer cannot be found in the context, say exactly:
"I couldn't find this information in the available syllabus."
5. Do not mention information that is not supported by the context.
6. Keep answers clear, concise, and easy for students to understand.
7. Preserve the subject code, subject name, module number,
   and topic names from the provided context.
8. For questions asking for topics, present the topics as a
   clear bullet-point list.
9. For questions asking where a topic is covered, identify
   the subject and module where it appears.
10. If multiple subjects contain the topic, mention each
    relevant subject separately.

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