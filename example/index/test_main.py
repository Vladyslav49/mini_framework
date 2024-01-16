import pytest
from httpx import Client

from .main import app


@pytest.fixture(scope="session")
def client() -> Client:
    return Client(app=app, base_url="http://testserver")


def test_index(client: Client) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.text == "Hello, World!"
