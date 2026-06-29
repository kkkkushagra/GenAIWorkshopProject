from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import HTMLResponse

from assistant import CollegeKnowledgeAssistant


app = FastAPI(title="College Knowledge Assistant", version="1.0.0")
assistant = CollegeKnowledgeAssistant("data")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    source: str


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="index.html", context={})


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
