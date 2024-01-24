import pytest
from httpx import Client

from ..main import app


@pytest.fixture(scope="session")
def client() -> Client:
    return Client(app=app, base_url="http://testserver")
