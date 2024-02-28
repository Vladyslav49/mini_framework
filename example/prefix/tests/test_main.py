from http import HTTPStatus

from httpx import Client


def test_index(client: Client) -> None:
    response = client.get("/index/")

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hello, World!"
