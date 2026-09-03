"""Modification advisor: gains, cost, and JPJ legality reminders."""

from __future__ import annotations

from . import llm
from .models import CarRef, ModAdvice, Mod, ModRequest

_SYSTEM = (
    "You are a car modification advisor for Malaysia. Recommend practical mods, "
    "estimate gains (power/handling/reliability/aesthetics), give costs in RM, "
    "and flag JPJ legality. Be honest that estimates vary. Return ONLY valid JSON "
    'matching: {"summary": str, "mods": [{"name": str, "category": str, '
    '"expected_gains": str, "cost_rm": str, "difficulty": str, '
    '"legality_my": str, "caveats": str}]}'
)

_DISCLAIMER = (
    "Legality varies by state and mod specifics; always verify with JPJ before "
    "installing. Estimates are indicative only."
)


def advise(req: ModRequest) -> ModAdvice:
    car_desc = f"{req.car.make} {req.car.model} {req.car.year} {req.car.engine}".strip()
    prompt = (
        f"Car: {car_desc or '(unspecified)'}\n"
        f"Goal: {req.goal or 'general improvement'}\n"
        f"Usage: {req.usage}\n"
        f"Budget: RM {req.budget_rm if req.budget_rm else 'unspecified'}"
    )
    try:
        data = llm.complete_json(_SYSTEM, prompt)
        mods = [Mod(**m) for m in data.get("mods", [])]
        return ModAdvice(
            summary=data.get("summary", ""),
            mods=mods,
            legal_disclaimer=_DISCLAIMER,
        )
    except Exception as e:  # noqa: BLE001
        return ModAdvice(
            summary=f"(LLM unavailable: {e})",
            mods=[],
            legal_disclaimer=_DISCLAIMER,
        )
