from http import HTTPStatus

from httpx import Client


def test_index(client: Client) -> None:
    response = client.get("/", params={"name": "Dio", "age": 124})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"name": "Dio", "age": 124}


def test_index_with_invalid_age(client: Client) -> None:
    response = client.get("/", params={"name": "Vladyslav", "age": 16})

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {
        "detail": [
            {
                "loc": ["age"],
                "msg": "Input should be greater than or equal to 18",
                "type": "greater_than_equal",
            }
        ],
        "hi": "Hello, World!",
    }
