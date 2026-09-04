import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ai.mock_provider import MockAIProvider


def test_mock_provider_generates_response():
    provider = MockAIProvider()

    response = provider.generate_response("Hello NEXORA")

    assert response == "Mock response: Hello NEXORA"