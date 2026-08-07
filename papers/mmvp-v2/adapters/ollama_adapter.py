"""Stub adapter for Ollama local backends."""
from __future__ import annotations
from typing import Dict, Any, Optional
from adapters.protocol import Response

class OllamaAdapter:
    def __init__(self, model: str, base_url: str = "http://localhost:11434") -> None:
        self.model = model
        self.base_url = base_url

    def complete(self, prompt: str, **kwargs: Any) -> Response:
        raise NotImplementedError("OllamaAdapter requires local Ollama; not implemented for offline tests")
