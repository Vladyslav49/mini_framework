from http import HTTPStatus

from httpx import Client


def test_index(client: Client) -> None:
    response = client.get("/", params={"name": "Dio", "age": 124})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"name": "Dio", "age": 124}


def test_index_with_invalid_age(client: Client) -> None:
    response = client.get("/", params={"name": "Vladyslav", "age": 16})

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    json = response.json()

    assert len(json["detail"]) == 1
    assert (
        json["detail"][0].items()
        >= {
            "loc": ["age"],
            "msg": "Input should be greater than or equal to 18",
            "type": "greater_than_equal",
        }.items()
    )
    assert json["hi"] == "Hello, World!"
