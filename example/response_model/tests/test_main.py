from http import HTTPStatus

from httpx import Client


def test_index(client: Client) -> None:
    response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == [
        {"name": "Dio", "age": 124},
        {"name": "Jotaro", "age": 17},
    ]
