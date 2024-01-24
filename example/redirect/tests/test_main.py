from http import HTTPStatus

from httpx import Client


def test_index(client: Client) -> None:
    response = client.get("/")

    assert response.text == ""
    assert response.status_code == HTTPStatus.TEMPORARY_REDIRECT
    assert response.headers["Location"] == "/hello/"
