from http import HTTPStatus

from httpx import Client


def test_index(client: Client) -> None:
    response = client.post("/", files={"file": "Hello, World!"})

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hello, World!"


def test_hello(client: Client) -> None:
    response = client.post(
        "/hello/", data={"name": "World"}, files={"file": "Hello, World!"}
    )

    assert response.text == "Hello, World!"
    assert response.status_code == HTTPStatus.OK


def test_upload_files(client: Client) -> None:
    response = client.post(
        "/upload-files/",
        files=[
            ("file", "Hello, World 0!"),
            ("file", "Hello, World 1!"),
            ("file", "Hello, World 2!"),
        ],
    )

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hello, World!"


def test_upload_multiple_files(client: Client) -> None:
    response = client.post(
        "/upload-multiple-files/",
        files=[
            ("file", "Hello, World 0!"),
            ("file", "Hello, World 1!"),
        ],
    )

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hello, World!"


def test_upload_multiple_files_with_list(client: Client) -> None:
    response = client.post(
        "/upload-multiple-files-with-list/",
        files=[
            ("file", "Hello, World 0!"),
            ("file", "Hello, World 1!"),
            ("file", "Hello, World 2!"),
            ("file", "Hello, World 3!"),
        ],
    )

    assert response.status_code == HTTPStatus.OK
    assert response.text == "Hello, World!"
