"""Ollama local backend adapter."""
from __future__ import annotations
import os
from typing import Any, Dict, Optional
from ..adapters.protocol import Response
from .http_client import HttpClient


class OllamaAdapter:
    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434", api_key: Optional[str] = None) -> None:
        self.model = model
        self.base = f"{base_url.rstrip('/')}/api/chat"
        self.api_key = api_key or os.environ.get("OLLAMA_API_KEY")

    def complete(self, prompt: str, **kwargs: Any) -> Response:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        raw = HttpClient("ollama").post_json(self.base, payload, headers=headers if headers else None)
        text = raw.get("message", {}).get("content", "")
        return Response(
            model=self.model,
            text=text,
            metadata={
                "provider": "ollama",
                "raw_response": raw,
            },
        )
