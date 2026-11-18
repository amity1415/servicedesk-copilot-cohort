"""Schema-checked ticket inference with at most one output-repair attempt."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Classification(BaseModel):
    category: Literal[
        "Access & Identity",
        "Network & VPN",
        "Email & Collaboration",
        "Hardware & Devices",
        "Software",
        "Security",
        "Onboarding & Offboarding",
        "General Enquiry",
    ]
    priority: Literal["P1", "P2", "P3", "P4"]
    summary: str = Field(min_length=3, max_length=160)


def classify(client, text: str) -> Classification:
    """TODO: implement classify following this session's BUILD_GUIDE.md"""
    raise NotImplementedError("TODO: implement classify following this session's BUILD_GUIDE.md")
