from http import HTTPStatus

from httpx import Client


def test_index(client: Client) -> None:
    response = client.post("/", json={"name": "john"})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"name": "john"}
