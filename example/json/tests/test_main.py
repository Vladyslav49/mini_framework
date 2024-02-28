from http import HTTPStatus

from httpx import Client


def test_index(client: Client) -> None:
    response = client.post("/", json={"name": "john"})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"name": "john"}


def test_hello(client: Client) -> None:
    response = client.post("/hello/", json={"name": "john"})

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hello, john!"


def test_user(client: Client) -> None:
    user = {"name": "Alice", "age": 30}

    response = client.post("/user/", json=user)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user


def test_user_embeded(client: Client) -> None:
    user = {"name": "Bob", "age": 25}

    response = client.post("/user-embeded/", json={"user": user})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user


def test_user_with_id(client: Client) -> None:
    user_id = 123
    user = {"name": "Charlie", "age": 40}

    response = client.post(
        "/user-with-id/", json={"id": user_id, "user": user}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"id": user_id, "user": user}


def test_user_with_home(client: Client) -> None:
    user = {"name": "David", "age": 35}
    home = {
        "owner": user,
        "address": "123 Main St",
        "square_footage": 1500.0,
        "num_rooms": 3,
    }

    response = client.post("/home/", json=home)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == home
