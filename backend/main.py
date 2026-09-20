from fastapi import FastAPI
from pydantic import BaseModel

from backend.rag import generate_answer


app = FastAPI()


class ChatRequest(BaseModel):
    question : str


@app.get("/")
def home():
    return {
        "message" : "College Chatbot API is running!"
    }

@app.get("/health")
def health():
    return {
        "status" : "healthy"
    }

@app.post("/chat")
def chat(request: ChatRequest):

    question = request.question.strip()

    if not question:
        return{
            "question": "",
            "answer": "Please enter a question.",
            "sources": []
        }

    try:
        result = generate_answer(question)

    except Exception:
        return {
            "question": question,
            "answer": "Sorry, I couldn't process your question right now.",
            "sources": []
        }
    
    return {
        "question" : question,
        "answer" : result["answer"],
        "sources": result["sources"]
    }