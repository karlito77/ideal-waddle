"""Dependency wiring. One in-memory repository per app instance."""
from __future__ import annotations

from fastapi import Request

from riskintel.storage import Repository


def get_repo(request: Request) -> Repository:
    return request.app.state.repo
