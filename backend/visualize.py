"""AI image visualization of car modifications (STUB).

Wired to Replicate (img2img/text-to-image) and Stability AI if configured.
This is intentionally minimal: it renders a visualization based on the user's
description without over-riding their creativity.
"""

from __future__ import annotations

import httpx

from . import config


def generate(description: str, car: str = "") -> dict:
    prompt = f"{car} {description}".strip()
    if config.IMAGE_PROVIDER == "stability" and config.STABILITY_API_KEY:
        return _stability(prompt)
    if config.REPLICATE_API_TOKEN:
        return _replicate(prompt)
    return {
        "status": "not_configured",
        "message": "Image generation is not configured. Set REPLICATE_API_TOKEN "
                   "or STABILITY_API_KEY in .env.",
        "prompt": prompt,
    }


def _replicate(prompt: str) -> dict:
    resp = httpx.post(
        "https://api.replicate.com/v1/models/" + config.REPLICATE_MODEL + "/predictions",
        headers={"Authorization": f"Token {config.REPLICATE_API_TOKEN}"},
        json={"input": {"prompt": prompt}},
        timeout=60,
    )
    resp.raise_for_status()
    return {"status": "submitted", "provider": "replicate", "data": resp.json()}


def _stability(prompt: str) -> dict:
    resp = httpx.post(
        "https://api.stability.ai/v2beta/stable-image/generate/core",
        headers={"Authorization": f"Bearer {config.STABILITY_API_KEY}"},
        files={"none": ""},
        data={"prompt": prompt, "output_format": "png"},
        timeout=120,
    )
    resp.raise_for_status()
    return {"status": "submitted", "provider": "stability", "data": resp.json()}
