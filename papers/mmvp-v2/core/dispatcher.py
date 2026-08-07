"""Model dispatcher for MMVP."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, List, Dict, Any
import json

@dataclass(frozen=True)
class Response:
    model: str
    text: str
    metadata: Dict[str, Any]

class Backend(Protocol):
    def complete(self, prompt: str, **kwargs: Any) -> Response:
        ...

class Dispatcher:
    def __init__(self, backends: List[Backend]) -> None:
        self.backends = backends

    def dispatch(self, prompt: str, **kwargs: Any) -> List[Response]:
        if not prompt.strip():
            raise ValueError("prompt must be non-empty")
        return [b.complete(prompt, **kwargs) for b in self.backends]
