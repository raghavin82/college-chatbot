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

    answer = generate_answer(request.question)

    return {
        "question" : request.question,
        "answer" : answer
    }