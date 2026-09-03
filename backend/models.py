"""Pydantic request/response models."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class CarRef(BaseModel):
    make: str = ""
    model: str = ""
    year: str = ""
    trim: str = ""
    engine: str = ""


class KnowledgeRequest(BaseModel):
    car: CarRef = Field(default_factory=CarRef)
    question: str


class KnowledgeAnswer(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list)


class ModRequest(BaseModel):
    car: CarRef = Field(default_factory=CarRef)
    goal: str = ""
    budget_rm: Optional[float] = None
    usage: str = "street"  # street | track | offroad


class Mod(BaseModel):
    name: str
    category: str
    expected_gains: str
    cost_rm: str
    difficulty: str
    legality_my: str
    caveats: str = ""


class ModAdvice(BaseModel):
    summary: str = ""
    mods: list[Mod] = Field(default_factory=list)
    legal_disclaimer: str = ""


class Workshop(BaseModel):
    name: str
    specialty: str
    location: str
    rating: str = ""
    source: str = ""


class DocumentExtraction(BaseModel):
    text: str
    masked: bool = False
    fields: dict = Field(default_factory=dict)
