"""Workshop finder (STUB): Google Places search + curated fallback."""

from __future__ import annotations

import json

import httpx

from . import config
from .models import Workshop


def _curated() -> list[Workshop]:
    path = config.DATA_DIR / "seed" / "workshops.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [Workshop(**w) for w in data]


def find(need: str, location: str = "") -> list[Workshop]:
    if config.GOOGLE_PLACES_API_KEY:
        try:
            return _google_places(need, location)
        except Exception:  # noqa: BLE001
            pass
    return _curated()


def _google_places(need: str, location: str) -> list[Workshop]:
    query = f"{need} car workshop" + (f" near {location}" if location else "")
    resp = httpx.post(
        "https://places.googleapis.com/v1/places:searchText",
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": config.GOOGLE_PLACES_API_KEY,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating",
        },
        json={"textQuery": query},
        timeout=30,
    )
    resp.raise_for_status()
    out: list[Workshop] = []
    for p in resp.json().get("places", []):
        out.append(
            Workshop(
                name=p.get("displayName", {}).get("text", ""),
                specialty=need,
                location=p.get("formattedAddress", ""),
                rating=str(p.get("rating", "")),
                source="google",
            )
        )
    return out
