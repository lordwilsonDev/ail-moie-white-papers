"""Backend protocol definition for MMVP."""
from __future__ import annotations
from typing import Protocol, Dict, Any
from dataclasses import dataclass

@dataclass(frozen=True)
class Response:
    model: str
    text: str
    metadata: Dict[str, Any]

class Backend(Protocol):
    def complete(self, prompt: str, **kwargs: Any) -> Response:
        ...
