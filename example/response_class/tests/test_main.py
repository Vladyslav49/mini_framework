from http import HTTPStatus

from httpx import Client


def test_plain_text(client: Client) -> None:
    response = client.get("/plain-text/")

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hello, World!"


def test_json(client: Client) -> None:
    response = client.get("/json/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Hello, World!"}
