import pytest
from fastapi.testclient import TestClient

from src.app import app
from src.logger import logger

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_env():
    import os
    os.environ["TAVILY_API_KEY"] = "TAVILY_API_KEY"


def test_healthcheck():
    response = client.get("/api/")
    assert response.status_code == 200
