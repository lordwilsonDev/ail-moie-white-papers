"""OpenAI-compatible backend adapter."""
from __future__ import annotations
import os
from typing import Any, Dict, Optional
from ..adapters.protocol import Response
from .http_client import HttpClient


class OpenAIAdapter:
    def __init__(self, model: str = "gpt-4o-mini", api_key: Optional[str] = None) -> None:
        self.model = model
        self.client = HttpClient("openai", api_key, env_var="OPENAI_API_KEY")
        self.base = "https://api.openai.com/v1/chat/completions"

    def complete(self, prompt: str, **kwargs: Any) -> Response:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": kwargs.get("max_tokens", 1024),
        }
        raw = self.client.post_json(self.base, payload)
        choice = raw["choices"][0]["message"]["content"]
        usage = raw.get("usage", {})
        return Response(
            model=self.model,
            text=choice,
            metadata={
                "provider": "openai",
                "finish_reason": raw["choices"][0].get("finish_reason"),
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "raw_response": raw,
            },
        )
