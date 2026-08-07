"""Google Generative AI backend adapter."""
from __future__ import annotations
import os
from typing import Any, Dict, Optional
from ..adapters.protocol import Response
from .http_client import HttpClient


class GoogleAdapter:
    def __init__(self, model: str = "gemini-1.5-flash", api_key: Optional[str] = None) -> None:
        self.model = model
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key missing; set GOOGLE_API_KEY or GEMINI_API_KEY")
        self.base = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def complete(self, prompt: str, **kwargs: Any) -> Response:
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        url = f"{self.base}?key={self.api_key}"
        raw = HttpClient("google").post_json(url, payload)
        text = raw.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        return Response(
            model=self.model,
            text=text,
            metadata={
                "provider": "google",
                "raw_response": raw,
            },
        )
