from httpx import Client


def test_index(client: Client) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.text == "Hello, World!"
