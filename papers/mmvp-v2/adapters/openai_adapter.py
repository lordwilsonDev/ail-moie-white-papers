"""Stub adapter for OpenAI-compatible backends."""
from __future__ import annotations
from typing import Dict, Any, Optional
from adapters.protocol import Response, Backend

class OpenAIAdapter:
    def __init__(self, model: str, base_url: Optional[str] = None, api_key: Optional[str] = None) -> None:
        self.model = model
        self.base_url = base_url
        self.api_key = api_key

    def complete(self, prompt: str, **kwargs: Any) -> Response:
        raise NotImplementedError("OpenAIAdapter requires network access; not implemented for offline tests")
