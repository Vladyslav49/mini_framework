from http import HTTPStatus

import pytest
from httpx import Client

pytestmark = pytest.mark.random_order(disabled=True)


def test_cookies(client: Client) -> None:
    response = client.get("/cookies/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {}


def test_set_cookies(client: Client) -> None:
    response = client.get("/set-cookies/")

    assert response.status_code == HTTPStatus.CREATED
    assert response.text == "Cookies set"

    assert response.cookies["name"] == "John"
    assert response.cookies["age"] == "20"


def test_cookies_set(client: Client) -> None:
    response = client.get("/cookies/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"name": "John", "age": "20"}


def test_clear_cookie_name(client: Client) -> None:
    response = client.get("/clear-cookie-name/")

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Cookies cleared"

    with pytest.raises(KeyError):
        response.cookies["name"]


def test_cookie_name_cleared(client: Client) -> None:
    response = client.get("/cookies/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"age": "20"}


def test_get_age(client: Client) -> None:
    response = client.get("/age/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"age": "20"}
