from http import HTTPStatus

from httpx import Client


def test_not_found(client: Client) -> None:
    response = client.get("/")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.text == HTTPStatus.NOT_FOUND.phrase
