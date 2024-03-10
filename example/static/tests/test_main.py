from http import HTTPStatus

from httpx import Client


def test_index(client: Client) -> None:
    expected_url = f"{client.base_url}/css/styles.css/"

    response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert (
        f'<link rel="stylesheet" type="text/css" href="{expected_url}">'
        in response.text
    )


def test_file_not_modified(client: Client) -> None:
    response = client.get(
        "/css/styles.css/",
        headers={"if-modified-since": "Sat, 13 Mar 3000 15:00:00 GMT"},
    )

    assert response.status_code == HTTPStatus.NOT_MODIFIED
    assert not response.text
