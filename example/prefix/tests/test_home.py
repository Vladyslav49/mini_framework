from http import HTTPStatus

from httpx import Client


def test_home(client: Client) -> None:
    response = client.get("/index/home/")

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Home"
