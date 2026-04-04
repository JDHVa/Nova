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

# En caso de que no entiendan las lineas como quiera las voy a comentar por si acaso y no entienden (Disclaimer: Si no entiendes por que todo el codigo esta en ingles, es por que son palabras reservadas asi que es necesario hacerlo en ingles / If some of the lines cant be understan by you im going to cokmment all of it (Dislaimer: If you dont understan why is the code in english is becuase some words are neccesarry to write it in english)) Something else i want to

app = FastAPI(title="API Del Proyecto NOVA", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

chats = None
xray = None


def getchats():
    global chats
    if chats is None:
        from chat_service import ChatService

        chats = ChatService()
    return chats


def getxray():
    global xray
    if xray is None:
        from xray_analyzer import XrayAnalyzer

        xray = XrayAnalyzer()
    return xray


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
    return {"status": "ok", "service": "Asistente Medico NOVA IA"}


@app.get("/api/ui-content")
async def ui_content(lang: str = "es"):

    service = getchats()
    return service.get_ui_content(lang)


@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        service = getchats()
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
        analyzer = getxray()
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
