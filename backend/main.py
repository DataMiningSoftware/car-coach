"""FastAPI application."""

from __future__ import annotations

import shutil

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from . import config, docs, knowledge, mods, visualize, workshops
from .models import (
    CarRef,
    DocumentExtraction,
    KnowledgeAnswer,
    KnowledgeRequest,
    ModAdvice,
    ModRequest,
    Workshop,
)

app = FastAPI(title="car-coach", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/cars")
def list_cars() -> list[dict]:
    return knowledge.load_cars()


@app.post("/api/knowledge")
def ask(req: KnowledgeRequest) -> KnowledgeAnswer:
    return knowledge.answer(req.question, req.car)


@app.post("/api/mods")
def mod_advice(req: ModRequest) -> ModAdvice:
    return mods.advise(req)


@app.post("/api/documents")
async def upload_document(file: UploadFile = File(...)) -> DocumentExtraction:
    path = config.UPLOADS_DIR / (file.filename or "upload.pdf")
    with path.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    return docs.extract(path)


@app.post("/api/visualize")
def visualize_car(req: dict) -> dict:
    return visualize.generate(req.get("description", ""), req.get("car", ""))


@app.post("/api/workshops")
def find_workshops(req: dict) -> list[Workshop]:
    return workshops.find(req.get("need", ""), req.get("location", ""))
