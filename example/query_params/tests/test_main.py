from http import HTTPStatus

from httpx import Client


def test_index_with_query_params(client: Client) -> None:
    response = client.get("/", params={"name": "John"})

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hello, John!"


def test_index_without_query_params(client: Client) -> None:
    response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hello, Anonymous!"


def test_hello_with_query_params(client: Client) -> None:
    response = client.get("/hello/", params={"name": "John"})

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hello, John!"


def test_hello_without_query_params(client: Client) -> None:
    response = client.get("/hello/")

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hello, Anonymous!"


def test_greetings(client: Client) -> None:
    response = client.get(
        "/greetings/", params=[("names", "John"), ("names", "World")]
    )

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hello, John, World!"
