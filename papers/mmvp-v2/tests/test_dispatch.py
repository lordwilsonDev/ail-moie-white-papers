"""Test MMVP dispatcher and mock backend."""
from __future__ import annotations
import pytest
from core.dispatcher import Dispatcher, Response
from adapters.mock_adapter import MockBackend

class TestDispatcher:
    def test_dispatch_returns_all_responses(self):
        prompts = {"q": "answer:42"}
        backend = MockBackend("mock-model", prompts)
        dispatcher = Dispatcher([backend, backend])
        responses = dispatcher.dispatch("q")
        assert len(responses) == 2

    def test_empty_prompt_raises(self):
        backend = MockBackend("mock-model", {})
        dispatcher = Dispatcher([backend])
        with pytest.raises(ValueError):
            dispatcher.dispatch("")
