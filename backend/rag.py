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
        return "I couldn't find this information in the available syllabus."

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

Answer the user's question using ONLY the syllabus
context provided below.

Rules:
1. Use only the provided syllabus context.
2. Do not use general knowledge.
3. Do not invent syllabus information.
4. If the answer cannot be found in the context, say:
"I couldn't find this information in the available syllabus."
5. Keep the answer clear and concise.

SYLLABUS CONTEXT:
{context}

USER QUESTION:
{question}
"""
    )

    return response.text


if __name__ == "__main__":

    question = input("Ask a syllabus question: ")

    answer = generate_answer(question)

    print("\nAnswer:\n")
    print(answer)