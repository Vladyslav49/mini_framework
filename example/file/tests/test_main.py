from http import HTTPStatus, HTTPMethod

from httpx import Client


def test_index(client: Client) -> None:
    with client.stream(HTTPMethod.GET, "/") as response:
        assert response.status_code == HTTPStatus.OK

        for i, line in enumerate(response.iter_lines()):
            assert line == str(i)
