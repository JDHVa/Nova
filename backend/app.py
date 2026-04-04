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

app = FastAPI(title="NOVA Asistente Medico API", version="1.0.0")

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


class HistorialMsgs(BaseModel):
    role: str  # "user" | "model"
    content: str


class Chats(BaseModel):
    message: str
    historial: List[HistorialMsgs] = []
    lenguaje: str = "es"
    budget: Optional[str] = None


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "NOVA Medical Assistant"}


@app.get("/api/ui-content")
async def ui_content(lang: str = "es"):
    service = get_chat_service()
    return service.get_ui_content(lang)


@app.post("/api/chat")
async def chat(request: Chats):
    try:
        service = get_chat_service()
        response = await service.send_message(
            message=request.message,
            historial=[m.dict() for m in request.historial],
            lenguaje=request.lenguaje,
            budget=request.budget,
        )
        return {"response": response, "Exito": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze-xray")
async def analyze_xray(file: UploadFile = File(...)):
    extensiones = (".jpg", ".jpeg", ".png")
    filename = (file.filename or "").lower()
    if not filename.endswith(extensiones):
        raise HTTPException(400, "Por favor sube una imagen en .png, .jpeg, .jpg")

    try:
        contenido = await file.read()
        analyzer = get_xray_analyzer()
        resultado = analyzer.analyze(contenido)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


path_fronthend = Path(__file__).parent.parent / "frontend"

if path_fronthend.exists():
    app.mount("/static", StaticFiles(directory=str(path_fronthend)), name="static")


@app.get("/")
async def root():
    index = path_fronthend / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"Mensaje": "La API si esta funcionando, ve a index.html alchillidog."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
