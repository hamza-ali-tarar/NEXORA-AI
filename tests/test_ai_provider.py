import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ai.provider import AIProvider


def test_ai_provider_is_abstract():
    assert AIProvider.__abstractmethods__ == {"generate_response"}