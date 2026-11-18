"""Grouped ticket classification experiments with explicit feature boundaries."""

from __future__ import annotations

from pathlib import Path


def read_examples(data: Path) -> list[dict]:
    """TODO: implement read_examples following this session's BUILD_GUIDE.md"""
    raise NotImplementedError(
        "TODO: implement read_examples following this session's BUILD_GUIDE.md"
    )


def request_text(row: dict) -> str:
    """TODO: implement request_text following this session's BUILD_GUIDE.md"""
    raise NotImplementedError(
        "TODO: implement request_text following this session's BUILD_GUIDE.md"
    )


def split_examples(rows: list[dict], seed: int = 42):
    """TODO: implement split_examples following this session's BUILD_GUIDE.md"""
    raise NotImplementedError(
        "TODO: implement split_examples following this session's BUILD_GUIDE.md"
    )


def features(train_text: list[str], test_text: list[str]):
    """TODO: implement features following this session's BUILD_GUIDE.md"""
    raise NotImplementedError("TODO: implement features following this session's BUILD_GUIDE.md")


def train(data: Path, reports: Path) -> dict:
    """TODO: implement train following this session's BUILD_GUIDE.md"""
    raise NotImplementedError("TODO: implement train following this session's BUILD_GUIDE.md")
