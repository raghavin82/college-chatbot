from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.rag import generate_answer


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


class ChatRequest(BaseModel):
    question : str
    history: list = Field(default_factory=list)


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
        result = generate_answer(question, request.history)

    except Exception as error:

        print("CHAT ERROR: ", repr(error))

        if "429" in str(error) or "RESOURCE_EXHAUSTED" in str(error):
            return {
                "question": question,
                "answer": "The AI service has temporarily reached its usage limit. Please try again later.",
                "sources": []
            }

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