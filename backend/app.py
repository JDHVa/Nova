from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="NOVA Medical Assistant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_chat_service = None
_xray_analyzer = None


def get_chat_service():
    global _chat_service
    if _chat_service is None:
        from chat_service import ChatService

        _chat_service = ChatService()
    return _chat_service


def get_xray_analyzer():
    global _xray_analyzer
    if _xray_analyzer is None:
        from xray_analyzer import XrayAnalyzer

        _xray_analyzer = XrayAnalyzer()
    return _xray_analyzer


class HistoryMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[HistoryMessage] = []
    language: str = "es"
    budget: Optional[str] = None


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "NOVA Medical Assistant"}


@app.get("/api/ui-content")
async def ui_content(lang: str = "es"):

    service = get_chat_service()
    return service.get_ui_content(lang)


@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        service = get_chat_service()
        response = await service.send_message(
            message=request.message,
            history=[m.dict() for m in request.history],
            language=request.language,
            budget=request.budget,
        )
        return {"response": response, "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze-xray")
async def analyze_xray(file: UploadFile = File(...)):
    valid_extensions = (".jpg", ".jpeg", ".png")
    filename = (file.filename or "").lower()
    if not filename.endswith(valid_extensions):
        raise HTTPException(
            400,
            "Por favor sube una imagen JPG o PNG / Please upload a JPG or PNG image",
        )
    try:
        contents = await file.read()
        analyzer = get_xray_analyzer()
        result = analyzer.analyze(contents)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


frontend_path = Path(__file__).parent.parent / "frontend"

if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")


@app.get("/")
async def root():
    index = frontend_path / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {
        "message": "NOVA API si jala vete a index.html para que veas como funciona crack."
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
