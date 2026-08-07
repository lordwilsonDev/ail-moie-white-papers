"""Stub adapter for DeepSeek-compatible backends."""
from __future__ import annotations
from typing import Dict, Any, Optional
from adapters.protocol import Response

class DeepSeekAdapter:
    def __init__(self, model: str, api_key: Optional[str] = None, base_url: str = "https://api.deepseek.com") -> None:
        self.model = model
        self.base_url = base_url
        self.api_key = api_key

    def complete(self, prompt: str, **kwargs: Any) -> Response:
        raise NotImplementedError("DeepSeekAdapter requires network access; not implemented for offline tests")
