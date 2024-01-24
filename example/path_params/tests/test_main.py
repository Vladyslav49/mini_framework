from http import HTTPStatus

from httpx import Client


def test_hello_world(client: Client) -> None:
    response = client.get("/hello/world/")

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hello!"


def test_hello_with_path_params(client: Client) -> None:
    response = client.get("/hello/john/")

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hello, John!"


def test_hello_from_user_with_path_params(client: Client) -> None:
    response = client.get("/hello/john/mary/")

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hello, John from Mary!"


def test_hi_with_path_params(client: Client) -> None:
    response = client.get("/hi/john/")

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hi, John!"


def test_hello(client: Client) -> None:
    response = client.get("/hello/")

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hello, Anonymous!"
