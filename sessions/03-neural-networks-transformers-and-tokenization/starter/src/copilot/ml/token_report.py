"""Named-tokenizer measurements; pricing is optional and never fabricated."""

from __future__ import annotations

from pathlib import Path


def measure(
    data: Path,
    reports: Path,
    encoding=None,
    encoding_name="cl100k_base",
    input_price_per_million=None,
    output_price_per_million=None,
    assumed_output_tokens=128,
) -> dict:
    """TODO: implement measure following this session's BUILD_GUIDE.md"""
    raise NotImplementedError("TODO: implement measure following this session's BUILD_GUIDE.md")
