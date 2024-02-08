from http import HTTPStatus

from httpx import Client


def test_index(client: Client) -> None:
    response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hello, World!"


def test_hello(client: Client) -> None:
    response = client.get("/hello/John/")

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hello, John!"
