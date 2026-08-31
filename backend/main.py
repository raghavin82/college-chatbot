from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class ChatRequest(BaseModel):
    question : str


@app.get("/")
def home():
    return {"message" : "College Chatbot API is running!"}

@app.get("/health")
def health():
    return {"status" : "healthy"}

@app.post("/chat")
def chat(request: ChatRequest):
    if "hello" in request.question.lower():
        answer = "Hello! How can I help you?"
    else:
        answer = "I recieved your question, but I don't know the answer yet."
    return {
        "question" : request.question,
        "answer" : answer
    }