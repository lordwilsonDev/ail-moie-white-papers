"""Minimal stdlib HTTP client for MMVP backend adapters."""
from __future__ import annotations
import json
import os
import ssl
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from typing import Any, Dict, Optional


class HttpClient:
    def __init__(self, provider: str, api_key: Optional[str] = None, *, env_var: Optional[str] = None) -> None:
        self.provider = provider
        self.api_key = api_key or os.environ.get(env_var or f"{provider.upper()}_API_KEY", "")
        if not self.api_key:
            raise ValueError(f"{provider} API key missing; set {env_var or provider.upper() + '_API_KEY'}")

    def post_json(self, url: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        data = json.dumps(payload).encode("utf-8")
        req = Request(url, data=data, headers={**(headers or {}), "Content-Type": "application/json"})
        return self._request(req)

    def get_json(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        req = Request(url, headers=headers or {})
        return self._request(req)

    def _request(self, req: Request) -> Dict[str, Any]:
        ctx = ssl.create_default_context()
        try:
            with urlopen(req, context=ctx, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except HTTPError as exc:
            body = ""
            try:
                body = exc.read().decode("utf-8", errors="replace")
            except Exception:
                pass
            raise RuntimeError(
                f"{self.provider} request failed: {exc.code} {exc.reason} - {body}"
            ) from exc
