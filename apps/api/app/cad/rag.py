"""Optional engineering-knowledge interface; no vector store is required yet."""
from __future__ import annotations
from typing import Protocol


class EngineeringKnowledgeProvider(Protocol):
    async def retrieve(self, query: str) -> list[str]:
        """Return relevant drawing/CAD guidance for an interpretation request."""


class NullEngineeringKnowledgeProvider:
    async def retrieve(self, query: str) -> list[str]:
        return []
