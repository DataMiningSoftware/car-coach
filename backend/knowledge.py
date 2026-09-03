"""RAG knowledge assistant: specs, owner remarks, and model history."""

from __future__ import annotations

import json

from . import config, llm
from .models import CarRef, KnowledgeAnswer
from .retriever import BM25

_SYSTEM = (
    "You are a friendly car expert helping a non-expert. Answer using ONLY the "
    "provided knowledge. If it is insufficient, say what is unknown and give "
    "general guidance with a clear caveat. Be clear and concise."
)


def load_cars() -> list[dict]:
    path = config.DATA_DIR / "seed" / "cars.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _build_chunks(cars: list[dict]) -> tuple[list[str], list[dict]]:
    chunks: list[str] = []
    meta: list[dict] = []
    for car in cars:
        cid = f"{car['make']} {car['model']} ({car.get('year', '')})"
        chunks.append(f"Specifications of {cid}: {json.dumps(car.get('specs', {}), ensure_ascii=False)}")
        meta.append({"car": cid, "section": "specs"})
        for r in car.get("owner_remarks", []):
            chunks.append(f"Owner remark about {cid}: {r}")
            meta.append({"car": cid, "section": "owner_remarks"})
        if car.get("history"):
            chunks.append(f"History of {cid}: {car['history']}")
            meta.append({"car": cid, "section": "history"})
    return chunks, meta


def _matching_cars(car: CarRef | None, cars: list[dict]) -> list[dict]:
    if not car or not car.make:
        return []
    make = car.make.lower()
    model = car.model.lower()
    return [
        c for c in cars
        if make in c["make"].lower() and (not model or model in c["model"].lower())
    ]


def answer(question: str, car: CarRef | None = None) -> KnowledgeAnswer:
    cars = load_cars()
    chunks, meta = _build_chunks(cars)
    bm25 = BM25()
    bm25.fit(chunks)
    hits = bm25.search(question, top_k=4)

    # Always ground on the specified car's full profile first.
    matched = _matching_cars(car, cars)
    priority_chunks, priority_meta = _build_chunks(matched)

    context_parts = priority_chunks + [text for text, _ in hits]
    sources = [s["car"] for s in priority_meta] + [meta[chunks.index(t)]["car"] for t, _ in hits]
    context = "\n\n".join(dict.fromkeys(context_parts))  # dedupe, keep order
    sources = list(dict.fromkeys(sources))

    car_desc = f"{car.make} {car.model} {car.year}".strip() if car else ""
    prompt = (
        f"Car: {car_desc or '(not specified)'}\n"
        f"Question: {question}\n\n"
        f"Relevant knowledge:\n{context or '(none found)'}"
    )

    if not context:
        return KnowledgeAnswer(
            answer="I don't have any data on that car yet. Try another model, "
                   "or contribute a review so future users can benefit.",
            sources=[],
        )

    try:
        text = llm.complete(_SYSTEM, prompt)
        return KnowledgeAnswer(answer=text, sources=sources)
    except Exception as e:  # noqa: BLE001
        return KnowledgeAnswer(
            answer=f"(LLM unavailable: {e})\n\n{context}",
            sources=sources,
        )
