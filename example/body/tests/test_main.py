from http import HTTPStatus

from httpx import Client


def test_index_with_body(client: Client) -> None:
    response = client.post("/", content="World")

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hello, World!"


def test_index_without_body(client: Client) -> None:
    response = client.post("/")

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hello, Anonymous!"
