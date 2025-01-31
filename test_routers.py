import pytest


@pytest.fixture(scope="module", autouse=True)
def setup_env():
    import os

    os.environ["TAVILY_API_KEY"] = "TAVILY_API_KEY"


def test_healthcheck():
    assert True
