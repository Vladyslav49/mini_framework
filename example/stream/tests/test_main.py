from http import HTTPStatus, HTTPMethod

from httpx import Client, Response


def test_index(client: Client) -> None:
    with client.stream(HTTPMethod.GET, "/") as response:
        response: Response

        assert response.status_code == HTTPStatus.OK

        for i, line in enumerate(response.iter_text()):
            assert line == str(i)
