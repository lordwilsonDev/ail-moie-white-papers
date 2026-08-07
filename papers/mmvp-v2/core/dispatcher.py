"""Model dispatcher with provenance tracking for MMVP."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol, List, Dict, Any
import json

@dataclass(frozen=True)
class Response:
    model: str
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class Backend(Protocol):
    def complete(self, prompt: str, **kwargs: Any) -> Response:
        ...

class Dispatcher:
    def __init__(self, backends: List[Backend]) -> None:
        self.backends = backends

    def dispatch(self, prompt: str, **kwargs: Any) -> List[Response]:
        if not prompt.strip():
            raise ValueError("prompt must be non-empty")
        results: List[Response] = []
        for backend in self.backends:
            response = backend.complete(prompt, **kwargs)
            meta = dict(response.metadata)
            meta.setdefault("provider", getattr(backend, "__class__", type(backend)).__name__.replace("Adapter", "").lower())
            results.append(Response(model=response.model, text=response.text, metadata=meta))
        return results
