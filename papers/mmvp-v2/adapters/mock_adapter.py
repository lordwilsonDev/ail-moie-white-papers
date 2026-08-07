"""Mock backend for deterministic MMVP tests."""
from __future__ import annotations
from typing import Dict, Any
from adapters.protocol import Response

class MockBackend:
    def __init__(self, model: str, replies: Dict[str, str]) -> None:
        self.model = model
        self.replies = replies

    def complete(self, prompt: str, **kwargs: Any) -> Response:
        text = self.replies.get(prompt, f"[{self.model}] default response")
        return Response(model=self.model, text=text, metadata={"mock": True, "prompt_hash": str(hash(prompt))})
