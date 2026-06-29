from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from assistant import CollegeKnowledgeAssistant


app = FastAPI(title="College Knowledge Assistant", version="1.0.0")
assistant = CollegeKnowledgeAssistant("data")


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    source: str


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "College Knowledge Assistant API is running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        response_text = assistant.answer_query(request.question.strip())
        source = "Unknown"
        for line in response_text.splitlines():
            if line.startswith("Source:"):
                source = line.replace("Source:", "").strip()
                break

        return ChatResponse(answer=response_text, source=source)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
