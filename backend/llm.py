"""Groq LLM helpers (OpenAI-compatible client)."""

from __future__ import annotations

import json

from . import config

_client = None


def _get_client():
    global _client
    if not config.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not set. Add it to .env")
    if _client is None:
        from openai import OpenAI

        _client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=config.GROQ_API_KEY)
    return _client


def complete(system: str, prompt: str, temperature: float = 0.2, max_tokens: int = 512) -> str:
    resp = _get_client().chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content or ""


def complete_json(system: str, prompt: str, temperature: float = 0.2) -> dict:
    text = complete(system, prompt, temperature, max_tokens=900).strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    return json.loads(text)
