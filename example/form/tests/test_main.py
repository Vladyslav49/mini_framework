from http import HTTPStatus

from httpx import Client


def test_index(client: Client) -> None:
    response = client.post("/", files={"file": "Hello, World!"})

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hello, World!"
