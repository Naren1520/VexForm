"""Pytest configuration and shared fixtures."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


@pytest.fixture
def client():
    """FastAPI test client with mocked settings."""
    with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key", "SESSION_SECRET": "test-secret"}):
        from main import app
        return TestClient(app)
