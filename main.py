# Project: Medicine Search RAG
# Structure:
# - vectorizer.py: Load CSV -> Embed -> Save to SQLite
# - search_engine.py: Query from SQLite -> Search vector
# - api.py: FastAPI chat API

from fastapi import FastAPI, Request, Form
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from search_engine import MedicineSearchEngine

app = FastAPI()
# add cors
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
search_engine = MedicineSearchEngine()
templates = Jinja2Templates(directory="templates")

class QueryRequest(BaseModel):
    question: str

@app.post("/search")
async def search_medicine(req: QueryRequest):
    results = search_engine.search(req.question)
    return {"matches": [{"text": text, "score": float(score)} for text, score in results]}

@app.get("/", response_class=HTMLResponse)
async def chat_ui(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/medications", response_class=JSONResponse)
async def chat_submit(request: Request, query: str):
    data = search_engine.search_with_llm(query)
    return data

# Run server with:
# uvicorn api:app --reload
