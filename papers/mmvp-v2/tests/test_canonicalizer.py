"""Test MMVP canonicalizer."""
from __future__ import annotations
import pytest
from core.canonicalizer import canonicalize

class TestCanonicalizer:
    def test_strips_whitespace(self):
        assert canonicalize("  hi  ") == "hi"

    def test_normalizes_line_endings(self):
        assert canonicalize("a\r\nb") == "a\nb"

    def test_collapses_internal_spaces(self):
        assert canonicalize("a    b") == "a b"

    def test_collapses_multiple_blanks(self):
        assert canonicalize("a\n\n\n\nb") == "a\n\nb"

    def test_rejects_non_string(self):
        with pytest.raises(TypeError):
            canonicalize(123)
