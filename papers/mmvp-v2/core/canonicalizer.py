"""Question canonicalizer for MMVP."""
from __future__ import annotations
import re

def canonicalize(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("text must be str")
    out = text.strip()
    out = re.sub(r"\r\n?", "\n", out)
    out = re.sub(r"[ \t]+", " ", out)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip()
